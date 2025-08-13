"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from dao.databaseConnection import DataBase
from dao.mappers.fairness import Fairness
from dao.mappers.truthfullness import Truthfullness
from dao.mappers.ethics import Ethics
from dao.mappers.privacy import Privacy
from dao.mappers.saftey import Saftey
import json
class Scores:
    def __init__(self):
        self.db = DataBase().db
        self.fairness_coll = self.db['fairness']
        self.privacy_coll = self.db['privacy']
        self.saftey_coll = self.db['saftey']
        self.ethics_coll = self.db['ethics']
        self.truthfullness_coll=self.db['truthfullness']

    def getScores(self,category:str):
        
        if "fairness" in category:
            return self.getFairnessScores()
        elif "truthfulness" in category:
            return self.getTruthfullnessScores()
        elif "ethics" in category:
            return self.getEthicsScores()
        elif "privacy" in category:
            return self.getPrivacyScores()
        elif "safety" in category:
            return self.getSafteyScores()
    
    def addScore(self,payload:dict):
        category=payload['category']
        if "fairness" in category:
            return self.addFairnessScore(payload)
        elif "truthfullness" in category:
            return self.addTruthfullnessScore(payload)
        elif "ethics" in category:
            return self.addEthicsScore(payload)
        elif "privacy" in category:
            return self.addPrivacyScore(payload)
        elif "safety" in category:
            return self.addSafteyScore(payload)

    def deleteScores(self,category,model_name):
          
        if "fairness" in category:
            res=self.fairness_coll.delete_one({'model_name':model_name})
        elif "truthfullness" in category:
            res=self.truthfullness_coll.delete_one({'model_name':model_name})
        elif "ethics" in category:
            res=self.ethics_coll.delete_one({'model_name':model_name})
        elif "privacy" in category:
            res=self.privacy_coll.delete_one({'model_name':model_name})
        elif "safety" in category:
            res=self.saftey_coll.delete_one({'model_name':model_name})
        
        if res.deleted_count==1:
            return "Deleted Successfully"
        return "Some problem Occures while deleting the scores"
    
    
    
    
    
    def getFairnessScores(self):
        records = self.fairness_coll.find({},{'_id': False})
        # Create a list to store the modified records
        modified_records = []
        for record in records:
            modified_records.append(record)
        print(modified_records)     
        return modified_records
    
    
    def getTruthfullnessScores(self):
        records = self.truthfullness_coll.find({},{'_id': False})
        # Create a list to store the modified records
        modified_records = []
        for record in records:
            modified_records.append(record)      
        return modified_records
    
    
    def getSafteyScores(self):
        records = self.saftey_coll.find({},{'_id': False})
        # Create a list to store the modified records
        modified_records = []
        for record in records:
            modified_records.append(record)      
        return modified_records
    
    
    def getPrivacyScores(self):
        records = self.privacy_coll.find({},{'_id': False})
        # Create a list to store the modified records
        modified_records = []
        for record in records:
            modified_records.append(record)      
        return modified_records
    
    
    def getEthicsScores(self):
        records = self.ethics_coll.find({},{'_id': False})
        # Create a list to store the modified records
        modified_records = []
        for record in records:
            modified_records.append(record)      
        return modified_records
    
    
    
    def addFairnessScore(self,payload:dict):
        model_name=payload['model_name']
        overall_agreement_rate=payload['overall_agreement_rate']
        stereotype_recognition=payload['stereotype_recognition']
        stereotype_query_test=payload['stereotype_query_test']
        disparagement_race=payload['disparagement_race']
        disparagement_sex=payload['disparagement_sex']
        prefereence_rta=payload['prefereence_rta']
        inhouse_model=payload['inhouse_model']
        scores = {"stereotype_recognition": stereotype_recognition, "overall_agreement_rate": overall_agreement_rate, "stereotype_query_test": stereotype_query_test, "disparagement_race": disparagement_race,"disparagement_sex":disparagement_sex,"prefereence_rta":prefereence_rta}
        normalized_scores = {}
        print("Before normalizing",scores)
        # Normalize scores for benchmarks where higher values are better
        total_count=0
        for benchmark, score in scores.items():
            if score=="-" or score=="" or score=="null":
                scores[benchmark]="-"
                continue
            score=round(float(score)*100,2)
            total_count+=1
            if benchmark in ["stereotype_recognition", "stereotype_query_test","disparagement_race","disparagement_sex","prefereence_rta"]:
                normalized_scores[benchmark] = score
                scores[benchmark]=score
            else:
                normalized_scores[benchmark] = 100 - score
                scores[benchmark]=100-score
        # Calculate the average of normalized scores
        combined_score = round(sum(normalized_scores.values()) / total_count,2)
        print("Combined Score:", combined_score)
        overall=str(combined_score)
        fairness=Fairness(model_name=model_name,stereotype_query_test=str(scores["stereotype_query_test"]),stereotype_recognition=str(scores["stereotype_recognition"]),disparagement_race=str(scores["disparagement_race"]),disparagement_sex=str(scores["disparagement_sex"]),prefereence_rta=str(scores['prefereence_rta']),overall_agreement_rate=str(scores['overall_agreement_rate']),overall=str(overall),inhouse_model=inhouse_model)
        result=self.fairness_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')
    

    
    def addTruthfullnessScore(self,payload:dict):
        model_name=payload['model_name']
        internal=payload['internal']
        external=payload['external']
        persona_sycophancy=payload['persona_sycophancy']
        preference_sycophancy=payload['preference_sycophancy']
        adv_factuality=payload['adv_factuality']
        hallucination=payload['hallucination']
        inhouse_model=payload['inhouse_model']
        scores = {"internal": internal, "external": external, "persona_sycophancy": persona_sycophancy, "preference_sycophancy": preference_sycophancy,"adv_factuality":adv_factuality,"hallucination":hallucination}
        normalized_scores = {}
        total_count=0
        # Normalize scores for benchmarks where higher values are better
        for benchmark, score in scores.items():
            if score=="-" or score=="" or score=="null":
                scores[benchmark]="-"
                continue
            score=round(float(score)*100,2)
            total_count+=1
            if benchmark in ["internal", "external","adv_factuality","Hallucination"]:
                normalized_scores[benchmark] = score
                scores[benchmark]=score
            else:
                normalized_scores[benchmark] = 100 - score
                scores[benchmark]=100-score

        # Calculate the average of normalized scores
        combined_score = round(sum(normalized_scores.values()) / total_count,2)
        print("Combined Score:", combined_score)
        overall=str(combined_score)
        fairness=Truthfullness(model_name=model_name,internal=str(scores['internal']),external=str(scores['external']),persona_sycophancy=str(scores['persona_sycophancy']),preference_sycophancy=str(scores['preference_sycophancy']),hallucination=str(scores['hallucination']),adv_factuality=str(scores['adv_factuality']),overall=str(overall),inhouse_model=inhouse_model)
        result=self.truthfullness_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')
    
    
    def addEthicsScore(self,payload:dict):
        model_name=payload['model_name']
        social_chemistry_101_acc=payload['social_chemistry_101_acc']
        ehitcs_acc=payload['ehitcs_acc']
        moralchoice_acc=payload['moralchoice_acc']
        moralchoice_rta=payload['moralchoice_rta']
        emotional_acc=payload['emotional_acc']
        inhouse_model=payload['inhouse_model']
        scores = {"social_chemistry_101_acc": social_chemistry_101_acc, "ehitcs_acc": ehitcs_acc, "moralchoice_acc": moralchoice_acc, "moralchoice_rta": moralchoice_rta,"emotional_acc":emotional_acc}
        normalized_scores = {}
        total_count=0
        # Normalize scores for benchmarks where higher values are better
        for benchmark, score in scores.items():
            if score=="-" or score=="" or score=="null":
                scores[benchmark]="-"
                continue
            score=round(float(score)*100,2)
            total_count+=1
            if benchmark in ["social_chemistry_101_acc", "ehitcs_acc","moralchoice_acc","moralchoice_rta","emotional_acc"]:
                normalized_scores[benchmark] = score
                scores[benchmark]=score
            else:
                normalized_scores[benchmark] = 100 - score
                scores[benchmark]=100-score

        # Calculate the average of normalized scores
        combined_score = round(sum(normalized_scores.values()) / total_count,2)
        print("Combined Score:", combined_score)
        overall=str(combined_score)
        fairness=Ethics(model_name=model_name,social_chemistry_101_acc=str(scores["social_chemistry_101_acc"]),ehitcs_acc=str(scores["ehitcs_acc"]),moralchoice_acc=str(scores['moralchoice_acc']),moralchoice_rta=str(scores['moralchoice_rta']),emotional_acc=str(scores['emotional_acc']),overall=overall,inhouse_model=inhouse_model)
        result=self.ethics_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')

    
    def addPrivacyScore(self,payload:dict):
        model_name=payload['model_name']
        privacy_awareness_normal=payload['privacy_awareness_normal']
        privacy_awareness_aug=payload['privacy_awareness_aug']
        privacy_leakage_rta=payload['privacy_leakage_rta']
        privacy_leakage_td=payload['privacy_leakage_td']
        privacy_leakage_cd=payload['privacy_leakage_cd']
        privacy_awareness_correlation=payload['privacy_awareness_correlation']
        scores = {"privacy_awareness_normal": privacy_awareness_normal, "privacy_awareness_aug": privacy_awareness_aug, "privacy_leakage_rta": privacy_leakage_rta, "privacy_leakage_td": privacy_leakage_td,"privacy_leakage_cd":privacy_leakage_cd,"privacy_awareness_correlation":privacy_awareness_correlation}
        inhouse_model=payload['inhouse_model']
        normalized_scores = {}
        total_count=0
        # Normalize scores for benchmarks where higher values are better
        for benchmark, score in scores.items():
            if score=="-" or score=="" or score=="null":
                scores[benchmark]="-"
                continue
            score=round(float(score)*100,2)
            total_count+=1
            if benchmark in ["privacy_awareness_normal", "privacy_awareness_aug","privacy_leakage_rta","privacy_awareness_correlation"]:
                normalized_scores[benchmark] = score
                scores[benchmark]=score
            else:
                normalized_scores[benchmark] = 100 - score
                scores[benchmark]=100-score

        # Calculate the average of normalized scores
        print(sum(normalized_scores.values()),len(normalized_scores))
        combined_score = round(sum(normalized_scores.values()) / total_count,2)
        print("Combined Score:", combined_score)
        overall=str(combined_score)
        fairness=Privacy(model_name=model_name,privacy_awareness_normal=str(scores['privacy_awareness_normal']),privacy_awareness_aug=str(scores['privacy_awareness_aug']),privacy_leakage_rta=str(scores["privacy_leakage_rta"]),privacy_leakage_td=str(scores["privacy_leakage_td"]),privacy_leakage_cd=str(scores["privacy_leakage_cd"]),privacy_awareness_correlation=str(scores["privacy_awareness_correlation"]),overall=overall,inhouse_model=inhouse_model)
        result=self.privacy_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')
    
      
    
    def addSafteyScore(self,payload:dict):
        model_name=payload['model_name']
        jailbreak=payload['jailbreak']
        toxicity=payload['toxicity']
        misuse=payload['misuse']
        exaggerated_safety=payload['exaggerated_safety']
        inhouse_model=payload['inhouse_model']
        total_count=0
        scores = {"jailbreak": jailbreak, "toxicity": toxicity, "misuse": misuse, "exaggerated_safety": exaggerated_safety}
        normalized_scores = {}

        # Normalize scores for benchmarks where higher values are better
        for benchmark, score in scores.items():
            if score=="-" or score=="" or score=="null":
                scores[benchmark]="-"
                continue
            score=round(float(score)*100,2)
            total_count+=1
            if benchmark in ["jailbreak","misuse"]:
                normalized_scores[benchmark] = score
                scores[benchmark]=score
            else:
                normalized_scores[benchmark] = 100 - score
                scores[benchmark]=100-score

        # Calculate the average of normalized scores
        print(sum(normalized_scores.values()),len(normalized_scores))
        combined_score = round(sum(normalized_scores.values()) / total_count,2)
        print("Combined Score:", combined_score)
        overall=str(combined_score)
        fairness=Saftey(model_name=model_name,jailbreak=jailbreak,toxicity=toxicity,misuse=misuse,exaggerated_safety=exaggerated_safety,overall=overall,inhouse_model=inhouse_model)
        result=self.saftey_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')
        
        
    