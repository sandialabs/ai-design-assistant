from ada.ui.api import API as baseAPI
import json
from ada.analysis.apis.xfoil import AnalysisCase
from ada.analysis.apis.xfoil.run import run as runXFOIL
from ada.analysis.apis.xfoil.standardPlot import standardPlot
from ada.analysis.apis.xfoil.forcePlot import forcePlot
from ada.analysis.apis.xfoil.boundaryLayerPlot import boundaryLayerPlot
from ada.analysis.apis.xfoil.polarPlot import polarPlot
from ada.analysis.apis.xfoil.boundaryLayerPlot import alternativeNameDict as blp_alternativeNameDict
from ada.analysis.apis import currentToolList
import numpy as np
import shutil
import multiprocessing
import os
import datetime
from ada.analysis.saveLoadAnalysisCase import saveAnalysisCase, loadAnalysisCase

def processDataIndicies(uiManager, dataIndicies):
    if dataIndicies == 'None':
        dataIndicies = uiManager.activeDataItems
        if dataIndicies is None:
            return 'Must provide a data set to generate a plot'

    elif isinstance(dataIndicies,list):
        dataIndicies = [int(di)-1 for di in dataIndicies]
    else:
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

        dataIndicies = setVal

    return dataIndicies

# def generateXfoilResult(rc):
#     if 'cl' in list(rc.inputs.store.keys()):
#         xfoil_mode = 'cl'
#         xfoil_value = rc.inputs['cl']
#     else:
#         xfoil_mode = 'alfa'
#         xfoil_value = rc.inputs['alpha']

#     # fileLeader = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1))
#     fileLeader = rc.fileLeader
#     geometry = rc.geometry

#     try:
#         process_id = rc.process_id
#     except:
#         process_id = ''

#     res = runXFOIL(mode                    = xfoil_mode, 
#                    upperKulfanCoefficients = [c.magnitude for c in geometry.upperCoefficients],
#                    lowerKulfanCoefficients = [c.magnitude for c in geometry.lowerCoefficients],
#                    val                     = xfoil_value, 
#                    Re                      = rc.inputs['re'], 
#                    M                       = rc.inputs['mach'], 
#                    N_panels                = rc.inputs['n_panels'], 
#                    N_crit                  = rc.inputs['n_crit'], 
#                    xtr_u                   = rc.inputs['xtr_u'], 
#                    xtr_l                   = rc.inputs['xtr_l'],
#                    flapLocation            = None,
#                    flapDeflection          = 0.0,
#                    polarfile               = str(fileLeader) + os.sep + 'polars%s.txt'%('_'+str(process_id)),
#                    cpDatafile              = str(fileLeader) + os.sep + 'cp_x%s.txt'%('_'+str(process_id)),
#                    blDatafile              = str(fileLeader) + os.sep + 'bl%s.txt'%('_'+str(process_id)),
#                    defaultDatfile          = str(fileLeader) + os.sep + 'airfoil%s.dat'%('_'+str(process_id)),
#                    executionFile           = str(fileLeader) + os.sep + 'wrtfl%s.txt'%('_'+str(process_id)),
#                    stdoutFile              = str(fileLeader) + os.sep + 'stdout%s.txt'%('_'+str(process_id)),
#                    tempFileTrailer         = str(process_id),
#                    saveDatfile             = True,
#                    removeData              = False,
#                    max_iter                = 200)

#     if res is None:
#         return 'FAILURE: Xfoil did not return a result'
#     else:
#         if xfoil_mode == 'alfa':
#             rc.outputs['cl']      = res['cl']
#         else:
#             rc.outputs['alpha']   = res['alpha']

#         rc.outputs['bl_data'] = res['bl_data']
#         rc.outputs['cd']      = res['cd']
#         rc.outputs['cm']      = res['cm']
#         rc.outputs['cp_data'] = res['cp_data']
#         rc.outputs['xtr_l']   = res['xtr_bot']
#         rc.outputs['xtr_u']   = res['xtr_top']

#         rc.geometry = {}
#         rc.geometry['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
#         rc.geometry['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]

#         rc.mutableLock  = True
#         return rc


