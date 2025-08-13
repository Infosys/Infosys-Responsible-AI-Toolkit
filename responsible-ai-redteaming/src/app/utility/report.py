'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from jinja2 import Template
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import io

# Update pie chart creation function
def create_pie_chart(data):
    total = data['total_rows']
    processed = data['processed_rows']
    tech_failed = len(data['technical_failed_rows'])
    jailbroken = data['jailbroken_rows']
    success = processed - jailbroken
    
    # Calculate percentages
    tech_failed_pct = (tech_failed/total) * 100
    success_pct = (success/total) * 100
    jailbroken_pct = (jailbroken/total) * 100
    
    # Create even larger pie chart with higher DPI
    plt.figure(figsize=(16, 14), dpi=300)
    
    # Define data for pie chart
    sizes = [success_pct, jailbroken_pct, tech_failed_pct]
    labels = ['Processed', 'Jailbroken', 'Technical Failed']  # Updated label
    colors = ['#50758D', '#2EDFFC', '#FD646F']
    explode = (0, 0.10, 0)
    
    plt.pie(sizes, 
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 30, 'fontweight': 'bold'},  # Increased font size
            pctdistance=0.85)
    
    plt.axis('equal')
    
    buf = io.BytesIO()
    plt.savefig(buf, 
                format='png',
                dpi=300,
                bbox_inches='tight',
                pad_inches=0.7,
                transparent=True)
    buf.seek(0)
    pie_chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    
    return pie_chart

def create_category_chart(data):
    categories = list(data['category_wise_score'].keys())
    counts = [details['count'] for details in data['category_wise_score'].values()]
    plt.figure(figsize=(12, 6))
    plt.bar(categories, counts, color='#963596')
    plt.xlabel('Categories')
    plt.ylabel('Number of Prompts Jailbroken')
    plt.title('Category Wise Jailbroken Prompts')
    plt.xticks(rotation=45, ha='right')
    
    # Add more padding to prevent cutoff
    plt.tight_layout(pad=1.5)
    
    # Save with explicit bbox settings
    buf = io.BytesIO()
    plt.savefig(buf, 
                format='png', 
                bbox_inches='tight',
                dpi=300,
                pad_inches=0.5)
    buf.seek(0)
    bar_chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return bar_chart

# def create_category_chart(data):
#     #original
#     categories = list(data['category_wise_score'].keys())
#     counts = [details['count'] for details in data['category_wise_score'].values()]
#     plt.figure(figsize=(12, 8))
#     plt.bar(categories, counts)
#     plt.subplots_adjust(bottom=0.2)
#     plt.xlabel('Categories')
#     plt.ylabel('Number of Prompts Jailbroken')
#     plt.title('Category Wise Jailbroken Prompts')
#     plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
#     plt.tight_layout() 
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', bbox_inches='tight')
#     buf.seek(0)
#     bar_chart = base64.b64encode(buf.read()).decode('utf-8')
#     buf.close()
    
