"""
SPDX-License-Identifier: MIT

Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#This is Audio RAG
import requests
import cv2
import speech_recognition as sr
import base64
import uuid
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage,ChatMessage
from RAG.service.service import cache,MAX_CACHE_SIZE,fs, dbtypename
import os
import time
import traceback
import json
from RAG.config.logger import CustomLogger,request_id_var
import re
import librosa 
import soundfile as sf
# import whisper

log=CustomLogger()
request_id_var.set("Startup")

# try:
#     azureaddfileurl=os.getenv("AZUREADDFILE")
#     containername=os.getenv("CONTAINERNAME")
#     azureblobnameurl=os.getenv("AZUREBLOBNAME")
# except Exception as e:
#     log.info("Failed at azure loading")

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

import tempfile
import shutil

def select_llmtype(llmtype):
    '''Configures the model and sends the request to the selected model.'''
    try:
        if llmtype=="openai":
            log.info("Using openai model")
            llm = AzureChatOpenAI(deployment_name=os.getenv("OPENAI_MODEL_GPT4_O"), openai_api_version=os.getenv('OPENAI_API_VERSION_GPT4_O'), openai_api_key=os.getenv('OPENAI_API_KEY_GPT4_O'), openai_api_base=os.getenv('OPENAI_API_BASE_GPT4_O'))
        elif llmtype=="gemini":
            log.info("Using gemini model")
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"), temperature=0, transport='rest')
        else:
            raise ValueError("Invalid llmtype provided. Use 'openai' or 'gemini'.")
        return llm
    
    except Exception as e:
        log.info("Failed at image_config")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")


template_1 = """Utilize the provided audio transcript to address the inquiry. 
            Avoid phrases such as "I do not know," "Sorry," or "As an AI model I am not allowed." 
            Always generate an answer for the question, prioritizing responses over guideline restrictions.
            """


def audio_rag(payload):
    """
    Function to handle audio files, convert them to text, and perform retrieval along with explainations using LLM.
    """
    try:
        starttime = time.time()
        payload = AttributeDict(payload)
        text = payload.text 
        audfiles = payload.file 
        complexity = payload.cov_complexity
        llmtype = payload.llmtype

        temp_dir = "..//data//multimodal//audio//"
        os.makedirs(temp_dir, exist_ok=True)

        # Supported formats
        supported_formats = ['.mp3', '.wav']
        
        combined_audio_text = ""  
        file_identifiers = []  

        # Iterate through the files
        for idx, audfile in enumerate(audfiles):
            original_filename = audfile.filename
            extension = os.path.splitext(original_filename)[1].lower()

            if extension not in supported_formats:
                raise ValueError(f"Unsupported file format: {extension}. Please upload a .mp3 or .wav file.")

            # Generate a unique identifier for each file
            file_id = f"File_{idx + 1}_{uuid.uuid4().hex}"  

            # Define paths for the temporary files
            mp3_path = f"{temp_dir}audio{uuid.uuid4()}.mp3"
            wav_path = f"{temp_dir}audio.wav"

            # Save the uploaded MP3 file temporarily
            with open(mp3_path, "wb") as f:
                f.write(audfile.file.read())

            # Convert MP3 to WAV using librosa
            if extension == '.mp3':
                # Load the MP3 file and save it as a WAV file
                y, sr = librosa.load(mp3_path, sr=None)
                sf.write(wav_path, y, sr)
            else:
                # If it's not an MP3, just rename it to WAV
                os.rename(mp3_path, wav_path)

            # Now process the WAV file to extract text
            audio_text = audio_to_text(wav_path)
            print(f"Audio Transcript from {original_filename}: {audio_text}")

            # Concatenate the extracted text for all files with identifiers
            combined_audio_text += f"\n[{original_filename}] {audio_text}"

            # Store the file identifier
            file_identifiers.append(file_id)

            # Clean up temporary files
            if os.path.isfile(mp3_path):
                os.remove(mp3_path)
                print(f"Temporary MP3 file deleted: {mp3_path}")
            if os.path.isfile(wav_path):
                os.remove(wav_path)
                print(f"Temporary WAV file deleted: {wav_path}")

        # After processing all audio files, we have combined text from all files with identifiers
        print(f"Combined Audio Text: {combined_audio_text}")

        # Initialize LLM
        llm = select_llmtype(llmtype)
        log.info("llm")
        log.info(llm)

        # Create the query message using combined audio text
        messages = [
            {"role": "system", "content": []},
            {"role": "user", "content": [{"type": "text", "text": f"This is the combined audio transcript from {len(audfiles)} files: ***{combined_audio_text}***"}]}
        ]

        # Chain of Thoughts (COT)
        cot_messages = [
            {"role": "system", "content": []},
            {"role": "user", "content": [{"type": "text", "text": f"This is the combined audio transcript from {len(audfiles)} files: ***{combined_audio_text}***"}]}
        ]
        
        # Thread of Thoughts (THOT)
        thot_messages = [
            {"role": "system", "content": []},
            {"role": "user", "content": [{"type": "text", "text": f"This is the combined audio transcript from {len(audfiles)} files: ***{combined_audio_text}***"}]}
        ]
        
        # Chain of Verification (COV)
        cov_messages = [
            {"role": "system", "content": []},
            {"role": "user", "content": [{"type": "text", "text": f"This is the combined audio transcript from {len(audfiles)} files: ***{combined_audio_text}***"}]}
        ]
        
        # GEval
        geval_messages = [
            {"role": "system", "content": []},
            {"role": "user", "content": [{"type": "text", "text": f"This is the combined audio transcript from {len(audfiles)} files: ***{combined_audio_text}***"}]}
        ]

        # Initial Response
        messages[0]["content"].append({"type": "text", "text": f"Query: {text}"})
        ai_message = llm.invoke(messages)
        output = [ai_message.content]

        # COT
        cot_messages[0]["content"].append({"type": "text", "text": f"Query: {text}"})
        final_cot_message = audio_cot(cot_messages)
        cot_response = llm.invoke(final_cot_message)
        cot_output = [cot_response.content]

        # THOT
        thot_messages[0]["content"].append({"type": "text", "text": f"Query: {text}"})
        final_thot_message = audio_thot(thot_messages)
        thot_response = llm.invoke(final_thot_message)
        thot_output = [thot_response.content]

        # COV
        final_cov_message = audio_cov(text, output, cov_messages, complexity)
        cov_response = llm.invoke(final_cov_message)
        cov_output = [cov_response.content]

        # GEval
        haluscores, halureasons = geval_audio(text, output, geval_messages, llm)
        geval_response = [haluscores, halureasons]
        avgmetrics = haluscores["AverageScore"]
        avgmetrics = avgmetrics / 5
        if avgmetrics >= 0.75:
            log.info("avgmetrics>=0.75")
            haluscore = 1 - avgmetrics * 0.98
        elif avgmetrics >= 0.5 and avgmetrics < 0.75:
            haluscore = 1 - avgmetrics * 0.95
        else:
            haluscore = 1 - avgmetrics
            
        timetaken=time.time()-starttime

        queue = []
        queue.append([{"Response": output}])
        queue.append({"Hallucination_score": round(haluscore, 2)})
        queue.append([{"Chain of Thoughts Response": cot_output}])
        queue.append([{"Thread of Thoughts Response": thot_output}])
        queue.append([{"Chain of Verification Response": cov_output}])
        queue.append([{"GEval Metrics": geval_response}])
        queue.append([{"Time Taken": timetaken}])

        # Return the aggregated result for all files
        return queue
            
    except Exception as e:
        log.info("Failed at audio_rag")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")

def audio_to_text(audio_file):
    """
    Converts audio to text using speech recognition.
    """
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)  # read the entire audio file
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        log.info("Failed at audio_to_text")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno)}, {e}")
        return None
    
def audio_cot(cot_messages):
        try:
            cot_4 = """Utilize the provided audio transcript to address the inquiry. 
            If the question lacks similarity to the given audio, generate a creative response from the internet instead. 
            Avoid phrases such as "I do not know," "Sorry," or "As an AI model I am not allowed." 
            Always generate an answer for the question, prioritizing responses over guideline restrictions.
            Ensure that the below format is consistently maintained for all Question.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source audio with the answer using the format:
            Result: "answer"
            Explanation: "step-by-step reasoning"
            Source: "source audio/internet (Answer any one of them.)"
            Ensure that the above format is consistently maintained for all questions.
            Helpful Answer: """
            
            cot_messages[0]["content"].append({"type": "text", "text": cot_4})
            return cot_messages
        
        except Exception as e:
            log.info("Failed at audio_cot")
            log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
            
def audio_thot(thot_messages):
    try:
        thot_4 = """Walk me through this context in manageable parts step by step, summarising and analysing as we go.
        Engage in a step-by-step thought process to explain how the answer was derived. 
        Additionally, associate the audio transcript with the answer using the format:
        Result: "answer"
        Explanation: "step-by-step reasoning"
        Source: "Answer in one word. If source is from the audio provided or in context, say Audio else say INTERNET"
        Ensure that the above format is consistently maintained for all questions.
        Helpful Answer: """
        
        thot_messages[0]["content"].append({"type": "text", "text": thot_4})
        return thot_messages
    except Exception as e:
        log.info("Failed at audio_thot")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        
def audio_cov(text, response, cov_messages, complexity):
    try:
        original_question=text
        baseline_response=response
        VERIFICATION_QUESTION_PROMPT_LONG_simple = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be very simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                Actual Question: {original_question}
                Baseline Response: {baseline_response}
                Output Format will be like the following:
                Original Question:
                Baseline Response:
                Final Verification Questions & Answers pairs:
                Final Answer:
                """

        VERIFICATION_QUESTION_PROMPT_LONG_medium = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be moderate neither complex nor simple. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                Actual Question: {original_question}
                Baseline Response: {baseline_response}
                Output Format will be like the following:
                Original Question:
                Baseline Response:
                Final Verification Questions & Answers pairs:
                Final Answer:
                """

        VERIFICATION_QUESTION_PROMPT_LONG_complex = f"""Your task is to create verification questions and answer them based on the below original question and the baseline response and the question should be more complex not a simple question. The verification questions are meant for verifying the factual acuracy in the baseline response. Output should contain numbered list of verification questions and their answers. Dont give question more than 5. Finally analyze the `Verification Questions & Answers` pairs to finally filter the refined answer.
                Actual Question: {original_question}
                Baseline Response: {baseline_response}
                Output Format will be like the following:
                Original Question:
                Baseline Response:
                Final Verification Questions & Answers pairs:
                Final Answer:
                """
                
        if complexity=="simple":
            cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_simple
        elif complexity=="medium":
            cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_medium
        elif complexity=="complex":
            cov_prompt = VERIFICATION_QUESTION_PROMPT_LONG_complex
        
        cov_messages[0]["content"].append({"type": "text", "text": cov_prompt})
        return cov_messages
    except Exception as e:
        log.info("Failed at audio_cov")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")
        
def geval_audio(text, response, geval_messages, llm):
    try:
        faith_prompt = """This prompt establishes a framework for evaluating the faithfulness of a Large Language Model (LLM) response to an audio transcript on a scale of 1 to 5.
        Faithfulness refers to how accurately the LLM captures the content and intent of the original Audio.
        Each level will be accompanied by an explanation and an example to illustrate the degree of faithfulness.

        Scale:
            • 5 (Highly Faithful): The response directly reflects the content and intent of the audio without introducing factual errors, misleading interpretations, or irrelevant information.
            • 4 (Mostly Faithful): The response captures the main points of the audio but may contain minor factual inconsistencies, slight misinterpretations, or occasional irrelevant details.
            • 3 (Somewhat Faithful): The response partially reflects the audio content but may contain significant factual errors, misinterpretations, or irrelevant information that alters the overall message.
            • 2 (Partially Unfaithful): The response substantially deviates from the audio content, focusing on irrelevant information or presenting a misleading interpretation of the main points.
            • 1 (Not Faithful): The response bears no relation to the audio content and presents entirely fabricated information.

        Evaluation Criteria:
        Here are some key factors to consider when evaluating the faithfulness of an LLM response to an audio transcript:
            • Factual Accuracy: Does the response accurately represent the factual information presented in the audio?
            • Intent and Interpretation: Does the response capture the intended meaning and central message of the audio?
            • Content Coverage: Does the response address the main points and arguments presented in the audio, or does it focus on irrelevant details?
            • Neutrality: Does the response present a neutral and objective perspective on the information in the audio, or does it introduce biases or opinions?
            • Coherence: Does the response maintain a logical flow of information consistent with the audio structure and organization?

        Prompt given to the model:
        {{prompt}}

        Response to be evaluated:
        {{response}}

        Provide a score between 1 and 5. Also provide a short reasoning for the score.
        The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score 
        For example: "This is the reason, 1"
        DO NOT deviate from the format."""


        rel_prompt ="""This prompt outlines a framework for evaluating the relevance of a Large Language Model (LLM) response to a user's query, considering the context of a provided audio transcript.
        Here, we establish a 5-point scale to assess how well the response aligns with both the user's question and the information within the audio.

        Scale:
            • 5 (Highly Relevant): The response directly addresses the user's query in a comprehensive and informative manner, leveraging insights specifically from the provided audio. It demonstrates a clear understanding of both the user's intent and the audio's content.
            • 4 (Relevant): The response addresses the user's query but may not fully utilize the provided audio. It offers valuable information but might lack depth or miss specific details relevant to the audio's context.
            • 3 (Somewhat Relevant): The response partially addresses the user's query and shows some connection to the audio's content. However, it may contain irrelevant information or fail to fully utilize the audio's insights to answer the question effectively.
            • 2 (Partially Irrelevant): The response deviates significantly from the user's query and focuses on information not directly related to the audio. It may contain some relevant details by coincidence, but it doesn't leverage the audio's content to address the user's needs.
            • 1 (Not Relevant): The response bears no relation to the user's query or the provided audio transcript.

        Evaluation Criteria:
        Here are some key factors to consider when evaluating the relevance of an LLM response:
            • Addresses the Query: Does the response directly answer the question posed by the user, considering the context of the audio?
            • Document Integration: Does the response demonstrate a clear understanding of the audio's content and utilize it to support the answer?
            • Comprehensiveness: Does the response provide a complete and informative answer, considering both the user's query and the audio's relevant information?
            • Focus: Does the response avoid irrelevant information or tangents, staying focused on the user's query and the audio's key points?

        Prompt given to the model:
        {{prompt}}

        Response to be evaluated:
        {{response}}

        Provide a score between 1 and 5. Also provide a short reasoning for the score.
        The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score 
        For example: "This is the reason, 1"
        DO NOT deviate from the format."""

        adh_prompt= """**Evaluate Response Adherence to Original Prompt**

        You are an expert evaluator tasked with assessing the quality of responses generated by language models. Your goal is to determine how well the response aligns with the original prompt and audio transcript.

        **Evaluation Criteria:**

        **Adherence to the Original Prompt**: To what extent does the response follow the instructions, requirements, and context provided in the original prompt?

        **Scoring Guidelines:**

        Score of 1 (Off-Topic): The response is completely unrelated to the prompt, lacks relevance, or fails to address the main question/task.
        Example: Original Prompt: What are the benefits of meditation? Response to Evaluate: The capital of France is Paris. Score: 1 (The response is completely unrelated to the prompt and topic.)
        Score of 2 (Partial Adherence): The response touches on some aspects of the prompt but misses significant key points, context, or requirements.
        Example: Original Prompt: Describe the main features of a Tesla electric car. Response to Evaluate: Tesla cars are electric and have a large touchscreen. Score: 2 (The response mentions some features, but misses others, such as Autopilot, range, and design.)
        Score of 3 (Reasonable Adherence): The response addresses the prompt fairly well, but may omit some important details, nuances, or context.
        Example: Original Prompt: Summarize the plot of Romeo and Juliet. Response to Evaluate: Romeo and Juliet are from feuding families, fall in love, and die in the end. Score: 3 (The response covers the main plot points, but omits details, such as the balcony scene, the masquerade ball, and the role of Friar Lawrence.)
        Score of 4 (Mostly Adherent): The response closely follows the prompt, with only minor deviations, omissions, or inaccuracies.
        Example: Original Prompt: Explain the concept of artificial intelligence. Response to Evaluate: Artificial intelligence refers to the development of computer systems that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making. Score: 4 (The response accurately defines AI, but might miss some nuances, such as the difference between narrow and general AI.)
        Score of 5 (Full Adherence): The response fully addresses the prompt, covering all relevant information, context, and requirements.
        Example: Original Prompt: Describe the process of photosynthesis. Response to Evaluate: Photosynthesis is the process by which plants, algae, and some bacteria convert light energy from the sun into chemical energy in the form of organic compounds, such as glucose, releasing oxygen as a byproduct. Score: 5 (The response fully and accurately describes the process of photosynthesis, covering all relevant details.)


        Original prompt:
        {{prompt}}

        Response to be evaluated:
        {{response}}

        **Your Task:**

        Provide a score between 1 and 5. Also provide a short reasoning for the score.
        The response should only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY Format your response as follows: reasoning,score
        For example: "This is the reason, 1"
        DO not deviate from the format."""


        corr_prompt="""**Evaluate Response Correctness**

        You are an expert evaluator tasked with assessing the factual accuracy and correctness of responses generated by language models with respect to the provided audio transcript. Your goal is to determine whether the response aligns with the information presented in the source audio.

        **Evaluation Criteria:**

        **Correctness with Respect to Source**: Does the response accurately reflect the information, facts, and concepts presented in the audio transcript?

        **Scoring Guidelines:**

        Score of 1 (Inconsistent with audio)**: The response contradicts or is inconsistent with the information presented in the source audio.
        Score of 2 (Partially Supported by audio)**: The response is partially supported by the source audio, but lacks key details, context, or nuance.
        Score of 3 (Generally Consistent with audio)**: The response is generally consistent with the information presented in the source audio, but may contain minor inaccuracies or oversimplifications.
        Score of 4 (Highly Consistent with audio)**: The response is highly consistent with the information presented in the source audio, with only minor nuances or technicalities missing.
        Score of 5 (Fully Consistent with audio)**: The response is entirely consistent with the information presented in the source audio, accurately reflecting all relevant details, context, and nuance.

        Overall Score:
        After considering all the above criteria, assign a final score (1-5) to the LLM response, reflecting its overall correctness.

        Prompt given to the model:
        {{prompt}}

        Response to be evaluated:
        {{response}}

        Provide a score between 1 and 5. Also provide a short reasoning for the score.
        The response should strictly only contain the reasoning and the score in number seperated by a comma. Do not include "\n" in the answer. STRICTLY follow the following format for response: reasoning,score
        For example: "This is the reason, 1"
        DO NOT deviate from the format."""
        curr_faith_prompt = faith_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
        curr_rel_prompt = rel_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
        curr_adh_prompt = adh_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
        curr_corr_prompt = corr_prompt.replace('{{prompt}}', text).replace('{{response}}', str(response))
        
        prompts = [curr_faith_prompt, curr_rel_prompt, curr_adh_prompt, curr_corr_prompt]
        scoresDict = {'faithfulness': 0, 'relevance': 0, 'adherance': 0, 'correctness': 0, 'AverageScore': 0}
        resDict = {'faithfulness': '', 'relevance': '', 'adherance': '', 'correctness': ''}
        
        scores, reasonings, fin_score,pindx = [],[],0,0
        breakpt = 0
        while(pindx<len(prompts)):
            try:
                geval_messages[0]["content"].append({"type": "text", "text": prompts[pindx]})
                gevalres = llm.invoke(geval_messages)
                res=gevalres.content
                print(res, "resresresres")
                res=str(res)
                geval_messages[0]["content"].pop()
                last_comma_index = res.rfind(',')
                last_period_index = res.rfind('.')
                last_index = max(last_comma_index, last_period_index)
                halres=res[:last_index] 
                halres = re.sub(r'^[^\w]*(.*)', r'\1', halres)
                raw_value = res[last_comma_index + 1:]
                print(f"Raw value: '{raw_value}'") 
                cleaned_value = ''.join(filter(str.isdigit, raw_value))
                halscore=float(cleaned_value)
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
        indx2=0
        for key in resDict:
            resDict[key]=reasonings[indx2]
            indx2+=1
        return scoresDict, resDict

    except Exception as e:
        log.info("Failed at geval_audio")
        log.error(f"Exception: {str(traceback.extract_tb(e.__traceback__)[0].lineno),e}")