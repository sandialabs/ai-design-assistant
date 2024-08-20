import itertools
import copy
import numpy as np
# import ada
from ada.geometry.airfoils.kulfan import Kulfan
# from ada.analysis.apis import xfoil
# from ada.analysis.apis.xfoil.standardPlot import standardPlot
from ada.ui.openAIwrapper import sendToOpenAI
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
# from datetime import datetime
import datetime
import os
from ada.ui.callRAG import callRAG
from ada.ui.callLLM import callLLM
import json
import shutil
import subprocess
import platform
from ada.analysis.saveLoadAnalysisCase import saveAnalysisCase, loadAnalysisCase
from ada.analysis.apis import currentToolList
from ada.ui.api import API as baseAPI
from ada.analysis.apis.xfoil.api_ui import API_UI as xfoilAPI
import natsort


PATH_TO_ADA = os.environ['PATH_TO_ADA']

colors = ['#0065cc', '#e69f00', '#009e73', '#d55e00', '#56b4ff', '#fca7c7', '#ede13f', '#666666', '#000000']
matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)



class Call(object):
    def __init__(self):
        self.query         = None
        self.interpretaion = None
        self.response      = None

    def print_html(self, callIndex=0, isLast=False):
        pstr = ''
        if isLast:
            pstr += '<div class="body-cell last">\n'
        else:
            pstr += '<div class="body-cell">\n'
        pstr += '    <div class="io-cell input-cell">\n'
        pstr += '        <div class="label io-text">Query [%d]</div>\n'%(callIndex)
        pstr += '        <div class="query-cell io-text">%s</div>\n'%(self.query)
        pstr += '    </div>\n'
        pstr += '    <div class="io-cell output-cell">\n'
        pstr += '        <div class="label io-text">Interpretation [%d]</div>\n'%(callIndex)
        pstr += '        <div class="interpretation-cell io-text">%s</div>\n'%(self.interpretaion)
        pstr += '    </div>\n'
        pstr += '    <div class="io-cell output-cell">\n'
        pstr += '        <div class="label io-text">Response [%d]</div>\n'%(callIndex)
        pstr += '        <div class="response-cell io-text">%s</div>\n'%(self.response)
        pstr += '    </div>\n'
        pstr += '</div>\n'
        return pstr


class AirfoilGeometry(Kulfan):
    def __init__(self):
        super().__init__()
        self._mutableLock = False

    def print_html(self, idx, isActive=False):
        pstr = ''
        if isActive:
            pstr += '<div class="geometry-cell active">\n'
        else:
            pstr += '<div class="geometry-cell">\n'
        # pstr += '<div class="geometry-cell">\n'
        if self.mutableLock:
            pstr += '    <div class="geomtry-type">Airfoil %d--Kulfan Geometry--Locked</div>\n'%(idx)
        else:
            pstr += '    <div class="geomtry-type">Airfoil %d--Kulfan Geometry--Unlocked</div>\n'%(idx)
        pstr += '    <table class="geometry-table">\n'
        pstr += '        <tr class="geometry-row">\n'
        pstr += '            <td></td>\n'
        pstr += '            <td class="geometry-value">K_upper</td>\n'
        pstr += '            <td class="geometry-value">K_lower</td>\n'
        pstr += '        </tr>\n'
        for i,vl in enumerate(self.upperCoefficients):
            pstr += '        <tr class="geometry-row">\n'
            pstr += '            <td class="geometry-parameter">K[%d]</td>\n'%(i+1)
            pstr += '            <td class="geometry-value">%f</td>'%(self.upperCoefficients[i])
            pstr += '            <td class="geometry-value">%f</td>'%(self.lowerCoefficients[i])
            pstr += '        </tr>\n'
        pstr += '    </table>\n'
        pstr += '</div>\n'
        return pstr

    @property
    def mutableLock(self):
        return self._mutableLock
    
    @mutableLock.setter
    def mutableLock(self,val):
        if val == True:
            self._mutableLock = True
        else:
            self._mutableLock = False
            # do nothing, only allow locking, not unlocking
            # but being lazy before the refactor, so just allowing for now
            # pass



