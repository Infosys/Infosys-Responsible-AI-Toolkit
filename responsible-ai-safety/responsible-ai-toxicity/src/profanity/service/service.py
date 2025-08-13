'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import importlib
import io
import os
from profanity.mappers.mappers import profanity, profanityScoreList, ProfanityAnalyzeRequest, ProfanityAnalyzeResponse,ProfanitycensorRequest, ProfanitycensorResponse
from typing import List
from profanity.constants.local_constants import (DELTED_SUCCESS_MESSAGE)
from profanity.exception.exception import ProfanityNotFoundError, ProfanityException, ProfanityNameNotEmptyError
import pandas as pd
import dask.dataframe as dd
import pandas as pd
from dask import delayed
from detoxify import Detoxify
import tempfile
import requests
import faiss
from sentence_transformers import SentenceTransformer
from profanity.config.logger import CustomLogger
# from better_profanity import profanity
from better_profanity import profanity

import importlib.resources as pkg_resources
import better_profanity

from profanity.util.nsfw_model.nsfw_detector.predict import Detector
from profanity.util.nsfw_model.nsfw_detector.videonsfw import process_video

import json
from PIL import Image, ImageFilter
import base64
from io import BytesIO
from dotenv import load_dotenv
from profanity.util.NudeNet.NudeNet import nudeNetImages, nudeNetVideo
import httpx
import dask.dataframe as dd
import time
import logging
import pandas as pd
from dask.diagnostics import ProgressBar
from pathlib import Path
from toxicModel import *
from typing import Optional
from io import StringIO
load_dotenv()
log = CustomLogger()
sslv={"False":False,"True":True,"None":True}


# data = pd.read_csv('../data/wordlist.csv')
# encoder = SentenceTransformer(model_name_or_path="../models/paraphrase-mpnet-base-v2")
# vectors = encoder.encode(data['word_list'])
# index = faiss.IndexFlatL2(vectors.shape[1])
# faiss.normalize_L2(vectors)
check_point = 'toxic_debiased-c7548aa0.ckpt'
toxicityModel = Detoxify(checkpoint='../models/detoxify/'+ check_point,
                            device="cpu",
                            huggingface_config_path='../models/detoxify')
