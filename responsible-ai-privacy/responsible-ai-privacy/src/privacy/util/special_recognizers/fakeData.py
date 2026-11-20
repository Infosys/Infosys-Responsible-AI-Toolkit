'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
class FakeDataGenerate:
    def fake_data_generation(self,results,input_text):
        fake_data_dict = {}
        for i in results:
            if hasattr(FakeData, i.entity_type):
                ent = getattr(FakeData, i.entity_type)
                fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": ent()})})
            elif i.entity_type in get_session_dict():
                ent_value =get_session_dict()[i.entity_type]

                text = str(input_text[i.start:i.end])
                print("text===",text)
                random_data=""
                while True:
                    if text in ent_value:
                        random_data = secrets.choice(ent_value)
                        print("RNDAOM dATA 348===",random_data)
                        if random_data.lower() != str(input_text[i.start:i.end]).lower()  :
                            fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": random_data})})
                            ent_value.remove(random_data)
                            break
                    else:
                        print("Value of ent_value 344========",text)
                        break
                fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": random_data})})
                      
            else:
                
                decision_process = i.analysis_explanation
             
                if(decision_process==None):        
                    continue
                pattern = decision_process.pattern        
               
                t=x.xeger(pattern)
                p=r'[\x00-\x1F\x7F-\xFF]'  
                 
                t1=re.sub(p, ' ', t)
                     
                fake_data_dict.update({i.entity_type: OperatorConfig("replace", {"new_value": t1})})
                       
                
                
        return fake_data_dict