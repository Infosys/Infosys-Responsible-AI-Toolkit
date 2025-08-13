"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
from fastapi import HTTPException
import pandas
import matplotlib.pyplot as plt
import base64
import os
import time
import tempfile
import requests
from datetime import datetime
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

from fairness.constants.local_constants import *
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.Filestore import FileStore
from fairness.config.logger import CustomLogger
log = CustomLogger()


class Utils:
    def __init__(self) -> None:
        # self.fileStore = FileStoreReportDb()
        self.fileStore = FileStore()
    
    def save_as_json_file_obj(self,fileName:str,content):
        with open(fileName, "w") as outfile:
            json.dump(content,outfile,indent=2)
    
    def save_as_json_file(self, fileName:str, content1, content2=None):
        combined_content = {"content1": content1, "content2": content2}
        with open(fileName, "w") as outfile:
            json.dump(combined_content, outfile, indent=2)

    def save_as_file(self,filename:str, content):
        with open(filename,"wb") as outfile:
            outfile.write(content)
    
    def read_html_file(self,filename:str):
        with open(filename, 'r') as file:
            html_content = file.read()
        return html_content
    
    def json_to_html_individualMetric(self,json_obj2,label, Datainfo = None, unprivileged= None, methodType=None):
        utils = Utils()
        df = pandas.read_json(json.dumps(json_obj2))
        # Extract metric names and values
        data = df.iloc[0]
        content = data[label]
        name = content['name']
        name_dict = {"CONSISTENCY": "Consistency"}
        name= name_dict[name]
        value = float(content['value'])
        desc=content['description']
        methodType = Datainfo[1]
        protectedattribute = str(Datainfo[3])
        privileged = str(Datainfo[4])
        protct = protectedattribute.replace("'", "").replace("[","").replace("]","")
        html_content = ""
        html_content +=f"""
            <table border="1" style="border-collapse: collapse; width:100%; font-family: sans-serif; font-size:16px">
                <tr>
                    <th>Metric</th>
                    <th>Protected Attribute</th>
                    <th>Result</th>
                </tr>
        """
        if methodType == "ALL":
            # If methodType is passed, call a function
            html_content += f"""
            <body>
                <h3 style='color:#963596; text-align:left; font-size:19px; font-family: sans-serif;'>INDIVIDUAL METRICS</h3>
                <p style='font-family: sans-serif; font-size:16px;'>Individual metrics in fairness analysis assess the performance and treatment of individual instances within a dataset or model. These metrics focus on outcomes for specific individuals rather than comparing groups. They evaluate how consistently and fairly an individual is treated based on their characteristics.</p>
            </body>
            """
            if value > 0.70:
                html_content += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{protct}</td>
                        <td style='color: green;'>Pass</td>    
                    </tr>
                """
            elif value < 0.70:
                html_content += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{protct}</td>
                        <td style='color: red;'>Fail</td>   
                    </tr>
                """
        else:
            result = utils.html_new(Datainfo, unprivileged)
            log.info(f"result{result}")
            html_content += result
            html_content += f"""
            <body>
                <h3 style='color:#963596; text-align:left; font-size:19px; font-family: sans-serif;'>INDIVIDUAL METRICS</h3>
                <p style='font-family: sans-serif; font-size:16px;'>Individual metrics in fairness analysis assess the performance and treatment of individual instances within a dataset or model. These metrics focus on outcomes for specific individuals rather than comparing groups. They evaluate how consistently and fairly an individual is treated based on their characteristics.</p>
            </body>
            """
            if value > 0.70:
                html_content += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{protct}</td>
                        <td style='color: green;'>Pass</td>    
                    </tr>
                """
            elif value < 0.70:
                html_content += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{protct}</td>
                        <td style='color: red;'>Fail</td>   
                    </tr>
                """
        html_content += "</table>"
        html_content += """
            <body>
            <h3 style='font-family: sans-serif; font-size:17px;'>Note:</h3>
            <p style='font-family: sans-serif; font-size:16px;'>Pass: A higher consistency value indicates that the predictions for similar instances are more consistent.</p>
            <p style='font-family: sans-serif; font-size:16px;'>Fail: A lower consistency value indicates that the predictions for similar instances are less consistent.</p>
            </body>
        """


        return html_content

    def json_to_html(self,json_obj,json_obj2,label,Datainfo=None,unprivileged=None):
        utils = Utils()
        # fileName = Datainfo[0]
        biasType = Datainfo[0]
        bias_dict = {"PRETRAIN": "Pretrain", "POSTTRAIN": "Posttrain"}
        biasType = bias_dict[biasType]
        methodType = Datainfo[1]
        taskType = Datainfo[2]
        task_dict = {"CLASSIFICATION": "Classification"}
        taskType = task_dict[taskType]
        protectedattribute = str(Datainfo[3])
        protct = protectedattribute.replace("'", "").replace("[","").replace("]","") # Remove quotes
        privileged = str(Datainfo[4])
        privl = privileged.replace("'", "").replace("[","").replace("]","") 
        unpriv = str(unprivileged)
        unprivl = unpriv.replace("'", "").replace("[","").replace("]","")  
        # if json_obj2 is not None:
        #     utils.json_to_html_individualMetric(json_obj2,label)
        df = pandas.read_json(json.dumps(json_obj))
 
    # Extract metric names and values
        data = df.iloc[0]
        metrics = data['metrics']
 
        # # Generate HTML content
        html_content = f"""
        <div style='display: flex; justify-content: center; align-items: left; color:white; background-color: #963596; font-size:23px; font-family: sans-serif; border-radius: 10px; position: relative;'>
            <h2 style='margin: 0; style=font-family: sans-serif;'>INFOSYS RESPONSIBLE AI OFFICE</h2>
            <span style='position:absolute; right:1; font-size:15px; align-self: center; padding: 0 10px;'>{timestamp}</span>
        </div>
        """
        # html_content += f"<h3 style='font-weight:normal; color:#963596; font-size:23px font-family: sans-serif;'>FAIRNESS REPORT</h3>"
        # html_content = html_content+f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:16px; font-family: sans-serif;'>{F_Desc}</h3>"
        # html_content = html_content+f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:16px; font-family: sans-serif;'>{Obj_Desc}</h3>"
        html_content += f"""
        <body>
            <h3 style='color:#963596; text-align:left; font-size:19px; font-family: sans-serif;'>FAIRNESS REPORT</h3>
            <p style='font-family: sans-serif; font-size:16px;'>{Obj_Desc}</p>
        </body>
        """
        html_content += f"""
        <div style='width: 50%; font-family: sans-serif;'>
            <h3 class="header" style="color:#963596; font-size:19px;"><strong>DATA INFORMATION</strong></h3>
            <table>
                <tr><td style="font-size:16px; font-family: sans-serif;">Bias Type</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{biasType}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Bias Detection Technique(s)</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{methodType}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Task Type</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{taskType}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Privileged Group(s)</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{privl}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Unprivileged Group(s)</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{unprivl}</td></tr>
            </table>
        </div>
        """
        html_content += f"""
        <body>
            <h3 style='color:#963596; text-align:left; font-size:19px; font-family: sans-serif;'>GROUP METRICS</h3>
            <p style='font-family: sans-serif; font-size:16px;'>Group metrics are measures used to compare the success rates of different groups, like privileged and unprivileged.</p>
        </body>
        """
        html_content +=f"""
            <table border="1" style="border-collapse: collapse; width:100%;  font-size:16px; font-family: sans-serif;">
                <tr>
                    <th style= >Metric</th>
                    <th>Protected Attribute</th>
                    <th>Indicator</th>
                    <th>Favouring Groups</th>
                    <th>Unfavouring Groups</th>
                </tr>
        """

        # Iterate over metrics and create plots
        for metric in metrics:
            metric_name = metric['name']
            log.info(f"metric_name{metric_name}")
            if biasType == "Pretrain":
                metric_dict = {"STATISTICAL PARITY-DIFFERENCE": "Statistical Parity Difference", "DISPARATE-IMPACT": "Disparate Impact", "SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS": "Smoothed Empirical Differential Fairness", "BASE_RATE": "base rate" }
                metric_name = metric_dict[metric_name]
                metric_value = float(metric['value'])
                metric_desc=metric['description']
                if metric_name == "Statistical Parity Difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td> 
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                if metric_name == "Disparate Impact":
                    if metric_value > 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                if metric_name == "Smoothed Empirical Differential Fairness":
                    if metric_value > 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>No Bias</td>
                            <td>No Bias</td>
                        </tr>
                        """
                    elif metric_value < 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
            # html_content += "</table>"
            
            else: 
                metric_name = metric['name']
                log.info(f"metric_name{metric_name}")
                metric_value = float(metric['value'])
                metric_desc=metric['description']
                if metric_name == "Statistical parity":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td> 
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "Disparate Impact":
                    if metric_value > 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 1:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "Four Fifths":
                    if metric_value > 0.8:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>
                        </tr>
                        """
                    elif metric_value < 0.8:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>     
                        </tr>
                        """
                elif metric_name == "Cohen D":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td> 
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "Equality of opportunity difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td> 
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "False positive rate difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "False negative Rate difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>     
                        </tr>
                        """
                elif metric_name == "True negative Rate difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """
                elif metric_name == "Average Odds Difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>     
                        </tr>
                        """
                elif metric_name == "Accuracy Difference":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>     
                        </tr>
                        """
                elif metric_name == "Z Test (Difference)":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>     
                        </tr>
                        """

                elif metric_name == "ABROCA (area between roc curves).":
                    if metric_value > 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{privl}</td>
                            <td>{unprivl}</td>
                            
                        </tr>
                        """
                    elif metric_value == 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>No Bias</td>
                            <td>NA</td>
                            <td>NA</td>
                        </tr>
                        """
                    elif metric_value < 0:
                        html_content += f"""
                        <tr>
                            <td>{metric_name}</td>
                            <td>{protct}</td>
                            <td>Bias</td>
                            <td>{unprivl}</td>
                            <td>{privl}</td>     
                        </tr>
                        """
        if json_obj2 is not None:
            result = utils.json_to_html_individualMetric(json_obj2,label,Datainfo)
            html_content += result
        html_content += "</table>"
        return html_content

    def html_new(self, Datainfo=None, unprivileged=None):
        biasType = Datainfo[0]
        methodType = Datainfo[1]
        taskType = Datainfo[2]
        bias_dict = {"PRETRAIN": "Pretrain", "POSTTRAIN": "Posttrain"}
        biasType = bias_dict[biasType]
        task_dict = {"CLASSIFICATION": "Classification"}
        taskType = task_dict[taskType]
        method_dict = {"ALL": "All", "STATISTICAL-PARITY-DIFFERENCE": "Statistical Parity Difference", "DISPARATE-IMPACT": "Disparate Impact", "SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS": "Smoothed Empirical Differential Fairness", "CONSISTENCY": "consistency"}
        methodType = method_dict[methodType]
        protectedattribute = str(Datainfo[3])
        protct = protectedattribute.replace("'", "").replace("[","").replace("]","") # Remove quotes
        privileged = str(Datainfo[4])
        privl = privileged.replace("'", "").replace("[","").replace("]","") 
        unpriv = str(unprivileged)
        unprivl = unpriv.replace("'", "").replace("[","").replace("]","")  

        html_content = f"""
        <div style='display: flex; justify-content: center; align-items: left; color:white; background-color: #963596; font-size:23px; font-family: sans-serif; border-radius: 10px; position: relative;'>
            <h2 style='margin: 0;'>INFOSYS RESPONSIBLE AI OFFICE</h2>
            <span style='position:absolute; right:1; font-size:15px; align-self: center; padding: 0 10px;'>{timestamp}</span>
        </div>
        """
        html_content += f"<body><h3 style='color:#963596; text-align:left; font-size:23px' style=font-family: sans-serif;>FAIRNESS REPORT</h3></body>"
        html_content = html_content+f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px; color: darkgray; style=font-family: sans-serif;'>{F_Desc}</h3>"
        html_content = html_content+f"<h3 style='font-weight:normal; font-family: sans-serif; font-size:17px; color: darkgray;style=font-family: sans-serif;'>{Obj_Desc}</h3>"
        html_content += f"""
        <div style='width: 50%;'>
            <h3 class="header" style="font-size:22px; color:#963596;"><strong>DATA INFORMATION</strong></h3>
            <p><strong style="color:#963596; font-size:16px; font-family: sans-serif;">BiasType:</strong> <span style="color: darkgray; font-size:16px; font-family: sans-serif;">{biasType}</span></p>
            <p><strong style="color:#963596; font-size:16px; font-family: sans-serif;">MethodType:</strong> <span style="color: darkgray; font-size:16px; font-family: sans-serif;">{methodType}</span></p>
            <p><strong style="color:#963596; font-size:16px; font-family: sans-serif;">TaskType:</strong> <span style="color: darkgray; font-size:16px; font-family: sans-serif;">{taskType}</span></p>
            <p><strong style="color:#963596; font-size:16px; font-family: sans-serif;">privilegedGroup:</strong> <span style="color: darkgray; font-size:16px; font-family: sans-serif;">{privl}</span></p>
            <p><strong style="color:#963596; font-size:16px; font-family: sans-serif;">unprivilegedGroup:</strong> <span style="color: darkgray; font-size:16px; font-family: sans-serif;">{unprivl}</span></p>
        </div>
        """
        return html_content
                
    def save_html_to_file(self,html_string, filename):
        with open(filename, 'w') as f:
            f.write(html_string)

    def parse_nutanix_bucket_object(self,fullpath: str):
        split_path = fullpath.split("//")
        return {'bucket_name': split_path[0], 'object_key': "/".join(split_path[1:])}
    
    def get_data_frame(self,extension: str,tpath: str,sep: str, usecols: list):
        if extension == "csv":
            return  pandas.read_csv(tpath,sep=",", usecols=usecols)
        elif extension=="parquet":
            return pandas.read_parquet(tpath,sep=",", usecols=usecols)
        elif extension == "feather":
            return pandas.read_feather(tpath,sep=",", usecols=usecols)
        elif extension == "json":
            return pandas.read_json(tpath,sep=",", usecols=usecols)
    
    def uploadfile_to_db(self,uploadPath,filePath):
         # to upload file in Nutanix
        buck_dict = self.parse_nutanix_bucket_object(uploadPath)
        bucket_ = buck_dict['bucket_name']
        key_ = buck_dict['object_key']
        strt_time = time.time()
        log.info(f"Start time{strt_time}")
        fileName=os.path.basename(filePath)
        NutanixObjectStorage.upload_with_high_threshold(filePath, bucket_,
                                                        key_ + "/" + fileName, 10)
        end_time = time.time()
        log.info(f"End time{end_time}")
        log.info(f"Total Time:{end_time - strt_time}")
    
    def uploadfile_to_mongodb(self,filePath,fileType=None):
        log.info(f"filePath{filePath}")
         # to upload file in Mongodb
        strt_time = time.time()
        log.info(f"Start time {strt_time}")
        fileId=self.fileStore.save_local_file(filePath=filePath,fileType=fileType)
        log.info(fileId)
        end_time = time.time()
        log.info(f"End time{end_time}")
        log.info(f"Total Time:{end_time - strt_time}")
        return fileId
    
    def modifyDf(self,df,catAttribute,labelmap,label):
        reverseLabelMap={v: k for k, v in labelmap.items()}
        def map_values(x):
            if int(x) == 1:
                return "privileged"
            else:
                return "unprivileged"
        for cat in catAttribute['name']:
            df[cat]=df[cat].apply(map_values).astype(str)
        df[label]=df[label].map(reverseLabelMap).astype(str)
        return df
    
    def pretrain_save_file(self,df: pandas.DataFrame, extension: str, file_path: str):
        if extension == "csv":
            df.to_csv(file_path, index=False)
        elif extension == "parquet":
            df.to_parquet(file_path, index=False)
        elif extension == "json":
            df.to_json(file_path, index=False, orient='records')
        elif extension == "feather":
            df.to_feather(file_path)

    def get_extension(self,fileName: str):
        if fileName.endswith(".csv"):
            return "csv"
        elif fileName.endswith(".feather"):
            return "feather"
        elif fileName.endswith(".parquet"):
            return "parquet"
        elif fileName.endswith(".json"):
            return "json"

    def get_data_frame(self,extension: str, fileName: str):
        # if extension == "csv":
        return pandas.read_csv(os.path.join(self.LOCAL_FILE_PATH, fileName))
        # elif extension=="parquet":
        #     return pandas.read_parquet(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))
        # elif extension == "feather":
        #     return pandas.read_feather(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))
        # elif extension == "json":
        #     return pandas.read_json(os.path.join(FairnessService.LOCAL_FILE_PATH, fileName))

    def store_file_locally(self,extension, file_content, file_path, file_name):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create temporary file
            temp_file_name = temp_file.name
            # Write binary data to the temporary file
            file_content = file_content.read()
            temp_file.write(file_content)
            # Reset the file pointer to the beginning for reading
            temp_file.seek(0)

            df = pandas.DataFrame()
            if extension == "csv":
                df = pandas.read_csv(temp_file)
            elif extension == "parquet":
                df = pandas.read_parquet(temp_file)
            elif extension == "feather":
                df = pandas.read_feather(temp_file)
            elif extension == "json":
                df = pandas.read_json(temp_file)
            df.to_csv(os.path.join(file_path, file_name), index=False)
            # Close the temporary file before deletion
            temp_file.close()
        os.remove(temp_file_name)

    
    def store_file_locally_DB(self,extension, file_content, file_path, file_name):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create temporary file
            temp_file_name = temp_file.name
            # Write binary data to the temporary file
            file_content = file_content
            temp_file.write(file_content)
            # Reset the file pointer to the beginning for reading
            temp_file.seek(0)

            df = pandas.DataFrame()
            if extension == "csv":
                df = pandas.read_csv(temp_file)
            elif extension == "parquet":
                df = pandas.read_parquet(temp_file)
            elif extension == "feather":
                df = pandas.read_feather(temp_file)
            elif extension == "json":
                df = pandas.read_json(temp_file)
            df.to_csv(os.path.join(file_path, file_name), index=False)
            # Close the temporary file before deletion
            temp_file.close()
        os.remove(temp_file_name)
        # with open(os.path.join(file_path, file_name), 'wb') as f:
        #     f.write(file_content.read())
        
        
    def parse_priv(self, priv):
        priv_list = []
        i = 0
        while (i < len(priv)):
            if "[" in priv[i]:
                i += 1
                priv_string = ""
                while (i < len(priv) and "]" not in priv[i]):
                    if "[" in priv[i]:
                        raise HTTPException(
                            status_code=400, detail="Priviledged attribute not closed properly")
                    priv_string += priv[i]
                    i += 1
                if "]" not in priv[i]:
                    raise HTTPException(
                        status_code=400, detail="Priviledged attribute not closed properly")
                i += 1
                priv_array = priv_string.split(",")
                priv_list.append(priv_array)
            else:
                if "," in priv[i]:
                    i += 1
                if "[" in priv[i]:
                    continue
                priv_string = ""
                while (i < len(priv) and "," not in priv[i]):
                    if priv[i] == '[' or priv[i] == ']':
                        raise HTTPException(
                            status_code=400, detail="Priviledged attribute not opened properly")
                    priv_string += priv[i]
                    i += 1
                if i < len(priv) and "," not in priv[i]:
                    raise HTTPException(
                        status_code=400, detail="Priviledged attribute not closed properly")
                priv_list.append([priv_string])
                i += 1
        return priv_list
    
    def is_time_difference_12_hours(self, creation_time, expiration_time):
        """
        Checks if the time difference between current time and creation time is 12 hours.
        Args:
            creation_time (datetime.datetime): The time the item was created.
            expiration_time (int): The expiration time in hours.
        Returns:
            bool: True if the time difference is 12 hours, False otherwise.
        """
        time_difference = datetime.now() - creation_time
        log.info(f"time diff : {time_difference}")
        log.info(f"time diff total hours : {time_difference.total_seconds() / 3600}")

        # Check if difference is exactly 12 hours, accounting for minutes and seconds
        return (time_difference.total_seconds() / 3600) < expiration_time