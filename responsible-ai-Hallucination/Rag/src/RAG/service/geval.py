"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# import openai
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage,ChatMessage
import time
import os
from RAG.config.logger import CustomLogger,request_id_var

log = CustomLogger()
import traceback
try:
    # openai.verify_ssl_certs = False
    request_id_var.set("Startup")
    deployment_name=os.environ.get("OPENAI_MODEL")

    # openai.api_type = os.environ.get("OPENAI_API_TYPE")
    # openai.api_base = os.environ.get("OPENAI_API_BASE")
    # openai.api_key = os.environ.get("OPENAI_API_KEY")
    # openai.api_version = os.environ.get("OPENAI_API_VERSION")
except Exception as e:
    log.error("Failed at Completion Function")
    log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")


faith_prompt = """This prompt establishes a framework for evaluating the faithfulness of a Large Language Model (LLM) response to a document on a scale of 1 to 5.
Faithfulness refers to how accurately the LLM captures the content and intent of the original document.
Each level will be accompanied by an explanation and an example to illustrate the degree of faithfulness.

Scale:
	• 5 (Highly Faithful): The response directly reflects the content and intent of the document without introducing factual errors, misleading interpretations, or irrelevant information.
	• 4 (Mostly Faithful): The response captures the main points of the document but may contain minor factual inconsistencies, slight misinterpretations, or occasional irrelevant details.
	• 3 (Somewhat Faithful): The response partially reflects the document's content but may contain significant factual errors, misinterpretations, or irrelevant information that alters the overall message.
	• 2 (Partially Unfaithful): The response substantially deviates from the document's content, focusing on irrelevant information or presenting a misleading interpretation of the main points.
	• 1 (Not Faithful): The response bears no relation to the document's content and presents entirely fabricated information.

Evaluation Criteria:
Here are some key factors to consider when evaluating the faithfulness of an LLM response to a document:
	• Factual Accuracy: Does the response accurately represent the factual information presented in the document?
	• Intent and Interpretation: Does the response capture the intended meaning and central message of the document?
	• Content Coverage: Does the response address the main points and arguments presented in the document, or does it focus on irrelevant details?
	• Neutrality: Does the response present a neutral and objective perspective on the information in the document, or does it introduce biases or opinions?
	• Coherence: Does the response maintain a logical flow of information consistent with the document's structure and organization?

Example Scenarios (using a hypothetical document about the benefits of solar energy):
	• Scenario 1:
		○ Document: Solar energy offers a clean, renewable source of electricity with minimal environmental impact. It can reduce reliance on fossil fuels and contribute to a sustainable future. However, initial installation costs can be high.
		○ Highly Faithful Response (Level 5): "This document highlights solar energy as a clean and sustainable alternative to fossil fuels. While upfront costs might be a barrier, solar panels offer long-term environmental benefits." (This response accurately reflects the document's key points and intent.)
		○ Partially Unfaithful Response (Level 2): "Solar energy is expensive and not very efficient. It's better to stick with traditional power sources." (This response misinterprets the document's message and presents an opposing viewpoint.)
	• Scenario 2:
		○ Document: Solar energy is a promising technology, but further research is needed to improve efficiency and reduce costs. Additionally, considerations like weather dependence and energy storage need to be addressed for wider adoption.
		○ Mostly Faithful Response (Level 4): "The document discusses the potential of solar energy while acknowledging challenges like cost and efficiency. It emphasizes the need for further development to make solar a more viable option." (This response captures the main points but might downplay the environmental benefits mentioned in the document.)
        ○ Somewhat Faithful Response (Level 3): "Solar energy is a clean source of power, but it only works during the day. We need to find ways to store solar energy for nighttime use." (This response focuses on a single point from the document and ignores the discussion about cost and efficiency.)

Prompt given to the model:
{{prompt}}

Source document:
{{document}}

Response to be evaluated:
{{response}}

Provide a score between 1 and 5. Also provide a short reasoning for the score.
The response should only contain the reasoning and the score in number seperated by a comma. Format your response as follows: reasoning,score. 
For example: "This is the reason, 0.1."
DO not deviate from the format."""


