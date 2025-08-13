'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024-2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
 
 
 
import numpy as np
import pandas as pd
from numpy.random import choice
import matplotlib.pyplot as plt
import os
import pickle
import json
from src.config.logger import CustomLogger
import math
 
import warnings
warnings.filterwarnings("ignore")
 
#import tensorflow as tf
# if tf.executing_eagerly():
#     tf.compat.v1.disable_eager_execution()
 
from src.service.utility import Utility as UT
from src.service.report import Report as RT
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
#from keras.models import load_model
# from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.preprocessing import image
# from tensorflow.image import grayscale_to_rgb
from art.estimators.classification import SklearnClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
 
from art.estimators.classification.scikitlearn import ScikitlearnClassifier
from art.attacks.evasion import ZooAttack
from art.estimators.classification.query_efficient_bb import QueryEfficientGradientEstimationClassifier
from art.attacks.evasion.fast_gradient import FastGradientMethod
from art.attacks.evasion import hop_skip_jump
from art.attacks.evasion import DeepFool
from art.attacks.evasion import Wasserstein
from art.attacks.evasion import BoundaryAttack
from art.attacks.evasion import CarliniL2Method
from art.attacks.evasion import PixelAttack
from art.attacks.evasion import UniversalPerturbation
from art.attacks.evasion import FastGradientMethod
from art.attacks.evasion import SpatialTransformation
from art.attacks.evasion import SquareAttack
from art.attacks.inference.attribute_inference import AttributeInferenceBlackBox
from art.attacks.inference.membership_inference import MembershipInferenceBlackBox
from art.attacks.inference.membership_inference import MembershipInferenceBlackBoxRuleBased
from art.attacks.evasion import ProjectedGradientDescent
from art.attacks.evasion import BasicIterativeMethod
from art.attacks.evasion import SaliencyMapMethod
from art.attacks.evasion import DecisionTreeAttack
from art.attacks.evasion import FastGradientMethod, FrameSaliencyAttack
from art.attacks.evasion import SimBA
from art.attacks.evasion import NewtonFool
from art.attacks.evasion import GeoDA
from art.attacks.inference.membership_inference import LabelOnlyGapAttack
from art.attacks.evasion import ElasticNet
from art.attacks.poisoning.poisoning_attack_svm import PoisoningAttackSVM
from art.attacks.inference.attribute_inference import AttributeInferenceWhiteBoxLifestyleDecisionTree, AttributeInferenceWhiteBoxDecisionTree
from art.attacks.inference.membership_inference import LabelOnlyDecisionBoundary
from art.attacks.evasion import virtual_adversarial
from art.estimators.classification import KerasClassifier
from art.estimators.classification import XGBoostClassifier
from art.estimators.classification import TensorFlowV2Classifier
from sklearn.preprocessing import OneHotEncoder
from art.attacks.evasion import ThresholdAttack
import concurrent.futures as con
 
log =CustomLogger()
 
telemetry_flg =os.getenv("TELEMETRY_FLAG")
 
apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'
 



class Art:

