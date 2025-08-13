# # from keras.models import load_model
# import numpy as np
# from collections import deque
# import warnings
# warnings.filterwarnings("ignore")
# import cv2
# import tensorflow as tf
# from tensorflow import keras
# import tensorflow_hub as hub

# model_path = "nsfw.299x299.h5"
# model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer},compile=False)
# labels = {0 : "drawings", 1 : "hentai", 2 : "neutral", 3 : "porn", 4 : "sexy"}
# size = 128
# input_vid = "ex4anime.mp4"
# output_vid = "Output1.mp4"

# # Mean Subtraction
# # mean = np.array([123.68, 116.779, 103.939][::1], dtype="float32")
# Q = deque(maxlen=size)

# vs = cv2.VideoCapture(input_vid)
# writer = None
# (W, H) = (None, None)

# # loop over frames from the video file stream
# while True:
#     # read the next frame from the file
#     (grabbed, frame) = vs.read()

#     # if the frame was not grabbed, then we have reached the end
#     # of the stream
#     if not grabbed:
#         break

#     # if the frame dimensions are empty, grab them
#     if W is None or H is None:
#         (H, W) = frame.shape[:2]
    
#     output = frame.copy()
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     frame = frame/255.0
#     frame = cv2.resize(frame, (299,299)).astype("float32")
    
# #     frame -= mean
    
#     # make predictions on the frame and then update the predictions
#     # queue
#     preds = model.predict(np.expand_dims(frame, axis=0))[0]
#     print(preds)
#     Q.append(preds)

#     # perform prediction averaging over the current history of
#     # previous predictions

#     results = np.array(Q).mean(axis=0)
#     i = np.argmax(preds)
#     label = labels[i]
#     # draw the activity on the output frame
#     text = "activity: {}:".format(label)
#     cv2.putText(output, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

#     # check if the video writer is None
#     if writer is None:
#         # initialize our video writer
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         writer = cv2.VideoWriter(output_vid, fourcc, 30, (W, H), True)

#     # write the output frame to disk
#     writer.write(output)

#     # show the output image
#     cv2.imshow("Output",output)
#     key = cv2.waitKey(1) & 0xFF

#     # if the `q` key was pressed, break from the loop
#     if key == ord("q"):
#         break
        
# # release the file pointers
# print("[INFO] cleaning up...")
# writer.release()
# vs.release()











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

# def process_video(payload):
#     input_vid = payload['video']
#     print(input_vid,"input_vid")
#     output_vid ="test.mp4"
#     size=128
#     labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
#     Q = deque(maxlen=size)

#     vs = cv2.VideoCapture(input_vid)
#     writer = None
#     (W, H) = (None, None)

#     while True:
#         (grabbed, frame) = vs.read()

#         if not grabbed:
#             break
#         if frame is None:
#             continue    
#         if W is None or H is None:
#             (H, W) = frame.shape[:2]
        
#         output = frame.copy()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame = frame/255.0
#         frame = cv2.resize(frame, (299,299)).astype("float32")

#         preds = model.predict(np.expand_dims(frame, axis=0))[0]
#         Q.append(preds)

#         results = np.array(Q).mean(axis=0)

#         for i, (label, score) in enumerate(zip(labels, results)):
#             cv2.putText(output, f"{label}: {score:.2f}", (35, 50 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

#         i = np.argmax(results)
#         label = labels[i]

#         if results[i] > 0.25:
#             text = "activity: {}:".format(label)
#             cv2.putText(output, text, (35, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

#         if writer is None:
#             fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#             writer = cv2.VideoWriter(output_vid, fourcc, 30, (W, H), True)

#         # writer.write(output)

#         # cv2.imshow("Output",output)
#         key = cv2.waitKey(1) & 0xFF

#         if key == ord("q"):
#             break

#     print("[INFO] cleaning up...")
#     writer.release()
#     vs.release()
#     return "TRUE"

# def process_video(payload, safetyConfig):
#     input_vid = payload['video']
#     size = 128
#     labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
#     Q = deque(maxlen=size)
#     filename = input_vid.filename
#     safetyConfig = json.loads(safetyConfig)
#     print(safetyConfig,"safetyConfig")
#     # Save the uploaded video file to a temporary location
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         temp_file_path = temp_file.name
#         input_vid.file.seek(0)  # Ensure the file cursor is at the beginning
#         temp_file.write(input_vid.file.read())

#     vs = cv2.VideoCapture(temp_file_path)
#     writer = None
#     (W, H) = (None, None)
#     videoAnalyze = {}
#     while True:
#         (grabbed, frame) = vs.read()

#         if not grabbed:
#             break
#         if frame is None:
#             continue
#         if W is None or H is None:
#             (H, W) = frame.shape[:2]

#         output = frame.copy()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame = frame / 255.0
#         frame = cv2.resize(frame, (299, 299)).astype("float32")

#         preds = model.predict(np.expand_dims(frame, axis=0))[0]
#         Q.append(preds)

#         results = np.array(Q).mean(axis=0)

#         for i, (label, score) in enumerate(zip(labels, results)):
#             cv2.putText(output, f"{label}: {score:.2f}", (35, 50 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1.25,
#                         (0, 255, 0), 5)

#         i = np.argmax(results)
#         label = labels[i]

#         if results[i] > safetyConfig[label]:
#             # Apply blurring to the frame
#             output = cv2.GaussianBlur(output, (101, 101), 0)

#         if results[i] > 0.25:
#             text = "activity: {}:".format(label)
#             cv2.putText(output, text, (35, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

#         # FOR SAVING TO DISK
#         if writer is None:
#             output_vid = f"{filename}_output.mp4"
#             fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#             writer = cv2.VideoWriter(output_vid, fourcc, 30, (W, H), True)
#         writer.write(output)

#         # key = cv2.waitKey(1) & 0xFF

#         # if key == ord("q"):
#         #     break

#     print("[INFO] cleaning up...")
#     writer.release()
#     vs.release()
#     # Assuming temp_file_path is the path to your temporary video file
#     with open(temp_file_path, 'rb') as f:
#         video_bytes = f.read()
#     video_base64 = base64.b64encode(video_bytes).decode('utf-8')
    
#     # Prepare the response
#     for i, label in enumerate(labels):
#         videoAnalyze[label] = float(results[i])  # Convert numpy.float32 to float

#     response = {
#         "videoAnalyze": videoAnalyze,
#         "BlurredVideo": video_base64
#     }
#     # Delete the temporary file
#     os.remove(temp_file_path)

#     # return FileResponse(output_vid, media_type="video/mp4", filename=output_vid)
#     return response


def process_video(payload, safetyConfig):
    input_vid = payload['video']
    size = 128
    labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
    Q = deque(maxlen=size)
    filename = input_vid.filename
    safetyConfig = json.loads(safetyConfig)
    print(safetyConfig, "safetyConfig")
    
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

        print("[INFO] cleaning up...")
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

    # test(video_base64)
    os.remove(temp_file_path)  # Clean up the temporary input file
    return response
        
def test(video_base64):
    # Decode the Base64 string
    video_data = base64.b64decode(video_base64)

    # Write the data to an MP4 file
    with open('output_video.mp4', 'wb') as video_file:
        video_file.write(video_data)

    print("Video has been written to output_video.mp4")
    
        
        
## FOR IMAGES

# import cv2
# import numpy as np
# from collections import deque
# import warnings
# warnings.filterwarnings("ignore")
# import tensorflow as tf
# import tensorflow_hub as hub

# model_path = "nsfw.299x299.h5"
# model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
# labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
# size = 128
# input_img = "rko.jpg"
# output_img = "rko1.jpg"

# # Mean Subtraction
# # mean = np.array([123.68, 116.779, 103.939][::1], dtype="float32")
# Q = deque(maxlen=size)

# # Load and preprocess the input image
# image = cv2.imread(input_img)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# image = image / 255.0
# image = cv2.resize(image, (299, 299)).astype("float32")
# # image -= mean

# # Make predictions on the input image
# preds = model.predict(np.expand_dims(image, axis=0))[0]
# Q.append(preds)
# print(preds,"preds")
# # Perform prediction averaging over the current history of previous predictions
# results = np.array(Q).mean(axis=0)

# # Define your labels
# labels = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

# # Create a blank output image
# output = np.zeros_like(image)

# # Draw the scores for all classes on the output image
# for i, (label, score) in enumerate(zip(labels, results)):
#     cv2.putText(output, f"{label}: {score:.2f}", (35, 50 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

# # Find the label with the highest score
# i = np.argmax(results)
# label = labels[i]

# # If the highest score is above 0.25, draw the label on the output image
# if results[i] > 0.25:
#     text = "activity: {}:".format(label)
#     cv2.putText(output, text, (35, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 255, 0), 5)

# # Save the output image
# cv2.imwrite(output_img, output)

# # Show the output image
# cv2.imshow("Output", output)
# cv2.waitKey(0)
# cv2.destroyAllWindows()