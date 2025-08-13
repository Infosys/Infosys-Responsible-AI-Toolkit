"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from io import BytesIO
import zipfile
import torch
import tqdm
from trustllm.task import fairness
from trustllm.utils import file_process
from trustllm import config
from trustllm.generation import generation
from trustllm.task.pipeline import *
import os
import csv
import datetime
from trustllm.dataset_download import download_dataset
from config.logger import CustomLogger
import logging
from service.scores import Scores
from dao.mappers.fairness import Fairness
from dao.mappers.privacy import Privacy
from dao.mappers.ethics import Ethics
from service.utilsService import Utils
import json
evaluator = fairness.FairnessEval()
# log=CustomLogger()
logging.basicConfig(
    level=logging.INFO,  # Set the desired logging level
    # Specify the file name for the log file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #     Set the file mode to 'w' for overwriting or 'a' for appending
)
# Create a logger instance
log = logging.getLogger()


class Operations:
    def dataset_download():
        # unqiue datasets for each opearions, for not loosing the generation results.
        path = "dataset_"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        download_dataset(save_path=os.path.join('../datasets', path))
        log.info("Dataset download successfully. "+"dataset_name:"+path)
        return {"dataset_name": path}
    @staticmethod
    def generation(model_name, test_type, dataset_name):
        log.info("Generation started......")
        try:
            dataset_path = os.path.join("../datasets", os.path.join(dataset_name,"dataset"))
            if not os.path.exists(dataset_path):
                raise (FileNotFoundError)
            llm_gen = generation.LLMGeneration(
                model_path=model_name,
                test_type=test_type,
                data_path=dataset_path,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
             #run generation for 1 times, to get the best results and avoid null values.
            iterations = 1
            while(iterations > 0):
                llm_gen.generation_results()
                iterations -= 1
            # Utils.removeNullValues(dataset_path,test_type) 
            log.info("Generation completed....")
            return "Generated"
        except FileNotFoundError as e:
            log.info("Dataset not found")
            raise e.__dict__
        except Exception as e:
            log.exception("There is some problem"+e)
            raise e
    def onlineGeneration(model_name, test_type, dataset_name, model_url, auth_token):
        log.info("Generation started......")
        try:
            if model_name == None and model_url == None:
                raise ValueError(
                    "Model name and model url can not be null at a same time")
            online_model = True
            config.inhouse_url = model_url
            config.auth_token = auth_token
            dataset_path = os.path.join("../datasets",  os.path.join(dataset_name,"dataset"))
            if not os.path.exists(dataset_path):
                raise (FileNotFoundError)
            
            llm_gen = generation.LLMGeneration(
                online_model=online_model,
                model_path=model_name,
                test_type=test_type,
                data_path=dataset_path,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            #run generation for 5 times, to get the best results and avoid null values.
            iterations = 3
            while(iterations > 0):
                llm_gen.generation_results()
                iterations -= 1
            # Utils.removeNullValues(dataset_path,test_type)      
            log.info("Generation completed....")
            return "Generated"
        except FileNotFoundError as e:
            log.info("Dataset not found")
            raise e.__dict__
        except Exception as e:
            log.error(e.__dict__)
            raise e.__dict__

    #method for llm evaluations
    def evaluation(model_name, dataset_name, data_file,task_type,save_to_db):
        log.info("Evaluation started...")
        # extract the data_file
        if dataset_name is not None and data_file is not None:
            raise Exception("Please provide only single value between dataset_name and data_file")
        generation_path = "generation_results/datasets"
        if dataset_name and os.path.exists(os.path.join("generation_results/datasets", dataset_name))==False:
            if os.path.exists(os.path.join("../datasets",dataset_name))==False:
                    raise FileNotFoundError("DataSet is not present")
            generation_path="../datasets"
        
        if data_file:
            new_file_name = "dataset_reup"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            content = data_file.file.read()
            with zipfile.ZipFile(BytesIO(content), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(generation_path))
                extracted_files = zip_ref.namelist()
            first_entry = extracted_files[0]
            extracted_folder_name = first_entry.split('/')[0]
            dataset_name = extracted_folder_name
        print(dataset_name)
        dataset_name=os.path.join(dataset_name,"dataset")
        config.azure_openai = True
        config.azure_engine = os.getenv("azure_engine")
        config.azure_api_base = os.getenv("azure_api_base")
        config.openai_key = os.getenv("openai_key")
        config.azure_api_version = os.getenv("azure_api_version")
        response=None
        if task_type=="fairness":
            response=Operations.evaluate_fairness(dataset_name=dataset_name,model_name=model_name,generation_path=generation_path,save_to_db=save_to_db)
        elif task_type=="privacy":
            response=Operations.evaluate_privacy(dataset_name=dataset_name,model_name=model_name,generation_path=generation_path,save_to_db=save_to_db)
        elif task_type=="ethics":
            response=Operations.evaluate_ethics(dataset_name=dataset_name,model_name=model_name,generation_path=generation_path,save_to_db=save_to_db)
        elif task_type=="safety":
            response=Operations.evaluate_safety(dataset_name=dataset_name,model_name=model_name,generation_path=generation_path,save_to_db=save_to_db)
        elif task_type=="truthfulness":
            response=Operations.evaluate_truthfulness(dataset_name=dataset_name,model_name=model_name,generation_path=generation_path,save_to_db=save_to_db)
            
        return response
                
                
                
    def evaluate_fairness(dataset_name, model_name,generation_path,save_to_db):
        fairness_results = run_fairness(
                stereotype_recognition_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "fairness/stereotype_recognition.json"),
                stereotype_query_test_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "fairness/stereotype_query_test.json"),
                disparagement_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "fairness/disparagement.json"),
                preference_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "fairness/preference.json"),
                stereotype_agreement_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "fairness/stereotype_agreement.json")
            )
        print("Evaluation scores are: ", str(fairness_results))
        log.info("Evaluation scores are: ", str(fairness_results))
            # add model name to dict
        fairness_results["model"] = model_name
            # column names in csv
        field_names = ["model", "stereotype_recognition", "stereotype_agreement",
                        "stereotype_query", "disparagement", "preference"]
            # store results in txt and csv
        output_txt = "fairness_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".txt"
        output_csv = "fairness_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".csv"
            # remove after successful execution
        with open(os.path.join('output', output_txt), "w") as f:
            f.write(str(fairness_results))

        with open(os.path.join('output', output_csv), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerow(fairness_results)

            # store scores in DB
        # fairness = Fairness(model_name=model_name, category="fairness",stereotype_query_test=str(fairness_results["stereotype_query"]), stereotype_recognition=str(fairness_results["stereotype_recognition"]), disparagement_race=str(fairness_results[
        #                         "disparagement"]["race"]), disparagement_sex=str(fairness_results["disparagement"]["sex"]), overall_agreement_rate=str(fairness_results["stereotype_agreement"]), prefereence_rta=str(fairness_results["preference"]['overall']))
        
        fairness = {"model_name":model_name, "category":"fairness","stereotype_query_test":str(fairness_results["stereotype_query"]), "stereotype_recognition":str(fairness_results["stereotype_recognition"]), "disparagement_race":str(fairness_results[
                                "disparagement"]["race"]), "disparagement_sex":str(fairness_results["disparagement"]["sex"]), "overall_agreement_rate":str(fairness_results["stereotype_agreement"]), "prefereence_rta":str(fairness_results["preference"]['overall'])}
        if save_to_db:
            score = Scores()
            response = score.addScore(fairness)
            if 'Insertion Successful' in response:
                log.info("Scores are generated and stored successfully")
            else:
                log.info("There is some problem while storing the scores")
        return fairness_results
                
                
    def evaluate_privacy(dataset_name, model_name,generation_path,save_to_db):
        results=run_privacy(privacy_awareness_query_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "privacy/privacy_awareness_query.json"),privacy_confAIde_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "privacy/privacy_awareness_confAIde.json"),privacy_leakage_path=os.path.join(os.path.join(
                    generation_path, dataset_name),"privacy/privacy_leakage.json"))
        print("Evaluation scores are: ", str(results))
        log.info("Evaluation scores are: ", str(results))
            # add model name to dict
        results["model"] = model_name
            # column names in csv
        field_names = ["model", "privacy_confAIde", "privacy_awareness_query_normal",
                        "privacy_awareness_query_aug", "privacy_leakage"]
            # store results in txt and csv
        output_txt = "privacy_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".txt"
        output_csv = "privacy_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".csv"
            # remove after successful execution
        with open(os.path.join('output', output_txt), "w") as f:
            f.write(str(results))

        with open(os.path.join('output', output_csv), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerow(results)

            # store scores in DB
        
        privacy={
            "model_name":model_name,
            "category":"privacy",
            "privacy_awareness_aug":str(results["privacy_awareness_query_aug"]),"privacy_awareness_correlation":str(results["privacy_confAIde"]),"privacy_awareness_normal":str(results["privacy_awareness_query_normal"]),"privacy_leakage_cd":str(results["privacy_leakage"]["CD"]),
            "privacy_leakage_rta":str(results["privacy_leakage"]["RtA"]),
            "privacy_leakage_td":str(results["privacy_leakage"]["TD"])
            }
        if save_to_db:
            score = Scores()
            response = score.addScore(privacy)
            if 'Insertion Successful' in response:
                    log.info("Scores are generated and stored successfully")
            else:
                    log.info("There is some problem while storing the scores")
        return results
    
    def evaluate_ethics(dataset_name, model_name,generation_path,save_to_db):
        results=run_ethics(
                    awareness_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "ethics/awareness.json"),
                    explicit_ethics_path=os.path.join(os.path.join(
                    generation_path, dataset_name), "ethics/explicit_moralchoice.json"),implicit_ethics_path_ETHICS=os.path.join(os.path.join(
                    generation_path, dataset_name), "ethics/implicit_ETHICS.json"),implicit_ethics_path_social_norm=os.path.join(os.path.join(
                    generation_path, dataset_name), "ethics/implicit_SocialChemistry101.json")
        )
        print("Evaluation scores are: ", str(results))
        log.info("Evaluation scores are: ", str(results))
            # add model name to dict
        results["model"] = model_name
            # column names in csv
        field_names = ["model", "explicit_ethics_res_low", "explicit_ethics_res_high",
                        "implicit_ethics_res_ETHICS", "implicit_ethics_res_social_norm", "emotional_res"]
            # store results in txt and csv
        output_txt = "ethics_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".txt"
        output_csv = "ethics_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".csv"
            # remove after successful execution
        with open(os.path.join('output', output_txt), "w") as f:
            f.write(str(results))

        with open(os.path.join('output', output_csv), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerow(results)

            # store scores in DB
        emotional_acc=(results['emotional_res']['culture']+results['emotional_res']['perspective']+results['emotional_res']['emotion']+results['emotional_res']['capability'])/4
        ethics={
            "model_name":model_name,
            "category":"ethics",
            "social_chemistry_101_acc":str(results["implicit_ethics_res_social_norm"]['overall']),
            "ehitcs_acc":str(results["implicit_ethics_res_ETHICS"]["overall"]),
            "moralchoice_acc":str(results["explicit_ethics_res_low"]),
            "moralchoice_rta":str(results["explicit_ethics_res_high"]),
            "emotional_acc":str(emotional_acc)
            }
        if save_to_db:
            score = Scores()
            response = score.addScore(ethics)
            if 'Insertion Successful' in response:
                    log.info("Scores are generated and stored successfully")
            else:
                    log.info("There is some problem while storing the scores")
        
        return results
    
    def evaluate_safety(dataset_name, model_name,generation_path,save_to_db):
        results=run_safety(
                   exaggerated_safety_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "safety/exaggerated_safety.json"),
                   jailbreak_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "safety/jailbreak.json"),
                   misuse_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "safety/misuse.json"),
        )
        print("Evaluation scores are: ", str(results))
        log.info("Evaluation scores are: ", str(results))
            # add model name to dict
        results["model"] = model_name
            # column names in csv
        field_names = ["model", "jailbreak_res", "exaggerated_safety_res",
                        "misuse_res", "toxicity_res"]
            # store results in txt and csv
        output_txt = "safety_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".txt"
        output_csv = "safety_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".csv"
            # remove after successful execution
        with open(os.path.join('output', output_txt), "w") as f:
            f.write(str(results))
            

        with open(os.path.join('output', output_csv), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerow(results)

            # store scores in DB
        
        safety={
            "model_name":model_name,
            "category":"safety",
            "jailbreak":str(results["jailbreak_res"]),
            "toxicity":str("-"),
            "misuse":str(results["misuse_res"]),
            "exaggerated_safety":str(results["exaggerated_safety_res"])
            }
        if save_to_db:
            score = Scores()
            response = score.addScore(safety)
            if 'Insertion Successful' in response:
                    log.info("Scores are generated and stored successfully")          
            else:
                    log.info("There is some problem while storing the scores")
        return results
    
    def evaluate_truthfulness(dataset_name, model_name,generation_path,save_to_db):
        results=run_truthfulness(
                   advfact_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "truthfulness/golden_advfactuality.json"),
                   external_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "truthfulness/external.json"),
                   hallucination_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "truthfulness/hallucination.json"),
                   internal_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "truthfulness/internal.json"),
                   sycophancy_path=os.path.join(os.path.join(
                   generation_path, dataset_name), "truthfulness/sycophancy.json"),
        )
        print("Evaluation scores are: ", str(results))
        log.info("Evaluation scores are: ", str(results))
            # add model name to dict
        results["model"] = model_name
            # column names in csv
        field_names = ["model", "misinformation_internal", "misinformation_external",
                        "hallucination", "sycophancy_persona","sycophancy_preference","advfact"]
            # store results in txt and csv
        output_txt = "truthfulness_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".txt"
        output_csv = "truthfulness_scores"+datetime.datetime.now().strftime("%m%d%Y%H%M%S")+".csv"
            # remove after successful execution
        with open(os.path.join('output', output_txt), "w") as f:
            f.write(str(results))

        with open(os.path.join('output', output_csv), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerow(results)

            # store scores in DB
        
        truthfulness={
            "model_name":model_name,
            "category":"truthfulness",
            "internal":str(results["misinformation_internal"]["avg"]),
            "external":str(results["misinformation_external"]["avg"]),
            "hallucination":str(results["hallucination"]["avg"]),
            "persona_sycophancy":str(results["sycophancy_persona"]),
            "preference_sycophancy":str(results["sycophancy_preference"]),
            "adv_factuality":str(results["advfact"])
            }
        if save_to_db:
            score = Scores()
            response = score.addScore(truthfulness)
            if 'Insertion Successful' in response:
                    log.info("Scores are generated and stored successfully")          
            else:
                    log.info("There is some problem while storing the scores")
        return results
                
        
    
        
