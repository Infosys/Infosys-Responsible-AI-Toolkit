from typing import Dict, Callable
from privacy.service.Video_service import *
from privacy.service.csv_service import *
from privacy.service.json_service import *
from privacy.service.files_service import *
from privacy.service.pdf_service import PDFService
from privacy.service.ppt_service import PPTService  
from privacy.service.docs_service import DOCService
from fastapi import Response

class FileService:
    @staticmethod
    def anonymize_file(payload: Dict, file_extension: str) -> str:
        if file_extension == 'csv':
            return CSVService.csv_anonymize(payload)
        elif file_extension == 'json':
            return JSONService.anonymize_json(payload)
        elif file_extension == 'pdf':
            # ans=PDFService.mask_pdf(payload)
            # response = Response(content=ans.read(), media_type="application/pdf")
            return PDFService.mask_pdf(payload)
            # return response
        elif file_extension == 'pptx' or file_extension == 'ppt':
            # ans=PPTService.mask_ppt(payload)
            # response = Response(content=response.read(), media_type="application/pdf")
            return PPTService.mask_ppt(payload)
        elif file_extension == 'docx':
            return DOCService.mask_doc(payload)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")