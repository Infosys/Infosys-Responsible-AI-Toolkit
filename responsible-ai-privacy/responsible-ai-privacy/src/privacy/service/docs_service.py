'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import base64
import io
from typing import Tuple
from PIL import Image
from privacy.service.imagePrivacy import AttributeDict, ImagePrivacy
from privacy.service.api_req import ApiCall
from privacy.service.textPrivacy import TextPrivacy
from privacy.service.__init__ import AttributeDict
import numpy as np
from privacy.config.logger import request_id_var
from privacy.config.logger import CustomLogger
import os
import threading
import uuid
from docx import Document
from docx.shared import Inches
import tempfile

log = CustomLogger()
error_dict = {}
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import ConflictResolutionStrategy
anonymizer = AnonymizerEngine()
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
LINE_NO_LABEL = "Line No:"

class DOCService:
    @staticmethod
    def process_images(run, payload, uid):
        try:
            request_id_var.set(uid)
            blip = run._element.xpath('.//pic:blipFill/a:blip')[0]
            r_id = blip.get(qn('r:embed'))
            log.debug(f"Relationship ID: {r_id}")

            # Get the image part using the relationship ID
            document_part = run.part
            image_part = document_part.related_parts[r_id]
            img_bytes = image_part.blob
            log.debug(f"Image bytes length: {len(img_bytes)}")
            
            if len(img_bytes) < 700:
                log.debug("Image is too small to process.")
                return None
            
            with io.BytesIO(img_bytes) as imgd:
                payload["image"] = AttributeDict({"file": imgd})
                res_image = ImagePrivacy.image_anonymize(AttributeDict(payload))
            log.debug(f"Anonymized image response: {res_image}")
            res_img = base64.b64decode(res_image)
            with io.BytesIO(res_img) as img_stream:
                img = Image.open(img_stream).copy()
            
            # Use tempfile to create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                img_path = tmp_file.name
                img.save(img_path)
            
            run.clear()
            run.add_picture(img_path, width=Inches(1.25))
            os.remove(img_path)
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "DOCMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)

    def editText(text, i, run):
        request_id_var.set("editText")
        print(text[i.start : i.end])
        run.text = run.text.replace(text[i.start:i.end], f"<{i.entity_type}>")
    @staticmethod
    def process_text(paragraph, payload, uid):
        try:
            request_id_var.set(uid)
            for run in paragraph.runs:
                text = run.text
                acc_details = None
                if payload.portfolio is not None:
                    acc_details = AttributeDict({"portfolio": payload.portfolio, "account": payload.account})
                res = TextPrivacy.text_analyze(text=text, acc_name=acc_details, exclusion=payload.exclusion.split(',') if payload.exclusion is not None else [],pii_entities_to_be_redacted=payload.pii_entities_to_be_redacted.split(',') if payload.pii_entities_to_be_redacted != None else [],nlp=payload.nlp, score_threshold=payload.score_threshold if payload.score_threshold is not None else 0.0)
                res = anonymizer._remove_conflicts_and_get_text_manipulation_data(res, (ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED))
                res = anonymizer._merge_entities_with_whitespace_between(text, res)
                resThreads = []
                for i in res:
                    thread = threading.Thread(target=DOCService.editText, args=(text, i, run))
                    thread.start()
                    resThreads.append(thread)
                for thread in resThreads:
                    thread.join()
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "DOCMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def mask_doc(payload):
        try:
            log.debug("payload:-" + str(payload))
            request_id = uuid.uuid4().hex
            request_id_var.set(request_id)
            payload=AttributeDict(payload)

            if payload.portfolio is not None or payload.account is not None:
                response_value = ApiCall.request(AttributeDict({"portfolio": payload.portfolio, "account": payload.account}))
                if response_value is None:
                    return None

            doc_file = Document(io.BytesIO(payload.file.file.read()))

            for paragraph in doc_file.paragraphs:
                threads = []
                thread = threading.Thread(target=DOCService.process_text, args=(paragraph, payload, id))
                thread.start()
                threads.append(thread)
                for run in paragraph.runs:
                    if run._element.xpath('.//pic:blipFill/a:blip'):
                        thread = threading.Thread(target=DOCService.processImages, args=(paragraph, run, payload, id))
                        thread.start()
                        threads.append(thread)
                for thread in threads:
                    thread.join()

            doc_bytes = io.BytesIO()
            doc_file.save(doc_bytes)
            doc_bytes.seek(0)

            return doc_bytes
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "DOCMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
        
