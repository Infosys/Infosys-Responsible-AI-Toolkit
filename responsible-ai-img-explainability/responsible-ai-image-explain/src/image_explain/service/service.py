'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import gc
from image_explain.utils.metrics.aesthetic_score import AestheticScore
from image_explain.utils.metrics.alignment_score import AlignmentScore
from image_explain.service.responsible_ai_image_explain import ImageExplain
from image_explain.mappers.mappers import AnalyzeResponse, ObjectDetectionResponse
from image_explain.config.logger import CustomLogger
from image_explain.utils.prompts.base import Prompt
from mimetypes import guess_type
import concurrent.futures
from PIL import Image
import requests
import shutil
import base64
import math
import time
import uuid
import cv2
import os
import json

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

path="../image"

class ImageService:

    @staticmethod
    def read_image_base64(image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('ascii')
        
    @staticmethod
    def nd_array_to_base64(image):
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    @staticmethod
    def scale_value(value, x_min, x_max, a=1, b=100):
        return a + ((value - x_min) / (x_max - x_min)) * (b - a)
    
    @staticmethod
    def analyze_image_bias(mime_type, image_base64, evaluator):
        return ImageExplain.image_based_bias_analysis(mime_type=mime_type, image=image_base64, evaluator=evaluator)

    @staticmethod
    def detect_bias(image_path, prompt, mime_type):
        try:
            URL = os.getenv("BIAS_DETECTION_API")
            with open(image_path, 'rb') as image_file:
                response = requests.request(
                    "POST", 
                    url=URL, 
                    data={"prompt": prompt, "evaluator": "GPT_4o"}, 
                    files={'image': (os.path.basename(image_path), image_file, mime_type)}
                )

            # Check if the response status code is 200 OK
            if response.status_code == 200:
                return response.json()
            else:
                # Return a dictionary with empty strings for the keys "Analysis" and "Bias type(s)"
                return {"Analysis": "No bias identified", "Bias type(s)": "No bias"}
        except Exception as e:
            return None

    @staticmethod
    def prompt_based_analysis_task(mime_type, image_base64, prompt, evaluator):
        return ImageExplain.prompt_based_analysis(mime_type=mime_type, image=image_base64, prompt=prompt, evaluator=evaluator)

    @staticmethod
    def get_aesthetic_score(image_path):
        return AestheticScore.score(image_path=image_path)
    
    @staticmethod
    def get_alignment_score(image_path, text):
        return AlignmentScore.score(image_path=image_path, text=text)
    
    @staticmethod
    def query_based_image_analysis(generated_image_base64, mime_type, prompt, evaluator):
        return ImageExplain.query_based_image_analysis(image_base64=generated_image_base64, mime_type=mime_type, prompt=prompt, evaluator=evaluator)
    
    @staticmethod
    def get_uncertainity_score(prompt, mime_type, generated_image_base64, evaluator):
        prompt = Prompt.uncertainty_template(input=prompt)
        return ImageExplain.uncertainity_score(prompt=prompt,mime_type=mime_type, image=generated_image_base64, evaluator=evaluator)
    
    @staticmethod
    def extract_object(image_path, bounding_box):
        """
        Extracts an object from an image based on bounding box coordinates.

        Parameters:
        - image_path (str): Path to the input image.
        - bounding_box (tuple): Bounding box coordinates in the format (x, y, width, height).

        Returns:
        - cropped_image (numpy.ndarray): The extracted object as an image.
        """
        # Read the image
        image = cv2.imread(image_path)

        # Ensure the image was loaded
        if image is None:
            raise ValueError("Image not found or unable to read.")

        # Extract bounding box coordinates
        x, y, w, h = bounding_box

        # Crop the region of interest (ROI) using the bounding box
        cropped_image = image[y:y+h, x:x+w]

        return cropped_image
    
    @staticmethod
    def extract_coordinates_as_int(boxes):
        """
        Extracts bounding box coordinates (xyxy format) as a list of tuples with integer values.

        Parameters:
        - boxes: The ultralytics.engine.results.Boxes object.

        Returns:
        - List of tuples containing bounding box coordinates (x_min, y_min, x_max, y_max) as integers.
        """
        # Convert the tensor to a numpy array and then to a list of tuples with int values
        coordinates = [tuple(map(int, coord.tolist())) for coord in boxes.xyxy]
        return coordinates

    def analyze_image(payload) -> AnalyzeResponse:
        # Validate the payload
        if "image" not in payload or "evaluator" not in payload:
            raise ValueError("Invalid payload. Please provide image & evaluator name.")
        
        try:
            # Extract the payload
            prompt = payload.get("prompt", None)
            image = payload["image"]
            evaluator = payload["evaluator"]
            query_flag = payload.get("query_flag", False)

            # Open the image file
            imageName = image.filename
            imageFile = image.file
            uuid_value = str(uuid.uuid4())
            imageContent = Image.open(imageFile)

            # Save the image to a temporary directory
            os.makedirs(f"{path}/{uuid_value}", exist_ok=True)
            image_path = f"{path}/{uuid_value}/{imageName}"
            imageContent.save(image_path)

            # Read the image content as base64
            generated_image_base64 = ImageService.read_image_base64(image_path)
            mime_type, _ = guess_type(image_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            # Dictionary mapping method names to their arguments
            method_args = {
                'analyze_image_bias': (mime_type, generated_image_base64, evaluator),
                'detect_bias': (image_path, prompt, mime_type),
                'prompt_based_analysis_task': (mime_type, generated_image_base64, prompt, evaluator),
                'get_aesthetic_score': (image_path,),
                'get_alignment_score': (image_path, prompt),
                'query_based_image_analysis': (generated_image_base64, mime_type, prompt, evaluator),
            }


            # List of method names to be executed
            method_names = [
                    'prompt_based_analysis_task',
                    'get_aesthetic_score',
                ]
            if prompt is None:
                method_names.append('analyze_image_bias')
            elif query_flag and prompt is not None and prompt != "":
                method_names.append('detect_bias')
                method_names.append('get_alignment_score')
                method_names.append('query_based_image_analysis')
            else:
                method_names.append('detect_bias')
                method_names.append('get_alignment_score')

            # Execute tasks in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit tasks to be executed in parallel
                futures = {executor.submit(getattr(ImageService, method_name), *method_args[method_name]): method_name for method_name in method_names}

                # Wait for the results and collect them dynamically
                results = {}
                for future in concurrent.futures.as_completed(futures):
                    method_name = futures[future]
                    try:
                        results[method_name] = future.result()
                    except Exception as e:
                        results[method_name] = f"An error occurred: {e}"

            # Access the results dynamically
            bias_response = results.get('detect_bias') or results.get('analyze_image_bias')
                
            if isinstance(bias_response, str) and bias_response is not None:
                bias_response = json.loads(bias_response)
            
            response = results.get('prompt_based_analysis_task')
            aes_score = results.get('get_aesthetic_score')
            alignment_score = results.get('get_alignment_score')
            query_bases_response = results.get('query_based_image_analysis')
            
            if prompt is not None and prompt != "":
                uncertainity = ImageService.get_uncertainity_score(prompt, mime_type, generated_image_base64, evaluator)
            else:
                uncertainity= ImageService.get_uncertainity_score(response, mime_type, generated_image_base64, evaluator)
            
            score = uncertainity['uncertainty_score']['score']
            uncertainity_score= uncertainity['uncertainty_score']
            if uncertainity is not None:
                uncertainity_label = 'Highly certain' if score < 35 else 'Moderately certain' if score < 70 else 'Less certain'
                metrics = {
                    "certainity_score": score,
                    "certainity_label": uncertainity_label
                }

            if prompt is None:
                method_names.append('certainity_score')
            else:
                method_names.append('certainity_score')

            if aes_score is not None and query_flag == False:
                # Scale the scores to a range of 1-100
                scaled_aes_score = ImageService.scale_value(value=aes_score, x_min=0, x_max=10)
                creativity_label = 'Less Creative' if scaled_aes_score < 35 else 'Moderately Creative' if scaled_aes_score < 70 else 'Highly Creative'
                metrics["creativity_score"] = math.ceil(scaled_aes_score)
                metrics["creativity_label"] = creativity_label
            
            if alignment_score is not None and prompt is not None and prompt != "":
                scaled_alignment_score = ImageService.scale_value(value=alignment_score, x_min=-1, x_max=1)
                coherence_label = 'Less coherence' if scaled_alignment_score < 35 else 'Moderately coherence' if scaled_alignment_score < 70 else 'Highly coherence'

                metrics["coherence_score"] = math.ceil(scaled_alignment_score)
                metrics["coherence_label"] = coherence_label
                            
            response_obj = {
                'image_description': response['ImageDescription'],
                'insights': {
                    "watermark": response['WatermarkContent'],
                    "style": response['Style'],
                    "style_analysis": response['StyleAnalysis'],
                    "query_response": query_bases_response['Response'] if query_bases_response else "NA"
                },
                'metrics': metrics,
                'super_pixels': ''  # img_seg_base64
            }

            if bias_response is not None:
                response_obj['insights'].update({
                    "bias_type": bias_response['Bias type(s)'],
                    "bias_analysis": bias_response['Analysis']
                })


            return AnalyzeResponse(**response_obj)
        except requests.RequestException as re:
            log.error(f"UUID: {uuid_value}, Request error: {re}", exc_info=True)
            raise RuntimeError(f"Error during bias detection request: {re}")
        except Exception as e:
            log.error(f"UUID: {uuid_value}, Unexpected error: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred: {e}")
        finally:
            try:
                shutil.rmtree(f"{path}/{uuid_value}")
            except Exception as e:
                log.error(f"UUID: {uuid_value}, Error cleaning up temporary files: {e}", exc_info=True)
                raise
            # Clear memory
            if image is not None:
                del image
            if imageContent is not None:
                del imageContent
            if futures is not None:
                del futures
            if results is not None:
                del results
            if executor is not None:
                executor.shutdown(wait=False)
                del executor
            gc.collect()
    
    def object_detection_img(payload) -> ObjectDetectionResponse:
        # Validate the payload
        if "image" not in payload or "evaluator" not in payload:
            raise ValueError("Invalid payload. Please provide image & evaluator name.")
        
        if 'llama' not in payload["evaluator"].lower() and 'gpt' not in payload["evaluator"].lower() and 'gemini' not in payload["evaluator"].lower():
                raise ValueError("Currently supporting GPT-4o & Llama & Gemini models only.")

        
        try:
            # Extract the payload
            image = payload["image"]
            evaluator = payload["evaluator"]

            # Open the image file
            imageName = image.filename
            imageFile = image.file
            uuid_value = str(uuid.uuid4())
            imageContent = Image.open(imageFile)

            # Save the image to a temporary directory
            os.makedirs(f"{path}/{uuid_value}", exist_ok=True)
            image_path = f"{path}/{uuid_value}/{imageName}"
            imageContent.save(image_path)

            # Read the image content as base64
            generated_image_base64 = ImageService.read_image_base64(image_path)
            mime_type, _ = guess_type(image_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            if 'gpt' in evaluator.lower():
                mime_type = mime_type
                generated_image_base64 = generated_image_base64
            if 'llama' in evaluator.lower():
                mime_type = None
                generated_image_base64 = image_path

            # Perform analysis on the image
            start_time = time.time()

            def detect_objects():
                if 'llama' in evaluator.lower():
                    prompt = Prompt.detect_objects_slm_prompt()
                else:
                    prompt = Prompt.detect_objects_prompt()
                return ImageExplain.analyze_image(mime_type=mime_type, image=generated_image_base64, prompt=prompt, evaluator=evaluator)

            def get_bounding_boxes():
                if 'llama' in evaluator.lower():
                    prompt = Prompt.bounding_boxes_slm_prompt()
                else:
                    prompt = Prompt.bounding_boxes_prompt()
                return ImageExplain.analyze_image(mime_type=mime_type, image=generated_image_base64, prompt=prompt, evaluator=evaluator)

            # Run the tasks in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_detect_objects = executor.submit(detect_objects)
                future_bounding_boxes = executor.submit(get_bounding_boxes)

                img_objs = future_detect_objects.result()
                img_bounding_boxes = future_bounding_boxes.result()

            if 'gpt' or 'gemini' in evaluator.lower():
                add_objs = list(set(img_bounding_boxes) - set(img_objs))
            elif 'llama' in evaluator.lower():
                add_objs = img_objs + img_bounding_boxes

            if 'llama' in evaluator.lower():
                prompt = Prompt.validate_objects_slm_prompt(img_objs, img_bounding_boxes)
            else:
                prompt = Prompt.validate_objects_prompt(add_objs)
            add_objs_presence = ImageExplain.analyze_image(mime_type=mime_type, image=generated_image_base64, prompt=prompt, evaluator=evaluator)

            prompt = Prompt.obj_detection_exp_prompt(img_objs, img_bounding_boxes, add_objs, add_objs_presence)
            results = ImageExplain.analyze_image(mime_type=None, image=None, prompt=prompt, evaluator=evaluator)

            if 'llama' in evaluator.lower():
                res = results
            elif 'gpt' or 'gemini' in evaluator.lower():
                res = results['explanation']
            end_time = time.time()

            total_time = round(end_time-start_time, 3)
            response = {'explanation': res, 'predicted_image':'', 'time_taken': total_time}

            return ObjectDetectionResponse(**response)
        except Exception as e:
            log.error(f"Error: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred: {e}")
        finally:
            try:
                if uuid_value:
                    shutil.rmtree(f"{path}/{uuid_value}")
            except Exception as e:
                log.error(f"UUID: {uuid_value}, Error cleaning up temporary files: {e}", exc_info=True)
                raise
            gc.collect()