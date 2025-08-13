"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import base64
import datetime
from io import BytesIO
import time
from fastapi import HTTPException
import numpy as np
import pandas
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import requests
from fairness.constants.llm_constants import SUCCESS_RATE_INFO
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.Data import Dataset,DataAttributes,DataAttributeValues
from fairness.dao.databaseconnection import DataBase
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.report import Report
from fairness.dao.WorkBench.html import Html
import uuid
from fpdf import FPDF
from PIL import Image
from scipy import stats   
from fairness.config.logger import CustomLogger

log = CustomLogger()

LOCAL_FILE_PATH="../output/datasets/"
SUCCESS_RATE_LOCAL_PATH='../output/graphs/success_rates/'
OUTPUT_FOLDER='../output/'
class SuccessRateService:
    def __init__(self, db=None):
        self.db = DataBase().db
        self.fileStore = FileStoreReportDb()
        self.batch =  Batch()
        self.tenet =  Tenet()
        self.dataset = Dataset()
        self.dataAttributes = DataAttributes()
        self.dataAttributeValues = DataAttributeValues()
    def check_categorical_attributes(categorical_attributes,data):
        for each in categorical_attributes:
            if each not in list(data.columns):
                raise HTTPException({"error": "Categorical attribute not found"}, "Categorical attribute not found", "Categorical attribute not found")
    


    def get_extension(fileName: str):
        if fileName.endswith(".csv"):
            return "csv"
        elif fileName.endswith(".feather"):
            return "feather"
        elif fileName.endswith(".parquet"):
            return "parquet"
        elif fileName.endswith(".json"):
            return "json"   

    def get_data_frame(extension: str,fileName: str):
        return  pandas.read_csv(os.path.join(LOCAL_FILE_PATH, fileName))

    def get_dataframe(extension,file):
        if extension == "csv":
               return  pandas.read_csv(file)
        elif extension=="parquet":
            return pandas.read_parquet(file)
        elif extension == "feather":
            return pandas.read_feather(file)
        elif extension == "json":
            return pandas.read_json(file)
    class HTMLStylePDF(FPDF):
        def header(self):
            # No standard header
            pass
        
        def footer(self):
            # No standard footer
            pass
    def image_to_pdf(image_paths, output_pdf, title=None):
        pdf = FPDF()
        pdf.add_page()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add title if provided
        if title:
            PURPLE = (150, 53, 150)
            WHITE = (255, 255, 255)
            BLACK = (0, 0, 0)
            
            # Header section
            pdf.set_font('Helvetica', 'B', 23)
            pdf.set_text_color(*WHITE)
            pdf.set_fill_color(*PURPLE)
            
            # Full-width header
            pdf.cell(0, 15, 'INFOSYS RESPONSIBLE AI OFFICE', 
                    align='C', fill=True, border=0)            
            # Reset Y position
            pdf.set_y(30)
        pdf.set_y(25)  # Reduce vertical space
        pdf.set_text_color(*PURPLE)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 10, 'REPORT', ln=True)
        
        # Success Rate
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*BLACK)
        lines = SUCCESS_RATE_INFO.split('\n')
        for line in lines:
            pdf.cell(0, 10, line, ln=True)
        # Add image
            # Process each image
        for index,image_path in enumerate(image_paths):
            # Add a new page
            if index!=0:
                pdf.add_page()
            
            # Open image to get dimensions
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate scaling to fit page width
            page_width = pdf.w
            page_height = pdf.h
            
            # Calculate scaling factor
            width_scale = page_width / img_width
            height_scale = page_height / img_height
            
            # Use the smaller scale to ensure image fits
            scale_factor = min(width_scale, height_scale)
            
            new_width = img_width * scale_factor
            new_height = img_height * scale_factor
            
            # Calculate positioning to center the image
            x_position = (page_width - new_width) / 2
            y_position = (page_height - new_height) / 2
            
            # Add image to PDF
            pdf.image(image_path, x=x_position, y=y_position, w=new_width, h=new_height)
        
        # Save PDF
        pdf.output(output_pdf)
        print(f"PDF created: {output_pdf}")

    
    def create_graphs(success_rates):
        pdf_name="population_success_rate_"+str(uuid.uuid4())+".pdf"
        pdf_path=os.path.join(SUCCESS_RATE_LOCAL_PATH,pdf_name)
        image_paths=[]
        try:
            with PdfPages(pdf_path) as pdf:
                for attribute, each_group in success_rates.items():
                    subclasses = list(each_group.keys())
                    grouped_success_rates = [each_group[group]["group_success_rate"] for group in each_group]
                    population_success_rates = [each_group[group]["population_success_rate"] for group in each_group]
                    participations = [each_group[group]["population"] for group in each_group]
                    n_groups=len(subclasses)
                    bar_width = 0.35 if n_groups<=20 else 0.2
                    font_size=10 if n_groups<=20 else 8
                    fig_height=8+n_groups*0.5
                    x=np.arange(len(subclasses))
                    figure_width = max(len(subclasses) * 1, 13)
                    # Add banner at the top
                    fig,(ax1)=plt.subplots(1,1,figsize=(figure_width,fig_height),gridspec_kw={'height_ratios':[2]})
                    bars_success_rate=ax1.bar(x,population_success_rates,bar_width,label='Success Rate',color='lightblue')
                    bars_ppopulation=ax1.bar(x+bar_width,participations,bar_width,label='Population',color='orange')
                    for i,bar in enumerate(bars_ppopulation):
                        height=bar.get_height()
                        if abs(participations[i]-population_success_rates[i])<3.0:
                            ax1.text(bar.get_x()+bar.get_width()/2,height+5,f'{participations[i]:.2f}',ha='center',va='bottom',fontsize=10,color='black')
                        else:
                            ax1.text(bar.get_x()+bar.get_width()/2,height+2,f'{participations[i]:.2f}',ha='center',va='bottom',fontsize=10,color='black')
                    max_height=0
                    for i,bar in enumerate(bars_success_rate):
                        height=bar.get_height()
                        max_height=max(max_height,height)
                        ax1.text(bar.get_x()+bar.get_width()/2,height+2,f'{population_success_rates[i]:.2f}',ha='center',va='bottom',fontsize=10,color='black')
                        
                    line_success_rate=ax1.plot(x+bar_width/2,grouped_success_rates,marker='o',color='b',label='Grouped Success Rate')
                    for i,rate in enumerate(grouped_success_rates):
                        ax1.text(x[i]+bar_width/2,rate+2,f'{rate:.2f}',ha='center',va='bottom',fontsize=10,color='b')
                    ax1.set_ylabel('Population (%)')
                    ax1.set_title("Population and Success Rate for "+attribute,fontsize=14)
                    ax1.set_xticks(x+bar_width/2)
                    ax1.set_xticklabels(subclasses,rotation=90,ha='right',fontdict={'fontsize':8,'fontweight':'bold'})
                    ax1.margins(y=0.2)
                    ax1.legend()
                    
                    plt.tight_layout()
                    pdf.savefig(fig)
                    times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Save the figure as an image
                    image_path = os.path.join(SUCCESS_RATE_LOCAL_PATH, f"{attribute}_{times_stamp}.png")
                    # image_path = OUTPUT_FOLDER + f"{attribute}.png"
                    fig.savefig(image_path)
                    image_paths.append(image_path)
                    plt.close(fig)
            SuccessRateService.image_to_pdf(image_paths, pdf_path, title="Responsible AI Office")
            return pdf_name
        finally:
            for image_path in image_paths:
                os.remove(image_path)
                
                
    def create_graphs_workbench(success_rates, label_col=None, favorable_outcome=None, categorical_attributes=None):
        formatted_categorical_attributes = str(categorical_attributes).replace('[', '').replace(']', '').replace("'", "")
        pdf_name = "population_success_rate_" + ".pdf"
        pdfname = "fairness_successrate.pdf"
        # pdf_path = os.path.join(SUCCESS_RATE_LOCAL_PATH, pdf_name)
        pdf_path = SUCCESS_RATE_LOCAL_PATH+pdf_name
        # Ensure the output directory exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        # html_path = os.path.join(OUTPUT_FOLDER, "fairness_report.html")
        html_path = OUTPUT_FOLDER+"fairness_report.html"
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = f"""
        <div style='display: flex; justify-content: center; align-items: left; color:white; background-color: #963596; font-size:23px; font-family: sans-serif; border-radius: 10px; position: relative;'>
            <h2 style='margin: 0; style=font-family: sans-serif;'>INFOSYS RESPONSIBLE AI OFFICE</h2>
            <span style='position:absolute; right:1; font-size:15px; align-self: center; padding: 0 10px;'>{timestamp}</span>
        </div>
        """

        html_content += f"""
        <body>
            <h3 style='color:#963596; text-align:left; font-size:19px; font-family: sans-serif;'>FAIRNESS REPORT</h3>
            <p style='font-family: sans-serif; font-size:16px;'>{SUCCESS_RATE_INFO}</p>
        </body>
        """

        html_content += f"""
        <div style='width: 50%; font-family: sans-serif;'>
            <h3 class="header" style="color:#963596; font-size:19px;"><strong>DATA INFORMATION</strong></h3>
            <table>
                <tr><td style="font-size:16px; font-family: sans-serif;">Model's Prediction Column</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{label_col}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Favorable Outcome</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{favorable_outcome}</td></tr>
                <tr><td style="font-size:16px; font-family: sans-serif;">Attributes For Analysis</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{formatted_categorical_attributes}</td></tr>
            </table>
        </div>
        """

        with PdfPages(pdf_path) as pdf:
            for attribute, each_group in success_rates.items():
                subclasses = list(each_group.keys())
                grouped_success_rates = [each_group[group]["group_success_rate"] for group in each_group]
                population_success_rates = [each_group[group]["population_success_rate"] for group in each_group]
                participations = [each_group[group]["population"] for group in each_group]
                n_groups = len(subclasses)
                bar_width = 0.35 if n_groups <= 20 else 0.2
                font_size = 10 if n_groups <= 20 else 8
                fig_height = 8 + n_groups * 0.1
                x = np.arange(len(subclasses))
                figure_width = max(len(subclasses) * 0.8, 10)

                fig, ax1 = plt.subplots(1, 1, figsize=(figure_width, fig_height), gridspec_kw={'height_ratios': [2]})
                bars_success_rate = ax1.bar(x, population_success_rates, bar_width, label='Success Rate', color='#1ca0f2')
                bars_population = ax1.bar(x + bar_width, participations, bar_width, label='Population', color='#05050F')

                # Preventing label overlap for population values
                for i, bar in enumerate(bars_population):
                    height = bar.get_height()
                    # Check if there's existing text near this position
                    existing_texts = [t for t in ax1.texts if abs(t.get_position()[0] - (bar.get_x() + bar.get_width() / 2)) < 0.1 and abs(t.get_position()[1] - height) < 5]
                    # If there is overlap, shift the text upwards
                    if existing_texts:
                        ax1.text(bar.get_x() + bar.get_width() / 2, height + 6, f'{participations[i]:.2f}%', ha='center', va='bottom', fontsize=10, color='black')
                    else:
                        ax1.text(bar.get_x() + bar.get_width() / 2, height + 2, f'{participations[i]:.2f}%', ha='center', va='bottom', fontsize=10, color='black')

                max_height = 0
                # Preventing label overlap for success rate values
                for i, bar in enumerate(bars_success_rate):
                    height = bar.get_height()
                    max_height = max(max_height, height)
                    # Check if there's existing text near this position
                    existing_texts = [t for t in ax1.texts if abs(t.get_position()[0] - (bar.get_x() + bar.get_width() / 2)) < 0.1 and abs(t.get_position()[1] - height) < 5]
                    # If there is overlap, shift the text upwards
                    if existing_texts:
                        ax1.text(bar.get_x() + bar.get_width() / 2, height + 6, f'{population_success_rates[i]:.2f}%', ha='center', va='bottom', fontsize=10, color='black')
                    else:
                        ax1.text(bar.get_x() + bar.get_width() / 2, height + 1, f'{population_success_rates[i]:.2f}%', ha='center', va='bottom', fontsize=10, color='black')

                # Preventing label overlap for grouped success rate values
                line_success_rate = ax1.plot(x + bar_width / 2, grouped_success_rates, marker='o', color='#963596', label='Grouped Success Rate')
                for i, rate in enumerate(grouped_success_rates):
                    # Check if there's existing text near this position
                    existing_texts = [t for t in ax1.texts if abs(t.get_position()[0] - (x[i] + bar_width / 2)) < 0.1 and abs(t.get_position()[1] - rate) < 5]
                    # If there is overlap, shift the text upwards
                    if existing_texts:
                        ax1.text(x[i] + bar_width / 2, rate + 7, f'{rate:.2f}%', ha='center', va='bottom', fontsize=10, color='#963596')
                    else:
                        ax1.text(x[i] + bar_width / 2, rate + 4, f'{rate:.2f}%', ha='center', va='bottom', fontsize=10, color='#963596')

                ax1.set_ylabel('Population (%)')
                ax1.set_title(f"Population and Success Rate for {attribute}", fontsize=14)
                ax1.set_xticks(x + bar_width / 2)
                ax1.set_xticklabels(subclasses, rotation=90, ha='right', fontdict={'fontsize': 8, 'fontweight': 'bold'})
                ax1.margins(y=0.2)
                ax1.legend()

                plt.tight_layout()
                pdf.savefig(fig)
                times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # Save the figure as an image
                image_path = os.path.join(OUTPUT_FOLDER, f"{attribute}_{times_stamp}.png")
                # image_path = OUTPUT_FOLDER + f"{attribute}.png"
                fig.savefig(image_path)
                plt.close(fig)

                # # Add the image to the HTML content
                # html_content += f'<h3>{attribute}</h3><img src="{image_path}" alt="{attribute}""><br>'
                # Convert image to base64
                with open(image_path, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

                # Add the base64 image to the HTML content
                html_content += f'<h3>{attribute}</h3><img src="data:image/png;base64,{image_base64}" alt="{attribute}"><br>'
        html_content += """
        </body>
        </html>
        """

        with open(html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        
        with open(html_path, "r", encoding="utf-8") as html_file:
            html_data = html_file.read()

        # pdfkit.from_string(html_data,"../output/"+pdfname)


        return html_data


    def analyze(payload):
        file=payload["file"]
        categorical_attributes=payload["categorical_attributes"]
        label_col=payload["label"]
        favorable_outcome=payload["favourable_outcome"]
        extension = SuccessRateService.get_extension(file.filename)  
        data =  SuccessRateService.get_dataframe(extension,file.file)
        success_rates = {}
        if not isinstance(data[label_col].dtype, str):
            data[label_col] = data[label_col].astype(str)
        SuccessRateService.check_categorical_attributes(categorical_attributes,data)
        favorable_data = data[data[label_col] == str(favorable_outcome)]
        total_records=len(data)
    
        for col in categorical_attributes:
            if col != label_col:  # Skip label column for rates
                class_counts = data[col].value_counts()
                favorable_subclass_counts = favorable_data[col].value_counts()
             
                success_rates[col] = {}
                for k, v in favorable_subclass_counts.items():
                    success_rates[col][k] = {
                        "population_success_rate": (v / total_records) * 100 if k in class_counts else 0,
                        "group_success_rate": (v / class_counts[k]) * 100 if k in class_counts else 0,
                        "population": (class_counts[k]/total_records)*100 if k in class_counts else 0
                    }
        
        #for mixed attributes
        for i in range(len(categorical_attributes)):
            for j in range(i+1,len(categorical_attributes)):
                grouped=data.groupby([categorical_attributes[i],categorical_attributes[j]]).agg(total=(label_col,'count'),success=(label_col,lambda x:(x==favorable_outcome).sum()))
                grouped[categorical_attributes[i]+"-"+categorical_attributes[j]]=(grouped['success']/grouped['total'])*100
                grouped["population_success_rate_"+categorical_attributes[i]+"-"+categorical_attributes[j]]=(grouped['success']/total_records)*100
                success_rates[categorical_attributes[i]+"-"+categorical_attributes[j]]={f"{row[categorical_attributes[i]]}-{row[categorical_attributes[j]]}":{"group_success_rate":row[categorical_attributes[i]+"-"+categorical_attributes[j]],"population_success_rate":row["population_success_rate_"+categorical_attributes[i]+"-"+categorical_attributes[j]],"population":(row['total']/total_records)*100} for _,row in grouped.reset_index().iterrows()}
                
        # Calculate the z-scores of success rates
        for attribute, each_group in success_rates.items():
            rates = [v['population_success_rate'] for v in each_group.values()]
            z_scores = stats.zscore(rates)
            for i, (k, v) in enumerate(each_group.items()):
                v["z_score"] = z_scores[i]
        
        #sort the success rated by the participation desc
        for attribute, each_group in success_rates.items():
            success_rates[attribute] = {k: v for k, v in sorted(each_group.items(), key=lambda item: item[1]["population"], reverse=True)}
  
        pdf_name=SuccessRateService.create_graphs(success_rates)
        success_rates["pdf_name"]=pdf_name
        return {"success_rates": success_rates}
    
    def workbench_analyze(self, payload: dict):
        try:
            if payload['Batch_id'] is None or '':
                log.error("Batch Id id missing")
            batchId = payload['Batch_id']
            self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
            tenet_id = self.tenet.find(tenet_name='Fairness')
            batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
            datasetId = batch_details['DataId']
            dataset_details = self.dataset.find(Dataset_Id=datasetId)
            dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=[
                                                        'label', 'favorableOutcome', 'protectedAttribute'])
            log.info("Dataset Attribute Ids:"+str(dataset_attribute_ids))
            dataset_attribute_values = self.dataAttributeValues.find(
                dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)

            log.info("Dataset Attribute Values:"+str(dataset_attribute_values))
            fileId = dataset_details["SampleData"]

            label_col = dataset_attribute_values[0]
            favorable_outcome = dataset_attribute_values[1]
            categorical_attributes = dataset_attribute_values[2]
            content=self.fileStore.read_file(fileId)
            if content is None:
                raise HTTPException(status_code=500, detail="No content received from the POST request")
            content=self.fileStore.read_file(fileId)
            if content is None:
                raise HTTPException(status_code=500, detail="No content received from the POST request")

            data = pandas.read_csv(BytesIO(content['data']))
            success_rates = {}
            if not isinstance(data[label_col].dtype, str):
                data[label_col] = data[label_col].astype(str)
            SuccessRateService.check_categorical_attributes(categorical_attributes,data)
            favorable_data = data[data[label_col] == str(favorable_outcome)]
            total_records=len(data)
        
            for col in categorical_attributes:
                if col != label_col:  # Skip label column for rates
                    class_counts = data[col].value_counts()
                    favorable_subclass_counts = favorable_data[col].value_counts()
                
                    success_rates[col] = {}
                    for k, v in favorable_subclass_counts.items():
                        success_rates[col][k] = {
                            "population_success_rate": (v / total_records) * 100 if k in class_counts else 0,
                            "group_success_rate": (v / class_counts[k]) * 100 if k in class_counts else 0,
                            "population": (class_counts[k]/total_records)*100 if k in class_counts else 0
                        }
            
            #for mixed attributes
            for i in range(len(categorical_attributes)):
                for j in range(i+1,len(categorical_attributes)):
                    grouped=data.groupby([categorical_attributes[i],categorical_attributes[j]]).agg(total=(label_col,'count'),success=(label_col,lambda x:(x==favorable_outcome).sum()))
                    grouped[categorical_attributes[i]+"-"+categorical_attributes[j]]=(grouped['success']/grouped['total'])*100
                    grouped["population_success_rate_"+categorical_attributes[i]+"-"+categorical_attributes[j]]=(grouped['success']/total_records)*100
                    success_rates[categorical_attributes[i]+"-"+categorical_attributes[j]]={f"{row[categorical_attributes[i]]}-{row[categorical_attributes[j]]}":{"group_success_rate":row[categorical_attributes[i]+"-"+categorical_attributes[j]],"population_success_rate":row["population_success_rate_"+categorical_attributes[i]+"-"+categorical_attributes[j]],"population":(row['total']/total_records)*100} for _,row in grouped.reset_index().iterrows()}
                    
            # Calculate the z-scores of success rates
            for attribute, each_group in success_rates.items():
                rates = [v['population_success_rate'] for v in each_group.values()]
                z_scores = stats.zscore(rates)
                for i, (k, v) in enumerate(each_group.items()):
                    v["z_score"] = z_scores[i]
            
            #sort the success rated by the participation desc
            for attribute, each_group in success_rates.items():
                success_rates[attribute] = {k: v for k, v in sorted(each_group.items(), key=lambda item: item[1]["population"], reverse=True)}
    
            html_data=SuccessRateService.create_graphs_workbench(success_rates,label_col,favorable_outcome,categorical_attributes)
            # with open(os.path.join(SUCCESS_RATE_LOCAL_PATH,pdf_name), "rb") as f:
            #     pdf_content = f.read()
            # pdf_fileId = self.fileStore.save_file(file=pdf_content, filename=pdf_name, contentType="application/pdf", tenet='Fairness', container_name=PDF_CONTAINER_NAME)
            # success_rates["pdf_name"]=pdf_fileId       
            # report_document={
            #     "ReportId":time.time(),
            #      "BatchId":batchId,
            #      "ReportFileId":pdf_name,
            #      "TenetId":tenet_id,
            #      "ReportName":pdf_name,
            #      "ContentType":"application/pdf",
            #      "CreatedDateTime":datetime.datetime.now()}
            # report_metadata=Report.create(report_document)   
            # if not report_metadata:
            #     raise HTTPException(status_code=500, detail="Report Metadata could not be inserted into DB")  
            tenet_id = self.tenet.find(tenet_name='Fairness')
            html_containerName = os.getenv('HTML_CONTAINER_NAME')
            htmlFileId = self.fileStore.save_file(file=BytesIO(html_data.encode(
                'utf-8')), filename='fairness_successrate.html', contentType='text/html', tenet='Fairness', container_name=html_containerName)
            log.info("HtmlFileId:"+ str(htmlFileId))
        
    
            HtmlId = time.time()
            doc = {
                'HtmlId': HtmlId,
                'BatchId': batchId,
                'TenetId': tenet_id,
                'ReportName': 'fairness_successrate.html',
                'HtmlFileId': htmlFileId,
                'CreatedDateTime': datetime.datetime.now(),
            }
            Html.create(doc)
    
            url = os.getenv("REPORT_URL")
            payload = {"batchId": batchId}
            response = requests.request(
            "POST", url, data=payload, verify=False).json()
            print(response)
            if response['status'] != "SUCCESS":
                raise HTTPException(status_code=500, detail="Report could not be generated")
            update_status=self.batch.update(batch_id=batchId, value={"Status": "Completed"})
            if not update_status:
                raise HTTPException(status_code=500, detail="Batch Status could not be updated in DB")
            # os.remove(os.path.join(SUCCESS_RATE_LOCAL_PATH,pdf_name))
            return {"success_rates": success_rates, "Html_Id": htmlFileId}
        except Exception as e:
            self.batch.update(batch_id=batchId, value={"Status": "Failed"})
            raise e
    def download_pdf(pdf_name):
        return os.path.join(SUCCESS_RATE_LOCAL_PATH,pdf_name)

   