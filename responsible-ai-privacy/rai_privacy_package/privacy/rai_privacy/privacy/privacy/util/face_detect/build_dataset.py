from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from privacy.config.logger import CustomLogger
import numpy as np
import argparse
import cv2
import os

import argparse
import random
import os

from tqdm import tqdm
log=CustomLogger()
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data-dir', default='data/dataset_raw', 
                    help="Directory with the raw dataset")
parser.add_argument('-o', '--output-dir', default='data/64x64_dataset', 
                    help="Where to write the new data")
parser.add_argument('-s', '--size', type=int, default=64, 
                    help="Where to write the new data")
parser.add_argument('-c', '--confidence', type=float, default=0.5, 
                    help="Confidence threshold to detect face")
parser.add_argument('--face-model', type=str, default="face_detector", 
                    help="path to face detector model directory")

def extract_face(filename, output_dir, net, size, confidence_threshold):
    image = cv2.imread(filename)
    if image is None:
        return

    filename_out = filename.split('/')[-1].split('.')[0]
    (h, w) = image.shape[:2]

    blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size=(128, 128), mean=(104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            try:
                frame = image[startY:endY, startX:endX]
                frame = cv2.resize(frame, (size, size), interpolation=cv2.INTER_AREA)
                if i > 0:
                    image_out = os.path.join(output_dir, '%s_%s.jpg' % (filename_out, i))
                else:
                    image_out = os.path.join(output_dir, '%s.jpg' % filename_out)
                cv2.imwrite(image_out, frame)
            except Exception as e:
                 log.error(str(e))
                 log.error("Line No:"+str(e.__traceback__.tb_lineno))

def app():
    args = parser.parse_args()

    assert os.path.isdir(args.data_dir), "Couldn't find the dataset at {}".format(args.data_dir)

    prototxtPath = os.path.join(args.face_model, "deploy.prototxt")
    weightsPath = os.path.join(args.face_model, "res10_300x300_ssd_iter_140000.caffemodel")
    net = cv2.dnn.readNet(prototxtPath, weightsPath)

    # Define the data directories
    train_mask_dir = os.path.join(args.data_dir, 'train/Mask')
    train_non_mask_dir = os.path.join(args.data_dir, 'train/Non Mask')
    os.makedirs(train_mask_dir, exist_ok=True)
    os.makedirs(train_non_mask_dir, exist_ok=True)

    test_mask_dir = os.path.join(args.data_dir, 'test/Mask')
    test_non_mask_dir = os.path.join(args.data_dir, 'test/Non Mask')
    os.makedirs(test_mask_dir, exist_ok=True)
    os.makedirs(test_non_mask_dir, exist_ok=True)

    # Get the filenames in each directory (train and test)
    filenames_mask = os.listdir(train_mask_dir)
    filenames_mask = [os.path.join(train_mask_dir, f) for f in filenames_mask if f.endswith('.jpg')]

    filenames_non_mask = os.listdir(train_non_mask_dir)
    filenames_non_mask = [os.path.join(train_non_mask_dir, f) for f in filenames_non_mask if f.endswith('.jpg')]

    test_filenames_mask = os.listdir(test_mask_dir)
    test_filenames_mask = [os.path.join(test_mask_dir, f) for f in test_filenames_mask if f.endswith('.jpg')]

    test_filenames_non_mask = os.listdir(test_non_mask_dir)
    test_filenames_non_mask = [os.path.join(test_non_mask_dir, f) for f in test_filenames_non_mask if f.endswith('.jpg')]

    # Split the images into 80% train and 20% dev
    # Make sure to always shuffle with a fixed seed so that the split is reproducible
    filenames_mask.sort()
    filenames_non_mask.sort()
    random.shuffle(filenames_mask)
    random.shuffle(filenames_non_mask)

    split_mask = int(0.8 * len(filenames_mask))
    train_filenames_mask = filenames_mask[:split_mask]
    dev_filenames_mask = filenames_mask[split_mask:]

    split_non_mask = int(0.8 * len(filenames_non_mask))
    train_filenames_non_mask = filenames_non_mask[:split_non_mask]
    dev_filenames_non_mask = filenames_non_mask[split_non_mask:]

    filenames = {'train/Mask': train_filenames_mask,
                 'train/Non Mask': train_filenames_non_mask,
                 'test/Mask': test_filenames_mask,
                 'test/Non Mask': test_filenames_non_mask,
                 'validation/Mask': dev_filenames_mask,
                 'validation/Non Mask': dev_filenames_non_mask}

    # Preprocess train, dev and test
    for split in filenames.keys():
        output_dir_split = os.path.join(args.output_dir, split)
        os.makedirs(output_dir_split, exist_ok=True)

        print("Processing {} data, saving preprocessed data to {}".format(split, output_dir_split))
        for filename in tqdm(filenames[split]):
            extract_face(filename, output_dir_split, net, args.size, args.confidence)

    print("Done building dataset")


if __name__ == '__main__':
    app()
