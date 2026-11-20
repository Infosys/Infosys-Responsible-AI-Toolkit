'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
import base64
import io
import matplotlib.pyplot as plt
import pydicom
from PIL import Image
from privacy.service.__init__ import AttributeDict,admin_par,error_dict
from presidio_image_redactor import DicomImageRedactorEngine
from privacy.service.api_req import ApiCall
from privacy.config.logger import request_id_var
from privacy.config.logger import CustomLogger

log = CustomLogger()

class DICOMPrivacy:
    @staticmethod
    def dcm_to_png(dcmObj):
        plt.clf()
        plt.imshow(dcmObj.pixel_array,cmap=plt.cm.bone)
        plt.axis('off')
        buffer=io.BytesIO()
        plt.savefig(buffer,format='png', bbox_inches='tight', pad_inches=0)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue())
        
    
   
    @staticmethod
    def read_dicom(payload):
        error_dict[request_id_var.get()]=[]
        log.debug("Entering in readDicom function")
        try:
            dicom_engine = DicomImageRedactorEngine()
            dicom_instance = pydicom.dcmread(payload.file)
            redacted_dicom_instance = dicom_engine.redact(dicom_instance, fill="contrast") 
            original=DICOMPrivacy.dcm_to_png(dicom_instance)
            redacted=DICOMPrivacy.dcm_to_png(redacted_dicom_instance)

            obj={"original":original,"anonymize":redacted}
            log.debug("Returning from readDicom function")
            return obj
  
        except Exception as e:
            log.error(str(e))
            log.error("Line No:" + str(e.__traceback__.tb_lineno))
            log.error(str(e.__traceback__.tb_frame))
            error_dict[request_id_var.get()].append({
                "UUID": request_id_var.get(),
                "function": "read_dicom",
                "msg": str(e.__class__.__name__),
                "description": str(e) + "Line No:" + str(e.__traceback__.tb_lineno)
            })
            raise RuntimeError(e)
  



class saveImage:
    @staticmethod
    def save_img(img_data):
        
        
        with open("file.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        