rel_prompt ="""This prompt outlines a framework for evaluating the relevance of a Large Language Model (LLM) response to a user's query, considering the context of a provided document.
Here, we establish a 5-point scale to assess how well the response aligns with both the user's question and the information within the document.

Scale:
	• 5 (Highly Relevant): The response directly addresses the user's query in a comprehensive and informative manner, leveraging insights specifically from the provided document. It demonstrates a clear understanding of both the user's intent and the document's content.
	• 4 (Relevant): The response addresses the user's query but may not fully utilize the provided document. It offers valuable information but might lack depth or miss specific details relevant to the document's context.
	• 3 (Somewhat Relevant): The response partially addresses the user's query and shows some connection to the document's content. However, it may contain irrelevant information or fail to fully utilize the document's insights to answer the question effectively.
	• 2 (Partially Irrelevant): The response deviates significantly from the user's query and focuses on information not directly related to the document. It may contain some relevant details by coincidence, but it doesn't leverage the document's content to address the user's needs.
	• 1 (Not Relevant): The response bears no relation to the user's query or the provided document.

Evaluation Criteria:
Here are some key factors to consider when evaluating the relevance of an LLM response:
	• Addresses the Query: Does the response directly answer the question posed by the user, considering the context of the document?
	• Document Integration: Does the response demonstrate a clear understanding of the document's content and utilize it to support the answer?
	• Comprehensiveness: Does the response provide a complete and informative answer, considering both the user's query and the document's relevant information?
	• Focus: Does the response avoid irrelevant information or tangents, staying focused on the user's query and the document's key points?

Example Scenarios:
Scenario 1 (Document: Benefits and drawbacks of solar energy):
	• User Query: "What are the environmental benefits of solar energy, according to this document?"
	• Highly Relevant Response (Level 5): "The document highlights that solar energy is a clean and renewable source of electricity, reducing reliance on fossil fuels and greenhouse gas emissions. This contributes to a cleaner environment." (This response pinpoints the environmental benefits from the document and directly addresses the user's query.)
	• Partially Relevant Response (Level 2): "Solar energy is a good alternative energy source. We need to find ways to store the energy collected during the day." (This response mentions solar energy as an alternative but doesn't address the environmental benefits from the document.)
Scenario 2 (Document: A historical analysis of the American Civil War):
	• User Query: "What were the main causes of the American Civil War, based on this document?"
	• Relevant Response (Level 4): "The document identifies slavery, states' rights, and economic differences between the North and South as key factors leading to the American Civil War." (This response accurately reflects the main causes from the document, even if it might not delve into extensive detail.)
    • Somewhat Relevant Response (Level 3): "The American Civil War was a major conflict in US history. Abraham Lincoln was the President at the time, and the war had a lasting impact on the nation." (This response mentions the Civil War but doesn't utilize the document's insights on the causes and provides tangential details.)

Prompt given to the model:
{{prompt}}

Source document:
{{document}}

Response to be evaluated:
{{response}}

Provide a score between 1 and 5. Also provide a short reasoning for the score.
The response should only contain the reasoning and the score in number seperated by a comma. Format your response as follows: reasoning,score. 
For example: "This is the reason, 0.1."
DO not deviate from the format."""

