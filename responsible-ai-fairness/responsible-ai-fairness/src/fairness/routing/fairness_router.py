"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import Annotated, Any, Dict, List
from fairness.config.logger import CustomLogger
from fairness.exception.exception import FairnessException
from fairness.mappers.mappers import AuditRequest, BatchId, MonitoringRequest
from fairness.service.service import FairnessService
from fairness.service.service import FairnessUIservice
from fairness.service.service_latest import FairnessServiceUpload
from fairness.service.service_latest import FairnessUIserviceUpload
from fairness.service.preprocessing import FairnessServicePreproc
from fairness.service.preprocessing import FairnessUIservicePreproc
from fairness.service.inprocessing import InprocessingService
from fairness.service.wrapper import FairnessWorkbench
from fairness.service.bart import BartService
from fairness.service.service_success_rates import SuccessRateService
from fairness.service.service_monitoring import FairnessAudit
from fastapi import APIRouter, HTTPException, UploadFile, Form,Body
from requests.exceptions import ChunkedEncodingError
from fastapi.responses import FileResponse
from fairness.mappers.mappers import FairnessAnalysisRequest,MitigationRequest,IndividualRequest,GetDataRequest
from fairness.exception.custom_exception import CustomHTTPException
from fairness.Telemetry.Telemetry_call import workbench_preprocess_labels, workbench_preprocess_get_batchId, workbenchAnalyse_get_data, workbench_Analyse, inprocess_get_data, inprocess_uploadfile, Wrapper_download, wraper_batch
from fairness.Telemetry.Telemetry_call import image_openai_keys,text_openai_keys
from fastapi import APIRouter, HTTPException, Depends
from fairness.auth.auth_client_id import get_auth_client_id
from fairness.auth.auth_jwt import get_auth_jwt
from fairness.auth.auth_none import get_auth_none
from fairness.mappers.mappers import GetDataRequest
import traceback
import os
from openai import AuthenticationError
from typing import Optional


llm_router = APIRouter()
workbench_router = APIRouter()
standalone_apis_router = APIRouter()
monitoring_apis=APIRouter()
log = CustomLogger()
uiService = FairnessUIservice()
service = FairnessService()
analyse = FairnessServiceUpload()
analyseUpload = FairnessUIserviceUpload()
servicepreproc = FairnessServicePreproc()
uiServicepreproc = FairnessUIservicePreproc()
fairnessWorkbench = FairnessWorkbench()
inprocessing = InprocessingService()
fairnesstelemetryurl = os.getenv("FAIRNESS_TELEMETRY_URL")
telemetry_flag = os.getenv("tel_Falg")
auth_type = os.environ.get("AUTH_TYPE")

if auth_type == "azure":
    auth = get_auth_client_id()
elif auth_type == "jwt":
    auth = get_auth_jwt()

elif auth_type == 'none':
    auth = get_auth_none()
else:
    raise HTTPException(status_code=500, detail="Invalid authentication type configured")
   
@llm_router.post('/fairness/analysis/llm')
def bias_analysis_in_text(
    response: Annotated[str, Form()], 
    evaluator: Annotated[Optional[str], Form()] = None, auth=Depends(auth)
):
    try:
        payload={
            'response': response,
            'evaluator': evaluator
        }

        log.info('before invoking get analysis llm service')

        log.debug('request payload: '+str(payload))

        response=uiService.get_analysis_llm(payload)

        log.debug('response: '+str(response))

        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        errormsg = str(last_traceback)
        raise CustomHTTPException(text_openai_keys, "OPEN AI KEY WAS NOT FOUND", "open ai keys are not found in db")
    except AuthenticationError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        errormsg = str(last_traceback)
        raise CustomHTTPException(text_openai_keys, "OPEN AI KEY is Invalid", "open ai keys are not found in db")

@llm_router.post('/fairness/analysis/image')
def bias_analysis_in_image(
    prompt: Annotated[str, Form()],
    image: UploadFile,
    evaluator: Annotated[Optional[str], Form()] = None, auth=Depends(auth)
):
    try:
        payload={
            'prompt': prompt,
            'image': image,
            'evaluator': evaluator
        }

        log.info('before invoking get analysis image service')

        log.debug('request payload: '+str(payload))
        
        response=uiService.get_analysis_image(payload)

        log.debug('response: '+str(response))

        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        errormsg = str(last_traceback)
        raise CustomHTTPException(image_openai_keys, "OPEN AI KEY WAS NOT FOUND", "open ai keys are not found in db")
    except AuthenticationError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        errormsg = str(last_traceback)
        raise CustomHTTPException(image_openai_keys, "OPEN AI KEY is Invalid", "open ai keys are not found in db")