# index.add(vectors)
safetyconfig = os.getenv("SAFETY_COFIG")
# config = os.getenv("PROFANITY_TELEMETRY_URL")
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ProfanityService:

    def analyze (payload: ProfanityAnalyzeRequest) -> ProfanityAnalyzeResponse:
        log.debug(f"payload: {payload}")
        text = payload.inputText
        # search_vector = np.array([encoder.encode(text)])
        # faiss.normalize_L2(search_vector)
        # k = index.ntotal
        # distances, ann = index.search(search_vector, k=k)
        # results = pd.DataFrame({'distances': distances[0], 'ann': ann[0]})
        # merge = pd.merge(results,data,left_on = 'ann', right_index=True)
        # top_five_words = merge.head(5)
        # cen_words = top_five_words['word_list'].to_list()
        List_profanity = []
        # profanity_score_dict = {}
        # for i in cen_words:
        #     match = re.finditer(i, text)
        #     for a in match:
        #         obj_profanity = profanity(profaneWord=a.group(),
        #                               beginOffset=a.start(),
        #                               endOffset=a.end())
        #         log.debug(f"obj_profanity: {obj_profanity}")
        #         List_profanity.append(obj_profanity)
        
        output = toxicityModel.predict(text)
        toxic_score = output['toxicity']
        print("toxic_score:",toxic_score)
        if toxic_score > 0.6:
            res = profanity.censor(text)
        else:
            res =[text,[],[]]

        print('res:',res)
        for i in range(len(res[1])):
            List_profanity.append({"profaneWord": res[1][i],"beginOffset":res[2][i][0],"endOffset":res[2][i][1]})

        log.info(f"List_profanity: {List_profanity}")
        print("ttt",type(output['toxicity']))
        List_profanity_score = []
        obj_profanityScore_toxic = profanityScoreList(metricName='toxicity',
                                      metricScore=round(float(output['toxicity']),3))
        obj_profanityScore_severe_toxic = profanityScoreList(metricName='severe_toxicity',
                                      metricScore=round(float(output['severe_toxicity']),3))
        obj_profanityScore_obscene = profanityScoreList(metricName='obscene',
                                      metricScore=round(float(output['obscene']),3))
        obj_profanityScore_threat = profanityScoreList(metricName='threat',
                                      metricScore=round(float(output['threat']),3))
        obj_profanityScore_insult = profanityScoreList(metricName='insult',
                                      metricScore=round(float(output['insult']),3))
        obj_profanityScore_identity_attack = profanityScoreList(metricName='identity_attack',
                                      metricScore=round(float(output['identity_attack']),3))
        obj_profanityScore_sexual_explicit = profanityScoreList(metricName='sexual_explicit',
                                      metricScore=round(float(output['sexual_explicit']),3))
        
        List_profanity_score.append(obj_profanityScore_toxic)
        List_profanity_score.append(obj_profanityScore_severe_toxic)
        List_profanity_score.append(obj_profanityScore_obscene)
        List_profanity_score.append(obj_profanityScore_threat)
        List_profanity_score.append(obj_profanityScore_insult)
        List_profanity_score.append(obj_profanityScore_identity_attack)
        List_profanity_score.append(obj_profanityScore_sexual_explicit)
        log.debug(f"List_profanity_score: {List_profanity_score}")

        objProfanityAnalyzeResponse = ProfanityAnalyzeResponse
        objProfanityAnalyzeResponse.profanity = List_profanity
        objProfanityAnalyzeResponse.profanityScoreList = List_profanity_score

        return objProfanityAnalyzeResponse

    def censor(payload: ProfanitycensorRequest) -> ProfanitycensorResponse:
        text = payload.inputText
       
        censor_text = ""
       
        # print("x===",x)
        output = toxicityModel.predict(text)
        # print("Output=====",output)
        toxic_score = output['toxicity']
        # print("toxic_score:",toxic_score)
        if toxic_score > 0.6:
            censor_text = profanity.censor(text)[0]
        else:
            censor_text = text
        # censor_text = profanity.censor(text)

        log.info(f"censor_text: {censor_text}")

        obj_ProfanitycensorResponse = ProfanitycensorResponse
        obj_ProfanitycensorResponse.outputText = censor_text

        return obj_ProfanitycensorResponse
    

    def imageToByte(img):
        buffer = BytesIO()
        img.save(buffer, format="png")
        image_data = buffer.getvalue()
        base64_string = base64.b64encode(image_data).decode("utf-8")
        return base64_string

    def imageAnalyze(payload):
        payload=AttributeDict(payload)
        if(payload.portfolio==None or payload.account==None):
            # config = os.getenv("SAFETY_COFIG")
            config=safetyconfig
            config = json.loads(config)
            # print("config169=====",config)
            # config={"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}
        else:
            data = ApiCall.request(payload)
            # print("data======",data)
            if(data==404):
                        # print( response_value)
                return data
            if(len(data)==0):
                return None
            # raise ProfanityException("No Config Found , Check with admin")
            config = data

        image = Image.open(payload.image.file)
        # print("image====",image)
        res = Detector.detector(image,payload.accuracy)
        # print("res=====",res)
        
        response={"analyze":res,"ORIGINAL":ProfanityService.imageToByte(image)}
        # return [result]
         # Check if the scores exceed the configured thresholds
        if (res["sexy"] > float(config["sexy"]) or 
            res["hentai"] > float(config["hentai"]) or 
            res["porn"] > float(config["porn"])):
            # If any of the explicit categories exceed their thresholds, blur the image
            image = image.filter(ImageFilter.GaussianBlur(radius=30))
        elif (res["sexy"] > res["neutral"] and res["sexy"] > res["drawings"] or 
            res["hentai"] > res["neutral"] and res["hentai"] > res["drawings"] or 
            res["porn"] > res["neutral"] and res["porn"] > res["drawings"]):
            # If any category exceeds neutral and also exceeds drawings, blur the image
            image = image.filter(ImageFilter.GaussianBlur(radius=30))
        response["BLURRED"]=ProfanityService.imageToByte(image)
        # processed_image_path = 'processed_image.png'
        # image.save(processed_image_path)
        # print(processed_image_path,"PATH")
        log.debug(str(res))
        return response
    

    def imageGenerate(payload):
        try:
            payload=AttributeDict(payload)
            payload=AttributeDict(payload)
            if(payload.portfolio==None or payload.account==None):
                # config = os.getenv("SAFETY_COFIG")
                config=safetyconfig
                config = json.loads(config)
                # config={"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}
            else:
                data = ApiCall.request(payload)
                if(data==404):
                        # print( response_value)
                    return data
                # print("data======",data)
                if(len(data)==0):
                    return "Portfolio/Account Not Found"
                config = data

            reqUrl = os.getenv("IMAGEGEN_IP")
            
            
            payload1={"prompt":payload.prompt,"model":"DALL-E-2"}
            headers = {"Content-Type": "application/json"}
        
            response = requests.request("POST", reqUrl, json=payload1, headers=headers,verify=sslv[os.getenv("VERIFY_SSL","None")])
            
            if(response.status_code!=200):
                raise ProfanityException("Image Generation Failed , Check with admin")

            
            img_data = response.json().get("image")
            
            img = base64.b64decode(img_data)
           
            image=Image.open(BytesIO(img))
            # image.show()
            accuracy = "high"
            res = Detector.detector(image,accuracy)
          
    
            response={"analyze":res,"ORIGINAL":ProfanityService.imageToByte(image)}
            # return [result]
            if(res["sexy"]>float(config["sexy"]) or res["hentai"]>float(config["hentai"]) or res["porn"]>float(config["porn"])):
                # print("bad")
                image = image.filter(ImageFilter.GaussianBlur(radius=30))
            elif(res["sexy"]>res["neutral"] or res["hentai"]>res["neutral"] or res["porn"]>res["neutral"]):
                image = image.filter(ImageFilter.GaussianBlur(radius=30))
            response["BLURRED"]=ProfanityService.imageToByte(image)

            # log.debug(str(res))
            return response
        except Exception as e:
            log.error(str(e))
            raise Exception("Process Failed , Check with admin")
    
    def videoCensor(payload):
        try:
            payload=AttributeDict(payload)
            payload=AttributeDict(payload)
            # if(payload.portfolio==None or payload.account==None):
            config = os.getenv("SAFETY_COFIG")
            print("config====",config)
            # config = json.loads(config)
            # config={"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.5,"sexy":0.5}
            safetyconfig=config  
            videoBase64 = process_video(payload,safetyconfig)
                 
            return videoBase64
        except Exception as e:
            log.error(str(e))
            raise Exception("Process Failed , Check with admin")
        
    def nudCensor(payload):
        try:
            payload=AttributeDict(payload)
            # if(payload.portfolio==None or payload.account==None):
            # config = os.getenv("NUD_CONFIG")
            # print("config====",config)
            # config = json.loads(config)
            # config={"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.5,"sexy":0.5}
            # nudconfig=config  
            imageBase64 = nudeNetImages(payload)
                 
            return imageBase64
        except Exception as e:
            log.error(str(e))
            raise Exception("Process Failed , Check with admin")
    
    def nudVideoCensor(payload):
        try:
            payload=AttributeDict(payload)
            payload=AttributeDict(payload)
            # # if(payload.portfolio==None or payload.account==None):
            # config = os.getenv("SAFETY_CONFIG")
            # print("config====",config)
            # config = json.loads(config)
            # config={"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.5,"sexy":0.5}
            # safetyconfig=config  
            videoBase64 = nudeNetVideo(payload)
                 
            return videoBase64
        except Exception as e:
            log.error(str(e))
            raise Exception("Process Failed , Check with admin")
        


