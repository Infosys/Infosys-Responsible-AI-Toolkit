
import time
import cv2
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
side_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_profileface.xml')

class FaceDetect:
    def frontFaceDetection(image):
        if(len(image.shape)==3):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            front_face = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            return front_face
        return None
        
    def fullFaceDetection(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            front_face = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            side_faces = side_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if(len(front_face)==0 and len(side_faces)>0):
                front_face=side_faces
            elif(len(front_face)>0 and len(side_faces)>0):
                front_face=np.concatenate((front_face, side_faces), axis=0)
            return front_face    
            
        