@llm_router.post('/fairness/bart/response')
def sterotype_classification_using_bart( 
                 text:Annotated[str, Form()], auth= Depends(auth)
                 ):
    try:
        bartService=BartService()
        log.info("before invoking service ")
        log.debug("request payload: " + str(text))
        log.debug(str(text))
        response = bartService.predict(text)
        log.debug(response)
        return response
    except FairnessException as cie:
        log.error(cie.__dict__)
        log.info("exit method")
        raise HTTPException(**cie.__dict__)

@standalone_apis_router.post('/fairness/analyse')
def analyze_classification_dataset(payload:FairnessAnalysisRequest=Body(...),file:GetDataRequest= Depends(), auth= Depends(auth)):
    payload = {
                "biasType": payload.biasType,
                "methodType": payload.methodType,
                "taskType": payload.taskType,
                "label": payload.label,
                "predLabel":payload.predLabel,
                "FavourableOutcome": payload.favourableOutcome,
                "ProtectedAttribute": payload.protectedAttribute,
                "priviledged": payload.priviledgedGroups, 
                "file": file.file}
    
    log.info("before invoking create get attribute mitigation usecase service ")
    log.debug("request payload: " + str(payload))
    log.debug(str(payload))
    
    response = analyseUpload.upload_file(payload)
    log.debug(response)
    return response

@standalone_apis_router.post('/fairness/pretrainMitigate')
def mitigate_bias_in_classification_Dataset(payload:MitigationRequest=Body(...),file:GetDataRequest= Depends(), auth= Depends(auth)):
    payload = {
                "MitigationType": payload.mitigationType,
                "MitigationTechnique": payload.mitigationTechnique,
                "taskType": payload.taskType,
                "label": payload.label,
                "FavourableOutcome": payload.favourableOutcome,
                "ProtectedAttribute": payload.protectedAttribute,
                "priviledged": payload.priviledgedGroups, 
                "file": file.file}
    log.info("before invoking create get attribute mitigation usecase service ")
    log.debug("request payload: " + str(payload))
    log.debug(str(payload))
    response = analyseUpload.upload_file_Premitigation(payload)
    log.debug(response)
    return response

@standalone_apis_router.get('/fairness/download/mitigatedData/{fileName}')
def download_mitigated_file(fileName: str, auth= Depends(auth)):
    try:
        log.debug(fileName)
        headers = {
            'Content-Disposition': f'attachment; filename={fileName}'
        }
        response = analyseUpload.get_mitigated_data(fileName)
        return FileResponse(response, media_type="application/octet-stream", headers=headers)

    except Exception as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)
    

@standalone_apis_router.post('/fairness/individualMetrics',response_model=List[Dict[str, Any]])
def individual_metric(payload:IndividualRequest=Body(...),file:GetDataRequest= Depends(), auth= Depends(auth)):
    payload = {
                "label": payload.label, 
                "k":payload.k,
                "file": file.file}
    log.info("before invoking create get attribute mitigation usecase service ")
    log.debug("request payload: " + str(payload))
    log.debug(str(payload))
    response = analyseUpload.getLabels_Individual(payload)
    log.debug(response)
    return response

@workbench_router.post('/fairness/preprocessing/mitigation/get_data')
def preprocessing_mitigation_api_returning_atrributes(MitigationType: Annotated[str, Form()],
            MitigationTechnique: Annotated[str, Form()],
            taskType: Annotated[str, Form()],
            fileId: Annotated[str, Form()], auth= Depends(auth)):
    payload = {"MitigationType": MitigationType,
            "MitigationTechnique": MitigationTechnique,
            "taskType": taskType,
            "fileId": fileId}
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        log.debug(str(payload))
        response = uiServicepreproc.upload_file_pretrainMitigation(payload)
        log.debug(response)
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_preprocess_labels, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_preprocess_labels, "error occured"+ " Line no:" + str(errormsg), "file not found")



@workbench_router.post('/fairness/preprocessing/mitigation/BatchId')
def preprocessing_dataset_mitigation(payload: BatchId, auth= Depends(auth)):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        response = uiServicepreproc.return_pretrainMitigation_protected_attrib(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_preprocess_get_batchId, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_preprocess_labels, "error occured"+ " Line no:" + str(errormsg), "file not found")    

@workbench_router.get('/fairness/mitigation/getMitigatedData/{fileName}')
def download_mitigateFile(fileName: str, auth= Depends(auth)):
    try:
        log.debug(fileName)
        content_type=""
        if fileName.endswith(".csv"):
            content_type="text/csv"
        elif fileName.endswith(".feather"):
            content_type="application/octet-stream"
        elif fileName.endswith(".parquet"):
            content_type="application/octet-stream"
        elif fileName.endswith(".json"):
             content_type="application/json" 
        headers = {
            'Content-Disposition': f'attachment; filename={fileName}',
            "Content-Type": content_type
        }
        response = service.get_mitigated_data(fileName)
        log.info(f"{response}")
        # return FileResponse(response, headers=headers)
        return response

    except FairnessException as cie:
        log.error(cie.__dict__)
        log.info("exit create usecase routing method")
        raise HTTPException(**cie.__dict__)