def generateXfoilResult(rcDict):
    if 'cl' in list(rcDict.keys()):
        xfoil_mode = 'cl'
        xfoil_value = rcDict['cl']
    else:
        xfoil_mode = 'alfa'
        xfoil_value = rcDict['alpha']

    fileLeader = rcDict['fileLeader']
    upperKulfanCoefficients = rcDict['upperKulfanCoefficients']
    lowerKulfanCoefficients = rcDict['lowerKulfanCoefficients']
    process_id = rcDict['process_id']

    res = runXFOIL(mode                    = xfoil_mode, 
                   upperKulfanCoefficients = upperKulfanCoefficients,
                   lowerKulfanCoefficients = lowerKulfanCoefficients,
                   val                     = xfoil_value, 
                   Re                      = rcDict['re'], 
                   M                       = rcDict['mach'], 
                   N_panels                = rcDict['n_panels'], 
                   N_crit                  = rcDict['n_crit'], 
                   xtp_u                   = rcDict['xtp_u'], 
                   xtp_l                   = rcDict['xtp_l'],
                   flapLocation            = None,
                   flapDeflection          = 0.0,
                   polarfile               = None, # str(fileLeader) + os.sep + 'polars%s.txt'%('_'+str(process_id)),
                   cpDatafile              = None, # str(fileLeader) + os.sep + 'cp_x%s.txt'%('_'+str(process_id)),
                   blDatafile              = None, # str(fileLeader) + os.sep + 'bl%s.txt'%('_'+str(process_id)),
                   defaultDatfile          = None, # str(fileLeader) + os.sep + 'airfoil%s.dat'%('_'+str(process_id)),
                   executionFile           = None, # str(fileLeader) + os.sep + 'wrtfl%s.txt'%('_'+str(process_id)),
                   stdoutFile              = None, # str(fileLeader) + os.sep + 'stdout%s.txt'%('_'+str(process_id)),
                   # tempFileTrailer         = str(process_id),
                   # saveDatfile             = True,
                   # removeData              = False,
                   TE_gap                  = 0.0,
                   timeout                 = 5.0,
                   max_iter                = 200)

    if res is None:
        return None
    else:
        outputDict = {}
        if xfoil_mode == 'alfa':
            outputDict['cl']      = res['cl']
        else:
            outputDict['alpha']   = res['alpha']

        outputDict['bl_data'] = res['bl_data']
        outputDict['cd']      = res['cd']
        outputDict['cm']      = res['cm']
        outputDict['cp_data'] = res['cp_data']
        outputDict['xtp_l']   = res['xtp_bot']
        outputDict['xtp_u']   = res['xtp_top']
        outputDict['xtr_l']   = res['xtr_bot']
        outputDict['xtr_u']   = res['xtr_top']

        # rc.geometry = {}
        # rc.geometry['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
        # rc.geometry['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]
        # rc.mutableLock  = True
        return outputDict



def makeBasicData():
    functionDict = {}
    functionDict['name']=None
    functionDict['description']=None
    functionDict['parameters']={}
    functionDict['parameters']['type']='object'
    
    functionDict['parameters']['properties']={}
    
    # The analysisTool argument will be filtered out before it reaches here by the uiManager, but this is requred to make the sorting happen
    functionDict['parameters']['properties']['toolName']={}
    functionDict['parameters']['properties']['toolName']['type']="string"
    functionDict['parameters']['properties']['toolName']['enum']=currentToolList
    functionDict['parameters']['properties']['toolName']['description']="The analysis tool being run.  If cannot determine unambiguously, return the string 'None'."

    functionDict['parameters']['properties']['caseIndex']={}
    functionDict['parameters']['properties']['caseIndex']['type']="string"
    functionDict['parameters']['properties']['caseIndex']['description']="The index (an integer) of the case being used in the function.  If cannot determine unambiguously, return the string 'None'."
    
    functionDict['parameters']['properties']['geometryIndex']={}
    functionDict['parameters']['properties']['geometryIndex']['type']="string"
    functionDict['parameters']['properties']['geometryIndex']['description']="The index (an integer) of the geometry being used in the function.  If cannot determine unambiguously, return the string 'None'."
    
    functionDict['parameters']['required']=['toolName','caseIndex','geometryIndex']
    # functionDict['parameters']['required']=['caseIndex','geometryIndex']
    
    return functionDict

