'''
MIT license https://opensource.org/licenses/MIT Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import os
import shutil
import zipfile
import shutil
import time
from datetime import datetime
import requests
import io
from app.config.logger import CustomLogger

from app.service.utility import Utility as UT
from fastapi.responses import StreamingResponse
import pdfkit

from app.dao.Batch import Batch
from app.dao.Html import Html
from app.dao.Report import Report
from app.dao.SaveFileDB import FileStoreDb
import re

log = CustomLogger()

fetch_file = os.getenv("AZURE_GET_API")
upload_file = os.getenv("AZURE_UPLOAD_API")
dataset_container = os.getenv("DATA_CONTAINER_NAME")
model_container = os.getenv("MODEL_CONTAINER_NAME")
zip_container = os.getenv("ZIP_CONTAINER_NAME")




def path_check(safe_path):
    # Ensure the path is valid and does not contain any illegal characters
    if re.match(r'^[\w\-:\\\/\s.]+$', str(safe_path)):
        return safe_path
    else:
        raise ValueError(f"Invalid path: {safe_path}")

def is_safe_path(basedir, path, follow_symlinks=True):
    # Normalize the path
    normalized_path = os.path.normpath(path)
    
    # Resolve symbolic links
    if follow_symlinks:
        real_path = os.path.realpath(normalized_path)
    else:
        real_path = os.path.abspath(normalized_path)
    
    # Check if the resolved path starts with the base directory
    return os.path.commonpath([real_path, basedir]) == basedir

def sanitize_filename(filename):
    # Allow only specific characters: alphanumeric, underscores, hyphens, and dots
    allowed_chars = re.compile(r'^[a-zA-Z0-9_.-]+$')
    if allowed_chars.match(filename):
        return filename
    else:
        raise ValueError(f"Invalid filename: {filename}")

class InfosysRAI:

    db_type = os.getenv('DB_TYPE').lower()

    def download_report(payload: dict):
        # Check if payload is not None and it contains 'batchId'
        if payload['batchId'] is None:
            log.error("batchId is missing")
            return {'status':'FAILURE', 'message':'BatchId is missing', 'BatchId':None}
        try:
            batch_id = payload['batchId']
            tenet_id = Batch.find_tenet_id(batch_id=batch_id)
            
            report_file_details = Report.find_one(batch_id=batch_id, tenet_id=tenet_id)

            if InfosysRAI.db_type == 'mongo':
                container_name =  None
            elif tenet_id == 3.3:
                container_name = zip_container
            else:
                container_name = os.getenv('PDF_CONTAINER_NAME')

            file = FileStoreDb.read_file(unique_id = report_file_details['ReportFileId'], container_name = container_name)
            
            response = StreamingResponse(io.BytesIO(file['data']), media_type=report_file_details['ContentType'])
            response.headers["Content-Disposition"] = 'attachment; filename='+report_file_details['ReportName']
            
            return response

        except Exception as e:
            log.error(e, exc_info=True)
            return {'status': 'FAILURE', 'message': f'Error while downloading the report, due to {str(e)}', 'BatchId': payload['batchId']}

    def combinedReport(payload):
        
        try:          
            root_path = os.getcwd()
            root_path = root_path[:-4] + "/database"
            dirList = ["data","model","payload","report"]
            for dir in dirList:
                dirs = root_path + "/" + dir
                if not os.path.exists(dirs):
                    os.mkdir(dirs)

            batch_id = payload['batchid']
            tenet_id = Batch.find_tenet_id(batch_id=batch_id)
            zip_file_details = Html.find(batch_id=batch_id, tenet_id=tenet_id)
            
            # access data content from SaveFileDB
            if(os.getenv("DB_TYPE") == "mongo"):
                dataContent = FileStoreDb.findOne(zip_file_details['HtmlFileId'])
                reportName = dataContent["fileName"]
                data = dataContent["data"]
            else:
                response = requests.get(url = fetch_file, params ={"container_name":zip_container,"blob_name":zip_file_details['HtmlFileId']})
                binary_data = response.content
                temp = io.BytesIO(binary_data)
                data = temp.read()

                content_disposition = response.headers.get('content-disposition')
                reportName =  content_disposition.split(';')[1].split('=')[1]
            
            data_path = root_path + "/data"
            report_path = root_path + "/report"

            # Sanitize and validate reportName
            reportName = sanitize_filename(reportName)  
            report_path = os.path.join(report_path,reportName) 

            # Validate the path using path_check
            report_path = path_check(report_path)


            # if not is_safe_path(root_path + "/report", report_path): 
            #      raise ValueError("Unsafe file path detected") 
            if os.path.exists(report_path):                          
                os.remove(report_path)                                       
            with open(report_path, 'wb') as f:
                f.write(data)
            
            # converting html file into pdf
            UT.htmlToPdfWithWatermark({'report_path':report_path, 'data_path':data_path})
            
            # modified zip file after removing html file
            temp_zip_path = report_path.replace('.zip','_temp.zip') 
            with zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
                with zipfile.ZipFile(report_path, 'r') as original_zip:
                    for file_info in original_zip.infolist():
                        if not file_info.filename.endswith('.html'):
                            data = original_zip.read(file_info.filename)
                            temp_zip.writestr(file_info, data)
                        # if file_info.filename.endswith('.pdf'):
                        #     data = original_zip.read(file_info.filename)
                        #     responses = requests.post(url = upload_file, files ={"file":(reportName, file)}, data ={"container_name":zip_container}).json()
                        #     print("file_info", file_info)
                os.remove(report_path)
            os.rename(temp_zip_path, report_path)

            if(os.getenv("DB_TYPE") == "mongo"):
                reportid = time.time()
                file = open(report_path,'rb')
                with FileStoreDb.fs.new_file(_id=reportid, filename=reportName, contentType="zip") as f:
                    shutil.copyfileobj(file,f)
                    reportid=f._id
                    time.sleep(1)
                file.close()
            else:
                file = open(report_path,'rb')
                responses = requests.post(url = upload_file, files ={"file":(reportName, file)}, data ={"container_name":zip_container}).json()
                reportid = responses["blob_name"]
                file.close()

            # Save data to DB
            report_id = time.time()
            data = {
                "ReportId": report_id, 
                "BatchId": batch_id,
                "TenetId": tenet_id,
                "ReportName": reportName,
                "ReportFileId": reportid,
                "ContentType": "application/zip",
                "CreatedDateTime": datetime.now()
            }
            Report.create(data)
            os.remove(report_path)

            log.info(str(f'report_id: {report_id}'))
            return {'status': 'SUCCESS', 'message': 'HTML to PDF conversion successful', 'ReportId': report_id} 
        except Exception as exc:
            log.exception(str(exc))
            return {'status': 'FAILURE', 'message': f'Error while converting html to pdf, due to {str(exc)}', 'BatchId': batch_id}



    def html_to_pdf_conversion(payload):
        # Check if payload is None
        if payload['batchId'] is None:
            log.error("batchId is missing")
            return {'status':'FAILURE', 'message': 'batchId is missing', 'BatchId':None}
        try:
            batch_id = payload['batchId']
            tenet_id = Batch.find_tenet_id(batch_id=batch_id)
            html_file_id, report_name = Html.find_one(batch_id=batch_id, tenet_id=tenet_id)

            if InfosysRAI.db_type == 'mongo':
                container_name = None
            else:
                container_name = os.getenv('HTML_CONTAINER_NAME')

            file = FileStoreDb.read_file(unique_id = html_file_id, container_name = container_name)

            if tenet_id == 1.1 and report_name.endswith('.zip'):
                # Create a BytesIO object from the file data
                zip_data = io.BytesIO(file['data'])

                # Open the zip file
                with zipfile.ZipFile(zip_data, 'a') as zipf:
                    # Extract all files
                    zipf.extractall(path='temp')

                with open('temp/output/explanationreport.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()

                has_global_explanation = 'global-explanation' in html_content
                has_local_explanation = 'local-explanation' in html_content
              
                # Add CSS to prevent page breaks inside tables and graphs
                css = """
                <style>
                    * {
                        page-break-inside: avoid;
                    }
                    td {
                        padding-right: 20px;
                    }
                    td, p {
                        font-size: 20px; /* Adjust font size as needed */
                    }
                    h3 {
                        font-size: 25px; /* Adjust font size as needed */
                    }
                    h2 {    
                        font-size: 35px; /* Adjust font size as needed */
                    }
                </style>
                """
                # Add additional CSS if both global and local explanations exist
                if has_global_explanation and has_local_explanation:
                    css += """
                    <style>
                        .local-explanation {
                            page-break-before: always;
                        }
                    </style>
                    """

                # Insert the CSS into the HTML content
                html_content = css + html_content
            else:
                html_content = file['data'].decode('utf-8')

            # Convert the HTML file to PDF
            option = {
                        'page-size':'A4',
                        'orientation':'Portrait',
                        'margin-top':'0.50in',
                        'margin-right':'0.50in',
                        'margin-bottom':'0.50in',
                        'margin-left':'0.50in',
                        'encoding':'UTF-8',
                        'no-outline':None
                    }
            pdf_content = pdfkit.from_string(input = html_content, output_path = False, options = option)
            
            if tenet_id == 1.1 and report_name.endswith('.zip'):
                # Save the PDF to a file
                with open('temp/output/explanationreport.pdf', 'wb') as f:
                    f.write(pdf_content)

                # Remove the HTML file from the zip
                os.remove('temp/output/explanationreport.html')

                # Add the PDF file to the zip
                with zipfile.ZipFile(zip_data, 'a') as zipf:
                    zipf.write('temp/output/explanationreport.pdf')

                # Create a zip file and add the HTML report and CSV file to it
                with zipfile.ZipFile('temp/report.zip', 'w') as zipf:
                    # Path to the directory you want to zip
                    directory = 'temp/output'

                    # Iterate over all the files in the directory
                    for foldername, subfolders, filenames in os.walk(directory):
                        for filename in filenames:
                            # Create the full file path
                            full_file_path = os.path.join(foldername, filename)

                            # Create the archive name (file path within the zip)
                            # This should be the file name without the 'temp/output' part
                            archive_name = os.path.relpath(full_file_path, directory)

                            # Add the file to the zip
                            zipf.write(full_file_path, arcname=archive_name)

                # Now you can save the updated zip file to the database
                # Assuming FileStoreDb.save_file() takes a file-like object
                with open('temp/report.zip', 'rb') as zipf:
                    report_file_id = FileStoreDb.save_file(file=zipf, tenet_id=tenet_id, content_type='application/zip')

                report_name = 'report.zip'
                content_type = 'application/zip'
                # Cleanup: remove the temporary directory
                shutil.rmtree('temp')
            else:
                report_file_id = FileStoreDb.save_file(file=pdf_content, tenet_id=tenet_id, content_type='application/pdf')
                report_name = 'report.pdf'
                content_type = 'application/pdf'
            # Save data to DB
            report_id = time.time()
            
            data={"ReportId": report_id, 
                  "BatchId": batch_id,
                  "TenetId": tenet_id,
                  "ReportName": report_name,
                  "ReportFileId": report_file_id,
                  "ContentType": content_type,
                  "CreatedDateTime": datetime.now()
                }
            Report.create(data)
            
            return {'status': 'SUCCESS', 'message': 'HTML to PDF conversion successful', 'ReportId': report_id}
            
        except Exception as e:
            log.error(e, exc_info=True)
            return {'status': 'FAILURE', 'message': f'Error while converting html to pdf, due to {str(e)}', 'BatchId': payload['batchId']}