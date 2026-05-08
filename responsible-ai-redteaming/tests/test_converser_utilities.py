'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pytest


def test_get_model_path_and_template_gpt4():
    """Test get_model_path_and_template with GPT-4"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-4")
    assert path == "gpt-4"
    assert template == "gpt-4"

def test_get_model_path_and_template_gpt35():
    """Test get_model_path_and_template with GPT-3.5"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-3.5-turbo")
    assert path == "gpt-3.5-turbo"
    assert template == "gpt-3.5-turbo"

def test_get_model_path_and_template_claude():
    """Test get_model_path_and_template with Claude"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("claude-instant-1")
    assert path == "claude-instant-1"
    assert template == "claude-instant-1"





def test_clean_attacks_and_convs_valid():
    """Test clean_attacks_and_convs with valid data"""
    from app.utility.conversers import clean_attacks_and_convs
    attacks = ["attack1", "attack2", "attack3"]
    convs = ["conv1", "conv2", "conv3"]
    cleaned_attacks, cleaned_convs = clean_attacks_and_convs(attacks, convs)
    assert len(cleaned_attacks) == 3
    assert len(cleaned_convs) == 3
    assert cleaned_attacks == attacks
    assert cleaned_convs == convs

def test_clean_attacks_and_convs_with_none():
    """Test clean_attacks_and_convs with None values"""
    from app.utility.conversers import clean_attacks_and_convs
    attacks = ["attack1", None, "attack3"]
    convs = ["conv1", "conv2", "conv3"]
    cleaned_attacks, cleaned_convs = clean_attacks_and_convs(attacks, convs)
    assert len(cleaned_attacks) == 2
    assert len(cleaned_convs) == 2
    assert None not in cleaned_attacks

def test_clean_attacks_and_convs_all_none():
    """Test clean_attacks_and_convs with all None"""
    from app.utility.conversers import clean_attacks_and_convs
    attacks = [None, None, None]
    convs = ["conv1", "conv2", "conv3"]
    cleaned_attacks, cleaned_convs = clean_attacks_and_convs(attacks, convs)
    # When all None, returns (None, None) due to exception
    assert cleaned_attacks is None and cleaned_convs is None

def test_clean_attacks_and_convs_empty():
    """Test clean_attacks_and_convs with empty lists"""
    from app.utility.conversers import clean_attacks_and_convs
    attacks = []
    convs = []
    result = clean_attacks_and_convs(attacks, convs)
    # Should handle empty lists gracefully
    assert result is not None

def test_get_model_path_gpt4_turbo():
    """Test get_model_path_and_template with gpt-4-turbo"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-4-turbo")
    assert path == "gpt-4-1106-preview"
    assert template == "gpt-4-1106-preview"

def test_get_model_path_gpt4o():
    """Test get_model_path_and_template with gpt-4o"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-4o")
    assert path == "gpt-4-1106-preview"

def test_get_model_path_gpt4o_mini():
    """Test get_model_path_and_template with gpt-4o-mini"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-4o-mini-eastus2-rai")
    assert path == "gpt-4-1106-preview"

def test_get_model_path_gemini_pro():
    """Test get_model_path_and_template with gemini-pro"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gemini-1.5-pro")
    assert path == "gemini-1.5-pro"
    assert template == "gemini-1.5-pro"

def test_get_model_path_gemini_flash():
    """Test get_model_path_and_template with gemini flash"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gemini-1.5-flash-8b")
    assert path == "gemini-1.5-pro"

def test_get_model_path_gemini_2_flash():
    """Test get_model_path_and_template with gemini 2.0 flash"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gemini-2.0-flash")
    assert path == "gemini-2.0-flash"
    assert template == "gemini-2.0-flash"

def test_get_model_path_claude_2():
    """Test get_model_path_and_template with claude-2"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("claude-2")
    assert path == "claude-2"



def test_get_model_path_invalid_model():
    """Test get_model_path_and_template with invalid model raises error"""
    from app.utility.conversers import get_model_path_and_template
    with pytest.raises(ValueError):
        get_model_path_and_template("invalid-model-xyz")

