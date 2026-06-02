/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input, SimpleChanges } from '@angular/core';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ResponseComparisonService } from './response-comparison.service';
import { SharedDataService } from 'src/app/services/shared-data.service';
import { ChangeDetectorRef } from '@angular/core';
import Chart from 'chart.js/auto';
import ChartAnnotation from 'chartjs-plugin-annotation';
Chart.register(ChartAnnotation);

@Component({
  selector: 'app-response-comparison',
  templateUrl: './response-comparison.component.html',
  styleUrls: ['./response-comparison.component.css'],

})
export class ResponseComparisonComponent {

  // ========================= INPUT PROPERTIES =========================
  // Core State and Configuration
  @Input() fmRes: any;
  @Input() prompt: any;
  @Input() submitFlag: any;
  @Input() selectedUseCaseName: any;
  @Input() hallucinationSwitchCheck: boolean = false;
  @Input() selectedTranslate: any;
  @Input() UploadedFile: any;
  @Input() vectorId: any;
  @Input() fileupload: any;

  // AI Model States
  @Input() openAIRes: any;
  @Input() cotState: any;
  @Input() thotState: any;
  @Input() covState: any;
  @Input() tokenImpState: any;
  @Input() gotState: any;
  @Input() rereadState: any = { status: '' };
  @Input() lotState: any = { status: '' };
  @Input() logicOfThoughtsState: any = { status: '' };
  @Input() llmExplainState: any;

  // Moderation and Results
  @Input() nemoModerationRailRes: any;
  @Input() hallucinateRetrievalKeplerRes: any;
  @Input() gEvalres: any;
  @Input() serperResponseState: any;
  @Input() lightRag: any;

  // Multimodal Content
  @Input() MMImageResponse: any;
  @Input() MMTimeTaken: any;
  @Input() MMImageTHOT: any;
  @Input() MMImageCOV: any;
  @Input() MMImageCOT: any;
  @Input() MMImageHallucinationScore: any;
  @Input() MMPdfReference: any;
  @Input() isLoadingMMImage: boolean = false;
  @Input() enableSearch: any;

  // Evaluation Scores
  @Input() faithfulnessScore: any;
  @Input() relevanceScore: any;
  @Input() adhernceScore: any;
  @Input() correctnessScore: any;
  @Input() averageScore: any;
  @Input() faithfulness: any;
  @Input() relevance: any;
  @Input() adhernce: any;
  @Input() correctness: any;

  // ========================= COMPONENT STATE =========================
  // UI State Management
  activeTab = 'Faithfulness Check';
  isArrowDown: boolean = true;
  isMultimodal = false;

  // Collapse States
  isCollapsed = false;
  isGOTCollapsed = false;
  isTokenCollapsed = false;
  isCOTCollapsed = false;
  isTHOTCollapsed = false;
  isRereadCollapsed = false;
  isLotCollapsed = false;
  isLogicOfThoughtsCollapsed = false;

  // API Management
  ApiCallHappened = new Set<string>();
  isLoading: boolean = false;

  // Configuration
  model_name = 'gpt4';
  selectCoveComplexity: any = 'simple';
  selectedLlmModel: any = 'gpt4';
  metrics = ['uncertainty', 'coherence'];

  // ========================= RESPONSE DATA =========================
  // Core Responses
  covResponse: any = {};
  cotResponse: any = {};
  thotResponse: any = {};
  tokenImportanceResponse: any = {};
  llmExplainResponse: any = {};
  apiResult: any = {};
  GOTAnswer: string = '';

  // Specialized Responses
  rereadResponse: any = {};
  rereadResult: any;
  rereadExplanation: any;
  lotResponse: any = {};
  logicOfThoughtsResponse: any = {};

  // Search and Format
  isSerperSelected: any = false;
  responseSerper: any = {};
  responseSerperStatus = '';
  generatedTextFormatted = '';

  // Shared Data
  templateBasedResponse: any = {};
  naviResponse: any = {};
  imageFailedCases: any = {};

