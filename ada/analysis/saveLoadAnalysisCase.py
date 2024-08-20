import json
from ada.analysis.apis.xfoil import AnalysisCase as xfoilAnalysisCase


def loadAnalysisCase(filename):
    f = open(filename,'r')
    loadDict = json.load(f)
    f.close()
    
    if isinstance(loadDict,list):
        toolName = loadDict[0]['toolName']
    else:
        toolName = loadDict['toolName']
    
    if toolName == 'xfoil':
        acType = xfoilAnalysisCase
    else:
        raise ValueError("Could not find a data structure for tool named '%s' "%(toolName))
    
    if isinstance(loadDict,list):
        acList = []
        for ld in loadDict:
            ac = acType()
            ac.load_from_dict(ld)
            acList.append(ac)
        return acList
    else:
        ac = acType()
        ac.load_from_dict(loadDict)
        return ac


def saveAnalysisCase(filename, analysisCase, indent=4):
    if isinstance(analysisCase,list):
        writableList = [ac.get_serializable() for ac in analysisCase]
        f = open(filename,'w')
        f.write(json.dumps(writableList,indent=indent))
        f.close()
    else:
        f = open(filename,'w')
        f.write(json.dumps(analysisCase.get_serializable(),indent=indent))
        f.close()