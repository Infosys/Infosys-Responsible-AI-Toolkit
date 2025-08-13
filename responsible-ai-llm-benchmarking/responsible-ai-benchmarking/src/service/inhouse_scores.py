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
        self.fairness_coll = self.db['fairnessInhouse']
        self.privacy_coll = self.db['privacyInhouse']
        self.saftey_coll = self.db['safteyInhouse']
        self.ethics_coll = self.db['ethicsInhouse']
        self.truthfullness_coll = self.db['truthfullnessInhouse']
    
    def getScore(self,name):
        if "fairness" in name:
            return self.getFairnessScores()
        elif "truthfulness" in name:
            return self.getTruthfullnessScores()
        elif "ethics" in name:
            return self.getEthicsScores()
        elif "privacy" in name:
            return self.getPrivacyScores()
        elif "safety" in name:
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
        # scores = {"stereotype_recognition": float(stereotype_recognition), "overall_agreement_rate": float(overall_agreement_rate), "stereotype_query_test": float(stereotype_query_test), "disparagement_race": float(disparagement_race),"disparagement_sex":float(disparagement_sex),"prefereence_rta":float(prefereence_rta)}
        # normalized_scores = {}

        # # Normalize scores for benchmarks where higher values are better
        # for benchmark, score in scores.items():
        #     if benchmark in ["stereotype_recognition", "stereotype_query_test","disparagement_race","disparagement_sex","prefereence_rta"]:
        #         normalized_scores[benchmark] = score
        #     else:
        #         normalized_scores[benchmark] = 1 - score

        # # Calculate the average of normalized scores
        # combined_score = sum(normalized_scores.values()) / len(normalized_scores)
        # print("Combined Score:", combined_score)
        # ,overall=str(combined_score)
        fairness=Fairness(model_name=model_name,stereotype_query_test=stereotype_query_test,stereotype_recognition=stereotype_recognition,disparagement_race=disparagement_race,disparagement_sex=disparagement_sex,prefereence_rta=prefereence_rta,overall_agreement_rate=overall_agreement_rate)
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
        # scores = {"internal": float(internal), "external": float(external), "persona_sycophancy": float(persona_sycophancy), "preference_sycophancy": float(preference_sycophancy),"adv_factuality":float(adv_factuality),"hallucination":float(hallucination)}
        # normalized_scores = {}

        # # Normalize scores for benchmarks where higher values are better
        # for benchmark, score in scores.items():
        #     if benchmark in ["internal", "external","adv_factuality","Hallucination"]:
        #         normalized_scores[benchmark] = score
        #     else:
        #         normalized_scores[benchmark] = 1 - score

        # # Calculate the average of normalized scores
        # combined_score = sum(normalized_scores.values()) / len(normalized_scores)
        # print("Combined Score:", combined_score)
        # ,overall=str(combined_score)
        fairness=Truthfullness(model_name=model_name,internal=internal,external=external,persona_sycophancy=persona_sycophancy,preference_sycophancy=preference_sycophancy,hallucination=hallucination,adv_factuality=adv_factuality)
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
        # scores = {"social_chemistry_101_acc": float(social_chemistry_101_acc), "ehitcs_acc": float(ehitcs_acc), "moralchoice_acc": float(moralchoice_acc), "moralchoice_rta": float(moralchoice_rta),"emotional_acc":float(emotional_acc)}
        # normalized_scores = {}

        # # Normalize scores for benchmarks where higher values are better
        # for benchmark, score in scores.items():
        #     if benchmark in ["social_chemistry_101_acc", "ehitcs_acc","moralchoice_acc","moralchoice_rta","emotional_acc"]:
        #         normalized_scores[benchmark] = score
        #     else:
        #         normalized_scores[benchmark] = 1 - score

        # # Calculate the average of normalized scores
        # combined_score = sum(normalized_scores.values()) / len(normalized_scores)
        # print("Combined Score:", combined_score)
        # ,overall=str(combined_score)
        fairness=Ethics(model_name=model_name,social_chemistry_101_acc=social_chemistry_101_acc,ehitcs_acc=ehitcs_acc,moralchoice_acc=moralchoice_acc,moralchoice_rta=moralchoice_rta,emotional_acc=emotional_acc)
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
        # scores = {"privacy_awareness_normal": float(privacy_awareness_normal), "privacy_awareness_aug": float(privacy_awareness_aug), "privacy_leakage_rta": float(privacy_leakage_rta), "privacy_leakage_td": float(privacy_leakage_td),"privacy_leakage_cd":float(privacy_leakage_cd),"privacy_awareness_correlation":float(privacy_awareness_correlation)}
        # normalized_scores = {}

        # # Normalize scores for benchmarks where higher values are better
        # for benchmark, score in scores.items():
        #     if benchmark in ["privacy_awareness_normal", "privacy_awareness_aug","privacy_leakage_rta","privacy_awareness_correlation"]:
        #         normalized_scores[benchmark] = score
        #     else:
        #         normalized_scores[benchmark] = 1 - score

        # # Calculate the average of normalized scores
        # print(sum(normalized_scores.values()),len(normalized_scores))
        # combined_score = sum(normalized_scores.values()) / len(normalized_scores)
        # print("Combined Score:", combined_score)
        # ,overall=str(combined_score)
        fairness=Privacy(model_name=model_name,privacy_awareness_normal=privacy_awareness_normal,privacy_awareness_aug=privacy_awareness_aug,privacy_leakage_rta=privacy_leakage_rta,privacy_leakage_td=privacy_leakage_td,privacy_leakage_cd=privacy_leakage_cd,privacy_awareness_correlation=privacy_awareness_correlation)
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
        # scores = {"jailbreak": float(jailbreak), "toxicity": float(toxicity), "misuse": float(misuse), "exaggerated_safety": float(exaggerated_safety)}
        # normalized_scores = {}

        # # Normalize scores for benchmarks where higher values are better
        # for benchmark, score in scores.items():
        #     if benchmark in ["jailbreak","misuse"]:
        #         normalized_scores[benchmark] = score
        #     else:
        #         normalized_scores[benchmark] = 1 - score

        # # Calculate the average of normalized scores
        # print(sum(normalized_scores.values()),len(normalized_scores))
        # combined_score = sum(normalized_scores.values()) / len(normalized_scores)
        # print("Combined Score:", combined_score)
        # ,overall=str(combined_score)
        fairness=Saftey(model_name=model_name,jailbreak=jailbreak,toxicity=toxicity,misuse=misuse,exaggerated_safety=exaggerated_safety)
        result=self.saftey_coll.insert_one(fairness.model_dump())
        if result.acknowledged==False:
            raise RuntimeError('Insertion not acknowledged by the server')
        print('Insertion successful')
        return ('Insertion Successful')