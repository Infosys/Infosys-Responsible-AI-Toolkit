/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NGXLogger } from "ngx-logger";

@Component({
  selector: 'app-ai-content-detector',
  templateUrl: './ai-content-detector.component.html',
  styleUrls: ['./ai-content-detector.component.css']
})
export class AiContentDetectorComponent implements OnInit {
  // FOR SHIMMER
  isLoadingPrompt = true;
  ////
  flag:boolean=false;
  Prompt='';
  Prompt1='Artificial intelligence (AI) is revolutionizing our world. It empowers machines to mimic human intelligence, enabling them to learn, reason, and solve problems. From facial recognition in smartphones to chatbots answering your questions, AI is woven into daily life. AI is transforming industries like healthcare, finance, and transportation. It analyzes vast datasets to uncover patterns and predict trends, leading to improved decision-making.';
  Prompt2='Life can be seen as an unending journey, like the sun that arches daily from dawn to dusk. This constant movement represents lifelong learning, a ceaseless quest for growth and understanding. Think of a tree. It begins as a tiny seed and grows into a mighty entity, experiencing the cycle of seasons. We should continually learn and adapt to the worlds rhythm like a tree.';
  textLength:number=0;
  showSpinner1: any;
  textDetector='';
  ip_port:any;
  response:any;
  responseLoading = false;
  loadComplete = false;
  isAIChecked: boolean = false;
  isHumanChecked: boolean = false;

  constructor(private cdr: ChangeDetectorRef, private logger: NGXLogger, public https: HttpClient, private _snackBar: MatSnackBar) { }

   // Initializes the component and sets up the API endpoint
  ngOnInit(): void {
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        this.ip_port = JSON.parse(x)
      }
    }
    // set tieout for isLoadingPrompt

    this.isLoadingPrompt = false;
    this.textDetector = this.ip_port.result.textDetector + this.ip_port.result.textDetectorModel;
  }

   // Handles API errors and displays appropriate messages
  handleError(error: any) {
    console.log(error)
    console.log(error.status);
    console.log(error.error.detail);
    let message
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error.detail || error.error.message || "API has failed";
    }
    const action = 'Close';
    this.openSnackBar(message, action);
  }

  // Displays a snackbar with a message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

 // Resets the text input and related states
  resetText() {
    this.Prompt = '';
    this.loadComplete=false;
    this.responseLoading=false; 
  }

  // Resets the response table
  resetTable(): void {
    this.response = {};
  }

   // Handles checkbox selection and updates the prompt
  onCheckboxChange(checkboxId: string): void {
    if (checkboxId === 'ai') {
      this.isAIChecked = true;
      this.isHumanChecked = false;
      this.Prompt = this.Prompt1;
    } else if (checkboxId === 'human') {
      this.isAIChecked = false;
      this.isHumanChecked = true;
      this.Prompt = this.Prompt2;
    }
  }

  // Handles button clicks and updates the prompt
  onButtonClick(buttonId: string): void {
    if (buttonId === 'ai') {
      this.isAIChecked = true;
      this.isHumanChecked = false;
      this.Prompt = this.Prompt1;
    } else if (buttonId === 'human') {
      this.isAIChecked = false;
      this.isHumanChecked = true;
      this.Prompt = this.Prompt2;
    }
  }
  
  // Validates the text input and makes an API call if valid
  textValidationMethod() {
    this.responseLoading = true;
    this.loadComplete = false;
    try {
      const a = this.Prompt.replace(/[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]/g, '');
      const words = a.split(' ');
      const filteredWords = words.filter(word => word !== '');
      this.textLength = filteredWords.length;
      this.logger.log("Total words count", this.textLength);
      if (this.textLength >= 50) {
        this.showSpinner1 = true;
        const body = {
          text: this.Prompt
        }
        this.logger.log("User provided payload", JSON.stringify(body));
        this.https.post(this.textDetector, JSON.stringify(body), { headers: new HttpHeaders().set('Content-Type', 'application/json') }).subscribe(
          (res: any) => {
            this.logger.info("Api call has been successfull");
            this.response = res;
            this.flag = true;
            this.showSpinner1 = false;
            this.loadComplete = true;
            this.responseLoading=false; 
          },
          error => {
            this.logger.log("Error status", error.status);
            this.showSpinner1 = false;

            this.handleError(error)   
            this.loadComplete = false;       
            this.responseLoading=false;   
          }
        );
      }
      else {
        this.response = {};
        this._snackBar.open('Number of words should be greater than or equal to 50', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'bottom',
          duration: 3000,
        });
        this.responseLoading = false;
        this.loadComplete = false;
        this.cdr.detectChanges();
      }
    } catch (error) {
      this.logger.error("textValidationMethod method failed", error);
    }
  }
}