class LocalAPI(baseAPI):
    def __init__(self):
        pass

    def make_basic_data(self):
        functionDict = {}
        functionDict['name']=None
        functionDict['description']=None
        functionDict['parameters']={}
        functionDict['parameters']['type']='object'
        functionDict['parameters']['properties']={}
        functionDict['parameters']['required']=[]

        return functionDict
    
    def return_function_data(self):

        functionData = []
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='generateAirfoil'
        functionDict['description']='Generates a 2D Airfoil'

        airfoil_directories = [
            PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/uiuc_airfoils',
            PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/airfoiltools_airfoils',
            PATH_TO_ADA + 'ada/geometry/airfoil_files',
            PATH_TO_ADA + 'ada/geometry/generated_naca4_airfoils',
        ]

        airfoil_directory_data = {}
        for afl_dir in airfoil_directories:
            # file_data_dict = {}
            pth = afl_dir
            combined = os.listdir(pth)
            files   = [f for f in combined if os.path.isfile(pth + os.sep + f)]
            for fl in files:
                airfoil_directory_data[fl] = pth + os.sep + fl
                
        airfoil_names = list(airfoil_directory_data.keys())
        for ai, aflnm in enumerate(airfoil_names):
            airfoil_names[ai] = aflnm[0:-4]
        
        functionDict['parameters']['properties']['aflString']={}
        functionDict['parameters']['properties']['aflString']['type']="string"
        # this is correct, but adds lots of tokens and slows it down a lot
        # I've had no issues without full enumeration
        # functionDict['parameters']['properties']['aflString']['enum']=airfoil_names
        functionDict['parameters']['properties']['aflString']['description']="The name of an airfoil.  Examples include: NACA2412, S814, and LA5055"
        
        functionDict['parameters']['required'].extend(['aflString'])
            
        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='modifyGeometry'
        functionDict['description']='Modifies a geometry parameter'
        
        functionDict['parameters']['properties']['surface']={}
        functionDict['parameters']['properties']['surface']['type']="string"
        functionDict['parameters']['properties']['surface']['enum']=['upper','lower']
        functionDict['parameters']['properties']['surface']['description']="Selects between the upper and lower surface parameterizations.  Letter 'l' can also be used to indicate the lower surface, and letter 'u' can also indicate the upper surface."
        
        functionDict['parameters']['properties']['index']={}
        functionDict['parameters']['properties']['index']['type']="string"
        functionDict['parameters']['properties']['index']['description']="The index (an integer) that corresonds to the value being changed.  This may be coupled with the letter K, as in K[1] or K_1 to indicate the desired index."
        
        functionDict['parameters']['properties']['value']={}
        functionDict['parameters']['properties']['value']['type']="string"
        functionDict['parameters']['properties']['value']['description']="The value of the parameter that is being modified.  This will be a single float number."
        
        functionDict['parameters']['properties']['geometryIndex']={}
        functionDict['parameters']['properties']['geometryIndex']['type']="string"
        functionDict['parameters']['properties']['geometryIndex']['description']="The index (an integer) of the geometry being used in the function.  If no geometryNumber can be unambiguously determined, then return the string 'None'"
        
        functionDict['parameters']['required'].extend(['surface','index','value','geometryIndex'])
        
        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='changeActiveGeometry'
        functionDict['description']='Changes the currently active geometry'
        
        functionDict['parameters']['properties']['activeGeometryIndex']={}
        functionDict['parameters']['properties']['activeGeometryIndex']['type']="string"
        functionDict['parameters']['properties']['activeGeometryIndex']['description']="The index (an integer) of the new active geometry"
        
        functionDict['parameters']['required'].extend(['activeGeometryIndex'])
        
        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='changeActiveAnalysis'
        functionDict['description']='Changes the currently active analysis'
        
        functionDict['parameters']['properties']['activeAnalysisTool']={}
        functionDict['parameters']['properties']['activeAnalysisTool']['type']="string"
        functionDict['parameters']['properties']['activeAnalysisTool']['enum']=currentToolList
        functionDict['parameters']['properties']['activeAnalysisTool']['description']="The name of the new active analysis tool.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['properties']['activeAnalysisIndex']={}
        functionDict['parameters']['properties']['activeAnalysisIndex']['type']="string"
        functionDict['parameters']['properties']['activeAnalysisIndex']['description']="The index (an integer) of the new active analysis case.  Do not call this function if activeAnalysisIndex cannot be determined unambiguously."
        
        functionDict['parameters']['required'].extend(['activeAnalysisTool','activeAnalysisIndex'])
        
        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='copyGeometry'
        functionDict['description']='Copies a geometry object'
        
        functionDict['parameters']['properties']['geometryIndex']={}
        functionDict['parameters']['properties']['geometryIndex']['type']="string"
        functionDict['parameters']['properties']['geometryIndex']['description']="The index (an integer) of the geometry to copy.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required'].extend(['geometryIndex'])
        
        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='copyAnalysis'
        functionDict['description']='Copies an analysis case'
        
        functionDict['parameters']['properties']['toolName']={}
        functionDict['parameters']['properties']['toolName']['type']="string"
        functionDict['parameters']['properties']['toolName']['enum']=currentToolList
        functionDict['parameters']['properties']['toolName']['description']="The name of the type of analysis case that is being copied.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['properties']['caseIndex']={}
        functionDict['parameters']['properties']['caseIndex']['type']="string"
        functionDict['parameters']['properties']['caseIndex']['description']="The index (an integer) analysis case to copy.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required'].extend(['toolName','caseIndex'])

        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='run'
        functionDict['description']='Runs an analysis.  This function is often called using only the word "run" or "run [analysis]" where [analysis] is the name of an analysis tool contained in the toolName enumerated list'
        
        functionDict['parameters']['properties']['toolName']={}
        functionDict['parameters']['properties']['toolName']['type']="string"
        functionDict['parameters']['properties']['toolName']['enum']=currentToolList
        functionDict['parameters']['properties']['toolName']['description']="The name of the type of analysis case that is being copied.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['properties']['caseIndex']={}
        functionDict['parameters']['properties']['caseIndex']['type']="string"
        functionDict['parameters']['properties']['caseIndex']['description']="The index (an integer) analysis case to copy.  If cannot determine unambiguously, return the string 'None'."

        functionDict['parameters']['properties']['geometryIndex']={}
        functionDict['parameters']['properties']['geometryIndex']['type']="string"
        functionDict['parameters']['properties']['geometryIndex']['description']="The index (an integer) of the geometry to copy.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required'].extend(['toolName','caseIndex','geometryIndex'])
        

        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='selectData'
        functionDict['description']='Selects a specific list of data indicies'
        
        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be selected.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required'].extend(['dataIndicies'])

        functionData.append(functionDict)
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='deselectData'
        functionDict['description']='Deselects a specific list of data indicies'
        
        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be deselected.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required'].extend(['dataIndicies'])

        functionData.append(functionDict)
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='clearDataSelection'
        functionDict['description']='Clears all of the active data selections'
            
        functionData.append(functionDict)
        # ================================================================================================================================
        functionDict = self.make_basic_data()
        functionDict['name']='makeRequest'
        functionDict['description']='This function should be selected when on other function is appropriate.  It generally involves a request for information, code example, or similar.'
            
        functionData.append(functionDict)
        # ================================================================================================================================

        return functionData

    def return_handle_map(self):
        ldr = ''

        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]

        handle_map = {}
        for mth in method_list:
            if mth not in ['return_function_data', 'return_handle_map', 'make_basic_data']:
                handle_map[ldr + mth] = getattr(self, mth)
        return handle_map


    def generateAirfoil(self, uiManager, aflString, **kwargs):
        aflString = aflString.replace(' ','')
        aflString = aflString.lower()
        if aflString[0:4].lower() == 'naca':
            nacaNumbers = aflString[4:]
            if len(nacaNumbers)!=4:
                return 'Error: invalid naca4'
            else:
                afl1 = AirfoilGeometry() 
                afl1.naca4_like(int(nacaNumbers[0]), int(nacaNumbers[1]), int(nacaNumbers[2:]))
                uiManager.geometryItems.append(afl1)
                
        else:
            # this needs to utilize the large database of airfoils
            afl1 = AirfoilGeometry()

            airfoil_directories = [
                PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/uiuc_airfoils',
                PATH_TO_ADA + 'ada/geometry/airfoil_scraping/raw_airfoil_files/airfoiltools_airfoils',
                PATH_TO_ADA + 'ada/geometry/airfoil_files',
            ]

            airfoil_directory_data = {}
            for afl_dir in airfoil_directories:
                # file_data_dict = {}
                pth = afl_dir
                combined = os.listdir(pth)
                files   = [f for f in combined if os.path.isfile(pth + os.sep + f)]
                for fl in files:
                    airfoil_directory_data[fl] = pth + os.sep + fl
    
            search_file = aflString + '.dat'
            afl1.fit2file(airfoil_directory_data[search_file])

            uiManager.geometryItems.append(afl1)

        uiManager.activeGeometry = len(uiManager.geometryItems)-1

        res = {}
        res['new_camera_position'] = [0.5,0,1.0]
        res['new_camera_target']   = [0.5,0,0]
        
        res['curves'] = [ [ uiManager.geometryItems[uiManager.activeGeometry].xcoordinates.tolist(), 
                            uiManager.geometryItems[uiManager.activeGeometry].ycoordinates.tolist(), 
                            [0 for i in range(0,len(uiManager.geometryItems[uiManager.activeGeometry].xcoordinates))] ] ]
        res['clear_objects'] = True
        uiManager.graphicWindowDictionary = res
        
        return "Query task complete"
        
    def modifyGeometry(self, uiManager, surface, index, value, geometryIndex, **kwargs):
        if geometryIndex=='None':
            geometryIndex = uiManager.activeGeometry+1

        if uiManager.geometryItems[int(geometryIndex)-1].mutableLock == True:
            self.copyGeometry(uiManager,geometryIndex)
            uiManager.activeGeometry = len(uiManager.geometryItems)-1

        afl = uiManager.geometryItems[uiManager.activeGeometry]

        if surface == 'lower':
            afl.lowerCoefficients[int(index)-1] = float(value)

        elif surface == 'upper':
            afl.upperCoefficients[int(index)-1] = float(value)

        else:
            raise ValueError('invalid surface')

        tsh = self.changeActiveGeometry(uiManager, uiManager.activeGeometry+1)

        return "Query task complete"
        
