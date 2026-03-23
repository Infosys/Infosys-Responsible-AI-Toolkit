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

    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img



class Detect:
    def getFace(image:Image):
        # print(type(image))
        image= asarray(image)
        # print(image)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # print(len(image.shape))
        # print(image.shape)
        if(len(image.shape)==3):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif(len(image.shape)==2):
            gray = image
        else:
            gray = image
        # print(gray)

# Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        # print("done")
        # print(faces)
# Extract and save each detected face
        for i, (x, y, w, h) in enumerate(faces):
            face = image[y:y+h, x:x+w]
            # print(x,y,w,h)
            
            # cv2.imwrite(f'C:\\WORK\\GIT\\responsible-ai-privacy\\responsible-ai-privacy\\src\\face_{i}.jpg', face)
            # print("returning")
            return(x,y,w,h)
        
class EncryptImage:
    text=""
    entity=[]
    def __init__(self, image_analyzer_engine: Optional[ImageAnalyzerEngine] = None):
        if not image_analyzer_engine:
            image_analyzer_engine = ImageAnalyzerEngine()
        self.image_analyzer_engine = image_analyzer_engine
        self.bbox_processor = BboxProcessor()
        # redactorEngine = ImageRedactorEngine(image_analyzer_engine=self.image_analyzer_engine)
    
    def getText(self,image:Image,ocr_kwargs:Optional[dict] = None,**analyzer_data):
        # "Code/Functions from image_analyzer_engine"
        print(type(image))
        perform_ocr_kwargs, ocr_threshold = self.image_analyzer_engine._parse_ocr_kwargs(ocr_kwargs)
        ocr_result = self.image_analyzer_engine.ocr.perform_ocr(image, **perform_ocr_kwargs)

        
        # Apply OCR confidence threshold if it is passed in
        if ocr_threshold:
            ocr_result = self.image_analyzer_engine.threshold_ocr_result(ocr_result, ocr_threshold)

        # Analyze text
        text = self.image_analyzer_engine.ocr.get_text_from_ocr_dict(ocr_result)
        EncryptImage.text=text
        
    def imageAnonimyze( self,
        image: Image,
        fill: Union[int, Tuple[int, int, int]] = (0, 0, 0),
        ocr_kwargs: Optional[dict] = None,
        encryptionList:Optional[list]=[],
        **text_analyzer_kwargs,):
        
        """"Code/Functions from Image Redactor"""
        image = ImageChops.duplicate(image)

        bboxes = self.image_analyzer_engine.analyze(
            image, ocr_kwargs, **text_analyzer_kwargs
        )
        
        # EncryptImage.entity.extend(bboxes)
        print("box==========",bboxes)
        draw = ImageDraw.Draw(image)
        
        for box in bboxes:
            if(box.entity_type in encryptionList):
                
                EncryptImage.entity.append(box)
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            # print("=================",x0,y0)
            draw.rectangle([x0, y0, x1, y1], fill=fill)
        if("entities" in text_analyzer_kwargs):
            if("Face_Detect" in text_analyzer_kwargs["entities"]):
                res=Detect.getFace(image)
                if(res==None):
                    pass
                elif(len(res)==4):
                    x,y,w,h=res
                    draw.rectangle([x-(x*.05),y-(x*.05),x+w+(w*.25),y+h+(h*.25)], fill=fill)
        # x0,y0,x1,y1=(738, 1028, 217, 58)
        # draw.rectangle([x-(x*.05),y-(x*.05),x+w+(w*.25),y+h+(h*.25)], fill=fill)
                
      
        return image

        
        
    def dis():
        print("===========",EncryptImage.text)
        print("---------",EncryptImage.text.title())
        # print("==========",EncryptImage.entity)
        print("--------------------")
        
    def encrypt(self,image:Image,ocr_kwargs:Optional[dict] = None,encryptionList=[],**analyzer_data):
        """"Code Reference from Image Verify"""
        image = ImageChops.duplicate(image)
        image_x, image_y = image.size
        
        
        bboxes=EncryptImage.entity
        text=EncryptImage.text
        # print("boxA==",bboxes)
        dict_operators={}
        if encryptionList is not None and len(encryptionList) >0 :
            for entity in encryptionList:
                dict_operators.update({entity: OperatorConfig("hash", {"hash-type": 'md5'})})
        else:
            dict_operators = None
            
        # print("dic=",dict_operators)
        analyzer_result=bboxes
        # print(analyzer_result)
        anonymizeEngine=AnonymizerEngine()
        anonymizeResult=anonymizeEngine.anonymize(text=text,
                                        operators=dict_operators,
                                              analyzer_results=analyzer_result)
        # print(r.items)
        
        # print("==========",anonymizeResult.items)
        result=anonymizeResult.items
        result=sorted(result, key=lambda i: i.start)
        
        
        # print("RRRRRRRRR=========",len(result),len(bboxes))
        fig, ax = plt.subplots()
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
                # print("i====######",i)
                drawen.append((box.start,box.end))
                if((i-excess)<len(result)):
                        # print(drawen,result[i-excess])
                        id=' '.join(random.choices(string.ascii_uppercase +
                             string.digits, k=N//2))
                        entity_type =id
                        res.append({"id":id,"text":result[i-excess].text,"entity_type":result[i-excess].entity_type,"start":box.start,"end":box.end})  
                x0 = box.left-15
                y0 = box.top
                x1 = x0 + box.width
                y1 = y0 + box.height
                # ax.annotate(
                #     entity_type,
                #     xy=(x1-((x1-x0)/2) , y1-((y1-y0)/2) ),
                #     xycoords="data",
                #     bbox=dict(boxstyle="round4,pad=.5", fc="0.9"),
                # )
                ax.text(x1-((x1-x0)/2), y1-((y1-y0)/2), entity_type, fontsize=12,bbox=dict(facecolor='white', alpha=0.5))
            # print("====",res)
            ax.imshow(image)
            im_from_fig = fig2img(fig)
            im_resized = im_from_fig.resize((image_x, image_y))
            im_resized = im_from_fig
            return (im_resized,res)
        

        
        
        
        
