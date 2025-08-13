'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# Add new moderation handler class
import requests
import urllib3
import logging
from app.config.logger import CustomLogger
import os
log = CustomLogger()
from dotenv import load_dotenv
load_dotenv()
log_file = "run.log"
logging.basicConfig(filename=log_file, level=logging.INFO)
log = logging.getLogger(__name__)

class ModerationHandler:
    def __init__(self, moderation_url=os.getenv("MODERATION_API")):
        self.url = moderation_url
        moderation_url=moderation_url
    def check_moderation(self, prompt: str) -> dict:
        try:
            payload = {
                "AccountName": "",
                "userid": "None", 
                "PortfolioName": "",
                "lotNumber": "1",
                "Prompt": prompt,
                "ModerationChecks": [
                    "PromptInjection", "JailBreak", "Toxicity",
                    "Piidetct", "Refusal", "Profanity",
                    "RestrictTopic", "TextQuality", "CustomizedTheme"
                ],
                "ModerationCheckThresholds": {
                    "PromptinjectionThreshold": 0.7,
                    "JailbreakThreshold": 0.7,
                    "PiientitiesConfiguredToDetect": [
                        "PERSON", "LOCATION", "DATE", "AU_ABN", "AU_ACN",
                        "AADHAR_NUMBER", "AU_MEDICARE", "AU_TFN", "CREDIT_CARD",
                        "CRYPTO", "DATE_TIME", "EMAIL_ADDRESS", "ES_NIF",
                        "IBAN_CODE", "IP_ADDRESS", "IT_DRIVER_LICENSE",
                        "IT_FISCAL_CODE", "IT_IDENTITY_CARD", "IT_PASSPORT",
                        "IT_VAT_CODE", "MEDICAL_LICENSE", "PAN_Number",
                        "PHONE_NUMBER", "SG_NRIC_FIN", "UK_NHS", "URL",
                        "PASSPORT", "US_ITIN", "US_PASSPORT", "US_SSN", "IN_PAN"
                    ],
                    "PiientitiesConfiguredToBlock": [
                        "PAN_Number", "EMAIL_ADDRESS", "IN_PAN", "IN_AADHAAR"
                    ],
                    "RefusalThreshold": 0.7,
                    "ToxicityThresholds": {
                        "ToxicityThreshold": 0.6,
                        "SevereToxicityThreshold": 0.6,
                        "ObsceneThreshold": 0.6,
                        "ThreatThreshold": 0.6,
                        "InsultThreshold": 0.6,
                        "IdentityAttackThreshold": 0.6,
                        "SexualExplicitThreshold": 0.6
                    },
                    "ProfanityCountThreshold": 1,
                    "RestrictedtopicDetails": {
                        "RestrictedtopicThreshold": 0.7,
                        "Restrictedtopics": [
                            "terrorism", "explosives", "nudity", "cruelty",
                            "cheating", "fraud", "crime", "hacking", "immoral",
                            "unethical", "illegal", "robbery", "forgery",
                            "misinformation"
                        ]
                    },
                    "CustomTheme": {
                        "Themename": "string",
                        "Themethresold": 0.6,
                        "ThemeTexts": ["Sall", "Text2", "Text3"]
                    }
                }
            }
            log.info("evaluated prompt ")
            log.info(prompt)
            log.info(os.getenv("MODERATION_API"))
            response = requests.post(os.getenv("MODERATION_API"), json=payload,verify=False)
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "moderationResults": {
                        "summary": {
                            "status": "FAILED",
                            "reason": ["Moderation API Error"]
                        }
                    }
                }
        except Exception as e:
            log.error(f"Moderation check failed: {str(e)}")
            return {
                "moderationResults": {
                    "summary": {
                        "status": "FAILED",
                        "reason": str(e)
                    }
                }
            }