#     def printAirfoilCoordinates(self):
#         pass
        
#     def plotAirfoilGeometry(self):
#         pass
        
    def changeActiveGeometry(self, uiManager, activeGeometryIndex, **kwargs):
        uiManager.activeGeometry = int(activeGeometryIndex)-1
        res = {}
        res['new_camera_position'] = [0.5,0,1.0]
        res['new_camera_target']   = [0.5,0,0]
        
        res['curves'] = [ [ uiManager.geometryItems[uiManager.activeGeometry].xcoordinates.tolist(), 
                            uiManager.geometryItems[uiManager.activeGeometry].ycoordinates.tolist(), 
                            [0 for i in range(0,len(uiManager.geometryItems[uiManager.activeGeometry].xcoordinates))] ] ]
        res['clear_objects'] = True
        uiManager.graphicWindowDictionary = res
        return "Query task complete"
        
    def changeActiveAnalysis(self, uiManager, activeAnalysisTool, activeAnalysisIndex, **kwargs):
        if activeAnalysisTool == 'None':
            activeAnalyslsTool = uiManager.activeAnalysis[0]
        uiManager.activeAnalysis = (activeAnalysisTool , int(activeAnalysisIndex)-1 )
        return "Query task complete"
        
    def copyAnalysis(self, uiManager, toolName, caseIndex, **kwargs):
        if toolName == 'None':
            toolName = uiManager.activeAnalysis[0]
        if caseIndex == 'None':
            caseIndex = uiManager.activeAnalysis[1]+1

        rc1 = uiManager.analysisItems[toolName][int(caseIndex)-1].free_copy()
        uiManager.analysisItems[toolName].append(rc1)
        return "Query task complete"
        
    def copyGeometry(self, uiManager, geometryIndex, **kwargs):
        if geometryIndex=='None':
            geometryIndex = uiManager.activeGeometry+1

        afl = copy.deepcopy(uiManager.geometryItems[int(geometryIndex)-1])
        afl.mutableLock = False  # being lazy before goemetry refactor
        uiManager.geometryItems.append(afl)

        return "Query task complete"

    def selectData(self, uiManager, dataIndicies, **kwargs):
        setVal = None
        try:
            setVal = int(dataIndicies)-1
            setVal = [setVal]
        except:
            # is not a single nubmer
            pass

        if setVal is None:
            try:
                if (dataIndicies[0] in ['[','(','{'] and dataIndicies[-1] in [']',')','}']):
                    vl = dataIndicies[1:-1]
                    vl_split = vl.split(',')
                    setVal = [int(v)-1 for v in vl_split]
                else:
                    # will fail
                    pass

            except:
                # could not extract an array, will now fail
                pass

        if setVal is None:
            return "FAILURE: Could not parse '%s' into a valid list of indicies"%(dataIndicies)

        if uiManager.activeDataItems is None:
            uiManager.activeDataItems = []

        didAppend = False
        for vl in setVal:
            if vl > len(uiManager.dataItems):
                # invalid selection
                pass
            else:
                didAppend = True
                uiManager.activeDataItems.append(vl)

        if not didAppend:
            return "FAILURE: No valid data index was specified"

        else:
            return "Query task complete"

    def deselectData(self, uiManager, dataIndicies, **kwargs):
        if dataIndicies == 'None':
            self.clearDataSelection(uiManager, **kwargs)
            return 'Query task complete'

        setVal = None
        try:
            setVal = int(dataIndicies)-1
            setVal = [setVal]
        except:
            # is not a single nubmer
            pass

        if setVal is None:
            try:
                if (dataIndicies[0] in ['[','(','{'] and dataIndicies[-1] in [']',')','}']):
                    vl = dataIndicies[1:-1]
                    vl_split = vl.split(',')
                    setVal = [int(v)-1 for v in vl_split]
                else:
                    # will fail
                    pass

            except:
                # could not extract an array, will now fail
                pass

        if setVal is None:
            return "FAILURE: Could not parse '%s' into a valid list of indicies"%(dataIndicies)

        currentActiveIndicies = uiManager.activeDataItems
        newActiveIndicies = []
        for cai in currentActiveIndicies:
            if cai not in setVal:
                newActiveIndicies.append(cai)

        uiManager.activeDataItems = newActiveIndicies

        return "Query task complete"

    def clearDataSelection(self, uiManager, **kwargs):
        uiManager.activeDataItems = None
        return "Query task complete"

    def run(self, uiManager, toolName='None', caseIndex='None', geometryIndex='None', **kwargs):
        if toolName == 'None' or toolName == '':
            toolName = uiManager.activeAnalysis[0]
        if caseIndex == 'None' or caseIndex == '':
            caseIndex = uiManager.activeAnalysis[1]+1
        if geometryIndex == 'None' or geometryIndex == '':
            geometryIndex = uiManager.activeGeometry+1

        if toolName=='xfoil':
            xfoil = xfoilAPI()
            res = xfoil.run(uiManager, toolName, int(caseIndex), int(geometryIndex), **kwargs)
            return res
        else:
            raise ValueError('Invalid tool name %s'%(toolName))

    def makeRequest(self, uiManager, rawInput, **kwargs):
        # uiManager.callRAG()
        opt = uiManager.callRAG(rawInput, False)
        # c.interpretaion = "Passed the query directly to the RAG framework"
        # c.response = opt
        # c.callMode = 'RAG'
        return opt


