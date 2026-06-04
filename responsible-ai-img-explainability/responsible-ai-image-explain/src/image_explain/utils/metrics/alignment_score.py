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
from image_explain.config.logger import CustomLogger
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

log = CustomLogger()

class AlignmentScore:

    # Class-level attributes for the model and processor
    processor = CLIPProcessor.from_pretrained("../model/clip-vit-base-patch16")
    model = CLIPModel.from_pretrained("../model/clip-vit-base-patch16")
    
    def score(image_path: str, text: str) -> float:
        """
        Calculate the alignment score between an image and text.

        This method calculates the alignment score between the provided image and text.
        The alignment score is a measure of how well the image and text align semantically.

        Parameters:
        image_path (str): The path to the image file.
        text (str): The text prompt to compare with the image.

        Returns:
        float: The alignment score between the image and text.
        """
        image = None
        inputs = None
        outputs = None
        try:
            # Load the image
            image = Image.open(image_path)

            # Preprocess the image and text
            inputs = AlignmentScore.processor(text=text, images=image, return_tensors="pt", padding=True)

            # Forward pass through the model
            with torch.no_grad():
                outputs = AlignmentScore.model(**inputs)

            # Compute the cosine similarity between text and image embeddings
            alignment_score = torch.nn.functional.cosine_similarity(outputs.image_embeds, outputs.text_embeds).item()

            return alignment_score
        except FileNotFoundError as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise FileNotFoundError(f"The image file was not found at the specified path: {image_path}")
        except Exception as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise RuntimeError(f"An error occurred while calculating the alignment score: {e}")
        finally:
            # Clear memory
            if image is not None:
                del image
            if inputs is not None:
                del inputs
            if outputs is not None:
                del outputs
            gc.collect()