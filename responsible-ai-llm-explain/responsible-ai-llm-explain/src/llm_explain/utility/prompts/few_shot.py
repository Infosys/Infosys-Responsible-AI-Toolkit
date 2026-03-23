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
one_shot_sentiment_analysis = """
    Prompt: Unfortunately the movie served with hacked script but the actors performed well
    {
        "Sentiment": "Negative",
        "Keywords": ["unfortunately", "hacked"],
        "Explanation": "The model predicted the input as Negative because it anchored or focused on the word "unfortunately" and "hacked" in your input. In this context, the model likely learned that when someone mentions a hacked script or unfortunately, it usually indicates a negative opinion about a movie. Despite the actors performing well, the emphasis on the script being hacked led the model to classify the overall sentiment as negative. This shows that the model paid close attention to specific keywords, like "unfortunately" and "hacked" to make its prediction.",
        "token_importance_mapping": [
                                        {"token": "Unfortunately", "importance_score": 80, "position": 0}, 
                                        {"token": "hacked", "importance_score": 90, "position": 4}
                                    ]
    }
"""
# TokenImportance
one_shot_token_importance = """
    {
        "Token": ["Who", "are", "the", "co-founders", "of", "Infosys?"],
        "Importance Score": [1, 0.5, 0.5, 1, 0.5, 1],
        "Position": [0, 1, 2, 3, 4, 5]
    }
"""
# Tone Analysis
few_shot_examples_tone_analysis = """
    [Response]: Absolutely! I'm thrilled about the opportunity and eager to learn more about the position.
    [Output]: 
    {
        "Reasoning": "The text uses positive and enthusiastic language, along with keywords like 'thrilled' and 'eager,' indicating a strong interest in the position.",
        "Tone": ["Positive", "Formal"]
        "Score": 0.8
        "Recommendation":
    }

    [Response]: Ugh, another interview? Why do I even bother?
    [Output]:
    {
        "Reasoning": "The text expresses negativity and frustration with keywords like ugh and bother.",
        "Tone": ["Negative", "Informal"]
        "Score": 0.2
        "Recommendation":
    }

    [Response]: Congratulations on your promotion! You absolutely deserve it!
    [Output]:
    {
        "Reasoning": "The text uses positive and celebratory language with emojis and encouraging words.",
        "Tone": ["Positive", "Informal"]
        "Score": 0.5
        "Recommendation":
    }
"""

# Response Coherence
LANGUAGE_COHERENCE_FEW_SHOT__COT = """
    [Response]: Exercise is beneficial for both physical and mental health. It strengthens the body and uplifts the mind.
    [Output]:
    {
        "Reasoning": "The text is coherent and effectively conveys the message with clear organization of ideas.",
        "Score": 5
    }

    [Response]: Regular exercise contributes to overall well-being by enhancing physical strength and mental clarity.
    [Output]:
    {
        "Reasoning": "The text maintains coherence by linking ideas logically, providing a clear flow of information.",
        "Score": 4
    }

    [Response]: Exercise good. Health. Make body strong. Help mind. Benefits many.
    [Output]:
    {
        "Reasoning": "The text lacks coherence, as it presents fragmented ideas without clear connections.",
        "Score": 2
    }
"""

# Response Relevance
RESPONSE_RELEVANCE_FEW_SHOT__COT = """
[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{
    "Reasoning": "While the given response provides information about the birth data, nationality and occupation of Lionel Messi, it includes some irrelevant details about Messi's career such as association to multiple clubs and trophies won.",
    "Score": 0.5
}

[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times. During his time with Barcelona, Barcelona featured star players like Neymar, Andres Iniesta and was managed by Luis Enrique.
[Output]:
{
    "Reasoning": "While the given response provides information about the birth data, nationality and occupation of Lionel Messi, it includes a lot of irrelevant inforamtion such as details about Messi's career and Barcelona club.",
    "Choice": 0.0
}
"""

