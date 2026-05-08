'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''


from datetime import datetime
from fastapi import APIRouter, Form, HTTPException
from app.service.service import InfosysRAI
from app.config.logger import CustomLogger
import gc

report = APIRouter()

log=CustomLogger()

# ------------------------------------------------------------------------------------

@report.post('/v1/report/htmltopdfconversion')
async def html_to_pdf_conversion(batchId: float=Form(...)):
    log.info("Entered html_to_pdf_conversion routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking html_to_pdf_conversion usecase service ")
        payload = {'batchId': batchId}
        log.debug("Request payload: "+ str(payload))
        response = InfosysRAI.html_to_pdf_conversion(payload)
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        gc.collect()
        return response
    except Exception as exc:
        log.error(exc.__dict__)
        log.info("Exit create usecase routing method")
        raise HTTPException(**exc.__dict__)

@report.post('/v1/report/converttopdfreport')
async def convert_to_pdf_report(batchId:float=Form(...)):
    payload = {'batchid':batchId}
    response = InfosysRAI.combinedReport(payload)
    gc.collect()
    log.info(str(response))
    return response

@report.post('/v1/report/downloadreport')
async def download_report(batchId:float=Form(...)):
    log.info("Entered download_report routing method")
    try:
        start_time = datetime.now()
        log.info(f"start_time: {start_time}")
        log.info("Before invoking html_to_pdf_conversion usecase service ")
        payload = {'batchId': batchId}
        log.debug("Request payload: "+ str(payload))
        response = InfosysRAI.download_report(payload)
        log.info("After invoking create usecase service ")
        log.debug("Response : "+ str(response))
        log.info("Exit create usecase routing method")
        end_time = datetime.now()
        log.info(f"end_time: {end_time}")
        total_time = end_time - start_time
        log.info(f"total_time: {total_time}")
        gc.collect()
        return response
    except Exception as exc:
        log.error(exc.__dict__)
        log.info("Exit create usecase routing method")
        raise HTTPException(**exc.__dict__)

# ------------------------------------------------------------------------------------


