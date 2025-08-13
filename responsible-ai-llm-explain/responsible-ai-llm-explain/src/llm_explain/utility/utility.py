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

from llm_explain.config.logger import CustomLogger
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException
from openai import AzureOpenAI
from tenacity import retry
from tqdm import tqdm
import numpy as np
import asyncio
import os
import tiktoken
import requests

from dotenv import load_dotenv
load_dotenv()

log = CustomLogger()

class Utils:
    
    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    
    def normalize_vector(v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm
    
    def calculate_normalized_entropy(logprobs):
        """
        Calculate the normalized entropy of a list of log probabilities.
    
        Parameters:
            logprobs (list): List of log probabilities.
        
        Returns:
            float: Normalized entropy.
        """
        try:
            entropy = -np.sum(np.exp(logprobs) * logprobs)
        
            # Calculate maximum possible entropy for N tokens sampled
            N = len(logprobs)
            max_entropy = np.log(N)
        
            # Normalize the entropy
            normalized_entropy = entropy/max_entropy
            return normalized_entropy
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

 
    async def process_token_async(i, top_logprobs_list, choice, choice_embedding, max_tokens):
       
       
        """
        Asynchronously process a token to calculate its normalized entropy and mean cosine distance.
       
        Parameters:
            i (int): Token index.
            top_logprobs_list (list): List of top log probabilities for each token.
            choice (dict): The choice containing log probabilities and tokens.
            choice_embedding (array): Embedding of the full choice.
            max_tokens (int or None): Maximum number of tokens to consider for the partial string.
           
        Returns:
            tuple: Mean cosine distance and normalized entropy for the token.
        """
        try:   
            top_logprobs = top_logprobs_list[i]
            normalized_entropy = Utils.calculate_normalized_entropy(list(top_logprobs.values()))
        
            tasks = []
    
            # Loop through each sampled token to construct partial strings and calculate embeddings
            for sampled_token in top_logprobs:
                tokens_to_use = choice['logprobs']['tokens'][:i] + [sampled_token]
            
                # Limit the number of tokens in the partial string if max_tokens is specified
                if max_tokens is not None and len(tokens_to_use) > max_tokens:
                    tokens_to_use = tokens_to_use[-max_tokens:]
    
                constructed_string = ''.join(tokens_to_use)
                task = Utils.get_embedding(constructed_string)
            
                tasks.append(task)
            
            embeddings = await asyncio.gather(*tasks)
        
            cosine_distances = []
    
            # Calculate cosine distances between embeddings of partial strings and the full choice
            for new_embedding in embeddings:
                cosine_sim = cosine_similarity(new_embedding.reshape(1, -1), choice_embedding.reshape(1, -1))[0][0]
                cosine_distances.append(1 - cosine_sim)
            
            mean_distance = np.mean(cosine_distances)
        
            return mean_distance, normalized_entropy
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    def decoded_tokens(string, tokenizer):
        return [tokenizer.decode([x]) for x in tokenizer.encode(string)] 
    
    def scale_importance_log(importance_scores, base=None, offset=0.0, min_percentile=0, max_percentile=100, smoothing_constant=1e-10, scaling_factor=1.0, bias=0.0):
        # Extract the importance values
        try:
            importance_values = np.array([score[1] for score in importance_scores])

            # Apply optional percentile-based clipping
            if min_percentile > 0 or max_percentile < 100:
                min_val = np.percentile(importance_values, min_percentile)
                max_val = np.percentile(importance_values, max_percentile)
                importance_values = np.clip(importance_values, min_val, max_val)

            # Subtract the minimum value and add the optional offset
            importance_values = importance_values - np.min(importance_values) + offset

            # Add smoothing constant to ensure non-zero values
            importance_values += smoothing_constant

            # Apply logarithmic scaling, with an optional base
            scaled_values = np.log(importance_values) if base is None else np.log(importance_values) / np.log(base)

            # Apply scaling factor and bias
            scaled_values = scaling_factor * scaled_values + bias

            # Normalize to the range [0, 1]
            scaled_values = (scaled_values - np.min(scaled_values)) / (np.max(scaled_values) - np.min(scaled_values))

            # Pair the scaled values with the original tokens
            scaled_importance_scores = [(token, scaled_value) for token, scaled_value in zip([score[0] for score in importance_scores], scaled_values)]

            return scaled_importance_scores
        except Exception as e:
            log.error(e,exc_info=True)
            raise 
    
    @retry
    async def get_embedding(input_text):
        try:
            response = Utils.client.embeddings.create(
                input = input_text,
                model= "text-embedding-ada-002",
                timeout= 4.0
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            log.error(e,exc_info=True)
            raise 
        
    async def approximate_importance(perturbed_text, original_embedding, model=None, tokenizer=None):
        try:
            perturbed_embedding = await Utils.get_embedding(perturbed_text)
            cosine_dist = 1 - cosine_similarity(original_embedding.reshape(1, -1), perturbed_embedding.reshape(1, -1))[0][0]
            return cosine_dist
        except Exception as e:
            log.error(e,exc_info=True)
            raise 

    async def ablated_relative_importance(input_text, tokenizer, model=None,):
        try:
            original_embedding = await Utils.get_embedding(input_text)
            tokens = Utils.decoded_tokens(input_text, tokenizer)
            importance_scores = []
            
            with tqdm(total=len(tokens), desc="Calculating Token Importances", position=0, leave=True) as progress:
                for i in range(len(tokens)):
                    if len(tokens[i]) < 4:
                        continue
                    perturbed_text = "".join(tokens[:i] + tokens[i+1:])
                    importance = await Utils.approximate_importance(perturbed_text, original_embedding, model, tokenizer)
                    importance_scores.append((tokens[i], importance))
                    progress.update(1)
                    
            return importance_scores
        except Exception as e:
            log.error(e,exc_info=True)
            raise

    def get_price_details(model: str):
        '''
        Returns price per tokens of the model.

        Parameters:
        model (str): Model name (Ex: gpt-4)
        '''
        prompt_price_per_1000_tokens = {
            "gpt-4o": 0.0050,
            "gpt-35-turbo": 0.0005,
            "gpt-35-turbo-instruct": 0.0015,
            "gpt4": 0.0300
        }
        
        response_price_per_1000_tokens = {
            "gpt-4o": 0.0150,
            "gpt-35-turbo": 0.0015,
            "gpt-35-turbo-instruct": 0.0020,
            "gpt4": 0.0600
        }

        try:
            return prompt_price_per_1000_tokens[model], response_price_per_1000_tokens[model]
        except KeyError:
            raise ValueError(f"Model '{model}' is not found in the pricing details. Only gpt-4o, gpt-35-turbo, gpt-35-turbo-instruct & gpt4 are available. Please contact administrator")
        
    def get_token_cost(input_tokens: int, output_tokens: int, model: str):
        '''
        Calculates the total cost for tokens.

        Parameters:
        tokens (int): Total token (Prompt tokens + Completion tokens)
        model (str): Model name (Ex: gpt4)
        '''

        if 'gpt-4o' in model:
            model = 'gpt-4o'
        # Example pricing (this should be replaced with actual pricing from Azure documentation)
        prompt_price_per_1000_tokens, response_price_per_1000_tokens = Utils.get_price_details(model)
        
        # Calculate cost
        total_cost = ((input_tokens / 1000) * prompt_price_per_1000_tokens) + ((output_tokens / 1000) * response_price_per_1000_tokens)
        return round(total_cost, 3)
    
    def calculate_token_count(text: str, model_name: str = "text-embedding-ada-002") -> int:
        # Load the appropriate tokenizer for the model
        tokenizer = tiktoken.encoding_for_model(model_name)
        # Encode the text into tokens
        tokens = tokenizer.encode(text)
        # Return the token count
        return len(tokens)
    
    def send_telemetry_request(explainability_telemetry_request, url):
        try:
            response = requests.post(url, json=explainability_telemetry_request)
            response.raise_for_status()
            response_data = response.json()
            log.info(f"Telemetry response: {response_data}")
        except Exception as e:
            log.error(str(e))
            raise HTTPException(
                status_code=500,
                detail="Please check with administration!!",
                headers={"X-Error": "Please check with administration!!"})