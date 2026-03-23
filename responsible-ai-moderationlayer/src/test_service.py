'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from service.service import identifyEmoji,emojiToText,wordToEmoji


def test_pass_identify_Emoji1():
    '''unit test for service.py method identifyEmoji()'''
    text="Officially in spring weather 🌸🥰"
    expected_dict={'value': ['🌸', '🥰'], 'location': [[29, 30], [30, 31]], 'mean': [':cherry_blossom:', ':smiling_face_with_hearts:'], 'flag': True}
    response=identifyEmoji(text=text)
    assert response==expected_dict

def test_fail_identify_Emoji():
    '''unit test for service.py method identifyEmoji()'''
    text="I'm going to fail this exam. 🙄💣"
    expected_dict={'value': ['🙄'], 'location': [[29, 30]], 'mean': [':face_with_rolling_eyes:'], 'flag': True}
    response=identifyEmoji(text=text)
    assert response!=expected_dict

def test_pass_identify_Emoji2():
    '''unit test for service.py method identifyEmoji()'''
    text="Officially in spring weather"
    expected_dict={'value': [], 'location': [], 'mean': [], 'flag': False}
    response=identifyEmoji(text=text)
    assert response==expected_dict

def test_pass_emojiToText():
    """unit test for service.py method emojiToText()"""
    text="I'm so angry right now! I want to punch someone. 😡👊"
    emoji_dict={'value': ['😡', '👊'], 'location': [[49, 50], [50, 51]], 'mean': [':pouting_face:', ':oncoming_fist:'], 'flag': True}
    expected_output=("I'm so angry right now! I want to punch someone.  pouting face oncoming fist", "I'm so angry right now! I want to punch someone.   ", {'😡': 'pouting face', '👊': 'oncoming fist'})
    response=emojiToText(text=text,emoji_dict=emoji_dict)
    assert response==expected_output

def test_pass_wordToEmoji():
    """unit test for service.py method wordToEmoji()"""
    text="Stephen Miller is a complete waste of space and everything else.🖕🤮💩🖕🏾☝🏾"
    current_emoji_dict={'🖕🏾☝🏾': 'fuck you gesture','🖕': 'fuck you gesture','🤮': 'face vomiting','💩': 'pile of poo'}
    result=["waste","fuck","fuck"]
    expected_output=['waste','🖕🏾☝🏾','🖕']
    response=wordToEmoji(text=text,current_emoji_dict=current_emoji_dict,result=result)
    assert response==expected_output

    

     

