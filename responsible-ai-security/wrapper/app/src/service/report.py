'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''




import os
import shutil
import pandas as pd
import numpy as np
import csv
import json
import matplotlib.pyplot as plt
from pathlib import Path

from src.config.urls import UrlLinks as UL
from src.service.utility import Utility as UT
from src.service.defence import Defence as DF
from src.config.logger import CustomLogger
import concurrent.futures as con

telemetry_flg =os.getenv("TELEMETRY_FLAG")

apiEndPoint ='/v1/security/model'
errorRequestMethod = 'GET'

log =CustomLogger()

class Report:

    def generateimagereport(payload):
        
        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            Current_Report_ID = UL.Current_ID + 1
            foldername = f'{payload["attackName"]}_{Current_Report_ID}'
            xlfilename = 'Attack_Samples.xlsx'
            root_path = root_path + "/report"
            report_path = os.path.join(root_path,foldername)
            if os.path.isdir(report_path):    #These 2Lines are anyway useless with unique ART_ID
                return foldername
            os.mkdir(report_path)

            attack_status_row = ""
            for dataList in payload['attackDataList']:
                field_names = [f'Base Model Name','Actual Labels','Confidence Score']
                attack_status_dict={f'Base Model Name':payload["modelName"],'Actual Labels':payload['attackDataList'][dataList][3],'Confidence Score':payload['attackDataList'][dataList][5]}
                row = f"""
                    <tr>
                        <td>
                            <div class="attack-data-table-img-column">
                                <div class="attack-data-table-img-column-value">{attack_status_dict['Base Model Name']}</div>
                            </div>
                        </td>
                        <td>
                            <div class="attack-data-table-img-column">
                                <div class="attack-data-table-img-column-value">{attack_status_dict['Actual Labels']}</div>
                            </div>
                        </td>
                        <td>
                            <div class="attack-data-table-img-column">
                                <div class="attack-data-table-img-column-value">{attack_status_dict['Confidence Score']:.4f}</div>
                            </div>
                        </td>
                    </tr>
                """
                attack_status_row += row


            items_not_equal = [(key, value) for key, value in payload['attackDataList'].items() if value[3] != value[4]]
            sorted_items_not_equal = sorted(items_not_equal, key=lambda x: x[1][6], reverse=True)
            top_keys = [item[0] for item in sorted_items_not_equal]
            sorted_dict = {key: value for key, value in sorted_items_not_equal}
            items_equal = [(key, value) for key, value in payload['attackDataList'].items() if value[3] == value[4]]
            sorted_dict.update({key: value for key, value in items_equal})
            payload['attackDataList'] = sorted_dict

            attack_ipop_row = ""
            for dataList in payload['attackDataList']:
                field_names = [f'Image Name', 'Actual Labels', 'Final Labels','Confidence Score', 'Success']
                val:any
                if payload['attackDataList'][dataList][3] == payload['attackDataList'][dataList][4]:
                    val = 'False'
                else:
                    val = 'True'
                attack_data_dict = {f'Image Name':payload['attackDataList'][dataList][0].split('^')[0], 'Actual Labels':payload['attackDataList'][dataList][3], 'Final Labels':payload['attackDataList'][dataList][4], 'Confidence Score':payload['attackDataList'][dataList][6], 'Success':val}
                if payload['attackDataList'][dataList][0].split('^')[1] in UT.AttackTypes['Art']['Evasion']:
                    file_path = str(Path.home() / 'Downloads' / payload['modelName'] / 'Evasion' / f"{payload['attackName']}" / f"{payload['attackDataList'][dataList][0].split('^')[0]}.{dataList.split('.')[1]}").replace('\\', '/')
                    row = f"""
                        <tr>
                            
                            <td>Art/Evasion/{payload['attackName']}/{attack_data_dict['Image Name']}</td>
                            <td>{attack_data_dict['Actual Labels']}</td>
                            <td>{attack_data_dict['Final Labels']}</td>
                            <td>{attack_data_dict['Confidence Score']:.4f}</td>
                            <td>{attack_data_dict['Success']}</td>
                        </tr>
                    """
                elif payload['attackDataList'][dataList][0].split('^')[1] in UT.AttackTypes['Art']['Inference']:
                    file_path = str(Path.home() / 'Downloads' / payload['modelName'] / 'Inference' / f"{payload['attackName']}" / f"{payload['attackDataList'][dataList][0].split('^')[0]}.{dataList.split('.')[1]}").replace('\\', '/')
                    row = f"""
                        <tr>
                        
                            <td>Art/Inference/{payload['attackName']}/{attack_data_dict['Image Name']}</td>
                            <td>{attack_data_dict['Actual Labels']}</td>
                            <td>{attack_data_dict['Final Labels']}</td>
                            <td>{attack_data_dict['Confidence Score']:.4f}</td>
                            <td>{attack_data_dict['Success']}</td>
                        </tr>
                    """
                elif payload['attackDataList'][dataList][0].split('^')[1] in UT.AttackTypes['Augly']['Augmentation']:
                    file_path = str(Path.home() / 'Downloads' / payload['modelName'] / 'Augmentation' / f"{payload['attackName']}" / f"{payload['attackDataList'][dataList][0].split('^')[0]}.{dataList.split('.')[1]}").replace('\\', '/')
                    row = f"""
                        <tr>
                        
                            <td>Augly/Augmentation/{payload['attackName']}/{attack_data_dict['Image Name']}</td>
                            <td>{attack_data_dict['Actual Labels']}</td>
                            <td>{attack_data_dict['Final Labels']}</td>
                            <td>{attack_data_dict['Confidence Score']:.4f}</td>
                            <td>{attack_data_dict['Success']}</td>
                        </tr>
                    """
                attack_ipop_row += row


            # Generating Attack Samples
            for dataList in payload['attackDataList']:
                img_path:any
                if payload['attackDataList'][dataList][3] == payload['attackDataList'][dataList][4]:
                    img_path = os.path.join(report_path, f"{payload['attackDataList'][dataList][0]+'F'}.{dataList.split('.')[1]}")
                else:
                    img_path = os.path.join(report_path, f"{payload['attackDataList'][dataList][0]+'T'}.{dataList.split('.')[1]}")
                plt.imshow(payload['attackDataList'][dataList][2][0])
                plt.axis('off')
                plt.title('Adversarial Sample')
                plt.savefig(img_path)
                plt.close()
            graph_html = UT.graphForAttack({'folder_path':report_path, 'attackName':payload["attackName"], 'attackDataList':payload['attackDataList'], 'top_keys':top_keys, 'type':'Image'})
            html_data = UT.htmlContentReport({'attackName':payload["attackName"],'graph_html':graph_html,'attack_ipop_row':attack_ipop_row, 'type':'Image'})
            
            with open(os.path.join(report_path,f"report.html"),"w") as file:
                file.writelines(UT.htmlCssContentReport({'type':'Image'}))
                file.writelines(html_data)


            shutil.make_archive(report_path,'zip',report_path)
            UT.updateCurrentID()
            del attack_status_row,items_not_equal,sorted_items_not_equal,top_keys,sorted_dict,items_equal,attack_ipop_row,graph_html,html_data
            return foldername
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generateimagereport", e, apiEndPoint, errorRequestMethod)

    
    def generatecsvreportart(payload):

        try:
            root_path = os.getcwd()
            root_path = UT.getcurrentDirectory() + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            Current_Report_ID = UL.Current_ID + 1
            foldername = f'{payload["attackName"]}_{Current_Report_ID}'
            csvfilename = 'Attack_Samples.csv'
            root_path = root_path + "/report"
            report_path = os.path.join(root_path,foldername)
            if os.path.isdir(report_path):    #These 2Lines are anyway useless with unique ART_ID
                return foldername
            os.mkdir(report_path)

            payload_folder_path = UT.getcurrentDirectory() + "/database/payload"
            payload_path = os.path.join(payload_folder_path,payload['modelName'] + ".txt")
            with open(f'{payload_path}') as f:
                data = f.read()
            data = json.loads(data)
            type = data['targetClassifier']
            tag = data['dataType']

            # Generating Attack Samples
            if payload["attackName"] == "HopSkipJumpImage":
                with open(os.path.join(report_path,csvfilename), 'w',newline="") as f:
                    write = csv.writer(f)
                    write.writerow(payload['columns'])
                    write.writerows(payload['attack_array'])
            else:
                with open(os.path.join(report_path,csvfilename), 'w',newline="") as f:
                    write = csv.writer(f)
                    write.writerow(payload['columns'])
                    write.writerows(payload['adversial_sample'])

            #Generating Defense Model
            DF.generateDenfenseModel({'modelName':payload['modelName'],'folderName':foldername, 'data_path':payload['data_path'], 'adversarial_path':os.path.join(report_path,csvfilename)})
            
            # generating graph for particular attack  
            csv_path = os.path.join(report_path,csvfilename)
            df = pd.read_csv(csv_path)
            cols = list(df.columns)
            key = 0
            if data['groundTruthClassLabel'] in cols and 'prediction' in cols:
                graph_html = UT.graphForAttack({'folder_path':report_path, 'target':data['groundTruthClassLabel'], 'attackName':payload["attackName"], 'type':'Tabular'})
                key = 1
            
            # Attack Status Data
            field_names = ['Attack id', 'Model Name', 'Attack Name', 'Status', 'Mean Difference']
            attack_status_dict={'Attack id':f'InfosysModelReport{Current_Report_ID}','Model Name':payload['modelName'],'Attack Name':payload["attackName"],'Status':'Complete','Mean Difference':payload['perturbation']}
            attack_status_row = f"""
                <tr>
                    <td>
                        <div class="attack-data-table-column">
                            <div class="attack-data-table-column-value">{attack_status_dict['Attack id']}</div>
                        </div>
                    </td>
                    <td>
                        <div class="attack-data-table-column">
                            <div class="attack-data-table-column-value">{attack_status_dict['Model Name']}</div>
                        </div>
                    </td>
                    <td>
                        <div class="attack-data-table-column">
                            <div class="attack-data-table-column-value">{attack_status_dict['Attack Name']}</div>
                        </div>
                    </td>
                    <td>
                        <div class="attack-data-table-column">
                            <div class="attack-data-table-column-value">{attack_status_dict['Status']}</div>
                        </div>
                    </td>
                    <td>
                        <div class="attack-data-table-column">
                            <div class="attack-data-table-column-value">{attack_status_dict['Mean Difference']:.4f}</div>
                        </div>
                    </td>
                </tr>
            """
            # Attack Input-Output Data (take only 5 rows for sample)
            attack_input_output_list = []
            for i in range(len(payload['attack_data_status'])):
                d = {}
                d['sample_index'] = payload['attack_data_status'][i][0]
                d['actual_labels'] = payload['attack_data_status'][i][1]
                d['final_labels'] = payload['attack_data_status'][i][2]
                d['success'] = payload['attack_data_status'][i][3]
                attack_input_output_list.append(d)
            attack_ipop_row = ""
            count = 0
            for data_list in attack_input_output_list:
                count += 1
                row = f"""
                <tr>
                    <td>{data_list['sample_index']}</td>
                    <td>{data_list['actual_labels']}</td>
                    <td>{data_list['final_labels']}</td>
                    <td>{data_list['success']}</td>
                </tr>
                """
                attack_ipop_row += row
                if count == 5:
                    break

            # most attackable column
            column_graph_data = UT.graphForAttackColumn({'report_path':report_path,'adversarial_data_path':os.path.join(report_path,csvfilename),'original_data_path':payload['data_path'],'type':'Tabular', 'attackName':payload['attackName']})
            
            # Call htmlContentReport
            html_data = UT.htmlContentReport({'attackName':payload["attackName"],'graph_html':graph_html,'attack_status_row':attack_status_row,'attack_ipop_row':attack_ipop_row, 'type':'Tabular', 'column_graph_data':column_graph_data})
            
            with open(os.path.join(report_path,f"report.html"),"w") as file:
                file.writelines(UT.htmlCssContentReport({'type':'Tabular'}))
                file.writelines(html_data)
            
            
            shutil.make_archive(report_path,'zip',report_path)
            UT.updateCurrentID()

            del df,cols,attack_status_row,attack_input_output_list,attack_ipop_row,column_graph_data,html_data
            return foldername
        
        except Exception as e:
            if(telemetry_flg == 'True'):
                with con.ThreadPoolExecutor() as executor:
                    executor.submit(log.log_error_to_telemetry, "generatecsvreportart", e, apiEndPoint, errorRequestMethod)