  // ========================= ANALYSIS DATA =========================
  // Uncertainty Metrics
  UncertaintyAIMetric: any;
  UncertaintyGotMetric: any;
  UncertaintyCotMetric: any;
  uncertaintyResult: any;

  // Token Analysis
  topTokens: any[] = [];
  tokens: any[] = [];

  // ========================= UI RESOURCES =========================
  // URLs and Assets
  MMImageUrl = '';

  // Chart Management
  chartInstance: Chart | null = null;
  myDistributionBarChart1Instance: Chart | null = null;
  tokenBarChartCreated: boolean = false;
  frequencyChartCreated: boolean = false;

  // ========================= CONSTRUCTOR =========================
  constructor(
    private dialog: MatDialog,
    private responseService: ResponseComparisonService,
    public _snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef,
    private sharedDataService: SharedDataService
  ) {
    this.initializeSharedDataSubscriptions();
  }

  // ========================= LIFECYCLE HOOKS =========================
  ngOnInit(): void {
    this.initializeComponent();
  }

  ngAfterViewChecked(): void {
    this.handleTokenChartCreation();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['cotState']) {
      console.log('cotState changed:', this.cotState);
    }
  }

  // ========================= INITIALIZATION METHODS =========================
  private initializeSharedDataSubscriptions(): void {
    this.sharedDataService.templateBasedResponses.subscribe(response => {
      this.templateBasedResponse = response;
    });

    this.sharedDataService.imageBasedFailedChecks.subscribe(response => {
      this.imageFailedCases = response;
    });

    this.sharedDataService.naviToneModerationRes.subscribe(response => {
      this.naviResponse = response;
    });
  }

  private initializeComponent(): void {
    const ip_port = this.getLocalStoreApi();
    this.setApilist(ip_port);
    this.responseService.fetchApiUrl();
    this.model_name = this.serperResponseState?.model || 'gpt4';
    this.cdr.detectChanges();
    
    if (this.submitFlag && !this.hallucinationSwitchCheck) {
      this.covgetApi();
    }
    this.checkMultimodalContent();
  }

  private checkMultimodalContent(): void {
    if (this.UploadedFile?.type?.startsWith('image/') || 
        this.UploadedFile?.type?.startsWith('audio/') || 
        this.UploadedFile?.type?.startsWith('video/') 
      ) {
      this.isMultimodal = true;
    }
  }

  private handleTokenChartCreation(): void {
    if (this.isTokenCollapsed && this.tokens.length > 0) {
      if (!this.tokenBarChartCreated) {
        this.createTokenBarChart();
        this.tokenBarChartCreated = true;
      }
      if (!this.frequencyChartCreated) {
        this.frequencyDistributionChart();
        this.frequencyChartCreated = true;
      }
    }
  }

  // ========================= CONFIGURATION METHODS =========================
  private getLocalStoreApi(): any {
    const storedData = localStorage.getItem('res');
    return storedData ? JSON.parse(storedData) : null;
  }

  private setApilist(ip_port: any): void {
    if (ip_port?.result) {
      this.MMImageUrl = ip_port.result.Rag + ip_port.result.MMImageUrl;
    }
  }

  // ========================= UI UTILITY METHODS =========================
  formatText(text: any): string {
    if (!text) return '';
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
  }

  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  changeTab = (tab: string): void => {
    this.activeTab = tab;
  }

  isEmptyObject(obj: any): boolean {
    return obj == null || obj == undefined || Object.keys(obj).length === 0;
  }

  isNonEmptyArray(value: any): boolean {
    return Array.isArray(value) && value.length > 0;
  }

  // ========================= UI INTERACTION METHODS =========================
  toggleArrow(): void {
    this.isArrowDown = !this.isArrowDown;
  }

  toggleCollapse(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  toggleTHOTCollapse(): void {
    this.isTHOTCollapsed = !this.isTHOTCollapsed;
  }

  toggleCOTCollapse(): void {
    this.isCOTCollapsed = !this.isCOTCollapsed;
  }

  toggleRereadCollapse(): void {
    this.isRereadCollapsed = !this.isRereadCollapsed;
  }

  toggleLotCollapse(): void {
    this.isLotCollapsed = !this.isLotCollapsed;
  }

  toggleGOTCollapse(): void {
    this.isGOTCollapsed = !this.isGOTCollapsed;
  }

  toggleTokenCollapse(): void {
    this.isTokenCollapsed = !this.isTokenCollapsed;
    this.tokenBarChartCreated = false;
    this.frequencyChartCreated = false;
  }

  toggleLogicOfThoughtsCollapse(): void {
    this.isLogicOfThoughtsCollapsed = !this.isLogicOfThoughtsCollapsed;
  }

  // ========================= MODAL AND NOTIFICATION METHODS =========================
  openRightSideModal(data: any): void {
    this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop'
    });
  }

  openSnackBar(message: string, action: string): void {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  openSource(baseResUrl: any): void {
    const binaryPdf = atob(baseResUrl);
    const blobPdf = new Blob([new Uint8Array(Array.from(binaryPdf).map(c => c.charCodeAt(0)))], { type: 'application/pdf' });
    const pdfUrl = URL.createObjectURL(blobPdf);
    window.open(pdfUrl, '_blank');
  }

  // ========================= ERROR HANDLING HELPER =========================
  private handleApiError(error: any, apiName: string, stateProperty: any, apiCallKey: string): void {
    console.log(`--RESPONSIBLE-COMPARISON-|||-Error-in-${apiName}`, error);
    stateProperty.status = 'FAILED';
    this.ApiCallHappened.delete(apiCallKey);
    
    const message = error.status === 500 
      ? "Internal Server Error. Please try again later."
      : error.error?.detail || error.error?.message || `Error in ${apiName}`;
    
    this.openSnackBar(message, "Close");
  }

  // ========================= API METHODS =========================
  // Chain of Verification API
  covgetApi() {
    if (this.ApiCallHappened.has('covgetApi')) {
      return;
    }
    this.covState.status = 'inPROCESS';
    this.ApiCallHappened.add('covgetApi');
    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      const payload = {
        fileupload: this.fileupload,
        text: this.prompt,
        vectorstoreid: this.vectorId,
        complexity: "simple",
        llmtype:'openai',
      };
      apiObservable = this.responseService.hallucinateCOV(payload);
    } 
    else {
      const payload1 = {
        text: this.prompt,
        complexity: this.selectCoveComplexity,
        model_name: this.selectedLlmModel,
        translate: this.selectedTranslate
      }
      apiObservable = this.responseService.covgetApi(payload1);
    }

    apiObservable.subscribe((res: any) => {
      if (this.hallucinationSwitchCheck) {
        this.covResponse.baseline = res.cov_response.baseline_response.replace(/\n/g, '<br>');
        this.covResponse.verification = res.cov_response.verification_answers.replace(/\n/g, '<br>');
        this.covResponse.final = res.cov_response.final_answer.replace(/\n/g, '<br>');
      } 
      else {
        this.covResponse.baseline = res.baseline_response.replace(/\n/g, '<br>');
        let formattedText = res.verification_answers
          .replace(/Question: 1/, 'Question: 1')
          .replace(/Question: 2/, '<br><br>Question: 2')
          .replace(/Question: 3/, '<br><br>Question: 3')
          .replace(/Question: 4/, '<br><br>Question: 4')
          .replace(/Question: 5/, '<br><br>Question: 5')
          .replace(/Answer:/g, '<br>Answer:');
        this.covResponse.verification = formattedText;
        this.covResponse.final = res.final_answer.replace(/\n/g, '<br>');
        this.generatedTextFormatted = res.final_answer.replace(/\n/g, '<br>');
      }
      this.covResponse.timetaken = res.timetaken;
    },
    error => {
      this.handleApiError(error, 'COV-API', this.covState, 'covgetApi');
    });
  }

  // Chain of Thoughts API
  callCOT() {
    this.cotState.payload = {
      temperature: '0',
      Prompt: this.prompt,
      model_name: this.selectedLlmModel
    };
    if (this.ApiCallHappened.has('openAicotgetApi')) {
      return;
    }
    this.cdr.detectChanges();

    this.cotState.status = 'inPROCESS';
    this.ApiCallHappened.add('openAicotgetApi');

    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      const payload = {
        fileupload: this.fileupload,
        text: this.prompt,
        vectorstoreid: this.vectorId,
        llmtype: "openai",
        embeddingmodel: "local"
      };
      apiObservable = this.responseService.hallucinateCOT(payload);
    } 
    else {
      apiObservable = this.responseService.openAicotgetApi(this.cotState.payload);
    }

    apiObservable.subscribe((res: any) => {
      if (this.hallucinationSwitchCheck) {
        this.cotResponse.text = res.cot_response.replace(/\n/g, '<br>').split('Source:')[0];
        this.cotResponse.sourceText = res['source-name'];
        this.cotResponse.token_cost = res['token_cost'];
        const payload1 = {
          inputPrompt: this.llmExplainState.payload['inputPrompt'],
          response: this.cotResponse.text,
          modelName: "gpt-4o"
        };
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyCotMetric = res;
        },
        error => {
          this.handleApiError(error, 'llmExplain', this.llmExplainState, 'llmExplain');
        });
      }
      else {
        this.cotResponse.text = res.text.replace(/\n/g, '<br>');
        const payload1 = {
          inputPrompt: this.llmExplainState.payload['inputPrompt'],
          response: this.cotResponse.text,
          modelName: "gpt-4o"
        };
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyCotMetric = res;
        },
        error => {
          this.handleApiError(error, 'llmExplain', this.llmExplainState, 'llmExplain');
        });
      }
      this.cotResponse.timetaken = res.timetaken;
    },
    error => {
      this.handleApiError(error, 'openAicotgetApi', this.cotState, 'openAicotgetApi');
    });
  }

  // Logic of Thoughts (LOT) API
  callLOT() {
    if (this.ApiCallHappened.has('logicOfThoughts')) {
      return;
    }
    this.logicOfThoughtsState.status = 'inPROCESS';
    this.ApiCallHappened.add('logicOfThoughts');

    const payload = {
      fileupload: this.fileupload,
      text: this.prompt,
      "llmtype": "openai",
      vectorstoreid: this.vectorId,
      embeddingmodel: "local"
    }
    this.responseService.lot(payload).subscribe((res: any) => {
      this.logicOfThoughtsResponse.text = res.lot_response.replace(/\n/g, '<br>').split('Source:')[0];
      this.logicOfThoughtsResponse.source_name = res['source-name'];
      this.logicOfThoughtsResponse.timetaken = res.timetaken;
      this.logicOfThoughtsResponse.token_cost = res.token_cost;
    },
    error => {
      this.handleApiError(error, 'logicOfThoughts', this.logicOfThoughtsState, 'logicOfThoughts');
    });
  }

  // Thread of Thoughts (THOT) API
  callTHOT() {
    if (this.ApiCallHappened.has('openAiTHOTApi')) {
      return;
    }
    this.thotState.status = 'inPROCESS';
    this.ApiCallHappened.add('openAiTHOTApi');

    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      const payload = {
        fileupload: this.fileupload,
        text: this.prompt,
        "llmtype": "openai",
        embeddingmodel: "local",
        vectorstoreid: this.vectorId
      };
      apiObservable = this.responseService.hallucinateThot(payload);
    } 
    else {
      apiObservable = this.responseService.openAiTHOTApi(this.thotState.payload);
    }

    apiObservable.subscribe((res: any) => {
      if (this.hallucinationSwitchCheck) {
        this.thotResponse.thot_response = res.thot_response.replace(/\n/g, '<br>').split('Source:')[0];
        this.thotResponse.sourceText = res['source-name']
        this.thotResponse.token_cost = res['token_cost']
        const payload1 = {
          inputPrompt: this.llmExplainState.payload['inputPrompt'],
          response: this.thotResponse.thot_response,
          modelName: "gpt-4o"
        };
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyAIMetric = res;
        },
        error => {
          this.handleApiError(error, 'LLM Explain API', this.llmExplainState, 'llmExplain');
        });
      } 
      else {
        let formattedText = res.text
          .replace(/Result:/g, '<br>')
          .replace(/Explanation:/g, '<br>')
          .replace(/\n\n/g, '<br>')
          .replace(/\n/g, '<br>');
        this.thotResponse.thot_response = formattedText;

        const lines = res?.text?.split('\n');
        const resultLine = lines.find((line: any) => line.startsWith('Result:'));
        const explanationLine = lines.find((line: any) => line.startsWith('Explanation:'));

        const payload1 = {
          inputPrompt: this.llmExplainState.payload['inputPrompt'],
          response: this.thotResponse.thot_response,
          modelName: "gpt-4o"
        };
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyAIMetric = res;
        },
        error => {
          this.handleApiError(error, 'LLM Explain API', this.llmExplainState, 'llmExplain');
        });
      }
      this.thotResponse.timetaken = res.timetaken;
    },
    error => {
      this.handleApiError(error, 'Open Ai THOT Api', this.thotState, 'openAiTHOTApi');
    });
  }

  // ========================= CHART METHODS =========================
  // Token Importance Bar Chart
  createTokenBarChart(): void {
    if (!this.tokens || this.tokens.length === 0) {
      return;
    }

    const ctx = document.getElementById('myTokenBarChart1') as HTMLCanvasElement;
    if (!ctx) {
      console.error("Canvas element not found.");
      return;
    }

    // Destroy the existing chart instance if it exists
    if (this.chartInstance) {
      this.chartInstance.destroy();
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

    this.chartInstance = new Chart(ctx, {
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

  // Token Frequency Distribution Chart
  frequencyDistributionChart(): void {
    if (!this.tokens || this.tokens.length === 0) {
      return;
    }

    const ctx = document.getElementById('myDistributionBarChart1') as HTMLCanvasElement;
    if (!ctx) {
      console.error("Canvas element not found.");
      return;
    }

    // Destroy the existing chart instance if it exists
    if (this.myDistributionBarChart1Instance) {
      this.myDistributionBarChart1Instance.destroy();
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

    this.myDistributionBarChart1Instance = new Chart(ctx, {
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

  // ========================= TOKEN ANALYSIS METHODS =========================
  // Update Top Tokens
  updatetopTokens() {
    this.topTokens = this.tokens
      .sort((a: any, b: any) => b.importance_score - a.importance_score);
    this.topTokens = this.topTokens.slice(0, 10);
  }

  // Token Importance API
  tokenImportance() {
    if (this.ApiCallHappened.has('tokenImportance')) {
      return;
    }
    this.tokenImpState.status = 'inPROCESS'
    this.ApiCallHappened.add('tokenImportance');

    this.responseService.tokenImportance(this.tokenImpState.payload).subscribe(
      (res: any) => {
        this.tokenImportanceResponse = res;
        this.tokens = res?.token_importance_mapping;

        this.updatetopTokens();

        this.createTokenBarChart();

        this.frequencyDistributionChart();
      },
      error => {
       this.handleApiError(error, 'token Importance API', this.tokenImpState, 'tokenImportance');
      });
  }

  // ========================= SEARCH AND UTILITY METHODS =========================
  // Toggle Search Functionality
  toggleSearch(event: any) {
    this.isSerperSelected = event.target.checked;
    if (this.isSerperSelected) {
      this.responseSerper = {};
      this.serperResponseState.payload['llm_response'] = this.fmRes?.moderationResults?.responseModeration?.generatedText;
      this.responseService.serperResponse(this.serperResponseState.payload).subscribe((res: any) => {
        this.responseSerper = res.metrics[0];
        this.generatedTextFormatted = res.internetResponse[0];
      }, 
      (error) => {
        this.responseSerperStatus = 'FAILED';
        this.handleApiError(error, 'Serper API', this.serperResponseState, 'serperResponse');
      });
    }
    else {
      this.generatedTextFormatted = this.formatText(this.fmRes?.moderationResults?.responseModeration?.generatedText);
    }
  }

  // ========================= ANALYSIS API METHODS =========================  
  // ReRead Analysis API
  reread() {
    if (this.ApiCallHappened.has('reread')) {
      return;
    }
    this.rereadState.status = 'inPROCESS';
    this.ApiCallHappened.add('reread');

    const payload1 = {
      inputPrompt: this.prompt,
      modelName: 'GPT4'
    };
    this.responseService.reread(payload1).subscribe((response: any) => {
      this.rereadResponse.rereadResult = response.response.result.replace(/\n/g, '<br>');
      this.rereadResponse.rereadExplanation = response.response.explanation.replace(/\n/g, '<br>');
      this.rereadResponse.rereadTimeTaken = response.time_taken;
      const payload2 = {
        inputPrompt: this.llmExplainState.payload['inputPrompt'],
        response: this.rereadResult + ' ' + this.rereadExplanation,
        modelName: "gpt-4o"
      };
      this.responseService.llmExplain(payload2).subscribe((response: any) => {
        this.uncertaintyResult = response;
      }, 
      error => {
        this.handleApiError(error, 'LLM Explain API', this.llmExplainState, 'llmExplain');
      });
    }, 
    error => {
      this.handleApiError(error, 'Reread API', this.rereadState, 'reread');
    });
  }

  // Logic of Thoughts Analysis API
  logicOfThoughts() {
    if (this.ApiCallHappened.has('lot')) {
      return;
    }
    this.lotState.status = 'inPROCESS';
    this.ApiCallHappened.add('lot');

    const payload = {
      inputPrompt: this.prompt,
      llmResponse: null,
      modelName: 'GPT4'
    };
    this.responseService.logicOfThoughts(payload).subscribe((response: any) => {
      this.lotResponse.lotExplanation = response.response.Explanation;
      this.lotResponse.lotPropositions = response.response.Propositions;
      this.lotResponse.lotExpression = response.response['Logical Expression'];
      this.lotResponse.lotExtendExplanation = response.response['Extended Logical Expression'];
      this.lotResponse.lotLaw = response.response['Law used to extend the logical expression'];
      this.lotResponse.lotExtendInfo = response.response['Extended Logical Information'];
      this.lotResponse.lotTimeTaken = response.time_taken;
    },
    error => {
      this.handleApiError(error, 'LogicOfThoughts API', this.lotState, 'lot');
    });
  }

  // Graph of Thoughts (GOT) API
  getGOT() {
    if (this.ApiCallHappened.has('got')) {
      return;
    }
    this.gotState.status = 'inPROCESS'
    this.ApiCallHappened.add('got');
    this.responseService.gotResponse(this.gotState.payload).subscribe(
      (res: any) => {
        this.apiResult = res;
        this.GOTAnswer = res.final_thought.replace(/\n/g, '<br>');
        const payload1 = {
          inputPrompt: this.llmExplainState.payload['inputPrompt'],
          response: res.final_thought,
          modelName: "gpt-4o"
        }
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyGotMetric = res;
        },
        error => {
          this.handleApiError(error, 'LLM Explain API', this.llmExplainState, 'llmExplain');
        });
      },
      error => {
        this.handleApiError(error, 'token Importance API', this.gotState, 'got');
      });
  }

  // LLM Explanation API
  llmExplanation() {
    if (this.ApiCallHappened.has('llmExplain')) {
      return;
    }
    this.llmExplainState.status = 'inPROCESS'
    this.ApiCallHappened.add('llmExplain');
    const payload = {
      inputPrompt: this.llmExplainState.payload['inputPrompt'],
      response: this.fmRes?.moderationResults?.responseModeration?.generatedText,
      modelName: "gpt-4o"
    }
    this.responseService.llmExplain(payload).subscribe((res: any) => {
      this.llmExplainResponse = res;
    },
    error => {
      this.handleApiError(error, 'LLM Explain API', this.llmExplainState, 'llmExplain');
    });
  }

}
