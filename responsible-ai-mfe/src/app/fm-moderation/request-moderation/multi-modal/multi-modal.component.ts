/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit } from '@angular/core';
import { TemplateBasedGuardrailService } from '../template-based-guardrail/template-based-guardrail.service';
import { FmModerationService } from 'src/app/services/fm-moderation.service';
import { SharedDataService } from 'src/app/services/shared-data.service';

@Component({
  selector: 'app-multi-modal',
  templateUrl: './multi-modal.component.html',
  styleUrls: ['./multi-modal.component.css']
})
export class MultiModalComponent implements OnInit {
  response: any = {}
  status: any = {}

  templateList = ['Image Prompt Injection Check', 'Image Jailbreak Check', 'Image Toxicity Check', 'Image Profanity Check', 'Image Restricted Topic Check']
  // templateList:any = [] to be used for dynamic template list

  constructor(private templateBasedService: TemplateBasedGuardrailService, public fmService: FmModerationService, private sharedDataService: SharedDataService) { }
  ngOnInit() {
    this.templateBasedService.fetchApiUrl()
    // this.templateList = this.fmService.getMultiModal().templateList // to be used for dynamic template list
    this.callBatch();
  }
  async callBatch() {
    console.log('Multi Modal Triggered');
    this.templateList.forEach((element: any) => {
      this.status[element] = '';
      this.response[element] = {};
    });
    const batchSize = 3;
    for (let i = 0; i < this.templateList.length; i += batchSize) {
      console.log('Batch started');
      const batchPromises = [];
      for (let j = i; j < i + batchSize && j < this.templateList.length; j++) {
        console.log('Processing', this.templateList[j]);
        batchPromises.push(this.callMultiModal(this.templateList[j]));
      }
      await Promise.all(batchPromises).then(results => {
        console.log('Batch completed', results);
      }).catch(error => {
        console.error('Error in batch');
      });
    }
    console.log('All requests processed');
  }

  // Function to check if an object is empty
  isEmptyObject(obj: any): boolean {
    return obj != null && typeof obj === 'object' && Object.keys(obj).length === 0;
  }

// Function to call the multi-modal API
  callMultiModal(templateName: any, Context?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (this.status[templateName] === 'loading' || this.status[templateName] === 'done') {
        if ((templateName == 'RESPONSE_COMPLETENESS_WRT_CONTEXT' && this.status[templateName] === 'done')) {
          this.response[templateName] = {}
        } else {
          reject('Operation already in progress or completed');
          return;
        }
      }
      this.status[templateName] = 'loading';
      const formPayload = new FormData();
      formPayload.append('AccountName', 'None');
      formPayload.append('PortfolioName', 'None');
      formPayload.append('userid', this.fmService.getMultiModal().userId);
      formPayload.append('lotNumber', '1');
      formPayload.append('Prompt', this.fmService.getMultiModal().prompt);
      formPayload.append('Image', this.fmService.getMultiModal().file);
      formPayload.append('TemplateName', templateName);
      formPayload.append('Restrictedtopics', "Terrorism,Explosives");
      formPayload.append('model_name', "gpt4O");
      console.log(formPayload, "MultiModal Payload")
      this.templateBasedService.multiModal(formPayload).subscribe(
        (res: any) => {
          console.log(res,"RESPONSE FROM MULTIMODAL");

          if(typeof res?.['moderationResults'] != 'object'){
            this.status[templateName] = 'failed';
            reject("Error in response from multiModal");
            return 
          }
          this.response[templateName] = res?.['moderationResults'];
          this.response[templateName]['description'] = res?.['description'];
          this.response[templateName]['timetaken'] = res?.['timeTaken'];
          // this.response[templateName]['description'] = res?.['description'];
          let data = {
            'analysis': this.response[templateName].explanation,
            'result': this.response[templateName].result,
          };
          if (data.result === 'FAILED'){
            this.sharedDataService.updateImageBasedModels(templateName,data,'templateBased')
          }
          this.status[templateName] = 'done';
          console.log(this.response);
          resolve(data); // Resolve the promise with the data
        },
        error => {
          this.status[templateName] = 'failed';
          reject(error); // Reject the promise with the error
        }
      );
    });
  }

  // Collapse and expand 
  showFullAnalysis: { [key: string]: boolean } = {
    fairness: false,
  };

  toggleAnalysis(template: string): void {
    this.showFullAnalysis[template] = !this.showFullAnalysis[template];
  }

}
