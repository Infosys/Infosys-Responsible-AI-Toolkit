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

from image_explain.utils.prompts.output_format import *
from image_explain.utils.prompts.few_shot import *

class Prompt:
        
    def image_analyze_prompt():
        template = f'''
            You are a detail-oriented LLM which pays close attention to the details. You are given a prompt and an image. Your job is to evaluate the image and provide a detailed analysis of the image.

            Please provide:
            1. Image Description: A detailed description of the elements present in the image, including key features, objects, colors, and any notable aspects.
            2. Style: Analyze the style of the given image and classify it to a style that resembles the image. Some of the example styles are Cartoon, Anime, Graphic Novel, Digital Art, Pixel Art, Abstract, Pop Art, Minimalism, etc., you can assign style from these or other style that is suitable to the image. Consider key visual elements such as line quality, color palette, texture, shading, composition, and any unique characteristics or cultural references that define its style. If the image mixes styles, identify and describe each contributing style. Also, provide reasoning on why the image the assigned specific style.
            3. Watermark Content: Extract the text or symbols from the detected watermark.

            Example Data:
            {IMAGE_ANALYZE_EXAMPLE}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {IMAGE_ANALYZE_OUTPUT_FORMAT}

        '''
        return template

    def analyze_bias_without_prompt():
        template = f'''
            You are an evaluator tasked to identify all potential bias(es) in the Image. Analyze the image and identify all possible potential bias(es) in it. Prioritize Human based biases over other types of biases. Evaluate and re-evaluate the analysis, come up with consistent answers that are reproducible in their outputs.

            Please analyze the following:
            1. Analysis: The analysis for the bias identified,
            2. Bias type(s): The bias type(s) which have been identified,
            3. Previledged group(s) : The group(s) that are favored by the bias,
            4. Un-Previledged group(s): The group(s) that are ignored by the bias,

            Example data:
            {BIAS_ANALYZE_EXAMPLE}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {BIAS_ANALYZE_OUTPUT_FORMAT}
        '''
        return template
    
    def query_based_image_analysis_prompt(prompt):
        template = f'''
            You are a detail-oriented LLM which pays close attention to the details. You are given a question and an image. 
            Your job is to analyze the given image in detail and provide answer in response to the given question.

            Please provide:
            1. Prompt Response: A response to the question from the image.
           
            Input:
            Question: {prompt}

            Example Data:
            {QUERY_BASED_IMAGE_ANALYSIS_EXAMPLE}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {QUERY_BASED_IMAGE_ANALYSIS_OUTPUT_FORMAT}

        '''
        return template

    def object_detection_img_prompt():
        return f'''
            You will be provided with an image containing bounding boxes drawn around specific objects. Each bounding box includes the object's name and score displayed at its top. Your tasks are as follows:

            1. Bounding Box Extraction: 
            - Identify the number of bounding boxes in the image.
            - Extract and return a list of strings, each representing the name and score associated with a bounding box. Only include objects within the bounding boxes.

            2. Generate Object Detection Explanation: 
            - Create a textual explanation for the detected objects, considering the following:
                - Explain why the YOLO model detected each object as its respective class, including misclassifications (if any).
                - Use grammatically correct sentences and prioritize readability.
                - Aggregate positional details where appropriate (e.g., "bottom-left corner," "bottom," and "bottom-right corner" can be grouped as "bottom"). If positions are too ambiguous, exclude them.
                - If a score is available, provide reasoning for why that score was assigned.
                - Include all detected objects in the explanation, even if some have similar names.

            EXAMPLE OUTPUT FORMAT:
            {OBJECT_DETECTION_EXAMPLE}

            You shoud provide output only in json format.
        '''

    def detect_objects_prompt():
        return """
                TASK: Detect and list all objects present in the given image.
                INPUT: An image containing various entities.
                INSTRUCTIONS:
                1. Identify and list all objects that are visually and clearly present in the image. This includes, but is not limited to, humans, animals, birds, vehicles, non-living things, and signboards.
                2. Focus exclusively on the visual content of the image and ignore any bounding boxes, annotations, or model-detected objects that do not have a clear visual representation.
                3. Do not recognize objects that are artifacts of adversarial noise, partial features, or ambiguous patterns. Only objects that are visually distinct and fully present should be included.
                4. Critically analyze the image content to filter out false positives caused by adversarial manipulations, unusual pixel arrangements, or unclear object outlines.
                5. Provide the output as a list of strings, each string representing the name of a visually confirmed object.
                6. Ensure that your response is based solely on visual evidence, and consistency is maintained for the same image across multiple queries.
                7. Do not generalize your response or do not group similar objects under one name like if there are multiple person's in the image provide persone multiple times in the response but not people.
                Ensure your response is visually accurate and consistent; whenever the same question is asked with the same image, the response should remain unchanged.
                Response should only be in below given format. Make sure you strictly follow the below output format.
                EXAMPLE OUTPUT FORMAT:
                {
                    "objects": ["car", "person", "tree"]
                }
            """
    def detect_objects_slm_prompt():
        return """
            You are a highly capable and detail-oriented Responsible AI Assistant. Your task is to analyze the given image thoroughly and accurately detect all objects present within it. Follow the instructions below to ensure consistency and clarity:
            TASK: Detect and list all objects visually present in the provided image.
            INPUT: An image containing various entities.
            INSTRUCTIONS:
            1. Object Detection:
                - Identify and list all objects that are visually and clearly present in the image. This includes, but is not limited to, humans, animals, birds, vehicles, non-living things, natural elements (e.g., trees, rocks), and man-made structures (e.g., buildings, signboards).
                - Focus exclusively on what is visually observable in the image. Ignore any annotations, bounding boxes, or model-detected objects that do not have a clear visual representation.
            2. Accuracy and Filtering:
                - Exclude objects that appear as artifacts of adversarial noise, partial features, or ambiguous patterns.
                - Only include objects that are visually distinct, complete, and fully present.
                - Critically analyze the image to avoid false positives caused by unclear outlines, unusual pixel arrangements, or potential adversarial manipulations.
                - Do not generalize your response or do not group similar objects under one name like if there are multiple person's in the image provide persone multiple times in the response but not people.
            3. Response Format:
                - Provide your output in a consistent and structured format.
                - Ensure your response is a JSON object containing a single key `"objects"`, where the value is a list of strings representing visually confirmed objects.
                - Example:
                ```json
                {
                "objects": ["car", "dog", "tree"]
                }
                ```
            4. Consistency and Explanation:
                - Ensure your response is consistent; the same image should always yield the same result across multiple queries.
                - Provide results based solely on visual evidence, and exclude any inferred or assumed objects.
            ADDITIONAL REQUIREMENTS:
                - Be unbiased, thorough, and transparent in your detection process.
                - Maintain a neutral tone in your analysis, and do not include any extraneous details or formatting styles (e.g., bold text).
            OUTPUT REQUIREMENTS:
                - The response must strictly adhere to the specified format.
                - Example Output:
                ```json
                {
                "objects": ["cat", "bicycle", "bench"]
                }
        """
    
    def bounding_boxes_prompt():
        return """
                TASK: Extract the names associated with bounding boxes in the given image.
                INPUT: An image with bounding boxes around specific objects, each labeled with a name at its top-left corner.
                INSTRUCTIONS:
                1. Identify and count the total number of bounding boxes present in the image.
                2. Extract and return a list of names displayed at the top-left corner of each bounding box.
                3. Include only the names associated with the bounding boxes. Do not include any names or objects that are not explicitly labeled within the bounding boxes.
                4. Focus solely on the bounding box labels and disregard the visual content of the image itself.
                5. Provide the output as a list of strings, where each string corresponds to the name of an identified bounding box label.
                6. Ensure your response is consistent; the same input should always yield the same output.
                7. Make sure all bounding boxes names are returned, do not miss anything.
                Make sure your response is consistent, whenever I ask the same question your response should be same.
                Response should only be in below given format.
                OUTPUT FORMAT:
                {
                    "bounding_box_labels": ["car", "person", "tree"]
                }
            """
    
    def bounding_boxes_slm_prompt():
        return """
            You are a highly capable and detail-oriented Responsible AI Assistant. Your task is to accurately extract the names associated with bounding boxes from the given image. Follow the instructions below to ensure consistency and clarity:
            TASK: Extract and list the names associated with bounding boxes in the provided image.
            INPUT: An image containing bounding boxes around specific objects, each labeled with a name at the top-left corner of the bounding box.
            INSTRUCTIONS:
            1. Bounding Box Identification:
                - Identify and count all the bounding boxes present in the image. Each bounding box has a label displayed at its top-left corner.
                - Focus exclusively on the labels of the bounding boxes and disregard the visual content of the objects inside the boxes.
            2. Name Extraction:
                - Extract the names of the objects associated with the bounding boxes. Only include names that are explicitly labeled at the top-left corner of the boxes.
                - Do not infer names based on visual content or include any names that are not directly linked to the bounding boxes.
            3. Filtering:
                - Avoid including any objects that are not clearly labeled within the bounding boxes.
                - Ignore any noise, ambiguity, or labels that do not belong to a bounding box.
                - Do not mention scores or confidence scores of objects in the response.
            4. Response Format:
                - Provide your output in a structured and consistent JSON format.
                - The output should include a single key `"bounding_box_labels"`, where the value is a list of strings representing the names associated with each bounding box.
                Example output:
                ```json
                {{
                "bounding_box_labels": ["car", "person", "tree"]
                }}
                ```
            5. Consistency and Explanation:
                - Ensure your response is consistent; the same image should always yield the same output across multiple queries.
                - Base your results solely on the labels within the bounding boxes and exclude any inferred or unlabelled objects.
            ADDITIONAL REQUIREMENTS:
                - Be unbiased, thorough, and transparent in your extraction process.
                - Maintain a neutral tone and avoid including any extraneous details or formatting styles (e.g., bold text).
            OUTPUT REQUIREMENTS:
                - The response must strictly adhere to the specified format.
                - Example Output:
                ```json
                {{
                "bounding_box_labels": ["car", "person", "tree"]
                }}
                ```
            Do not provide any description in the response, just the json is required.
        """
    
    def validate_objects_prompt(objects):
        return f"""
                TASK: Verify the presence of specific objects in the given image.
                
                INPUT: 
                1. Analyze the image visually to verify whether the objects in the provided list are genuinely present.
                2. A list of object names to verify ["List of object names to verify"].
                
                INSTRUCTIONS:
                1. Analyze the image visually to verify whether the objects in the provided list are genuinely present.
                2. Disregard any bounding boxes, annotations, or labels in the image. Base your analysis solely on the natural appearance of objects in the image.
                3. Be cautious of adversarial patterns. If the visual evidence of an object appears ambiguous or inconsistent (e.g., pixel-level artifacts mimicking an object), do not classify it as present. Only confirm objects that are visually distinct and natural.
                4. Do not infer or guess the presence of objects. Only verify objects based on clear and unaltered visual cues in the image.
                5. For each object in the provided list, return `True` if it is visually present and distinct, and `False` otherwise.
                6. Ensure that your response is consistent for the same input, and do not let adversarial patterns influence your analysis.
                
                INPUT LIST: {objects}

                Make sure your response is consistent, whenever I ask the same question your response should be same.
                
                OUTPUT FORMAT:
                Provide a list of boolean values corresponding to the input list, where `True` indicates the object is present and `False` indicates it is not.
                Do not provide anything list of boolean values.
                
                EXAMPLE:
                {{
                    "object_presence": ["True", "False", "True"]
                }}
            """
    
    def validate_objects_slm_prompt(img_objs, img_bounding_boxes):
        return f"""
                TASK: Verify the presence of objects in the given image.
                INSTRUCTIONS:
                    The image actually contains {img_objs}.
                    But the object detection model identified {img_bounding_boxes} in the image.
                    Your task is to find all the additinal objects wrongly identified by the YOLO model from the inputs given.
                    Provide your analysis as a paragraph in string format without bold or other formating styles.
            """
    
    def obj_detection_exp_prompt(img_objs, img_bounding_boxes, add_objs, add_objs_presence):
        return f"""
                TASK: Generate a detailed explanation for object detection results in the given image.
                
                INPUT:
                1. IMAGE_OBJECTS: A list of objects that are present in the image.
                2. IMAGE_BOUNDING_BOXES: A list of objects detected by the model, including all bounding box labels.
                3. ADDITIONAL_OBJECTS: A list of objects that are detected but need to be verified for their presence.
                4. ADDITIONAL_OBJECTS_PRESENCE: A corresponding list of boolean values indicating whether each object in ADDITIONAL_OBJECTS is actually present (`True`) or not (`False`).
                
                INSTRUCTIONS:
                1. Identify objects that are correctly detected by the model (present in both IMAGE_OBJECTS and IMAGE_BOUNDING_BOXES).
                2. Identify objects that are falsely detected (in IMAGE_BOUNDING_BOXES but marked as `False` in ADDITIONAL_OBJECTS_PRESENCE).
                3. Generate a detailed explanation that:
                - Lists the correctly detected objects.
                - Lists the falsely detected objects.
                
                OUTPUT FORMAT:
                A detailed explanation summarizing the correctly detected objects, falsely detected objects, and potential reason for failure (only one valid & conviencible reason for failure).
                Provide your output as a single paragraph. Do not mention about input variable names in your response.

                Make sure your response is consistent, whenever I ask the same question your response should be same.
                Do not provide any suggestions.
                
                INPUT:
                IMAGE_OBJECTS: {img_objs}
                IMAGE_BOUNDING_BOXES: {img_bounding_boxes}
                ADDITIONAL_OBJECTS: {add_objs}
                ADDITIONAL_OBJECTS_PRESENCE: {add_objs_presence}
                
                EXAMPLE OUTPUT:
                {{
                    "explanation": "The model is able to identify objects like "person", "bottle", "bowl", "wine glass", "car", "dog", "cell phone" and  "tie" whereas it wrongly identified handbag, sports ball. This could be due to poor lighting conditions that obscure the objects that makes it difficult for the model to accurately identify these items."
                }}
            """
    
    def obj_detection_exp_slm_prompt(img_objs, img_bounding_boxes, add_objs, add_objs_presence):
        return f"""
                TASK: Generate a detailed explanation for object detection results in the given image.
                
                INPUT:
                1. IMAGE_OBJECTS: Analysis of objects that are present in the image.
                2. IMAGE_BOUNDING_BOXES: Objects detected by the model, including only bounding box labels.
                3. ADDITIONAL_OBJECTS: A list of objects that are detected but need to be verified for their presence.
                4. ADDITIONAL_OBJECTS_PRESENCE: A corresponding analysis indicating whether objects in IMAGE_BOUNDING_BOXES are actually present (`True`) or not (`False`).
                
                INSTRUCTIONS:
                - Analyze IMAGE_BOUNDING_BOXES and ADDITIONAL_OBJECTS_PRESENCE carefully.
                - Lists the correctly detected objects.
                - Lists the falsely detected objects.
                - Provides potential reasons for false detections, such as poor lighting, occlusions, low resolution, or adversarial characteristics.
                - Explains the impact of these factors in a professional and user-friendly tone.
                
                OUTPUT FORMAT:
                A detailed explanation summarizing the correctly detected objects, falsely detected objects, and potential reasons for failures.
                Provide your output as a single paragraph. Do not mention about input variable names in your response.

                Make sure your response is consistent, whenever I ask the same question your response should be same.
                Do not provide any suggestions.
                
                INPUT:
                IMAGE_OBJECTS: {img_objs}
                IMAGE_BOUNDING_BOXES: {img_bounding_boxes}
                ADDITIONAL_OBJECTS: {add_objs}
                ADDITIONAL_OBJECTS_PRESENCE: {add_objs_presence}
                
                EXAMPLE OUTPUT:
                {{
                    "explanation": "The model is able to identify objects like "person", "bottle", "bowl", "wine glass", "car", "dog", "cell phone" and  "tie" whereas it wrongly identified handbag, sports ball. This could be due to poor lighting conditions that obscure the objects, occlusion where other objects or parts of the image block the view of the sports ball and handbag, or low resolution that makes it difficult for the model to accurately identify these items."
                }}
            """
    
    def object_detection_azure(object_name: str):
        return f"""
            TASK: Generate a detailed explanation for object detection results in the given image.
            INPUT: 
                1. An image
                2. Object name
            INSTRUCTIONS:
                1. Analyze and check whether the image contains {object_name} or not.
                2. Ensure that your response is based solely on visual evidence.
            OUTPUT FORMAT:
                {{
                    "object": 
                    "object_presence": True/False [Boolean Value],
                    "explanation": 
                }}
            """
    
    def object_detection_azure_summarize(object_name: str):
        return f"""
            You are expert Responsible AI assistance, below is the observation of individual objects identified in the image.
            You are required to generate a detailed explanation for the object detection results by considering the observations given. 
            Make sure if there are any objects incorrectly/wrongly identified then provide the potential reasons for the failure like (The model falsely classified bus as truck. At the top-center corner of the image, the pixels values resembles more similar to truck features, so the model wrongly classified that object as truck instead of bus. This could be due to poor lighting conditions that obscure the objects that makes it difficult for the model to accurately identify these items.)
            Write your summary in a professional way without grammatical errors, assume you are explaining the results.
            {object_name}

            response format:
            {{
                "summary": 
            }}
            """
    
    def object_detection_slm(object_name: str):
        return  f"""
            You are a highly capable and detail-oriented Responsible AI Assistant. Your task is to:
            1. Analyse the image thoroughly:
                Carefully examine every detail in the image, including the background, foreground, and any objects or patterns present. Use your comprehensive vision analysis capabilities to ensure no relevant aspect is overlooked.
            2. Validate the presence of specified:
                Determine whether the given object is present in the image. Use logical reasoning and visual features (such as shape, size, color, texture, and context) to confirm their existence.
                Make sure to validate the presence pf given object {object_name}, do not consider the similar object during validation.
            3. Provide a clear and concise explanation for your conclusion:
                3.1 If the object is present, explain how you identified it by describing the relevant visual features or context clues in the image.
                3.2 If the object in not present, describe the analysis you performed and why it did not meet the criteria for identifying the object.
            4. Adhere to principles of Responsible AI:
                Ensure your analysis is unbiased, thorough, and transparent. Provide explanations in a way that is easy to understand, even for non-technical users.
            5. Format you respone as follows:
                Validation: state whether the object is present or not.
                Explanation: Provide a step-by-step reasoning for your decision, referring to specific parts or features of the image where applicable.
            Be precise, detailed, and ensure that your explanation can be understood without ambiguity or technical jargon. Focus on clarity and accuracy in your response.
            There should not be bold or any formatting styles in your response.
            OBJECT NAME: {object_name}
            """
    
    def object_detection_slm_summarize(analysis: str):
        return f"""
            You are a Responsible AI Assistant tasked with summarizing a detailed analysis of multiple objects. Your responsibilities are as follows:      
            Input Analysis Parsing:
                Carefully read the input, which contains individual analyses for multiple objects from same image.
                Identify the key findings for each object, including whether it is present or not and the reasoning provided.          
            Generate a Summary:
                Provide a concise yet comprehensive summary of the analysis, highlighting the overall conclusions for all objects.
                Group similar findings together for clarity, such as all present objects in one section and all absent objects in another.
                Ensure the reasoning for key conclusions is briefly but clearly stated.
            Maintain Clarity and Professionalism:
                Write in a manner that is easy to understand, avoiding technical jargon wherever possible.
                Ensure the summary is unbiased, factual, and aligns with the principles of Responsible AI. 
            Format your response as follows:
                A brief summary of the analysis scope (e.g., "The analysis evaluated the presence of X objects in the given image."). Focus on providing a coherent summary that accurately reflects the detailed analyses while making it easy for a non-technical audience to understand.
                Do not provide assumptions or suggestions in your response.
                Do not discuss anything about Responsible AI in your response.
                All the input analysis is from single image, so do not mention anything about images in your response. 
                Provide your response as a paragraph in a string without any bold or style formatting in the response.            
            EXAMPLE OUTPUT:
                The analysis confirms the presence of people in image, identifying typical human attributes such as clothing, posture, and body parts. However, it incorrectly identifies a truck in one object, which actually shows a bus with specific text.            
            Make sure if there are any objects incorrectly/wrongly identified then provide the potential reasons for the failure like (The model falsely classified bus as truck. At the top-center corner of the image, the pixels values resembles more similar to truck features, so the model wrongly classified that object as truck instead of bus. This could be due to poor lighting conditions that obscure the objects that makes it difficult for the model to accurately identify these items.)
            INPUT: {analysis}
            """
    
    def uncertainty_template(input):

        template = f'''
        
            You are a Responsible AI expert with extensive experience in Explainable AI for Large Language Models. Your role is to clearly generate explanations for why the Large Language Model has generated a certain image for the given prompt.

            You are a helpful assistant. Do not fabricate information or provide assumptions in your response.

            Given the following prompt:

            INPUT: {input}
            
            Please assess the following metrics:

            1. Uncertainty: Evaluate the uncertainty for the given generated image w.r.t the given INPUT using a score between 0 (certain) and 95 (highly uncertain). Additionally, explain your reasoning behind the assigned score. Consider whether the image contributes to or reduces the uncertainty.
            
            Based on the score and explanation for each metric, provide a recommendation for how to change the INPUT to improve the certainty of generated image and the scores. Ensure that each recommendation is concrete and actionable. If a metric has a perfect score, provide positive reinforcement or suggest maintaining the current quality.

            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_local_explanation}
            '''
        return template