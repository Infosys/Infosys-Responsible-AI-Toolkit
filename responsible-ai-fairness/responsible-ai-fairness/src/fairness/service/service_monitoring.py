"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
from io import BytesIO
from fastapi import HTTPException
import numpy as np
import pandas
import openai
import json
import time
import base64
# from tenacity import retry, wait_random_exponential, stop_after_attempt
import concurrent.futures
import backoff
import requests
from fairness.constants.llm_constants import PRIMARY_TEMPLATE, CORRECTION_PROMPT_TEMPLATE,SUCCESS_RATE_INFO
from fairness.dao.WorkBench.Tenet import Tenet
from fairness.dao.WorkBench.Batch import Batch
from fairness.dao.WorkBench.Data import Dataset,DataAttributes,DataAttributeValues
from fairness.dao.databaseconnection import DataBase
from fairness.dao.WorkBench.FileStoreDb import FileStoreReportDb
from fairness.dao.WorkBench.report import Report
from fairness.dao.WorkBench.html import Html
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from fpdf import FPDF
from PIL import Image
import zipfile
import io
import logging
import seaborn as sns
import uuid
import os
import datetime
import textwrap
from requests.exceptions import ChunkedEncodingError
import re
from fairness.dao.LlmConnection import create_llm_connection
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log=logging.getLogger(__name__)
log.setLevel(logging.INFO)