# Fact Generation
FACT_GENERATE_FEW_SHOT = """
[Question]: Which is the tallest monument in Paris?
[Response]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]: 
[
    {
        "Fact": "The Eiffel Tower is located in Paris."
    },
    {
        "Fact": "The Eiffel Tower is the tallest structure in Paris."
    },
    {
        "Fact": "The Eiffel Tower is very old."
    },
    {
        "Fact": "The Eiffel Tower is very old."
    },
]

[Question]: who is the Chief minister of Andhra Pradesh ?
[Response]: As of my last training data in October 2021, the Chief Minister of Andhra Pradesh is Yeduguri Sandinti Jaganmohan Reddy. He assumed office on 30th May 2019. He is a member of the Yuvajana Sramika Rythu Congress Party (YSR Congress Party). However, you should verify from a reliable source for the most current information, as political positions can change.
[Output]: 
[
    {
        "Fact": "The Chief Minister of Andhra Pradesh is Yeduguri Sandinti Jaganmohan Reddy."
    },
    {
        "Fact": "Yeduguri Sandinti Jaganmohan Reddy assumed office on 30th May 2019."
    },
    {
        "Fact": "Yeduguri Sandinti Jaganmohan Reddy is a member of the Yuvajana Sramika Rythu Congress Party (YSR Congress Party)."
    }
]

[Question]: Is Leaning Tower of Pisa, which is located in Italy, the oldest monument in Europe?
[Response]: No
[Output]: 
{
    "Fact": "The Leaning Tower of Pisa is not the oldest monument in Europe."
}
"""

# Factuality Evaluation
FACT_EVAL_FEW_SHOT__COT = """
[Facts]: ["1. The Eiffel Tower is located in Paris.", "2. The Eiffel Tower is the tallest structure in Paris.", "3. The Eiffel Tower is very old."]
[Context]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]: 
{
    "Result": [
        {
            "Fact": "1. The Eiffel Tower is located in Paris.",
            "Reasoning": "The context explicity states that Paris, one of the most visited monuments in the world is located in Paris.",
            "Judgement": "yes"
        },
        {
            "Fact": "2. The Eiffel Tower is the tallest structure in Paris.",
            "Reasoning": "While the context speaks about the popularity of Effiel Tower, it has no mention about its height or whether it is tallest or not.",
            "Judgement": "no"
        },
        {
            "Fact": "3. The Eiffel Tower is very old.",
            "Reasoning": "While the context mentions that the Eiffel Tower was built in 1880s, it doesn't clarify what very old means.",
            "Judgement": "unclear"
        },
    ]
}
"""

# Filter Facts
FACT_FILTER_FEW_SHOT = """
[Question]: What are the main components of a computer?
[Response Facts]: 
[
    "A computer has a CPU, which is the brain of the computer.",
    "Computers are widely used in schools and offices.",
    "A computer's motherboard connects all the components.",
    "The CPU can be overclocked for better performance.",
    "Computers were invented in the 20th century."
]

[Output]:
[
    "A computer has a CPU, which is the brain of the computer.",
    "A computer's motherboard connects all the components.",
    "The CPU can be overclocked for better performance."
]

[Question]: What are the benefits of exercise?
[Response Facts]: 
[
    "Regular exercise improves cardiovascular health.",
    "Many people exercise in the morning.",
    "Exercise helps maintain a healthy weight.",
    "A balanced diet is also important for health.",
    "Exercise can reduce the risk of chronic diseases."
]

[Output]:
[
    "Regular exercise improves cardiovascular health.",
    "Exercise helps maintain a healthy weight.",
    "Exercise can reduce the risk of chronic diseases."
]
"""

LOT_FEW_SHOT_PHASE1 = """
"Propositions": {
        "A": "have keyboarding skills"; 
        "B": "be able to use a computer"; 
        "C": "be able to write your essays using a word processing program"
    },
    "Logical Expression": "¬A → ¬B , ¬B →¬C"
}
"""

LOT_FEW_SHOT_PHASE2 = """
{
    "Extended Logical Expression" : "C → A",
    "Law Used": "Law of Conjunction.The Double Negation Law states that the negation of the negation of a proposition is logically equivalent to the proposition itself (¬(¬𝑃)≡𝑃¬(¬P)≡P)"
}
"""

LOT_FEW_SHOT_PHASE3 = """
{
    "Extended Logical Information": "If you are able to write your essays using a word processing program,then you have keyboarding skills."
}
"""

LOT_FEW_SHOT_PHASE4 = """
{
    "Explanation": "If you are able to write your essays using a word processing program, then you have at least some keyboarding skills"
}
"""