class LoadData:

    def get_profanity_words(file_path: str):
        try:
            with open(file_path, 'r') as file:
                content = file.read()  # Read the entire content of the file
            # Convert content into a list of words (split by lines)
            return content.splitlines()
        except Exception as e:
            raise Exception(f"Profanity Word List Not Found: {str(e)}")
        

class AddProfaneWordService:
    
    def addProneWord(payload):

        try:
            # Read the content of the uploaded file
            payload=AttributeDict(payload)
            print("Inside add Profane function")
            payload_content = payload.file.file.read()
            payload_content = payload_content.decode('utf-8')  # Decode to string if necessary
            
            # Split the uploaded content into a list of words
            payload_list = payload_content.splitlines()

            # Print the payload_list (for debugging)
            # print("payload_list====", payload_list)

            # Path to the profanity word list file (already present)
            profanity_file_path = r'profanity\util\profanity_wordlist.txt'  # Replace with the actual path
            
            # Read profanity words from the existing file
            profanity_words = LoadData.get_profanity_words(profanity_file_path)
            
            # Combine the uploaded words with the profanity words
            combined_words = list(set(payload_list + profanity_words))  # Remove duplicates using set

            # Save the modified content back to a new file or overwrite the uploaded file
            modified_file_path = 'modified_file.txt'  # You can save to a new file
            
            
            
            with open(modified_file_path, 'w') as file:
                for word in combined_words:
                    file.write(word + '\n')
                    
            profanity.load_censor_words_from_file(r'modified_file.txt')
            
            os.remove(modified_file_path)

            return "success"

        except Exception as e:
            return {"error": str(e)}