def test_get_model_path_gpt35_new():
    """Test get_model_path_and_template with gpt-35-turbo_new"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-35-turbo_new")
    assert path == "gpt-3.5-turbo"

def test_get_model_path_gpt3():
    """Test get_model_path_and_template with gpt-3"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-3")
    assert path == "gpt-3.5-turbo"

def test_get_model_path_gpt4o_westus():
    """Test get_model_path_and_template with gpt-4o-westus"""
    from app.utility.conversers import get_model_path_and_template
    path, template = get_model_path_and_template("gpt-4o-westus")
    assert path == "gpt-4"
    assert template == "gpt-4"

def test_prune_returns_tuple():
    """Test prune function returns tuple of results"""
    from app.utility.conversers import prune
    attack_params = {'width': 2}
    sorting_score = [10, 5, 8, 2]
    on_topic_scores = [9, 4, 7, 1]
    adv_prompt_list = ['p1', 'p2', 'p3', 'p4']
    improv_list = ['i1', 'i2', 'i3', 'i4']
    convs_list = ['c1', 'c2', 'c3', 'c4']
    extracted_attack_list = ['e1', 'e2', 'e3', 'e4']
    
    result = prune(
        on_topic_scores=on_topic_scores,
        sorting_score=sorting_score,
        adv_prompt_list=adv_prompt_list,
        improv_list=improv_list,
        convs_list=convs_list,
        extracted_attack_list=extracted_attack_list,
        attack_params=attack_params
    )
    
    assert isinstance(result, tuple)
    assert len(result) == 7
    assert result[0] is not None
    assert len(result[2]) <= 2

def test_prune_filters_zero_scores():
    """Test prune filters out zero and negative scores"""
    from app.utility.conversers import prune
    attack_params = {'width': 5}
    sorting_score = [10, 0, -1, 5]
    on_topic_scores = [9, 0, 0, 4]
    adv_prompt_list = ['p1', 'p2', 'p3', 'p4']
    improv_list = ['i1', 'i2', 'i3', 'i4']
    convs_list = ['c1', 'c2', 'c3', 'c4']
    extracted_attack_list = ['e1', 'e2', 'e3', 'e4']
    
    result = prune(
        on_topic_scores=on_topic_scores,
        sorting_score=sorting_score,
        adv_prompt_list=adv_prompt_list,
        improv_list=improv_list,
        convs_list=convs_list,
        extracted_attack_list=extracted_attack_list,
        attack_params=attack_params
    )
    
    assert len(result[2]) == 2

def test_prune_with_judge_scores():
    """Test prune with judge_scores parameter"""
    from app.utility.conversers import prune
    attack_params = {'width': 3}
    sorting_score = [10, 8, 6]
    on_topic_scores = [9, 7, 5]
    judge_scores = [9, 7, 5]
    adv_prompt_list = ['p1', 'p2', 'p3']
    improv_list = ['i1', 'i2', 'i3']
    convs_list = ['c1', 'c2', 'c3']
    extracted_attack_list = ['e1', 'e2', 'e3']
    
    result = prune(
        on_topic_scores=on_topic_scores,
        sorting_score=sorting_score,
        judge_scores=judge_scores,
        adv_prompt_list=adv_prompt_list,
        improv_list=improv_list,
        convs_list=convs_list,
        extracted_attack_list=extracted_attack_list,
        attack_params=attack_params
    )
    
    assert result[1] is not None
    assert len(result[1]) == 3

def test_prune_minimum_elements():
    """Test prune ensures at least 2 elements even with all zero scores"""
    from app.utility.conversers import prune
    attack_params = {'width': 3}
    sorting_score = [0, 0, 0]
    on_topic_scores = [0, 0, 0]
    adv_prompt_list = ['p1', 'p2', 'p3']
    improv_list = ['i1', 'i2', 'i3']
    convs_list = ['c1', 'c2', 'c3']
    extracted_attack_list = ['e1', 'e2', 'e3']
    
    result = prune(
        on_topic_scores=on_topic_scores,
        sorting_score=sorting_score,
        adv_prompt_list=adv_prompt_list,
        improv_list=improv_list,
        convs_list=convs_list,
        extracted_attack_list=extracted_attack_list,
        attack_params=attack_params
    )
    
    assert len(result[2]) >= 2


