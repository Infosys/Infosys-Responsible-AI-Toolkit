/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TemplateBasedGuardrailService {
  apiEndpoints: any = {};

  constructor(private https: HttpClient) { }
// Initializes the component and sets up API lists
  fetchApiUrl() {
    let { ip_port } = this.retrieveLocalStorageData();
    this.setApiList(ip_port);
  }
  // setup the apis
  setApiList(ip_port: any) {
    this.apiEndpoints.llm_eval = ip_port.result.FM_Moderation + ip_port.result.EvalLLM;
    this.apiEndpoints.textDetector = ip_port.result.textDetector + ip_port.result.textDetectorModel;
    this.apiEndpoints.multimodal = ip_port.result.FM_Moderation + ip_port.result.Multimodel;
  }
  retrieveLocalStorageData() {
    let ip_port;
    if (localStorage.getItem('res') != null) {
      const x = localStorage.getItem('res');
      if (x != null) {
        ip_port = JSON.parse(x);
      }
    }
    return { ip_port };
  }

  evalLLM(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.llm_eval, payload);
  }

  multiModal(payload: any): Observable<any> {
    console.log('MultiModal Payload ', payload);
    console.log('URL Multimodal', this.apiEndpoints.multimodal);
    return this.https.post(this.apiEndpoints.multimodal, payload);
  }

  contentDetector(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.textDetector, payload);
  }
}
