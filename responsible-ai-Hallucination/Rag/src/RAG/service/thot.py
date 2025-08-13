"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


from langchain.chat_models import AzureChatOpenAI
from langchain.vectorstores.faiss import FAISS
import traceback
import pickle
from langchain.prompts import PromptTemplate
import os
import time
from RAG.config.logger import CustomLogger,request_id_var
from langchain.chains import RetrievalQA
from RAG.service.service import cache,MAX_CACHE_SIZE,fs, dbtypename,select_embeddingmodel, select_llmtype
from RAG.dao.AdminDb import collection
import tiktoken

log=CustomLogger()
request_id_var.set("Startup")

# llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL"), temperature=1)
VECTORSTORE_BASE_DIR = "../data/vectorstores/"
embeddingmodelname=os.getenv("EMBEDDING_MODEL_NAME")

def get_price_details(model: str):
    '''
    Returns price per tokens of the model.

    Parameters:
    model (str): Model name (Ex: gpt4)
    '''
    prompt_price_per_1000_tokens = {
        "gpt-4o": 0.0050,
        "gpt-35-turbo": 0.0005,
        "gpt-35-turbo-instruct": 0.0015,
        "gpt-4": 0.0300
    }
    
    response_price_per_1000_tokens = {
        "gpt-4o": 0.0150,
        "gpt-35-turbo": 0.0015,
        "gpt-35-turbo-instruct": 0.0020,
        "gpt-4": 0.0600
    }

    try:
        return prompt_price_per_1000_tokens[model], response_price_per_1000_tokens[model]
    except KeyError:
        raise ValueError(f"Model '{model}' is not found in the pricing details. Only gpt-4o, gpt-35-turbo, gpt-35-turbo-instruct & gpt-4 are available. Please contact administrator")
    
def get_token_cost(input_tokens: int, output_tokens: int, model: str):
    '''
    Calculates the total cost for tokens.

    Parameters:
    tokens (int): Total token (Prompt tokens + Completion tokens)
    model (str): Model name (Ex: gpt4)
    '''

    # Example pricing (this should be replaced with actual pricing from Azure documentation)
    prompt_price_per_1000_tokens, response_price_per_1000_tokens = get_price_details(model)

    # Calculate cost
    total_cost = ((input_tokens / 1000) * prompt_price_per_1000_tokens) + ((output_tokens / 1000) * response_price_per_1000_tokens)

    return {
        "total_cost": total_cost
    }
 
def calculate_token_count(text: str, model_name: str = embeddingmodelname) -> int:
    # Load the appropriate tokenizer for the model
    tokenizer = tiktoken.encoding_for_model(model_name)
    # Encode the text into tokens
    tokens = tokenizer.encode(text)
    # Return the token count
    return len(tokens)


def thot(text,fileupload,llmtype,vectorestoreid=None):
    """
    Function to generate a Thread of Thoughts (ThOT) response using the Langchain library and a vector store.
    """
    starttime = time.time()
    if fileupload==True:
        res = []
        log.info("Before llm calling")
        # with open("../data/docs/"+str(id)+"/DefaultVectorstore.pkl","rb") as file:
        #  vectorstore =pickle.load(file)
        if llmtype=="openai":
            if dbtypename=="mongo":
                vectorstore = pickle.loads(fs.get_last_version(_id=vectorestoreid+"vectorstore",filename="vectorstore.pkl").read())
            else:
                #########################
                # Define the filter to retrieve the document
                filter = {"id": vectorestoreid + "vectorstore"}
                document = collection.find_one(filter)
                if document:
                    vectorstore_binary = document["data"]
                    vectorstore = pickle.loads(vectorstore_binary)
                    print("Vectorstore retrieved successfully!")
                else:
                    print("Document not found!")
        else:
            vectorstore_path = f"{VECTORSTORE_BASE_DIR}{vectorestoreid}/"
            embedding_function = select_embeddingmodel(llmtype)
        
            # Load vectorstore using FAISS native method
            vectorstore = FAISS.load_local(
                vectorstore_path, 
                embedding_function, 
                allow_dangerous_deserialization=True
            )
            
            print(f"Vectorstore loaded successfully from: {vectorstore_path}")
            #################################
        log.info("Vectorstore loaded")
        retriever=vectorstore.as_retriever()

    else:
        starttime = time.time()
        res = []
        log.info("Before llm calling")
        # with open("../data/DefaultVectorstore.pkl","rb") as file:
         #    vectorstore =pickle.load(file)
        # vectorstore = pickle.loads(fs.get_last_version(_id=id+"vectorstore",filename="vectorstore.pkl").read())
        log.info("Vectorstore loaded")
        if vectorestoreid:
            
            vect=cache[int(vectorestoreid)]
            retriever=vect.as_retriever()
            
    llm= select_llmtype(llmtype)
    print("llm",llm)

    thot_4 = """Walk me through this context in manageable parts step by step, summarising and analysing as we go.
    Engage in a step-by-step thought process to explain how the answer was derived. 
    Additionally, associate the source with the answer using the format:
    Result: "answer"
    Explanation: "step-by-step reasoning"
    Source: "Answer in one word. If source is from the document provided or in context, say DOCUMENT else say INTERNET"
    Ensure that the above format is consistently maintained for all questions.

    {context}

    Question: {question}
    Helpful Answer: """
    QA_CHAIN_PROMPT_3 = PromptTemplate.from_template(thot_4)
    qa_chain_3 = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT_3}
    )
    output = qa_chain_3({"query": text})
    fullText = output["result"]
    input_token=calculate_token_count(text)
    output_token=calculate_token_count(fullText)
    token_cost=get_token_cost(input_token,output_token,"gpt-4")
    lines = [line for line in fullText.split('\n') if line.strip()]  # Remove empty lines
    if lines and ': ' in lines[-1]:
        realsource = lines[-1].split(': ')[1].strip('"')
    else:
        realsource = "None"
    timetaken=time.time()-starttime
    documents = retriever.get_relevant_documents(text)  
    unique_pdf_names = set()
    for Document in documents:
        docJson = Document.dict()
        if 'metadata' in docJson.keys():
            # metadata = docJson['metadata']
            # source = metadata.get('source', '')
            # pdfName = source[source.rfind("\\")+1:]
            pdfName = docJson['metadata']['source']#.split('\\')[-1]
            pdfName=os.path.basename(pdfName)
            unique_pdf_names.add(pdfName)
    if realsource.lower() == "internet":
        context=["Outside context/Internet"]
        sourceName = context
    else:
        sourceName = unique_pdf_names
    return {"thot_response":fullText,"timetaken":round(float(timetaken),2),  "source-name": sourceName, "token_cost": round(token_cost["total_cost"],3)}