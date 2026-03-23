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
export class ResponseComparisonService {
  apiEndpoints: any = {};

  constructor(private https: HttpClient) { }

  // Get Local Storage Data
  fetchApiUrl() {
    let { ip_port } = this.retrieveLocalStorageData();
    this.setApiList(ip_port);
  }
  setApiList(ip_port: any) {
    this.apiEndpoints.Moderationlayer_COV = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_COV;
    this.apiEndpoints.Moderationlayer_openaiCOT = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openaiCOT;
    this.apiEndpoints.thotApi = ip_port.result.FM_Moderation + ip_port.result.OpenAiThot;
    this.apiEndpoints.tokenImp = ip_port.result.Llm_Explain + ip_port.result.Token_Importance;
    this.apiEndpoints.hall_cov = ip_port.result.Rag + ip_port.result.RagCOV;
    this.apiEndpoints.hall_cot = ip_port.result.Rag + ip_port.result.RagCOT;
    this.apiEndpoints.hall_thot = ip_port.result.Rag + ip_port.result.RagTHOT;
    this.apiEndpoints.lotApi = ip_port.result.Rag + ip_port.result.RagLOT;
    this.apiEndpoints.serperApi = ip_port.result.Llm_Explain + ip_port.result.SerperResponse;
    this.apiEndpoints.got = ip_port.result.Llm_Explain + ip_port.result.ExplainGOT;
    this.apiEndpoints.llmExplain = ip_port.result.Llm_Explain + ip_port.result.Uncertainty;
    this.apiEndpoints.rereadUrl = ip_port.result.Llm_Explain + ip_port.result.ReReadReason;
    this.apiEndpoints.lotUrl = ip_port.result.Llm_Explain + ip_port.result.Explain_LOT;
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

  // HALLUCINATION APIS------------------
  hallucinateCOV(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.hall_cov, payload);
  }
  hallucinateThot(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.hall_thot, payload);
  }
  hallucinateCOT(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.hall_cot, payload);
  }

  // OPEN AI APIS---------------------
  covgetApi(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.Moderationlayer_COV, {
      text: payload.text,
      complexity: payload.complexity,
      model_name: payload.model_name,
      translate: payload.translate
    });
  }
  openAicotgetApi(payload :any): Observable<any> {
    return this.https.post(this.apiEndpoints.Moderationlayer_openaiCOT, payload);
  }
  openAiTHOTApi(payload:any): Observable<any> {
    return this.https.post(this.apiEndpoints.thotApi, payload);
  }
  tokenImportance(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.tokenImp, payload);
  }
  serperResponse(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.serperApi,payload);
  }
  gotResponse(payload: any):Observable<any> {
    return this.https.post(this.apiEndpoints.got,payload);
  }
  llmExplain(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.llmExplain, payload);
    }
    reread(payload: any): Observable<any> {
      return this.https.post(this.apiEndpoints.rereadUrl, payload);
      }
      logicOfThoughts(payload: any): Observable<any> {
        console.log(this.apiEndpoints.lotUrl);
        return this.https.post(this.apiEndpoints.lotUrl, payload);
      }
      lot(payload: any): Observable<any> {
        console.log(this.apiEndpoints.lotApi);
        return this.https.post(this.apiEndpoints.lotApi, payload);
      }
}