adh_prompt= """**Evaluate Response Adherence to Original Prompt**

You are an expert evaluator tasked with assessing the quality of responses generated by language models. Your goal is to determine how well the response aligns with the original prompt and source document.

**Evaluation Criteria:**

**Adherence to the Original Prompt**: To what extent does the response follow the instructions, requirements, and context provided in the original prompt?

**Scoring Guidelines:**

Score of 1 (Off-Topic): The response is completely unrelated to the prompt, lacks relevance, or fails to address the main question/task.
Example: Original Prompt: What are the benefits of meditation? Source Document: A scientific study on meditation and mental health. Response to Evaluate: The capital of France is Paris. Score: 1 (The response is completely unrelated to the prompt and topic.)
Score of 2 (Partial Adherence): The response touches on some aspects of the prompt but misses significant key points, context, or requirements.
Example: Original Prompt: Describe the main features of a Tesla electric car. Source Document: A Tesla brochure. Response to Evaluate: Tesla cars are electric and have a large touchscreen. Score: 2 (The response mentions some features, but misses others, such as Autopilot, range, and design.)
Score of 3 (Reasonable Adherence): The response addresses the prompt fairly well, but may omit some important details, nuances, or context.
Example: Original Prompt: Summarize the plot of Romeo and Juliet. Source Document: The original play by William Shakespeare. Response to Evaluate: Romeo and Juliet are from feuding families, fall in love, and die in the end. Score: 3 (The response covers the main plot points, but omits details, such as the balcony scene, the masquerade ball, and the role of Friar Lawrence.)
Score of 4 (Mostly Adherent): The response closely follows the prompt, with only minor deviations, omissions, or inaccuracies.
Example: Original Prompt: Explain the concept of artificial intelligence. Source Document: A textbook on AI and machine learning. Response to Evaluate: Artificial intelligence refers to the development of computer systems that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Score: 4 (The response accurately defines AI, but might miss some nuances, such as the difference between narrow and general AI.)
Score of 5 (Full Adherence): The response fully addresses the prompt, covering all relevant information, context, and requirements.
Example: Original Prompt: Describe the process of photosynthesis. Source Document: A biology textbook. Response to Evaluate: Photosynthesis is the process by which plants, algae, and some bacteria convert light energy from the sun into chemical energy in the form of organic compounds, such as glucose, releasing oxygen as a byproduct. Score: 5 (The response fully and accurately describes the process of photosynthesis, covering all relevant details.)


Original prompt:
{{prompt}}

Source document:
{{document}}

Response to be evaluated:
{{response}}

**Your Task:**

Provide a score between 1 and 5. Also provide a short reasoning for the score.
The response should only contain the reasoning and the score in number seperated by a comma. Format your response as follows: reasoning,score. 
For example: "This is the reason, 0.1."
DO not deviate from the format."""

# corr_prompt= """**Evaluate Response Correctness**

# You are an expert evaluator tasked with assessing the accuracy and correctness of responses generated by language models with respect to the provided source document. Your goal is to determine whether the response aligns with the information presented in the source document.

# **Evaluation Criteria:**

# **Correctness with Respect to Source**: Does the response accurately reflect the information, facts, and concepts presented in the source document?

# **Scoring Guidelines:**

# Score of 1 (Inconsistent with Source)**: The response contradicts or is inconsistent with the information presented in the source document.
# Example: Original Prompt: What are the benefits of meditation? Source Document: A scientific study on meditation and mental health. Response to Evaluate: Meditation has no scientifically proven benefits. Score: 1
# Score of 2 (Partially Supported by Source)**: The response is partially supported by the source document, but lacks key details, context, or nuance.
# Example: Original Prompt: What are the main features of a Tesla electric car? Source Document: A Tesla brochure. Response to Evaluate: Tesla cars are electric and have a large touchscreen. Score: 2 (Omits mention of Autopilot and Supercharger networks.)
# Score of 3 (Generally Consistent with Source)**: The response is generally consistent with the information presented in the source document, but may contain minor inaccuracies or oversimplifications.
# Example: Original Prompt: What is the process of photosynthesis? Source Document: A biology textbook. Response to Evaluate: Photosynthesis is the process by which plants convert light energy into chemical energy. Score: 3 (Omits mention of chlorophyll, water, and carbon dioxide.)
# Score of 4 (Highly Consistent with Source)**: The response is highly consistent with the information presented in the source document, with only minor nuances or technicalities missing.
# Example: Original Prompt: What are the main causes of climate change? Source Document: A scientific report on climate change. Response to Evaluate: The main causes of climate change are the increasing levels of carbon dioxide and other greenhouse gases in the atmosphere, primarily due to fossil fuel burning and deforestation. Score: 4 (Omits mention of methane and nitrous oxide as greenhouse gases.)
# Score of 5 (Fully Consistent with Source)**: The response is entirely consistent with the information presented in the source document, accurately reflecting all relevant details, context, and nuance.
# Example: Original Prompt: What is the definition of artificial intelligence? Source Document: A textbook on AI and machine learning. Response to Evaluate: Artificial intelligence refers to the development of computer systems that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Score: 5 (Accurately reflects the source document's definition)

