# from ada import rag_query_engine
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.query_engine import CitationQueryEngine
import os
import ada
from llama_index.llms.openai import OpenAI
import datetime



pth_to_data = str(ada.ada_path) + os.sep + "data"
# print(pth_to_data)

def buildRAGqueryEngine(citeSources, llmModel="gpt-4o"):
    reader = SimpleDirectoryReader(input_dir=pth_to_data, recursive=True)
    all_docs = []
    for docs in reader.iter_data():
        for doc in docs:
            all_docs.append(doc)
    index = VectorStoreIndex.from_documents(all_docs)
    llm = OpenAI(model=llmModel)

    if citeSources:
        rag_query_engine = CitationQueryEngine.from_args(
            index,
            similarity_top_k=3,
            # here we can control how granular citation sources are, the default is 512
            citation_chunk_size=200,
            llm=llm,
        )
    else:
        rag_query_engine = index.as_query_engine(llm=llm)

    return rag_query_engine

def callRAG(uiManager, query, citeSources):
    query_engine = buildRAGqueryEngine(citeSources)
    resp_raw = query_engine.query(query)
    resp = str(resp_raw)
    citations = []
    if citeSources:
        for nd in resp_raw.source_nodes:
            citations.append(str(nd.node.get_text()))
        # print(response.source_nodes[0].node.get_text())

    resp = resp.replace('\n', '<br>\n')
    if "```" in resp:
        new_resp_lines = []
        respLines = resp.split('<br>\n')
        inFile = False
        fileLines = []
        for ln in respLines:
            if "```" in ln:
                scriptType = None
                # fileLines = []
                if 'python' in ln or 'shell' in ln:
                    inFile = True
                    fileLines = []
                    scriptType = ln[3:]
                    fileLines.append('<pre class="code-literal">')
                    fileLines.append('<div class="%s-script script">'%(scriptType))
                    fileLines.append('<div class="file-text">')
                    # fileLines.append('    <div class="file-button-overlay">')
                    # fileLines.append('    <button class="copy-button">&#x1F4C4</button>')
                    # fileLines.append('    <button class="copy-button">&#128196</button>')
                    if scriptType == 'shell':
                        fileLines.append('    <button class="copy-button" onclick="copyText(event)"><img class="copy-image" src="copy_icon_white.svg"></button>')
                    elif scriptType == 'python':
                        fileLines.append('    <button class="copy-button" onclick="copyText(event)"><img class="copy-image" src="copy_icon_black.svg"></button>')
                    
                    # fileLines.append('    </div>')

                else:
                    if scriptType == 'shell':
                        ext = '.sh'
                    elif scriptType == 'python':
                        ext = '.py'
                    else:
                        ext = '.txt'

                    dt_string = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S.%f")
                    file_location = os.path.join(uiManager.sessionDirectory,  'Call_%d'%(len(uiManager.calls)+1), dt_string + ext)
                    f = open( file_location , 'w')
                    f.write('\n'.join(fileLines[3:]))
                    f.close()

                    inFile = False
                    fileLines.append('</div>')
                    fileLines.append('</div>')
                    fileLines.append('</pre>')
                    new_resp_lines += fileLines

            elif inFile == True:
                ln_strip = ln.replace('<br>\n','')
                fileLines.append(ln_strip)

            else:
                new_resp_lines.append(ln)

        new_resp = '\n'.join(new_resp_lines)

        for ct in citations:
            new_resp += '<br>\n'
            new_resp += ct.replace('\n','<br>\n')


        return new_resp

    else:
        return resp


# # response = query_engine.query("Give an example of a typical xfoil session")
# # print(response)

# response2 = query_engine.query("Describe the limtations of XFOIL and provide a citation to location in the file")
# # response2 = query_engine.query("What might cause inaccurate results or failures when using XFOIL")
# # response2 = query_engine.query("What are some best practices for using XFOIL?")
# print(response2)

# # response3 = query_engine.query("Create a shell script that runs a NACA2412 airfoil at 3 degrees angle of attack, a mach number of 0.2, a reynolds number of 1e7, an upper surface trip at 0.2, a lower surface trip at 0.4, and an N_crit of 6.0 using XFOIL")
# # print(response3)

# # response4 = query_engine.query("What is the typical climate of San Fransisco?")
# # print(response4)

# # response5 = query_engine.query("How do I turn off the interactive plotting window in XFOIL?")
# # print(response5)

# # response6 = query_engine.query("""This script for running xfoil did not converge, how can I fix it:





