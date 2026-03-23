# # USAGE
# # python mask_detect_video.py --video your_video.mp4
# import tensorflow as tf
# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# from tensorflow.keras.preprocessing.image import img_to_array
# from tensorflow.keras.models import load_model
# import numpy as np
# import argparse
# import cv2
# import os

# def mask_video():

#     # construct the argument parser and parse the arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-f", "--face", type=str, default="face_detector",
#                         help="Path to face detector model directory")
#     parser.add_argument("-m", "--model", type=str, default="mask_detector.model",
#                         help="Path to trained face mask detector model")
#     parser.add_argument('-s', '--size', type=int, default=64,
#                         help="Size of face image")
#     parser.add_argument("-c", "--confidence", type=float, default=0.5,
#                         help="Minimum probability to filter weak detections")
#     parser.add_argument("-v", "--video", type=str,
#                         help="Path to input video file")
#     args = parser.parse_args()
#     # Suppress TensorFlow INFO-level messages
#     import tensorflow as tf
#     tf.get_logger().setLevel('ERROR')  # or 'WARNING' or 'INFO'

#     # load our serialized face detector model from disk
#     prototxtPath = os.path.sep.join([args.face, "deploy.prototxt"])
#     weightsPath = os.path.sep.join([args.face, "res10_300x300_ssd_iter_140000.caffemodel"])
#     net = cv2.dnn.readNet(prototxtPath, weightsPath)

#     # load the face mask detector model from disk
#     model = load_model(args.model)

#     # initialize the video stream
#     if args.video:
#         vs = cv2.VideoCapture(args.video)
#     else:
#         print("[ERROR] No video file provided.")
#         return

#     while True:
#         # grab the frame from the video stream
#         (grabbed, frame) = vs.read()

#         # if the frame was not grabbed, then we have reached the end
#         # of the stream
#         if not grabbed:
#             break

#         # detect faces in the frame
#         detect_and_draw(frame, net, model, args)

#         # show the output frame
#         cv2.imshow("Frame", frame)

#         # break the loop if the 'q' key is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # release the video stream and close any open windows
#     vs.release()
#     cv2.destroyAllWindows()

# def detect_and_draw(frame, net, model, args):
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, mean=(104.0, 177.0, 123.0))

#     net.setInput(blob)
#     detections = net.forward()

#     for i in range(0, detections.shape[2]):
#         confidence = detections[0, 0, i, 2]
#         if confidence < args.confidence:
#             # Drop low confidence detections
#             continue

#         box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#         (startX, startY, endX, endY) = box.astype("int")
#         (startX, startY) = (max(0, startX), max(0, startY))
#         (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

#         try:
#             face = frame[startY:endY, startX:endX]
#             face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
#             face = cv2.resize(face, (args.size, args.size))
#             face = img_to_array(face)
#             face = preprocess_input(face)
#             face = np.expand_dims(face, axis=0)

#             mask = model.predict(face)[0]

#             label = "Mask" if mask < 0.5 else "No Mask"
#             color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
#             # display the label and bounding box rectangle on the output frame
#             cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
#             cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
#         except Exception as e:
#             print(e)

# if __name__ == "__main__":
#     mask_video()


# # USAGE
# # python mask_detect_video.py --video your_video.mp4
# import tensorflow as tf
# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# import numpy as np
# import argparse
# import cv2
# import os

# def mask_video():
#     # construct the argument parser and parse the arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-f", "--face", type=str, default="face_detector",
#                         help="Path to face detector model directory")
#     parser.add_argument("-m", "--model", type=str, default="mask_detector.model",
#                         help="Path to trained face mask detector model")
#     parser.add_argument('-s', '--size', type=int, default=64,
#                         help="Size of face image")
#     parser.add_argument("-c", "--confidence", type=float, default=0.5,
#                         help="Minimum probability to filter weak detections")
#     parser.add_argument("-v", "--video", type=str,
#                         help="Path to input video file")
#     args = parser.parse_args()
#     # Suppress TensorFlow INFO-level messages
#     import tensorflow as tf
#     tf.get_logger().setLevel('ERROR')  # or 'WARNING' or 'INFO'

#     # load our serialized face detector model from disk
#     prototxtPath = os.path.sep.join([args.face, "deploy.prototxt"])
#     weightsPath = os.path.sep.join([args.face, "res10_300x300_ssd_iter_140000.caffemodel"])
#     net = cv2.dnn.readNet(prototxtPath, weightsPath)

#     # initialize the video stream
#     if args.video:
#         vs = cv2.VideoCapture(args.video)
#     else:
#         print("[ERROR] No video file provided.")
#         return

#     while True:
#         # grab the frame from the video stream
#         (grabbed, frame) = vs.read()

#         # if the frame was not grabbed, then we have reached the end
#         # of the stream
#         if not grabbed:
#             break

#         # detect faces in the frame
#         detect_and_draw(frame, net, args)

#         # show the output frame
#         cv2.imshow("Frame", frame)

#         # break the loop if the 'q' key is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # release the video stream and close any open windows
#     vs.release()
#     cv2.destroyAllWindows()

# def detect_and_draw(frame, net, args):
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, mean=(104.0, 177.0, 123.0))

#     net.setInput(blob)
#     detections = net.forward()

#     for i in range(0, detections.shape[2]):
#         confidence = detections[0, 0, i, 2]
#         if confidence < args.confidence:
#             # Drop low confidence detections
#             continue

#         box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#         (startX, startY, endX, endY) = box.astype("int")
#         (startX, startY) = (max(0, startX), max(0, startY))
#         (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

#         # draw a dark pink solid rectangle around the detected face
#         frame[startY:endY, startX:endX, :] = (136, 28, 238)

# if __name__ == "__main__":
#     mask_video()

# import tensorflow as tf
# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# import numpy as np
# import argparse
# import cv2
# import os

# def mask_video():
#     # construct the argument parser and parse the arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-f", "--face", type=str, default="face_detector",
#                         help="Path to face detector model directory")
#     parser.add_argument("-m", "--model", type=str, default="mask_detector.model",
#                         help="Path to trained face mask detector model")
#     parser.add_argument('-s', '--size', type=int, default=64,
#                         help="Size of face image")
#     parser.add_argument("-c", "--confidence", type=float, default=0.5,
#                         help="Minimum probability to filter weak detections")
#     parser.add_argument("-v", "--video", type=str,
#                         help="Path to input video file")
#     parser.add_argument("-o", "--output", type=str, default="output.mp4",
#                         help="Path to save the output video file with .mp4 extension")
#     args = parser.parse_args()
#     # Suppress TensorFlow INFO-level messages
#     import tensorflow as tf
#     tf.get_logger().setLevel('ERROR')  # or 'WARNING' or 'INFO'

#     # load our serialized face detector model from disk
#     prototxtPath = os.path.sep.join([args.face, "deploy.prototxt"])
#     weightsPath = os.path.sep.join([args.face, "res10_300x300_ssd_iter_140000.caffemodel"])
#     net = cv2.dnn.readNet(prototxtPath, weightsPath)

#     # initialize the video stream
#     if args.video:
#         vs = cv2.VideoCapture(args.video)
#     else:
#         print("[ERROR] No video file provided.")
#         return

#     # Define the codec and create a VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(args.output, fourcc, 20.0, (int(vs.get(3)), int(vs.get(4))))

#     while True:
#         # grab the frame from the video stream
#         (grabbed, frame) = vs.read()

#         # if the frame was not grabbed, then we have reached the end
#         # of the stream
#         if not grabbed:
#             break

#         # detect faces in the frame
#         detect_and_draw(frame, net, args)

#         # write the output frame to the video file
#         out.write(frame)

#     # release the video stream and close any open windows
#     vs.release()
#     out.release()
#     cv2.destroyAllWindows()

# def detect_and_draw(frame, net, args):
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, mean=(104.0, 177.0, 123.0))

#     net.setInput(blob)
#     detections = net.forward()

#     for i in range(0, detections.shape[2]):
#         confidence = detections[0, 0, i, 2]
#         if confidence < args.confidence:
#             # Drop low confidence detections
#             continue

#         box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#         (startX, startY, endX, endY) = box.astype("int")
#         (startX, startY) = (max(0, startX), max(0, startY))
#         (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

#         # draw a dark pink solid rectangle around the detected face
#         frame[startY:endY, startX:endX, :] = (136, 28, 238)

# if __name__ == "__main__":
#     mask_video()



# import tensorflow as tf
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# import numpy as np
# import cv2
# import os
# from werkzeug.datastructures import FileStorage  # Use this if you're using Flask for handling file uploads

# def mask_video(video, output_path="output.mp4"):
#     # Suppress TensorFlow INFO-level messages
#     # tf.get_logger().setLevel('ERROR')  # or 'WARNING' or 'INFO'
#     face_path="privacy/util/face_detect/face_detector"
#     model_path="privacy/util/face_detect/results/Xception-size-64-bs-32-lr-0.0001.h5" 
#     size=64
#     confidence=0.5
#     # Load our serialized face detector model from disk
#     prototxtPath = os.path.sep.join([face_path, "deploy.prototxt"])
#     weightsPath = os.path.sep.join([face_path, "res10_300x300_ssd_iter_140000.caffemodel"])
#     net = cv2.dnn.readNet(prototxtPath, weightsPath)
#     print("STARTED")
#     # If video is a FileStorage object, save it to a temporary file
#     if isinstance(video, FileStorage):
#         video_path = "temp_video.mp4"
#         video.save(video_path)
#     else:
#         video_path = video  # Assume it's already a file path

#     # Initialize the video stream
#     vs = cv2.VideoCapture(video_path)

#     # Define the codec and create a VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(vs.get(3)), int(vs.get(4))))

#     while True:
#         # Grab the frame from the video stream
#         (grabbed, frame) = vs.read()

#         # If the frame was not grabbed, we have reached the end of the stream
#         if not grabbed:
#             break

#         # Detect faces in the frame
#         detect_and_draw(frame, net, size, confidence)

#         # Write the output frame to the video file
#         out.write(frame)

#     # Release the video stream and close any open windows
#     vs.release()
#     out.release()
#     cv2.destroyAllWindows()

#     # If a temporary video file was created, remove it
#     if isinstance(video, FileStorage):
#         os.remove(video_path)

# def detect_and_draw(frame, net, size, confidence):
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, mean=(104.0, 177.0, 123.0))

#     net.setInput(blob)
#     detections = net.forward()

#     for i in range(0, detections.shape[2]):
#         conf = detections[0, 0, i, 2]
#         if conf < confidence:
#             # Drop low confidence detections
#             continue

#         box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#         (startX, startY, endX, endY) = box.astype("int")
#         (startX, startY) = (max(0, startX), max(0, startY))
#         (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

#         # Draw a dark pink solid rectangle around the detected face
#         frame[startY:endY, startX:endX, :] = (136, 28, 238)


