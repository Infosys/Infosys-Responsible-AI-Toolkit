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
IMAGE_ANALYZE_OUTPUT_FORMAT = """
    [Output]:
    {
        "ImageDescription": "[Detailed description of the elements present in the image.]",
        "Style": "[Style of the image]"
        "StyleAnalysis": "[Reasoning of the style of the image.]",
        "WatermarkContent": "Extracted Watermark Text",
    }
"""

# Bias Analyse
BIAS_ANALYZE_OUTPUT_FORMAT = """
    [Output]:
    {
        "Analysis": "[Crisp and to the point analysis including all necessary details]",
        "Key Words": "[Highlight the words in the input which are crucial for the analysis]",
        "Justification": "[Justify why the key words highlighted are crucial in the analysis made]",
        "Bias type(s)": "[Comma separated bias type(s), state NA in case of no bias type]",
        "Previledged group(s)": "[Comma separated group(s), state NA in case of no group]",
        "Un-Previledged group(s)": "[Comma separated group(s), state NA in case of no group]",
        "Bias score": "[High / Medium / Low / Neutral]"
    }
"""

# Query Based Image Analysis
QUERY_BASED_IMAGE_ANALYSIS_OUTPUT_FORMAT = """
    [Output]:
    {
        "Response": "[Crisp and to the point analysis including all necessary details]",   
    }
"""

# Uncertainty Analysis
output_format_local_explanation = """
    [Output]:
        "uncertainty_score": {
            "score": Integer
        }
"""