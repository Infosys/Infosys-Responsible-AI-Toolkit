'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import cv2
from PIL import Image, ImageChops
from presidio_image_redactor import ImageRedactorEngine
from presidio_image_redactor.image_analyzer_engine import ImageAnalyzerEngine
import matplotlib
import io
from numpy import asarray
from matplotlib import pyplot as plt
import string
import random
from typing import Optional
import time
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageAnalyzerEngine, BboxProcessor
from PIL import Image, ImageDraw, ImageChops
from presidio_anonymizer.entities import (RecognizerResult,
    OperatorResult,
    OperatorConfig)
from typing import Union, Tuple, Optional

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it."""

    with io.BytesIO() as buf:
        fig.savefig(buf)
        buf.seek(0)
        return Image.open(buf).copy()
       
class EncryptImage:
    text=""
    entity=[]
    def __init__(self, image_analyzer_engine: Optional[ImageAnalyzerEngine] = None):
        if not image_analyzer_engine:
            image_analyzer_engine = ImageAnalyzerEngine()
        self.image_analyzer_engine = image_analyzer_engine
        self.bbox_processor = BboxProcessor()
       
    
    def get_text(self,image:Image,ocr_kwargs:Optional[dict] = None):
    
        print(type(image))
        perform_ocr_kwargs, ocr_threshold = self.image_analyzer_engine._parse_ocr_kwargs(ocr_kwargs)
        ocr_result = self.image_analyzer_engine.ocr.perform_ocr(image, **perform_ocr_kwargs)

        
      
        if ocr_threshold:
            ocr_result = self.image_analyzer_engine.threshold_ocr_result(ocr_result, ocr_threshold)
        text = self.image_analyzer_engine.ocr.get_text_from_ocr_dict(ocr_result)
        EncryptImage.text=text
        
    def image_anonymize( self,
        image: Image,
        fill: Union[int, Tuple[int, int, int]] = (0, 0, 0),
        ocr_kwargs: Optional[dict] = None,
        encryption_list:Optional[list]=[],
        **text_analyzer_kwargs,):
        
        """"Code/Functions from Image Redactor"""
        image = ImageChops.duplicate(image)

        bboxes = self.image_analyzer_engine.analyze(
            image, ocr_kwargs, **text_analyzer_kwargs
        )
        
        print("box==========",bboxes)
        draw = ImageDraw.Draw(image)
        
        for box in bboxes:
            if(box.entity_type in encryption_list):
                
                EncryptImage.entity.append(box)
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            draw.rectangle([x0, y0, x1, y1], fill=fill)
            
     
                
      
        return image

        
    @staticmethod    
    def dis():
        print("===========",EncryptImage.text)
        print("---------",EncryptImage.text.title())
   
        print("--------------------")
        
    def encrypt(self,image:Image,encryption_list=[]):
        """"Code Reference from Image Verify"""
        image = ImageChops.duplicate(image)
        image_x, image_y = image.size
        
        
        bboxes=EncryptImage.entity
        text=EncryptImage.text

        dict_operators={}
        if encryption_list is not None and len(encryption_list) >0 :
            for entity in encryption_list:
                dict_operators.update({entity: OperatorConfig("hash", {"hash-type": 'md5'})})
        else:
            dict_operators = None
        analyzer_result=bboxes
        anonymize_engine=AnonymizerEngine()
        anonymize_result=anonymize_engine.anonymize(text=text,
                                        operators=dict_operators,
                                              analyzer_results=analyzer_result)

        result=anonymize_result.items
        result=sorted(result, key=lambda i: i.start)
        
        fig, ax = plt.subplots()
        try:
            ax.axis('off')
            image_r = 70
            fig.set_size_inches(image_x / image_r, image_y / image_r)
            res=[]
            drawen=[]
            excess=0
            if len(bboxes) == 0:
                return (image,res)
            else:
                for i in range(len(bboxes)):
                    box=bboxes[i]
                    N=box.end-box.start
                    if((box.start,box.end)in drawen):
                        excess+=1
                        continue
                    drawen.append((box.start,box.end))
                    if((i-excess)<len(result)):
                            entity_id=' '.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=N//2))
                            entity_type =entity_id
                            res.append({"id":entity_id,"text":result[i-excess].text,"entity_type":result[i-excess].entity_type,"start":box.start,"end":box.end})  
                    x0 = box.left-15
                    y0 = box.top
                    x1 = x0 + box.width
                    y1 = y0 + box.height
                    ax.text(x1-((x1-x0)/2), y1-((y1-y0)/2), entity_type, fontsize=12,bbox=dict(facecolor='white', alpha=0.5))
                ax.imshow(image)
                im_from_fig = fig2img(fig)
                im_resized = im_from_fig.resize((image_x, image_y))
                return (im_resized,res)
        finally:
            plt.close(fig)
        

        
        
        
        