#analyse with group, individual metrics
@workbench_router.post('/fairness/bias/Workbench/analyse/uploadfile')
def analyze_api_for_returning_attributes(biasType: Annotated[str, Form()],
            methodType: Annotated[str, Form()],
            taskType: Annotated[str, Form()],
            fileId: Annotated[str, Form()], auth= Depends(auth)):
    
    payload = {"biasType": biasType,
            "methodType": methodType,
            "taskType": taskType,
            "fileId": fileId}
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        log.debug(str(payload))
        response = uiServicepreproc.analyse_UploadFile(payload)
        log.debug(response)
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbenchAnalyse_get_data, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbenchAnalyse_get_data, "error occured"+ " Line no:" + str(errormsg), "file not found")


@workbench_router.post('/fairness/bias/workbench/analyze/batchId/Attributes')
def analyze_bias_in_structured_dataset(payload: BatchId, auth= Depends(auth)):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        response = uiServicepreproc.return_protected_attrib_analyseDB(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_Analyse, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(workbench_Analyse, "error occured"+ " Line no:" + str(errormsg), "file not found")

#inprocessing mitigation upload file
@workbench_router.post('/fairness/Workbench/inprocessing_uploadfile')
def inprocessing_api_for_returning_attributes(fileId: Annotated[str, Form()], auth= Depends(auth)):
    log.info("Entered create usecase routing method")
    payload={
        'fileId': fileId,
    }
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        log.debug(str(payload))
        response = inprocessing.upload_inprocess(payload)
        log.debug(response)
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(inprocess_uploadfile, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(inprocess_uploadfile, "error occured"+ " Line no:" + str(errormsg), "file not found")
    
@standalone_apis_router.post('/fairness/analyse/success_rate')
def get_success_rates(payload:AuditRequest=Body(...),file:GetDataRequest= Depends()):
    payload={
        "label":payload.label,
        "favourable_outcome":payload.favourableOutcome,
        "categorical_attributes":payload.categorical_attrbutes,
        "file":file.file
    }
    response = SuccessRateService.analyze(payload)
    return response     

@standalone_apis_router.get('/fairness/analyse/success_rate/download/{filename}')
def download_report(filename: str):
    response = SuccessRateService.download_pdf(filename)
    return FileResponse(
        response,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
    
@standalone_apis_router.post('/fairness/audit/fairness_classifier')
def audit_fairness_classifier(payload:MonitoringRequest=Body(...),file:GetDataRequest= Depends()):
    payload={
        "label":payload.label,
        "file":file.file
    }
    audit=FairnessAudit()
    response = audit.audit(payload)
    return response  

@standalone_apis_router.get('/fairness/audit/fairness_classifier/download/{filename}')
def download_report(filename: str):
    response = FairnessAudit.download_file(filename)
    return FileResponse(
        response,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@workbench_router.post('/fairness/wrapper/batchId')
def wrapper_endpoint_for_triggering_workbench(payload: BatchId, auth= Depends(auth)):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        response = fairnessWorkbench.wapper_trigger(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(wraper_batch, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(wraper_batch, "error occured"+ " Line no:" + str(errormsg), "file not found")


@workbench_router.post('/fairness/wrapper/download')
def wrapper_enpoint_for_downloading_report(payload: BatchId, auth= Depends(auth)):
    log.info("Entered create usecase routing method")
    try:
        log.info("before invoking create usecase service ")
        log.debug("request payload: " + str(payload))
        response = fairnessWorkbench.wrapper_download(payload)
        log.info("after invoking create usecase service ")
        log.debug("response : " + str(response))
        log.info("exit create usecase routing method")
        return response
    except HTTPException as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2] 
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(Wrapper_download, "filenot found error"+ " Line no:" + str(errormsg),  cie.__dict__.get("detail"))
    except ChunkedEncodingError as cie:
        log.error(cie.__dict__)
        log.info("inside exception data")
        log.info("exit create usecase routing method")
        traceback.print_exc()
        tb = traceback.TracebackException.from_exception(cie)
        last_traceback = list(tb.format())[-2]  
        log.info(f"{last_traceback}last_line")
        errormsg = str(last_traceback)
        raise CustomHTTPException(Wrapper_download, "error occured"+ " Line no:" + str(errormsg), "file not found")

