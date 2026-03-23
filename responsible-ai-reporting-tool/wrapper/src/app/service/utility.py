'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''



import os
import os
import zipfile
import pdfkit

from app.config.logger import CustomLogger
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
log=CustomLogger()



class Utility:
    

    def sortReportsList(payload):
        sort_reports = sorted(payload, key=lambda x:x['CreatedDateTime'], reverse=True)
        return sort_reports



    def htmlToPdfWithWatermark(payload):

        try:
            with zipfile.ZipFile(payload['report_path'], 'r') as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.filename.endswith('.html'):

                        # convert html file into pdf file
                        html_path = zip_file.extract(file_info.filename, payload['data_path'])
                        pdf_path = os.path.join(payload['data_path'], file_info.filename.split('.')[0]+'.pdf')
                        option = {
                            'page-size':'A4',
                            'orientation':'Portrait',
                            'encoding':'UTF-8',
                            'no-outline':None,
                        }
                        pdfkit.from_file(html_path, output_path=pdf_path, options=option)
                        os.remove(html_path)

                        # create watermark.pdf file
                        watermark_path = os.path.join(payload['data_path'], 'watermark.pdf')
                        txt = 'Infosys'
                        txt = ''
                        c = canvas.Canvas(watermark_path, pagesize=letter)
                        c.setFont('Helvetica', 50)
                        c.setFillColorRGB(0.53,0.15,0.76)
                        c.setFillAlpha(0.13)
                        c.rotate(45)
                        c.drawString(400, 8, txt)
                        c.save()

                        # adding watermark in each page of report.pdf file
                        combine_pdf = os.path.join(payload['data_path'], 'report.pdf')
                        modify_pdf = os.path.join(payload['data_path'], 'report.pdf')

                        with open(combine_pdf, 'rb') as pdf_file, open(watermark_path, 'rb') as watermark_file:
                            pdf_reader = PdfReader(pdf_file)
                            watermark_reader = PdfReader(watermark_file)
                            watermark_page = watermark_reader.pages[0]
                            pdf_writer = PdfWriter()

                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                page.merge_page(watermark_page)
                                pdf_writer.add_page(page)

                            with open(modify_pdf, 'wb') as out_file:
                                pdf_writer.write(out_file)
                        os.remove(watermark_path)

                        with zipfile.ZipFile(payload['report_path'], 'a') as update_zip:
                            update_zip.write(pdf_path, arcname=file_info.filename.split('.')[0]+'.pdf')
                        os.remove(pdf_path)

            return 
        
        except Exception :
            # Log the detailed error for debugging purposes
            log.error("An error occurred during frame processing.")