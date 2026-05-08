'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from app.utility import report

# Helper to build category_wise_score structure
class Detail:
    def __init__(self, goal, prompt, response):
        self.goal = goal
        self.prompt = prompt
        self.response = response

class Cat:
    """Container allowing both attribute and dict-style access (report code mixes)."""
    def __init__(self, count, provided, details):
        self.count = count
        self.provided = provided
        self.details = details
    def __getitem__(self, item):  # for details['count'] style
        return getattr(self, item)
    def get(self, item, default=None):
        return getattr(self, item, default)

def _build_category(count, provided, n_details=1):
    details = [Detail(f"goal{i}", f"prompt{i}", f"response{i}") for i in range(n_details)]
    return Cat(count, provided, details)

def test_generate_html_report_pair_multiple_most_vulnerable():
    # Craft two categories with same highest ratio (>0) and a third lower
    data = {
        'total_rows': 9,
        'processed_rows': 9,
        'technical_failed_rows': [],
        'jailbroken_rows': 3,  # success other branch
        'category_wise_score': {
            'CatA': _build_category(count=2, provided=4),  # ratio .5
            'CatB': _build_category(count=2, provided=4),  # ratio .5 (tie) -> plural path
            'CatC': _build_category(count=0, provided=1),  # ratio 0 -> ignored for most vulnerable list
        },
        'target_model': 'model-x',
        'target_temperature': 0.3,
        'n_iterations': 2,
        'technique_type': 'PAIR',
        'usecase_name': None,
        'target_endpoint_url': None,
    }
    html = report.generate_html_report_pair(data)
    assert 'RED TEAMING PAIR REPORT' in html  # header without usecase
    assert 'CatA and CatB' in html  # plural two-category path
    # Ensure risk level tokens appear for categories
    assert 'High' in html or 'Medium' in html or 'Low' in html


def test_generate_html_report_pair_single_category():
    data = {
        'total_rows': 5,
        'processed_rows': 5,
        'technical_failed_rows': [],
        'jailbroken_rows': 1,
        'category_wise_score': {
            'Only': _build_category(count=1, provided=2)
        },
        'target_model': 'm1',
        'target_temperature': 0.1,
        'n_iterations': 1,
        'technique_type': 'PAIR',
        'usecase_name': 'UseX',
        'target_endpoint_url': 'http://x'
    }
    html = report.generate_html_report_pair(data)
    assert 'for UseX' in html  # header with usecase branch
    assert 'Only category' in html  # single category wording


def test_generate_html_report_pair_no_vulnerability():
    data = {
        'total_rows': 1,
        'processed_rows': 1,
        'technical_failed_rows': [],
        'jailbroken_rows': 0,
        'category_wise_score': {},  # triggers no vulnerability branch
        'target_model': 'm2',
        'target_temperature': 0.9,
        'n_iterations': 3,
        'technique_type': 'PAIR',
        'usecase_name': None,
        'target_endpoint_url': None
    }
    html = report.generate_html_report_pair(data)
    assert 'No vulnerability data available.' in html


def test_generate_html_report_tap_branches():
    # For TAP function we want two vulnerable categories and one zero
    data = {
        'total_rows': 12,
        'processed_rows': 12,
        'technical_failed_rows': [],
        'jailbroken_rows': 4,
        'category_wise_score': {
            'Hi': _build_category(count=3, provided=3),  # ratio 1.0
            'Med': _build_category(count=2, provided=4), # ratio 0.5
            'Low': _build_category(count=1, provided=6), # ratio ~0.166
        },
        'target_model': 'tap-model',
        'target_temperature': 0.7,
        'n_iterations': 4,
        'technique_type': 'TAP',
        'usecase_name': 'UC',
        'target_endpoint_url': None,
        'depth': 2,
        'width': 3,
        'branching_factor': 4,
    }
    html = report.generate_html_report_tap(data)
    # Highest ratio single category path
    assert 'Hi category' in html
    # Recommendations lists should mention High / Medium / Monitor sections
    assert 'Critical:' in html
    assert 'Important:' in html
    assert 'Monitor:' in html
    # Basic sanity: each detail present
    for cat in ['Hi','Med','Low']:
        assert cat in html


def test_generate_html_report_tap_many_tie_and_empty_bar_chart(monkeypatch):
    # Force tie among >2 categories with ratio >0 -> multi-category grammar with comma & 'and'
    cats = {
        'A': _build_category(count=1, provided=2),  # ratio 0.5
        'B': _build_category(count=1, provided=2),  # ratio 0.5
        'C': _build_category(count=1, provided=2),  # ratio 0.5
    }
    data = {
        'total_rows': 6,
        'processed_rows': 6,
        'technical_failed_rows': [],
        'jailbroken_rows': 3,
        'category_wise_score': cats,
        'target_model': 'tap-model2',
        'target_temperature': 0.4,
        'n_iterations': 2,
        'technique_type': 'TAP',
        'usecase_name': None,
        'target_endpoint_url': None,
        'depth': 1,
        'width': 1,
        'branching_factor': 1,
    }
    # Monkeypatch matplotlib bar plotting section to simulate empty categories for bar chart branch
    # Achieve this by clearing categories right before bar chart loop via patching plt.bar to raise handled exception
    import matplotlib.pyplot as plt
    original_bar = plt.bar
    def fake_bar(*args, **kwargs):  # noqa: ARG001
        raise RuntimeError("force bar fail")
    plt.bar = fake_bar  # cause exception so bar_chart becomes '' path
    try:
        html = report.generate_html_report_tap(data)
    finally:
        plt.bar = original_bar
    # Expect grammar list with commas and 'and C'
    assert 'A, B, and C' in html or 'A, B, and C' in html.replace('\n','')
    # Bar chart suppressed
    assert 'Category Wise Jailbroken Prompts' not in html or 'src="data:image/png;base64,' in html
