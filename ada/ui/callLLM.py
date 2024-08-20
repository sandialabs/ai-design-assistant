import os
from openai import OpenAI

def callLLM(uiManager, ipt, model="gpt-4o"):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG"),
    )


    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": ipt,
            }
        ],
        model = model,
    )

    resp = chat_completion.choices[0].message.content

    resp = resp.replace('\n', '<br>\n')
    if "```" in resp:
        runningRespLines = []
        tempFileLines    = []
        appendLoc = 1
        respLines = resp.split('<br>\n')
        for ln in respLines:
            if "```" in ln:
                if appendLoc == 1:
                    scriptType = ln[3:]
                    runningRespLines.append('<div class="%s-script">'%(scriptType))
                    runningRespLines.append('<div class="file-text">')
                    appendLoc = 2
                else:
                    runningRespLines.append('</div>')
                    runningRespLines.append('</div>')
                    appendLoc = 1

            else:
                # if appendLoc == 1:
                runningRespLines.append(ln)
                # else:
                #     tempFileLines.append('    ' + ln)
        resp = '<br>\n'.join(runningRespLines)

    return resp
