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

# Image Analyze
IMAGE_ANALYZE_EXAMPLE = """
    [Output]:
    {
        "ImageDescription": "The image depicts a vast mountain range with sharp, rugged peaks. The mountains are bathed in sunlight, casting long shadows that add depth to the scene. Above, a clear blue sky stretches without any clouds, creating a stark contrast with the dark tones of the mountains. The foreground features sparse vegetation, with patches of snow visible on the higher peaks.",
        "Style": "Photorealism"
        "StyleAnalysis": "The image is classified as Photorealism due to its meticulous attention to detail and the lifelike rendering of the mountain landscape. The precise use of light and shadow creates a sense of depth and three-dimensionality, enhancing the realism of the scene. The accurate depiction of colors, such as the dark tones of the mountains contrasted against the clear blue sky, and the intricate textures of the rocky peaks and sparse vegetation, all contribute to the photorealistic quality. This style aims to replicate the visual experience of looking at an actual photograph, thereby immersing the viewer in the natural beauty and ruggedness of the landscape.",
        "WatermarkContent": "None"
    }
"""

# Bias Analyse
BIAS_ANALYZE_EXAMPLE = """
    [Output]:
    {
        "Analysis": "The input statement is generalizing that 'black people' often commit crimes which is a stereotype and not based on individual actions. This is a biased statement as it unfairly attributes a negative behavior to all members of a certain racial group.",
        "Key Words": "*Black people often* commit crimes"
        "Justification": "*Black people often* generalizes the action about a particular Race."
        "Bias type(s)": "Racial bias, Stereotyping",
        "Previledged group(s)": "Black people",
        "Un-Previledged group(s)": "White people",
        "Bias score": "High"
    }
"""

# Query Based Image Analysis
QUERY_BASED_IMAGE_ANALYSIS_EXAMPLE = """
    [Output]:
    {
        "Response": "One girl is there in the image. She is wearing a red dress and holding a bouquet of flowers."
    }
"""

OBJECT_DETECTION_EXAMPLE = """
    [Output]:
    {
        "cat 0.83": {
            "Explanation": "The model assigned this object to the 'cat' class because it detected a feline shape and features, such as ears and fur, in the image. The score of 0.83 indicates a high confidence in this classification."
        }
    }
"""