class API_UI(baseAPI):
    def __init__(self):
        pass

    def return_function_data(self):
        # raise ValueError('Base class method not overwritten')
        
        
        functionData = []
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_boundaryLayerPlot'
        functionDict['description']='Plots the boundary layer parameters of a 2D airfoil'

        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be used by the function.  If cannot determine unambiguously, return the string 'None'."

        functionDict['parameters']['properties']['parameter']={}
        functionDict['parameters']['properties']['parameter']['type']="string"
        functionDict['parameters']['properties']['parameter']['enum']=list(blp_alternativeNameDict.keys())
        functionDict['parameters']['properties']['parameter']['description']="The boundary layer parameter to be plotted.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required']=['toolName']
        functionDict['parameters']['required'].extend(['dataIndicies','parameter'])

        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_forcePlot'
        functionDict['description']='Plots forces acting on a 2D airfoil'

        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be used by the function.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required']=['toolName']
        functionDict['parameters']['required'].extend(['dataIndicies'])

        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_polarPlot'
        functionDict['description']='Plots the polar for a 2D airfoil'

        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be used by the function.  If cannot determine unambiguously, return the string 'None'."

        functionDict['parameters']['required']=['toolName']
        functionDict['parameters']['required'].extend(['dataIndicies'])

        functionData.append(functionDict)

        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_sweepPlot'
        functionDict['description']='Plots a sweep for a 2D airfoil'
        functionData.append(functionDict)
        
        # ================================================================================================================================
        # functionDict = makeBasicData()
        # functionDict['name']='analysis_apis_xfoil_run'
        # functionDict['description']='Runs XFOIL.  This function is likely to be called by either "run xofil", "run xfoil analysis", "run xfoil case" or similar'
        # functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_standardPlot'
        functionDict['description']='Creates the standard plot expected by most XFOIL users'
        
        functionDict['parameters']['properties']['dataIndicies']={}
        functionDict['parameters']['properties']['dataIndicies']['type']="string"
        functionDict['parameters']['properties']['dataIndicies']['description']="A square bracket bounded list of integers (ex: [1,2,3,4,5]) that is the list of indicies to be used by the function.  If cannot determine unambiguously, return the string 'None'."
        
        functionDict['parameters']['required']=['toolName']
        functionDict['parameters']['required'].extend(['dataIndicies'])

        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_modifyAnalysisCase'
        functionDict['description']='Modifies the parameters of the current analysis case.  Inputs that are a string in the enumerated list followed by a parseable value seperated by a whitespace are likely to be an attempt to call this function.  Ex: alfa 10.  Ex: alpha (-10,10,21).  Ex: n_panels 200.  Ex: reynolds number [1e6,1e7,1e8]'
        
        functionDict['parameters']['properties']['parameter']={}
        functionDict['parameters']['properties']['parameter']['type']="string"
        
        pel = []
        ac = AnalysisCase()
        for ky, vl in ac.inputs.info.items():
            pel.extend(vl['alternativeNames'])
            if ky not in pel:
                pel.append(ky)
        
        functionDict['parameters']['properties']['parameter']['enum']=pel
        functionDict['parameters']['properties']['parameter']['description']=("The name of the parameter that is being modified.  It is likely that this function will be called only by using one of the enumerated parameters followed by a value.  For example, " + 
                                                                              "an input of 'alpha 10' should become {'parameter':'alpha', 'value':'10'}, and 'alpha (-10,10,21)' should become {'parameter':'alpha', 'value':'(-10,10,21)'} and similar.  " )

        functionDict['parameters']['properties']['value']={}
        functionDict['parameters']['properties']['value']['type']="string"
        functionDict['parameters']['properties']['value']['description']="The value to set the parameter to.  This can be a single number, a list of number contained within parenthesis, ex: (-10,10,30), or a list contained withing square brackets, ex: [1,2,3,4,5]"
        
        functionDict['parameters']['required'].extend(['parameter','value'])

        functionData.append(functionDict)
        
        # ================================================================================================================================
        functionDict = makeBasicData()
        functionDict['name']='analysis_apis_xfoil_addAnalysisCase'
        functionDict['description']='Creates a new XFOIL analysis case.  This function is frequently called via "xfoil case", "xfoil analysis", "xfoil analysis case" or similar'
        functionData.append(functionDict)
        
        # ================================================================================================================================
        return functionData

    def return_handle_map(self):
        ldr = 'analysis_apis_xfoil_'

        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]

        handle_map = {}
        for mth in method_list:
            if mth not in ['return_function_data', 'return_handle_map', 'run']:
                handle_map[ldr + mth] = getattr(self, mth)
        return handle_map

    def run(self, uiManager, toolName, caseIndex, geometryIndex, portNumber, **kwargs):
        # Handled by the outer run wrapper
        # if toolName == 'None':
        #     toolName = uiManager.activeAnalysis[0]
        # if caseIndex == 'None':
        #     caseIndex = uiManager.activeAnalysis[1]+1
        # if geometryIndex == 'None':
        #     geometryIndex = uiManager.activeGeometry+1

        ncores = multiprocessing.cpu_count()
        if shutil.which('mpirun') is not None:
            # multiprocessing available
            pass  

        analysisCase = uiManager.analysisItems[toolName][caseIndex-1]
        uiManager.analysisItems[toolName][caseIndex-1].mutableLock = True
        rcs = analysisCase.generateSingleCases()

        geometry = uiManager.geometryItems[geometryIndex-1]
        uiManager.geometryItems[geometryIndex-1].mutableLock = True
        
        if 'cl' in list(analysisCase.inputs.store.keys()):
            xfoil_mode = 'cl'
            xfoil_value = analysisCase.inputs['cl']
        else:
            xfoil_mode = 'alfa'
            xfoil_value = analysisCase.inputs['alpha']

        if len(rcs) == 1:
            rc = rcs[0]
            rcDict = {}
            if xfoil_mode == 'cl':
                rcDict['cl'] = xfoil_value
            else:
                rcDict['alpha'] = xfoil_value

            rcDict['fileLeader']              = str(os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1)))
            rcDict['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
            rcDict['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]
            rcDict['process_id']              = 0
            rcDict['re']                      = rc.inputs['re']
            rcDict['mach']                    = rc.inputs['mach']
            rcDict['n_panels']                = rc.inputs['n_panels']
            rcDict['n_crit']                  = rc.inputs['n_crit']
            rcDict['xtp_u']                   = rc.inputs['xtp_u']
            rcDict['xtp_l']                   = rc.inputs['xtp_l']
            # rcDict['xtr_u']                   = rc.inputs['xtr_u']
            # rcDict['xtr_l']                   = rc.inputs['xtr_l']

            resDict = generateXfoilResult(rcDict)

            if xfoil_mode == 'alfa':
                rc.outputs['cl']      = resDict['cl']
            else:
                rc.outputs['alpha']   = resDict['alpha']

            rc.outputs['bl_data'] = resDict['bl_data']
            rc.outputs['cd']      = resDict['cd']
            rc.outputs['cm']      = resDict['cm']
            rc.outputs['cp_data'] = resDict['cp_data']
            rc.outputs['xtr_l']   = resDict['xtr_l']
            rc.outputs['xtr_u']   = resDict['xtr_u']

            rc.geometry = {}
            rc.geometry['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
            rc.geometry['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]

            rc.mutableLock  = True

            results = rc

        else:
            results = []

            rcDicts = []
            for i,rc in enumerate(rcs):
                rcDict = {}
                if xfoil_mode == 'cl':
                    rcDict['cl'] = rc.inputs['cl']
                else:
                    rcDict['alpha'] = rc.inputs['alpha']

                rcDict['fileLeader']              = str(os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1)))
                rcDict['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
                rcDict['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]
                rcDict['process_id']              = i
                rcDict['re']                      = rc.inputs['re']
                rcDict['mach']                    = rc.inputs['mach']
                rcDict['n_panels']                = rc.inputs['n_panels']
                rcDict['n_crit']                  = rc.inputs['n_crit']
                rcDict['xtp_u']                   = rc.inputs['xtp_u']
                rcDict['xtp_l']                   = rc.inputs['xtp_l']

                rcDicts.append(rcDict)

            pool = multiprocessing.Pool()  
            resDicts = pool.map(generateXfoilResult, rcDicts)
            pool.close()

            for i,rc in enumerate(rcs):
                resDict = resDicts[i]
                if resDict is not None:
                    if xfoil_mode == 'alfa':
                        rc.outputs['cl']      = resDict['cl']
                    else:
                        rc.outputs['alpha']   = resDict['alpha']

                    rc.outputs['bl_data'] = resDict['bl_data']
                    rc.outputs['cd']      = resDict['cd']
                    rc.outputs['cm']      = resDict['cm']
                    rc.outputs['cp_data'] = resDict['cp_data']
                    rc.outputs['xtr_l']   = resDict['xtr_l']
                    rc.outputs['xtr_u']   = resDict['xtr_u']

                    rc.geometry = {}
                    rc.geometry['upperKulfanCoefficients'] = [c.magnitude for c in geometry.upperCoefficients]
                    rc.geometry['lowerKulfanCoefficients'] = [c.magnitude for c in geometry.lowerCoefficients]

                    rc.mutableLock  = True
                    results.append(rc)

        dataOutput = {}
        dataOutput['analysisIndex'] = uiManager.activeAnalysis
        dataOutput['geometryIndex'] = uiManager.activeGeometry
        dataOutput['queryIndex']    = len(uiManager.calls)+1
        dataOutput['data']          = results
        uiManager.dataItems.append(dataOutput)
        if uiManager.activeDataItems is None:
            uiManager.activeDataItems = []
        uiManager.activeDataItems.append(len(uiManager.dataItems)-1)

        if isinstance(results, list):
            for r in results:
                r.analysisIndex = uiManager.activeAnalysis
                r.geometryIndex = uiManager.activeGeometry
                r.queryIndex    = len(uiManager.calls)+1
        else:
            results.analysisIndex = uiManager.activeAnalysis
            results.geometryIndex = uiManager.activeGeometry
            results.queryIndex    = len(uiManager.calls)+1

        saveAnalysisCase(os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), 'generatedData.json'), results, indent=4)

        if isinstance(results,list):
            return 'Query task complete'
        else:
            return self.standardPlot(uiManager, [len(uiManager.dataItems)], portNumber)

    def standardPlot(self, uiManager, dataIndicies, portNumber, **kwargs):

        dataIndicies = processDataIndicies(uiManager, dataIndicies)

        inputDataList = []

        for di in dataIndicies:
            data = uiManager.dataItems[di]['data']
            if isinstance(data, list):
                return 'Data sweep passed in, could not complete request'
            inputData = {}
            if 'alpha' in list(data.inputs.keys()):
                inputData['alpha']             = data.inputs['alpha']
                inputData['cl']                = data.outputs['cl']
            else:
                inputData['alpha']             = data.outputs['alpha']
                inputData['cl']                = data.inputs['cl']

            inputData['cm']                = data.outputs['cm']
            inputData['cd']                = data.outputs['cd']
            inputData['re']                = data.inputs['re']
            inputData['n_crit']            = data.inputs['n_crit']
            inputData['xtp_u']             = data.inputs['xtp_u']
            inputData['xtp_l']             = data.inputs['xtp_l']
            inputData['xtr_u']             = data.outputs['xtr_u']
            inputData['xtr_l']             = data.outputs['xtr_l']
            inputData['cp_data']           = {}
            inputData['cp_data']['x']      = data.outputs['cp_data']['x']
            inputData['cp_data']['cp']     = data.outputs['cp_data']['cp']
            inputData['bl_data']           = {}
            inputData['bl_data']['x']      = data.outputs['bl_data']['x']
            inputData['bl_data']['y']      = data.outputs['bl_data']['y']
            inputData['bl_data']['Dstar']  = data.outputs['bl_data']['Dstar']

            inputDataList.append(inputData)

        stPlot = standardPlot(inputDataList)

        dt_string = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f")
        file_location = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        relative_file_location = os.path.join(uiManager.relativeSessionDirectory , 'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        stPlot.savefig(file_location)

        file_location2 = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.png')
        stPlot.savefig(file_location2)

        return '<img src="http://localhost:'+str(portNumber)+'/'+ relative_file_location + '" width="80%" alt="Image">\n'


    def boundaryLayerPlot(self, uiManager, dataIndicies, parameter, portNumber, **kwargs):

        dataIndicies = processDataIndicies(uiManager, dataIndicies)

        inputDataList = []

        for di in dataIndicies:
            data = uiManager.dataItems[di]['data']
            if isinstance(data, list):
                return 'Data sweep passed in, could not complete request'
            inputData = {}
            if 'alpha' in list(data.inputs.keys()):
                inputData['alpha']             = data.inputs['alpha']
                inputData['cl']                = data.outputs['cl']
            else:
                inputData['alpha']             = data.outputs['alpha']
                inputData['cl']                = data.inputs['cl']

            inputData['cm']                = data.outputs['cm']
            inputData['cd']                = data.outputs['cd']
            inputData['re']                = data.inputs['re']
            inputData['n_crit']            = data.inputs['n_crit']
            inputData['xtp_u']             = data.inputs['xtp_u']
            inputData['xtp_l']             = data.inputs['xtp_l']
            inputData['xtr_u']             = data.outputs['xtr_u']
            inputData['xtr_l']             = data.outputs['xtr_l']
            inputData['cp_data']           = data.outputs['cp_data']
            inputData['bl_data']           = data.outputs['bl_data']

            inputDataList.append(inputData)


        blPlot = boundaryLayerPlot(inputDataList,parameter,[di+1 for di in dataIndicies])

        dt_string = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f")
        file_location = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        relative_file_location = os.path.join(uiManager.relativeSessionDirectory , 'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        blPlot.savefig(file_location)

        file_location2 = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.png')
        blPlot.savefig(file_location2)

        return '<img src="http://localhost:'+str(portNumber)+'/'+ relative_file_location + '" width="80%" alt="Image">\n'


    def forcePlot(self, uiManager, dataIndicies, portNumber, **kwargs ):

        dataIndicies = processDataIndicies(uiManager, dataIndicies)

        pstr = ''
    
        for di in dataIndicies:
            data = uiManager.dataItems[di]['data']
            if isinstance(data, list):
                return 'Data sweep passed in, could not complete request'
            inputData = {}
            if 'alpha' in list(data.inputs.keys()):
                inputData['alpha']             = data.inputs['alpha']
                inputData['cl']                = data.outputs['cl']
            else:
                inputData['alpha']             = data.outputs['alpha']
                inputData['cl']                = data.inputs['cl']

            inputData['cm']                = data.outputs['cm']
            inputData['cd']                = data.outputs['cd']
            inputData['re']                = data.inputs['re']
            inputData['n_crit']            = data.inputs['n_crit']
            inputData['xtp_u']             = data.inputs['xtp_u']
            inputData['xtp_l']             = data.inputs['xtp_l']
            inputData['xtr_u']             = data.outputs['xtr_u']
            inputData['xtr_l']             = data.outputs['xtr_l']
            inputData['cp_data']           = data.outputs['cp_data']
            inputData['bl_data']           = data.outputs['bl_data']

            # inputDataList.append(inputData)

            fPlot = forcePlot(inputData)

            dt_string = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f")
            file_location = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
            relative_file_location = os.path.join(uiManager.relativeSessionDirectory , 'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
            fPlot.savefig(file_location)

            file_location2 = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.png')
            fPlot.savefig(file_location2)

            pstr += '<img src="http://localhost:'+str(portNumber)+'/'+ relative_file_location + '" width="80%" alt="Image">\n<br>\n'

        return pstr


    def sweepPlot(self, uiManager):
        pass

    def polarPlot(self, uiManager, dataIndicies, portNumber, **kwargs):
        dataIndicies = processDataIndicies(uiManager, dataIndicies)
        # if len(dataIndicies) > 1:
        #     return 'Error: polar plot takes in a single data index of a sweep'

        outerDataList = []
        for di in dataIndicies:
            data = uiManager.dataItems[di]['data']

            if not isinstance(data,list):
                return 'Error: polar plot must take a sweep data instance'            

            dataList = []
            for idata in data:
                dataDict = {}
                if 'alpha' in list(idata.inputs.keys()):
                    dataDict['alpha']             = idata.inputs['alpha']
                    dataDict['cl']                = idata.outputs['cl']
                else:
                    dataDict['alpha']             = idata.outputs['alpha']
                    dataDict['cl']                = idata.inputs['cl']

                dataDict['cd']       = idata.outputs['cd']
                dataDict['cm']       = idata.outputs['cm']
                dataDict['xtp_u']    = idata.inputs['xtp_u']
                dataDict['xtp_l']    = idata.inputs['xtp_l']
                dataDict['xtr_u']    = idata.outputs['xtr_u']
                dataDict['xtr_l']    = idata.outputs['xtr_l']
                dataDict['re']       = idata.inputs['re']
                dataDict['m']        = idata.inputs['m']
                dataDict['n_crit']   = idata.inputs['n_crit']
                dataDict['n_panels'] = idata.inputs['n_panels']

                dataList.append(dataDict)

            outerDataList.append(dataList)

        pPlot = polarPlot(outerDataList)

        dt_string = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f")
        file_location = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        relative_file_location = os.path.join(uiManager.relativeSessionDirectory , 'Call_%d'%(len(uiManager.calls)+1), dt_string + '.svg')
        pPlot.savefig(file_location)

        file_location2 = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + '.png')
        pPlot.savefig(file_location2)

        pstr = '<img src="http://localhost:'+str(portNumber)+'/'+ relative_file_location + '" width="80%" alt="Image">\n<br>\n'

        return pstr




    def modifyAnalysisCase(self, uiManager, toolName, caseIndex, parameter, value, **kwargs):
        # handle manual mode
        # if ':' in parameter:
        #     ipt_split = parameter.split(':')
        #     parameter = ipt_split[0]
        #     value = ipt_split[1]

        if toolName == 'None':
            toolName = uiManager.activeAnalysis[0]
        if caseIndex == 'None':
            caseIndex = uiManager.activeAnalysis[1]+1

        setVal = None
        try:
            setVal = float(value)
        except:
            # is not a single nubmer
            pass

        try:
            values = []
            if (value[0] == '[' and value[-1] == ']') or (value[0] == '{' and value[-1] == '}'):
                vl = value[1:-1]
                vl_split = vl.split(',')
                setVal = [float(v) for v in vl_split]
            elif value[0] == '(' and value[-1] == ')':
                vl = value[1:-1]
                vl_split = vl.split(',')
                if len(vl_split) == 3 and float(vl_split[2]).is_integer():
                    setVal = np.linspace(float(vl_split[0]),float(vl_split[1]),int(vl_split[2])).tolist()
                else:
                    setVal = [float(v) for v in vl_split]
            else:
                # will fail
                pass

        except:
            # could not extract an array, will now fail
            pass

        if setVal is None:
            return "FAILURE: Could not parse '%s' into a valid value for parameter %s"%(value,parameter)

        if uiManager.analysisItems[toolName][int(caseIndex)-1].mutableLock:
            rc1 = uiManager.analysisItems[toolName][int(caseIndex)-1].free_copy()
            uiManager.analysisItems[toolName].append(rc1)

            uiManager.activeAnalysis = (uiManager.activeAnalysis[0], len(uiManager.analysisItems[toolName])-1)
            uiManager.analysisItems[toolName][len(uiManager.analysisItems[toolName])-1].inputs[parameter] = setVal

        else:
            uiManager.analysisItems[toolName][int(caseIndex)-1].inputs[parameter] = setVal
        return "Query task complete"

    def addAnalysisCase(self, uiManager, **kwargs):
        rc1 = AnalysisCase()

        if rc1.toolName not in list(uiManager.analysisItems.keys()):
            uiManager.analysisItems[rc1.toolName] = []

        uiManager.analysisItems[rc1.toolName].append(rc1)
        uiManager.activeAnalysis = (rc1.toolName , len(uiManager.analysisItems[rc1.toolName])-1 )
        return "Query task complete"


