class UIHandler(object):
    def __init__(self, print_calls=False):
        self.geometryItems = []
        self.analysisItems = {}#[]
        self.calls = []
        self.dataItems = []
        self.activeDataItems = None
        self.activeGeometry = None
        self.activeAnalysis = None

        self._print_calls = print_calls

        self.graphicWindowDictionary = {}
        # self.workingDirectory = str(Path.home())

        dt_now           = datetime.datetime.now()
        dt_now_string    = dt_now.strftime("%m-%d-%Y_%H-%M-%S")
        dt_now_m1_string = (dt_now-datetime.timedelta(seconds=1)).strftime("%m-%d-%Y_%H-%M-%S")
        dt_now_m2_string = (dt_now-datetime.timedelta(seconds=2)).strftime("%m-%d-%Y_%H-%M-%S")
        dt_now_m3_string = (dt_now-datetime.timedelta(seconds=3)).strftime("%m-%d-%Y_%H-%M-%S")
        dt_now_m4_string = (dt_now-datetime.timedelta(seconds=4)).strftime("%m-%d-%Y_%H-%M-%S")
        dt_now_m5_string = (dt_now-datetime.timedelta(seconds=5)).strftime("%m-%d-%Y_%H-%M-%S")

        if os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m5_string )):
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m5_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_m5_string )
        elif os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m4_string )):
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m4_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_m4_string )
        elif os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m3_string )):
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m3_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_m3_string )
        elif os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m2_string )):
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m2_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_m2_string )
        elif os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m1_string )):
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_m1_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_m1_string )
        else:
            self.sessionDirectory = os.path.join(Path.home(), '.ada', 'Session_' + dt_now_string )
            self.relativeSessionDirectory = os.path.join('.ada', 'Session_' + dt_now_string )
            if not os.path.exists(os.path.join(Path.home(), '.ada', 'Session_' + dt_now_string )):
                os.mkdir(self.sessionDirectory)

        self.workingDirectory = str(self.sessionDirectory)


    def generateBodyHTML(self):
        divString = ''
        for i,c in enumerate(self.calls):
            isLast = False
            if i == len(self.calls) - 1:
                isLast = True
            divString += c.print_html(i+1,isLast)
            divString += '\n'

        return divString

    def generateFiletreeHTML(self):

        combined = os.listdir(self.workingDirectory)
        # files   = list(sorted([f for f in combined if os.path.isfile(self.workingDirectory + os.sep + f)]))
        # folders = list(sorted([f for f in combined if not os.path.isfile(self.workingDirectory + os.sep + f)]))
        files   = natsort.natsorted([f for f in combined if os.path.isfile(self.workingDirectory + os.sep + f)], alg=natsort.ns.IGNORECASE)
        folders = natsort.natsorted([f for f in combined if not os.path.isfile(self.workingDirectory + os.sep + f)], alg=natsort.ns.IGNORECASE)

        pstr = ''

        pstr += '<div class="file-table-container">\n'
        pstr += '<div class="pwd-wrapper">\n'
        wd = self.workingDirectory
        wdList = wd.split(os.sep)
        for w in wdList:
            if not w.isspace() and w!='':
                pstr += '<a class="pwd-link">%s</a><br>\n'%(w)
        pstr += '</div>\n'        
        pstr += '<table class="file-table">\n'

        pstr += '    <tr class="file-row">\n'
        pstr += '        <td class="folder-indicator">+</td>\n'
        pstr += '        <td class="folder-name">..</td>\n'
        pstr += '    </tr>\n'

        for folder in folders:
            if folder[0]!='.' or folder == '.ada':
                pstr += '    <tr class="file-row">\n'
                pstr += '        <td class="folder-indicator">+</td>\n'
                pstr += '        <td class="folder-name">%s</td>\n'%(folder)
                pstr += '    </tr>\n'

        for file in files:
            if file[0]!='.':
                pstr += '    <tr class="file-row">\n'
                pstr += '        <td class="folder-indicator"></td>\n'
                pstr += '        <td class="folder-name">%s</td>\n'%(file)
                pstr += '    </tr>\n'

        pstr += '</table>\n'
        pstr += '</div>\n'

        return pstr

    def generateGeometryHTML(self):
        divString = ''
        for i,ni in enumerate(self.geometryItems):
            isActive = False
            if i==self.activeGeometry:
                isActive = True
            divString += ni.print_html(i+1, isActive)
            divString += '\n'
        return divString

    def generateAnalysisHTML(self):
        divString = ''
        for ky,ail in self.analysisItems.items():
            divString += '<div class="analysis-tool-name">%s</div>\n'%(ail[0].toolName)
            for i,ni in enumerate(ail):
                isActive = False
                if i==self.activeAnalysis[1]:
                    isActive = True
                divString += ni.print_html(i+1, isActive)
                divString += '\n'
        return divString

    def generateDataHTML(self):
        pstr = ''

        pstr += '<div class="data-table-container">\n'
        pstr += '<table class="data-table">\n'
        pstr += '    <tr class="data-row">\n'
        pstr += '        <td class="data-table-index">Index</td>\n'
        pstr += '        <td class="data-table-query">Query</td>\n'
        pstr += '        <td class="data-table-tool">Tool</td>\n'
        pstr += '        <td class="data-table-casenumber">Case</td>\n'
        pstr += '        <td class="data-table-geometry">Geometry</td>\n'
        pstr += '    </tr>\n'

        for i,dta in enumerate(self.dataItems):
            if self.activeDataItems is not None:
                if i in self.activeDataItems:
                    pstr += '    <tr class="data-row active">\n'
                else:
                    pstr += '    <tr class="data-row">\n'
            else:
                pstr += '    <tr class="data-row">\n'
            pstr += '        <td class="data-table-index">%d</td>\n'%(i+1)
            pstr += '        <td class="data-table-query">%s</td>\n'%(dta['queryIndex'])
            pstr += '        <td class="data-table-tool">%s</td>\n'%(dta['analysisIndex'][0])
            pstr += '        <td class="data-table-casenumber">%d</td>\n'%(dta['analysisIndex'][1]+1)
            pstr += '        <td class="data-table-geometry">%d</td>\n'%(dta['geometryIndex']+1)
            pstr += '    </tr>\n'

        pstr += '</table>\n'
        pstr += '</div>\n'
        # print(pstr)
        return pstr

    def generateGraphicWindow(self):
        res = self.graphicWindowDictionary
        self.graphicWindowDictionary = {}
        return res
        

    def makeCall(self, ipt, callMode='Functions', portNumber=8000):
        if callMode == '_FileClick':
            if ipt[0] == '+':
                if ipt == '+..':
                    pth = Path(self.workingDirectory)
                    # self.workingDirectory = str(pth[0:-1])
                    self.workingDirectory = str(pth.resolve().parent)
                else:
                    pth = Path(self.workingDirectory)
                    # pth.append(ipt[1:])
                    self.workingDirectory = str(os.path.join(pth,ipt[1:]))
            else:
                pth = Path(self.workingDirectory)
                filepath = str(os.path.join(pth,ipt))

                if platform.system() == 'Darwin':       # macOS
                    subprocess.call(('open', filepath))
                elif platform.system() == 'Windows':    # Windows
                    os.startfile(filepath)
                else:                                   # linux variants
                    subprocess.call(('xdg-open', filepath))

        elif ipt != '':
            callDir = os.path.join(self.sessionDirectory,  'Call_%d'%(len(self.calls)+1))
            if os.path.exists(callDir):
                shutil.rmtree(callDir)
            os.mkdir( callDir )

            c = Call()
            c.query = ipt

            if callMode == 'Functions':
                c.callMode = 'Functions'

                xfoil = xfoilAPI()
                functionAllocationDict2 = xfoil.return_handle_map()
                functionData2 = xfoil.return_function_data()

                lapi = LocalAPI()
                functionAllocationDict = lapi.return_handle_map()
                functionData = lapi.return_function_data()

                functionAllocationDict = functionAllocationDict | functionAllocationDict2
                functionData += functionData2

                # print(json.dumps(functionData,indent=4))
                opt = 'No task performed'
                if "::" in ipt:
                    ipt_split = ipt.split("::")

                    if ipt_split[0] in functionAllocationDict.keys():
                        if len(ipt_split) == 1:
                            opt = functionAllocationDict[ipt_split[0]]()
                            processed_inputs = ''
                        else:
                            opt = functionAllocationDict[ipt_split[0]](ipt_split[1])
                            processed_inputs = ipt_split[1]

                        c.interpretaion = ipt_split[0] + " : " + processed_inputs
                        c.response = opt
                    
                    else:
                        opt = "FAILURE:  OpenAI called for function '%s' that is not available"%(ipt_split[0])
                        c.interpretaion = "Attempted to call a function" 
                        c.response = opt


                else:
                    opt = 'Called to OpenAI'

                    # if self.activeAnalysis is not None or self.activeGeometry is not None:
                    #     ipt += '.  The following are default values that may be used if no other value is provided:  '
                    #     if self.activeAnalysis is not None:
                    #         ipt += ' toolName=%s   caseIndex=%d'%(self.activeAnalysis[0], self.activeAnalysis[1]+1)
                    #     if self.activeGeometry is not None:
                    #         ipt += '   geometryIndex=%d'%(self.activeGeometry+1)

                    chat_completion = sendToOpenAI(ipt, functionData)

                    if chat_completion.choices[0].message.tool_calls is None:
                        # OpenAI just did bad things, try again
                        chat_completion = sendToOpenAI(ipt, functionData)

                        if chat_completion.choices[0].message.tool_calls is None:
                            # try one more time
                            chat_completion = sendToOpenAI(ipt, functionData)

                            # if this fails, there is probably an actual issue
                            # I've never had something fail 3 times in a row
                    if self._print_calls:
                        print(chat_completion)

                    # print(chat_completion.choices[0].message.tool_calls[0].function.name)
                    # print(json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments))
                    # if chat_completion.choices[0].message.tool_calls[0].function.name == 'multi_tool_use':
                    #     # not currently supported 
                    #     if len(json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)['tool_uses']) == 1:
                    #         # returned a multi_tool_use, but only one function
                    #         functionName = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)['tool_uses'][0]['recipient_name']
                    #         functionName = functionName.replace('functions.','')
                    #         if functionName in functionAllocationDict.keys():
                    #             functionHandle = functionAllocationDict[functionName]
                    #             inputs = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)['tool_uses'][0]['parameters']
                    #             opt = functionHandle(**inputs)
                    #         else:
                    #             opt = "FAILURE:  OpenAI called for function '%s' that is not available"%(functionName)
                    #     else:
                    #         opt = 'FAILURE:  OpenAI attempted to create a workflow of multiple functions'
                    # else:

                    # print(chat_completion.choices[0].message.tool_calls[0].function.name)
                    # print(json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments))

                    functionName = chat_completion.choices[0].message.tool_calls[0].function.name
                    if functionName in functionAllocationDict.keys():
                        functionHandle = functionAllocationDict[functionName]
                        inputs = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)
                        # if functionName in ['plotAirfoilGeometry','run']:
                        #     inputs['portNumber'] = portNumber
                        
                        # if functionName in ['callLLM','callRAG']:
                        #     # use the exact input from the user (LLM can overwrite improperly)
                        #     opt = functionHandle(ipt)
                        #     # print("{'query (overwritten)': %s}"%(ipt))
                        #     c.interpretaion = "Function handling chose to pass the query directly to the %s framework"%(functionName[-3:])
                        #     c.response = opt
                        # else:
                        # if functionName in list(lapi.return_handle_map().keys()):
                        inputs['uiManager']  = self
                        inputs['portNumber'] = portNumber
                        inputs['rawInput']   = ipt

                        opt = functionHandle(**inputs)
                        c.interpretaion = functionName + " : " + str(json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments))
                        c.response = opt

                    else:
                        opt = "FAILURE:  OpenAI called for function '%s' that is not available"%(functionName)
                        c.interpretaion = "Attempted to call a function" 
                        c.response = opt

            elif callMode == 'RAG':
                opt = self.callRAG(ipt, False)
                c.interpretaion = "Passed the query directly to the RAG framework"
                c.response = opt
                c.callMode = 'RAG'

            elif callMode == 'RAG-C':
                opt = self.callRAG(ipt, True)
                c.interpretaion = "Passed the query directly to the RAG framework and requested citations"
                c.response = opt
                c.callMode = 'RAG-C'

            elif callMode == 'LLM':
                opt = self.callLLM(ipt)
                c.interpretaion = "Passed the query directly to LLM"
                c.response = opt
                c.callMode = 'LLM'

            else:
                raise ValueError("Invalid call mode recieved: %s"%(callMode))

            self.calls.append(c)

            callString = json.dumps(c.__dict__, indent = 4)

            f = open(os.path.join(self.sessionDirectory,  'Call_%d'%(len(self.calls)), 'call_log.json'),'w')
            f.write(callString)
            f.close()


    def callLLM(self,query):
        resp = callLLM(self, query)
        return resp

    def callRAG(self,query,citeSources):
        resp = callRAG(self, query,citeSources)
        return resp