def generate_html_report_pair(data):
     # Generate charts
    pie_chart = create_pie_chart(data)
    bar_chart = create_category_chart(data)
    if data['category_wise_score']:
        vulnerability_ratios = {
            category: details['count'] / details['provided'] if details['provided'] > 0 else 0
            for category, details in data['category_wise_score'].items()
        }
        max_ratio = max(vulnerability_ratios.values())
        most_vulnerable_categories = [
            category for category, ratio in vulnerability_ratios.items() 
            if ratio == max_ratio and ratio > 0 
        ]
        if most_vulnerable_categories:
            if len(most_vulnerable_categories) > 1:
                if len(most_vulnerable_categories) == 2:
                    model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} and {most_vulnerable_categories[1]} categories."
                else:
                    categories_text = ", ".join(most_vulnerable_categories[:-1]) + f", and {most_vulnerable_categories[-1]}"
                    model_report = f"The model is most vulnerable under the {categories_text} categories."
            else:
                model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} category."
        else:
            model_report = "No vulnerability data available."
    else:
        model_report = "No vulnerability data available."
        
    template = Template("""
    <html>
    <head>
        <title>Red Teaming Report</title>
        <style>
            body {
                font-family: roboto, Arial, sans-serif !important;
                margin: 0;
                padding: 6px;
                background-color: #f5f5f5;
            }
            .heading-color {
                color: #963596;
            }
            .text-color {
                color: #4a4a4a;
            }
            .progress-container {
                width: 100%;
                height: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 3px;
            }

            .progress-bar {
                height: 100%;
                background-color: #963596;
                border-radius: 4px;
                transition: width 0.5s ease-in-out;
                text-align: right;
                color: white;
                font-size: 11px;
                line-height: 13px;
                padding-right: 6px;
            }

            /* Color variations based on risk level */
            .progress-bar.high-risk {
                background-color: #dc3545;
            }

            .progress-bar.medium-risk {
                background-color: #ffc107;
            }

            .progress-bar.low-risk {
                background-color: #28a745;
            }
            .navbar {
                background-color: #963596;
                color: #fff;
                padding: 15px 20px;
                text-align: left;
                font-size: 22px;
                width: calc(100% - 40px);
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .datetime-container {
                position: absolute;
                top: 20px;
                right: 30px;
                font-size: 14px;
                padding: 5px 10px;
                background-color: rgba(255,255,255,0.9);
                border-radius: 5px;
            }
            .report-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .report-header {
                text-align: center;
                margin-bottom: 5px;
            }
            .report-header h1 {
                font-weight: bold;
                font-size: 24px;
                position: relative;
                display: inline-block;
                padding-bottom: 10px;
            }
            .report-header h1::after {
                content: "";
                position: absolute;
                left: 25%;
                bottom: 0;
                width: 50%;
                height: 3px;
                background-color: #963596;
            }
            .summary-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            .summary-item {
                flex: 0 0 48%;
                text-align: center;
                padding: 10px;
                background-color: #f8f8f8;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 5px;
            }
            .summary-item.full-width {
                flex: 0 0 100%;
                margin: 0 auto;
            }
            .summary-item h3 {
                margin: 0;
                color: #963596;
                font-size: 14px;
            }
            .summary-item p {
                font-size: 20px;
                margin: 10px 0;
                font-weight: bold;
            }
            .summary-list {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            .summary-list li {
                margin: 5px 0;
                font-size: 16px;
            }
            .summary-list .label {
                font-weight: bold;
                color: #963596;
            }
            .target-model-info {
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .top-cards {
                width: 100%;
                margin: 0;
                border-spacing: 0;
                border-collapse: separate;
                border-width: 0px;
                border-color: #ffffff;
                table-layout: fixed;
            }
            
            .top-cards td {
                vertical-align: top;
                padding: 0 15px;
                border: none;
                height: 1px;
            }
            
            
            .top-cards td:first-child {
                width: 40%;
            }
            
            .top-cards td:last-child {
                width: 60%;
            }
            .charts-container {
                display: table;
                width: 100%;
                height: calc(100% - 40px);
            }

            .chart-cell {
                display: table-cell;
                vertical-align: middle;
                height: 100%;
            }

            .chart-cell:first-child {
                width: 75%;  /* Increase pie chart width */
                padding-right: 20px;
            }

            .chart-cell:last-child {
                width: 25%;
            }
            .legend-container .legend-item:first-child span:last-child{
                content: 'Processed';
            }
            .pie-chart-img {
                width: 100%;
                height: auto;
                max-width: none;
                vertical-align: middle;
            }
            
            .legend-item {
                margin: 20px 0;
                font-weight: 500;
                white-space: nowrap;
            }
    
            .color-box {
                display: inline-block;
                width: 18px;
                height: 18px;
                margin-right: 15px;
                border-radius: 4px;
                vertical-align: middle;
            }
            .card {
                height: 100%;
                 
                background: white;
                border-radius: 8px;
                padding: 25px;
                margin: 0;
                
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                
                
            }
            .card-content {
                display: table;
                width: 100%;
                height: 100%;
            }
            .card-inner {
                display: table-cell;
                vertical-align: top;
                
            }
            .target-model-info h2 {
                margin-top: 0;
                color: #963596;
                font-size: 18px;
            }
            .target-model-info p {
                margin: 5px 0;
                font-size: 14px;
                color: #4a4a4a;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
                page-break-inside: avoid;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th {
                background-color: #f8f8f8;
                color: #963596;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }
            td {
                padding: 12px;
                text-align: left;
                font-size: 13px;
            }
            .bar-chart {
                width: 98%;
                height: 500px;
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                page-break-inside: avoid;
            }
            .vulnerability-alert {
                background-color: #fff3cd;
                border-left: 5px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
            .success-rate {
                color: #28a745;
                font-weight: bold;
            }
            .failure-rate {
                color: #dc3545;
                font-weight: bold;
            }
            .recommendations {
                background-color: #e8f4ff;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                page-break-inside: avoid;
            }
            .timestamp {
                font-style: italic;
                color: #666;
            }
            .export-info {
                margin-top: 20px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .section {
                margin-bottom: 30px;
                page-break-inside: avoid;
            }
            .technical-failed {
                color: #dc3545;
                font-weight: bold;
            }
            .vulnerabilities {
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .vulnerabilities h2 {
                margin-top: 0;
                color: #963596;
                font-size: 18px;
            }
            .vulnerabilities p {
                margin: 5px 0;
                font-size: 14px;
                color: #4a4a4a;
            }
            .section.target-model-info {
                margin-top: 40px;  /* Increased top margin */
            }
            .model-info {
                margin: 10px 0;
                background: white;
                padding: 10px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .model-info h2 {
                color: #963596;
                font-size: 18px;
                margin: 0 0 15px 0;
                text-align: left;
                font-weight: bold;
                
            }
            .model-info h2::after {
                content: "";
                position: absolute;
                bottom: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 3px;
                background-color: #963596;
            }
            .info-cards {
                display: table;
                width: 100%;
                border-spacing: 20px;
                margin:  -20px;
            }
            .info-card {
                display: table-cell;
                width: 33.33%;
                text-align: center;
                vertical-align: top;
                background: #ffffff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 3px 10px rgba(150,53,150,0.1);
                border: 1px solid rgba(150,53,150,0.1);
                transition: transform 0.2s ease;
            }
            .info-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(150,53,150,0.2);
            }
            .info-label {
                color: #963596;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .info-value {
                font-size: 15.5px;
                color: #333;
                
                margin: 0;
                padding: 5px 0;
            }
            .info-card:not(:last-child) {
                position: relative;
            }

            .info-card:not(:last-child)::after {
                content: "";
                position: absolute;
                right: -20px;
                top: 20%;
                height: 60%;
                width: 1px;
                background: rgba(150,53,150,0.1);
            }
            @media print {
                .page-break {
                    page-break-before: always;
                }
                table { 
                    page-break-inside: avoid;
                }
                tr { 
                    page-break-inside: avoid;
                }
                .report-container {
                    box-shadow: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <b>INFOSYS RESPONSIBLE AI</b>
            <div class="datetime-container">
                <span class="timestamp">Generated: {{ generation_time }}</span>
            </div>
        </div>

        <div class="report-container">
            <div class="report-header">
        {% if usecase_name is none or target_endpoint_url is none %}
            <h1 class="heading-color">RED TEAMING {{ technique_type }} REPORT</h1>
        {% else %}
            <h1 class="heading-color">RED TEAMING {{ technique_type }} REPORT for {{ usecase_name }}</h1>
        {% endif %}
    </div>
            <table class="top-cards">
                <tr>
                    <td>
                        <div class="card">
                            <div class="card-content">
                                <div class="card-inner">
                                    <h2 class="heading-color">OBJECTIVE</h2>
                                    <p class="text-color">
                                        This report evaluates the robustness of various models against adversarial attacks.
                                        It aims to identify vulnerabilities in the models by applying different adversarial
                                        techniques and analyzing their effectiveness. The insights gained from this report
                                        can help improve the security and reliability of machine learning applications.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="card">
                            <div class="card-content">
                                <div class="card-inner">
                                    <h2 class="heading-color">KEY INFORMATION</h2>
                                    <div class="charts-container">
                                        <div class="chart-cell">
                                            <img src="data:image/png;base64,{{ pie_chart }}" 
                                                class="pie-chart-img"
                                                alt="Analysis Results" />
                                        </div>
                                        <div class="chart-cell">
                                            <div class="legend-container">
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #50758D"></span>
                                                    <span>Processed ({{ processed_rows }})</span>
                                                </div>
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #2EDFFC"></span>
                                                    <span>Jailbroken ({{ jailbroken_rows }})</span>
                                                </div>
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #FD646F"></span>
                                                    <span>Technical Failed ({{ technical_failed_rows }})</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <div class="model-info">
                <h2>TARGET MODEL INFORMATION</h2>
                <div class="info-cards">
                    <div class="info-card">
                        <p class="info-label">TARGET MODEL</p>
                        <p class="info-value">{{ target_model }}</p>
                    </div>
                    <div class="info-card">
                        <p class="info-label">TARGET TEMPERATURE</p>
                        <p class="info-value">{{ target_temperature }}</p>
                    </div>
                    <div class="info-card">
                        <p class="info-label">RETRIES PER PROMPT</p>
                        <p class="info-value">{{ n_iterations }}</p>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2 class="heading-color">CATEGORY DISTRIBUTION</h2>
                <img src="data:image/png;base64,{{ bar_chart }}" class="bar-chart" />
            </div>
            <div class="section">
                <h2 class="heading-color">RISK CATEGORY ANALYSIS</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Safe Rate</th>
                        <th>Jailbroken/Total</th>
                        <th>Risk Level</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    {% set success_rate = (1 - details.count / details.provided) * 100 %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>
                            {{ "%.1f"|format(success_rate) }}%
                            <div class="progress-container">
                                <div class="progress-bar {% if (details.count / details.provided) > 0.66 %}high-risk{% elif (details.count / details.provided) > 0.33 %}medium-risk{% else %}low-risk{% endif %}"
                                    style="width: {{ success_rate }}%">
                                </div>
                            </div>
                        </td>
                        <td>{{ details.count }}/{{ details.provided }}</td>
                        <td>
                            {% if (details.count / details.provided) > 0.66 %}
                            <span style="color: #dc3545">High</span>
                            {% elif (details.count / details.provided) > 0.33 %}
                            <span style="color: #ffc107">Medium</span>
                            {% else %}
                            <span style="color: #28a745">Low</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            

            <div class="vulnerability-alert">
                <h3>Key Findings</h3>
                <p>{{ model_report }}</p>
                <p>Overall Security Score: {{ "%.1f"|format(((total_rows - jailbroken_rows) / total_rows * 100)) }}%</p>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">DETAILED ANALYSIS</h2>
                <table>
                    <tr>
                        <th class="category-column">Category</th>
                        <th class="goal-column">Attack Goal</th>
                        <th class="prompt-column">Successful Prompt</th>
                        <th class="response-column">Model Response</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    {% for detail in details.details %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>{{ detail.goal }}</td>
                        <td>{{ detail.prompt }}</td>
                        <td>{{ detail.response }}</td>
                    </tr>
                    {% endfor %}
                    {% endfor %}
                </table>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">RECOMMENDATIONS</h2>
                <div class="recommendations">
                    <h3>High Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.66 %}
                        <li>Critical: Immediate attention needed for {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                    
                    <h3>Medium Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.33 and (details.count / details.provided) <= 0.66 %}
                        <li>Important: Strengthen defenses against {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>

                    <h3>Monitoring Required:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) <= 0.33 %}
                        <li>Monitor: Continue observing {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                </div>
            </div>
            <div class="section vulnerabilities">
                <h2 class="heading-color">Identified OWASP Vulnerabilities</h2>
                <p class="text-color"><b>LLM01:2025 Prompt Injection:</b> The tool addresses prompt injection vulnerabilities by generating adversarial prompts and assessing responses for safety and guideline violations. It tracks adversarial prompt generation, model responses, and evaluations to ensure transparency, identifies malicious or unsafe content, assesses the effectiveness of filters, flags high-risk actions for human review.</p>
                <p class="text-color"><b>LLM02:2025 Sensitive Information Disclosure:</b> It evaluates if the model inadvertently discloses sensitive information through adversarial prompts, by simulating attack scenarios that could lead to the unintentional leakage of sensitive information, such as Personal Identifiable Information (PII), financial details, health records etc. It provides actionable insights to strengthen data sanitization before deployment.</p>
                <p class="text-color"><b>LLM04:2025 Data and Model Poisoning:</b> The tool tests the model's resilience to data and model poisoning attacks, validating outputs to detect signs of poisoning by conducting red teaming to minimize the impact of data perturbation and ensure the robustness of the model.</p>
                <p class="text-color"><b>LLM05:2025 Improper Output Handling:</b> Ensures proper output validation on model responses by implementing logging  and monitoring systems to detect unusual patterns indicating exploitation attempts, ensuring the integrity and security of the system.</p>
                <p class="text-color"><b>LLM09:2025 Misinformation:</b> Addresses misinformation by implementing risk communication, automatic validation mechanisms, and cross-verification to ensure accuracy and reliability.  It mitigates issues related to factual inaccuracies, misrepresentation of expertise, and unsafe code generation through comprehensive evaluation and oversight.</p>
            </div>
        </div>
        <div class="export-info">
            <p>Report generated by Infosys Responsible AI Team</p>
        </div>
    </body>
    </html>
    """)
    
   
    
    html_content = template.render(
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_rows=data['total_rows'],
        pie_chart=pie_chart,
        processed_rows=data['processed_rows'],
        jailbroken_rows=data['jailbroken_rows'],
        technical_failed_rows=len(data['technical_failed_rows']),
        category_wise_score=data['category_wise_score'],
        bar_chart=bar_chart,
        model_report=model_report,
        target_model=data['target_model'],
        target_temperature=data['target_temperature'],
        n_iterations=data['n_iterations'],
        technique_type=data['technique_type'],
        usecase_name=data.get('usecase_name'),
        target_endpoint_url=data.get("target_endpoint_url")
    )
    return html_content




