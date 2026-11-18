
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
from privacy.service.__init__ import AttributeDict,anonymizer,ConflictResolutionStrategy
import numpy as np
from privacy.config.logger import request_id_var
from privacy.config.logger import CustomLogger
import os
import threading
import uuid
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import tempfile
from unidecode import unidecode
LINE_NO_LABEL = "Line No:"

log = CustomLogger()
error_dict = {}

class PPTService:
    @staticmethod
    def normalize_text_with_mapping(text):
        normalized_text = []
        index_map = []
        boundary_map = [0]

        for index, char in enumerate(text):
            normalized = unidecode(char)
            if normalized:
                normalized_text.append(normalized)
                index_map.extend([index] * len(normalized))
                boundary_map.extend([index + 1] * len(normalized))
            else:
                boundary_map[-1] = index + 1

        return ''.join(normalized_text), index_map, boundary_map

    @staticmethod
    def get_original_substring(source_text, entity, index_map, boundary_map):
        if not index_map or not boundary_map:
            return None
        if entity.start >= entity.end:
            return None
        if entity.end > len(index_map) or entity.end >= len(boundary_map):
            return None
        original_start = index_map[entity.start]
        original_end = boundary_map[entity.end]
        return source_text[original_start:original_end]

    @staticmethod
    def process_images(slide, shape, payload, uid):
        try:
            request_id_var.set(uid)
            image = shape.image
            img_bytes = image.blob
            if len(img_bytes) < 700:
                return None
            with io.BytesIO(img_bytes) as imgd:
                payload["image"] = AttributeDict({"file": imgd})
                res_image = ImagePrivacy.image_anonymize(AttributeDict(payload))
            res_img = base64.b64decode(res_image)
            with io.BytesIO(res_img) as img_stream:
                img = Image.open(img_stream).copy()
            
            # Use tempfile to create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                img_path = tmp_file.name
                img.save(img_path)
            
            slide.shapes.add_picture(img_path, shape.left, shape.top, shape.width, shape.height)
            slide.shapes._spTree.remove(shape._element)
            os.remove(img_path)
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "PPTMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def edit_text(text, i, shape, source_text, index_map, boundary_map):
        request_id_var.set("editText")
        log.debug(str(text[i.start:i.end]) + ":" + str(i.entity_type))
        replacement_text = PPTService.get_original_substring(source_text, i, index_map, boundary_map)
        if replacement_text:
            shape.text = shape.text.replace(replacement_text, f"<{i.entity_type}>")
        else:
            log.warning(f"Could not map entity {i.entity_type} back to original text")
    @staticmethod
    def process_text(slide, payload, uid):
        try:
            request_id_var.set(uid)
            for shape in slide.shapes:
                if shape.has_text_frame:
                    source_text = shape.text
                    text, index_map, boundary_map = PPTService.normalize_text_with_mapping(source_text)

                    acc_details = None
                    if payload.portfolio is not None:
                        acc_details = AttributeDict({"portfolio": payload.portfolio, "account": payload.account})
                    res = TextPrivacy.text_analyze(text=text, acc_name=acc_details, exclusion=payload.exclusion.split(',') if payload.exclusion is not None else [],pii_entities_to_be_redacted=payload.pii_entities_to_be_redacted.split(",") if payload.pii_entities_to_be_redacted is not None else [],nlp=payload.nlp, score_threshold=payload.score_threshold if payload.score_threshold is not None else 0.0)

                    if not isinstance(res, list):
                        raise ValueError(f"Expected a list from text_analyze, but got: {type(res)}")
                    res = anonymizer._remove_conflicts_and_get_text_manipulation_data(res, (ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED))
                    res = anonymizer._merge_entities_with_whitespace_between(text, res)
                    res_threads = []
                    for i in res:
                        thread = threading.Thread(target=PPTService.edit_text, args=(text, i, shape, source_text, index_map, boundary_map))
                        thread.start()
                        res_threads.append(thread)
                    for thread in res_threads:
                        thread.join()
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "PPTMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)
    @staticmethod
    def process_tables(slide, payload, uid):
        try:
            request_id_var.set(uid)
            for shape in slide.shapes:
                if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                    table = shape.table
                    for row in table.rows:
                        for cell in row.cells:
                            source_text = cell.text
                            text, index_map, boundary_map = PPTService.normalize_text_with_mapping(source_text)
                            text = text + " ,"
                            acc_details = None
                            if payload.portfolio is not None:
                                acc_details = AttributeDict({"portfolio": payload.portfolio, "account": payload.account})
                            res = TextPrivacy.text_analyze(text=text, acc_name=acc_details, exclusion=payload.exclusion.split(',') if payload.exclusion is not None else [],pii_entities_to_be_redacted=payload.pii_entities_to_be_redacted.split(",") if payload.pii_entities_to_be_redacted is not None else [],nlp=payload.nlp, score_threshold=payload.score_threshold if payload.score_threshold is not None else 0.0)
                            res = anonymizer._remove_conflicts_and_get_text_manipulation_data(res, (ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED))
                            res = anonymizer._merge_entities_with_whitespace_between(text, res)
                            for i in res:
                                replacement_text = PPTService.get_original_substring(source_text, i, index_map, boundary_map)
                                if replacement_text:
                                    cell.text = cell.text.replace(replacement_text, f"<{i.entity_type}>")
                                else:
                                    log.warning(f"Could not map entity {i.entity_type} in table cell")
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "PPTMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)

    @staticmethod
    def process_notes(slide, payload, uid):
        try:
            request_id_var.set(uid)
            if not slide.notes_slide or not slide.notes_slide.notes_text_frame:
                return

            notes_text_frame = slide.notes_slide.notes_text_frame

            for paragraph in notes_text_frame.paragraphs:
                source_text = paragraph.text
                if not source_text.strip():
                    continue

                text, index_map, boundary_map = PPTService.normalize_text_with_mapping(source_text)

                acc_details = None
                if payload.portfolio is not None:
                    acc_details = AttributeDict({"portfolio": payload.portfolio, "account": payload.account})
                res = TextPrivacy.text_analyze(text=text, acc_name=acc_details, exclusion=payload.exclusion.split(',') if payload.exclusion is not None else [],pii_entities_to_be_redacted=payload.pii_entities_to_be_redacted.split(",") if payload.pii_entities_to_be_redacted is not None else [],nlp=payload.nlp, score_threshold=payload.score_threshold if payload.score_threshold is not None else 0.0)

                if not isinstance(res, list):
                    raise ValueError(f"Expected a list from text_analyze, but got: {type(res)}")
                res = anonymizer._remove_conflicts_and_get_text_manipulation_data(res, (ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED))
                res = anonymizer._merge_entities_with_whitespace_between(text, res)

                for entity in res:
                    replacement_text = PPTService.get_original_substring(source_text, entity, index_map, boundary_map)
                    if replacement_text:
                        paragraph.text = paragraph.text.replace(replacement_text, f"<{entity.entity_type}>")
                    else:
                        log.warning(f"Could not map entity {entity.entity_type} in notes")
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "PPTMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)

    def mask_ppt(payload):
        try:
            log.debug("payload:-" + str(payload))
            request_id= uuid.uuid4().hex
            request_id_var.set(request_id)
            payload = AttributeDict(payload)
            if payload.portfolio is not None or payload.account is not None:
                response_value = ApiCall.request(AttributeDict({"portfolio": payload.portfolio, "account": payload.account}))
                if response_value is None:
                    return None

            ppt_file = Presentation(io.BytesIO(payload.file.file.read()))

            for slide in ppt_file.slides:
                threads = []
                thread = threading.Thread(target=PPTService.process_text, args=(slide, payload, request_id))
                thread.start()
                threads.append(thread)
                for shape in slide.shapes:
                    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                        thread = threading.Thread(target=PPTService.process_images, args=(slide, shape, payload, request_id))
                        thread.start()
                        threads.append(thread)
                    elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                        thread = threading.Thread(target=PPTService.process_tables, args=(slide, payload, request_id))
                        thread.start()
                        threads.append(thread)
                thread = threading.Thread(target=PPTService.process_notes, args=(slide, payload, request_id))
                thread.start()
                threads.append(thread)
                for thread in threads:
                    thread.join()

            ppt_bytes = io.BytesIO()
            ppt_file.save(ppt_bytes)
            ppt_bytes.seek(0)

            return ppt_bytes
        except Exception as e:
            log.error(str(e))
            log.error(LINE_NO_LABEL + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            if request_id_var.get() not in error_dict:
                error_dict[request_id_var.get()] = []
            error_dict[request_id_var.get()].append({"UUID": request_id_var.get(), "function": "PPTMASKMainFunction", "msg": str(e.__class__.__name__), "description": str(e) + LINE_NO_LABEL + str(e.__traceback__.tb_lineno)})
            raise RuntimeError(e)