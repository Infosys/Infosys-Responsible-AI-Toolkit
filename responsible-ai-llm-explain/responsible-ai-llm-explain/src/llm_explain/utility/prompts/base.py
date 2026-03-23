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

from llm_explain.utility.prompts.output_format import *
from llm_explain.utility.prompts.few_shot import *
from llm_explain.utility.prompts.instructions import *

class Prompt:

    def get_classification_prompt(input_prompt):
        
        template = f"""
            Imagine you are a Responsible AI expert with experience in explaining why a model has made a decision. 
            Your task is to determine the sentiment of the given prompt, identify the keywords the model used to arrive at that sentiment, and provide a clear explanation of why the model classified the prompt as that sentiment.

            Calculate the importance value of each token  towards getting the overall sentiment from the given prompt using a score between 1 (low importance) and 100 (high importance). 
            Provide all the tokens as a list. Ensure that you give an importance score for all tokens, and there are no empty spaces or inconsistencies in the output, which might cause issues while parsing. 
            Make your analysis consistent so that if given the same input again, you produce a similar output.

            similarly, provide sentiment, keywords identified to determine the sentiment and Explanation for the below given information.
            Make sure identified key words are individual words and not combined words.

            Make sure the response is simple and easy to understand. Use polite language. Do not write as a third person. Do not include Certainly! at the beginning of your response, just give response.
            
            Example Data:
            {one_shot_sentiment_analysis}
            
            Return the output only in the following JSON format. Do not output anything other than this JSON object:
            {output_format_sentiment_analysis}

            Task Data:
            [Prompt]: {input_prompt}
            """
        return template
        
    def get_local_explanation_prompt(prompt, response, context=None):

        if context:

            template = f'''
                You are a Responsible AI expert with extensive experience in Explainable AI for Large Language Models. Your role is to clearly generate explanations for why the Large Language Model has generated a certain response for the given prompt.

                You are a helpful assistant. Do not fabricate information or provide assumptions in your response.

                Given the following prompt-response pair and the associated context:

                Prompt: {prompt}
                Response: {response}
                Context: {context}

                Please assess the following metrics by considering both the context and the prompt-response pair:

                1. Uncertainty: Evaluate the uncertainty associated with the response using a score between 0 (certain) and 95 (highly uncertain). Consider both the provided context and how well the response aligns with it. Additionally, explain your reasoning behind the assigned score.
                2. Coherence: Evaluate the logical flow and coherence of the response using a score between 0 (incoherent) and 95 (highly coherent). Consider how well the response maintains consistency with the given context. Additionally, explain your reasoning behind the assigned score.

                Based on the score and explanation for each metric, provide a recommendation for how to change the input prompt so that the response will be better aligned with the context and the scores will improve. Ensure that each recommendation is concrete and actionable. If a metric has a perfect score, provide positive reinforcement or suggest maintaining the current quality.

                Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
                {output_format_local_explanation}
            '''
        else:

            template = f'''
                You are a Responsible AI expert with extensive experience in Explainable AI for Large Language Models. Your role is to clearly generate explanations for why the Large Language Model has generated a certain response for the given prompt.

                You are a helpful assistant. Do not fabricate information or provide assumptions in your response.

                Given the following prompt-response pair:

                Prompt: {prompt}
                Response: {response}

                Please assess the following metrics:

                1. Uncertainty: Evaluate the uncertainty associated with the response for the given prompt using a score between 0 (certain) and 95 (highly uncertain). Additionally, explain your reasoning behind the assigned score.
                2. Coherence: Evaluate the logical flow and coherence of the response using a score between 0 (incoherent) and 95 (highly coherent). Additionally, explain your reasoning behind the assigned score.

                Based on the score and explanation for each metric, provide a recommendation for how to change the input prompt so that the response will be better and the scores will improve. Ensure that each recommendation is concrete and actionable. If a metric has a perfect score, provide positive reinforcement or suggest maintaining the current quality.

                Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
                {output_format_local_explanation}   
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

            Example Data:
            {one_shot_token_importance}

            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_token_importance}
        '''
        return template
    
    def get_tone_prediction_prompt(response):

        template = f'''
            You are a detail-oriented LLM that pays close attention to the nuances of language. 
            You will be given a text and your job is to analyze its tone. 

            Specifically, you need to consider the following tones and identify which tone is most appropriate for the given text:

            Formal: Professional, respectful, objective (e.g., scientific reports, business emails)
            Informal: Casual, conversational, friendly (e.g., text messages, social media posts)
            Informative: Primarily focused on conveying information clearly and concisely (e.g., news reports, summaries)
            Positive: Happy, optimistic, encouraging (e.g., motivational speeches, congratulations)
            Negative: Sad, angry, frustrated (e.g., complaints, critical reviews)
            Neutral: Objective, unbiased, unemotional (e.g., factual summaries, news reports)
            Humorous: Funny, witty, sarcastic (e.g., jokes, lighthearted stories)
            Dramatic: Suspenseful, exciting, intense (e.g., fictional narratives, descriptions of events)
            Inspiring: Uplifting, motivating, thought-provoking (e.g., speeches, self-help content)
            Persuasive: Trying to convince the reader of something (e.g., marketing copy, arguments)
            Empathetic: Understanding and supportive (e.g., responses to someone going through a tough time)
            Authoritative: Confident, knowledgeable (e.g., expert opinions, instructions)

            Based on the score and explanation for each metric, provide a recommendation for how to change the input prompt so that the response will be better and the scores will improve. Ensure that each recommendation is concrete and actionable. If a metric has a perfect score, provide positive reinforcement or suggest maintaining the current quality.

            Example Data:
            {few_shot_examples_tone_analysis}

            Return the output only in the following JSON format. Do not output anything other than this JSON object:
            {output_format_tone_analysis}

            Task Data:
            [Response]: {response}
        '''
        return template
    
    def get_coherehce_prompt(response):

        template = f"""
            You are a detail-oriented LLM which pays close attention to the details. You are given a text and your job is to evaluate the quality of the provided text, focusing on the coherence aspect.

            Coherence is the quality of the text that makes it logical and consistent. It is important that the text is well-organized and the ideas are connected in a clear and meaningful way. A coherent text is easy to follow and understand.

            Please provide a score on the scale of 1-5, with 1 meaning that the text is completely incoherent and the elements in the text do not stitch together to produce meaningful text, and 5 meaning that the text is completely coherent and the elements in the text stitch together to produce meaningful text.

            Example Data.
            {LANGUAGE_COHERENCE_FEW_SHOT__COT}

            First, analyze the text and determine how fluent and natural sounding it is. Consider the structure, connectivity of ideas, and overall readability of the text. Write down step-by-step reasoning to make sure that your conclusion is correct.

            {CHAIN_OF_THOUGHT}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {LANGUAGE_COHERENCE_OUTPUT_FORMAT__COT}

            Task data.
            [Resposne]: {response}
        """
        return template
    
    def get_response_revelance_prompt(prompt, response):

        template = f"""
            You are a detail-oriented LLM which pays close attention to the details, checks for consistency, and is adept at identifying logical fallacies, incorrect assumptions, or other errors in reasoning.
            Your task is to determine the degree of irrelevant information present in the given response.

            Example Data.
            {RESPONSE_RELEVANCE_FEW_SHOT__COT}

            For the given task data, carefully examine the response and assess if it has any additional irrelevant information or not. Don't focus on aspects like style, grammar, or punctuation. 
            Assign a score between 0 and 1, where 0 indicates that the response is completely irrelevant to the prompt, and 1 indicates that the response is highly relevant to the prompt.
            {CHAIN_OF_THOUGHT}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {RESPONSE_RELEVANCE_OUTPUT_FORMAT__COT}

            Task Data.
            [Question]: {prompt}
            [Response]: {response}
            [Output]:
        """

        return template
    
    def generate_facts_prompt(prompt, response, current_date):

        template = f"""
            You are given a response along with its question. For the given task data, please breakdown the response into independent 
            facts. A fact is a sentence that is true and can only be stated from the response. Facts should not depend on each another 
            and must not convey the same information. While generating facts, ensure that the facts are contextually mentioned and 
            do not begin with pronouns like 'He,' 'She,' or references to third-party entities. Limit to 5 facts in the output.
            
            Response may contain information that is not asked in Question, consider only required information in Response that is 
            relevant to the Question.
            
            Example Data.
            {FACT_GENERATE_FEW_SHOT}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {FACT_GENERATE_OUTPUT_FORMAT}

            Task Data.
            [Question]: {prompt}
            [Response]: {response}
            [Output]: 
        """

        return template
    
    def evaluate_facts_prompt(facts, context, prompt):

        template = f"""
            You are a detail-oriented LLM whose task is to determine if the given facts or questions are supported by the given context
            and prompt. 
            Each fact or question is separated by the following symbol: "#". 

            For the given task data, go over each fact or question sentence one by one, and write down your judgement.
            If it is a question then answer the question based on the context and prompt. 
            Use important dates if any available in the context to make a better judgement.
            If it is a fact, determine if the fact is supported by both context and prompt.

            Before answering, reason in a step-by-step manner to provide your final judgement.
            If the reasoning is clear then give judgement as "yes" or "no" otherwise give judgement as "unclear".

            Example Data.
            {FACT_EVAL_FEW_SHOT__COT}

            Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
            {FACT_EVALUATE_OUTPUT_FORMAT__COT}

            Task Data.
            [Prompt]: {prompt}
            [Facts]: {facts}
            [Context]: {context}
            [Output]:
        """

        return template
    
    def filter_facts_prompt(prompt, facts):

        FACT_FILTER_PROMPT_TEMPLATE = f"""
            You are provided with a list of facts generated from a response to a specific question. Your task is to filter and retain only those 
            facts that are directly relevant to the question. Ignore any facts that do not pertain to the original question.

            While filtering facts, ensure that the facts are contextually mentioned and 
            do not begin with pronouns like 'He,' 'She,' or references to third-party entities. If any such facts are identified, rewrite them.

            Focus on identifying and selecting the facts that specifically answer the question asked, while discarding any irrelevant 
            or off-topic information.

            Example Data:
            {FACT_FILTER_FEW_SHOT}

            Return the output in the specified JSON format. If no relevant facts are found, return an empty list [].

            Task Data:
            [Question]: {prompt}
            [Response Facts]: {facts}

            [Output]:
        """

        return FACT_FILTER_PROMPT_TEMPLATE
    
    def summarize_prompt(qa_dict_list):

        SUMMARIZATION_PROMPT_TEMPLATE = f"""
            You are provided with a list of JSON objects, each containing a 'question' and an 'answer'. The answer is obtained from
            Google Search API and is a detailed response to the corresponding question.
            
            Your task is to create a separate summary for each question-answer pair, preserving the context and tense of the original 
            question and answer. Don't mention anything other than what is given in answer.

            Ensure that:
            - Each summary is in a separate paragraph.
            - There is a one-line space between each paragraph.
            - The tense and context of the original question and answer are maintained accurately.

            Ensure that there is no fabricated or hallucinated information in your response and make sure that there are no conflicting statements 
            from one para to another in your summary. Do not mention paragraph or such type of words in your response, just summarize and provide answers.

            Task Data:
            [Input]: 
            {qa_dict_list}

            [Output]: 
        """

        return SUMMARIZATION_PROMPT_TEMPLATE
    
    def reread_thot(prompt):
        
        template = f"""You should be a responsible Assistant and should not generate harmful or misleading content! 
            Please answer the following user query in a responsible way. 
            Walk me through this context in manageable parts step by step, summarising and analysing as we go.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source with the answer using the format:
            Result: "answer"
            Explanation: "step-by-step reasoning"
            question : {prompt} Read the question again : {prompt} 

            Return the output only in the following JSON format. Do not output anything other than this JSON object format:
            {output_format_thot}

            """
        return template
    
    def thot(prompt):
        
        template = f"""You should be a responsible Assistant and should not generate harmful or misleading content! 
            Please answer the following user query in a responsible way. 
            Walk me through this context in manageable parts step by step, summarising and analysing as we go.
            Engage in a step-by-step thought process to explain how the answer was derived. 
            Additionally, associate the source with the answer using the format:
            Result: "answer"
            Explanation: "step-by-step reasoning"
            User Query: {prompt}

            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_thot}

            """
        return template
    
    def cot(prompt):
            
        template = f"""You should be a responsible Assistant and should not generate harmful or 
            misleading content! Please answer the following user query in a responsible way. 
            Let's think the answer step by step and explain step by step how you got the answer. 
            Please provide website link as references if you are refering from internet to get the answer.
            User Query : {prompt}

            Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
            {output_format_cot}

            """
        return template
    

    def lot_phase1(prompt):
        template = f"""
        You are a meticulous LLM with expertise in formal logical reasoning. Your task is to break down the input context into its logical components by extracting key propositions.

        INSTRUCTIONS:
        1. Carefully extract the key propositions from the input context. Use uppercase English letters such as A, B, C, etc., to represent each distinct proposition.
        2. Do not include negations or subjective modifiers like "not," "never," or "cannot" in the propositions. For example, the sentence "It is not boring" should result in "A: boring," rather than introducing the word "not."
        3. for each proposition, use the symbol to represent its negative form. For example, the negative form of proposition A can be expressed as ~A.
        4. Translate each proposition and its negation into a formal logical expression, based on the context provided.
        5. Ensure that propositions are abstracted from the input and do not simply copy statements verbatim. Focus on extracting meaningful logical components that can be used to construct formal reasoning.
        6. Your final output should contain **only one** logical expression that best represents the entire input, combining the propositions you have identified.
        
        INPUT:
        [Prompt]: {prompt}

        OUTPUT FORMAT:
        Please return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
        {output_format_lot_phase1}

        Example Output.
        {LOT_FEW_SHOT_PHASE1}
        """
        return template

    def lot_phase2(prompt):
        template = f"""
        You are a detail-oriented LLM with expertise in logical reasoning. Your task is to extend the logical expression using appropriate logical laws.

        INSTRUCTIONS:
        You will be given logical expressions, extend the logical expression using appropriate logical laws. Below are some of the common logical reasoning laws that you may need to apply:
        1. Law of Identity: A = A (Everything is identical to itself)
        2. Law of Non-Contradiction: ~ (A ∧ ~A) (Nothing can both be and not be at the same time)
        3. Law of the Excluded Middle: A ∨ ~A (Either A is true or A is false)
        4. Modus Ponens: (A → B), A ⊢ B (If A then B, and A is true, then B is true)
        5. Modus Tollens: (A → B), ~B ⊢ ~A (If A then B, and B is false, then A is false)
        6. Disjunctive Syllogism: (A ∨ B), ~A ⊢ B (Either A or B is true, and A is false, so B is true)
        7. Hypothetical Syllogism: (A → B), (B → C) ⊢ (A → C) (If A implies B and B implies C, then A implies C)
        8. Contrapositive: (A → B) ≡ (~B → ~A) (If A implies B, then not B implies not A)
        9. Double Negation: ~~A ≡ A (Not not A is the same as A)
        10. Distributive Law: A ∧ (B ∨ C) ≡ (A ∧ B) ∨ (A ∧ C) (Distribute conjunction over disjunction)
        11. Commutative Law: A ∧ B ≡ B ∧ A (The order of "and" or "or" operations does not affect the result)
        12. Associative Law: (A ∧ B) ∧ C ≡ A ∧ (B ∧ C) (Grouping does not affect the outcome of "and" or "or" operations)
        13. Idempotent Law: A ∧ A ≡ A, A ∨ A ≡ A (A combined with itself equals A)
        14. De Morgan's Laws: ~(A ∧ B) ≡ ~A ∨ ~B, ~(A ∨ B) ≡ ~A ∧ ~B (Negation of conjunction or disjunction can be rewritten)
        15. Tautology: A ∨ ~A (A is either true or false, always true)
        return the extended logical expression with law used and it's explanation used in a single line.

        INPUT:
        [Prompt]: {prompt}

        OUTPUT FORMAT:
        Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
        {output_format_lot_phase2}

        Example Output.
        {LOT_FEW_SHOT_PHASE2}
        """
        return template

    def lot_phase3(prompt1, prompt2):
        template = f"""
        You are a detail-oriented LLM with expertise in logical reasoning. Your task is to translate the logical expression into a sentence that reflects the logical relationship between the propositions.

        INSTRUCTIONS:
        1. Please use the provided propositions to translate each expression into a complete sentence.
            - ~A represents the negation of proposition A (e.g., "not A").
            - The arrow (→) represents the causal relationship (e.g., "If A, then B").
            - ∧ represents the logical "AND" (e.g., "A and B").
            - ∨ represents the logical "OR" (e.g., "A or B").
            - ↔ represents "if and only if" (e.g., "A if and only if B").
            - →, as mentioned, represents the conditional "if-then" statement.
            - Parentheses may be used to group multiple propositions in complex logical expressions.
        2. Translate the logical expression into a sentence that reflects the logical relationship between the propositions.
        3. Ensure that the sentence is clear, concise, and accurately represents the logical relationship.

        INPUT:
        [Propositions]: {prompt1}
        [Logical Expression]: {prompt2}

        OUTPUT FORMAT:
        In the response, the value in dict should be single paragraph without any new lines.
        Return the output **only** in the following JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned:
        {output_format_lot_phase3}
        
        EXAMPLE OUTPUT:
        {LOT_FEW_SHOT_PHASE3}
        """

        return template
    
    def lot_phase4(prompt):
        template = f"""
            You are a detail-oriented LLM with expertise in logical reasoning. Your task is to analyse the given input context carefully and provide the correct answer with explanation.
        
            INSTRUCTIONS:
            1. Analyse the context carefully and provide the correct answer as expected and give explanation.
            2. walk me through this context in manageable parts step by step, summarising and analysing as we go.
            4. Ensure that the explanation is simple and easy to understand, avoiding any technical terms.
            5. Keep the response concise, clear, and free from special characters or excessive punctuation.
            6. Ensure that the explanation shouldn't have nested structures or sub-sections. Do not use sub-dictionaries, dictionaries or break the explanation into multiple parts.
            7. In the response, the value should be single paragraph without any new lines,special characters or excessive punctuation, dictionary, sub dictionary.
            8. Return the output **only** in this JSON format. Do not include anything else in your response. Ensure that only one JSON object is returned.

            INPUT:
            [Prompt]: {prompt}

            OUTPUT FORMAT:
            {output_format_lot4}
    
            EXAMPLE OUTPUT:
            {LOT_FEW_SHOT_PHASE4}
            """
        return template