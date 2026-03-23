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
import csv
import json
import pickle

import seaborn as sns
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from src.service.utility import Utility as UT
from src.config.logger import CustomLogger
import concurrent.futures as con


telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

log = CustomLogger()

class Defence:


    def generateDenfenseModel1(payload):
        
        try:
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = ""
            SAFE_DIR = payload_folder_path
            def open_safe_file(filename):
                if '..' in filename or '/' in filename:
                    raise ValueError("Invalid filename")
                payload_path = os.path.join(SAFE_DIR, filename+".txt")
                return open(os.path.join(SAFE_DIR, filename+".txt"), "w", newline="")
            
            with open_safe_file(payload["modelName"]) as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]
            
            #reading original dataset
            data_path = UT.getcurrentDirectory()+f'/database/data/{payload["dataFileName"]}.csv'
            df1 = pd.read_csv(data_path, delimiter=',')
            df1.drop(Output_column,axis=1,inplace=True)
            df1.insert(df1.shape[1],"Attack",[0 for i in range(df1.shape[0])])

            #reading attack dataset
            root_path = UT.getcurrentDirectory() + "/database/report"
            report_folder = os.path.join(root_path,payload['folderName'])
            report_csv = os.path.join(report_folder,'Attack_Samples.csv')
            df2 = pd.read_csv(report_csv)
            df2.drop(Output_column,axis=1,inplace=True)
            df2.drop(columns=df2.columns[-2:], axis=1, inplace=True)
            cols = list(df2.columns)
            df2.insert(df2.shape[1],"Attack",[1 for i in range(df2.shape[0])])
    
            #creating defensemodel dataset
            fields=[]
            for col in df1.columns:
                fields.append(col)
            df1=np.array(df1)
            df2=np.array(df2)

            #creating defense_model path
            root_path = UT.getcurrentDirectory() + "/database"
            report_path = os.path.join(root_path+"/report",payload['folderName'])
            temp_path = root_path + "/cacheMemory"

            SAFE_DIR = temp_path
            def open_safe_file(filename):
                if '..' in filename or '/' in filename:
                    raise ValueError("Invalid filename")
                temp_path = os.path.join(SAFE_DIR, filename)
                return open(os.path.join(SAFE_DIR, filename),"w",newline="")
            with open_safe_file(f'{payload["modelName"]}defenseModel.csv') as f:
                write = csv.writer(f)
                write.writerow(fields)
                write.writerows(df1)
                write.writerows(df2)
        
            # creating defense Model
            df=pd.read_csv(temp_path)
            X=df.loc[:,df.columns!="Attack"]
            Y=df["Attack"]
            X_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.25,random_state=1)
            model=XGBClassifier()
            model.fit(X_train,y_train)
            pickle.dump(model, open(os.path.join(report_path,"DefenseModel.pkl"), 'wb'))

            del model,X_train,x_test,y_train,y_test,df1,df2
            UT.databaseDelete(temp_path)
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateDenfenseModel", exc, apiEndPoint, errorRequestMethod)
            raise Exception


    def generateCombinedDenfenseModel1(payload):

        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
        
            Output_column = payload['payloadData']['groundTruthClassLabel']

            dfs = []
            fields = []
            for filename in os.listdir(payload['report_path']):
                if filename.endswith('.csv'):
                    if filename == payload['modelName']+'.csv':   # reading original dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        df.drop(Output_column,axis=1,inplace=True)
                        df.insert(df.shape[1],"Attack",[0 for i in range(df.shape[0])])
                        for col in df.columns:
                            fields.append(col)
                        df = np.array(df)
                        dfs.append(df)
                    else:                                         # reading attack dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        df = df[df[df.columns[-1]] == True]
                        df.drop(Output_column,axis=1,inplace=True)
                        df.drop(columns=df.columns[-2:], axis=1, inplace=True)
                        cols = list(df.columns)
                        df.insert(df.shape[1],"Attack",[1 for i in range(df.shape[0])])
                        df = np.array(df)
                        dfs.append(df)       
            
            # creating defense_model path
            temp_path = root_path + "/cacheMemory"
            SAFE_DIR = temp_path
            def open_safe_file(filename):
                if '..' in filename or '/' in filename:
                    raise ValueError("Invalid filename")
                temp_path = os.path.join(SAFE_DIR, filename)
                return open(os.path.join(SAFE_DIR, filename),"w",newline="")
            with open(temp_path,"w",newline="") as f:
                write = csv.writer(f)
                write.writerow(fields)
                for df in dfs:
                    write.writerows(df)
            
            # creating defense Model
            df = pd.read_csv(temp_path)
            X = df.loc[:,df.columns!="Attack"]
            Y = df["Attack"]
            X_train,x_test,y_train,y_test = train_test_split(X,Y,test_size=0.25,random_state=1)
            model = XGBClassifier()
            model.fit(X_train,y_train)
            pickle.dump(model, open(os.path.join(payload['report_path'],"DefenseModel.pkl"), 'wb'))

            del model,X_train,x_test,y_train,y_test
            UT.databaseDelete(temp_path)

        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateCombinedDenfenseModel", e, apiEndPoint, errorRequestMethod)
            raise Exception
        return "Success"
    

    def generateDenfenseModel(payload):
        
        try:
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,payload["modelName"] + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            #reading original dataset
            df1 = pd.read_csv(payload['data_path'], delimiter=',')
            df1.drop(Output_column,axis=1,inplace=True)
            df1.insert(df1.shape[1],"Attack",[0 for i in range(df1.shape[0])])

            df2 = pd.read_csv(payload['adversarial_path'], delimiter=',')
            df2.drop(Output_column,axis=1,inplace=True)
            df2.drop(columns=df2.columns[-2:], axis=1, inplace=True)
            cols = list(df2.columns)
            df2.insert(df2.shape[1],"Attack",[1 for i in range(df2.shape[0])])
    
            #creating defensemodel dataset
            fields=[]
            for col in df1.columns:
                fields.append(col)
            df1=np.array(df1)
            df2=np.array(df2)

            #creating defense_model path
            root_path = UT.getcurrentDirectory() + "/database"
            report_path = os.path.join(root_path+"/report",payload['folderName'])
            temp_path = root_path + "/cacheMemory"
            temp_path = os.path.join(temp_path,f'{payload["modelName"]}defenseModel.csv')

            if os.path.exists(temp_path):
                os.remove(temp_path)
            with open(temp_path,"w",newline="") as f:
                write = csv.writer(f)
                write.writerow(fields)
                write.writerows(df1)
                write.writerows(df2)
        
            # creating defense Model
            df=pd.read_csv(temp_path)
            X=df.loc[:,df.columns!="Attack"]
            Y=df["Attack"]
            X_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.25,random_state=1)
            model=XGBClassifier()
            model.fit(X_train,y_train)
            pickle.dump(model, open(os.path.join(report_path,"DefenseModel.pkl"), 'wb'))

            del model,X_train,x_test,y_train,y_test,df1,df2,df
            UT.databaseDelete(temp_path)

        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateDenfenseModel", exc, apiEndPoint, errorRequestMethod)
            raise Exception


    def generateCombinedDenfenseModel2(payload):

        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
        
            Output_column = payload['payloadData']['groundTruthClassLabel']

            dfs = []
            fields = []
            for filename in os.listdir(payload['report_path']):
                if filename.endswith('.csv'):
                    if filename == payload['dataFileName']+'.csv':   # reading original dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        df.drop(Output_column,axis=1,inplace=True)
                        df.insert(df.shape[1],"Attack",[0 for i in range(df.shape[0])])
                        for col in df.columns:
                            fields.append(col)
                        df = np.array(df)
                        dfs.append(df)
                    else:                                         # reading attack dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        df = df[df[df.columns[-1]] == True]
                        df.drop(Output_column,axis=1,inplace=True)
                        df.drop(columns=df.columns[-2:], axis=1, inplace=True)
                        cols = list(df.columns)
                        df.insert(df.shape[1],"Attack",[1 for i in range(df.shape[0])])
                        df = np.array(df)
                        dfs.append(df)       
            
            # creating defense_model path
            temp_path = root_path + "/cacheMemory"
            temp_path = os.path.join(temp_path,f"{payload['modelName']}defenseModel.csv")

            if os.path.exists(temp_path):
                os.remove(temp_path)
            with open(temp_path,"w",newline="") as f:
                write = csv.writer(f)
                write.writerow(fields)
                for df in dfs:
                    write.writerows(df)
            
            # creating defense Model
            df = pd.read_csv(temp_path)
            X = df.loc[:,df.columns!="Attack"]
            Y = df["Attack"]
            X_train,x_test,y_train,y_test = train_test_split(X,Y,test_size=0.25,random_state=1)
            model = XGBClassifier()
            model.fit(X_train,y_train)
            pickle.dump(model, open(os.path.join(payload['report_path'],"DefenseModel.pkl"), 'wb'))

            del model,X_train,x_test,y_train,y_test
            UT.databaseDelete(temp_path)

        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateCombinedDenfenseModel", exc, apiEndPoint, errorRequestMethod)
            raise Exception
    
    
    def generateCombinedDenfenseModel(payload):

        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)
        
            Output_column = payload['payloadData']['groundTruthClassLabel']

            # Create a dictionary to store the data
            data_dict = {}
            max_filename_len = 0
            filenames = []
            shapes = []
            for filename in os.listdir(payload['report_path']):
                if filename.endswith('.csv'):
                      # reading original dataset
                    if filename == payload['dataFileName']+'.csv':   # reading original dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        X = df.drop(Output_column, axis=1)
                        Y = df[Output_column]
                        filenames.append(filename)
                        shapes.append(df.shape)
                        max_filename_len = max(max_filename_len, len(filename))
                        
                    else:                                         # reading attack dataset
                        file_path = os.path.join(payload['report_path'], filename)
                        df = pd.read_csv(file_path)
                        X = df.drop(df.columns[-3:], axis=1)
                        Y = df[df.columns[-2]]
                        filenames.append(filename)
                        shapes.append(df.shape)
                        max_filename_len = max(max_filename_len, len(filename))

                    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=1)
                    data_dict[filename] = [X_train, X_test, Y_train, Y_test]  
            log.info(f"{'-'*16} shape of all available adversarial dataset {'-'*20}")
            for filename, shape in zip(filenames, shapes):
                log.info(f"{filename:<{max_filename_len}} :-  {shape}")           
            log.info("-"*80)

            # Loop through each filename in the dictionary
            all_X_train = []
            all_X_test = []
            all_Y_train = []
            all_Y_test = []
            for filename in data_dict:
                all_X_train.append(data_dict[filename][0])
                all_X_test.append(data_dict[filename][1])
                all_Y_train.append(data_dict[filename][2])
                all_Y_test.append(data_dict[filename][3])
            
            # Concatenate all X_train, X_test, Y_train, Y_test dataframes
            X_train_all = pd.concat([df for df in all_X_train])
            X_test_all = pd.concat([df for df in all_X_test])
            Y_train_all = pd.concat([df.reset_index(drop=True) for df in all_Y_train]).rename('target')
            Y_test_all = pd.concat([df.reset_index(drop=True) for df in all_Y_test]).rename('target')
            
            # Create and train an LogisticRegression model
            model = LogisticRegression()
            model.fit(X_train_all, Y_train_all)

            # Make predictions on the test set
            Y_pred = model.predict(X_test_all)

            # Evaluate the model's performance
            accuracy = accuracy_score(Y_test_all, Y_pred)

            # Calculate confusion matrix
            conf_mat = confusion_matrix(Y_test_all, Y_pred)

            classification_reports = classification_report(Y_test_all, Y_pred, output_dict=True)

            # Calculate particular attack accuracy
            attack_accuracy_dict = {}
            for filename in data_dict:
                Y_pred_particular = model.predict(data_dict[filename][1])
                accuracy_particular = accuracy_score(data_dict[filename][3], Y_pred_particular)
                attack_accuracy_dict[filename] = accuracy_particular


            # Export model file in that path
            pickle.dump(model, open(os.path.join(payload['report_path'],"DefenseModel.pkl"), 'wb'))
            return conf_mat, classification_reports, attack_accuracy_dict

        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateCombinedDenfenseModel", exc, apiEndPoint, errorRequestMethod)
            raise Exception


    def generateDenfenseModelendpoint(payload):
        
        try:
            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = ""
            SAFE_DIR = payload_folder_path
            def open_safe_file(filename):
                if '..' in filename or '/' in filename:
                    raise ValueError("Invalid filename")
                payload_path = os.path.join(SAFE_DIR, filename+".txt")
                return open(os.path.join(SAFE_DIR, filename+".txt"), "w", newline="")
            
            with open_safe_file(payload["modelName"]) as f:
                data = f.read()
            data = json.loads(data)
            Output_column = data["groundTruthClassLabel"]

            #reading original dataset
            data_path = UT.getcurrentDirectory()+f'/database/data/{payload["modelName"]}.csv'
            df1 = pd.read_csv(data_path, delimiter=',')
            df1.drop(Output_column,axis=1,inplace=True)
            df1.insert(df1.shape[1],"Attack",[0 for i in range(df1.shape[0])])

            root_path = UT.getcurrentDirectory() + "/database/report"
            report_folder = os.path.join(root_path,payload['folderName'])
            report_csv = os.path.join(report_folder,'Attack_Samples.csv')
            df2 = pd.read_csv(report_csv)
            df2.drop(Output_column,axis=1,inplace=True)
            df2.drop(columns=df2.columns[-2:], axis=1, inplace=True)
            cols = list(df2.columns)
            df2.insert(df2.shape[1],"Attack",[1 for i in range(df2.shape[0])])
    
            #creating defensemodel dataset
            fields=[]
            for col in df1.columns:
                fields.append(col)
            df1=np.array(df1)
            df2=np.array(df2)

            #creating defense_model path
            root_path = UT.getcurrentDirectory() + "/database"
            report_path = os.path.join(root_path+"/report",payload['folderName'])
            temp_path = root_path + "/cacheMemory"

            SAFE_DIR = temp_path
            def open_safe_file(filename):
                if '..' in filename or '/' in filename:
                    raise ValueError("Invalid filename")
                temp_path = os.path.join(SAFE_DIR, filename)
                return open(os.path.join(SAFE_DIR, filename),"w",newline="")
            with open_safe_file(f'{payload["modelName"]}defenseModel.csv') as f:
                write = csv.writer(f)
                write.writerow(fields)
                write.writerows(df1)
                write.writerows(df2)
        
            # creating defense Model
            df=pd.read_csv(temp_path)
            X=df.loc[:,df.columns!="Attack"]
            Y=df["Attack"]
            X_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.25,random_state=1)
            model=XGBClassifier()
            model.fit(X_train,y_train)
            pickle.dump(model, open(os.path.join(report_path,"DefenseModel.pkl"), 'wb'))

            del model,X_train,x_test,y_train,y_test,df1,df2
            UT.databaseDelete(temp_path)
        except Exception as exc:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateDenfenseModelendpoint", exc, apiEndPoint, errorRequestMethod)
            raise Exception