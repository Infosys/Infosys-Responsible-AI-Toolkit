'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import json
import os
import sys
class Navi_ToneScoring_Templates:
    tone_score_data = ""
    sentiment_chart_data =""
    word_book=""
    tonespecific_phrase=""
    def __init__(self) -> None:
        EXE_CREATION = os.getenv("EXE_CREATION")
        if(EXE_CREATION == "True"):
            # Get the base path (this will be the path to the executable when running the bundled app)
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        else:
            ## BELOW ONE FOR NORMAL APP RUNNING
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_path, "data/Navi_ToneScoring_Data.json"), "r",encoding="utf8") as f:
            self.tone_score_data = json.load(f)
            f.close()
        with open(os.path.join(base_path, "data/Navi_SentimentChart_data.json"), "r",encoding="utf8") as f:
            self.sentiment_chart_data = json.load(f)
            f.close()
        with open(os.path.join(base_path, "data/Navi_wordbook_Data.json"), "r",encoding="utf8") as f:
            self.word_book = json.load(f)
            f.close()
        with open(os.path.join(base_path, "data/NAVI_ToneSpecific_Phrases_Data.json"), "r",encoding="utf8") as f:
            self.tonespecific_phrase = json.load(f)
            f.close()
    text ="""{input_text}"""
    
    def render_Template(self):
        NAVI_TONEMODERATION_PROMPT_MESSAGE =[
                    {"role": "system","content": """You are expert in identifying customer sentiment through user interaction.You should carefully identify user sentiment as well Tone . Once the response generated you should identify response tone using the response generated. Your task is to correct the response so that it aligns to customer sentiment and tone as well. Here is the text:{raw_text_dumps}"""},
                    {"role": "system","content": """Instructions:
                    Sentiment Categories: Negative, Positive, Neutral
                    Tone Categories: DISAPPOINTED, FRUSTRATED, NEUTRAL, HAPPY, ENTHUSIASTIC, JOYFUL, UPBEAT, UNHAPPY, BORED
                    Specifica Domain: LNC, Sales, Deals,Decision supporting

                    When customer sentiment is positive & Response Tone is neutral:
                    a. Specific domain: Advisory role, Suggestive, Resourceful tone.
                    b. Generic domain: Expert role, Delightful tone.
                    c. Support domain: Support role, Empathetic (if unhappy), Supportive, Resourceful tones.

                    When customer sentiment is positive & Response Tone is positive: No tone change in response.

                    When customer sentiment is negative & Response Tone is positive:
                    a. Specific domain: Advisory role, Empathetic, Suggestive tones.
                    b. Generic domain: Expert role, Informative, Persuasive tones.
                    c. Support domain: Support role, Empathetic (if unhappy), Supportive, Resourceful tones.

                    When customer sentiment is negative & Response Tone is neutral:
                    a. Specific domain: Advisory role, Suggestive, Encouraging tones.
                    b. Generic domain: Expert role, Informative, Empathetic tones.
                    c. Support domain: Support role, Informative, Empathetic tones.

                    When customer sentiment is negative & Response Tone is negative:
                    a. Specific domain: Advisory role, Empathetic, Suggestive, Resourceful, Encouraging tones.
                    b. Generic domain: Expert role, Informative, Encouraging tones.
                    c. Support domain: Support role, Supportive, Empathetic tones.
                     
                    % Description of the sentiment chart  (JSON): {self.sentiment_chart_data}
                    % Description of the tone score  (JSON): {self.tone_score_data}
                      """},
                    {"role": "system", "content":  f"sentiment tells you how user is feeling & this you will be to get from prompt.% Description of the sentiment chart  (JSON): {self.sentiment_chart_data} " },
                   {"role": "system", "content":  f"% Description of the tone score  (JSON): {self.tone_score_data} " },
                   {"role": "system", "content":  f"% Description of the Word Book  (JSON): {self.word_book} " },
                   {"role": "system", "content":  f"When being resourceful,informative,Suggestive elobarate your suggestions , information, resource information with list of information" },
                   {"role": "system", "content":  f"Provide the output in JSON format which will have  keys emotion,Tone Score,role,Sentiment,Domain,outputBeforemoderation,outputAfterSentimentmoderation " },
                   {"role": "system", "content":  f"For outputAfterSentimentmoderation try to take suitable content  from : {self.tonespecific_phrase}" },
                   {"role": "user", "content":  f"""{self.text} \n Remember, you are a responsible ChatGPT and good at avoiding generating harmful or misleading content!""" }
                ]
        return NAVI_TONEMODERATION_PROMPT_MESSAGE