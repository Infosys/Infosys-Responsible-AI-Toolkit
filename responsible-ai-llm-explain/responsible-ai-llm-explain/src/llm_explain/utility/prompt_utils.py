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

class Prompt:
        
    def get_prompt(prompt, response):
        
        template = f'''
            You are a Responsible AI expert with extensive experience in Explainable AI for Large Language Models. Your role is to clearly generate explanations for why the Large Language Model has generated a certain response for the given prompt.

            You are a helpful assistant. Do not fabricate information or provide assumptions in your response.

            Given the following prompt-response pair:

            Prompt: {prompt}
            Response: {response}

            Please assess the following metrics:

            1. Sentiment: Evaluate the sentiment associated with the response using a score between -1 (negative), 0 (neutral), and 1 (positive). Additionally, explain your reasoning behind the assigned sentiment score.

            2. Grammatical Mistakes: Evaluate the grammatical correctness of the response using a score between 0 (no mistakes) and 1 (more mistakes). Additionally, explain your reasoning behind the assigned grammatical mistakes score.

            3. Uncertainty: Evaluate the uncertainty associated with the response for the given prompt using a score between 0 (certain) and 1 (highly uncertain). Additionally, explain your reasoning behind the assigned uncertainty score.

            4. Out of Vocabulary (OOV): Assess the percentage of out-of-vocabulary words in the response relative to the prompt using a score between 0 and 100. Additionally, explain your reasoning behind the assigned OOV words percentage.

            5. Coherence: Evaluate the logical flow and coherence of the response using a score between 0 (incoherent) and 1 (highly coherent). Additionally, explain your reasoning behind the assigned coherence score.

            6. Relevance: Assess the relevance of the response to the given prompt using a score between 0 (irrelevant) and 1 (highly relevant). Additionally, explain your reasoning behind the assigned relevance score.

            7. How did you arrive at the following response based on the prompt provided?
                Prompt: {prompt}
                Response: {response}
                Explain the reasoning and steps taken to generate this response.

            Your response should be in the following JSON format:
            {{
                "sentiment": {{
                    "score": "",
                    "explanation": ""
                }},
                "grammatical_mistakes": {{
                    "score": "",
                    "explanation": ""
                }},
                "uncertainty": {{
                    "score": "",
                    "explanation": ""
                }},
                "out_of_vocabulary": {{
                    "score": "",
                    "explanation": ""
                }},
                "coherence": {{
                    "score": "",
                    "explanation": ""
                }},
                "relevance": {{
                    "score": "",
                    "explanation": ""
                }},
                "reasoning": ""
            }}

            Do not provide any response other than the JSON object.
            '''
        return template

    def get_token_importance_prompt(prompt):
       
        template = f'''
            You are a helpful assistant. Do not fabricate information or do not provide assumptions in your response.
 
            Given the following prompt:
 
            Prompt: {prompt}
 
            Please assess the following metric:
 
            1. Token Importance: Evaluate the importance of each token in the prompt. Calculate the importance value of each token in the given prompt using a
            score between 0 (low importance) and 1 (high importance). Provide all the tokens as a list. Ensure that you give an importance score for all tokens,
            and there are no empty spaces or inconsistencies in the output, which might cause issues while parsing. Make your analysis consistent so that if given
            the same input again, you produce a similar output.
 
            Your response should be in the following JSON format:
 
            output-format:
            {{
                "Token": ["Each Token from input prompt"],
                "Importance Score": ["The value here should be a comma-separated list of importance scores"],
                "Position": ["The value here should be a comma-separated list of respective token index positions"]
            }}
 
            Do not provide any response other than the JSON object.
        '''
        return template