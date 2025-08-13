/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ChangeDetectionStrategy, Component, INJECTOR, Input, SimpleChanges } from '@angular/core';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ResponseComparisonService } from './response-comparison.service';
import { SharedDataService } from 'src/app/services/shared-data.service';
import { AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { Node, Edge } from '@swimlane/ngx-graph';
import { KeyValue } from '@angular/common';
import { urlList } from 'src/app/urlList';
import Chart from 'chart.js/auto';
import ChartAnnotation from 'chartjs-plugin-annotation';
Chart.register(ChartAnnotation);

@Component({
  selector: 'app-response-comparison',
  templateUrl: './response-comparison.component.html',
  styleUrls: ['./response-comparison.component.css'],

})
export class ResponseComparisonComponent {
  @Input() openAIRes: any;
  @Input() cotState: any;
  @Input() thotState: any;
  @Input() fmRes: any;
  @Input() nemoModerationRailRes: any;
  @Input() covState: any;
  @Input() prompt: any;
  @Input() tokenImpState: any;
  @Input() gotState: any;
  @Input() rereadState: any ={status: ''};
  @Input() lotState: any ={status: ''};
  @Input() logicOfThoughtsState: any ={status: ''};
  @Input() hallucinationSwitchCheck: boolean = false;
  @Input() hallucinateRetrievalKeplerRes: any;
 // @Input() RagMultiModalResponse: any;
  @Input() gEvalres: any;
  @Input() serperResponseState: any;
  @Input() selectedUseCaseName: any;
  @Input() llmExplainState: any;
  @Input() templateBasedPayload:any;
  @Input() submitFlag:any;
  @Input() selectedTranslate:any;
  @Input() UploadedFile:any;
  @Input() vectorId:any;
  @Input() fileupload: any;
  @Input() MMImageResponse:any;
  @Input() MMTimeTaken:any;
  @Input() faithfulnessScore: any;
  @Input() relevanceScore: any;
  @Input() adhernceScore: any;
  @Input() correctnessScore: any;
  @Input() averageScore: any;
  @Input() faithfulness: any;
  @Input() relevance: any;
  @Input() adhernce: any;
  @Input() correctness: any;
  @Input() isLoadingMMImage: boolean = false;
  @Input() MMImageTHOT: any;
  @Input() MMImageCOV: any;
  @Input() MMImageCOT: any;
  @Input() MMImageHallucinationScore: any;
  @Input() enableSearch: any;
  @Input() MMPdfReference: any;
  @Input() lightRag: any;
  imageFailedCases:any = {};
  covResponse: any = {}
  cotResponse: any = {}
  thotResponse: any = {}
  tokenImportanceResponse: any = {};
  activeTab = 'Faithfulness Check';
  apiEndpoints: any = {};
  ApiCallHappened = new Set<string>();
  isSerperSelected: any = false;
  responseSerper: any = {};
  responseSerperStatus = '';
  UncertaintyAIMetric:any;
  refLink: any = '';
  model_name = 'gpt4';
  templateBasedResponse: any = {}
  naviResponse: any = {};
  graphData: any = [];
  chart: any;
  apiResult: any = {};
  nodes: Node[] = [];
  links: Edge[] = [];
  isLoading: boolean = false;
  responseBlocked: boolean = false;
  openAIResTextFormatted: any = '';
  generatedTextFormatted = '';
  GOTExpanded = false;
  llmExplainResponse: any = {};
  isArrowDown: boolean = true;
  metrics = ['uncertainty', 'coherence'];
  UncertaintyGotMetric:any;
  UncertaintyCotMetric:any;
  selectCoveComplexity: any = 'simple';
  selectedLlmModel: any = 'gpt4';
  summary:boolean = true;
  GOTAnswer: string = '';
  MMImageUrl='';
  //MMImageResponse: any;
  // MMImageTHOT: any;
  // MMImageCOV: any;
  // MMImageCOT: any;
  // MMImageHallucinationScore: any;
  rereadResult:any;
  rereadExplanation:any;
  rereadTimeTaken:any;
  uncertaintyResult:any;
  rereadloading= false;
  rereadCalled = false;
  rereadResponse:any = {};
  // faithfulnessScore:any;
  // relevanceScore:any;
  // adhernceScore:any;
  // correctnessScore:any;
  // averageScore:any;
  // faithfulness:any;
  // relevance:any;
  // adhernce:any;
  // correctness:any;
  // isLoadingMMImage= false;
  MMVideoUrl='';
  MMVideoResponse: any;
  isLoadingMMVideo= false;
  firstClick= false;
  MMAudioUrl='';
  MMAudioResponse: any;
  isLoadingMMAudio= false;
  topTokens: any[] = [];
  tokens:any[] = [];
  isMultimodal = false;
  lotExplanation: any;
  lotPropositions: any;
  lotExpression: any;
  lotExtendExplanation: any;
  lotLaw: any;
  lotExtendInfo: any;
  lotTimeTaken: any;
  lotResponse:any = {};
  logicOfThoughtsResponse:any = {};
  chartInstance: Chart | null = null;
  myDistributionBarChart1Instance: Chart | null = null;
  tokenBarChartCreated: boolean = false;
frequencyChartCreated: boolean = false;

  constructor(private dialog: MatDialog, private responseService: ResponseComparisonService, public _snackBar: MatSnackBar, private https: HttpClient, private cdr: ChangeDetectorRef, private sharedDataService: SharedDataService) {
    this.sharedDataService.templateBasedResponses.subscribe(response => {
      this.templateBasedResponse = response
      console.log(this.templateBasedResponse,"templateBased Service Data")
    });
    this.sharedDataService.imageBasedFailedChecks.subscribe(response => {
      this.imageFailedCases = response
      console.log(this.imageFailedCases.modelBased,this.imageFailedCases.templateBased,"imageFailedCases Service Data")
    });
    this.sharedDataService.naviToneModerationRes.subscribe(response => {
      this.naviResponse = response
      console.log(this.naviResponse)
    });
  }
    isCollapsed = false;

    // Toggles the collapse state of the component
    toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
    }
    isTHOTCollapsed = false;

    // Toggles the collapse state of the THOT section
    toggleTHOTCollapse() {
        this.isTHOTCollapsed = !this.isTHOTCollapsed;
    }
    isCOTCollapsed = false;

    // Toggles the collapse state of the cOT section
    toggleCOTCollapse() {
        this.isCOTCollapsed = !this.isCOTCollapsed;
    }
    isRereadCollapsed = false;
    isLotCollapsed = false;

    // Toggles the collapse state of the Reread section
    toggleRereadCollapse() {
        this.isRereadCollapsed = !this.isRereadCollapsed;
    }

    // Toggles the collapse state of the LOT section
    toggleLotCollapse() {
        this.isLotCollapsed = !this.isLotCollapsed;
    }

    isGOTCollapsed = false;
    isTokenCollapsed = false;
// Toggles the collapse state of the GOT section
    toggleGOTCollapse() {
        this.isGOTCollapsed = !this.isGOTCollapsed;
    }

    ngAfterViewChecked(): void {
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

    // Toggles the collapse state of the Token section
    toggleTokenCollapse(): void {
      this.isTokenCollapsed = !this.isTokenCollapsed;
      this.tokenBarChartCreated = false;
      this.frequencyChartCreated = false;
    }
    isLogicOfThoughtsCollapsed = false;

    // Toggles the collapse state of the Logic of Thoughts section
    toggleLogicOfThoughtsCollapse() {
      this.isLogicOfThoughtsCollapsed = !this.isLogicOfThoughtsCollapsed;
  }

  // Initializes the component and sets up API calls
  ngOnInit(): void {
    let ip_port: any;
    ip_port = this.getLocalStoreApi();
    this.setApilist(ip_port);
    this.responseService.fetchApiUrl();
    this.model_name = this.serperResponseState.model;
    this.cdr.detectChanges();
    console.log("hallucinationSwitchCheck", this.hallucinationSwitchCheck)
    if (this.submitFlag && !this.hallucinationSwitchCheck) {
      this.covgetApi();
    }
    console.log("covState.payload", this.covState.payload)
    console.log("submitFlag",this.submitFlag)
    console.log("Cot State Payload", this.cotState.payload)
    //this.generatedTextFormatted = this.formatText(this.fmRes?.moderationResults?.responseModeration?.generatedText);
  //  this.RagMultiModalResponse.response.text = this.RagMultiModalResponse?.response?.text?.replace(/\n\n/g, '<br>');
    if (this.UploadedFile?.type?.startsWith('image/') || this.UploadedFile?.type?.startsWith('audio/') || this.UploadedFile?.type?.startsWith('video/') || this.UploadedFile?.type?.startsWith('application/')) {
      this.isMultimodal = true;
    }
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
    this.MMImageUrl = ip_port.result.Rag + ip_port.result.MMImageUrl;
    this.MMVideoUrl = ip_port.result.Rag + ip_port.result.MMVideoUrl;
    this.MMAudioUrl = ip_port.result.Rag + ip_port.result.MMAudioUrl;
  }

    // Formats text by replacing special characters with HTML tags
  formatText(text: any) {
    if (!text) {
      return '';
    }
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
  }

  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  // change the active tab
  changeTab = (tab: string) => {
    this.activeTab = tab;
  }

   // Checks if an object is empty
  isEmptyObject(obj: any) {
    if (obj == null || obj == undefined) {
      return true;
    }
    return Object.keys(obj).length === 0;
  }
  
  // Toggles the arrow state
  toggleArrow() {
    this.isArrowDown = !this.isArrowDown;
  }

  // Opens a source file in a new tab
  openSource(baseResUrl: any) {
    var binaryPdf = atob(baseResUrl);
    var blobPdf = new Blob([new Uint8Array(Array.from(binaryPdf).map(c => c.charCodeAt(0)))], { type: 'application/pdf' });
    var pdfUrl = URL.createObjectURL(blobPdf);
    window.open(pdfUrl, '_blank');
  }

  // Displays a snackbar with a message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // Checks if a value is a non-empty array
  isNonEmptyArray(value: any): boolean {
    return Array.isArray(value) && value.length > 0;
  }

  // Opens a right-side modal with the provided data
  openRightSideModal(data: any) {
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop'
    });
  }

   // Calls the COV API
  covgetApi() {
    if (this.ApiCallHappened.has('covgetApi')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-Cov-get-api-already-called");
      return;
    }
    this.covState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-covGet-API-CALL", this.covState);
    this.ApiCallHappened.add('covgetApi');
    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      console.log("HALLUCINATION COV")
      const payload = {
        "fileupload": this.fileupload,
        "text": this.prompt,
        "vectorestoreid": this.vectorId,
        "complexity": "simple"
      };
      apiObservable = this.responseService.hallucinateCOV(payload);
    } else {
      const payload1 = {
        "text": this.prompt,
        "complexity": this.selectCoveComplexity,
        "model_name": this.selectedLlmModel,
        "translate": this.selectedTranslate
      }
      apiObservable = this.responseService.covgetApi(payload1);
    }

    apiObservable.subscribe(
      (res: any) => {
        console.log(res)
        if (this.hallucinationSwitchCheck) {
          this.covResponse.baseline = res.cov_response.baseline_response.replace(/\n/g, '<br>');
          this.covResponse.verification = res.cov_response.verification_answers.replace(/\n/g, '<br>');
          this.covResponse.final = res.cov_response.final_answer.replace(/\n/g, '<br>');
        } else {
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
          this.generatedTextFormatted= res.final_answer.replace(/\n/g, '<br>');
        }
        this.covResponse.timetaken = res.timetaken;
      },
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-COV-API", error);
        this.covState.status = 'FAILED'
        this.ApiCallHappened.delete('covgetApi');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in COV API";
        }
        this.openSnackBar(message, "Close")
      }
    );
  }

  // Calls the COT API
  callCOT() {
    this.cotState.payload={
      temperature: '0',
      Prompt: this.prompt,
      model_name: this.selectedLlmModel
    }
    if (this.ApiCallHappened.has('openAicotgetApi')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-openAicotgetApi-already-called");
      return;
    }
    this.cdr.detectChanges();

    this.cotState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-openAicotgetApi-CALL", this.cotState);
    this.ApiCallHappened.add('openAicotgetApi');

    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      const payload = {
        "fileupload": this.fileupload,
        "text": this.prompt,
        "vectorestoreid": this.vectorId
      };
      apiObservable = this.responseService.hallucinateCOT(payload);
    } else {
      apiObservable = this.responseService.openAicotgetApi(this.cotState.payload);
    }

    apiObservable.subscribe(
      (res: any) => {
        if (this.hallucinationSwitchCheck) {
          this.cotResponse.text = res.cot_response.replace(/\n/g, '<br>').split('Source:')[0];
          this.cotResponse.sourceText = res['source-name'];
          this.cotResponse.token_cost = res['token_cost'];
          const payload1 = {
            "inputPrompt": this.llmExplainState.payload['inputPrompt'],
            "response": this.cotResponse.text,
            "modelName": "gpt-4o"
          };
          console.log("payload1:", payload1);
          this.responseService.llmExplain(payload1).subscribe((res: any) => {
            this.UncertaintyCotMetric = res;
          });
        } else {
          this.cotResponse.text = res.text.replace(/\n/g, '<br>');
          const payload1 = {
            "inputPrompt": this.llmExplainState.payload['inputPrompt'],
            "response": this.cotResponse.text,
            "modelName": "gpt-4o"
          }
          console.log("payload1:", payload1)
          this.responseService.llmExplain(payload1).subscribe((res: any) => {
            this.UncertaintyCotMetric = res;
          },
            error => {
              console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-llmExplain", error);
              this.llmExplainState.status = 'FAILED'
              this.ApiCallHappened.delete('llmExplain');
              let message
              if (error.status === 500) {
                message = "Internal Server Error. Please try again later.";
              } else {
                message = error.error.detail || error.error.message || "Error in LLM Explain   API";
              }
              this.openSnackBar(message, "Close")
            })
        }
        this.cotResponse.timetaken = res.timetaken;
        console.log(this.cotResponse)
      }
      ,
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-openAicotgetApi", error);
        this.cotState.status = 'FAILED'
        this.ApiCallHappened.delete('openAicotgetApi');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in openAicotgetApi";
        }
        this.openSnackBar(message, "Close")
      }
    );
  }

  // // Calls the LOT API
  callLOT(){
    if (this.ApiCallHappened.has('logicOfThoughts')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-logicOfThoughts-already-called");
      return;
    }
    this.logicOfThoughtsState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-logicOfThoughts-CALL", this.logicOfThoughtsState);
    this.ApiCallHappened.add('logicOfThoughts');
  
      const payload ={
        "fileupload": this.fileupload,
        "text": this.prompt,
        "vectorestoreid": this.vectorId
      }
      this.responseService.lot(payload)
      .subscribe((res:any) => {
        console.log("lotres", res)
        this.logicOfThoughtsResponse.text = res.lot_response.replace(/\n/g, '<br>').split('Source:')[0];
        this.logicOfThoughtsResponse.source_name = res['source-name'];
        this.logicOfThoughtsResponse.timetaken = res.timetaken;
        this.logicOfThoughtsResponse.token_cost = res.token_cost;
      },
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-logicOfThoughts", error);
        this.logicOfThoughtsState.status = 'FAILED'
        this.ApiCallHappened.delete('logicOfThoughts');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in logicOfThoughts API";
        }
        this.openSnackBar(message, "Close")
      })
    }  

    // // Calls the THOT API
  callTHOT() {
    this.thotState.payload={
      temperature: '0',
      Prompt: this.prompt,
      model_name: this.selectedLlmModel
    }
    if (this.ApiCallHappened.has('openAiTHOTApi')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-openAiTHOTApi-already-called");
      return;
    }
    this.thotState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-openAiTHOTApi-CALL", this.thotState);
    this.ApiCallHappened.add('openAiTHOTApi');

    let apiObservable;
    if (this.hallucinationSwitchCheck) {
      console.log("hallucinateThotCalled")
      const payload = {
        "fileupload": this.fileupload,
        "text": this.prompt,
        "vectorestoreid": this.vectorId
      };
      apiObservable = this.responseService.hallucinateThot(payload);
    } else {
      apiObservable = this.responseService.openAiTHOTApi(this.thotState.payload);
    }

    apiObservable.subscribe(
      (res: any) => {
        if (this.hallucinationSwitchCheck) {
          this.thotResponse.thot_response = res.thot_response.replace(/\n/g, '<br>').split('Source:')[0];
          this.thotResponse.sourceText = res['source-name']
          this.thotResponse.token_cost = res['token_cost']
          const payload1 = {
            "inputPrompt": this.llmExplainState.payload['inputPrompt'],
            "response": this.thotResponse.thot_response,
            "modelName": "gpt-4o"
          };
          console.log("payload1:", payload1);
          this.responseService.llmExplain(payload1).subscribe((res: any) => {
            this.UncertaintyAIMetric = res;
          });
        } else {
          //this.thotResponse.thot_response = res.text.replace(/\n/g, '<br>');
            let formattedText = res.text
            .replace(/Result:/g, '<br>')
            .replace(/Explanation:/g, '<br>')
            .replace(/\n\n/g, '<br>')
            .replace(/\n/g, '<br>');
            this.thotResponse.thot_response = formattedText;

            const lines = res?.text?.split('\n');
            const resultLine = lines.find((line: any) => line.startsWith('Result:'));
            const explanationLine = lines.find((line: any) => line.startsWith('Explanation:'));

            console.log("Lines::",formattedText)
          
            let resultValue = '';
            let explanationValue = '';
          
            // if (resultLine) {
            //   resultValue = resultLine.split('Result:')[1]?.replace(/"/g, ''); // Remove the surrounding quotes
            // }      
            // if (explanationLine) {
            //   explanationValue = explanationLine.split('Explanation:')[1]?.replace(/"/g, ''); // Remove the surrounding quotes
            // }
            // if (resultLine) {
            //   resultValue = resultLine.split('Result:')[1] // Trim leading and trailing whitespace
            //   const nextNewLineIndex = resultValue.indexOf('\n');
            //   if (nextNewLineIndex !== -1) {
            //     resultValue = resultValue.substring(0, nextNewLineIndex).trim();
            //   }
            // }
            
            // if (explanationLine) {
            //   explanationValue = explanationLine.split('Explanation:')[1]?.trim(); // Trim leading and trailing whitespace
            //   const nextNewLineIndex = explanationValue.indexOf('\n');
            //   if (nextNewLineIndex !== -1) {
            //     explanationValue = explanationValue.substring(0, nextNewLineIndex);
            //   }
            // }
            // if(!resultLine || !explanationLine){
            //   this.thotResponse.thot_response = formattedText;
            // } else {        
            // this.thotResponse.thot_response = `${resultValue}<br>${explanationValue}`;
            // }
            
            const payload1 = {
              "inputPrompt": this.llmExplainState.payload['inputPrompt'],
              "response": this.thotResponse.thot_response,
              "modelName": "gpt-4o"
            }
            console.log("payload1:", payload1)
            this.responseService.llmExplain(payload1).subscribe((res: any) => {
              this.UncertaintyAIMetric = res;
            },
              error => {
                console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-llmExplain", error);
                this.llmExplainState.status = 'FAILED'
                this.ApiCallHappened.delete('llmExplain');
                let message
                if (error.status === 500) {
                  message = "Internal Server Error. Please try again later.";
                } else {
                  message = error.error.detail || error.error.message || "Error in LLM Explain   API";
                }
                this.openSnackBar(message, "Close")
              })
        }
        this.thotResponse.timetaken = res.timetaken;
      },
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-openAiTHOTApi", error);
        this.thotState.status = 'FAILED'
        this.ApiCallHappened.delete('openAiTHOTApi');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in Open Ai THOT Api";
        }
        this.openSnackBar(message, "Close")
      }
    );

  }

  // Creates a bar chart for token importance
  createTokenBarChart(): void {
    if (!this.tokens || this.tokens.length === 0) {
      console.log("No tokens available to create the chart.");
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
  
    console.log("Creating token bar chart with tokens:", this.tokens);
  
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
              generateLabels: function(chart) {
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
//   createFrequencyBarChart(): void {
//     if (!this.tokens || this.tokens.length === 0) {
//         console.log("No tokens available to create the chart.");
//         return;
//     }

//     const ctx = document.getElementById('myFrequencyBarChart1') as HTMLCanvasElement;
//     if (!ctx) {
//         console.error("Canvas element not found.");
//         return;
//     }

//     console.log("Creating frequency bar chart with tokens:", this.tokens);

//     // Calculate frequency of each importance_value
//     const frequencyMap: { [key: string]: number } = this.tokens.reduce((acc: { [key: string]: number }, token: any) => {
//         const value = token.importance_value.toFixed(2); // Round to 2 decimal places for grouping
//         acc[value] = (acc[value] || 0) + 1;
//         return acc;
//     }, {});

//     const labels = Object.keys(frequencyMap);
//     const data = Object.values(frequencyMap) as number[];
//     const maxFrequency = Math.max(...data);

//     new Chart(ctx, {
//         type: 'bar',
//         data: {
//             labels: labels,
//             datasets: [
//                 {
//                     label: 'Frequency of Importance Values',
//                     data: data,
//                     backgroundColor: '#1f77b4',
//                     borderColor: '#1f77b4',
//                     borderWidth: 1,
//                     order: 2
//                 },
//                 {
//                     label: 'Frequency Line',
//                     data: data,
//                     type: 'line',
//                     borderColor: 'red',
//                     borderWidth: 2,
//                     fill: false,
//                     pointRadius: 0,
//                     tension: 0.4,
//                     order: 1
//                 }
//             ]
//         },
//         options: {
//             plugins: {
//               legend: {
//                   display: false 
//               }
//             },
//             scales: {
//                 x: {
//                     grid: {
//                         display: false
//                     },
//                     title: {
//                         display: true,
//                         text: 'Importance Value'
//                     }
//                 },
//                 y: {
//                     beginAtZero: true,
//                     min: 0,
//                     max: maxFrequency > 4 ? maxFrequency : 4,
//                     title: {
//                         display: true,
//                         text: 'Frequency'
//                     },
//                     ticks: {
//                         stepSize: 1 
//                     }
//                 }
//             }
//         }
//     });
// }

// Creates a frequency distribution chart for tokens
frequencyDistributionChart(): void {
  if (!this.tokens || this.tokens.length === 0) {
      console.log("No tokens available to create the chart.");
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

  console.log("Creating frequency distribution chart with tokens:", this.tokens);

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
              generateLabels: function(chart) {
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
      (console.log('topTokens:', this.topTokens));
}

// Calls the token importance API
  tokenImportance() {
    if (this.ApiCallHappened.has('tokenImportance')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-tokenImportance-already-called");
      return;
    }
    this.tokenImpState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-tokenImportance-CALL", this.tokenImpState);
    this.ApiCallHappened.add('tokenImportance');

    this.responseService.tokenImportance(this.tokenImpState.payload).subscribe(
      (res: any) => {
        this.tokenImportanceResponse = res;
        this.tokens = res?.token_importance_mapping;
        console.log("Tokens populated:", this.tokens);
        
        this.updatetopTokens();
        console.log("Top tokens updated:", this.topTokens);
        
        this.createTokenBarChart();
        console.log("Token bar chart created");
        
        // this.createFrequencyBarChart();
        this.frequencyDistributionChart();
        console.log("Frequency distribution chart created");
      },
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-tokenImportance", error);
        this.tokenImpState.status = 'FAILED'
        this.ApiCallHappened.delete('tokenImportance');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in token Importance API";
        }
        this.openSnackBar(message, "Close")
      }
    );
  }

   // Toggles the search option
  toggleSearch(event: any) {
    this.isSerperSelected = event.target.checked;
    console.log("search:::", this.isSerperSelected);
    if (this.isSerperSelected) {
      this.responseSerper = {};
      // this.refLink ='';
      // call llm-explain api
      this.serperResponseState.payload['llm_response'] = this.fmRes?.moderationResults?.responseModeration?.generatedText;
      this.responseService.serperResponse(this.serperResponseState.payload).subscribe((res: any) => {
        this.responseSerper = res.metrics[0];
        this.generatedTextFormatted=res.internetResponse[0];
        // this.refLink = res.referenxceLink;
      }, (error) => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-serperResponse", error);
        this.responseSerperStatus = 'FAILED'
      }
      )
    }
    else{
      this.generatedTextFormatted=this.formatText(this.fmRes?.moderationResults?.responseModeration?.generatedText);
    }
  }

  // Calls the reread API
  reread(){
    if (this.ApiCallHappened.has('reread')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-reread-already-called");
      return;
    }
    this.rereadState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-reread-CALL", this.rereadState);
    this.ApiCallHappened.add('reread');
    
    const payload1 = {
      "inputPrompt": this.prompt,
      "modelName": 'GPT4'
    }
    this.responseService.reread(payload1)
      .subscribe((response: any) => {
       console.log("reread successful");
       this.rereadResponse.rereadResult= response.response.result.replace(/\n/g, '<br>');;
       this.rereadResponse.rereadExplanation= response.response.explanation.replace(/\n/g, '<br>');
       this.rereadResponse.rereadTimeTaken= response.time_taken;
       const payload2 = {
        "inputPrompt": this.llmExplainState.payload['inputPrompt'],
        "response": this.rereadResult + ' ' + this.rereadExplanation,
        "modelName": "gpt-4o"
      };
    this.responseService.llmExplain( payload2)
      .subscribe((response: any) => {
       console.log("reread successful");
       this.uncertaintyResult=response;
      }, error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-llmExplain", error);
        this.llmExplainState.status = 'FAILED'
        this.ApiCallHappened.delete('llmExplain');
          let message
          if (error.status === 500) {
            message = "Internal Server Error. Please try again later.";
          } else {
            message = error.error.detail || error.error.message || "Error in LLM Explain API";
          }
          this.openSnackBar(message, "Close")
      });
      }, error => {
        console.error('Error in reread API call', error);
        this.rereadState.status = 'FAILED'
        this.ApiCallHappened.delete('reread');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in  Reread API";
        }
        this.openSnackBar(message, "Close")
      });  
  }

   // Calls the logic of thoughts API
  logicOfThoughts() {
    if (this.ApiCallHappened.has('lot')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-lot-already-called");
      return;
    }
    this.lotState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-reread-CALL", this.lotState);
    this.ApiCallHappened.add('lot');

    const payload = {
       "inputPrompt": this.prompt,
       "llmResponse":null,
       "modelName": 'GPT4'
    };
    this.responseService.logicOfThoughts(payload)
    .subscribe((response: any) => {  
      console.log('API response:', response);
      this.lotResponse.lotExplanation = response.response.Explanation;
      this.lotResponse.lotPropositions = response.response.Propositions;
      this.lotResponse.lotExpression = response.response['Logical Expression'];
      this.lotResponse.lotExtendExplanation = response.response['Extended Logical Expression'];
      this.lotResponse.lotLaw = response.response['Law used to extend the logical expression'];
      this.lotResponse.lotExtendInfo = response.response['Extended Logical Information'];
      this.lotResponse.lotTimeTaken = response.time_taken;
      },
        error => {
          console.error('Error in lot API call', error);
        this.lotState.status = 'FAILED'
        this.ApiCallHappened.delete('lot');
          let message
          if (error.status === 500) {
            message = "Internal Server Error. Please try again later.";
          } else {
            message = error.error.detail || error.error.message || "Error in  LogicOfThoughts API";
          }
          this.openSnackBar(message, "Close")
        });
    }

     // Calls the logic GOT API
  getGOT() {
    if (this.ApiCallHappened.has('got')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-got-already-called");
      return;
    }
    this.gotState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-got-CALL", this.gotState);
    this.ApiCallHappened.add('got');
    this.responseService.gotResponse(this.gotState.payload).subscribe(
      (res: any) => {
        this.apiResult = res;
        this.GOTAnswer = res.final_thought.replace(/\n/g, '<br>');
        //this.updateGraph();
        const payload1 = {
          "inputPrompt": this.llmExplainState.payload['inputPrompt'],
          "response": res.final_thought,
          "modelName": "gpt-4o"
        }
        console.log("payload1:", payload1)
        this.responseService.llmExplain(payload1).subscribe((res: any) => {
          this.UncertaintyGotMetric = res;
        },
          error => {
            console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-llmExplain", error);
            this.llmExplainState.status = 'FAILED'
            this.ApiCallHappened.delete('llmExplain');
            let message
            if (error.status === 500) {
              message = "Internal Server Error. Please try again later.";
            } else {
              message = error.error.detail || error.error.message || "Error in LLM Explain   API";
            }
            this.openSnackBar(message, "Close")
          })
      },
      error => {
        console.error('Error in getGOT API call', error);
        this.gotState.status = 'FAILED'
        this.ApiCallHappened.delete('got');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in token Importance API";
        }
        this.openSnackBar(message, "Close")
      }
    );
  }

  // Updates the graph with API results
  updateGraph() {
    console.log('updateGraph called');
    this.nodes = [];
    this.links = [];
    console.log('apiResult.graph:', this.apiResult.graph);
    this.apiResult.graph.forEach((graph: any, index: number) => {
      if (graph.operation) {
        const operationId = `operation${index}`;
        this.nodes.push({ id: operationId, label: `Operation: ${graph.operation}`, data: { color: '#ffbbff' } });

        console.log('operation:', graph.operation);

        graph.thoughts.forEach((thought: any, thoughtIndex: number) => {
          if (thought.current) {
            const thoughtId = `${operationId}thought${thoughtIndex}`;
            const thoughtLabel = `${thought.current}, Score: ${thought.score}`;
            this.nodes.push({ id: thoughtId, label: thoughtLabel });
            this.links.push({ id: `link${operationId}${thoughtId}`, source: operationId, target: thoughtId, label: 'Thought' });

            console.log('thought:', thoughtLabel);
          }
        });
      }
    });
    this.isLoading = false;
    console.log('nodes:', this.nodes);
    console.log('links:', this.links);
    this.cdr.detectChanges();
  }

  // Calls the LLM explanation API
  llmExplanation() {
    if (this.ApiCallHappened.has('llmExplain')) {
      console.log("--RESPONSIBLE-COMPARISON-|||-llmExplain-already-called");
      return;
    }
    this.llmExplainState.status = 'inPROCESS'
    console.log("--RESPONSIBLE-COMPARISON-|||-llmExplain-CALL", this.llmExplainState);
    this.ApiCallHappened.add('llmExplain');
    const payload = {
      "inputPrompt": this.llmExplainState.payload['inputPrompt'],
      "response": this.fmRes?.moderationResults?.responseModeration?.generatedText,
      "modelName": "gpt-4o"
    }
    console.log("payload:", payload)
    this.responseService.llmExplain(payload).subscribe((res: any) => {
      this.llmExplainResponse = res;
      //this.UncertaintyAIMetric = res;
    },
      error => {
        console.log("--RESPONSIBLE-COMPARISON-|||-Error-in-llmExplain", error);
        this.llmExplainState.status = 'FAILED'
        this.ApiCallHappened.delete('llmExplain');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in LLM Explain   API";
        }
        this.openSnackBar(message, "Close")
      })
  }

  // Returns the LLM explanation response as an array
  get llmExplainResponseArray(): Array<KeyValue<string, any>> {
    return Object.entries(this.llmExplainResponse).map(([key, value]) => ({ key, value }));
  }

ngOnChanges(changes: SimpleChanges) {
  console.log('cotCheck')
  if (changes['cotState']) {
    console.log('cotState changed:', this.cotState);

  }
}

}