# Prompt given to the model:
# {{prompt}}

# Source document:
# {{document}}

# Response to be evaluated:
# {{response}}


# **Your Task:**

# Provide a score between 1 and 5, indicating the level of correctness of the response with respect to the source document.
# The response should contain only score:
# """

corr_prompt="""**Evaluate Response Correctness**

You are an expert evaluator tasked with assessing the factual accuracy and correctness of responses generated by language models with respect to the provided source document. Your goal is to determine whether the response aligns with the information presented in the source document.

**Evaluation Criteria:**

**Correctness with Respect to Source**: Does the response accurately reflect the information, facts, and concepts presented in the source document?

**Scoring Guidelines:**

Score of 1 (Inconsistent with Source)**: The response contradicts or is inconsistent with the information presented in the source document.
Example: Original Prompt: What are the benefits of meditation? Source Document: A scientific study on meditation and mental health. Response to Evaluate: Meditation has no scientifically proven benefits. Score: 1
Score of 2 (Partially Supported by Source)**: The response is partially supported by the source document, but lacks key details, context, or nuance.
Example: Original Prompt: What are the main features of a Tesla electric car? Source Document: A Tesla brochure. Response to Evaluate: Tesla cars are electric and have a large touchscreen. Score: 2 (Omits mention of Autopilot and Supercharger networks.)
Score of 3 (Generally Consistent with Source)**: The response is generally consistent with the information presented in the source document, but may contain minor inaccuracies or oversimplifications.
Example: Original Prompt: What is the process of photosynthesis? Source Document: A biology textbook. Response to Evaluate: Photosynthesis is the process by which plants convert light energy into chemical energy. Score: 3 (Omits mention of chlorophyll, water, and carbon dioxide.)
Score of 4 (Highly Consistent with Source)**: The response is highly consistent with the information presented in the source document, with only minor nuances or technicalities missing.
Example: Original Prompt: What are the main causes of climate change? Source Document: A scientific report on climate change. Response to Evaluate: The main causes of climate change are the increasing levels of carbon dioxide and other greenhouse gases in the atmosphere, primarily due to fossil fuel burning and deforestation. Score: 4 (Omits mention of methane and nitrous oxide as greenhouse gases.)
Score of 5 (Fully Consistent with Source)**: The response is entirely consistent with the information presented in the source document, accurately reflecting all relevant details, context, and nuance.
Example: Original Prompt: What is the definition of artificial intelligence? Source Document: A textbook on AI and machine learning. Response to Evaluate: Artificial intelligence refers to the development of computer systems that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Score: 5 (Accurately reflects the source document's definition)

Overall Score:
After considering all the above criteria, assign a final score (1-5) to the LLM response, reflecting its overall correctness.

Prompt given to the model:
{{prompt}}

Source document:
{{document}}

Response to be evaluated:
{{response}}

Provide a score between 1 and 5. Also provide a short reasoning for the score.
The response should only contain the reasoning and the score in number seperated by a comma. Format your response as follows: reasoning,score. 
For example: "This is the reason, 0.1."
DO not deviate from the format."""

