'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from privacy.service.__init__ import *
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig)
from privacy.util.fakerEntities import FakeData
from xeger import Xeger
x = Xeger()
from privacy.config.logger import CustomLogger
log=CustomLogger
import re
import secrets
import random
class FakeDataCSVGenerate:
    def fakeDataGeneration(results,df):
        fakeData_Dict = {}
        ans=[]
        # print("results===",results)
        
        for i in results:
           
        # Ensure we're iterating through the same length of value and recognizer_results lists
            # for rec,v in i.recognizer_results,i.value:
            value=i.value
            mapped_results = []
            # for rec, v in zip(i.recognizer_results, i.value):
            for v, rec in enumerate(i.recognizer_results):
                # print("reci===", rec)
                
                
                # Check if recognizer_results for this index is empty or not
                if len(rec) == 0:
                    continue  # Skip the current iteration if there are no recognizer results
                # k=0
                temp=[]
                # for en in rec:
                for k, en in enumerate(rec):
                   
                    if hasattr(FakeData, en.entity_type):
                        # print("en=====",en.entity_type)
                        
                        ent = getattr(FakeData, en.entity_type)
                        unique_key = f"{en.entity_type}{k}"
                        en.entity_type=en.entity_type+"_"+str(value[v][en.start:en.end]).replace(" ","")
                        # print("en.entity_type59=======",en.entity_type)
                        mapped_results.append({"Original": en.entity_type, "surname": value[v]})
                        hex_key = unique_key.encode("utf-8").hex()
                        # temp.append(OperatorConfig("replace", {"new_value": ent()}))
                        fakeData_Dict[en.entity_type] =OperatorConfig("replace", {"new_value": ent()})
                        # print("fakeData_Dict===",fakeData_Dict)
                        # fakeData_Dict.add({en.entity_type+str(k): OperatorConfig("replace", {"new_value": ent()})})
                    elif en.entity_type in get_session_dict():
                        entValue =get_session_dict()[en.entity_type]
                        
                        # text = str(inputText[i.start:i.end])
                        # print("i.value=======",i.value)
                        # text="Abc"
                        # print("text===",text)
                        random_data=""
                        random_data = secrets.choice(entValue)
                        # while True:
                        #     if text in entValue:
                        #         #random_data = random.choice(entValue)
                        #         random_data = secrets.choice(entValue)
                        #         print("RNDAOM dATA 348===",random_data)
                        #         if random_data.lower() != str(text[i.start:i.end]).lower()  :
                        #             fakeData_Dict.update({en.entity_type: OperatorConfig("replace", {"new_value": random_data})})
                        #             entValue.remove(random_data)
                        #             break
                        #     else:
                        #         break
                            
                            
                                # print("Value of entValue 344========",text)
                        en.entity_type=en.entity_type+"_"+str(value[v][en.start:en.end]).replace(" ","")
                        mapped_results.append({"entity_type": en.entity_type+"_"+str(value[v]), "surname": value[v]})
                              
                        fakeData_Dict.update({en.entity_type: OperatorConfig("replace", {"new_value": random_data})})
                                #print("ent_value after removing====",dict_operators)    
                            # Rest of your code
                    else:
                        # Handle the case when ent does not exist
        
                        decision_process = en.analysis_explanation
                        # print("en===",en)
                        
                        # log.debug("decision process======"+str(decision_process))
                        if(decision_process==None):        
                            continue
                        pattern = decision_process.pattern      
                        
                        if(pattern==None):
                            continue
                        
                        # Add function to generate fakeData using regex pattern
                        t=x.xeger(pattern)
                        
                        p=r'[\x00-\x1F\x7F-\xFF]'  
                                # p= r"^\ [^]"
                        t1=re.sub(p, ' ', t)
                                # print("t1====",t1)
                        fakeData_Dict.update({en.entity_type: OperatorConfig("replace", {"new_value": t1})})
            ans.append(mapped_results)

               

        # print("ans===",ans)
        return fakeData_Dict,results
        
        