/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, from, map, catchError, throwError } from 'rxjs';
import { NonceService } from '../nonce.service';
import { urlList } from '../urlList';
import {
  ApiEndpoints,
  PrivacyAnalyzePayload,
  PrivacyAnonymizePayload,
  PrivacyEncryptPayload,
  ProfanityPayload,
  ExplainabilityPayload,
  COVPayload,
  FairnessPayload,
  FMConfigPayload,
  LLMEvalPayload,
  OpenAIPayload,
  RAGRetrievalPayload,
  GEvalPayload,
  MultimodalUploadData,
  NemoCheckPayload,
  UserRolePayload,
  UserRoleResponse,
  ApiResponse,
  HallucinationResponse,
  LightRagResponse,
  FileUploadPayload,
  EmbeddingPayload,
  TimeApiResponse,
  RecommendationResponse,
  RecognizerResponse,
  SummaryEvalPayload
} from './interfaces/fm-moderation.interface';

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
    this.apiEndpoints.explainCOV = ip_port.result.Llm_Explain + ip_port.result.Explain_Cov;

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
    this.apiEndpoints.FairnessApiUrl = ip_port.result.Fairness + ip_port.result.FairUnstructure;

    // HALLUCINATION
    this.apiEndpoints.Admin_getEmbedings = ip_port.result.Admin_Rag + ip_port.result.Admin_getEmbedings;
    this.apiEndpoints.rag_FileUpload = ip_port.result.Rag + ip_port.result.RAG_FileUpload
    this.apiEndpoints.hall_cov = ip_port.result.Rag + ip_port.result.RagCOV;
    this.apiEndpoints.hall_cot = ip_port.result.Rag + ip_port.result.RagCOT;//"http://10.68.44.81:8002/rag/v1/cot";
    this.apiEndpoints.hall_thot = ip_port.result.Rag + ip_port.result.RagTHOT;

    this.apiEndpoints.GetTemplates = ip_port.result.Admin + ip_port.result.GETACCTEMPMAP;
    
    // RECOMMENDATION API
    this.apiEndpoints.promptRecommendation = ip_port.result.FM_Moderation + ip_port.result.PromptRecommendation;
    
    // PRIVACY RECOGNIZERS
    this.apiEndpoints.privacyRecognizersList = ip_port.result.Privacy + ip_port.result.Privacy_getRecognizer;
    
    // RAG G-EVAL
    this.apiEndpoints.RAG_gEval = ip_port.result.Rag + ip_port.result.RagGEVAL;
    
    // LIGHT RAG
    this.apiEndpoints.lightRag = ip_port.result.Rag + ip_port.result.LiteRAG;
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
  getFMService(data: any, fmlocalselected: any, p0?: unknown) {
    console.log("DATA:", data);
    const value = urlList.authToken
    const headers = new HttpHeaders
    ({'Authorization': value });
    console.log("FM VALUE: ", fmlocalselected);
    if (fmlocalselected == false) {
      console.log("DEPLOYED API TRIGGERED");
      return this.https.post(this.apiEndpoints.fm_api, data,{ headers: headers});
    } else if (fmlocalselected == true) {
      console.log("LOCAL API TRIGGERED");
 
      return this.getModerationData(this.apiEndpoints.fm_api, data);
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
        // Verify the origin of the received message
        if (event.origin !== window.location.origin) {
          return;
        }

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

  // ====== PRIVACY API METHODS ======
  
  /**
   * Calls Privacy Analyze API
   */
  callPrivacyAnalyze(payload: PrivacyAnalyzePayload): Observable<any> {
    return this.https.post(this.apiEndpoints.privacyAnalyzeApi, payload);
  }

  /**
   * Calls Privacy Anonymize API
   */
  callPrivacyAnonymize(payload: PrivacyAnonymizePayload): Observable<any> {
    return this.https.post(this.apiEndpoints.privacyAnonApi, payload);
  }

  /**
   * Calls Privacy Encrypt API
   */
  callPrivacyEncrypt(payload: PrivacyEncryptPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.privacyEncrypt, payload);
  }

  /**
   * Calls Privacy Decrypt API
   */
  callPrivacyDecrypt(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.privacyDecrypt, payload);
  }

  /**
   * Gets available recognizers for privacy
   */
  getRecognizers(): Observable<RecognizerResponse> {
    const headers = { 'accept': 'application/json' };
    return this.https.get<RecognizerResponse>(this.apiEndpoints.privacyRecognizersList!, { headers });
  }

  // ====== PROFANITY API METHODS ======
  
  /**
   * Calls Profanity Analyze API
   */
  callProfanityAnalyze(payload: ProfanityPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.profAnzApiUrl, payload);
  }

  /**
   * Calls Profanity Censor API
   */
  callProfanityCensor(payload: ProfanityPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.profCenApiUrl, payload);
  }

  // ====== EXPLAINABILITY API METHODS ======
  
  /**
   * Calls Explainability API
   */
  callExplainability(payload: ExplainabilityPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.explApiUrl, payload);
  }

  /**
   * Calls COV (Chain of Verification) API
   */
  callCOV(payload: COVPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.Moderationlayer_COV, payload);
  }
  callExplain_COV(payload: COVPayload): Observable<any> {
    console.log("COV PAYLOAD IN SERVICE:", this.apiEndpoints.explainCOV);
    return this.https.post(this.apiEndpoints.explainCOV, payload);
  }

  // ====== FAIRNESS API METHODS ======
  
  /**
   * Calls Fairness API
   */
  callFairness(payload: FairnessPayload): Observable<any> {
    const body = new URLSearchParams();
    body.set('response', payload.response);
    body.set('evaluator', payload.evaluator);
    
    return this.https.post(this.apiEndpoints.FairnessApiUrl, body, {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    });
  }

  /**
   * Calls Fairness Image API
   */
  callFairnessImage(formData: FormData): Observable<any> {
    return this.https.post(this.apiEndpoints.FairnessApiUrl + 'fairness_image', formData);
  }

  // ====== FM MODERATION API METHODS ======
  
  /**
   * Calls FM Config API
   */
  callFMConfig(payload: FMConfigPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.fm_config_getAttributes, payload).pipe(
      map((response: any) => ({
        response,
        comp_Payload: response
      })),
      catchError(error => throwError(error))
    );
  }

  /**
   * Calls LLM Evaluation API
   */
  callLLMEval(payload: LLMEvalPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.llm_eval, payload);
  }

  /**
   * Calls OpenAI API
   */
  callOpenAI(payload: OpenAIPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.fm_api_openAi, payload);
  }

  /**
   * Gets user role settings
   */
  getUserRole(payload: UserRolePayload): Observable<UserRoleResponse> {
    return this.https.post<UserRoleResponse>(this.apiEndpoints.admin_fm_admin_UserRole, payload);
  }

  /**
   * Gets FM API time
   */
  getFMTime(): Observable<TimeApiResponse> {
    return this.https.get<TimeApiResponse>(this.apiEndpoints.fm_api_time!);
  }

  // ====== RAG API METHODS ======
  
  /**
   * Calls RAG Retrieval API
   */
  callRAGRetrieval(payload: RAGRetrievalPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.rag_Retrieval, payload);
  }

  /**
   * Calls Light RAG API
   */
  callLightRAG(formData: FormData): Observable<any> {
    return this.https.post(this.apiEndpoints.lightRag, formData);
  }

  /**
   * Calls G-Eval API
   */
  callGEval(payload: SummaryEvalPayload): Observable<any> {
    return this.https.post(this.apiEndpoints.RAG_gEval, payload);
  }

  /**
   * Uploads file for RAG
   */
  uploadRAGFile(formData: FormData): Observable<any> {
    return this.https.post(this.apiEndpoints.rag_FileUpload, formData);
  }

  /**
   * Gets embeddings
   */
  getEmbeddings(payload: EmbeddingPayload): Observable<any> {
    const body = new URLSearchParams();
    body.set('userId', payload.userId);
    
    return this.https.post(this.apiEndpoints.Admin_getEmbedings, body, {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    });
  }

  // ====== MULTIMODAL API METHODS ======
  
  /**
   * Calls Multimodal API
   */
  callMultimodal(url: string, formData: FormData): Observable<any> {
    return this.https.post(url, formData);
  }

  // ====== NEMO GUARDRAIL API METHODS ======
  
  /**
   * Calls Nemo Check API
   */
  callNemoCheck(apiUrl: string, fileData: FormData): Observable<any> {
    return this.https.post(apiUrl, fileData);
  }

  /**
   * Calls Nemo Moderation Rail API
   */
  callNemoModerationRail(fileData: FormData): Observable<any> {
    return this.https.post(this.apiEndpoints.nemo_ModerationRail, fileData);
  }

  // ====== RECOMMENDATION API METHODS ======
  
  /**
   * Gets prompt recommendations
   */
  getRecommendations(): Observable<RecommendationResponse> {
    return this.https.post<RecommendationResponse>(this.apiEndpoints.promptRecommendation!, {});
  }

  // ====== TRANSLATION API METHODS ======
  
  /**
   * Calls Translation API
   */
  callTranslate(payload: any): Observable<any> {
    return this.https.post(this.apiEndpoints.Moderationlayer_Translate, payload);
  }

  // ====== ADDITIONAL FILE UPLOAD METHODS ======
  
  /**
   * Uploads file with specific payload structure
   */
  uploadFileWithPayload(file: File, selectModel: string = 'gemini'): Observable<any> {
    const fileData = new FormData();
    fileData.append('payload', file);
    fileData.append('select_model', selectModel);
    return this.https.post(this.apiEndpoints.rag_FileUpload, fileData);
  }

  /**
   * Uploads multiple files for RAG processing
   */
  uploadMultipleFiles(files: File[], selectModel: string = 'openai'): Observable<any> {
    const fileData = new FormData();
    files.forEach(file => {
      fileData.append('files', file);
    });
    fileData.append('llmtype', selectModel);
    return this.https.post(this.apiEndpoints.rag_FileUpload, fileData);
  }

  // ====== IMAGE PROCESSING API METHODS ======
  
  /**
   * Analyzes image for profanity
   */
  analyzeProfanityImageAdvanced(formData: FormData, endpoint: string): Observable<any> {
    return this.https.post(endpoint, formData);
  }

  /**
   * Analyzes privacy in image with specific endpoint
   */
  analyzePrivacyImageAdvanced(formData: FormData, endpoint: string): Observable<any> {
    return this.https.post(endpoint, formData);
  }

  /**
   * Anonymizes privacy in image with specific endpoint
   */
  anonymizePrivacyImageAdvanced(formData: FormData, endpoint: string): Observable<any> {
    return this.https.post(endpoint, formData);
  }

  /**
   * Processes fairness for images
   */
  processFairnessImage(formData: FormData, endpoint: string): Observable<any> {
    return this.https.post(endpoint, formData);
  }

  // ====== ERROR HANDLING ======
  
  /**
   * Generic error handler for API calls
   */
  handleError(error: any): Observable<ApiResponse> {
    let message = 'An error occurred';
    
    if (error.status === 430) {
      message = error.error.detail;
    } else if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error?.detail || error.error?.message || "API has failed";
    }
    
    return throwError({
      success: false,
      error: message,
      status: error.status
    });
  }

  // ====== UTILITY METHODS ======
  
  /**
   * Safely gets API endpoint URL
   */
  private getApiEndpoint(endpoint: keyof ApiEndpoints): string {
    const url = this.apiEndpoints[endpoint];
    if (!url) {
      throw new Error(`API endpoint '${endpoint}' is not configured`);
    }
    return url;
  }

  /**
   * Creates form data for file uploads
   */
  createFileFormData(files: File[], additionalData?: Record<string, string>): FormData {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('llmtype', "openai");
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }
    
    return formData;
  }
}
