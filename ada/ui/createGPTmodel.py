import datetime
from openai import OpenAI
import time
import json
import pathlib
import os
path_to_here = pathlib.Path(__file__).parent.resolve()

print(path_to_here)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORG"),
)

def getFileIDs():
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG"),
    )
    resDict = {}
    rs = client.files.list()
    for d in rs.data:
        resDict[d.filename] = d.id

    return resDict


def generateExample(query, response, functionData):
    return {
        "messages":[
        {"role": "user", "content": query},
        {"role": "assistant", "function_call": response}
        ],
        "functions": functionData
    }

f = open('functionData.json','r')
functionData = json.load(f)
f.close()


exampleData = [
    ["generate a NACA2412 airfoil"                 , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA2412"}'}],
    ["generate a NACA4420 airfoil"                 , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA4420"}'}],
    ["generate a NACA 3319 airfoil"                , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA3319"}'}],
    ["NACA2816"                                    , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA2816"}'}],
    ["NACA 6321"                                   , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA6321"}'}],
    ["generate NACA 3211"                          , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA3211"}'}],
    ["generate a NACA3322"                         , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA3322"}'}],
    ["create a NACA5521"                           , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA5521"}'}],
    ["construct a NACA6626"                        , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA6626"}'}],
    ["instantiate a NACA2625"                      , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA2625"}'}],
    ["create an instance of a NACA 4321 airfoil"   , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA4321"}'}],
    ["make a NACA3330"                             , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA3330"}'}],
    ["geometry for NACA7221"                       , {"name": "generateAirfoil", "arguments":r'{"aflString":"NACA7221"}'}],
]


examples = []
for exd in exampleData:
    examples.append(generateExample(exd[0], exd[1], functionData))

uploadFileName = 'airfoilDesignTrainingData_%s.jsonl'%(datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))

path_to_uploadFile = os.path.join(path_to_here,'trainingData',uploadFileName)

with open(path_to_uploadFile, 'w') as outfile:
    for entry in examples:
        json.dump(entry, outfile)
        outfile.write('\n')


client.files.create(
  file=open(path_to_uploadFile, "rb"),
  purpose="fine-tune"
)
fls = getFileIDs()

time.sleep(2)

client.fine_tuning.jobs.create(
  training_file=fls[uploadFileName], 
  model="gpt-3.5-turbo",
)
