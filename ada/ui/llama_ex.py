from llama_index import VectorStoreIndex, SimpleDirectoryReader

# documents = SimpleDirectoryReader("data").load_data()
# print(documents)
# index = VectorStoreIndex.from_documents(documents)

reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
all_docs = []
for docs in reader.iter_data():
    for doc in docs:
        # do something with the doc
        # doc.text = doc.text.upper()
        all_docs.append(doc)
# print(all_docs)
index = VectorStoreIndex.from_documents(all_docs)

query_engine = index.as_query_engine()
print('starting')

# response = query_engine.query("Give an example of a typical xfoil session")
# print(response)

response2 = query_engine.query("Describe the limtations of XFOIL and provide a citation to location in the file")
# response2 = query_engine.query("What might cause inaccurate results or failures when using XFOIL")
# response2 = query_engine.query("What are some best practices for using XFOIL?")
print(response2)

# response3 = query_engine.query("Create a shell script that runs a NACA2412 airfoil at 3 degrees angle of attack, a mach number of 0.2, a reynolds number of 1e7, an upper surface trip at 0.2, a lower surface trip at 0.4, and an N_crit of 6.0 using XFOIL")
# print(response3)

# response4 = query_engine.query("What is the typical climate of San Fransisco?")
# print(response4)

# response5 = query_engine.query("How do I turn off the interactive plotting window in XFOIL?")
# print(response5)

# response6 = query_engine.query("""This script for running xfoil did not converge, how can I fix it:





