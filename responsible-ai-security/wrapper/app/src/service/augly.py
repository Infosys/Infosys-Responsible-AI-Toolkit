'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''



import numpy as np
import pandas as pd
from numpy.random import choice
import matplotlib.pyplot as plt
import os
import pickle
import json

import warnings
warnings.filterwarnings("ignore")

import tensorflow as tf
if tf.executing_eagerly():
    tf.compat.v1.disable_eager_execution()

from src.service.utility import Utility as UT
from src.service.report import Report as RT
from tensorflow.keras.preprocessing import image

from art.attacks.evasion import DeepFool
from art.estimators.classification import KerasClassifier

from src.config.logger import CustomLogger
import concurrent.futures as con

log =CustomLogger()
 
telemetry_flg =os.getenv("TELEMETRY_FLAG")
 
apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

class Augly:

    def Augly(payload):
             
        try:    
            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            with open(f'{Payload_path}') as f:
                data = f.read()
            payload_data = json.loads(data)
            
            attackDataList = {}
            for k in img:
                l = []
                x = image.img_to_array(img[k])
                x = x / 255
                x_art = np.expand_dims(x, axis=0)
                pred = model.predict(x_art)
                actual_prediction = np.argmax(pred, axis=1)[0]
                base_actual_confidence = pred[:,actual_prediction][0]
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                
                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                adv= DeepFool(classifier=classifier,epsilon=0.000025,nb_grads=3)
                x_art_adv = adv.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Augly")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
            
            Payload = {
                    'modelName':modelName,
                    'attackName':"Augly",
                    'attackDataList':attackDataList
                }
            
            foldername = RT.generateimagereport(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,img,attackDataList,Payload
            return {"Job_Id":f'{foldername}'}

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "Augly", e, apiEndPoint, errorRequestMethod)   
    