/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input, ViewEncapsulation } from '@angular/core';
import { TemplateBasedGuardrailService } from './template-based-guardrail.service';
import { SharedDataService } from 'src/app/services/shared-data.service';
import { RightSidePopupComponent } from '../../right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { FmModerationService } from 'src/app/services/fm-moderation.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-template-based-guardrail',
  templateUrl: './template-based-guardrail.component.html',
  styleUrls: ['./template-based-guardrail.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class TemplateBasedGuardrailComponent {
  @Input() llmEvalPayload: any;
  @Input() requestModerationTemplates: any;
  @Input() contentDetectorState: any;
  @Input() requestTime: any;
  @Input() templateBasedPayload: any;
  @Input() imagePromptInjection: any;
  @Input() imageJailbreak: any; 
  @Input() imageRestrictedTopic: any;
  @Input() fairness_response: any;
  @Input() coupledModeration: any;
  textareaContext = '';
  textareaContextCon = '';
  textareaContextConciseCon = '';
  textareaContextRer = '';
  textareaRerankingContext = '';
  contentDetectorRes: any = {}
  ApiCallHappened = new Set<string>();
  requestModerationResult: any = {};

  constructor(public snackBar: MatSnackBar, private templateBasedService: TemplateBasedGuardrailService, public fmService: FmModerationService, private sharedDataService: SharedDataService, private dialog: MatDialog) { }
  
  // Initializes the component and subscribes to data updates
  ngOnInit() {
    this.templateBasedService.fetchApiUrl()
    this.fmService.currentData.subscribe(data => {
      if (data) {
        this.requestModerationResult = data.moderationResults.requestModeration
      } else {
        console.log("No data")
      }
    });
    if (this.llmEvalPayload.Prompt !== '' && this.llmEvalPayload.Prompt !== undefined && this.llmEvalPayload.Prompt !== null && this.coupledModeration==true) {
      this.callBatch();
    }
  }
  response: any = {}
  status: any = {}


  counter = 0;
  i = 0;

  // Processes moderation templates in batches
  async callBatch() {
    // let requestModerationResultTemp = data.moderationResults.requestModeration
        // console.log(requestModerationResultTemp,"---------------+++++++++++++++++")
    this.requestModerationTemplates.forEach((element: any) => {
      this.status[element] = '';
      this.response[element] = {};
    });
    // this.requestModerationResult = requestModerationResultTemp;
    console.log(this.status,this.response,this.requestModerationTemplates)
    const batchSize = 3; // Maximum number of concurrent requests
    for (let i = 0; i < this.requestModerationTemplates.length; i += batchSize) {
      const batchPromises = [];
      for (let j = i; j < i + batchSize && j < this.requestModerationTemplates.length; j++) {
        // Call the function and push its promise into the batchPromises array
        const templatesToIgnore = ['CONTEXT_RELEVANCE', 'CONTEXT_CONCISENESS', 'CONTEXT_RERANKING'];
        if (!templatesToIgnore.includes(this.requestModerationTemplates[j])){
          batchPromises.push(this.callEvalLLM(this.requestModerationTemplates[j]));
        }
      }
      // Wait for all promises in the batch to be resolved before moving to the next batch
      await Promise.all(batchPromises).then(results => {
        // Handle results if needed
        console.log('Batch completed', results);
      }).catch(error => {
        // Handle error
        console.error('Error in batch');
      });
    }
    console.log('All requests processed');
    // while (this.counter != 3 && this.i < this.requestModerationTemplates.length) {
    //   console.log("Counter: ", this.counter);
    //   console.log("i: ", this.i);
    //   console.log("Template: ", this.requestModerationTemplates[this.i]);
    //   this.counter++;
    //   this.callEvalLLM(this.requestModerationTemplates[this.i]);
    //   this.i += 1;
    //   // 
    // }
    // for(let i=0; i<this.requestModerationTemplates.length; i++){
    //   this.callEvalLLM(this.requestModerationTemplates[i]);
    // }
    // this.callEvalLLM("Prompt Injection Check")
    // this.callEvalLLM("Jailbreak Check")
    // this.callEvalLLM("VALID_PROMPT")
  }

  // Calculates the total time taken for moderation checks
  getTotalTime(): string {
    let smoothLlmCheckTime = parseFloat(this.requestTime.smoothLlmCheck);
    let bergeronCheckTime = parseFloat(this.requestTime.bergeronCheck);
    let totalTime = smoothLlmCheckTime + bergeronCheckTime;
    return totalTime + 's';
  }

  // Checks if an object is empty
  isEmptyObject(obj: any): boolean {
    return obj != null && typeof obj === 'object' && Object.keys(obj).length === 0;
  }

  templateOptions = [
    { title: 'PROMPT INJECTION', value: 'Prompt Injection Check', parentId: 'accordianPI', dataTarget: 'collapsePI' },
    { title: 'Jailbreak Check', value: 'Jailbreak Check', parentId: 'accordianJB', dataTarget: 'collapseJB' },
    { title: 'FAIRNESS AND BIAS', value: 'Fairness and Bias Check', parentId: 'accordianFB', dataTarget: 'collapseFB' },
    { title: 'LANGUAGE CRITIQUE COHERENCE', value: 'LANGUAGE_CRITIQUE_COHERENCE', parentId: 'accordianLCC', dataTarget: 'collapseLCC' },
    { title: 'LANGUAGE CRITIQUE FLUENCY', value: 'LANGUAGE_CRITIQUE_FLUENCY', parentId: 'accordianLCF', dataTarget: 'collapseLCF' },
    { title: 'LANGUAGE CRITIQUE GRAMMAR', value: 'LANGUAGE_CRITIQUE_GRAMMAR', parentId: 'accordianLCG', dataTarget: 'collapseLCG' },
    { title: 'LANGUAGE CRITIQUE POLITENESS', value: 'LANGUAGE_CRITIQUE_POLITENESS', parentId: 'accordianLCP', dataTarget: 'collapseLCP' },
  ]

 // Opens a right-side modal with the provided data
  openRightSideModal(data: any) {
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      // height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      // position: {
      //   top: '57px', // Position the modal below the navbar
      //   right: '0'
      // },
      data: data,
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      // this.getAllBatches()
      console.log("POPUP CLOSE")
    });
  }

  // Calls the LLM evaluation API for a specific template
  callEvalLLM(templateName: any, Context?: any, ConciseContext?: any, RerankedContext?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const templatesToIgnore = ['CONTEXT_RELEVANCE', 'CONTEXT_CONCISENESS', 'CONTEXT_RERANKING'];
      if (this.status[templateName] === 'loading' || this.status[templateName] === 'done') {
        if ((templatesToIgnore.includes(templateName) && this.status[templateName] === 'done')) {
          this.response[templateName] = {}
          resolve(this.response[templateName]); 
        } else {
          reject(new Error('Template is either loading or already done.'));
          return;
        }
      }
      this.status[templateName] = 'loading';
      console.log(this.templateBasedPayload,"TEMPLATE BASED PAYLOAD")
      let payload = {
        Prompt: this.llmEvalPayload.Prompt,
        template_name: templateName,
        model_name: this.llmEvalPayload.model_name,
        AccountName: this.templateBasedPayload?.AccountName ? this.templateBasedPayload?.AccountName : "None",
        "PortfolioName": this.templateBasedPayload?.PortfolioName ? this.templateBasedPayload?.PortfolioName : "None",
        "userid": this.templateBasedPayload?.userid,
        "lotNumber": 1,
       // "Context": Context ? Context : "None",
       // "Concise_Context": ConciseContext ? ConciseContext : "None",
       // "Reranked_Context": RerankedContext ? RerankedContext : "None",
        "temperature": this.llmEvalPayload.temperature,
        "PromptTemplate": this.llmEvalPayload.PromptTemplate,
      };
      this.templateBasedService.evalLLM(payload).subscribe(
        (res: any) => {
          console.log(res,"RESPONSE FROM EVAL LLM")  
          if(typeof res?.['moderationResults'] != 'object'){
            this.status[templateName] = 'failed';
            reject("Error in response from evalLLM");
            return 
          }
          this.response[templateName] = res?.['moderationResults'];
          this.response[templateName]['description'] = res?.['description'];
          this.response[templateName]['timetaken'] = res?.['timeTaken'];
          console.log(this.response[templateName]);
          this.status[templateName] = 'done';
          let data = {
            'analysis': this.response[templateName].analysis,
            'result': this.response[templateName].result,
          };
          let templateToIgnore = ['Language Critique Coherence Check', 'Language Critique Fluency Check', 'Language Critique Grammar Check','Language Critique Politeness Check'];
          if (data.result === 'FAILED' && !templateToIgnore.includes(templateName)){ 
            this.sharedDataService.updateResponses(templateName, data);
          }
          console.log(this.response);
          this.counter--;
          resolve(data); // Resolve with the data on success
        },
        error => {
          this.status[templateName] = 'failed';
          reject(error); // Reject with the error
          this.snackBar.open('Moderation Request Failed', 'Close', {
            duration: 8000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        }
      );
    });
  }

  // Calls the content detector API
  callContentDetector() {
    if (this.ApiCallHappened.has('contentDetector')) {
      console.log("--REQUEST-MODERATION-|||-contentDetector-already-called");
      return;
    }
    this.contentDetectorState.status = 'inPROCESS'
    console.log("--REQUEST-MODERATION-|||-contentDetector-CALL", this.contentDetectorState);
    this.ApiCallHappened.add('contentDetector');
    const body = {
      text: this.contentDetectorState.prompt
    }
    console.log(body)
    this.templateBasedService.contentDetector(body).subscribe(
      (res: any) => {
        this.contentDetectorRes = res;
      },
      error => {
        console.log("--REQUEST-MODERATION-|||-Error-in-contentDetector", error);
        this.contentDetectorState.status = 'FAILED'
        this.ApiCallHappened.delete('contentDetector');
        let message
        if (error.status === 500) {
          message = "Internal Server Error. Please try again later.";
        } else {
          message = error.error.detail || error.error.message || "Error in Content Detector API";
        }
      }
    );
  }

  // Show Hide Analysis
  showFullAnalysis: { [key: string]: boolean } = {
  };

  // Toggles the visibility of the full analysis for a template
  toggleAnalysis(template: string): void {
    this.showFullAnalysis[template] = !this.showFullAnalysis[template];
  }
}