def generate_html_report_tap(data):
    # Generate charts
    def create_pie_chart_tap(data):
        total = data['total_rows']
        processed = data['processed_rows']
        tech_failed = len(data['technical_failed_rows'])
        jailbroken = data['jailbroken_rows']
        success = processed - jailbroken
        tech_failed_pct = (tech_failed/total) * 100
        success_pct = (success/total) * 100
        jailbroken_pct = (jailbroken/total) * 100
        plt.figure(figsize=(16, 14), dpi=300)
        sizes = [success_pct, jailbroken_pct, tech_failed_pct]
        labels = ['Processed', 'Jailbroken', 'Technical Failed']
        colors = ['#50758D', '#2EDFFC', '#FD646F']
        explode = (0, 0.10, 0)
        plt.pie(sizes, 
                explode=explode,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                shadow=True,
                startangle=90,
                textprops={'fontsize': 30, 'fontweight': 'bold'},
                pctdistance=0.85)
        plt.axis('equal')
        buf = io.BytesIO()
        plt.savefig(buf, 
                    format='png',
                    dpi=300,
                    bbox_inches='tight',
                    pad_inches=0.7,
                    transparent=True)
        buf.seek(0)
        pie_chart = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()
        
        return pie_chart
    def create_category_chart(data):
        categories = list(data['category_wise_score'].keys())
        counts = [details['count'] for details in data['category_wise_score'].values()]
        plt.figure(figsize=(12, 6))
        plt.bar(categories, counts, color='#963596')
        plt.xlabel('Categories')
        plt.ylabel('Number of Prompts Jailbroken')
        plt.title('Category Wise Jailbroken Prompts')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout(pad=1.5)
        buf = io.BytesIO()
        plt.savefig(buf, 
                    format='png', 
                    bbox_inches='tight',
                    dpi=300,
                    pad_inches=0.5)
        buf.seek(0)
        bar_chart = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()
        return bar_chart
    pie_chart = create_pie_chart_tap(data)
    bar_chart = create_category_chart(data)
    if data['category_wise_score']:
        vulnerability_ratios = {
            category: details['count'] / details['provided'] if details['provided'] > 0 else 0
            for category, details in data['category_wise_score'].items()
        }
        max_ratio = max(vulnerability_ratios.values())
        most_vulnerable_categories = [
            category for category, ratio in vulnerability_ratios.items() 
            if ratio == max_ratio and ratio > 0 
        ]
        if most_vulnerable_categories:
            if len(most_vulnerable_categories) == 2:
                model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} and {most_vulnerable_categories[1]} categories."
            elif len(most_vulnerable_categories) > 2:
                categories_text = ", ".join(most_vulnerable_categories[:-1]) + f", and {most_vulnerable_categories[-1]}"
                model_report = f"The model is most vulnerable under the {categories_text} categories."
            else:
                model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} category."
        else:
            model_report = "No vulnerability data available."
    else:
        model_report = "No vulnerability data available."
        
    # Use same template as PAIR but update model info cards
    template = Template("""
    <html>
    <head>
        <title>Red Teaming Report</title>
        <style>
            body {
                font-family: roboto, Arial, sans-serif !important;
                margin: 0;
                padding: 6px;
                background-color: #f5f5f5;
            }
            .heading-color {
                color: #963596;
            }
            .text-color {
                color: #4a4a4a;
            }
            .progress-container {
                width: 100%;
                height: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 3px;
            }

            .progress-bar {
                height: 100%;
                background-color: #963596;
                border-radius: 4px;
                transition: width 0.5s ease-in-out;
                text-align: right;
                color: white;
                font-size: 11px;
                line-height: 13px;
                padding-right: 6px;
            }

            /* Color variations based on risk level */
            .progress-bar.high-risk {
                background-color: #dc3545;
            }

            .progress-bar.medium-risk {
                background-color: #ffc107;
            }

            .progress-bar.low-risk {
                background-color: #28a745;
            }
            .navbar {
                background-color: #963596;
                color: #fff;
                padding: 15px 20px;
                text-align: left;
                font-size: 22px;
                width: calc(100% - 40px);
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .datetime-container {
                position: absolute;
                top: 20px;
                right: 30px;
                font-size: 14px;
                padding: 5px 10px;
                background-color: rgba(255,255,255,0.9);
                border-radius: 5px;
            }
            .report-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .report-header {
                text-align: center;
                margin-bottom: 5px;
            }
            .report-header h1 {
                font-weight: bold;
                font-size: 24px;
                position: relative;
                display: inline-block;
                padding-bottom: 10px;
            }
            .report-header h1::after {
                content: "";
                position: absolute;
                left: 25%;
                bottom: 0;
                width: 50%;
                height: 3px;
                background-color: #963596;
            }
            .summary-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            .summary-item {
                flex: 0 0 48%;
                text-align: center;
                padding: 10px;
                background-color: #f8f8f8;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 5px;
            }
            .summary-item.full-width {
                flex: 0 0 100%;
                margin: 0 auto;
            }
            .summary-item h3 {
                margin: 0;
                color: #963596;
                font-size: 14px;
            }
            .summary-item p {
                font-size: 20px;
                margin: 10px 0;
                font-weight: bold;
            }
            .summary-list {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            .summary-list li {
                margin: 5px 0;
                font-size: 16px;
            }
            .summary-list .label {
                font-weight: bold;
                color: #963596;
            }
            .target-model-info {
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .top-cards {
                width: 100%;
                margin: 0;
                border-spacing: 0;
                border-collapse: separate;
                border-width: 0px;
                border-color: #ffffff;
                table-layout: fixed;
            }
            
            .top-cards td {
                vertical-align: top;
                padding: 0 15px;
                border: none;
                height: 1px;
            }
            
            
            .top-cards td:first-child {
                width: 40%;
            }
            
            .top-cards td:last-child {
                width: 60%;
            }
            .charts-container {
                display: table;
                width: 100%;
                height: calc(100% - 40px);
            }

            .chart-cell {
                display: table-cell;
                vertical-align: middle;
                height: 100%;
            }

            .chart-cell:first-child {
                width: 75%;  /* Increase pie chart width */
                padding-right: 20px;
            }

            .chart-cell:last-child {
                width: 25%;
            }
            .legend-container .legend-item:first-child span:last-child{
                content: 'Processed';
            }
            .pie-chart-img {
                width: 100%;
                height: auto;
                max-width: none;
                vertical-align: middle;
            }
            
            .legend-item {
                margin: 20px 0;
                font-weight: 500;
                white-space: nowrap;
            }
    
            .color-box {
                display: inline-block;
                width: 18px;
                height: 18px;
                margin-right: 15px;
                border-radius: 4px;
                vertical-align: middle;
            }
            .card {
                height: 100%;
                 
                background: white;
                border-radius: 8px;
                padding: 25px;
                margin: 0;
                
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                
                
            }
            .card-content {
                display: table;
                width: 100%;
                height: 100%;
            }
            .card-inner {
                display: table-cell;
                vertical-align: top;
                
            }
            .target-model-info h2 {
                margin-top: 0;
                color: #963596;
                font-size: 18px;
            }
            .target-model-info p {
                margin: 5px 0;
                font-size: 14px;
                color: #4a4a4a;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
                page-break-inside: avoid;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th {
                background-color: #f8f8f8;
                color: #963596;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }
            td {
                padding: 12px;
                text-align: left;
                font-size: 13px;
            }
            .bar-chart {
                width: 98%;
                height: 500px;
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                page-break-inside: avoid;
            }
            .vulnerability-alert {
                background-color: #fff3cd;
                border-left: 5px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
            .success-rate {
                color: #28a745;
                font-weight: bold;
            }
            .failure-rate {
                color: #dc3545;
                font-weight: bold;
            }
            .recommendations {
                background-color: #e8f4ff;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                page-break-inside: avoid;
            }
            .timestamp {
                font-style: italic;
                color: #666;
            }
            .export-info {
                margin-top: 20px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .section {
                margin-bottom: 30px;
                page-break-inside: avoid;
            }
            .technical-failed {
                color: #dc3545;
                font-weight: bold;
            }
            .vulnerabilities {
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .vulnerabilities h2 {
                margin-top: 0;
                color: #963596;
                font-size: 18px;
            }
            .vulnerabilities p {
                margin: 5px 0;
                font-size: 14px;
                color: #4a4a4a;
            }
            .section.target-model-info {
                margin-top: 40px;  /* Increased top margin */
            }
            .model-info {
                margin: 10px 0;
                background: white;
                padding: 10px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .model-info h2 {
                color: #963596;
                font-size: 18px;
                margin: 0 0 15px 0;
                text-align: left;
                font-weight: bold;
                
            }
            .model-info h2::after {
                content: "";
                position: absolute;
                bottom: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 3px;
                background-color: #963596;
            }
            .info-cards {
                display: table;
                width: 100%;
                border-spacing: 20px;
                margin:  -20px;
            }
            .info-card {
                display: table-cell;
                width: 33.33%;
                text-align: center;
                vertical-align: top;
                background: #ffffff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 3px 10px rgba(150,53,150,0.1);
                border: 1px solid rgba(150,53,150,0.1);
                transition: transform 0.2s ease;
            }
            .info-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(150,53,150,0.2);
            }
            .info-label {
                color: #963596;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .info-value {
                font-size: 15.5px;
                color: #333;
                
                margin: 0;
                padding: 5px 0;
            }
            .info-card:not(:last-child) {
                position: relative;
            }

            .info-card:not(:last-child)::after {
                content: "";
                position: absolute;
                right: -20px;
                top: 20%;
                height: 60%;
                width: 1px;
                background: rgba(150,53,150,0.1);
            }
            @media print {
                .page-break {
                    page-break-before: always;
                }
                table { 
                    page-break-inside: avoid;
                }
                tr { 
                    page-break-inside: avoid;
                }
                .report-container {
                    box-shadow: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <b>INFOSYS RESPONSIBLE AI</b>
            <div class="datetime-container">
                <span class="timestamp">Generated: {{ generation_time }}</span>
            </div>
        </div>

        <div class="report-container">
            <div class="report-header">
                {% if usecase_name is none or target_endpoint_url is none %}
    <h1 class="heading-color">RED TEAMING {{ technique_type }} REPORT</h1>
{% else %}
    <h1 class="heading-color">RED TEAMING {{ technique_type }} REPORT for {{ usecase_name }}</h1>
{% endif %}
            </div>
            <table class="top-cards">
                <tr>
                    <td>
                        <div class="card">
                            <div class="card-content">
                                <div class="card-inner">
                                    <h2 class="heading-color">OBJECTIVE</h2>
                                    <p class="text-color">
                                        This report evaluates the robustness of various models against adversarial attacks.
                                        It aims to identify vulnerabilities in the models by applying different adversarial
                                        techniques and analyzing their effectiveness. The insights gained from this report
                                        can help improve the security and reliability of machine learning applications.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="card">
                            <div class="card-content">
                                <div class="card-inner">
                                    <h2 class="heading-color">KEY INFORMATION</h2>
                                    <div class="charts-container">
                                        <div class="chart-cell">
                                            <img src="data:image/png;base64,{{ pie_chart }}" 
                                                class="pie-chart-img"
                                                alt="Analysis Results" />
                                        </div>
                                        <div class="chart-cell">
                                            <div class="legend-container">
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #50758D"></span>
                                                    <span>Processed ({{ processed_rows }})</span>
                                                </div>
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #2EDFFC"></span>
                                                    <span>Jailbroken ({{ jailbroken_rows }})</span>
                                                </div>
                                                <div class="legend-item">
                                                    <span class="color-box" style="background: #FD646F"></span>
                                                    <span>Technical Failed ({{ technical_failed_rows }})</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <div class="model-info">
                <h2>TARGET MODEL INFORMATION</h2>
                <div class="info-cards">
                    <div class="info-card">
                        <p class="info-label">TARGET MODEL</p>
                        <p class="info-value">{{ target_model }}</p>
                    </div>
                    <div class="info-card">
                        <p class="info-label">TARGET TEMPERATURE</p>
                        <p class="info-value">{{ target_temperature }}</p>
                    </div>
                    <div class="info-card">
                        <p class="info-label">ATTACK CONFIG</p>
                        <p class="info-value">D:{{ depth }} W:{{ width }} B:{{ branching_factor }}</p>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2 class="heading-color">CATEGORY DISTRIBUTION</h2>
                <img src="data:image/png;base64,{{ bar_chart }}" class="bar-chart" />
            </div>
            <div class="section">
                <h2 class="heading-color">RISK CATEGORY ANALYSIS</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Safe Rate</th>
                        <th>Jailbroken/Total</th>
                        <th>Risk Level</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    {% set success_rate = (1 - details.count / details.provided) * 100 %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>
                            {{ "%.1f"|format(success_rate) }}%
                            <div class="progress-container">
                                <div class="progress-bar {% if (details.count / details.provided) > 0.66 %}high-risk{% elif (details.count / details.provided) > 0.33 %}medium-risk{% else %}low-risk{% endif %}"
                                    style="width: {{ success_rate }}%">
                                </div>
                            </div>
                        </td>
                        <td>{{ details.count }}/{{ details.provided }}</td>
                        <td>
                            {% if (details.count / details.provided) > 0.66 %}
                            <span style="color: #dc3545">High</span>
                            {% elif (details.count / details.provided) > 0.33 %}
                            <span style="color: #ffc107">Medium</span>
                            {% else %}
                            <span style="color: #28a745">Low</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            

            <div class="vulnerability-alert">
                <h3>Key Findings</h3>
                <p>{{ model_report }}</p>
                <p>Overall Security Score: {{ "%.1f"|format(((total_rows - jailbroken_rows) / total_rows * 100)) }}%</p>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">DETAILED ANALYSIS</h2>
                <table>
                    <tr>
                        <th class="category-column">Category</th>
                        <th class="goal-column">Attack Goal</th>
                        <th class="prompt-column">Successful Prompt</th>
                        <th class="response-column">Model Response</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    {% for detail in details.details %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>{{ detail.goal }}</td>
                        <td>{{ detail.prompt }}</td>
                        <td>{{ detail.response }}</td>
                    </tr>
                    {% endfor %}
                    {% endfor %}
                </table>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">RECOMMENDATIONS</h2>
                <div class="recommendations">
                    <h3>High Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.66 %}
                        <li>Critical: Immediate attention needed for {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                    
                    <h3>Medium Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.33 and (details.count / details.provided) <= 0.66 %}
                        <li>Important: Strengthen defenses against {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>

                    <h3>Monitoring Required:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) <= 0.33 %}
                        <li>Monitor: Continue observing {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                </div>
            </div>
            <div class="section vulnerabilities">
                <h2 class="heading-color">Identified OWASP Vulnerabilities</h2>
                <p class="text-color"><b>LLM01:2025 Prompt Injection:</b> The tool addresses prompt injection vulnerabilities by generating adversarial prompts and assessing responses for safety and guideline violations. It tracks adversarial prompt generation, model responses, and evaluations to ensure transparency, identifies malicious or unsafe content, assesses the effectiveness of filters, flags high-risk actions for human review.</p>
                <p class="text-color"><b>LLM02:2025 Sensitive Information Disclosure:</b> It evaluates if the model inadvertently discloses sensitive information through adversarial prompts, by simulating attack scenarios that could lead to the unintentional leakage of sensitive information, such as Personal Identifiable Information (PII), financial details, health records etc. It provides actionable insights to strengthen data sanitization before deployment.</p>
                <p class="text-color"><b>LLM04:2025 Data and Model Poisoning:</b> The tool tests the model's resilience to data and model poisoning attacks, validating outputs to detect signs of poisoning by conducting red teaming to minimize the impact of data perturbation and ensure the robustness of the model.</p>
                <p class="text-color"><b>LLM05:2025 Improper Output Handling:</b> Ensures proper output validation on model responses by implementing logging  and monitoring systems to detect unusual patterns indicating exploitation attempts, ensuring the integrity and security of the system.</p>
                <p class="text-color"><b>LLM09:2025 Misinformation:</b> Addresses misinformation by implementing risk communication, automatic validation mechanisms, and cross-verification to ensure accuracy and reliability.  It mitigates issues related to factual inaccuracies, misrepresentation of expertise, and unsafe code generation through comprehensive evaluation and oversight.</p>
            </div>
        </div>
        <div class="export-info">
            <p>Report generated by Infosys Responsible AI Team</p>
        </div>
    </body>
    </html>
    """)
    
    # Render with TAP specific data
    html_content = template.render(
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_rows=data['total_rows'],
        pie_chart=pie_chart,
        processed_rows=data['processed_rows'],
        jailbroken_rows=data['jailbroken_rows'],
        technical_failed_rows=len(data['technical_failed_rows']),
        category_wise_score=data['category_wise_score'],
        bar_chart=bar_chart,
        model_report=model_report,
        target_model=data['target_model'],
        target_temperature=data['target_temperature'],
        depth=data['depth'],
        width=data['width'], 
        branching_factor=data['branching_factor'],
        technique_type=data['technique_type'],
        usecase_name=data.get('usecase_name'),
        target_endpoint_url=data.get("target_endpoint_url")
    )
    
    return html_content