class ApiCall:

    def request(data):
        try:
            if(os.getenv("ADMIN_CONNECTION")=="False" or os.getenv("ADMIN_CONNECTION")=="false"):
           
                # print("--------------------------------------------------------------")
                return 404
            payload=AttributeDict({"portfolio":data.portfolio,"account":data.account})

            api_url = os.getenv("ADMIN_API")

            aurl=api_url+"/api/v1/rai/admin/SafetyDataList"

            log.debug("Calling Admin Api  ======")
            log.debug("api payload:"+str(payload))
            
            response1=httpx.post(aurl, json=payload,verify=sslv[os.getenv("VERIFY_SSL","None")])
            data_dict = response1.json()
            if(data_dict == None):
                return []
            
            print("x=====",data_dict)
            safetyData=data_dict["safetyParameter"][0]
            safetyData = AttributeDict(safetyData)
            safety = {"drawings":safetyData.drawings,"hentai":safetyData.hentai,"neutral":safetyData.neutral,"porn":safetyData.porn,"sexy":safetyData.sexy}
            
            return safety
            
        except Exception as e:
            log.error(str(e))
            raise Exception("Process Failed , Check with admin")

  
        # record=[ele for ele in records if ele.RecogName=="PASSPORT"][0]  
    


class CheckSafety:
    @staticmethod
    def check_toxicity_and_add_label(text: str) -> str:
        """Analyzes the text and returns if it's 'Safe' or 'Not Safe' based on toxicity score."""
        try:
            # Assuming `Toxic.analyze()` returns a dictionary with toxicity scores.
            data = Toxic.analyze(text)
            # print("data3777=====",data)
            toxic_score = data['toxicity']
            # print("toxic_score:",toxic_score)
            if toxic_score > 0.6:
                censor_text = profanity.censor(text)[0]
            else:
                censor_text = text
            threshold = 0.6
            toxic_score = any(score > threshold for score in data.values())
            # print("censor_text:",censor_text)
            return censor_text
            # return "Not Safe" if toxic_score else "Safe"
        except Exception as e:
            log.error(f"Error analyzing toxicity for text: {text}. Error: {e}")
            return "Error"  # Handle cases where toxicity analysis fails

    @staticmethod
    def checkSafety(csv_file, output_file: Optional[str] = None) -> dd.DataFrame:
        """Reads a CSV, filters out toxic rows, and returns the filtered dataset."""
        log.info(f"Reading CSV file: {csv_file}")
        
        try:
            
            

# Now use Dask to read the CSV file
            df = dd.read_csv(csv_file, header=None)
           
        except Exception as e:
            log.error(f"Failed to read the CSV file: {csv_file}. Error: {e}")
            return dd.from_pandas(pd.DataFrame(), npartitions=1)  # Return empty DataFrame on error
        
       
        t1 = time.time()
        # print(df.head())
        
        def apply_toxicity_check(partition):
            partition[0] = partition[0].apply(CheckSafety.check_toxicity_and_add_label)
            return partition
    
    # Use map_partitions to apply the function to each partition
        df = df.map_partitions(apply_toxicity_check)

    # Persist the DataFrame to optimize memory usage
        df_filtered = df.persist()

       

        # Time taken for the operation
        log.info(f"Time taken for processing: {time.time() - t1:.2f} seconds")

        # Optionally save the filtered result to a new CSV file
        if output_file:
            try:
                df_filtered.to_csv(output_file, index=False, single_file=True)
                log.info(f"Filtered data saved to {output_file}")
            except Exception as e:
                log.error(f"Error saving filtered data to {output_file}. Error: {e}")
       
        anonymized_df = pd.DataFrame(df_filtered.compute())
        # log.debug("Anonymized DataFrame: " + str(anonymized_df))

            # Convert the DataFrame to CSV
        output = io.StringIO()
        anonymized_df.to_csv(output, index=False)
        output.seek(0)

            # Save the CSV to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(output.getvalue().encode())
            temp_file_path = temp_file.name

        log.debug("Returning from csv_anonymize function")
        return output
        


class CsvSafetyService:
    
    def csvSafetyCheck(payload):
        
        
        payload=AttributeDict(payload)
       
        csvData = payload.file.file.read()
        
        
        with open("temp.csv","wb") as file:
            file.write(csvData)
        checker = CheckSafety()
        
            
        # with ProgressBar():
        safe_df = checker.checkSafety("temp.csv", output_file="output1.csv")
        # print("safe_df",safe_df)
        os.remove("temp.csv")
        os.remove("output1.csv")
        
        
        return safe_df
        
        
        
    