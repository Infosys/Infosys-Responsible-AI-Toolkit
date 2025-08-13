/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, from } from 'rxjs';
import { NonceService } from '../nonce.service';
import { urlList } from '../urlList';

@Injectable({
  providedIn: 'root'
})
export class FmModerationService {

  private dataSource = new BehaviorSubject<any>(null);
  currentData = this.dataSource.asObservable();

  private nemoGaurrailResponse = new BehaviorSubject<any>(null);
  currentNemoGaurrailResponse = this.nemoGaurrailResponse.asObservable();

  private _MultiModal: any = {
    show : false,
    userId : '',
    templateList : [],
    prompt: '',
    file: '',
    fairnessRes: null
  };

  apiEndpoints: any = {};
  roleML: boolean = false;
  loggedINuserId: any;

  constructor(private https: HttpClient,public nonceService:NonceService) { }

  // Fetches API URLs from local storage and sets them
  fetchApiUrl() {
    let { ip_port } = this.retrieveLocalStorageData();
    this.setApiList(ip_port);
  }

   // Retrieves data from local storage
  retrieveLocalStorageData() {
    let ip_port;
    let Account_Role;
    if (localStorage.getItem('role') != null) {
      const role = localStorage.getItem('role');
      if (JSON.parse(role!) == 'ROLE_ML') {
        this.roleML = true;
      }
    }
    if (localStorage.getItem('res') != null) {
      const x = localStorage.getItem('res');
      if (x != null) {
        ip_port = JSON.parse(x);
      }
    }
    if (localStorage.getItem('role') != null) {
      const x = localStorage.getItem('role');
      if (x != null) {
        Account_Role = JSON.parse(x);
        console.log(' Account_Role', Account_Role);
      }
    }
    if (localStorage.getItem("userid") != null) {
      const x = localStorage.getItem("userid")
      if (x != null) {
        this.loggedINuserId = JSON.parse(x)
      }
    }
    return { ip_port, Account_Role };
  }

  // Sets the API endpoints for the service
  setApiList(ip_port: any) {
    console.log('API LIST FUNCTION');
    this.apiEndpoints.fm_api = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_completions;
    this.apiEndpoints.fm_api_openAi = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openai;
    this.apiEndpoints.llm_eval = ip_port.result.FM_Moderation + ip_port.result.EvalLLM;
    this.apiEndpoints.fm_api_time = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_ModerationTime;
    this.apiEndpoints.admin_fm_admin_UserRole = ip_port.result.Admin + ip_port.result.Admin_userRole; // + environment.admin_fm_admin_UserRole
    this.apiEndpoints.nemo_TopicalRail = ip_port.result.Nemo + ip_port.result.Nemo_TopicalRail; //+ environment.nemo_TopicalRail
    this.apiEndpoints.nemo_JailBreakRail = ip_port.result.Nemo + ip_port.result.Nemo_JailBreakRail; // + environment.nemo_JailBreakRail
    this.apiEndpoints.nemo_ModerationRail = ip_port.result.Nemo + ip_port.result.Nemo_ModerationRail; // + environment.nemo_ModerationRail
    this.apiEndpoints.nemo_FactCheckRail = ip_port.result.Nemo + ip_port.result.Nemo_FactCheckRail; // + environment.nemo_FactCheckRail
    this.apiEndpoints.rag_Retrieval = ip_port.result.Rag + ip_port.result.RAG_RetrievalKepler;//'http://10.68.44.81:8002/rag/v1/RetrievalKepler'; // + environment.rag_Retrieval
    this.apiEndpoints.Moderationlayer_COV = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_COV;
    this.apiEndpoints.Moderationlayer_openaiCOT = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openaiCOT;
    this.apiEndpoints.Moderationlayer_gEval = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_gEval;
    this.apiEndpoints.Moderationlayer_getTemplates = ip_port.result.FM_Moderation + ip_port.result.Fm_GETTEMPLATES;
    this.apiEndpoints.Moderationlayer_Translate = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_Translate;
    this.apiEndpoints.fm_config_getAttributes = ip_port.result.Admin + ip_port.result.Fm_Config_GetAttributes;
    this.apiEndpoints.tokenImp = ip_port.result.Llm_Explain + ip_port.result.Token_Importance;
    this.apiEndpoints.UncertainApi = ip_port.result.Llm_Explain + ip_port.result.Uncertainty;
    this.apiEndpoints.thotApi = ip_port.result.FM_Moderation + ip_port.result.OpenAiThot;

    // PRIVACY API
    this.apiEndpoints.privacyAnonApi = ip_port.result.Privacy + ip_port.result.Privacy_text_anonymize;
    this.apiEndpoints.privacyAnalyzeApi = ip_port.result.Privacy + ip_port.result.Privacy_text_analyze;
    this.apiEndpoints.privacyEncrypt = ip_port.result.Privacy + ip_port.result.Privacy_encrypt;
    this.apiEndpoints.privacyDecrypt = ip_port.result.Privacy + ip_port.result.Privacy_decrypt;

    // PROFANITY API
    this.apiEndpoints.profAnzApiUrl = ip_port.result.Profanity + ip_port.result.Profanity_text_analyze  // +  environment.profAnzApiUrl
    this.apiEndpoints.profCenApiUrl = ip_port.result.Profanity + ip_port.result.Profanity_text_censor
    // Explainability API

    this.apiEndpoints.explApiUrl = ip_port.result.Explainability
    // FAIRNESS API
    this.apiEndpoints.FairnessApiUrl = ip_port.result.FairnessAzure + ip_port.result.FairUnstructure;

    // HALLUCINATION
    this.apiEndpoints.Admin_getEmbedings = ip_port.result.Admin_Rag + ip_port.result.Admin_getEmbedings;
    this.apiEndpoints.rag_FileUpload = ip_port.result.Rag + ip_port.result.RAG_FileUpload
    this.apiEndpoints.hall_cov = ip_port.result.Rag + ip_port.result.RagCOV;
    this.apiEndpoints.hall_cot = ip_port.result.Rag + ip_port.result.RagCOT;//"http://10.68.44.81:8002/rag/v1/cot";
    this.apiEndpoints.hall_thot = ip_port.result.Rag + ip_port.result.RagTHOT;

    this.apiEndpoints.GetTemplates = ip_port.result.Admin + ip_port.result.GETACCTEMPMAP;
  }