def call_openai_model(prompt,llmtype):
    """
    Calls the OpenAI model with the given prompt and returns the response.
    """
    print("inside model selection")
    print(f"llmtype: {llmtype}")
    try:
        if llmtype == "openai":
            llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL"), openai_api_version=os.environ.get("OPENAI_API_VERSION"), openai_api_key=os.environ.get("OPENAI_API_KEY"), openai_api_base=os.environ.get("OPENAI_API_BASE"))
            msg = ChatMessage(role='user',content=prompt)
            response=llm(messages=[msg])
        elif llmtype=="gemini":
            try:
                log.info("Using Gemini LLM")
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"), temperature=0, transport='rest')
                log.info("Using Gemini LLM")
                # msg = HumanMessage(content=prompt)
                response=llm.invoke(prompt)
                print("Response from Gemini:", response)
            except Exception as e:
                log.error("Failed to call Gemini model")
                log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
                response=None
        elif llmtype=="aws":
            from langchain_aws import ChatBedrock
            import boto3
            sslverify=os.getenv('SSL_VERIFY').lower() == 'true'
            print("SSL Verification is set to:", sslverify)
            bedrock_client = boto3.client(
                service_name=os.getenv("AWS_SERVICE_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
                region_name= os.getenv("AWS_REGION"),
                verify=sslverify  # Disable SSL verification
            )
            llm = ChatBedrock(
                name=os.getenv("AWS_SERVICE_NAME"),
                model_id=os.getenv("AWS_MODEL_ID"),
                model_kwargs={"max_tokens": 512, "temperature": 0.1},
                client=bedrock_client  # Use the custom client
            )
            log.info("AWS Bedrock model initialized successfully")
            response = llm.invoke(prompt)
        output=response.content
        print(output)
    except Exception as e:
        output = 'do not have reponse from model'
        log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
    return output 

def gEval(text,response,sourcetext,llmtype):
    """
    Evaluates the faithfulness, relevance, adherence, and correctness of a response to a given text and source document.
    """
    try:
        print("Inside geval")
        st=time.time()
        curr_faith_prompt = faith_prompt.replace('{{prompt}}', text).replace('{{document}}', sourcetext).replace('{{response}}', response)
        curr_rel_prompt = rel_prompt.replace('{{prompt}}', text).replace('{{document}}', sourcetext).replace('{{response}}', response)
        curr_adh_prompt = adh_prompt.replace('{{prompt}}', text).replace('{{document}}', sourcetext).replace('{{response}}', response)
        curr_corr_prompt = corr_prompt.replace('{{prompt}}', text).replace('{{document}}', sourcetext).replace('{{response}}', response)
        
        prompts = [curr_faith_prompt, curr_rel_prompt, curr_adh_prompt, curr_corr_prompt]
        scoresDict = {'faithfulness': 0, 'relevance': 0, 'adherance': 0, 'correctness': 0, 'AverageScore': 0}
        resDict = {'faithfulness': '', 'relevance': '', 'adherance': '', 'correctness': ''}
        
        
        scores, reasonings, fin_score,pindx = [],[],0,0
        breakpt = 0
        while(pindx<len(prompts)):
            try:
                res = call_openai_model(prompts[pindx],llmtype) 
                # Calculate token counts
                # input_token = calculate_token_count(text)
                # output_token = calculate_token_count(res)

                # # Get token cost
                # token_cost = get_token_cost(input_token, output_token, "gpt-4")
                
                last_comma_index = res.rfind(',')
                halres=res[:last_comma_index]  
                halscore=float(res[last_comma_index+1:])
                scores.append(halscore)
                reasonings.append(halres)
                # fin_score+=res
                pindx+=1
            except Exception as e:
                breakpt+=1
                if(breakpt>3):
                    print("Connection Broke... Try Again")
                    log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")
                    return
                pass
        
        fin_score=(scores[0]+scores[1]+scores[2]+scores[3])/4
        # fin_score/=4
        scores.append(round(fin_score,3))
        indx1=0
        for key in scoresDict:
            scoresDict[key]=scores[indx1]
            indx1+=1
        scoresDict["timetaken"]=str(round(time.time()-st,3))+"s"
        indx2=0
        for key in resDict:
            resDict[key]=reasonings[indx2]
            indx2+=1
        return scoresDict, resDict
    except Exception as e:
        log.error("Failed at geval")
        log.error(f"Exception: {e,str(traceback.extract_tb(e.__traceback__)[0].lineno)}")