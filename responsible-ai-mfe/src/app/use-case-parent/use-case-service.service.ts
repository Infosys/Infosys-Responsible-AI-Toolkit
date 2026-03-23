/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UseCaseServiceService {

  constructor() { }

  private currentScreen = new BehaviorSubject(1);
  getcurrentScreen = this.currentScreen.asObservable();

  // Updates the current screen number
  setMessage(page: number) {
    this.currentScreen.next(page);
  }

  private editParameter = new BehaviorSubject(false);
  geteditParameter = this.editParameter.asObservable();

  // Updates the edit parameter
  setEditParameter(edit: any) {
    this.editParameter.next(edit);
  }

  
  private aiCanvas = new BehaviorSubject('');
  getAiCanvas = this.aiCanvas.asObservable();
// Updates the AI canvas data
  setAiCanvas(data: any) {
    console.log("setAiCanvas21===",data)
    this.aiCanvas.next(data);
  }

  private raicanvas = new BehaviorSubject('');
  getRaiCanvas = this.raicanvas.asObservable();
 // Updates the RAI canvas data
  setRaiCanvas(data: any) { 
    console.log("setRaiCanvas29===",data)
    this.raicanvas.next(data);
  }

  private useCaseName = new BehaviorSubject('');
  getUsecaseName = this.useCaseName.asObservable();
// Updates the use case name
  setUseCaseName(data: any) {
    this.useCaseName.next(data);
  }

  private generateReport = new BehaviorSubject(true);
  getGenerateReport = this.generateReport.asObservable();
 // Updates the generate report flag
  setGenerateReport(data: any) {  
    this.generateReport.next(data);
  }

  private questionnaireResponse = new BehaviorSubject('');
  getQuestionnaireResponse = this.questionnaireResponse.asObservable();
// Updates the questionnaire response
  setQuestionnaireResponse(data: any) {
    this.questionnaireResponse.next(data);
  }


  private currentPage = new BehaviorSubject(1);
  getcurrentPage = this.currentScreen.asObservable();
// Updates the current page number
  setCurrentPage(page: number) {
    this.currentPage.next(page);
  }

}
