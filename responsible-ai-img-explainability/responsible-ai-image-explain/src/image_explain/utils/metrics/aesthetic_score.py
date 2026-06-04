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
import warnings
warnings.filterwarnings('ignore')
from image_explain.config.logger import CustomLogger
import torch.nn as nn
from PIL import Image
import torch
import gc
import clip

log = CustomLogger()

class AestheticScore:

    model, preprocess = clip.load('ViT-L/14')

    @staticmethod
    def get_aesthetic_model(clip_model: str = "vit_l_14") -> nn.Module:
        """
        Load the aesthetic model.

        This function loads the aesthetic model based on the specified CLIP model type.
        It supports 'vit_l_14' and 'vit_b_32' model types.

        Parameters:
        clip_model (str): The type of CLIP model to use. Must be one of 'vit_l_14' or 'vit_b_32'.

        Returns:
        nn.Module: The loaded aesthetic model.
        """
        try:
            # Initialize the model based on the specified CLIP model type
            if clip_model == "vit_l_14":
                model = nn.Linear(768, 1)
            elif clip_model == "vit_b_32":
                model = nn.Linear(512, 1)
            else:
                raise ValueError("clip_model must be one of 'vit_l_14' or 'vit_b_32'")

            # Path to the model file
            path_to_model = "../model/sa_0_4_vit_l_14_linear.pth"  # Model can be downloaded from -> https://github.com/LAION-AI/aesthetic-predictor/blob/main/sa_0_4_vit_l_14_linear.pth?raw=true

            # Load the model state dict
            state_dict = torch.load(path_to_model)
            model.load_state_dict(state_dict)  # Load the state dict into the model
            model.eval()  # Set the model to evaluation mode
        except FileNotFoundError as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise FileNotFoundError(f"The model file at {path_to_model} was not found.")
        except Exception as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise RuntimeError(f"An error occurred while loading the model: {e}")

        return model

    def score(image_path) -> float:
        """
        Get the aesthetic score of the image.

        This function preprocesses the input image, extracts its features using the CLIP model,
        and then predicts the aesthetic score using the aesthetic model.

        Parameters:
        image_path (str): The file path to the image to be scored.

        Returns:
        float: The predicted aesthetic score of the image.
        """
        try:
            # Open and preprocess the image
            image = AestheticScore.preprocess(Image.open(image_path)).unsqueeze(0)
        except FileNotFoundError as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise FileNotFoundError(f"The image file at {image_path} was not found.")
        except Exception as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise ValueError(f"An error occurred while processing the image: {e}")

        try:
            # Disable gradient calculation for inference
            with torch.no_grad():
                # Extract image features using the CLIP model
                image_features = AestheticScore.model.encode_image(image)
                
                # Normalize the image features
                image_features /= image_features.norm(dim=-1, keepdim=True)

                # Load the aesthetic model
                aesthetic_model= AestheticScore.get_aesthetic_model(clip_model="vit_l_14")
                
                # Predict the aesthetic score using the aesthetic model
                prediction = aesthetic_model(image_features)
                
                # Extract the score from the prediction
                aesthetic_score = prediction.item()
        except Exception as e:
            log.error(f"Request error: {e}", exc_info=True)
            raise RuntimeError(f"An error occurred during model inference: {e}")
        finally:
            # Clear memory
            del image
            del image_features
            del aesthetic_model
            del prediction
            gc.collect()

        return aesthetic_score
