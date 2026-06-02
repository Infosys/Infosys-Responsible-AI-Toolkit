/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import Chart from 'chart.js/auto';
import ChartAnnotation from 'chartjs-plugin-annotation';
Chart.register(ChartAnnotation);
import { HttpClient } from '@angular/common/http';
import { Subject, takeUntil } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';

@Component({
  selector: 'app-explainability-result',
  templateUrl: './explainability-result.component.html',
  styleUrls: ['./explainability-result.component.css']
})
export class ExplainabilityResultComponent implements OnInit, AfterViewInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // ===== INPUT PROPERTIES =====
  @Input() explainabilityRes: any;
  @Input() explainabilityOption!: string;
  @Input() prompt!: string;
  @Input() ExplanabilityFileId!: any;
  @Input() selectedOptions: any;
  @Input() selectedTranslate: any;
  @Input() covFinalAnswer: any;
  @Input() finalAnswer: any;
  @Input() COVAnswer: any;
  @Input() COVTimeTaken: any;
  @Input() isLoadingCOV: any;
  @Input() enableSearch: any;
  @Input() selectedExplainabilityModel: any;

  // ===== COMPONENT DATA PROPERTIES =====
  topSentiments: any[] = [];
  topTokens: any[] = [];
  tokens: any[] = [];
  apiResult: any = null;
  finalAnswer1: string = '';
  openAIAnswer: string = '';
  THOTAnswer: string = '';
  UncertaintyGotMetric: any;
  UncertaintyAIMetric: any;
  GOTAnswer: string = '';
  tokenImportanceResponse: any = {};
  InternetSearchMetric: any;
  InternetResponse: any;
  COVRAGResponse: string = '';
  THOTRAGResponse: string = '';
  THOTRAGSource: any;
  RetrivalKelperResponse: any = {};
  ThotRagResult:any ='';
  ThotRagExplanation:any ='';

  // Safe sanitized versions for template binding
  safeOpenAIAnswer: SafeHtml = '';
  safeTHOTAnswer: SafeHtml = '';
  safeFinalAnswer: SafeHtml = '';
  safeFinalAnswer1: SafeHtml = '';
  safeGOTAnswer: SafeHtml = '';
  safeThotRagResult: SafeHtml = '';
  safeThotRagExplanation: SafeHtml = '';
  //covFinalAnswer:any;
  //isLoadingCOV: boolean = false;
  isLoadingOpenAI: boolean = false;
  isLoadingTHOT: boolean = false;
  isLoadingUncertainty: boolean = false;
  isLoadingGOT: boolean = false;
  isLoadingTokenImportance: boolean = false;
  isLoadingSearch: boolean = false;
  isSerperSelected: boolean = false;
  isLoadingCOVRAG: boolean = false;
  isLoadingTHOTRAG: boolean = false;

  // ===== COMPONENT STATE PROPERTIES =====
  option = '';
  metrics = ['uncertainty', 'coherence'];
  firstClick = true;
  isArrowDown: boolean = true;

  // ===== API ENDPOINTS =====
  private COVUrl: any;
  private OpenAIUrl: any;
  private THOTUrl: any;
  private UncertaintyUrl: any;
  private GOTUrl: any;
  private TokenUrl: any;
  private InternetUrl: any;
  private COVRAGUrl: any;
  private THOTRAGUrl: any;
  private rereadUrl: any;
  private lotUrl: any;
  explApiUrl: any;

  // ===== API RESPONSE PROPERTIES =====
  COVRAGTime: any;
  THOTRAGTime: any;
  uncertaintyResult: any;
  rereadResponse: any = {};
  lotResponse: any = {};

  // ===== LOADING AND ERROR STATE PROPERTIES =====
  rereadloading = false;
  lotloading: boolean = false;
  lotShowErrorMessage: boolean = false;
  rereadShowErrorMessage: boolean = false;
  tokenImportanceShowErrorMessage: boolean = false;
  gotShowErrorMessage: boolean = false;

  constructor(private https: HttpClient, private dialog: MatDialog, private sanitizer: DomSanitizer) {}

  // Sanitize HTML content to prevent XSS attacks
  sanitizeHtml(html: any): SafeHtml {
    if (html == null || html == undefined) {
      return '';
    }
    // Allow only basic formatting tags and sanitize the content
    const sanitized = this.sanitizer.sanitize(4, html) || ''; // 4 = SecurityContext.HTML
    return this.sanitizer.bypassSecurityTrustHtml(sanitized);
  }

  // Sanitize and format text content (escape HTML and add line breaks)
  sanitizeText(text: any): SafeHtml {
    if (text == null || text == undefined) {
      return '';
    }
    // Escape HTML characters and convert line breaks
    let sanitized = String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\n\n/g, '<br>')
      .replace(/\n/g, '<br>');
    return this.sanitizer.bypassSecurityTrustHtml(sanitized);
  }

  // Initializes the component and sets up API endpoints
  ngOnInit() {
    this.option = this.explainabilityOption;
    let ip_port: any;
    ip_port = this.getLocalStoreApi();
    // seting up api list
    this.setApilist(ip_port);

    if (this.selectedOptions['Explainability']) {
      if (this.explainabilityOption == 'LLM') {
        this.OpenAI();
        this.GOT();
        this.reread();
        this.logicOfThoughts();
      } else if (this.explainabilityOption == 'RAG') {
        this.COVRAG();
        this.THOTRAG();
      }
    }
    this.topSentiments = this.explainabilityRes?.explanation?.[0]?.token_importance_mapping
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port;
    if (localStorage.getItem('res') != null) {
      const x = localStorage.getItem('res');
      if (x != null) {
        return (ip_port = JSON.parse(x));
      }
    }
  }

  // Sets the API list URLs
  setApilist(ip_port: any) {
    this.COVUrl = ip_port.result.Llm_Explain + ip_port.result.Explain_Cov;
    this.OpenAIUrl = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openai;
    this.THOTUrl = ip_port.result.Llm_Explain + ip_port.result.Explain_Thot;
    this.UncertaintyUrl = ip_port.result.Llm_Explain + ip_port.result.Uncertainty;
    this.GOTUrl = ip_port.result.Llm_Explain + ip_port.result.ExplainGOT;;
    this.TokenUrl = ip_port.result.Llm_Explain + ip_port.result.Token_Importance;
    this.InternetUrl = ip_port.result.Llm_Explain + ip_port.result.SerperResponse;
    this.COVRAGUrl = ip_port.result.Rag + ip_port.result.RagCOV;
    this.THOTRAGUrl = ip_port.result.Rag + ip_port.result.RagTHOT;
    this.explApiUrl = ip_port.result.Explainability;
    this.rereadUrl = ip_port.result.Llm_Explain + ip_port.result.ReReadReason;
    this.lotUrl = ip_port.result.Llm_Explain + ip_port.result.Explain_LOT;
  }

  // Handles actions after the view is initialized
  ngAfterViewInit(): void {
    if (this.explainabilityOption == 'Sentiment') { this.createBarChart(); }
    if (this.tokenImportanceResponse) {
      this.tokens = this.tokenImportanceResponse.token_importance_mapping;
      this.createTokenBarChart();
      this.frequencyDistributionChart();
    } else {
      console.error("tokenImportanceResponse is not available.");
    }
  }

  // ===== UTILITY METHODS =====
  
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  isEmptyObject(obj: any) {
    if (obj == null || obj == undefined) {
      return true;
    }
    return Object.keys(obj).length === 0;
  }

  // ===== CHART CREATION METHODS =====

  // Creates a bar chart for sentiments
  createBarChart(): void {
    const ctx = document.getElementById('myBarChart') as HTMLCanvasElement;

    // Extracting tokens and importance scores from topSentiments
    const labels = this.topSentiments?.map(sentiment => sentiment.token);
    const data = this.topSentiments?.map(sentiment => sentiment.importance_score / 100);
    const backgroundColorPlugin = {
      id: 'customCanvasBackgroundColor',
      beforeDraw: (chart: Chart) => {
        const ctx = chart.canvas.getContext('2d');
        if (ctx) {
          const chartArea = chart.chartArea;
          ctx.save();
          ctx.globalCompositeOperation = 'destination-over';
          ctx.fillStyle = '#c1d1f1a0';
          ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
          ctx.restore();
        }
      }
    };
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Tokens',
          data: data,
          backgroundColor: '#2ca02c',
          borderColor: '#2ca02c',
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            grid: {
              //display: false
            },
            beginAtZero: true,
            min: 0,
            max: 1,
            ticks: {
              stepSize: 0.2
            }
          }
        }
      },
      plugins: [backgroundColorPlugin]
    });
  }

  // Creates a bar chart for token importance
  createTokenBarChart(): void {
    if (!this.tokens || this.tokens.length === 0) {
      return;
    }

    const ctx = document.getElementById('myTokenBarChart') as HTMLCanvasElement;
    if (!ctx) {
      console.error("Canvas element not found.");
      return;
    }

    // Extracting tokens and importance scores from tokens
    const labels = this.tokens.map(token => token.token);
    const data = this.tokens.map(token => token.importance_value);

    const backgroundColorPlugin = {
      beforeDraw: (chart: Chart) => {
        const ctx = chart.canvas.getContext('2d');
        if (ctx) {
          const chartArea = chart.chartArea;
          ctx.save();
          ctx.globalCompositeOperation = 'destination-over';
          ctx.fillStyle = '#c1d1f1a0';
          ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
          ctx.restore();
        }
      }
    };

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Tokens',
          data: data,
          backgroundColor: '#2ca02c',
          borderColor: '#2ca02c',
          borderWidth: 1
        }]
      },
      options: {
        plugins: {
          legend: {
            display: true,
            position: 'top', // You can adjust position as per your preference (top, bottom, left, right)
            labels: {
              generateLabels: function (chart) {
                return [{
                  text: 'Tokens', // Custom label for green bars
                  fillStyle: '#2ca02c', // Color of the bars (green)
                  strokeStyle: '#2ca02c', // Border color (green)
                }];
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            title: {
              display: true,
              text: 'Tokens'
            }
          },
          y: {
            grid: {
              //display: false
            },
            beginAtZero: true,
            min: 0,
            max: 1,
            ticks: {
              stepSize: 0.2
            },
            title: {
              display: true,
              text: 'Importance Score'
            }
          }
        }
      }
    });
  }

  // Creates a frequency distribution chart for tokens
  frequencyDistributionChart(): void {
    if (!this.tokens || this.tokens.length === 0) {
      return;
    }

    const ctx = document.getElementById('myDistributionBarChart') as HTMLCanvasElement;
    if (!ctx) {
      console.error("Canvas element not found.");
      return;
    }

    // Group frequencies into specified ranges, starting with '0'
    const ranges = ['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'];
    const rangeCounts = { '0': 0, '0.1': 0, '0.2': 0, '0.3': 0, '0.4': 0, '0.5': 0, '0.6': 0, '0.7': 0, '0.8': 0, '0.9': 0, '1.0': 0 };

    this.tokens.forEach((token: any) => {
      const value = token.importance_value;
      if (value === 0) {
        rangeCounts['0']++;
      } else if (value > 0 && value < 0.1) {
        rangeCounts['0.1']++;
      } else if (value >= 0.1 && value < 0.2) {
        rangeCounts['0.2']++;
      } else if (value >= 0.2 && value < 0.3) {
        rangeCounts['0.3']++;
      } else if (value >= 0.3 && value < 0.4) {
        rangeCounts['0.4']++;
      } else if (value >= 0.4 && value < 0.5) {
        rangeCounts['0.5']++;
      } else if (value >= 0.5 && value < 0.6) {
        rangeCounts['0.6']++;
      } else if (value >= 0.6 && value < 0.7) {
        rangeCounts['0.7']++;
      } else if (value >= 0.7 && value < 0.8) {
        rangeCounts['0.8']++;
      } else if (value >= 0.8 && value < 0.9) {
        rangeCounts['0.9']++;
      } else if (value >= 0.9 && value <= 1.0) {
        rangeCounts['1.0']++;
      }
    });

    const data = Object.values(rangeCounts) as number[];

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ranges,
        datasets: [
          {
            label: 'Distribution of Importance Scores',
            data: data,
            backgroundColor: '#1f77b4',
            borderColor: '#1f77b4',
            borderWidth: 1,
            order: 2 // This dataset is behind the line
          },
          {
            label: 'Frequency Line',
            data: data,
            type: 'line',
            borderColor: 'red',
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
            tension: 0.4,
            order: 1 // This dataset is in front of the bars
          }
        ]
      },
      options: {
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              generateLabels: function (chart) {
                return [
                  {
                    text: 'Distribution of Importance Scores', // Custom label for blue
                    fillStyle: '#1f77b4', // Color of the bar (blue)
                    strokeStyle: '#1f77b4', // Border color (blue)
                  },
                  {
                    text: 'Frequency Line', // Custom label for red line
                    fillStyle: 'red', // Color of the line (red)
                    strokeStyle: 'red', // Border color (red)
                  }
                ];
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            title: {
              display: true,
              text: 'Importance Score Range'
            }
          },
          y: {
            beginAtZero: true,
            min: 0,
            title: {
              display: true,
              text: 'Frequency'
            },
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
  }

  // Updates the top tokens based on importance scores
  updatetopTokens() {
    this.topTokens = this.tokens
      .sort((a: any, b: any) => b.importance_score - a.importance_score);
    this.topTokens = this.topTokens.slice(0, 10);
  }

  // ===== UI INTERACTION METHODS =====

  // Opens a right-side modal with the provided data
  openRightSideModal(data: any) {
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop'
    });
  }

  // Toggles the arrow state and triggers token importance API
  toggleArrow() {
    this.isArrowDown = !this.isArrowDown;
    if (this.firstClick === true) {
      this.TokenImportance();
    }
    this.firstClick = false;
  }

  // ===== API METHODS =====

  // Calls the OpenAI API for explainability
  OpenAI() {
    this.isLoadingOpenAI = true;
    const payload1 = {
      temperature: '0',
      model_name: this.selectedExplainabilityModel,
      Prompt: this.prompt
    };

    this.https.post(this.OpenAIUrl, payload1)
      .pipe(takeUntil(this.destroy$))
      .subscribe((response: any) => {
        console.log('API response:', response);
        this.openAIAnswer = response.text.replace(/\n\n/g, '<br>');
        this.safeOpenAIAnswer = this.sanitizeText(response.text);
        this.isLoadingOpenAI = false;
        this.THOT();
        this.toggleSearch();  
      }, error => {
        console.error('API error:', error);
        this.isLoadingOpenAI = false;
      });
  }

  // Calls the THOT API for explainability
  THOT() {
    this.isLoadingTHOT = true;
    const payload2 = {
      temperature: '0',
      modelName: this.selectedExplainabilityModel,
      inputPrompt: this.prompt
    };

    this.https.post(this.THOTUrl, payload2)
.pipe(takeUntil(this.destroy$)).subscribe((apiResponse: any) => {
const resultValue = apiResponse.response.result;
const explanationValue = apiResponse.response.explanation;
       this.THOTAnswer= `${resultValue}<br><br/>${explanationValue}`;
    
        const payload3 = {
          inputPrompt: this.prompt,
          response: this.openAIAnswer,
          modelName: 'gpt-4o'
        };
        this.Uncertanity(payload3,"thot");
        this.isLoadingTHOT = false;
      }, error => {
        console.error('API error:', error);
        this.isLoadingTHOT = false;
      });
  }

  Uncertanity(payload: any, thought: any) {
    this.isLoadingUncertainty = true;
    this.https.post(this.UncertaintyUrl, payload).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      if (thought == "thot") {
        this.UncertaintyAIMetric = response;
      } else {
        this.UncertaintyGotMetric = response;
      }
      this.isLoadingUncertainty = false;
    }, 
    error => {
      console.error('API error:', error);
      this.isLoadingUncertainty = false;
    });
  }

  displayMetrics(response: any) {
    const metrics = ['uncertainty', 'coherence'];
    let tableHtml = '<table style="border-collapse: collapse; width: 100%;">';
    tableHtml += '<tr><th style="padding: 8px;">Metric</th><th>Score</th><th style="padding: 8px;">Explanation</th><th style="padding: 8px;">Recommendation</th></tr>';

    metrics.forEach(metric => {
      if (response[metric]) {
        // Sanitize all user-provided content to prevent XSS
        const sanitizedMetric = this.sanitizeForHtml(metric.charAt(0).toUpperCase() + metric.slice(1));
        const sanitizedScore = this.sanitizeForHtml(response[metric].score);
        const sanitizedExplanation = this.sanitizeForHtml(response[metric].explanation);
        const sanitizedRecommendation = this.sanitizeForHtml(response[metric].recommendation);
        
        tableHtml += `<tr>
          <td style="padding: 8px;">${sanitizedMetric}</td>
          <td style="padding: 8px;">${sanitizedScore}</td>
          <td style="padding: 8px;">${sanitizedExplanation}</td>
          <td style="padding: 8px;">${sanitizedRecommendation}</td>
        </tr>`;
      }
    });

    tableHtml += '</table>';
    const metricsTableElement = document.getElementById('metricsTable');
    if (metricsTableElement) {
      metricsTableElement.innerHTML = tableHtml;
    }
  }

  // Sanitize content for HTML insertion (escapes dangerous characters)
  private sanitizeForHtml(content: any): string {
    if (content == null || content == undefined) {
      return '';
    }
    return String(content)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  }

  // Calls the token importance API
  TokenImportance() {
    this.isLoadingTokenImportance = true;
    this.tokenImportanceShowErrorMessage = false;
    const payload5 = {
      inputPrompt: this.prompt,
      modelName: 'GPT',
    };

    this.https.post(this.TokenUrl, payload5).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.tokenImportanceResponse = response;
      this.isLoadingTokenImportance = false;
      this.tokens = this.tokenImportanceResponse?.token_importance_mapping;
      this.updatetopTokens();
      this.createTokenBarChart()
      this.frequencyDistributionChart();
      this.tokenImportanceShowErrorMessage = false;
    }, 
    error => {
      console.error('API error:', error);
      this.isLoadingTokenImportance = false;
      this.tokenImportanceShowErrorMessage = true;
    });
  }

  // Calls the reread API for explainability
  reread() {
    const payload1 = {
      inputPrompt: this.prompt,
      modelName: this.selectedExplainabilityModel
    }
    this.rereadShowErrorMessage = false;
    this.rereadloading = true;
    this.https.post(this.rereadUrl, payload1).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.rereadloading = false;
      this.rereadShowErrorMessage = false;
      this.rereadResponse.rereadResult = response.response.result.replace(/\n/g, '<br>');;
      this.rereadResponse.rereadExplanation = response.response.explanation.replace(/\n/g, '<br>');
      this.rereadResponse.rereadTimeTaken = response.time_taken;
      const payload2 = {
        inputPrompt: this.prompt,
        response: this.rereadResponse.rereadResult + ' ' + this.rereadResponse.rereadExplanation,
        modelName: this.selectedExplainabilityModel
      };
      this.https.post(this.UncertaintyUrl, payload2).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
        this.uncertaintyResult = response;
        this.rereadloading = false;
        this.rereadShowErrorMessage = false;
      }, 
      error => {
        this.rereadloading = false;
        this.rereadShowErrorMessage = true;
        let message;
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in Reread API";
        }
      });
    }, 
    error => {
      console.error('API error:', error);
      this.rereadloading = false;
      this.rereadShowErrorMessage = true;
      let message
      if (error.status === 500) {
        message = "Internal Server Error. Please try again later.";
      } else {
        message = error.error.detail || error.error.message || "Error in  Reread API";
      }
    });
  }

  // Calls the logic of thoughts API
  logicOfThoughts() {
    const payload = {
      inputPrompt: this.prompt,
      llmResponse: null,
      modelName: this.selectedExplainabilityModel
    };
    this.lotloading = true;
    this.lotShowErrorMessage = false;
    this.https.post(this.lotUrl, payload).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.lotloading = false;
      this.lotShowErrorMessage = false;
      this.lotResponse.lotExplanation = response.response.Explanation;
      this.lotResponse.lotPropositions = response.response.Propositions;
      this.lotResponse.lotExpression = response.response['Logical Expression'];
      this.lotResponse.lotExtendExplanation = response.response['Extended Logical Expression'];
      this.lotResponse.lotReasoningLaw = response.response['Law used to extend the logical expression'];
      this.lotResponse.lotExtendInfo = response.response['Extended Logical Information'];
      this.lotResponse.lotTimeTaken = response.time_taken;
    },
    error => {
      this.lotloading = false;
      this.lotShowErrorMessage = true;
      let message
      if (error.status === 500) {
        message = "API got Error. Please try again later.";
      } else {
        message = error.error.detail || error.error.message || "Error in  logicOfThoughts API";
      }
    });
  }

  // Calls the GOT API for explainability
  GOT() {
    this.isLoadingGOT = true;
    this.gotShowErrorMessage = false;
    const payload4 = {
      inputPrompt: this.prompt,
      modelName: this.selectedExplainabilityModel,
    };

    this.https.post(this.GOTUrl, payload4)
      .pipe(takeUntil(this.destroy$))
      .subscribe((response: any) => {
        this.apiResult = response;
        this.GOTAnswer = response.final_thought.replace(/\n/g, '<br>');
        this.safeGOTAnswer = this.sanitizeText(response.final_thought);
        this.gotShowErrorMessage = false;
        const payload = {
          inputPrompt: this.prompt,
          response: response.final_thought,
          modelName:this.selectedExplainabilityModel
        };
      this.Uncertanity(payload,"got");
        this.isLoadingGOT = false;
        this.gotShowErrorMessage = false;
      }, error => {
        console.error('API error:', error);
        this.isLoadingGOT = false;
        this.gotShowErrorMessage = true;
      });
  }

  // Handles the toggle for the search option
  onToggleSearch(event: Event) {
    const inputElement = event.target as HTMLInputElement;
    this.isSerperSelected = inputElement.checked;
    if (this.isSerperSelected) {
      //this.finalAnswer = this.InternetResponse.internetResponse[0];
      this.finalAnswer = this.sanitizeText(this.InternetResponse.internetResponse[0]);
    }else {
      //this.finalAnswer = this.covFinalAnswer;
      this.finalAnswer = this.sanitizeText(this.covFinalAnswer);
    }
  }

  // Calls the Internet search API
  toggleSearch() {
    this.isLoadingSearch = true;
    const payload6 = {
      inputPrompt: this.prompt,
      llm_response: this.openAIAnswer,
      modelName: this.selectedExplainabilityModel,
    };
    this.https.post(this.InternetUrl, payload6).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.InternetResponse = response;
      this.InternetSearchMetric = response.metrics[0];
      this.isLoadingSearch = false;
    },
    error => {
      console.error('API error:', error);
      this.isLoadingSearch = false;
    });
  }

  // Calls the COVRAG API for explainability
  COVRAG() {
    this.isLoadingCOVRAG = true;

    const payload7 = {
      complexity: 'simple',
      fileupload: 'true',
      text: this.prompt,
      vectorstoreid: this.ExplanabilityFileId?.id,
      llmtype: 'openai'
    };

    this.https.post(this.COVRAGUrl, payload7)
      .pipe(takeUntil(this.destroy$))
      .subscribe((response: any) => {
        const covResponse = response.cov_response;      
        this.finalAnswer1 = covResponse.final_answer;      
        this.safeFinalAnswer1 = this.sanitizeText(covResponse.final_answer);
        let formattedText = covResponse.verification_answers
          .replace(/Question:/g, '<br><br>Question:')
          .replace(/Answer:/g, '<br>Answer:');      
        this.COVRAGResponse = formattedText; 
        this.COVRAGTime = response.timetaken;     
        console.log('COVRAGResponse response:', this.COVRAGResponse);
        this.isLoadingCOVRAG = false;
        console.log('COVRAG finished, isLoadingCOVRAG:', this.isLoadingCOVRAG);
      }, error => {
        console.error('API error:', error);
        this.isLoadingCOVRAG = false;
        console.log('COVRAG error, isLoadingCOVRAG:', this.isLoadingCOVRAG);
      });
  }

  // Calls the THOTRAG API for explainability
  THOTRAG() {
    this.isLoadingTHOTRAG = true;
    const payload8 = {
      fileupload: 'true',
      text: this.prompt,
      vectorstoreid: this.ExplanabilityFileId?.id,
      llmtype: 'openai',
      embeddingmodel: 'local'
    };

    this.https.post(this.THOTRAGUrl, payload8).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.THOTRAGResponse = response.thot_response;
      this.THOTRAGSource = response['source-name'];
      this.THOTRAGTime = response.timetaken;
      this.splitFunction();
      this.isLoadingTHOTRAG = false;
    },
    error => {
      console.error('API error:', error);
      this.isLoadingTHOTRAG = false;
    });
  }

  // Splits the THOTRAG response into result and explanation
  splitFunction() {
    const lines = this.THOTRAGResponse.split('\n');
    let explanationValue = '';
    let isExplanation = false;
    const resultLine = lines.find(line => line.startsWith('Result:'));
    const resultAnswer = lines.find(line => line.startsWith('Answer:'));
    let resultValue;
    if (resultLine) {
      resultValue = resultLine.split('Result:')[1];
    } else if (resultAnswer) {
      resultValue = resultAnswer.split('Answer:')[1];
   }
   this.ThotRagResult = resultValue?.replace(/"/g, ''); // Remove the surrounding quotes
   this.safeThotRagResult = this.sanitizeText(this.ThotRagResult);

    const explanationParts: string[] = [];

for (const line of lines) {
  if (line.startsWith('Explanation:')) {
    isExplanation = true;

    const value = line.split('Explanation:')[1]?.trim();
    if (value) {
      explanationParts.push('<br>' + value);
    }
  } else if (line.startsWith('Source:')) {
    isExplanation = false;
    break;
  } else if (isExplanation) {
    explanationParts.push(line.trim());
  }
}

// Join once (outside loop)
 explanationValue = explanationParts.join('\n');

    this.ThotRagExplanation = explanationValue.replace(/"/g, '').replace(/\n/g, '<br>');
    this.safeThotRagExplanation = this.sanitizeText(explanationValue.replace(/"/g, ''));
    console.log('Explanation:', this.ThotRagExplanation);

  }
      // Cleanup subscriptions
      ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
      }
}
