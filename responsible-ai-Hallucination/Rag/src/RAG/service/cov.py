"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chat_models import AzureChatOpenAI
import pickle
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS
from RAG.service.service import show_score
import re
import os
import time
from RAG.config.logger import CustomLogger,request_id_var
from RAG.service.service import cache,fs,MAX_CACHE_SIZE, dbtypename, select_embeddingmodel, select_llmtype
from RAG.dao.AdminDb import collection
import tiktoken
import traceback
log=CustomLogger()
request_id_var.set("Startup")

# Base directory for storing vectorstores
VECTORSTORE_BASE_DIR = "../data/vectorstores/"
embeddingmodelname=os.getenv("EMBEDDING_MODEL_NAME")

# llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL"), temperature=1)

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
    
def cov(text,fileupload,complexity,llmtype,vectorestoreid=None):
    """
    Function to generate a Chain of Verification (COVe) response using the Langchain library and a vector store.
    """
    starttime = time.time()     
    if fileupload==True:
        res = []
        log.info("Before llm calling")
        # with open("../data/docs/"+str(id)+"/DefaultVectorstore.pkl","rb") as file:
        #vectorstore =pickle.load(file)
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
            ###############################
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
    
    BASELINE_PROMPT = """Answer the question based only on the following context:
    {context}

    Question: {original_question}
    Answer: """
    baseline_response_prompt_template = PromptTemplate.from_template(BASELINE_PROMPT)
    # baseline_response_chain = RetrievalQA.from_chain_type(
    #     llm_1,
    #     retriever=retriever,
    #     return_source_documents=False,
    #     chain_type_kwargs={"prompt": baseline_response_prompt_template}
    # )
    from operator import itemgetter
    
    baseline_response_chain = (
        {"context": itemgetter("original_question") | retriever,"original_question": itemgetter("original_question")}
        | baseline_response_prompt_template
        | llm
        | StrOutputParser()
    )
    VERIFICATION_QUESTION_PROMPT_LONG = """Your task is to create verification questions based on the below original question and the baseline response. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Create 5 verifiation questions

        Actual Question: {original_question}
        Baseline Response: {baseline_response}

        Final Verification Questions:"""

    VERIFICATION_QUESTION_PROMPT_LONG_simple = """Your task is to create verification questions based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Dont give question more than 5.
            Actual Question: {original_question}
            Baseline Response: {baseline_response}
            Final Verification Questions:"""

    VERIFICATION_QUESTION_PROMPT_LONG_medium = """Your task is to create verification questions based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Dont give question more than 5.
            Actual Question: {original_question}
            Baseline Response: {baseline_response}
            Final Verification Questions:"""

    VERIFICATION_QUESTION_PROMPT_LONG_complex = """Your task is to create verification questions based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should be numbered list of verification questions.Dont give question more than 5.
            Actual Question: {original_question}
            Baseline Response: {baseline_response}
            Final Verification Questions:"""
    
    if complexity=="simple":
        verification_question_generation_prompt_template_long = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_simple)
    elif complexity=="medium":
        verification_question_generation_prompt_template_long = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_medium)
    elif complexity=="complex":
        verification_question_generation_prompt_template_long = PromptTemplate.from_template(VERIFICATION_QUESTION_PROMPT_LONG_complex)
        
                
    
    verification_question_generation_chain = verification_question_generation_prompt_template_long | llm | StrOutputParser()

    EXECUTE_PLAN_PROMPT_SELF_LLM = """Answer the question based only on the following context:
    {context}

    Question: {verification_question}

    Answer:"""
    execution_prompt_self_llm = PromptTemplate.from_template(EXECUTE_PLAN_PROMPT_SELF_LLM)
    # execution_prompt_llm_chain = RetrievalQA.from_chain_type(
    #     llm_1,
    #     retriever=retriever,
    #     return_source_documents=False,
    #     chain_type_kwargs={"prompt": execution_prompt_self_llm}
    # )
    execution_prompt_llm_chain = (
        {"context": itemgetter("verification_question") | retriever, 
        "verification_question": itemgetter("verification_question")}
        | execution_prompt_self_llm
        | llm
        | StrOutputParser()
    )
    verification_chain = RunnablePassthrough.assign(
        split_questions=lambda x: x['verification_questions'].split("\n"),
    ) | RunnablePassthrough.assign(
        answers = (lambda x: [{"verification_question": q} for q in x['split_questions']])| execution_prompt_llm_chain.map()
    ) | (lambda x: "\n".join(["Question: {} Answer: {}\n".format(question, answer) for question, answer in zip(x['split_questions'], x['answers'])]))# Create final refined response

    FINAL_REFINED_PROMPT = """Given the below `Original Query` and `Baseline Answer`, analyze the `Verification Questions & Answers` to finally filter the refined answer.
    Original Query: {original_question}
    Baseline Answer: {baseline_response}

    Verification Questions & Answer Pairs:
    {verification_answers}

    Final Refined Answer:"""
    final_answer_prompt_template = PromptTemplate.from_template(FINAL_REFINED_PROMPT)
    final_answer_chain = final_answer_prompt_template | llm | StrOutputParser()
    chain_long = RunnablePassthrough.assign(
        baseline_response=baseline_response_chain
    ) | RunnablePassthrough.assign(
        verification_questions=verification_question_generation_chain
    ) | RunnablePassthrough.assign(
        verification_answers=verification_chain
    ) | RunnablePassthrough.assign(
        final_answer=final_answer_chain
    )
    Cov_response = chain_long.invoke({f"original_question":text})
    print(Cov_response["final_answer"])
    print("result", Cov_response)
    input_token=calculate_token_count(text)
    full_response=str(Cov_response)
    output_token=calculate_token_count(full_response)
    token_cost=get_token_cost(input_token,output_token,"gpt-4")
    timetaken=time.time()-starttime
    # print(retriever.get_relevant_documents(text))

    # # pdf_names = []
    # documents = retriever.get_relevant_documents(text)  
    # for Document in documents:
    #     docJson = Document.dict()
    #     if 'metadata' in docJson.keys():
    #         metadata = docJson['metadata']
    #         source = metadata.get('source', '')
    #         pdfName = source[source.rfind("\\")+1:]
            
    # # sourcearr=[]
    # # textArr = re.split(r'(?<=[.!?])\s+(?=\D|$)', Cov_response["final_answer"])
    # srcArr = []
    # for j in retriever.get_relevant_documents(text):
    #     srcArr.append(j.page_content)
    # score=show_score(text,Cov_response["final_answer"],srcArr)
    return {"cov_response":Cov_response,"timetaken":round(float(timetaken),2), "token_cost": round(token_cost["total_cost"],3)}