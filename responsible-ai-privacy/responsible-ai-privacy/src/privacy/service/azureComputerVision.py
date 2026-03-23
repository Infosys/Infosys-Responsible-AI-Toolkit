'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# from privacy.util.encrypt import EncryptImage

from presidio_image_redactor import ImageRedactorEngine,ImageAnalyzerEngine,ImagePiiVerifyEngine,OCR
# from privacy.service import easyocr_analyzer       
from dotenv import load_dotenv
from privacy.config.logger import CustomLogger
# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\amitumamaheshwar.h\AppData\Local\Programs\Tesseract-OCR"
import time
load_dotenv()
import os
import sys
import requests

from PIL import Image
from io import BytesIO

log = CustomLogger()

# log = CustomLogger()
# output_type = easyocr.Reader(['en'],model_storage_directory=r"privacy/util/model",download_enabled=False)
        
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class Data:
    encrypted_text=[]
    
apikey=os.getenv("API_KEY")
apiendpint=os.getenv("API_ENDPOINT")
# image_path=r"C:\WORK\GIT\responsible-ai-admin\responsible-ai-admin\src\rai_admin\temp\MicrosoftTeams-image (4).png"
# # Read the image into a byte array
# image_data = open(image_path, "rb").read()
# Set Content-Type to octet-stream
headers = {'Ocp-Apim-Subscription-Key': apikey, 'Content-Type': 'application/octet-stream'}
params = {'language': 'en', 'detectOrientation': 'true','features':['read']}
class ComputerVision(OCR):

    def process(a):
        return a

            
        
        
    # def perform_ocr(self, image: object, **kwargs) -> dict:
    #     # output_type = easyocr.Reader(['en'])
    #     s=time.time()
    #     # response(code)
        
    #     textmap={"text":[],"left":[],"top":[],"width":[],"height":[],"conf":[]}
    #     buffer = BytesIO()

    #     # Save the image to the in-memory buffer in PNG format
    #     image.save(buffer, "PNG")

    #     # Get the binary data from the buffer (seek to the beginning)
    #     binary_data = buffer.getvalue()
    #     image_data = binary_data
    #     # put the byte array into your post request
    #     response = requests.post(apiendpint, headers=headers, params=params, data = image_data)

    #     response.raise_for_status()

    #     analysis = response.json()
    #     line_infos = [region["lines"] for region in analysis["regions"]]
    #     word_infos = []
    #     for line in line_infos:
    #         for word_metadata in line:
    #             for word_info in word_metadata["words"]:
    #                 word_infos.append(word_info)

    #     for val in word_infos:
    #         boxval=val["boundingBox"].split(',')
    #         textmap["text"].append(val["text"])
    #         textmap["left"].append(int(boxval[0]))
    #         textmap["top"].append(int(boxval[1]))
    #         textmap["width"].append(int(boxval[2]))
    #         textmap["height"].append(int(boxval[3]))
    #         # textmap["conf"].append(val["conf"])
    #         # text.append(val["text"])
    #         # left.append(min(val['coordinates'][0][0],val["coordinates"][3][0]))
    #         # top.append(min(val['coordinates'][0][1],val["coordinates"][1][1]))
    #         # width.append(abs(val['coordinates'][1][0]-val["coordinates"][0][0]))
    #         # height.append(abs(val['coordinates'][3][1]-val["coordinates"][0][1]))
    #         # conf.append(val["conf"])
    #     print(textmap)
    #     log.warn("time======="+str(time.time()-s))
    #     return textmap
            

    def perform_ocr(self, image: object, **kwargs) -> dict:
        # output_type = easyocr.Reader(['en'])
        s=time.time()
        # response(code)
        
        textmap={"text":[],"left":[],"top":[],"width":[],"height":[],"conf":[]}
        buffer = BytesIO()

        # Save the image to the in-memory buffer in PNG format
        image.save(buffer, "PNG")

        # Get the binary data from the buffer (seek to the beginning)
        binary_data = buffer.getvalue()
        image_data = binary_data
        # put the byte array into your post request
        response = requests.post(apiendpint, headers=headers, params=params, data = image_data)

        response.raise_for_status()

        analysis = response.json()
        print(analysis)
        line_infos = [region["lines"] for region in analysis["readResult"]["blocks"]]
        textmap={"text":[],"left":[],"top":[],"width":[],"height":[],"conf":[]}
        for line in line_infos:
            for word_metadata in line:
                for val in word_metadata["words"]:
                    # word_infos.append(val)
                    textmap["text"].append(val["text"])
                    textmap["left"].append(min(val['boundingPolygon'][0]['x'],val["boundingPolygon"][3]['x']))
                    textmap["top"].append(min(val['boundingPolygon'][0]['y'],val["boundingPolygon"][1]['y']))
                    textmap["width"].append(abs(val['boundingPolygon'][1]['x']-val["boundingPolygon"][0]['x']))
                    textmap["height"].append(abs(val['boundingPolygon'][3]['y']-val["boundingPolygon"][0]['y']))
                    textmap["conf"].append(val["confidence"])
        print(textmap)
        log.warn("time======="+str(time.time()-s))
        return textmap
            
