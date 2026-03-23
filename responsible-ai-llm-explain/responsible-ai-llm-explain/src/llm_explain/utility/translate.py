'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import requests
from langcodes import *
from llm_explain.config.logger import CustomLogger
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

log = CustomLogger()


class Translate:
    def translate(text):
        try:
            #text = input()
            source = "auto"
            url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl=en&dt=t&dt=bd&dj=1&q={text}'
            resp = requests.get(url)
            # translated_text = resp.json()['sentences'][0]['trans']
            translated_text_list = [l['trans'] for l in resp.json()['sentences']]
            translated_text = "".join(translated_text_list)
            langcode = resp.json()['src'].split('-')[0]
            language = Language.make(language=langcode).display_name()
            return translated_text,language
        except Exception as e:
            log.error(f"Exception: {e}")
        
    def azure_translate(text):
        # set `<your-key>`, `<your-endpoint>`, and  `<region>` variables with the values from the Azure portal
        key = os.getenv("AZURE_TRANSLATE_KEY")
        endpoint = os.getenv("AZURE_TRANSLATE_ENDPOINT")
        region = os.getenv("AZURE_TRANSLATE_REGION")

        credential = TranslatorCredential(key, region)
        text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)

        try:
            #source_language = "en"
            target_languages = ["en"] #["es", "it"]
            input_text_elements = [ InputTextItem(text = text) ]

            response = text_translator.translate(content = input_text_elements, to = target_languages)#, from_parameter = source_language)
            translation = response[0] if response else None

            if translation:
                langcode = translation['detectedLanguage']['language']
                language = Language.make(language=langcode).display_name()
                for translated_text in translation.translations:
                    return translated_text.text, language

        except HttpResponseError as exception:
            log.error(f"Error Code: {exception.error.code}")
            log.error(f"Message: {exception.error.message}")