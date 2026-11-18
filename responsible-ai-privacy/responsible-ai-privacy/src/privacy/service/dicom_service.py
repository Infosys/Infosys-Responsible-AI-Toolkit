'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
import base64
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import pydicom
from PIL import Image
from presidio_image_redactor import DicomImageRedactorEngine
import cv2
from io import BytesIO
    
class DICOM:
    @staticmethod
    def dcm_to_png(dcm_obj):
        plt.imshow(dcm_obj.pixel_array,cmap=plt.cm.bone)
        plt.axis('off')
        b=BytesIO()
        plt.savefig(b,format='png', bbox_inches='tight', pad_inches=0)
        b.seek(0)
        return base64.b64encode(b.getvalue())
    @staticmethod
    def read_dicom(payload):

        engine = DicomImageRedactorEngine()
        dicom_instance = pydicom.dcmread(payload.file)
        print(type(dicom_instance))
        redacted_dicom_instance = engine.redact(dicom_instance, fill="contrast")        
        original=DICOM.dcm_to_png(dicom_instance)
        redacted=DICOM.dcm_to_png(redacted_dicom_instance)

        obj={"original":original,"anonymize":redacted}
        return obj


class saveImage:
    def save_img(img_data): 
        with open("file.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        