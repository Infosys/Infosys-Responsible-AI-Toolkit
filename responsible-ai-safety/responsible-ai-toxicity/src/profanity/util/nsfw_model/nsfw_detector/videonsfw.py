'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from keras.models import load_model
import numpy as np
from collections import deque
import warnings
warnings.filterwarnings("ignore")
import cv2
import tensorflow as tf
from tensorflow import keras
import tensorflow_hub as hub
import tempfile
import os
import base64
from collections import deque
from fastapi.responses import FileResponse
import json
model_path = "../models/nsfw.299x299.h5"
model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer},compile=False)


def process_video(payload, safetyConfig):
    input_vid = payload['video']
    size = 128
    labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
    Q = deque(maxlen=size)
    filename = input_vid.filename
    safetyConfig = json.loads(safetyConfig)
    
    # Create a temporary file to store the input video
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        input_vid.file.seek(0)
        temp_file.write(input_vid.file.read())

    vs = cv2.VideoCapture(temp_file_path)
    writer = None
    (W, H) = (None, None)
    videoAnalyze = {}

    # Create a temporary file for the processed video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_file:
        output_vid_path = output_file.name
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        while True:
            (grabbed, frame) = vs.read()

            if not grabbed:
                break
            if frame is None:
                continue
            if W is None or H is None:
                (H, W) = frame.shape[:2]

            output = frame.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame / 255.0
            frame = cv2.resize(frame, (299, 299)).astype("float32")

            preds = model.predict(np.expand_dims(frame, axis=0))[0]
            Q.append(preds)

            results = np.array(Q).mean(axis=0)

            # Apply blurring based on custom logic
            res = dict(zip(labels, results))
            if (res["sexy"] > float(safetyConfig["sexy"]) or
                    res["hentai"] > float(safetyConfig["hentai"]) or
                    res["porn"] > float(safetyConfig["porn"])):
                output = cv2.GaussianBlur(output, (101, 101), 30)
            elif (res["sexy"] > res["neutral"] or
                  res["hentai"] > res["neutral"] or
                  res["porn"] > res["neutral"]):
                output = cv2.GaussianBlur(output, (101, 101), 30)

            i = np.argmax(results)
            label = labels[i]

            if results[i] > 0.20:
                text = "Detection: {}:".format(label)
                cv2.putText(output, text, (35, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

            # Initialize the video writer if it's not already done
            if writer is None:
                writer = cv2.VideoWriter(output_vid_path, fourcc, 30, (W, H), True)

            # Write the processed frame to the output video file
            writer.write(output)

        if writer is not None:
            writer.release()  # Finalize the video file
    vs.release()

    # Read the processed video file and convert it to Base64
    with open(output_vid_path, 'rb') as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode('utf-8')

    # Delete the temporary processed video file
    os.remove(output_vid_path)

    for i, label in enumerate(labels):
        videoAnalyze[label] = float(results[i])

    response = {
        "videoAnalyze": videoAnalyze,
        "BlurredVideo": video_base64
    }

    os.remove(temp_file_path)  # Clean up the temporary input file
    return response
        
def test(video_base64):
    # Decode the Base64 string
    video_data = base64.b64decode(video_base64)

    # Write the data to an MP4 file
    with open('output_video.mp4', 'wb') as video_file:
        video_file.write(video_data)
