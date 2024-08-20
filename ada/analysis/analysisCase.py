import itertools
from collections.abc import MutableMapping
import numpy as np
import json
import copy
import importlib


class IODict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.mutuallyExclusive = []
        self.info = {}
        self._mutableLock = False

    def __getitem__(self, key):
        return self.store[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.mutableCheck()
        key = self._keytransform(key)
        for meiList in self.mutuallyExclusive:
            if key in meiList:
                kys = list(self.store.keys())
                for ky2 in kys:
                    if ky2 in meiList:
                        del self.store[ky2]

        self.store[key] = value
        self.store = dict(sorted(self.store.items()))

    def __delitem__(self, key):
        self.mutableCheck()
        del self.store[self._keytransform(key)]
        
    def __iter__(self):
        return iter(self.store)
    
    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        for ky, vl in self.info.items():
            altNames = vl['alternativeNames']
            chk_ky = key.lower().replace(' ','').replace('_','')
            if chk_ky in altNames:
                return ky
            if key.lower() == ky:
                return ky
            
        raise ValueError('Could not find key "%s" in the dictionary'%(key))
        
    def mutableCheck(self):
        if self._mutableLock:
            raise ValueError('Analysis has been run, all data is locked')
    
    def __repr__(self):
        return self.store.__repr__()


class AnalysisCase():
    def __init__(self):
        self.toolName = None
        self.toolAPIpath = None
        self.plottingParameters = {'linewidth':None,
                                   'marker':None,
                                   'linestyle':None,
                                   'color':None}
        
        self.inputs  = IODict()
        self.outputs = IODict()

        self.analysisIndex = None
        self.geometryIndex = None
        self.queryIndex    = None

        self._mutableLock = False
        
    def set_defaults(self):
        raise ValueError('Base class method not overwritten')

    def load_from_dict(self,loadDict):
        if self.mutableLock:
            raise ValueError('Analysis has been run, all data is locked')

        # defaults should be correct here
        # self.toolName = loadDict['toolName']
        # self.toolAPIpath = importlib.import_module('ada.analysis.apis.'+self.toolName.lower())
        
        self.plottingParameters = loadDict['plottingParameters']
        self._mutableLock = loadDict['_mutableLock']

        for ipsops in ['inputs','outputs']:
            if 'mutuallyExclusive' in list(loadDict[ipsops].keys()):
                getattr(self,ipsops).mutuallyExclusive = loadDict[ipsops]['mutuallyExclusive']

            if 'store' in list(loadDict[ipsops].keys()):
                for ky, vl in loadDict[ipsops]['store'].items():
                    getattr(self,ipsops)[ky] = vl

            if 'info' in list(loadDict[ipsops].keys()):
                getattr(self,ipsops).info = loadDict[ipsops]['info']

            if '_mutableLock' in list(loadDict[ipsops].keys()):
                getattr(self,ipsops).mutableLock = loadDict[ipsops]['_mutableLock']

        if 'analysisIndex' in list(loadDict.keys()):
            self.analysisIndex = loadDict['analysisIndex']

        if 'geometryIndex' in list(loadDict.keys()):
            self.geometryIndex = loadDict['geometryIndex']

        if 'queryIndex' in list(loadDict.keys()):
            self.queryIndex = loadDict['queryIndex']

        # TODO: rework the geometry package
        if 'geometry' in list(loadDict.keys()):
            self.geometry = loadDict['geometry']
        
    def generateSingleCases(self):
        # native python obects (ie lists, tuples, etc) wrap data
        # numpy arrays ARE data (ie, matricies, tensors, etc)
        # WILL NOT check for this, only check sizes of things assumed to be data
        # this data should not have units, those are handled elsewhere
        
        inputNames = self.inputs.keys()
        prodList = []
        for nm in inputNames:
            vl = self.inputs[nm]
            if vl is not None:
                if isinstance(vl,(list,tuple)):
                    prodList.append(vl)
                    
                elif isinstance(vl, np.ndarray):
                    # should have specified shape
                    assert(self.inputs.info[nm]['shape']==vl.shape)
                    prodList.append([vl])
                    
                else: # should be single number
                    assert(isinstance(vl,(int,float)))
                    prodList.append([vl])

        caseList = list(itertools.product(*prodList))
        if len(caseList) == 1:
            return [self.free_copy()]
        
        else:
            runCases = []
            rcClass = type(self)
            for cs in caseList:
                rc = rcClass()
                for i,nm in enumerate(inputNames):
                    rc.inputs[nm] = cs[i]
                    rc.analysisIndex = self.analysisIndex
                    rc.geometryIndex = self.geometryIndex
                    rc.queryIndex    = self.queryIndex  
                runCases.append(rc)
            return runCases
        
        
    def print_html(self, caseIndex=0, isActive=False ):
        pstr = ''
        if isActive:
            pstr += '<div class="analysis-cell active">\n'
        else:
            pstr += '<div class="analysis-cell">\n'
        if self.mutableLock:
            pstr += '<div class="analysiscase-name">Case %d--Locked</div>\n'%(caseIndex)
        else:
            pstr += '<div class="analysiscase-name">Case %d--Unlocked</div>\n'%(caseIndex)

        for ixr in ['Inputs']:#, 'Outputs']:
            # pstr += '<div class="analysiscase-input-name">%s</div>\n'%(ixr)
            pstr += '<table class="analysiscase-table">\n'
            if ixr == 'Inputs':
                dct = self.inputs
            else:
                dct = self.outputs
             
            for ky,vl in dct.items():
                pstr += '    <tr class="analysiscase-row">\n'
                pstr += '        <td class="qoi-name">%s</td>\n'%(dct.info[ky]['preferredName'])

                if isinstance(vl,list):
                    pstr += '        <td class="qoi-value">(%d Values)</td>\n'%(len(vl))
                    pstr += '        <td class="qoi-unit">%s</td>\n'%(dct.info[ky]['units'])

                else:
                    if isinstance(vl, np.ndarray):
                        pstr += '        <td class="qoi-value"><i>Array</i></td>\n'
                        pstr += '        <td class="qoi-unit">%s</td>\n'%(dct.info[ky]['units'])
                    elif isinstance(vl, dict):
                        pstr += '        <td class="qoi-value"><i>Dict</i></td>\n'
                        pstr += '        <td class="qoi-unit"></td>\n'
                    else:
                        assert(isinstance(vl, (float, int)) or vl is None)
                        if vl is None:
                            pstr += '        <td class="qoi-value">None</td>\n'
                            pstr += '        <td class="qoi-unit"></td>\n'
                        else:
                            pstr += ('        <td class="qoi-value">%s</td>\n'%(dct.info[ky]['printFormat']))%(vl)
                            pstr += '        <td class="qoi-unit">%s</td>\n'%(dct.info[ky]['units'])
                pstr += '    </tr>\n'
            pstr += '</table>\n'
        pstr += '</div>'
        return pstr

    def free_copy(self):
        # copies the inputs and unlocks the data
        rcClass = type(self)
        rc = rcClass()
        inputNames = self.inputs.keys()
        for i,nm in enumerate(inputNames):
            rc.inputs[nm] = self.inputs[nm]
            
            rc.analysisIndex = self.analysisIndex
            rc.geometryIndex = self.geometryIndex
            rc.queryIndex    = self.queryIndex   
            
        return rc
        
    def get_serializable(self):
        if self.mutableLock:
            scs = self.generateSingleCases()
            if len(scs) != 1:
                # is a locked sweep, but will have no output
                pass
            else:
                # is either locked single or single with output
                dct = {}
                for ky, vl in self.__dict__.items():
                    if ky == 'toolAPIpath':
                        dct[ky] = str(vl)
                    elif ky == 'outputs':
                        dct[ky] = self.outputs.__dict__
                    elif ky == 'inputs':
                        dct[ky] = self.inputs.__dict__
                    else:
                        dct[ky] = vl
                return dct

        # else:
            # scs = self.generateSingleCases()

        retList = []
        for sc in scs:
            dct = {}
            for ky, vl in sc.__dict__.items():
                if ky == 'toolAPIpath':
                    dct[ky] = str(vl)
                elif ky == 'outputs':
                    dct[ky] = sc.outputs.__dict__
                elif ky == 'inputs':
                    dct[ky] = sc.inputs.__dict__
                else:
                    dct[ky] = vl
            retList.append(dct)

        if len(scs) == 1:
            return retList[0]
        else:
            return retList

    @property
    def mutableLock(self):
        return self._mutableLock
    
    @mutableLock.setter
    def mutableLock(self,val):
        if val == True:
            self._mutableLock = True
            self.inputs._mutableLock = True
            self.outputs._mutableLock = True
        else:
            # do nothing, only allow locking, not unlocking
            pass