bias_types=[
    {'bias_type': 'race', 'groups': ["white", "black", "asian", "hispanic", "other"]},
    {'bias_type': 'gender', 'groups': ['male', 'female', "other"]},
    {'bias_type': 'age', 'groups': ['infants', 'toddlers', 'preschoolers', 'children', 'teenagers', 'young_adults', 'adults', 'middle_aged', 'seniors']},
    {'bias_type':'disability','groups':['physical_disabilities','sensory_disabilities','intellectual_disabilities','psychiatric_disabilities','learning_disabilities','chronic_health_conditions']},
]
LOCAL_PATH='../output/graphs/representation/'
OUTPUT_FOLDER = "../output/"
SUCCESS_RATE_LOCAL_PATH='../output/graphs/success_rates/'
ZIP_CONTAINER_NAME=os.getenv("ZIP_CONTAINER_NAME")
class FairnessAudit:
    def __init__(self):
        self.db = DataBase().db
        self.fileStore = FileStoreReportDb()
        self.batch =  Batch()
        self.tenet =  Tenet()
        self.dataset = Dataset()
        self.dataAttributes = DataAttributes()
        self.dataAttributeValues = DataAttributeValues()
        self.report = Report()
        
    def get_dataframe(extension,file):
        if extension == "csv":
               return  pandas.read_csv(file)
        elif extension=="parquet":
            return pandas.read_parquet(file)
        elif extension == "feather":
            return pandas.read_feather(file)
        elif extension == "json":
            return pandas.read_json(file)
    def get_extension(fileName: str):
        if fileName.endswith(".csv"):
            return "csv"
        elif fileName.endswith(".feather"):
            return "feather"
        elif fileName.endswith(".parquet"):
            return "parquet"
        elif fileName.endswith(".json"):
            return "json"   
        
    @backoff.on_exception(backoff.expo, exception=(openai.RateLimitError,json.decoder.JSONDecodeError), max_tries=10,backoff_log_level=logging.INFO)        
    def correct_respnse(self,response,errors,input_text):

        llm_connection = create_llm_connection()
        # Get the active LLM name and instance
        active_llm_name = llm_connection.get_active_llm()
        llm_instance = llm_connection.llm_instance 

        #Create error string numberd list
        try:
            # model_name=os.getenv("OPENAI_ENGINE_NAME")
            log.info("Correction Required, Correcting the response")
            errors=[f"{i+1}. {error}" for i,error in enumerate(errors)]
            errors_string='\n'.join(errors)
            correction_template=CORRECTION_PROMPT_TEMPLATE.format(bias_json_placeholder=json.dumps(bias_types),original_response=json.dumps(response),specific_errors=errors_string,input_text=input_text)
            # response=self.client.chat.completions.create(
            #     model=model_name,
            #     messages=[
            #         {"role": "user", "content": correction_template},
            #         ],
            #         temperature=0.7,
            #         max_tokens=800,
            #         top_p=0.95,
            #         frequency_penalty=0,
            #         presence_penalty=0,
            #         stop=None,
                    
            #     )
            generated_report = llm_instance.get_chat_completion(correction_template, input_text)
            if generated_report is not None:
                json_string=generated_report[generated_report.find('['): generated_report.rfind(']')+1]
                json_string=json_string.replace("\n","").replace("\t","").replace("\r","").strip()
                json_response=json.loads(json_string)
                return json_response
            else:
                log.info("Error: generated_report is None.")
        except json.decoder.JSONDecodeError as e:
            response=self.check_response([],input_text,errors=["JSONDecodeError: "+str(e)])
            return response['response']
        
            
    def check_response(self,response,input_text,errors=[]):
        log.info("Checking the response for any errors")
        log.info(response)
        required_fields={
            'bias_type':str,
            'bias_indicator':str,
            'privileged_groups':list,
            'unprivileged_groups':list,
            'bias_score':int,
            'explanation':str
        }
        #convert the response to lower case
        response=[{k.lower():v for k,v in response_dict.items()} for response_dict in response]
        if not errors:
            for field,expected_type in required_fields.items():
                for response_dict in response:
                    if response_dict['bias_type']!='NA':
                        if field not in response_dict:
                            errors.append(f"Response field {field} is missing")
                        elif not isinstance(response_dict[field],expected_type):
                            errors.append(f"Response field {field} is not of expected type {expected_type}")

            #check if the bias_type is NA
            for response_dict in response:
                if response_dict["bias_type"]=='NA':
                    errors.append("Bias Type is NA. Cross check the input text if really no bias is present or if there is any issue in the analysis")
                    break
            
            for response_dict in response:
                if "bias_type" in response_dict:
                    bias_types_list=[bias['bias_type'] for bias in bias_types]
                    if response_dict["bias_type"] not in bias_types_list:
                        if response_dict["bias_type"]!="NA":
                            errors.append(f"Invalid bias_type {response_dict['bias_type']}. Must be one of the following: {bias_types_list}")
                            break
                            
                elif response_dict["bias_type"]!='NA':  #If bias_type is NA, then privileged_groups and unprivileged_groups should be NA as well.  
                    if "privileged_groups" in response_dict:
                        if response_dict["bias_type"]!="NA":
                            if not all([group in bias['groups'] for group in response_dict['privileged_groups'] for bias in bias_types]):
                                errors.append(f"Invalid privileged_groups {response_dict['privileged_groups']}. Must be one of the following: {bias_types[response_dict['bias_type']]['groups']} for the bias_type {response_dict['bias_type']}")
                    if "unprivileged_groups" in response_dict:
                        if not all([group in bias['groups'] for group in response_dict['unprivileged_groups'] for bias in bias_types]):
                            errors.append(f"Invalid unprivileged_groups {response_dict['unprivileged_groups']}. Must be one of the following: {bias_types['groups']} for the bias_type {response_dict['bias_type']}")
                    
                    if "bias_indicator" in response_dict:
                        if response_dict['bias_indicator'] not in ['low', 'medium', 'high']:
                            errors.append(f"Invalid bias_indicator {response_dict['bias_indicator']}. Must be one of the following: low, medium, high")
           
        if errors:
            response=self.correct_respnse(response,errors,input_text)
        
        return {
            'valid': len(errors)==0,
            'errors': errors,
            'response': response,
        }
    # Function to extract JSON from response
    def extract_json(self,response_text):
        try:
            extraction_methods = [
                lambda x: json.loads(re.search(r'```json(.*?)```', x, re.DOTALL).group(1).strip()) if re.search(r'```json(.*?)```', x, re.DOTALL) else None,
                lambda x: json.loads(re.search(r'\[.*\]', x, re.DOTALL).group(0)) if re.search(r'\[.*\]', x, re.DOTALL) else None,
                lambda x: json.loads(re.findall(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', x)[-1]) if re.findall(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', x) else None
]
            for method in extraction_methods:
                try:
                    extracted_json = method(response_text)
                    if extracted_json:
                        return extracted_json
                except Exception as e:
                    continue
            return None
        except Exception as e:
            return None    
    backoff.on_exception(backoff.expo, exception=(openai.RateLimitError,json.decoder.JSONDecodeError,openai.BadRequestError), max_tries=15)
    def call_llm(self,prompt_template,text_message,flag=True):
        log.info("Analyzing the input text: "+str(text_message))
        llm_connection = create_llm_connection()
        # # Get the active LLM name and instance
        active_llm_name = llm_connection.get_active_llm()
        llm_instance = llm_connection.llm_instance  # Access the actual LLM instance
        try:
            # response = self.client.chat.completions.create(
            # model=model,
            #     # engine="gpt-4-turbo",
            # messages=[
            #     {"role": "system", "content": prompt_template},
            #     {"role": "user", "content": text_message}
            #     ],
            #     temperature=0.7,
            #     max_tokens=800,
            #     top_p=0.95,
            #     frequency_penalty=0,
            #     presence_penalty=0,
            #     stop=None,
                
            # )
            generated_report = llm_instance.get_chat_completion(prompt_template, text_message)
            if generated_report is not None:
                json_response=self.extract_json(generated_report)
                return json_response
                # errors=self.check_response(json_response,text_message)
                # if errors['valid']:
                #     return json_response
                # else:
                #     return errors['response']
            else:
                log.info("Error: generated_report is None.")
        except json.decoder.JSONDecodeError as e:
            log.error("JSONDecodeError: "+str(e))
            log.error(str(e.doc))
            response=self.call_llm(prompt_template,text_message)
            return response
        except openai.BadRequestError as e:
            # Handle the error
            log.info(f"Error: {e}")
            response_with_error = [{
            'bias_type': 'Blocked By Azure',
            'bias_indicator': 'high',
            'privileged_groups': [],
            'unprivileged_groups': [],
            'bias_score': 100,
            'explanation': 'This request was blocked by Azure. Immediate manual intervention required.'
        }]
        
            # Log the error for future reference
            log.error(f"BadRequestError encountered. Bias type set to 'Blocked By Azure' with a bias score of 100%.")
            
            return response_with_error
        except openai.RateLimitError as e:
            log.info(f"Rate limit exceeded: {e}")
        
    def image_to_pdf(image_paths, output_pdf, label=None):
        pdf = FPDF()
        pdf.add_page()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add title if provided
        PURPLE = (150, 53, 150)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        
        # Header section
        pdf.set_font('Helvetica', 'B', 17)
        pdf.set_text_color(*WHITE)
        pdf.set_fill_color(*PURPLE)
        
        # Full-width header
        pdf.cell(0, 11, 'INFOSYS RESPONSIBLE AI OFFICE', 
                align='C', fill=True, border=0)            
                    
        #remove the gap between the header and the content
        pdf.set_y(20)
        # Add image
            # Process each image
        for index,image_path in enumerate(image_paths):
            # Add a new page
            if index!=0:
                pdf.set_y(10)
                pdf.add_page()
            
            # Open image to get dimensions
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate scaling to fit page width
            page_width = pdf.w-20
            page_height = pdf.h- pdf.get_y() - 20
            
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
        log.info(f"PDF created: {output_pdf}")
        
    def bias_type_bar_chart_visualize(df):
        try:
            times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"bias_analysis_{times_stamp}.pdf"
            df['privileged_groups'] = df['privileged_groups'].apply(lambda x: x.replace('[', '').replace(']', '').replace("'", '').split(', ') if isinstance(x, str) else x)
            df['unprivileged_groups'] = df['unprivileged_groups'].apply(lambda x: x.replace('[', '').replace(']', '').replace("'", '').split(', ') if isinstance(x, str) else x)

            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            # Save graphs as images and embed them in the HTML content
            graph_paths = []

            bias_type_counts = df['bias_type'].value_counts()
            
            # Create 2x2 grid for the first set of graphs with smaller figure size
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))  # Reduced size (12x8 inches)
            axes = axes.flatten()  # Flatten to make it easier to iterate

            # Plot the bias type frequency
            bias_type_counts.plot(kind='bar', color='skyblue', ax=axes[0])
            axes[0].set_xlabel('Bias Type')
            axes[0].set_ylabel('Frequency')
            axes[0].set_title('Frequency of Bias Types in Responses')

            # Plot privileged groups frequencies for each bias type
            for i, bias_type in enumerate(df['bias_type'].unique()):
                privileged_flat = pd.Series([item for item in df[df['bias_type'] == bias_type]['privileged_groups'].dropna()])
                privileged_flat = pd.Series([item for sublist in privileged_flat for item in sublist])
                if not privileged_flat.empty:
                    privileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=axes[1])
                    axes[1].set_title(f'Frequency of Privileged Groups for {bias_type}')
                    axes[1].set_xlabel('Group')
                    axes[1].set_ylabel('Frequency')

            # Plot unprivileged groups frequencies for each bias type
            for i, bias_type in enumerate(df['bias_type'].unique()):
                unprivileged_flat = pd.Series([item for item in df[df['bias_type'] == bias_type]['unprivileged_groups'].dropna()])
                unprivileged_flat = pd.Series([item for sublist in unprivileged_flat for item in sublist])
                if not unprivileged_flat.empty:
                    unprivileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=axes[2])
                    axes[2].set_title(f'Frequency of Unprivileged Groups for {bias_type}')
                    axes[2].set_xlabel('Group')
                    axes[2].set_ylabel('Frequency')

            # Bias Score Distribution
            df['bias_score'] = pd.to_numeric(df['bias_score'], errors='coerce')  # Converts non-numeric to NaN
            df = df.dropna(subset=['bias_score'])  # Drop rows with NaN in bias_score
            sns.histplot(df['bias_score'], color='skyblue', kde=True, ax=axes[3])
            axes[3].set_title('Distribution of Bias Scores in Responses')
            axes[3].set_xlabel('Bias Score')
            axes[3].set_ylabel('Frequency')

            # Save the figure with all 4 plots
            plt.tight_layout()
            times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            graph_path = os.path.join(OUTPUT_FOLDER, f"bias_analysis_4_plots_{times_stamp}.png")
            plt.savefig(graph_path)
            plt.close()
            graph_paths.append(graph_path)
            # Privileged vs Unprivileged Groups Comparison (Bar Plot)
            privileged_flat = pd.Series([item for sublist in df['privileged_groups'].dropna() for item in sublist])
            unprivileged_flat = pd.Series([item for sublist in df['unprivileged_groups'].dropna() for item in sublist])

            # Plot privileged groups
            fig, ax = plt.subplots(figsize=(6, 4))  # Smaller figure size (6x4 inches)
            privileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=ax, alpha=0.7)
            ax.set_title('Frequency of Privileged Groups in Responses')
            ax.set_xlabel('Group')
            ax.set_ylabel('Frequency')
            plt.tight_layout()
            graph_path = os.path.join(OUTPUT_FOLDER, f'Frequency_of_Privileged_Groups_{times_stamp}.png')
            plt.savefig(graph_path)
            plt.close()
            graph_paths.append(graph_path)
            # Plot unprivileged groups
            fig, ax = plt.subplots(figsize=(6, 4))  # Smaller figure size (6x4 inches)
            unprivileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=ax, alpha=0.7)
            ax.set_title('Frequency of Unprivileged Groups in Responses')
            ax.set_xlabel('Group')
            ax.set_ylabel('Frequency')
            plt.tight_layout()
            graph_path = os.path.join(OUTPUT_FOLDER, f'Frequency_of_Unprivileged_Groups_{times_stamp}.png')
            plt.savefig(graph_path)
            plt.close()

            # Plot average bias score by bias level with threshhold and bias density
            threshold = int(os.getenv('THRESHOLD'))
            df["bias_score"] = pd.to_numeric(df["bias_score"], errors='coerce') # Converts non-numeric to NaN
            bias_density = df["bias_score"].sum()/(len(df["bias_score"])) # concentration of bias across the dataset
            # Group and sort data
            mean_scores = df.groupby("bias_indicator")["bias_score"].mean().sort_values(ascending=False)
            counts = df["bias_indicator"].value_counts()
            # Convert to DataFrame
            mean_scores = mean_scores.to_frame().reset_index()
            # Define colors manually
            color_map = {"high": "coral", "medium": "grey", "low": "skyblue"}
            bar_colors = [color_map[b] for b in mean_scores["bias_indicator"]]
            # Plot bar chart
            fig,ax=plt.subplots(figsize=(8, 6))
            sns.barplot(x=mean_scores["bias_indicator"], y=mean_scores["bias_score"], palette=bar_colors)
            # Add threshold and bias_density lines
            plt.axhline(threshold, color="red", linestyle="dashed", label=f"Threshold: {threshold}%")
            plt.axhline(bias_density, color="blue", linestyle="dashed", label=f"Bias Density: {round(bias_density)}%")
            for i, (count, y_value) in enumerate(zip(counts[mean_scores["bias_indicator"]], mean_scores["bias_score"])):
                ax.text(i, y_value + 2, f'({str(count)})', ha='center', va='bottom', fontsize=12, color=bar_colors[i], fontweight='bold')
            # Add legend for counts
            for label,color in color_map.items():
                ax.bar(0, 0, color=color, label=f'{label} Count: {counts.get(label, 0)}')
            # Format axes
            ax.set_title("Average Bias Score by Bias Level")
            ax.set_xlabel("Bias Indicator (high, medium, low)")
            ax.set_ylabel("Average Bias Score (%)")
            ax.set_ylim(0, 110)
            ax.set_yticks(range(0, 110, 10)) # Set Y-axis scale to 0, 10, 20, ..., 100
            plt.legend()
            plt.tight_layout()
            times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            graph_path = os.path.join(OUTPUT_FOLDER, f"bias_analysis_with_threshold_{times_stamp}.png")
            plt.savefig(graph_path)
            graph_paths.append(graph_path)
            # Read the image file and encode it in base64
            FairnessAudit.image_to_pdf(graph_paths, os.path.join(LOCAL_PATH, pdf_filename))
            return pdf_filename
        finally:
            for graph_path in graph_paths:
                os.remove(graph_path)
            log.info("Images removed from the local path")

    def bias_type_bar_chart_visualize_workbench(df, label):
        pdf_filename = 'audit_report_pdf.pdf'
        df['privileged_groups'] = df['privileged_groups'].apply(lambda x: x.replace('[', '').replace(']', '').replace("'", '').split(', ') if isinstance(x, str) else x)
        df['unprivileged_groups'] = df['unprivileged_groups'].apply(lambda x: x.replace('[', '').replace(']', '').replace("'", '').split(', ') if isinstance(x, str) else x)
        
        pdf = PdfPages(os.path.join(LOCAL_PATH, pdf_filename))

        # Generate HTML content
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
                    <tr><td style="font-size:16px; font-family: sans-serif;">Model Output column</td><td>:</td><td style="color: darkgray; font-size:16px; font-family: sans-serif;">{label}</td></tr>
                </table>
            </div>
        """
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Save graphs as images and embed them in the HTML content
        graph_paths = []

        bias_type_counts = df['bias_type'].value_counts()
        
        # Create 2x2 grid for the first set of graphs with smaller figure size
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))  # Reduced size (12x8 inches)
        axes = axes.flatten()  # Flatten to make it easier to iterate

        # Plot the bias type frequency
        bias_type_counts.plot(kind='bar', color='skyblue', ax=axes[0])
        axes[0].set_xlabel('Bias Type')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Frequency of Bias Types in Responses')

        # Plot privileged groups frequencies for each bias type
        for i, bias_type in enumerate(df['bias_type'].unique()):
            privileged_flat = pd.Series([item for item in df[df['bias_type'] == bias_type]['privileged_groups'].dropna()])
            privileged_flat = pd.Series([item for sublist in privileged_flat for item in sublist])
            if not privileged_flat.empty:
                privileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=axes[1])
                axes[1].set_title(f'Frequency of Privileged Groups for {bias_type}')
                axes[1].set_xlabel('Group')
                axes[1].set_ylabel('Frequency')

        # Plot unprivileged groups frequencies for each bias type
        for i, bias_type in enumerate(df['bias_type'].unique()):
            unprivileged_flat = pd.Series([item for item in df[df['bias_type'] == bias_type]['unprivileged_groups'].dropna()])
            unprivileged_flat = pd.Series([item for sublist in unprivileged_flat for item in sublist])
            if not unprivileged_flat.empty:
                unprivileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=axes[2])
                axes[2].set_title(f'Frequency of Unprivileged Groups for {bias_type}')
                axes[2].set_xlabel('Group')
                axes[2].set_ylabel('Frequency')

        # Bias Score Distribution
        df['bias_score'] = pd.to_numeric(df['bias_score'], errors='coerce')  # Converts non-numeric to NaN
        df = df.dropna(subset=['bias_score'])  # Drop rows with NaN in bias_score
        sns.histplot(df['bias_score'], color='skyblue', kde=True, ax=axes[3])
        axes[3].set_title('Distribution of Bias Scores in Responses')
        axes[3].set_xlabel('Bias Score')
        axes[3].set_ylabel('Frequency')

        # Save the figure with all 4 plots
        plt.tight_layout()
        times_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        graph_path = os.path.join(OUTPUT_FOLDER, f"bias_analysis_4_plots_{times_stamp}.png")
        plt.savefig(graph_path)
        plt.close()
        graph_paths.append(graph_path)
        # Read the image file and encode it in base64
        with open(graph_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        html_content += f'<img src="data:image/png;base64,{image_base64}" alt="Bias Analysis 4 Plots">'

        # Privileged vs Unprivileged Groups Comparison (Bar Plot)
        privileged_flat = pd.Series([item for sublist in df['privileged_groups'].dropna() for item in sublist])
        unprivileged_flat = pd.Series([item for sublist in df['unprivileged_groups'].dropna() for item in sublist])

        # Plot privileged groups
        fig, ax = plt.subplots(figsize=(6, 4))  # Smaller figure size (6x4 inches)
        privileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=ax, alpha=0.7)
        ax.set_title('Frequency of Privileged Groups in Responses')
        ax.set_xlabel('Group')
        ax.set_ylabel('Frequency')
        pdf.savefig(fig)
        plt.tight_layout()
        graph_path = os.path.join(OUTPUT_FOLDER, f'Frequency_of_Privileged_Groups_{times_stamp}.png')
        plt.savefig(graph_path)
        plt.close()
        graph_paths.append(graph_path)
        # Read the image file and encode it in base64
        with open(graph_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        html_content += f'<img src="data:image/png;base64,{image_base64}" alt="Frequency of Privileged Groups">'

        # Plot unprivileged groups
        fig, ax = plt.subplots(figsize=(6, 4))  # Smaller figure size (6x4 inches)
        unprivileged_flat.value_counts().plot(kind='bar', color='skyblue', ax=ax, alpha=0.7)
        ax.set_title('Frequency of Unprivileged Groups in Responses')
        ax.set_xlabel('Group')
        ax.set_ylabel('Frequency')
        pdf.savefig(fig)
        plt.tight_layout()
        graph_path = os.path.join(OUTPUT_FOLDER, f'Frequency_of_Unprivileged_Groups_{times_stamp}.png')
        plt.savefig(graph_path)
        plt.close()
        graph_paths.append(graph_path)
        # Read the image file and encode it in base64
        with open(graph_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        html_content += f'<img src="data:image/png;base64,{image_base64}" alt="Frequency of Unprivileged Groups">'
        
        # Plot average bias score by bias level with threshhold and bias density
        threshold = int(os.getenv('THRESHOLD'))
        df.loc[:, "bias_score"] = pd.to_numeric(df["bias_score"], errors='coerce') # Converts non-numeric to NaN

        # FIX: Normalize bias_indicator to lowercase before any processing
        df.loc[:, "bias_indicator"] = df["bias_indicator"].str.lower()

        bias_density = df["bias_score"].sum()/(len(df["bias_score"])) # concentration of bias across the dataset
        # Group and sort data
        mean_scores = df.groupby("bias_indicator")["bias_score"].mean().sort_values(ascending=False)
        counts = df["bias_indicator"].value_counts()
        # Convert to DataFrame
        mean_scores = mean_scores.to_frame().reset_index()
        # Define colors manually
        color_map = {"high": "coral", "medium": "grey", "low": "skyblue"}
        bar_colors = [color_map[b] for b in mean_scores["bias_indicator"]]
        # Plot bar chart
        fig,ax=plt.subplots(figsize=(8, 6))
        sns.barplot(x=mean_scores["bias_indicator"], y=mean_scores["bias_score"], palette=bar_colors)
        # Add threshold and bias_density lines
        plt.axhline(threshold, color="red", linestyle="dashed", label=f"Threshold: {threshold}%")
        plt.axhline(bias_density, color="blue", linestyle="dashed", label=f"Bias Density: {round(bias_density)}%")
        for i, (count, y_value) in enumerate(zip(counts[mean_scores["bias_indicator"]], mean_scores["bias_score"])):
            ax.text(i, y_value + 2, f'({str(count)})', ha='center', va='bottom', fontsize=12, color=bar_colors[i], fontweight='bold')
        # Add legend for counts
        for label,color in color_map.items():
            ax.bar(0, 0, color=color, label=f'{label} Count: {counts.get(label, 0)}')
        # Format axes
        ax.set_title("Average Bias Score by Bias Level")
        ax.set_xlabel("Bias Indicator (high, medium, low)")
        ax.set_ylabel("Average Bias Score (%)")
        ax.set_ylim(0, 110)
        ax.set_yticks(range(0, 110, 10)) # Set Y-axis scale to 0, 10, 20, ..., 100
        plt.legend()
        # Save the plot
        pdf.savefig(fig)
        plt.tight_layout()
        # Save the graph to a file
        graph_path = os.path.join(OUTPUT_FOLDER, f'Average_Bias_Score_by_Bias_Level_{times_stamp}.png')
        plt.savefig(graph_path)
        plt.close()
        # Add the graph path to a list for later reference
        graph_paths.append(graph_path)
        # Read the image file and encode it in base64
        with open(graph_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        # Add the image to HTML content
        html_content += f'<img src="data:image/png;base64,{image_base64}" alt="Average Bias Score by Bias Level">'
        pdf.close()

        # Define the HTML file path
        html_file_path = os.path.join(OUTPUT_FOLDER, 'report.html')

        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        
        with open(html_file_path, "r", encoding="utf-8") as html_file:
            html_data = html_file.read()

        # pdfkit.from_string(html_data,"../output/"+pdf_filename)

        return html_data



        
    def audit(self,payload):
        start_time=time.time()
        label=payload['label']
        file=payload['file']
        extension = FairnessAudit.get_extension(file.filename)  
        data =  FairnessAudit.get_dataframe(extension,file.file)
        inputs=data[label].tolist()
        #preprocess the inputs
        inputs=[input_text.replace('\n','').replace('\t','').replace('\r','').strip() for input_text in inputs]
        primary_template=PRIMARY_TEMPLATE
        primary_template=primary_template.replace('\n','').replace('\t','').replace('\r','').strip()
        prompt=primary_template.format(bias_json_placeholder=json.dumps(bias_types),input_text="{input_text}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results=list(executor.map(self.call_llm,[prompt]*len(inputs),inputs))
        data['response']=results
        data['bias_type']=data['response'].apply(lambda x: x[0]['bias_type'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
        data['bias_score']=data['response'].apply(lambda x: x[0]['bias_score'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
        data['privileged_groups']=data['response'].apply(lambda x: x[0]['privileged_groups'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))  
        data['unprivileged_groups']=data['response'].apply(lambda x: x[0]['unprivileged_groups'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
        data['bias_indicator']=data['response'].apply(lambda x: x[0]['bias_indicator'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
        
        data=data.replace('NA', pd.NA)
        csv_name='bias_audit_report_'+str(uuid.uuid4())+'.csv'
        data.to_csv(os.path.join(LOCAL_PATH,csv_name))
        pdf_filename=FairnessAudit.bias_type_bar_chart_visualize(data)
        response={'audit_report_csv':csv_name,'audit_report_pdf':pdf_filename}  
        end_time=time.time()
        total_time=end_time-start_time
        log.info("Time taken for the audit: "+str(total_time))
        return {'response':response,'time_taken':total_time}
    
    def workbench_audit(self,payload:dict):
        try: 
            start_time=time.time()
            if payload['Batch_id'] is None or '':
                log.error("Batch Id id missing")
            batchId = payload['Batch_id']
            self.batch.update(batch_id=batchId, value={"Status": "In-progress"})
            tenet_id = self.tenet.find(tenet_name='Fairness')
            batch_details = self.batch.find(batch_id=batchId, tenet_id=tenet_id)
            datasetId = batch_details['DataId']
            dataset_details = self.dataset.find(Dataset_Id=datasetId)
            dataset_attribute_ids = self.dataAttributes.find(dataset_attributes=[
                                                        'label'])
            log.info("Dataset Attribute Ids:"+str(dataset_attribute_ids))
            dataset_attribute_values = self.dataAttributeValues.find(
                dataset_id=datasetId, dataset_attribute_ids=dataset_attribute_ids, batch_id=batchId)

            log.info("Dataset Attribute Values:"+ str(dataset_attribute_values))
            fileId = dataset_details["SampleData"]

            label = dataset_attribute_values[0]
            content=self.fileStore.read_file(fileId)
            if content is None:
                raise HTTPException(status_code=500, detail="No content received from the POST request")
            content=self.fileStore.read_file(fileId)
            if content is None:
                raise HTTPException(status_code=500, detail="No content received from the POST request")

            data = pandas.read_csv(BytesIO(content['data']))
            inputs=data[label].tolist()
            inputs=[input_text.replace('\n','').replace('\t','').replace('\r','').strip() for input_text in inputs]
            primary_template=PRIMARY_TEMPLATE
            primary_template=primary_template.replace('\n','').replace('\t','').replace('\r','').strip()
            prompt=primary_template.format(bias_json_placeholder=json.dumps(bias_types),input_text="{input_text}")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results=list(executor.map(self.call_llm,[prompt]*len(inputs),inputs))
            data['response']=results
            data['bias_type']=data['response'].apply(lambda x: x[0]['bias_type'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
            data['bias_score']=data['response'].apply(lambda x: x[0]['bias_score'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
            data['privileged_groups']=data['response'].apply(lambda x: x[0]['privileged_groups'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))  
            data['unprivileged_groups']=data['response'].apply(lambda x: x[0]['unprivileged_groups'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
            data['bias_indicator']=data['response'].apply(lambda x: x[0]['bias_indicator'] if isinstance(x, list) and len(x) > 0 else (x if isinstance(x, str) else 'NA'))
            data=data.replace('NA', pd.NA)
            csv_name='bias_audit_report_'+str(uuid.uuid4())+'.csv'
            data.to_csv(os.path.join(LOCAL_PATH,csv_name))
            html_data=FairnessAudit.bias_type_bar_chart_visualize_workbench(data,label)
            
            tenet_id = self.tenet.find(tenet_name='Fairness')
            html_containerName = os.getenv('HTML_CONTAINER_NAME')
            htmlFileId = self.fileStore.save_file(file=BytesIO(html_data.encode(
                'utf-8')), filename='fairness_successrate.html', contentType='text/html', tenet='Fairness', container_name=html_containerName)
            log.info("HtmlFileId:"+ htmlFileId)
        
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
            
            report_id = self.report.find(batch_id=batchId)
            log.info(report_id)
            reportId = report_id['ReportFileId']
            reportName=report_id['ReportName']
            try:
                content = self.fileStore.read_file(reportId,os.getenv("PDF_CONTAINER_NAME"))
            except:
                content= self.fileStore.read_chunked_file(reportId,os.getenv("PDF_CONTAINER_NAME"))
            pdf_name=content['name']+"."+content['extension']
            #load csv and pdf and convert to bytes
            with open(os.path.join(LOCAL_PATH,csv_name), 'rb') as f:
                csv_file = f.read()
            # with open(os.path.join(OUTPUT_FOLDER,pdf_filename), 'rb') as f:
            #     pdf_file = f.read()
            zip_buffer=io.BytesIO()
            with zipfile.ZipFile(zip_buffer,'w') as zipf:
                zipf.writestr(csv_name,csv_file)
                zipf.writestr(reportName,content['data'])
            
            zip_buffer.seek(0)
            zip_file_bytes=zip_buffer.getvalue()
            zip_file_name="audit_report.zip"
            zip_fileid=self.fileStore.save_file(file=zip_file_bytes, filename=zip_file_name, contentType="zip", tenet='Fairness', container_name=ZIP_CONTAINER_NAME)
            response={'audit_report_id':zip_fileid}  
            os.remove(os.path.join(LOCAL_PATH,csv_name))
            # os.remove(os.path.join(OUTPUT_FOLDER,pdf_filename))
            report_document={"ReportId":time.time(),"BatchId":batchId,"ReportFileId":zip_fileid,"TenetId":tenet_id,"ReportName":zip_file_name,"ContentType":"zip","CreatedDateTime":datetime.datetime.now()}
            generated=Report.create(report_document)
            if not generated:
                raise HTTPException(status_code=500, detail="Report Metadata could not be inserted into DB")
            updated=self.batch.update(batch_id=batchId, value={"Status": "Completed"})
            if not updated:
                raise HTTPException(status_code=500, detail="Batch Status could not be updated in DB")
            end_time=time.time()
            total_time=end_time-start_time
            log.info("Time taken for the audit: "+str(total_time))
            return {'response':response,'time_taken':total_time}
        except Exception as e:
            self.batch.update(batch_id=batchId, value={"Status": "Failed"})
            raise e
    
    def download_file(filename):
        if os.path.exists(os.path.join(LOCAL_PATH,filename)):
            return os.path.join(LOCAL_PATH,filename)
        else:
            raise HTTPException(status_code=404, detail="File not found")
        
        
        