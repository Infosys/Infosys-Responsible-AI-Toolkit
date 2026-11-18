from typing import Dict, Callable
from privacy.service.Video_service import VideoService
from privacy.service.csv_service import CSVService
from privacy.service.json_service import JSONService
#from privacy.service.pdf_service import PDFService
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
        #elif file_extension == 'pdf':
           #return PDFService.mask_pdf(payload)
        elif file_extension == 'pptx' or file_extension == 'ppt':
            return PPTService.mask_ppt(payload)
        elif file_extension == 'docx':
            return DOCService.mask_doc(payload)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")