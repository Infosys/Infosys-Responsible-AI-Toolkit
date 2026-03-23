'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import os
import pandas as pd
import numpy as np
import joblib
import requests
import json

#import tensorflow as tf
# if tf.executing_eagerly():
#     tf.compat.v1.disable_eager_execution()
import warnings
warnings.filterwarnings("ignore")

from src.service.utility import Utility as UT
from src.service.report import Report as RT
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from art.estimators.classification.query_efficient_bb import QueryEfficientGradientEstimationClassifier
from art.attacks.evasion.fast_gradient import FastGradientMethod
from art.attacks.evasion import BoundaryAttack
from art.attacks.evasion import HopSkipJump
from art.attacks.inference.membership_inference import LabelOnlyGapAttack
from art.attacks.inference.membership_inference import MembershipInferenceBlackBoxRuleBased
from art.attacks.inference.membership_inference import LabelOnlyDecisionBoundary
from art.attacks.inference.membership_inference import MembershipInferenceBlackBox
import concurrent.futures as con
from src.config.logger import CustomLogger

log = CustomLogger()

telemetry_flg =os.getenv("TELEMETRY_FLAG")


apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

class ArtEndPoint:

# ---------------------------------------------------------------------------------------------------------------
    
    def QueryEfficientGradientAttack(payload):
        try:
            if tf.executing_eagerly():
                tf.compat.v1.disable_eager_execution()

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)
        
            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            classifier = QueryEfficientGradientEstimationClassifier(classifier=UT.createArtEstimator(Payload), num_basis=50,sigma=0.5, round_samples=0.03)
            attack = FastGradientMethod(estimator =classifier, eps=1)
            que_attack_x_train_adv = attack.generate(X_train)
            log.info("Actual Label: %i" % y_train[0])

            bpredictions = UT.getPredictionsFromEndpoint({'train_data':X_train, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            bscore = accuracy_score(y_train, bpredictions)
            log.info("\nBenign Training Score: %.4f" % bscore)
            log.info("Benign Training sample: ", X_train[0,:])
            bbprediction = UT.getPredictionsFromEndpoint({'train_data':X_train[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Benign Training Predicted Label: %i" % bbprediction[0])
            apredictions = UT.getPredictionsFromEndpoint({'train_data':que_attack_x_train_adv, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            ascore = accuracy_score(y_train, apredictions)
            log.info("\nAdversarial Training Score: %.4f" % ascore)
            log.info("Adversarial Training sample: ", que_attack_x_train_adv[0])
            aaprediction = UT.getPredictionsFromEndpoint({'train_data':que_attack_x_train_adv[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Adversarial Training Predicted Label: %i" % aaprediction[0])
            perturbation = np.mean(np.abs((que_attack_x_train_adv - X_train)))
            log.info('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':que_attack_x_train_adv,'target_data':y_train,'prediction_data':pd.Series(apredictions),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"QueryEfficientGradientAttackEndPoint",
                    # 'base_sample':X_train,
                    # 'adversial_sample':zoo_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bbprediction[0],
                    # 'adversial_prediction':aaprediction[0],
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':y_train[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportartendpoint(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "QueryEfficientGradientAttack", e, apiEndPoint, errorRequestMethod)
    

    def BoundaryAttack(payload):
        
        try:
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            attack = BoundaryAttack(estimator = UT.createArtEstimator(Payload),batch_size =25,epsilon=0.75)
            x_train_adv = attack.generate(X_train,y_train)
            log.info("Actual Label: %i" % y_train[0])

            bpredictions = UT.getPredictionsFromEndpoint({'train_data':X_train, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            bscore = accuracy_score(y_train, bpredictions)
            log.info("\nBenign Training Score: %.4f" % bscore)
            log.info("Benign Training sample: ", X_train[0,:])
            bbprediction = UT.getPredictionsFromEndpoint({'train_data':X_train[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Benign Training Predicted Label: %i" % bbprediction[0])
            apredictions = UT.getPredictionsFromEndpoint({'train_data':x_train_adv, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            ascore = accuracy_score(y_train, apredictions)
            log.info("\nAdversarial Training Score: %.4f" % ascore)
            log.info("Adversarial Training sample: ", x_train_adv[0])
            aaprediction = UT.getPredictionsFromEndpoint({'train_data':x_train_adv[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Adversarial Training Predicted Label: %i" % aaprediction[0])
            perturbation = np.mean(np.abs((x_train_adv - X_train)))
            log.info('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train_adv,'target_data':y_train,'prediction_data':pd.Series(apredictions),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"BoundaryAttackEndPoint",
                    # 'base_sample':X_train,
                    # 'adversial_sample':zoo_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bbprediction[0],
                    # 'adversial_prediction':aaprediction[0],
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':y_train[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportartendpoint(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "BoundaryAttack", e, apiEndPoint, errorRequestMethod)
    

    def HopSkipJumpAttack(payload):
        
        try:
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            attack = HopSkipJump(classifier = UT.createArtEstimator(Payload))
            x_train_adv = attack.generate(X_train)
            log.info("Actual Label: %i" % y_train[0])

            bpredictions = UT.getPredictionsFromEndpoint({'train_data':X_train, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            bscore = accuracy_score(y_train, bpredictions)
            log.info("\nBenign Training Score: %.4f" % bscore)
            log.info("Benign Training sample: ", X_train[0,:])
            bbprediction = UT.getPredictionsFromEndpoint({'train_data':X_train[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Benign Training Predicted Label: %i" % bbprediction[0])
            apredictions = UT.getPredictionsFromEndpoint({'train_data':x_train_adv, 'batch':True, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            ascore = accuracy_score(y_train, apredictions)
            log.info("\nAdversarial Training Score: %.4f" % ascore)
            log.info("Adversarial Training sample: ", x_train_adv[0])
            aaprediction = UT.getPredictionsFromEndpoint({'train_data':x_train_adv[0], 'batch':False, 'api':data['modelEndPoint'], 'data':data['data'], 'prediction':data['prediction']})
            log.info("Adversarial Training Predicted Label: %i" % aaprediction[0])
            perturbation = np.mean(np.abs((x_train_adv - X_train)))
            log.info('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train_adv,'target_data':y_train,'prediction_data':pd.Series(apredictions),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"HopSkipJumpAttackEndPoint",
                    # 'base_sample':X_train,
                    # 'adversial_sample':zoo_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bbprediction[0],
                    # 'adversial_prediction':aaprediction[0],
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':y_train[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportartendpoint(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "HopSkipJumpAttack", e, apiEndPoint, errorRequestMethod)


    def LabelOnlyGapAttack(payload):
        
        try:
        
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            attack = LabelOnlyGapAttack(UT.createArtEstimator(Payload))
            inferred_train = attack.infer(X_train,y_train)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            log.info(f"Members Accuracy: {train_acc:.4f}")

            Payload = {
                    'modelName':modelName,
                    'attackName':"LabelOnlyGapAttackEndPoint",
                    'inference_acc':train_acc,
                }

            foldername = RT.generateinferencereport(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "LabelOnlyGapAttack", e, apiEndPoint, errorRequestMethod)


    def MembershipInferenceBlackBoxRuleBasedAttack(payload):
        
        try:
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            attack = MembershipInferenceBlackBoxRuleBased(UT.createArtEstimator(Payload))
            inferred_train = attack.infer(X_train,y_train)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            log.info(f"Members Accuracy: {train_acc:.4f}")

            Payload = {
                    'modelName':modelName,
                    'attackName':"MembershipInferenceBlackBoxRuleBasedAttackEndPoint",
                    'inference_acc':train_acc,
                }

            foldername = RT.generateinferencereport(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "MembershipInferenceBlackBoxRuleBasedAttack", e, apiEndPoint, errorRequestMethod)
    

    def LabelOnlyDecisionBoundaryAttack(payload):
        
        try:
        
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            attack =LabelOnlyDecisionBoundary(estimator =UT.createArtEstimator(Payload),distance_threshold_tau=0.02)
            inferred_train = attack.infer(X_train,y_train)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            log.info(f"Members Accuracy: {train_acc:.4f}")

            Payload = {
                    'modelName':modelName,
                    'attackName':"LabelOnlyDecisionBoundaryAttackEndPoint",
                    'inference_acc':train_acc,
                }

            foldername = RT.generateinferencereport(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "LabelOnlyDecisionBoundaryAttack", e, apiEndPoint, errorRequestMethod)


    def MembershipInferenceBlackBoxAttack(payload):
        try:
            
            # if tf.executing_eagerly():
            #     tf.compat.v1.disable_eager_execution()        

            raw_data, data_path = UT.readDataFile(payload)
            modelName = UT.readModelFile(payload)
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1, inplace=False).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, train_size=0.80,random_state=32)
            Payload = {
                'modelEndPoint':data['modelEndPoint'],
                'nb_classes':len(data['groundTruthClassNames']),
                'input_shape':(len(list_of_column_names),),
                'api_data_variable':data['data'],
                'api_response_variable':data['prediction']
            }
            bb_attack = MembershipInferenceBlackBox(UT.createArtEstimator(Payload))
            inferred_train = bb_attack.infer(X_train,y_train)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            log.info(f"Members Accuracy: {train_acc:.4f}")

            Payload = {
                    'modelName':modelName,
                    'attackName':"MembershipInferenceBlackBoxAttackEndPoint",
                    'inference_acc':train_acc,
                }

            foldername = RT.generateinferencereport(Payload)
            # UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            return {"Job_Id":f'{foldername}'}
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "MembershipInferenceBlackBoxAttack", e, apiEndPoint, errorRequestMethod)
# ---------------------------------------------------------------------------------------------------------------