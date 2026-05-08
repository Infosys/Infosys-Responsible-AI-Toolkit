'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


from pydantic import BaseModel
from typing import List, Dict,Optional
class ToxicityThresholds(BaseModel):
    ToxicityThreshold: float
    SevereToxicityThreshold: float
    ObsceneThreshold: float
    ThreatThreshold: float
    InsultThreshold: float
    IdentityAttackThreshold: float
    SexualExplicitThreshold: float

class RestrictedtopicDetails(BaseModel):
    RestrictedtopicThreshold: float
    Restrictedtopics: List[str]

class CustomTheme(BaseModel):
    Themename: str
    Themethresold: float
    ThemeTexts: List[str]

class ModerationCheckThresholds(BaseModel):
    PromptinjectionThreshold: float
    JailbreakThreshold: float
    PiientitiesConfiguredToBlock: List[str]
    RefusalThreshold: float
    ToxicityThresholds: ToxicityThresholds
    ProfanityCountThreshold: int
    RestrictedtopicDetails: RestrictedtopicDetails
    CustomTheme: CustomTheme

class ModerationRequestData(BaseModel):
    AccountName: str
    userid: str
    PortfolioName: str
    lotNumber: int
    translate: str
    EmojiModeration: str
    Prompt: str
    ModerationChecks: List[str]
    ModerationCheckThresholds: ModerationCheckThresholds