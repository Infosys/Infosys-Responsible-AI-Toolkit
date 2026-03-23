'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import argparse
import time
import json
from os import listdir
import os
from os.path import isfile, join, exists, isdir, abspath
import shutil
import uuid

import numpy as np
import tensorflow as tf
from tensorflow import keras
import tensorflow_hub as hub
from profanity.config.logger import CustomLogger
log = CustomLogger()

IMAGE_DIM = 224   # required/default image dimensionality



    

def load_images(image_paths, image_size, verbose=True):
    '''
    Function for loading images into numpy arrays for passing to model.predict
    inputs:
        image_paths: list of image paths to load
        image_size: size into which images should be resized
        verbose: show all of the image path and sizes loaded
    
    outputs:
        loaded_images: loaded images on which keras model can run predictions
        loaded_image_indexes: paths of images which the function is able to process
    
    '''
    loaded_images = []
    loaded_image_paths = []

    if isdir(image_paths):
        parent = abspath(image_paths)
        try:
            files = listdir(parent)
            image_paths = [join(parent, f) for f in files if isfile(join(parent, f))]
        except (OSError, PermissionError) as e:
            log.error("Unable to access directory for image processing")
            image_paths = []
    elif isfile(image_paths):
        image_paths = [image_paths]

    for img_path in image_paths:
        try:
            if verbose:
                log.debug(f"Processing image with target size: {image_size}")
            image = keras.preprocessing.image.load_img(img_path, target_size=image_size)
            image = keras.preprocessing.image.img_to_array(image)
            image /= 255
            loaded_images.append(image)
            loaded_image_paths.append(img_path)
        except Exception as ex:
            log.error("Failed to load image due to processing error")
    
    return np.asarray(loaded_images), loaded_image_paths


class Model:
    def load_model(model_path):
        if model_path is None or not exists(model_path):
            raise ValueError("saved_model_path must be the valid directory of a saved model to load.")
        
        model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer},compile=False)
        return model


def classify(model, input_paths, image_dim=IMAGE_DIM, predict_args={}):
    """
    Classify given a model, input paths (could be single string), and image dimensionality.
    
    Optionally, pass predict_args that will be passed to tf.keras.Model.predict().
    """
    images, image_paths = load_images(input_paths, (image_dim, image_dim))
    probs = classify_nd(model, images, predict_args)
    return dict(zip(image_paths, probs))


def classify_nd(model, nd_images, predict_args={}):
    """
    Classify given a model, image array (numpy)
    
    Optionally, pass predict_args that will be passed to tf.keras.Model.predict().
    """
    model_preds = model.predict(nd_images, **predict_args)
    
    categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

    probs = []
    for i, single_preds in enumerate(model_preds):
        single_probs = {}
        for j, pred in enumerate(single_preds):
            single_probs[categories[j]] = float(pred)
        probs.append(single_probs)
    return probs




class Detector:
    def detector(image_obj, accuracy):
        id = uuid.uuid4().hex
        output_folder = id
        os.makedirs(output_folder, exist_ok=True)
        output_image_path = os.path.join(output_folder, "received.png")
        image_obj.save(output_image_path, format="PNG")

        source = os.path.join(id, 'received.png')
        img_dim = 224
        img_dim_high = 299

        if accuracy == "high":
            modelInception = Model.load_model('../models/nsfw.299x299.h5')
            modelMobilenet = Model.load_model('../models/nsfw_mobilenet2.224x224.h5')
            
            # High accuracy specific code
            startTime = time.time()
            image_preds_inception = classify(modelInception, source, img_dim_high)
            image_preds_mobilenet = classify(modelMobilenet, source, img_dim)
            endTime = time.time()
            log.debug("Total Time Taken for high accuracy=====" + str(endTime - startTime))
            
            # Check if "hentai" is the highest parameter in Inception model's predictions
            if max(image_preds_inception[source], key=image_preds_inception[source].get) == "hentai":
                combined_preds = image_preds_mobilenet[source]
            else:
                # Combine results using weighted average
                combined_preds = {}
                for key in image_preds_inception[source]:
                    combined_preds[key] = (0.7 * image_preds_mobilenet[source][key] + 0.2 * image_preds_inception[source][key])

            image_preds = {source: combined_preds}
        elif accuracy == "low":
            modelMobilenet = Model.load_model('../models/nsfw_mobilenet2.224x224.h5')
            
            # Low accuracy specific code
            startTime = time.time()
            image_preds = classify(modelMobilenet, source, img_dim)
            endTime = time.time()
            log.debug("Total Time Taken for low accuracy=====" + str(endTime - startTime))
        else:
            raise ValueError("Invalid accuracy value. Choose 'high' or 'low'.")

        res = source
        log.debug(json.dumps(image_preds, indent=2), '\n')
        shutil.rmtree(id)
        log.debug(str(id) + " Folder Deleted")
        return image_preds[res]