  // Updates the data source with new data
  updateData(data: any) {
    this.dataSource.next(data);
  }

  // Updates the Nemo Guardrail response
  updateNemoGaurrailResponse(data: any) {
    this.nemoGaurrailResponse.next(data);
  }

  // Updates the MultiModal object with new values
  updateMultiModal(show:boolean, userId:string, templateList:any, prompt:string,file:any) {
    this._MultiModal.show = show;
    this._MultiModal.userId = userId;
    this._MultiModal.templateList = templateList;
    this._MultiModal.prompt = prompt;
    this._MultiModal.file = file;
    this._MultiModal.fairnessRes = null;
  }

  // Updates a specific key-value pair in the MultiModal object
  updateMultiModalKeyVal(key:string, value:any) {
    this._MultiModal[key] = value;
  }

  // Retrieves the current MultiModal object
  getMultiModal() {
    return this._MultiModal;
  }

  // Resets the MultiModal object to its default state
  resetMultiModal() {
    this._MultiModal = {
      show : false,
      userId : '',
      templateList : [],
      prompt: '',
      file: '',
      fairnessRes: null
    };
  }

  // APIS- Fetches templates for the logged-in user
  getTemplates() {
    return this.https.get(this.apiEndpoints.GetTemplates+this.loggedINuserId);
    // return this.https.get("http://10.66.155.13:30016/api/v1/rai/admin/getAccTemplate"+'/'+this.loggedINuserId);
  }

  // Fetches moderation templates for the logged-in user
  moderationGetTemplates() {
    console.log(this.apiEndpoints.Moderationlayer_getTemplates+'/'+this.loggedINuserId);
    return this.https.get(this.apiEndpoints.Moderationlayer_getTemplates+'/'+this.loggedINuserId);
    // return this.https.get("http://10.66.155.13:30016/api/v1/rai/admin/getAccTemplate"+'/'+this.loggedINuserId);
  }

  // Calls the FM service API based on the selected mode
  getFMService(endpoint: string, data: any, fmlocalselected: any, p0?: unknown) {
    console.log(endpoint,"endpoint","DATA:", data,)
    const value = urlList.authToken
    const headers = new HttpHeaders
    ({'Authorization': value });
    console.log("FM VALUE: ", fmlocalselected);
    if (fmlocalselected == false) {
      console.log("DEPLOYED API TRIGGERED");
      return this.https.post(endpoint, data,{ headers: headers});
    } else if (fmlocalselected == true) {
      console.log("LOCAL API TRIGGERED");
 
      return this.getModerationData(endpoint,data);
    } else {
      // Default return statement
      console.log("INVALID FM VALUE");
      return null;
    }
  }

  // Sends a moderation API request with CSRF token
  public getModerationData(endpoint: string, data: any): Observable<any> {
    // Get the CSRF token from a secure place (e.g., a meta tag or cookie)
  const csrfToken = this.nonceService.getNonce();
    // Create a URL object from the endpoint
    const url = new URL(endpoint);
    // Extract the part of the URL after the domain
    const path = url.pathname + url.search;
    console.log(path,"PATH")
    const payload = {
      action: 'fetchModerationAPI',
      endpoint: path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken  // Include the CSRF token as a custom header
      },
      body: JSON.stringify({
        ...data,
        csrfToken // Optionally include it in the body as well, depending on your API design
      })    };

    return new Observable(observer => {
      // Send message to the content script
      window.postMessage(payload, window.location.origin);

      // Listen for the response from the content script
      window.addEventListener('message', function(event) {
        // Only accept messages from the same frame
        if (event.source !== window) {
          return;
        }

        const message = event.data;

        // Only accept messages that we sent to ourselves
        if (typeof message !== 'object' || message === null || !message.success) {
          return;
        }

        observer.next(message.data);
        observer.complete();
      });
    });
  }

  // Checks if required keys exist in local storage
  checkLocalStorageForKeys(): boolean {
    let selectedPortfolio = localStorage.getItem('selectedPortfolio');
    let selectedAccount = localStorage.getItem('selectedAccount');

    let state = selectedPortfolio !== null && selectedAccount !== null;

    return state;
  }



}