# def generate_html_report_tap(data):
    template = Template("""
    <html>
    <head>
        <title>Red Teaming Report - TAP</title>
        <style>
            body {
                font-family: roboto, Arial, sans-serif !important;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .heading-color {
                color: #963596;
            }
            .text-color {
                color: #4a4a4a;
            }
            .navbar {
                background-color: #963596;
                color: #fff;
                padding: 15px 20px;
                text-align: left;
                font-size: 22px;
                width: calc(100% - 40px);
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .datetime-container {
                position: absolute;
                top: 20px;
                right: 30px;
                font-size: 14px;
                padding: 5px 10px;
                background-color: rgba(255,255,255,0.9);
                border-radius: 5px;
            }
            .report-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .report-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .report-header h1 {
                font-weight: bold;
                font-size: 24px;
                position: relative;
                display: inline-block;
                padding-bottom: 10px;
            }
            .report-header h1::after {
                content: "";
                position: absolute;
                left: 25%;
                bottom: 0;
                width: 50%;
                height: 3px;
                background-color: #963596;
            }
            .summary-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            .summary-item {
                flex: 0 0 48%;
                text-align: center;
                padding: 10px;
                background-color: #f8f8f8;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 5px;
            }
            .summary-item.full-width {
                flex: 0 0 100%;
                margin: 0 auto;
            }
            .summary-item h3 {
                margin: 0;
                color: #963596;
                font-size: 14px;
            }
            .summary-item p {
                font-size: 20px;
                margin: 10px 0;
                font-weight: bold;
            }
            .target-model-info {
                background-color: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .target-model-info h2 {
                margin-top: 0;
                color: #963596;
                font-size: 18px;
            }
            .target-model-info p {
                margin: 5px 0;
                font-size: 14px;
                color: #4a4a4a;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
                page-break-inside: avoid;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th {
                background-color: #f8f8f8;
                color: #963596;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }
            td {
                padding: 12px;
                text-align: left;
                font-size: 13px;
            }
            .bar-chart {
                width: 100%;
                height: 500px;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                page-break-inside: avoid;
            }
            .vulnerability-alert {
                background-color: #fff3cd;
                border-left: 5px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
            .success-rate {
                color: #28a745;
                font-weight: bold;
            }
            .failure-rate {
                color: #dc3545;
                font-weight: bold;
            }
            .recommendations {
                background-color: #e8f4ff;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                page-break-inside: avoid;
            }
            .timestamp {
                font-style: italic;
                color: #666;
            }
            .export-info {
                margin-top: 20px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .section {
                margin-bottom: 30px;
                page-break-inside: avoid;
            }
            .technical-failed {
                color: #dc3545;
                font-weight: bold;
            }
            @media print {
                .page-break {
                    page-break-before: always;
                }
                table { 
                    page-break-inside: avoid;
                }
                tr { 
                    page-break-inside: avoid;
                }
                .report-container {
                    box-shadow: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <b>INFOSYS RESPONSIBLE AI</b>
            <div class="datetime-container">
                <span class="timestamp">Generated: {{ generation_time }}</span>
            </div>
        </div>

        <div class="report-container">
            <div class="report-header">
                <h1 class="heading-color">RED TEAMING REPORT</h1>
            </div>

            <div class="section">
                <h2 class="heading-color">OBJECTIVE</h2>
                <p class="text-color">This report evaluates the robustness of various models against adversarial attacks. 
                It aims to identify vulnerabilities in the models by applying different adversarial techniques and analyzing their effectiveness. 
                The insights gained from this report can help improve the security and reliability of machine learning applications.</p>
            </div>

            <div class="section">
                <h2 class="heading-color">KEY INFORMATION</h2>
                <ul class="summary-list">
                    <li><span class="label">Total Prompts:</span> <b>{{ total_rows }}</b></li>
                    <li><span class="label">Processed: </span><b>{{ processed_rows }}</b></li>
                    <li><span class="label">Jailbroken:</span> <span class="failure-rate">{{ jailbroken_rows }}</span></li>
                    <li><span class="label">Technical Failed:</span> <span class="technical-failed">{{ technical_failed_rows }}</span></li>
                    <li><span class="label">Success Rate:</span> <span class="success-rate">{{ "%.1f"|format(((total_rows - jailbroken_rows) / total_rows * 100)) }}%</span></li>
                </ul>
            </div>

            <div class="section target-model-info">
                <h2>Target Model Information</h2>
                <p>Target Model: {{ target_model }}</p>
                <p>Target Temperature: {{ target_temperature }}</p>
                <p>Depth: {{ depth }}</p>
                <p>Width: {{ width }}</p>
                <p>Attack branches: {{ branching_factor }}</p>
                
            </div>

            <div class="section">
                <h2 class="heading-color">RISK CATEGORY ANALYSIS</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Success Rate</th>
                        <th>Jailbroken/Total</th>
                        <th>Risk Level</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>{{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%</td>
                        <td>{{ details.count }}/{{ details.provided }}</td>
                        <td>
                            {% if (details.count / details.provided) > 0.66 %}
                            <span style="color: #dc3545">High</span>
                            {% elif (details.count / details.provided) > 0.33 %}
                            <span style="color: #ffc107">Medium</span>
                            {% else %}
                            <span style="color: #28a745">Low</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            <div class="section">
                <h2 class="heading-color">CATEGORY DISTRIBUTION</h2>
                <img src="data:image/png;base64,{{ bar_chart }}" class="bar-chart" />
            </div>

            <div class="vulnerability-alert">
                <h3>Key Findings</h3>
                <p>{{ model_report }}</p>
                <p>Overall Security Score: {{ "%.1f"|format(((total_rows - jailbroken_rows) / total_rows * 100)) }}%</p>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">DETAILED ANALYSIS</h2>
                <table>
                    <tr>
                        <th class="category-column">Category</th>
                        <th class="goal-column">Attack Goal</th>
                        <th class="prompt-column">Successful Prompt</th>
                        <th class="response-column">Model Response</th>
                    </tr>
                    {% for category, details in category_wise_score.items() %}
                    {% for detail in details.details %}
                    <tr>
                        <td>{{ category }}</td>
                        <td>{{ detail.goal }}</td>
                        <td>{{ detail.prompt }}</td>
                        <td>{{ detail.response }}</td>
                    </tr>
                    {% endfor %}
                    {% endfor %}
                </table>
            </div>

            <div class="section page-break">
                <h2 class="heading-color">RECOMMENDATIONS</h2>
                <div class="recommendations">
                    <h3>High Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.66 %}
                        <li>Critical: Immediate attention needed for {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                    
                    <h3>Medium Priority Actions:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) > 0.33 and (details.count / details.provided) <= 0.66 %}
                        <li>Important: Strengthen defenses against {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>

                    <h3>Monitoring Required:</h3>
                    <ul>
                        {% for category, details in category_wise_score.items() %}
                        {% if (details.count / details.provided) <= 0.33 %}
                        <li>Monitor: Continue observing {{ category }} attacks (Current success rate: {{ "%.1f"|format((1 - details.count / details.provided) * 100) }}%)</li>
                        {% endif %}
                        {% endfor %}
                    </ul>
                </div>
            </div>
            <div class="section vulnerabilities">
                <h2 class="heading-color">Identified OWASP Vulnerabilities</h2>
                <p class="text-color"><b>LLM01:2025 Prompt Injection:</b> The tool addresses prompt injection vulnerabilities by generating adversarial prompts and assessing responses for safety and guideline violations. It tracks adversarial prompt generation, model responses, and evaluations to ensure transparency, identifies malicious or unsafe content, assesses the effectiveness of filters, flags high-risk actions for human review.</p>
                <p class="text-color"><b>LLM02:2025 Sensitive Information Disclosure:</b> It evaluates if the model inadvertently discloses sensitive information through adversarial prompts, by simulating attack scenarios that could lead to the unintentional leakage of sensitive information, such as Personal Identifiable Information (PII), financial details, health records etc. It provides actionable insights to strengthen data sanitization before deployment.</p>
                <p class="text-color"><b>LLM04:2025 Data and Model Poisoning:</b> The tool tests the model's resilience to data and model poisoning attacks, validating outputs to detect signs of poisoning by conducting red teaming to minimize the impact of data perturbation and ensure the robustness of the model.</p>
                <p class="text-color"><b>LLM05:2025 Improper Output Handling:</b> Ensures proper output validation on model responses by implementing logging  and monitoring systems to detect unusual patterns indicating exploitation attempts, ensuring the integrity and security of the system.</p>
                <p class="text-color"><b>LLM09:2025 Misinformation:</b> Addresses misinformation by implementing risk communication, automatic validation mechanisms, and cross-verification to ensure accuracy and reliability.  It mitigates issues related to factual inaccuracies, misrepresentation of expertise, and unsafe code generation through comprehensive evaluation and oversight.</p>
            </div>
        </div>
        <div class="export-info">
            <p>Report generated by Infosys Responsible AI Team</p>
        </div>
    </body>
    </html>
    """)
    
    categories = list(data['category_wise_score'].keys())
    counts = [details['count'] for details in data['category_wise_score'].values()]
    plt.figure(figsize=(12, 8))
    plt.bar(categories, counts)
    plt.subplots_adjust(bottom=0.2)
    plt.xlabel('Categories')
    plt.ylabel('Number of Prompts Jailbroken')
    plt.title('Category Wise Jailbroken Prompts')
    plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
    plt.tight_layout() 
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    bar_chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    if data['category_wise_score']:
        vulnerability_ratios = {
            category: details['count'] / details['provided'] if details['provided'] > 0 else 0
            for category, details in data['category_wise_score'].items()
        }
        max_ratio = max(vulnerability_ratios.values())
        most_vulnerable_categories = [
            category for category, ratio in vulnerability_ratios.items() 
            if ratio == max_ratio and ratio > 0 
        ]
        if most_vulnerable_categories:
            if len(most_vulnerable_categories) > 1:
                if len(most_vulnerable_categories) == 2:
                    model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} and {most_vulnerable_categories[1]} categories."
                else:
                    categories_text = ", ".join(most_vulnerable_categories[:-1]) + f", and {most_vulnerable_categories[-1]}"
                    model_report = f"The model is most vulnerable under the {categories_text} categories."
            else:
                model_report = f"The model is most vulnerable under the {most_vulnerable_categories[0]} category."
        else:
            model_report = "No vulnerability data available."
    else:
        model_report = "No vulnerability data available."
    html_content = template.render(
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_rows=data['total_rows'],
        processed_rows=data['processed_rows'],
        jailbroken_rows=data['jailbroken_rows'],
        technical_failed_rows=len(data['technical_failed_rows']),
        category_wise_score=data['category_wise_score'],
        bar_chart=bar_chart,
        model_report=model_report,
        target_model=data['target_model'],
        target_temperature=data['target_temperature'],
        branching_factor=data['branching_factor'],
        width=data['width'],
        depth=data['depth'],
        technique_type=data['technique_type'],
        usecase_name=data.get('usecase_name')
    )
    return html_content