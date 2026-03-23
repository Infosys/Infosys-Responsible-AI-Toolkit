'''
Copyright 2024 Infosys Ltd.

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

# Sentiment Analysis
output_format_sentiment_analysis = """
    {
        "Sentiment": "Sentiment of the given prompt",
        "Keywords": [List of contributing keywords for the sentiment],
        "Explanation": "Explanation for the sentiment",
        "token_importance_mapping": [Dictionary of token importance mapping for identified keywords]
    }
"""

# Local Explanation
output_format_local_explanation = """
    {
        "uncertainty": {
            "score": Integer,
            "explanation": "",
            "recommendation": ""
        },
        "coherence": {
            "score": Integer,
            "explanation": "",
            "recommendation": ""
        }
    }
"""

# Token Importance
output_format_token_importance = """
    {
        "Token": ["Each Token from input prompt"],
        "Importance Score": [The value here should be a comma-separated list of importance scores],
        "Position": [The value here should be a comma-separated list of respective token index positions]
    }
"""

# Tone Analysis
output_format_tone_analysis = """
    {
        "Reasoning": [Reasoning],  # Reasoning to critique the tone of the response, start with "Your response...."
        "Tone": [Tones]
        "Score": [Score]
        "Recommendation": [Recommendation]
    }
"""

# Coherence
LANGUAGE_COHERENCE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the coherence of the response,
    "Score": [Score],  # Score between 1 to 5, to evaluate the coherence of the response
}
"""

# Response Relevance
RESPONSE_RELEVANCE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the conciseness of the response for answering the query,
    "Score": [Score],  # Score assigned for the relevance of the response to the query
"""

# Fact Generation
FACT_GENERATE_OUTPUT_FORMAT = """
{
    "Facts": [ # List of all the facts
            {
                [1st Fact],  # 1st fact being analysed
            },
            {
                [2nd Fact],  # 2nd fact being analysed
            },
        ... # Do for all the facts
    ]
}
In case of no facts, return an empty list, i.e. [].
"""

# Factuality Evaluation
FACT_EVALUATE_OUTPUT_FORMAT__COT = """
{
    "Result": [  # List containing data for all the facts
        {
            "Fact": [1st Fact],  # 1st fact being analysed,
            "Reasoning": [Reasoning for 1st Fact],  # Reasoning to determine if the 1st fact can be verified from the context or not,
            "Judgement": [Judgement for 1st Fact]   # Judgement for 1st fact. Select one of the three - "yes", "unclear" or "no",
        },
        {
            "Fact": [2nd Fact],  # 2nd fact being analysed,
            "Reasoning": [Reasoning for 2nd Fact],  # Reasoning to determine if the 2nd fact can be verified from the context or not,
            "Judgement": [Judgement for 2nd Fact]   # Judgement for 2nd fact. Select one of the three - "yes", "unclear" or "no",
        },
        ... # Do for all the facts
    ]
}
"""

# Filter Facts
FACT_FILTER_OUTPUT_FORMAT = """
{
    "RelevantFacts": [
        "[Relevant Fact 1]",
        "[Relevant Fact 2]",
        ...
    ]
}
"""

# Thot Explanation
output_format_thot = """
    {
        "Result": "answer",
        "Explanation": "step-by-step reasoning"
    }
"""

#CoT Explanation
output_format_cot = """
    {
        "Explanation": "think the answer step by step and explain step by step how you got the answer"
    }
""" 

#LoT Explanation
output_format_lot_phase1 = """
    {
        "Propositions": "Propositions given in the output",
        "Logical Expression": "Logical Expression"
    }
"""

output_format_lot_phase2 = """
    {
        "Extended Logical Expression": "Drived extended logical expression",
        "Law Used": "Law used to derive the extended logical expression and its definition"
    }
"""

output_format_lot_phase3 = """
    {
        "Extended Logical Information: "Drived extended logical information",
    }
"""

output_format_lot4 = """
    {
        "Explanation": "Returned explaination should be in a plain text and shouldn't consist of special characters, sub-dictionaries"
    }
""" 