# ---------------------------------------------------------------------------------------------------------------
    
    # def PoisoningAttackSVM(payload):

    #     raw_data, data_path = UT.readDataFile(payload)
    #     model, model_path, modelName = UT.readModelFile(payload)
    #     Payload_path = UT.readPayloadFile(payload)

    #     list_of_column_names = list(raw_data.columns)
    #     payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
    #     payload_path = os.path.join(payload_folder_path,modelName + ".txt")
    #     with open(f'{payload_path}') as f:
    #         data = f.read()
    #     data = json.loads(data)
    #     Output_column = data["targetColumnNames"]
 
    #     X = raw_data.drop([Output_column], axis=1).to_numpy()
    #     y = raw_data[[Output_column]].to_numpy()
    #     y = y.flatten()
    #     X = X[y != 0, :2]
    #     y = y[y != 0]
    #     labels = np.zeros((y.shape[0], 2))
    #     labels[y == 2] = np.array([1, 0])
    #     labels[y == 1] = np.array([0, 1])
    #     y = labels
    #     n_sample = len(X)
    #     order = np.random.permutation(n_sample)
    #     X = X[order]
    #     y = y[order].astype(np.float32)
    #     X_train = X[:int(.9 * n_sample)]
    #     y_train = y[:int(.9 * n_sample)]
    #     train_dups = UT.find_duplicates(X_train)
    #     X_train = X_train[train_dups == False]
    #     y_train = y_train[train_dups == False]
    #     X_test = X[int(.9 * n_sample):]
    #     y_test = y[int(.9 * n_sample):]
    #     test_dups = UT.find_duplicates(X_test)
    #     X_test = X_test[test_dups == False]
    #     y_test = y_test[test_dups == False]
    #     kernel = 'linear' # one of ['linear', 'poly', 'rbf']
    #     attack_point, poisoned = UT.get_adversarial_examples(X_train, y_train, 0, X_test, y_test, kernel)
 
    #     clean_acc_train = np.average(np.all(model.predict(X_train) == y_train, axis=1))
    #     poison_acc_train = np.average(np.all(poisoned.predict(X_train) == y_train, axis=1))
    #     clean_acc_test = np.average(np.all(model.predict(X_test) == y_test, axis=1))
    #     poison_acc_test = np.average(np.all(poisoned.predict(X_test) == y_test, axis=1))
    #     print("Clean model accuracy on train set ({} samples): {}".format(len(y_train), clean_acc_train))
    #     print("Poison model accuracy on train set ({} samples): {}".format(len(y_train), poison_acc_train))
    #     print("Clean model accuracy on test set ({} samples): {}".format(len(y_test), clean_acc_test))
    #     print("Poison model accuracy on test set ({} samples): {}".format(len(y_test), poison_acc_test))

    #     Payload = {
    #             'modelName':modelName,
    #             'attackName':"Poisoning",
    #             'clean_train_acc':clean_acc_train,
    #             'poison_train_acc':poison_acc_train,
    #             'clean_test_acc':clean_acc_test,
    #             'poison_test_acc':poison_acc_test
    #         }
 
    #     foldername = RT.generateinferencereport(Payload)
    #     UT.databaseDelete(model_path)
    #     UT.databaseDelete(data_path)
    #     UT.databaseDelete(Payload_path)
    #     return {"Job_Id":f'{foldername}'}

    
    def MembershipInferenceRule(payload):
        
        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # raw_data, data_path = UT.readDataFile({'modelid':payload})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1).to_numpy()
            Y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            # x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)

            classifier = SklearnClassifier(model=model)
            attack = MembershipInferenceBlackBoxRuleBased(classifier)
            inferred_train = attack.infer(x_train, y_train)
            inferred_test = attack.infer(x_test, y_test)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            test_acc = 1 - (np.sum(inferred_test) / len(inferred_test))
            acc = (train_acc * len(inferred_train) + test_acc * len(inferred_test)) / (len(inferred_train) + len(inferred_test))
            print(f"Members Accuracy: {train_acc:.4f}")
            print(f"Attack Accuracy {acc:.4f}")
            x,y = UT.calc_precision_recall(np.concatenate((inferred_train, inferred_test)),
                                np.concatenate((np.ones(len(inferred_train)), np.zeros(len(inferred_test)))))
            
            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train,'target_data':y_train,'prediction_data':inferred_train,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"MembershipInferenceRule",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,Y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "MembershipInferenceRule", e, apiEndPoint, errorRequestMethod)    


    def MembershipInferenceBlackBox(payload):

        try:
            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1).to_numpy()
            Y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            # x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
            
            classifier = SklearnClassifier(model=model)
            attack_train_ratio = 0.5
            attack_train_size = int(len(x_train) * attack_train_ratio)
            attack_test_size = int(len(x_test) * attack_train_ratio)
            bb_attack = MembershipInferenceBlackBox(classifier)
            bb_attack.fit(x_train[:attack_train_size], y_train[:attack_train_size],
                            x_test[:attack_test_size], y_test[:attack_test_size])

            inferred_train_bb = bb_attack.infer(x_train[attack_train_size:], y_train[attack_train_size:])
            inferred_test_bb = bb_attack.infer(x_test[attack_test_size:], y_test[attack_test_size:])
            train_acc = np.sum(inferred_train_bb) / len(inferred_train_bb)
            test_acc = 1 - (np.sum(inferred_test_bb) / len(inferred_test_bb))
            acc = (train_acc * len(inferred_train_bb) + test_acc * len(inferred_test_bb)) / (len(inferred_train_bb) + len(inferred_test_bb))
            print(f"Members Accuracy: {train_acc:.4f}")
            print(f"Attack Accuracy {acc:.4f}")
            x,y = UT.calc_precision_recall(np.concatenate((inferred_train_bb, inferred_test_bb)),
                                np.concatenate((np.ones(len(inferred_train_bb)), np.zeros(len(inferred_test_bb)))))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train,'target_data':y_train,'prediction_data':inferred_train_bb.flatten().astype(int),'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"MembershipInferenceBlackBox",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }
            
            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,Y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "MembershipInferenceBlackBox", e, apiEndPoint, errorRequestMethod)    

    
    def LabelOnlyDecisionBoundaryAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]
            
            x = raw_data.drop([Output_column], axis=1).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
            
            classifier =  ScikitlearnClassifier(model=model)
            mia_label_only = LabelOnlyDecisionBoundary(classifier)
            attack_train_size = 50
            attack_test_size = 50
            training_sample = np.array([1] * len(x_train) + [0] * len(x_test))
            mia_label_only.calibrate_distance_threshold(x_train[:attack_train_size], y_train[:attack_train_size],
                                                        x_test[:attack_test_size], y_test[:attack_test_size])
            n = 60
            eval_data_idx = choice(len(x), n)
            x_eval, y_eval = x[eval_data_idx], y[eval_data_idx]
            eval_label = training_sample[eval_data_idx]
            pred_label = mia_label_only.infer(x_eval, y_eval)
            print("Accuracy: %f" % accuracy_score(eval_label, pred_label))
            score = accuracy_score(eval_label, pred_label)
            member_indexes = np.where(pred_label == 1)[0]
            member_values = [x[i] for i in member_indexes]
            # print("Data Which are infered by attacker \n", member_values)

            # Payload = {
            #         'modelName':modelName,
            #         'attackName':"LabelOnlyDecisionBoundary",
            #         'inference_acc':round(score,4),
            #         'infered_data':member_values
            #     }
        
            # foldername = RT.generateinferencereport(Payload)
            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_eval,'target_data':y_eval,'prediction_data':pred_label,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"LabelOnlyDecisionBoundary",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':score,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,x,y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "LabelOnlyDecisionBoundaryAttack", e, apiEndPoint, errorRequestMethod)    

    
    def AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1)
            Y = raw_data[[Output_column]]
            list_of_column_names.remove(Output_column)
            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
            x_train = x_train.to_numpy()
            x_test = x_test.to_numpy()
            y_train = y_train.to_numpy()
            y_test = y_test.to_numpy()
            
            art_classifier = SklearnClassifier(model = model)
            attack_feature = 2
            attack_x_test_predictions = np.array([np.argmax(arr) for arr in art_classifier.predict(x_test)]).reshape(-1,1)
            attack_x_test_feature = x_test[:, attack_feature].copy().reshape(-1, 1)
            attack_x_test = np.delete(x_test, attack_feature, 1)
            wb_attack = AttributeInferenceWhiteBoxLifestyleDecisionTree(SklearnClassifier(model=model), attack_feature=attack_feature)
            priors = [X.max()[attack_feature] / X.shape[0], X.min()[attack_feature] / X.shape[0]]
            values = [X.min()[attack_feature], X.max()[attack_feature]]
            inferred_train_wb1 = wb_attack.infer(attack_x_test, attack_x_test_predictions, values=values, priors=priors)
            train_acc = np.sum(inferred_train_wb1 == np.around(attack_x_test_feature, decimals=8).reshape(1,-1)) / len(inferred_train_wb1)
            attack_data = (inferred_train_wb1 == np.around(attack_x_test_feature, decimals=8).reshape(1,-1))[0].astype(int)
            print('train_acc:-',train_acc)

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_test,'target_data':y_test,'prediction_data':attack_data,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"AttributeInferenceWhiteBoxLifestyleDecisionTree",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':train_acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }
            
            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,Y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "AttributeInferenceWhiteBoxLifestyleDecisionTreeAttack", e, apiEndPoint, errorRequestMethod)    


    def AttributeInferenceWhiteBoxDecisionTreeAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1)
            Y = raw_data[[Output_column]]
            list_of_column_names.remove(Output_column)
            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
            x_train = x_train.to_numpy()
            x_test = x_test.to_numpy()
            y_train = y_train.to_numpy()
            y_test = y_test.to_numpy()
        
            art_classifier = SklearnClassifier(model = model)
            attack_feature = 2
            attack_x_test_predictions = np.array([np.argmax(arr) for arr in art_classifier.predict(x_test)]).reshape(-1,1)
            attack_x_test_feature = x_test[:, attack_feature].copy().reshape(-1, 1)
            attack_x_test = np.delete(x_test, attack_feature, 1)
            wb_attack = AttributeInferenceWhiteBoxDecisionTree(SklearnClassifier(model=model),attack_feature=attack_feature)
            priors = [X.max()[attack_feature] / X.shape[0], X.min()[attack_feature] / X.shape[0]]
            values = [X.min()[attack_feature], X.max()[attack_feature]]
            inferred_train_wb1 = wb_attack.infer(attack_x_test, attack_x_test_predictions,values=values,priors=priors)
            train_acc = np.sum(inferred_train_wb1 == np.around(attack_x_test_feature, decimals=8).reshape(1,-1)) / len(inferred_train_wb1)
            attack_data = (inferred_train_wb1 == np.around(attack_x_test_feature, decimals=8).reshape(1,-1))[0].astype(int)
            print('train_acc:-',train_acc)

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train,'target_data':y_train,'prediction_data':attack_data,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"AttributeInferenceWhiteBoxDecisionTree",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':train_acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }
        
            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,Y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "AttributeInferenceWhiteBoxDecisionTreeAttack", e, apiEndPoint, errorRequestMethod)    


    def InferenceLabelOnlyAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1).to_numpy()
            Y = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            # x_train, x_test, y_train, y_test = train_test_split(X,Y, test_size=0.2, random_state=123)
            x_train, x_test, y_train, y_test = train_test_split(X,Y, test_size=0.33, random_state=42)
            
            art_rf_classifier = SklearnClassifier(model=model)
            attack = LabelOnlyGapAttack(art_rf_classifier)
            inferred_train = attack.infer(x_train,y_train)
            inferred_test = attack.infer(x_test, y_test)
            train_acc = np.sum(inferred_train) / len(inferred_train)
            test_acc = 1 - (np.sum(inferred_test) / len(inferred_test))
            acc = (train_acc * len(inferred_train) + test_acc * len(inferred_test)) / (len(inferred_train) + len(inferred_test))
            print(f"Members Accuracy: {train_acc:.4f}")
            print(f"Attack Accuracy {acc:.4f}")

            attack_data_list,attack_data_status = UT.combineList({'attack_data':x_train,'target_data':y_train,'prediction_data':inferred_train,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"InferenceLabelOnlyGap",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,Y,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "InferenceLabelOnlyAttack", e, apiEndPoint, errorRequestMethod)    
    

    def AttributeInference(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X = raw_data.drop([Output_column], axis=1)
            Y = raw_data[[Output_column]]
            list_of_column_names.remove(Output_column)
            X_train1 = X.to_numpy()
            Y_train1 = Y.to_numpy()

            attack_train_ratio = 0.7
            attack_train_size = int(len(X_train1) * attack_train_ratio)
            attack_test_size = int(len(X_train1) * attack_train_ratio)
            attack_x_train = X_train1[:attack_train_size]
            attack_y_train = Y_train1[:attack_train_size]
            attack_x_test = X_train1[attack_train_size:]
            attack_y_test = Y_train1[attack_train_size:]
            attack_feature1 = 7  
            art_classifier= ScikitlearnClassifier(model)
            attack_x_test_predictions = np.array([np.argmax(arr) for arr in art_classifier.predict(attack_x_test)]).reshape(-1,1)
            attack_x_test_feature = attack_x_test[:, attack_feature1].copy().reshape(-1, 1)
            attack_x_test = np.delete(attack_x_test, attack_feature1, 1)
            bb_attack = AttributeInferenceBlackBox(art_classifier, attack_feature=attack_feature1)
            bb_attack.fit(attack_x_train)
            values = [X.min()[attack_feature1], X.max()[attack_feature1]]
            inferred_train_bb = bb_attack.infer(attack_x_test, pred=attack_x_test_predictions, values=values)
            train_acc = np.sum(inferred_train_bb == np.around(attack_x_test_feature, decimals=8).reshape(1,-1)) / len(inferred_train_bb)
            attack_data = (inferred_train_bb == np.around(attack_x_test_feature, decimals=8).reshape(1,-1))[0].astype(int)
            print('train_acc:-',train_acc)

            attack_data_list,attack_data_status = UT.combineList({'attack_data':attack_x_train,'target_data':attack_y_train,'prediction_data':attack_data,'type':'Inference'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"AttributeInference",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    'adversial_sample':attack_data_list,
                    'perturbation':train_acc,
                    'columns':list_of_column_names,
                    'attack_data_status':attack_data_status
                }
            
            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,X_train1,Y,Y_train1,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "AttributeInference", e, apiEndPoint, errorRequestMethod)    
    
# ---------------------------------------------------------------------------------------------------------------
    
    def ElasticNetAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"} 
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = ElasticNet(classifier=classifier)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^ElasticNet")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"ElasticNet",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_ElasticNet",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "ElasticNetAttack", e, apiEndPoint, errorRequestMethod)    


    def NewtonFoolAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))  

                attack = NewtonFool(classifier=classifier, eta=0.2)
                x_art_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^NewtonFool")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"NewtonFool",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_NewtonFool",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "NewtonFoolAttack", e, apiEndPoint, errorRequestMethod)        


    def SimbaAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = SimBA(classifier=classifier, epsilon=1.0025)
                x_art_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^SimBA")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"SimBA",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_SimBA",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation
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
                    executor.submit(log.log_error_to_telemetry, "SimbaAttack", e, apiEndPoint, errorRequestMethod)        


    def IterativeFrameSaliencyAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attacker = FastGradientMethod(estimator=classifier,eps=0.0025)
                attack = FrameSaliencyAttack(classifier=classifier,attacker=attacker)
                x_art_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^IterativeFrameSaliency")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"IterativeFrameSaliency",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_IterativeFrameSaliency",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "IterativeFrameSaliencyAttack", e, apiEndPoint, errorRequestMethod)        


    def SaliencyMapMethodAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = SaliencyMapMethod(classifier=classifier)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^SaliencyMapMethod")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"SaliencyMapMethod",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_SaliencyMapMethod",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "SaliencyMapMethodAttack", e, apiEndPoint, errorRequestMethod)        


    def BasicIterativeMethodAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = BasicIterativeMethod(estimator=classifier,max_iter=10,eps=1.0,eps_step=0.005)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^BasicIterativeMethod")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"BasicIterativeMethod",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_BasicIterativeMethod",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "BasicIterativeMethodAttack", e, apiEndPoint, errorRequestMethod)        


    def ProjectGradientDescentAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                adv = ProjectedGradientDescent(classifier,targeted=False,max_iter=10,eps=0.025)
                x_art_adv = adv.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^ProjectGradientDescentImage")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"ProjectGradientDescentImage",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_ProjectGradientDescentImage",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "ProjectGradientDescentAttack", e, apiEndPoint, errorRequestMethod)        


    def SquareAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))

                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                adv = SquareAttack(estimator =classifier,eps =0.01,max_iter=1000)
                x_art_adv = adv.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Square")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"Square",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_Square",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "SquareAttack", e, apiEndPoint, errorRequestMethod)        


    def SpatialTransformation(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))

                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                adv = SpatialTransformation(classifier =classifier, num_translations=50,max_translation =0.225,max_rotation=0.152,num_rotations=1)
                x_art_adv = adv.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class=Defect_Class[label_adv]
                print('Prediction:', Defect_Class[label_adv], '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^SpatialTransformation")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"SpatialTransformation",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_SpatialTransformation",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "SpatialTransformation", e, apiEndPoint, errorRequestMethod)        
    

    def FastGradientMethodAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = FastGradientMethod(estimator=classifier,eps=0.0025)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^FastGradientMethod")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"FastGradientMethod",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_FastGradientMethod",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "FastGradientMethodAttack", e, apiEndPoint, errorRequestMethod)        


    def UniversalPerturbationAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = UniversalPerturbation(classifier=classifier,attacker='pgd',eps=1.25)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^UniversalPerturbation")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"UniversalPerturbation",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_UniversalPerturbation",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "UniversalPerturbationAttack", e, apiEndPoint, errorRequestMethod)        


    def PixelAttack(payload):

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))

                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                attack = PixelAttack(classifier=classifier,max_iter=10,verbose=True)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Pixel")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"Pixel",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_Pixel",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "PixelAttack", e, apiEndPoint, errorRequestMethod)        


    def CarliniAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))

                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                attack = CarliniL2Method(classifier=classifier,max_iter=10)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^CarliniL2Method")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"CarliniL2Method",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_CarliniL2Method",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "CarliniAttack", e, apiEndPoint, errorRequestMethod)        


    def BoundaryAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                classifier = KerasClassifier(model=model, clip_values=(0, 255))

                attack = BoundaryAttack(estimator=classifier,targeted=False,epsilon=0.5,min_epsilon=0.25,delta=0.5)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Boundary")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"Boundary",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_Boundary",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "BoundaryAttack", e, apiEndPoint, errorRequestMethod)        


    def WassersteinAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))

                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                attack = Wasserstein(estimator=classifier)
                x_train_adv = attack.generate(x_art)
                pred_adv = classifier.predict(x_train_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_train_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Wasserstein")
                l.append(x_art)
                l.append(x_train_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)

            Payload = {
                    'modelName':modelName,
                    'attackName':"Wasserstein",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_Wasserstein",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_train_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "WassersteinAttack", e, apiEndPoint, errorRequestMethod)        
    

    def DeepfoolAttack(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            img, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            # img, data_path = UT.readDataFile(payload)
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
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"} 
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                base_prediction_class = Defect_Class[actual_prediction]
                print('Prediction:', base_prediction_class, '- confidence {0:.2f}'.format(base_actual_confidence))
                
                classifier = KerasClassifier(model=model, clip_values=(0, 255))
                adv= DeepFool(classifier=classifier,epsilon=0.000025,nb_grads=3)
                x_art_adv = adv.generate(x_art)
                pred_adv = classifier.predict(x_art_adv)
                label_adv = np.argmax(pred_adv, axis=1)[0]
                adv_confidence = pred[:,label_adv][0]
                # Defect_Class = {0: "Pit defect", 1: "Edge crack", 2: "Scratches", 3: "Rolled-in scale"}
                # Defect_Class = dict(zip(payload_data['groundTruthClassNames'], eval(payload_data['groundTruthClassLabel'])))
                Defect_Class = dict(zip(payload_data['groundTruthClassNames'], payload_data['groundTruthClassLabel'].split(',')))
                adv_prediction_class = Defect_Class[label_adv]
                print('Prediction:', adv_prediction_class, '- confidence {0:.2f}'.format(adv_confidence))
                perturbation = np.mean(np.abs((x_art_adv - x_art)))
                print('\nAverage perturbation: {:4.2f}'.format(perturbation))

                l.append(f"{k.split('.')[0]}^Deepfool")
                l.append(x_art)
                l.append(x_art_adv)
                l.append(base_prediction_class)
                l.append(adv_prediction_class)
                l.append(base_actual_confidence)
                l.append(adv_confidence)
                l.append(perturbation)
                attackDataList[k] = l
                # attackDataList.append(l)
            
            Payload = {
                    'modelName':modelName,
                    'attackName':"Deepfool",
                    # 'imageName':f"{os.path.basename(data_path).split('.')[0]}_Deepfool",
                    # 'base_sample':x_art,
                    # 'adversial_sample':x_art_adv,
                    # 'basePrediction_class':base_prediction_class,
                    # 'adversialPrediction_class':adv_prediction_class,
                    # 'baseActual_confidence':base_actual_confidence,
                    # 'adversialActual_confidence':adv_confidence,
                    # 'perturbation':perturbation,
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
                    executor.submit(log.log_error_to_telemetry, "DeepfoolAttack", e, apiEndPoint, errorRequestMethod)        

# ---------------------------------------------------------------------------------------------------------------
    
    def QueryEfficient(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X_train_1 = raw_data.drop([Output_column], axis=1).to_numpy()
            Y_train_1 = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            classifier = QueryEfficientGradientEstimationClassifier(classifier=SklearnClassifier(model=model), num_basis=10,sigma=0.01, round_samples=0.003)
            zoo = FastGradientMethod(estimator =classifier, eps=1)
            zoo_x_train_adv = zoo.generate(X_train_1)
            idx =0
            score = model.score(X_train_1, Y_train_1)

            # print("Benign Training Score: %.4f" % score)
            # print("Benign Training sample: ", X_train_1[idx,:])
            bprediction = model.predict([X_train_1[idx]])
            # print("Benign Training Predicted Label: %i" % bprediction)
            ascore = model.score(zoo_x_train_adv, Y_train_1)
            # print("\nAdversarial Training Score: %.4f" % ascore)
            # print("Adversarial Training sample: ", zoo_x_train_adv[idx])
            prediction = model.predict([zoo_x_train_adv[idx]])
            # print("Adversarial Training Predicted Label: %i" % prediction)
            # print("\nActual Label: %i" % Y_train_1[idx])
            perturbation = np.mean(np.abs((zoo_x_train_adv - X_train_1)))
            print('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':zoo_x_train_adv,'target_data':Y_train_1,'prediction_data':model.predict(zoo_x_train_adv),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])
            
            Payload = {
                    'modelName':modelName,
                    'attackName':"QueryEfficient",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    # 'base_sample':X_train_1[idx,:],
                    # 'adversial_sample':zoo_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':score,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bprediction,
                    # 'adversial_prediction':prediction,
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':Y_train_1[idx],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X_train_1,Y_train_1,zoo_x_train_adv,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "QueryEfficient", e, apiEndPoint, errorRequestMethod)        


    def ProjectedGradientDescentZoo(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            art_svm_classifier = SklearnClassifier(model=model)
            X_train = raw_data.drop([Output_column], axis=1).to_numpy()
            Y_train = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            pgd_attack = ProjectedGradientDescent(estimator=art_svm_classifier, targeted=False, max_iter=10, eps_step=1, eps=5)
            pgd_attack_x_train_adv = pgd_attack.generate(X_train)
            bscore = model.score(X_train, Y_train)

            # print("Benign Training Score: %.4f" % bscore)
            # print("Benign Training sample: ", X_train[0,:])
            bprediction = model.predict([X_train[0]])
            # print("Benign Training Predicted Label: %i" % bprediction)
            ascore = model.score(pgd_attack_x_train_adv, Y_train)
            # print("\nAdversarial Training Score: %.4f" % ascore)
            # print("Adversarial Training sample: ", pgd_attack_x_train_adv[0])
            aprediction = model.predict([pgd_attack_x_train_adv[0]])
            # print("Adversarial Training Predicted Label: %i" % aprediction)
            # print("\nActual Label: %i" % Y_train[0])
            perturbation = np.mean(np.abs((pgd_attack_x_train_adv - X_train)))
            print('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':pgd_attack_x_train_adv,'target_data':Y_train,'prediction_data':model.predict(pgd_attack_x_train_adv),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"ProjectedGradientDescentTabular",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    # 'base_sample':X_train[0,:],
                    # 'adversial_sample':pgd_attack_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bprediction,
                    # 'adversial_prediction':aprediction,
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':Y_train[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X_train,Y_train,pgd_attack_x_train_adv,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "ProjectedGradientDescentZoo", e, apiEndPoint, errorRequestMethod)        
    

    def DecisionTreeAttackVectors(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            list_of_column_names.remove(Output_column)
            X = raw_data.drop([Output_column], axis=1).to_numpy()
            y = raw_data[[Output_column]].to_numpy()
            X_train_1 = X[0:100,:]
            Y_train_1 = y[0:100]
            dt_attack = DecisionTreeAttack(classifier=SklearnClassifier(model=model))
            dt_attack_x_train_adv = dt_attack.generate(X_train_1)
            score = model.score(X_train_1, Y_train_1)

            # print("Benign Training Score: %.4f" % score)
            # print("Benign Training sample: ", X_train_1[0,:])
            prediction = model.predict([X_train_1[0]])
            # print("Benign Training Predicted Label: %i" % prediction)
            ascore = model.score(dt_attack_x_train_adv, Y_train_1)
            # print("\nAdversarial Training Score: %.4f" % ascore)
            # print("Adversarial Training sample: ", dt_attack_x_train_adv[0,:])
            aprediction = model.predict([dt_attack_x_train_adv[0]])
            # print("Adversarial Training Predicted Label: %i" % aprediction)
            # print("\nActual Label: %i" % Y_train_1[0])
            perturbation = np.mean(np.abs((dt_attack_x_train_adv - X_train_1)))
            print('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':dt_attack_x_train_adv,'target_data':Y_train_1,'prediction_data':model.predict(dt_attack_x_train_adv),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"DecisionTree",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    # 'base_sample':X_train_1[0,:],
                    # 'adversial_sample':dt_attack_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':round(score,4),
                    # 'adversial_score':round(ascore,4),
                    # 'base_prediction':prediction,
                    # 'adversial_prediction':aprediction,
                    'perturbation':round(perturbation,2),
                    'columns':list_of_column_names,
                    # 'actual_label':Y_train_1[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X,X_train_1,y,Y_train_1,dt_attack_x_train_adv,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "DecisionTreeAttackVectors", e, apiEndPoint, errorRequestMethod)        
    

    def HopSkipJumpCSV(payload): 

        try:

            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)

            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            #payload_folder_path = os.getcwd()[:-4] + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            X_train = raw_data.drop([Output_column], axis=1).to_numpy()
            Y_train = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            classifier =  ScikitlearnClassifier(model=model)
            ob=hop_skip_jump.HopSkipJump(classifier)
            attackVectors=ob.generate(X_train)
            bscore = model.score(X_train, Y_train)

            # print("Benign Training Score: %.4f" % bscore)
            # print("Benign Training sample: ", X_train[0,:])
            bprediction = model.predict([X_train[0]])
            # print("Benign Training Predicted Label: %i" % bprediction)
            ascore = model.score(attackVectors, Y_train)
            # print("\nAdversarial Training Score: %.4f" % ascore)
            # print("Adversarial Training sample: ", attackVectors[0])
            aprediction = model.predict([attackVectors[0]])
            # print("Adversarial Training Predicted Label: %i" % aprediction)
            # print("\nActual Label: %i" % Y_train[0])
            perturbation = np.mean(np.abs((attackVectors - X_train)))
            print('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':attackVectors,'target_data':Y_train,'prediction_data':model.predict(attackVectors),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"HopSkipJumpTabular",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    # 'base_sample':X_train[0,:],
                    # 'adversial_sample':attackVectors,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bprediction,
                    # 'adversial_prediction':aprediction,
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':Y_train[0],
                    'attack_data_status':attack_data_status
                }

            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X_train,Y_train,attackVectors,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "HopSkipJumpCSV", e, apiEndPoint, errorRequestMethod)        


    def ZooAttackVectors(payload): 

        try:
            
            model, model_path, modelName, modelFramework = UT.readModelFile(payload)
            raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
            Payload_path = UT.readPayloadFile(payload)
            
            list_of_column_names = list(raw_data.columns)
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,modelName + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            art_svm_classifier = SklearnClassifier(model=model)
            zoo = ZooAttack(classifier=art_svm_classifier, confidence=0.0, targeted=False, learning_rate=1e-1, max_iter=20,
                            binary_search_steps=10, initial_const=1e-3, abort_early=True, use_resize=False, 
                            use_importance=False, nb_parallel=1, batch_size=1, variable_h=0.2)
            X_train = raw_data.drop([Output_column], axis=1).to_numpy()
            Y_train = raw_data[[Output_column]].to_numpy()
            list_of_column_names.remove(Output_column)
            zoo_x_train_adv = zoo.generate(X_train)
            bscore = model.score(X_train, Y_train)

            # print("Benign Training Score: %.4f" % bscore)
            # print("Benign Training sample: ", X_train[0,:])
            bprediction = model.predict([X_train[0]])
            # print("Benign Training Predicted Label: %i" % bprediction)
            ascore = model.score(zoo_x_train_adv, Y_train)
            # print("\nAdversarial Training Score: %.4f" % ascore)
            # print("Adversarial Training sample: ", zoo_x_train_adv[0])
            aprediction = model.predict([zoo_x_train_adv[0]])
            # print("Adversarial Training Predicted Label: %i" % aprediction)
            # print("\nActual Label: %i" % Y_train[0])
            perturbation = np.mean(np.abs((zoo_x_train_adv - X_train)))
            print('\nAverage perturbation: {:4.2f}'.format(perturbation))

            attack_data_list,attack_data_status = UT.combineList({'attack_data':zoo_x_train_adv,'target_data':Y_train,'prediction_data':model.predict(zoo_x_train_adv),'adversial_score':ascore,'perturbation':perturbation,'type':'Evasion'})
            list_of_column_names.extend([Output_column, 'prediction', 'result'])

            Payload = {
                    'modelName':modelName,
                    'attackName':"ZerothOrderOptimization",
                    'data_path':data_path,
                    # 'dataFileName':os.path.basename(data_path).split('.')[0],
                    # 'base_sample':X_train[0,:],
                    # 'adversial_sample':zoo_x_train_adv,
                    'adversial_sample':attack_data_list,
                    # 'base_score':bscore,
                    # 'adversial_score':ascore,
                    # 'base_prediction':bprediction,
                    # 'adversial_prediction':aprediction,
                    'perturbation':perturbation,
                    'columns':list_of_column_names,
                    # 'actual_label':Y_train[0],
                    'attack_data_status':attack_data_status
                }
            
            foldername = RT.generatecsvreportart(Payload)
            UT.databaseDelete(model_path)
            UT.databaseDelete(data_path)
            UT.databaseDelete(Payload_path)
            del model,modelName,modelFramework,raw_data,X_train,Y_train,zoo_x_train_adv,attack_data_list,attack_data_status,list_of_column_names,Payload
            return {"Job_Id":f'{foldername}'}
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "ZooAttackVectors", e, apiEndPoint, errorRequestMethod)        

    
    # def VirtualAdversarialMethod(payload):

    #     try:

    #         model, model_path, modelName, modelFramework = UT.readModelFile(payload)
    #         raw_data, data_path = UT.readDataFile({'BatchId':payload, 'model':model ,'modelFramework':modelFramework})
    #         Payload_path = UT.readPayloadFile(payload)

    #         list_of_column_names = list(raw_data.columns)
    #         payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
    #         payload_path = os.path.join(payload_folder_path,modelName + ".txt")
    #         with open(f'{payload_path}') as f:
    #             data = f.read()
    #         data = json.loads(data)
    #         Output_column = data["groundTruthClassLabel"]
 
    #         datasetColumnLength = len(list_of_column_names)
    #         reshapeCol = math.sqrt(datasetColumnLength - 1)
    #         reshapeCol = int(reshapeCol)
    #         data = raw_data.drop([Output_column], axis=1).values
    #         labels = raw_data[Output_column].values
    #         data_list = [image.flatten() for image in data]
    #         data_list = [image / 255 for image in data_list]
    #         labels = labels.tolist()
    #         x_train, x_test, y_train, y_test = train_test_split(data_list, labels, test_size=0.25, random_state=42)
    #         x_train = np.array(x_train)
    #         x_test = np.array(x_test)
    #         y_train = np.array(y_train)
    #         y_test = np.array(y_test)
    #         x_test_shape = x_test.shape[0]
    #         y_test_shape = y_test.shape[0]
    #         if x_test_shape >= 100:
    #             x_test = x_test[0:100]
    #         else:
    #             x_test = x_test[0:x_test_shape]
    #         if y_test_shape >= 100:
    #             y_test = y_test[0:100]
    #         else:
    #             y_test = y_test[0:y_test_shape]
    #         nb_samples_train = x_train.shape[0]
    #         nb_samples_test = x_test.shape[0]
    #         x_train = x_train.reshape((nb_samples_train, reshapeCol * reshapeCol))
    #         x_test = x_test.reshape((nb_samples_test, reshapeCol * reshapeCol))
    #         list_of_column_names.remove(Output_column)
    #         attack = virtual_adversarial.VirtualAdversarialMethod(classifier=XGBoostClassifier(model=model,nb_features=reshapeCol * reshapeCol, nb_classes=10),max_iter=5,finite_diff=1.0,eps=0.4,verbose=True)
    #         x_test_adv = attack.generate(x=x_test, y=y_test)
    #         predictions = model.predict(x_test_adv)
    #         accuracy = np.sum(np.argmax(predictions, axis=1) == y_test )/ len(y_test)
    #         dim = tuple(range(1, len(x_test.shape)))
    #         perturbation = np.mean(np.amax(np.abs(x_test - x_test_adv), axis=dim))
    #         attack_data_list,attack_data_status = UT.combineList({'attack_data':x_test_adv,'target_data':y_test.reshape(-1, 1),'prediction_data':np.argmax(predictions, axis=1),'type':'Evasion'})
    #         list_of_column_names.extend([Output_column, 'prediction', 'result'])
    #         #print("Accuracy on adversarial test data: {}%".format(accuracy * 100))
 
    #         Payload = {
    #                 'modelName':modelName,
    #                 'attackName':"VirtualAdversarialMethod",
    #                 'dataFileName':os.path.basename(data_path).split('.')[0],
    #                 'adversial_sample':attack_data_list,
    #                 'perturbation':perturbation,
    #                 'columns':list_of_column_names,
    #                 'attack_data_status':attack_data_status
    #             }
 
    #         foldername = RT.generatecsvreportart(Payload)
    #         UT.databaseDelete(model_path)
    #         UT.databaseDelete(data_path)
    #         UT.databaseDelete(Payload_path)
    #         return {"Job_Id":f'{foldername}'}
        
    #     except Exception as e:
    #         if(telemetry_flg == 'True'):
    #             with con.ThreadPoolExecutor() as executor:  
    #                 executor.submit(log.log_error_to_telemetry, "VirtualAdversarialMethod", e, apiEndPoint, errorRequestMethod)
   
    
    # def GeometricDecisionAttack(payload):
       
    #     try:

    #         img, data_path = UT.readDataFile(payload)
    #         model, model_path, modelName = UT.readModelFile(payload)
    #         Payload_path = UT.readPayloadFile(payload)
           
    #         # list_of_column_names = list(raw_data.columns)
    #         payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
    #         payload_path = os.path.join(payload_folder_path,modelName + ".txt")
           
    #         with open(f'{payload_path}') as f:
    #             data = f.read()
 
    #         data = json.loads(data)
           
    #         target_classes = data["groundTruthClassLabel"]        
    #         target_classes_int = data['groundTruthClassNames']
           
    #         # dictionary of class mapping
    #         target_classes_dict = dict(zip(target_classes_int, target_classes))        
    #         num_classes = len(target_classes_int)
           
    #         img_array = image.img_to_array(img)
    #         input_shape_orig = img_array.shape        
    #         # target_size = input_shape_orig[:2]
           
    #         img_array = grayscale_to_rgb(img_array) if img_array.shape[-1] == 1 else img_array        
    #         img_array = img_array / 255.0
    #         img_array = np.expand_dims(img_array, axis=0)
           
    #         classifier =  TensorFlowV2Classifier(model=model, clip_values=(0, 1),
    #                                             nb_classes=num_classes, input_shape=input_shape_orig)
           
    #         print("\nGENERATING ATTACK DATA ...........")
    #         ob = GeoDA(classifier, verbose=True)
    #         attackVectors = ob.generate(img_array)
           
    #         print("\nSAMPLE TEST: ............")
           
    #         bprediction_encoded = classifier.predict(img_array)
    #         bprediction = np.argmax(bprediction_encoded, axis=1)
    #         bconfidence = bprediction_encoded[:,bprediction][0]    
    #         bprediction_cls = target_classes_dict[bprediction[0]]
    #         bprediction_cls_int = bprediction[0]
    #         print(f"Benign Predicted Label: {bprediction_cls_int} => {bprediction_cls} ")
 
    #         aprediction_encoded = classifier.predict(attackVectors)
    #         aprediction = np.argmax(aprediction_encoded, axis=1)
    #         aconfidence = aprediction_encoded[:,aprediction][0]
    #         aprediction_cls = target_classes_dict[aprediction[0]]
    #         aprediction_cls_int = aprediction[0]
    #         print(f"Adversarial Predicted Label: {aprediction_cls_int} => {aprediction_cls}")
           
    #         perturbation = np.mean(np.abs((attackVectors - img_array)))
    #         print('\nAverage perturbation over all samples: {:4.2f}'.format(perturbation))
           
    #         Payload = {
    #                 'modelName':modelName,
    #                 'attackName':"GeometricDecisionBasedAttack",
    #                 'imageName':f"{os.path.basename(data_path).split('.')[0]}_GeoDecisionAttack",
    #                 'base_sample':img_array,
    #                 'adversial_sample':attackVectors,
    #                 'basePrediction_class':bprediction_cls,
    #                 'adversialPrediction_class':aprediction_cls,
    #                 'baseActual_confidence':bconfidence,
    #                 'adversialActual_confidence':aconfidence,
    #                 'perturbation':perturbation,
    #             }
           
    #         foldername = RT.generateimagereport(Payload)
    #         UT.databaseDelete(model_path)
    #         UT.databaseDelete(data_path)
    #         UT.databaseDelete(Payload_path)
    #         return {"Job_Id":f'{foldername}'}
    #     except Exception as e:
    #         if(telemetry_flg == 'True'):
    #             with con.ThreadPoolExecutor() as executor:
    #                 executor.submit(log.log_error_to_telemetry, "GeometricDecisionAttack", e, apiEndPoint, errorRequestMethod)
   

    # def Threshold(payload):
    #     try:
    #         if tf.executing_eagerly():
    #             tf.compat.v1.disable_eager_execution()  
 
    #         raw_data, data_path = UT.readDataFile(payload)
    #         model, model_path, modelName = UT.readModelFile(payload)
    #         Payload_path = UT.readPayloadFile(payload)
 
    #         list_of_column_names = list(raw_data.columns)
    #         payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
    #         payload_path = os.path.join(payload_folder_path,modelName + ".txt")
    #         with open(f'{payload_path}') as f:
    #             data = f.read()
    #         data = json.loads(data)
    #         Output_column = data["groundTruthClassLabel"]
 
    #         datasetColumnLength = len(list_of_column_names)
    #         reshapeCol = math.sqrt(datasetColumnLength - 1)
    #         reshapeCol = int(reshapeCol)
    #         data = raw_data.drop([Output_column], axis=1).values
    #         labels = raw_data[Output_column].values
    #         data_list = [image.reshape((reshapeCol, reshapeCol)) / 255.0 for image in data]
    #         labels = labels.tolist()
    #         x_train, x_test, y_train, y_test = train_test_split(data_list, labels, test_size=0.25, random_state=42)
    #         x_train=np.array(x_train)
    #         x_test=np.array(x_test)
    #         y_train=np.array(y_train)
    #         y_test=np.array(y_test)
    #         x_train = x_train.reshape((-1, reshapeCol, reshapeCol, 1)).astype(np.float32) / 255.0
    #         x_test = x_test.reshape((-1, reshapeCol, reshapeCol, 1)).astype(np.float32) / 255.0
    #         encoder = OneHotEncoder()
    #         y_train = encoder.fit_transform(y_train.reshape(-1, 1)).toarray()
    #         y_test = encoder.fit_transform(y_test.reshape(-1, 1)).toarray()
    #         x_test_shape = x_test.shape[0]
    #         y_test_shape = y_test.shape[0]
    #         if x_test_shape >= 100:
    #             x_test_1 = x_test[0:100]
    #             x_test_shape = 100
    #         else:
    #             x_test_1 = x_test[0:x_test_shape]  
    #         if y_test_shape >= 100:
    #             y_test_1 = y_test[0:100]
    #             y_test_shape = 100
    #         else:
    #             y_test_1 = y_test[0:y_test_shape]      
    #         list_of_column_names.remove(Output_column)
 
    #         classifier_original = KerasClassifier(model, clip_values=(0, 1), use_logits=False)
       
    #         threshold_attack = ThresholdAttack(classifier=classifier_original,th= None,es= 1,max_iter= 10,targeted= False,verbose = True)
   
    #         result = threshold_attack.generate(x_test_1)
    #         perturbed_predictions = model.predict(result)
    #         dim = tuple(range(1, len(x_test_1.shape)))
    #         perturbation = np.mean(np.amax(np.abs(x_test_1 - result), axis=dim))
    #         reshapedAdversialData = result.reshape(x_test_shape,reshapeCol*reshapeCol)
    #         attack_data_list,attack_data_status = UT.combineList({'attack_data':reshapedAdversialData,'target_data':np.argmax(y_test_1, axis=1).reshape(-1, 1),'prediction_data':np.argmax(perturbed_predictions, axis=1),'type':'Evasion'})
    #         list_of_column_names.extend([Output_column, 'prediction', 'result'])
   
    #         Payload = {
    #                 'modelName':modelName,
    #                 'attackName':"Threshold",
    #                 'dataFileName':os.path.basename(data_path).split('.')[0],
    #                 'adversial_sample':attack_data_list,
    #                 'perturbation':perturbation,
    #                 'columns':list_of_column_names,
    #                 'attack_data_status':attack_data_status
    #             }
           
    #         foldername = RT.generatecsvreportart1(Payload)
    #         UT.databaseDelete(model_path)
    #         UT.databaseDelete(data_path)
    #         UT.databaseDelete(Payload_path)
       
    #         return {"Job_Id":f'{foldername}'}
    #     except Exception as e:
    #         if(telemetry_flg == 'True'):
    #             with con.ThreadPoolExecutor() as executor:
    #                 executor.submit(log.log_error_to_telemetry, "Threshold", e, apiEndPoint, errorRequestMethod)
    
    
    # def HopSkipJumpImage(payload): 

    #     raw_data, data_path = UT.readDataFile(payload)
    #     model, model_path, modelName = UT.readModelFile(payload)
    #     Payload_path = UT.readPayloadFile(payload)
       
    #     list_of_column_names = list(raw_data.columns)
    #     payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
    #     payload_path = os.path.join(payload_folder_path,modelName + ".txt")
    #     with open(f'{payload_path}') as f:
    #         data = f.read()
    #     data = json.loads(data)
    #     Output_column = data["targetColumnNames"]  
    #     raw_data = raw_data.iloc[0:10,:]  
    #     x = raw_data.drop([Output_column], axis=1).to_numpy()
    #     y = raw_data[[Output_column]].to_numpy()
    #     list_of_column_names.remove(Output_column)
    #     x = x.reshape(-1,28,28,1)
    #     classifier =  KerasClassifier(model=model)
    #     ob = hop_skip_jump.HopSkipJump(classifier)
    #     attackVectors = ob.generate(x)

    #     l=[]
    #     l.append(x[0])
    #     l=np.array(l)
    #     pred=model.predict(l)
    #     label_benign = np.argmax(pred, axis=1)[0]
    #     print("Benign Predicted Label : ", label_benign)
    #     j=attackVectors.reshape(attackVectors.shape[0],-1)
    #     h=pd.DataFrame(j,columns=list_of_column_names)
    #     # print("Adversial Whole DataFrame : ",h)
    #     # print("Adversial sample: ", attackVectors[0])
    #     m=[]
    #     m.append(attackVectors[0])
    #     m=np.array(m)
    #     pred=model.predict(m)
    #     label_adv = np.argmax(pred, axis=1)[0]
    #     print("Adversial Predicted Label : ", label_adv)
    #     perturbation = np.mean(np.abs((attackVectors - x)))
    #     print('\nAverage perturbation: {:4.2f}'.format(perturbation))

    #     attack_data_status = UT.checkList({'model':model, 'original_data':x, 'adversial_data':attackVectors})

    #     Payload = {
    #             'modelName':modelName,
    #             'attackName':"HopSkipJumpImage",
    #             'dataFileName':os.path.basename(data_path).split('.')[0],
    #             # 'base_sample':x[0],
    #             'adversial_sample':attackVectors[0],
    #             # 'basePrediction_label':label_benign,
    #             # 'adversialPrediction_label':label_adv,
    #             # 'attack_array':j,
    #             # 'adversial_dataframe':h,
    #             'perturbation':perturbation,
    #             'columns':list_of_column_names,
    #             'attack_data_status':attack_data_status
    #         }
 
    #     foldername = RT.generatecsvreportart(Payload)
    #     UT.databaseDelete(model_path)
    #     UT.databaseDelete(data_path)
    #     UT.databaseDelete(Payload_path)
    #     return {"Job_Id":f'{foldername}'}
  
# ---------------------------------------------------------------------------------------------------------------