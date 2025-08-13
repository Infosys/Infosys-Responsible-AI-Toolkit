/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Component, OnChanges, SimpleChanges, OnDestroy, ViewEncapsulation, ViewChild, ChangeDetectorRef } from '@angular/core';
import { FmModerationService } from '../services/fm-moderation.service';
import { catchError, map, throwError } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RightSidePopupComponent } from './right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { RoleManagerService } from '../services/role-maganer.service';
import { SharedDataService } from '../services/shared-data.service';
import { NgbPopover } from '@ng-bootstrap/ng-bootstrap';
import { NgModel } from '@angular/forms';
import { ImageService } from '../image/image.service';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { FormControl } from '@angular/forms';
import { urlList } from '../urlList';
import { NonceService } from '../nonce.service';
import { UserValidationService } from '../services/user-validation.service';

@Component({
  selector: 'app-fm-moderation',
  templateUrl: './fm-moderation.component.html',
  styleUrls: ['./fm-moderation.component.css']
})
export class FmModerationComponent {
  // FOR SHIMMER EFFECT
  isLoadingSelectType = true;
  isLoadingPrompt = true;
  /////
  selectedAccount='';
  selectedPortfolio='';
  Placeholder:string = 'Enter Prompt (supports prompt with emojis also)'
  tempValue: number = 0;
  spinner = false;
  apiEndpoints: any = {}
  roles: any;
  roleMlChecked = false;
  tenantarr: any = []
  optionarr: any = []
  selectedOptions: any = []
  options: any = ["Privacy", "Profanity", "FM-Moderation", "Explainability", "Fairness"]
  disabledOptions:any =  [];
  selectUsecaseOptions: any = ["Demo", "Navi"]
  portfolioName: any ='';
  accountName: any = '';
  exclusionList: any
  roleML: boolean = false;
  loggedINuserId: any;
  userRoleSettings: any = {
    openAiStatusasperUserRole: '',
    selfReminder: '',
    llmInteraction: '',
    // isNemo:''
  };
  // LLM MODELS
  // Moderation :
  // { name:"GPT-4o",value:"gpt4"},
  // { name:"GPT-3",value:"gpt3"},
  // {name:"AWS Anthropic", value :"AWS_CLAUDE_V3_5"},
  // {name:"LLAMA", value :"Llama3-70b"},
  // {name:"GEMINI-2.5-FLASH","value:"Gemini-Flash"},
  // {name:"GEMINI-2.5-PRO","value:"Gemini-Pro"},
  Models = [
   { name:"GPT-4o",value:"gpt4"},
   { name:"GPT-3",value:"gpt3"},
   {name:"AWS Anthropic", value :"AWS_CLAUDE_V3_5"},
   {name:"LLAMA", value :"Llama3-70b"},
   {name:"GEMINI-2.5-FLASH",value:"Gemini-Flash"},
   {name:"GEMINI-2.5-PRO",value:"Gemini-Pro"},
   //  {name:"DeepSeek", value :"Deepseek"},
   //  {name:"PHI_3_5", value :"PHI-3-5"},
  ]
  llmBased: any = [];
  selectCoveComplexity: any = 'simple';
  selectPromptTemplate: any = 'GoalPriority';
  uncertainitySwitchCheck: boolean = false;
  hallucinationSwitchCheck: boolean = false;
  enableEmbedding: boolean = false;
  LiteRAGSwitchCheck: boolean = false;
  nemoGaurdrailCheck: boolean = false;
  noOfOptionUncertanity: number = 2;
  selectedLlmModel: any = 'gpt4';
  selectedTranslate: any = 'no';
  activeTab = '';
  buttonText: string = 'Execute Local FM Moderation';
  fmlocalselected = false;
  submitFlag= false;
  optionFlag= false;
  coupledModeration= false;
  filePreview: any = '';
  explainabilityOption: string = 'LLM';
  fmTimeApiResult = {
    "OpenAIInteractionTime": '',
    "requestModeration": '',
    "responseModeration": ''
  }
  selectedExplainabilityModel: any = '';
  explainabilityModels =[
  {name:"GEMINI-2.5- FLASH",value:"gemini-flash"},
  {name:"GEMINI-2.5-PRO",value:"gemini-pro"},
  {name:"AWS Anthropic", value :"aws"},
  { name:"GPT-4o",value:"gpt-4o"}
  ]
  x:boolean = true
  vectorId: any;
  fileupload: boolean = true;
  document= false;
  image=false;
  audio=false;
  video=false;
  isPDFFile = false;
  MMImageUrl='';
  MMAudioUrl='';
  MMVideoUrl='';
  MMPdfUrl = '';
  faithfulnessScore:any;
  relevanceScore:any;
  adhernceScore:any;
  correctnessScore:any;
  averageScore:any;
  faithfulness:any;
  relevance:any;
  adhernce:any;
  correctness:any;
  isLoadingMMImage= false;
  MMImageTHOT: any;
  MMImageCOV: any;
  MMImageCOT: any;
  MMImageHallucinationScore: any;
  MMImageResponse: any;
  MMPdfReference: any;
  lightRagRes: any='';
  MMTimeTaken: any;
  RKRes: any ='';
  openAIRes = {}
  COTRes: any = {}
  THOTRes: any = {}
  privacyResponse: any = {};
  profanityRes: any = {};
  explainabilityRes: any = {};
  fairnessRes: any = {};
  coupledModerationRes: any = {};
  nemoModerationRailRes: any = {};
  privacyOption = 'Choose Options';
  nlpOption:any = '';
  // piiEntitiesToBeRedactedOption: any[] = [];
  piiEntitiesToBeRedactedOption = new FormControl([]);
  panelOpenState = false;
  privacy_options = ["Privacy-Analyze", "Privacy-Anonymize", "Privacy-Encrypt", "Privacy-Highlight"];
  available_Recognizers = [];
  nlp_options = [
    { viewValue: 'Spacy-wb-lg (Basic)', value: 'basic' },
    { viewValue: 'Spacy-wb-trf (Good)', value: 'good' },
    { viewValue: 'PIIRanha (Medium)', value: 'ranha' },
    { viewValue: 'Roberta (High)', value: 'roberta' }

  ];
  nlptooltip = `Spacy-wb-lg (low accuracy & faster response),\n
  Spacy-wb-trf (medium accuracy & faster response) - Recommended,\n
  Roberta (high accuracy & slower response),\n
  PIIRanha (medium accuracy & medium response)`;
  Language_options = ["en", "fr"]
  nemoChecksApiResponses: any = {};
  // covResponse: any = {finishReason:"stop",index:0,text:"Hello! Absolutely, I'm here to provide helpful, accurate, and responsible information. If you have any questions or need assistance with something, feel free to ask, and I'll do my best to assist you.","timetaken":2.031};
  covResponse: any;
  covState: any = {
    active: false,
    hallucination: false,
    payload: {}
  }
  cotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  }
  thotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  }
  tokenImpState: any = {
    active: false,
    payload: {}
  }
  gotState: any = {
    active: false,
    payload: {}
  }
  llmExplainState: any = {
    active: false,
    payload: {}
  }
  contentDetectorState: any = {
    active: false,
    propmt: ''
  }
  serperResponseState: any = {
    model: this.selectedLlmModel,
    payload: {}
  }
  files: any = [];
  filesExplainability: any = [];
  demoFile: any = [];
  demoFile1: any = [];
  ExplanabilityFileId: any;
  ExplanabilityFileName: any = '';
  file: any;
  allEmbeddingsRes: any = [];
  selectedEmbeddedFileName: any = '';
  selectedEmbeddedFileId: any;
  hallucinateRetrievalKeplerRes: any = {
    "status": false,
    "errorMesssage": '',
    "response": {}
  };
  lightRag:any ={
    "status": false,
    "errorMessage": '',
    "response": {}
  }
  gEvalres: any = {};
  hallucinationResModerationData: any = {};
  llmEvalRes: any = {
    selectedOption: '',
    response: []
  }
  prompt: any = '';
  llmEvalPayload: any = {
    "AccountName": "None",
    "PortfolioName": "None",
    "userid": "None",
    "lotNumber": 1,
    "Prompt": this.prompt,
    "model_name": this.selectedLlmModel,
    "temperature": this.tempValue.toString(),
    "PromptTemplate": this.selectPromptTemplate,
  }
  requestModerationTemplates: any = [];
  responseModerationTemplates: any = [];
  templateBasedPayload: any = {
    status: false,
  };
 RagMultimodal:any =["jpg","jpeg","png","gif","bmp","jfif" ];
 RagMultiVideo:any =["mp4","3gp"];
  RagMultiFiles:any=[];
  // RagMultiModalResponse:any ={
  //   "status": false,
  //   "errorMessage": '',
  //   "response": {},
  //   "multiModal": false
  // };

  fairnessEvaluator: any = '';
  fairnessEvaluators = [
    { name: 'GPT-4o', value: 'GPT_4' },
    { name: 'LLAMA', value: 'LLAMA' },
    { name: 'GEMINI-2.5-FLASH', value: 'GEMINI_2.5_FLASH' },
    { name: 'GEMINI-2.5-PRO', value: 'GEMINI_2.5_PRO' },
    { name: 'AWS Anthropic', value: 'AWS' },
  ];
  useCaseSelectedFlag: boolean = false;
  selectedUseCaseName: any = '';
  setLoadTemplateResMod: boolean = false;
  allTemplates: any = [];
  res:any;
recommandedKey:any = []
displayedKeys :any=[]
showAll = false;
recommendedContent: any ;
recommend:any=true;
promptTest:any=''
recommendDrop=false;
selectedButton!:any;
isListVisible=true
enableSearch = false;
// Changes the active tab
  changeTab(tab: string) {
    this.activeTab = tab;
  }

  // Sets the flag for loading template-based moderation
  setLoadTemplateResModTrue() {
    console.log("setLoadTemplateResModTrue")
    this.setLoadTemplateResMod = true
  }

  tooltipContent: any;
  // Explainability variables
  isLoadingCOV: boolean = false;
  private COVUrl:any;
  covFinalAnswer:any;
  finalAnswer: string = '';
  COVAnswer: string = '';
  COVTimeTaken: any;
  ngAfterViewInit() {
    const tooltipDiv = document.getElementById('tooltip-content');
    if (tooltipDiv) {
      this.tooltipContent = tooltipDiv.innerHTML;
    }
  }
  // TETSING
  openRightSideModal(data: any) {
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      data: data,
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      // this.getAllBatches()
      console.log("POPUP CLOSE")
    });
  }

  bulkRagId: any;
  dataCuratorMsg: string = '';

  constructor(private imageService: ImageService, public roleService: RoleManagerService, private sharedDataService: SharedDataService, private sanitizer: DomSanitizer, private https: HttpClient, public fmService: FmModerationService, public _snackBar: MatSnackBar, public dialog: MatDialog,public nonceService:NonceService,private validationService:UserValidationService,private cdRef: ChangeDetectorRef) { }
  // Initializes the component and sets up API calls
  ngOnInit(): void {

    this.roles = this.roleService.getLocalStoreUserRole()
    this.options = this.roleService.getSelectedTypeOptions("Workbench", "Unstructured-Text", "Generative-AI")
    // FOR HACKATHON
    this.settingSelectOptions();
    ////////////////////

    this.fmService.fetchApiUrl();

    this.CallGetTemplates();
    let { ip_port, Account_Role } = this.retrieveLocalStorageData();
    console.log(ip_port,"ip port to be sent")
    this.setApiList(ip_port);
    this.initializeUserRole(Account_Role);
    //isLoadingSelectType = false;

    // set timeout for is loading
    this.isLoadingSelectType = false;
    this.isLoadingPrompt = false;

    this.selectedNotification = 'None';
    // this.callModerationGetTemplates();
    this.getRecommmendation();
    this.getRecognizers()
    // // set localstorage localfm variable to false
    // localStorage.setItem('localfm', 'false');

    this.bulkRagId = sessionStorage.getItem('vectorId');
    sessionStorage.removeItem('vectorId');
    this.assignBulkValue();
  }

  // Assigns bulk values for FM moderation
  assignBulkValue() {
    // making FM moderation checked by deafult
    this.tenantarr.push("FM-Moderation");
    this.selectedOptions["FM-Moderation"] = true;
    
    if(this.bulkRagId !== '' && this.bulkRagId !== undefined && this.bulkRagId !== null) {
      this.document = true;
      this.hallucinationSwitchCheck = true;
      this.fileupload = true;
      let totalFiles = Number(sessionStorage.getItem('totalRagFiles'))
      this.dataCuratorMsg = 'Uploaded with '+ totalFiles +' RAG file'+ (totalFiles > 1 ? 's' : '')+' from Data Curator';
      this._snackBar.open( this.dataCuratorMsg, '✖', {
        horizontalPosition: 'end',
        verticalPosition: 'top',
        duration: 5000,
      });
      sessionStorage.removeItem('totalRagFiles');
    }
    else {
      this.dataCuratorMsg = '';
      this.document = false;
      this.hallucinationSwitchCheck = false;
    }
  }

   // Fetches available recognizers for privacy checks
  getRecognizers() {
    
    let url = this.apiEndpoints.privacyRecognizersList;
    const headers = { 'accept': 'application/json' };
    
    this.https.get(url, { headers }).subscribe(
      (response: any) => {
        const availableRecognizers = response['Available Recognizers'];
        this.available_Recognizers = availableRecognizers;
      },
      (error) => {
        console.error('API error:');
      }
    );
  }

  // callModerationGetTemplates() {
  //   this.fmService.moderationGetTemplates().subscribe(
  //     (res: any) => {
  //       console.log(res);
  //     },
  //     error => {
  //       console.log(error);
  //     });
  // }

   // Toggles the visibility of all recommended keys
  toggleShowAll() {
    this.showAll = true;
    this.displayedKeys = this.recommandedKey;
    console.log("displaykey==",this.displayedKeys);
    console.log("recommandedkey==",this.recommandedKey);
  }

  // Fetches recommendations for prompts
  getRecommmendation(){  
    this.https.post(this.apiEndpoints.promptRecommendation,{}).subscribe(
      (data: any) => {
        this.res = data;
        console.log("recommanded data==",this.res);
        this.recommandedFiles();
      })
  }

   // Displays recommended content for a selected button
  showRecommand(btn:any){
    this.isListVisible=true;
    this.recommendedContent=this.res.prompts[btn];
    this.recommendDrop=true
    this.selectedButton = btn;
    console.log("recommanded content==",this.recommendedContent);
  }

   // Populates the list of recommended files
  recommandedFiles(){
    Object.keys(this.res.prompts).forEach((key) => {
      if(this.res.prompts[key].length>0){
        this.recommandedKey.push(key)
      console.log(key, this.res.prompts[key]);
      }
    });
    this.displayedKeys = this.recommandedKey.slice(0, 3);
  }

  // Adds a recommended prompt to the input field
  addToPrompt(data:any){
    console.log("data==",data);
    this.isListVisible=false;
    console.log("inside add to prompt");
    this.prompt = data;
    this.promptTest=data;
    // this.prompt = data.target.value;
    // this.promptTest=data.target.value;
    console.log("prompt==",this.prompt);
  }

  // Resets the recommendation dropdown
  resetRecommend(){
    this.showAll=false;
    this.selectedButton = undefined;
  }
  // ngOnDestroy() {
  //   this.resetData();
  // }

  formatOption(option: string): string {
    return option.replace(/_/g, ' ');
  }

  // FOR HACKATHON ONLY
  settingSelectOptions() {
    if (this.roles == 'ROLE_ML') {
      this.options = ["FM-Moderation"]
      this.selectedOptions["FM-Moderation"] = true;
      this.roleMlChecked = true;
      this.viewoptions()
    }
    console.log(this.options, "OPTIONS IN FUNCTION")

  }
  //////////////////////////////
  // Updates the tenant array based on selected options
  viewoptions() {
    const myObject = { ...this.selectedOptions };
    console.log("myObject===", myObject)
    const filteredKeys = this.filterKeysByBoolean(myObject);
    console.log("only keys", filteredKeys);
    this.tenantarr = filteredKeys;
    if (this.tenantarr.includes('Fairness') && this.filesMultiModel.length > 0) {
      this.Placeholder = "Enter Context"
    }else {
      this.Placeholder = "Enter Prompt";
    }
    if(!(this.tenantarr.includes('FM-Moderation'))){
      this.hallucinationSwitchCheck = false; // file upload needs to be reset if fm not in list
      this.coupledModeration = false;
      this.enableEmbedding = false;
    }
    if((this.tenantarr.includes('FM-Moderation'))){
      this.coupledModeration = true;
    }
  }

   // Filters keys from an object based on their boolean values
  filterKeysByBoolean(obj: Record<string, boolean>): string[] {
    return Object.keys(obj).filter((key) => obj[key]);
  }

  // Sets the API endpoints based on the configuration
  setApiList(ip_port: any) {
    // MULTIMODEL
    this.privAnonImgUrl2 = ip_port.result.Privacy + ip_port.result.Privacy_image_anonymize;
    this.privAnzImgUrl2 = ip_port.result.Privacy + ip_port.result.Privacy_image_analyze;
    this.profImageAnalyse = ip_port.result.Profanity + ip_port.result.Profan_Image_Analyse;
    this.fairness_image = ip_port.result.FairnessAzure + ip_port.result.FairnessImage;
    this.apiEndpoints.multimodal = ip_port.result.FM_Moderation + ip_port.result.Multimodel;

    this.apiEndpoints.fm_api = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_completions; // + environment.fm_api
    this.apiEndpoints.fm_api_openAi = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openai; //+ environment.fm_api_openAi
    this.apiEndpoints.llm_eval = ip_port.result.FM_Moderation + ip_port.result.EvalLLM;
    // this.fm_api_privacyShield = this.ip_port.result.FM_Moderation + this.ip_port.result.Moderationlayer_PrivacyPopup; //+ environment.fm_api_privacyShield
    // this.priAnonApiUrl2 = this.ip_port.result.FM_Moderation + this.ip_port.result.Privacy_text_anonymize; //+ environment.priAnonApiUrl2
    this.apiEndpoints.fm_api_time = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_ModerationTime; //+ environment.fm_api_time
    // this.fm_api_inf_ProfanityPopup = this.ip_port.result.FM_Moderation + this.ip_port.result.Moderationlayer_ProfanityPopup; // + environment.fm_api_inf_ProfanityPopup
    // this.fm_api_inf_ToxicityPopup = this.ip_port.result.FM_Moderation + this.ip_port.result.Moderationlayer_ToxicityPopup; // + environment.fm_api_inf_ToxicityPopup
    this.apiEndpoints.admin_fm_admin_UserRole = ip_port.result.Admin + ip_port.result.Admin_userRole; // + environment.admin_fm_admin_UserRole
    this.apiEndpoints.nemo_TopicalRail = ip_port.result.Nemo + ip_port.result.Nemo_TopicalRail; //+ environment.nemo_TopicalRail
    this.apiEndpoints.nemo_JailBreakRail = ip_port.result.Nemo + ip_port.result.Nemo_JailBreakRail; // + environment.nemo_JailBreakRail
    this.apiEndpoints.nemo_ModerationRail = ip_port.result.Nemo + ip_port.result.Nemo_ModerationRail; // + environment.nemo_ModerationRail
    this.apiEndpoints.nemo_FactCheckRail = ip_port.result.Nemo + ip_port.result.Nemo_FactCheckRail; // + environment.nemo_FactCheckRail
    this.apiEndpoints.rag_Retrieval = ip_port.result.Rag + ip_port.result.RAG_RetrievalKepler;//'http://10.68.44.81:8002/rag/v1/RetrievalKepler'; // + environment.rag_Retrieval
    // this.Moderationlayer_feedback = this.ip_port.result.FM_Moderation + this.ip_port.result.Moderationlayer_feedback;
    this.apiEndpoints.Moderationlayer_COV = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_COV;
    this.apiEndpoints.Moderationlayer_openaiCOT = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openaiCOT;
    this.apiEndpoints.Moderationlayer_gEval = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_gEval;
    this.apiEndpoints.RAG_gEval = ip_port.result.Rag + ip_port.result.RagGEVAL;
    this.apiEndpoints.Moderationlayer_Translate = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_Translate;
    this.apiEndpoints.fm_config_getAttributes = ip_port.result.Admin + ip_port.result.Fm_Config_GetAttributes;
    // //this.fm_config_getAttributes = "http://localhost:30016/api/v1/rai/admin/getAttributes"
    // this.hall_cov = this.ip_port.result.Rag + this.ip_port.result.RagCOV;
    // this.hall_cot = this.ip_port.result.Rag + this.ip_port.result.RagCOT;//"http://10.68.44.81:8002/rag/v1/cot";
    this.apiEndpoints.tokenImp = ip_port.result.Llm_Explain + ip_port.result.Token_Importance;
    this.apiEndpoints.UncertainApi = ip_port.result.Llm_Explain + ip_port.result.Uncertainty;
    this.apiEndpoints.thotApi = ip_port.result.FM_Moderation + ip_port.result.OpenAiThot;

    // PRIVACY API
    this.apiEndpoints.privacyAnonApi = ip_port.result.Privacy + ip_port.result.Privacy_text_anonymize;
    this.apiEndpoints.privacyAnalyzeApi = ip_port.result.Privacy + ip_port.result.Privacy_text_analyze;
    this.apiEndpoints.privacyEncrypt = ip_port.result.Privacy + ip_port.result.Privacy_encrypt;
    this.apiEndpoints.privacyDecrypt = ip_port.result.Privacy + ip_port.result.Privacy_decrypt;
    this.apiEndpoints.privacyRecognizersList = ip_port.result.Privacy + ip_port.result.Privacy_getRecognizer;

    // PROFANITY API
    this.apiEndpoints.profAnzApiUrl = ip_port.result.Profanity + ip_port.result.Profanity_text_analyze  // +  environment.profAnzApiUrl
    this.apiEndpoints.profCenApiUrl = ip_port.result.Profanity + ip_port.result.Profanity_text_censor
    // Explainability API
    this.apiEndpoints.explApiUrl = ip_port.result.Explainability;
    this.COVUrl = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_COV;

    // FAIRNESS API
    this.apiEndpoints.FairnessApiUrl = ip_port.result.FairnessAzure + ip_port.result.FairUnstructure;
    // LIGHT RAG
    this.apiEndpoints.lightRag = ip_port.result.Rag + ip_port.result.LiteRAG;
    // HALLUCINATION
    this.apiEndpoints.Admin_getEmbedings = ip_port.result.Admin_Rag + ip_port.result.Admin_getEmbedings;
    this.apiEndpoints.rag_FileUpload = ip_port.result.Rag + ip_port.result.RAG_FileUpload
    this.apiEndpoints.hall_cov = ip_port.result.Rag + ip_port.result.RagCOV;
    this.apiEndpoints.hall_cot = ip_port.result.Rag + ip_port.result.RagCOT;//"http://10.68.44.81:8002/rag/v1/cot";
    this.apiEndpoints.hall_thot = ip_port.result.Rag + ip_port.result.RagTHOT;
    // RAG MULTIMODAL
    this.apiEndpoints.rag_image = ip_port.result.Rag + ip_port.result.Rag_Image;
    this.apiEndpoints.rag_video = ip_port.result.Rag + ip_port.result.Rag_Video;
    this.MMImageUrl = ip_port.result.Rag + ip_port.result.MMImageUrl;
    this.MMAudioUrl = ip_port.result.Rag + ip_port.result.MMAudioUrl;
    this.MMVideoUrl = ip_port.result.Rag + ip_port.result.MMVideoUrl;
    this.MMPdfUrl = ip_port.result.Rag + ip_port.result.MMPdfUrl;
    //Recommendation API
    this.apiEndpoints.promptRecommendation = ip_port.result.FM_Moderation + ip_port.result.PromptRecommendation;

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
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.loggedINuserId = x
        console.log(" userId", this.loggedINuserId)
      }
    }
    return { ip_port, Account_Role };
  }

  // Initializes user role settings
  initializeUserRole(Account_Role: any) {
    this.https.post(this.apiEndpoints.admin_fm_admin_UserRole, { role: Account_Role }).subscribe(
      (res: any) => {
        this.userRoleSettings.openAiStatusasperUserRole = res.isOpenAI;
        this.userRoleSettings.selfReminder = res.selfReminder;
        // this.userRoleSettings.isNemo = res.isNemo;
                this.userRoleSettings.llmInteraction = res.isOpenAI ? 'yes' : 'no';
        console.log(this.userRoleSettings)
      },
      error => {
        console.log(error.status);
        if (error.status == 430) {
          // this.showSpinner1 = false;
          // this.edited = false;
          console.log(error.error.detail);
          const message = error.error.detail;
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          // this.showSpinner1 = false;
          // this.edited = false;
          // console.log(error.error.detail)
          let message
          if (error.status === 500) {
            message = "Internal Server Error. Please try again later.";
          } else {
            message = error.error.detail || error.error.message || "API has failed";
          }
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        }
      });
  }

  // Opens a snackbar with a message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

   // Checks if an object is empty
  isEmptyObject(obj: Object): boolean {
    return JSON.stringify(obj) === '{}';
  }

  // Selects an embedded method for file processing
  selectEmbeddedMethod(data: any) {
    this.files = []
    this.RagMultiFiles=[];
    let selectedOption = data.options[data.options.selectedIndex];
    this.selectedEmbeddedFileName = selectedOption.value;
    this.selectedEmbeddedFileId = selectedOption.id;
  }
  SettingValue():void {
    this.fmlocalselected = true;
  }

  // Handles the form submission
  onSubmit(formData: any) {
    this.getSelectedValues();
    if (this.tenantarr == undefined || this.tenantarr.length == 0) {
      const message = 'Please select Select Type';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    if (this.tenantarr.includes('Fairness') && this.fairnessEvaluator.length == 0) {
      const message = 'Please select Evaluator for fairness';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
      return;
    }

    this.optionarr= this.tenantarr;
    this.optionFlag= true;
    if((this.tenantarr.includes('FM-Moderation'))){
      this.coupledModeration = true;
      this.submitFlag = true
    }else{
      this.submitFlag = false
    }

    // Rempoving the template Bsased Responses from Service
    this.sharedDataService.clearResponses();
    this.setLoadTemplateResMod = false;
   // this.templateBasedPayload['status'] = false;

   let { hallucinationSwitch, nemoGaurdrail, selectedUsecase, prompt, temp, llmAsEvaluatorSwitch } = formData.value;
   let accountName = this.selectedAccount;
   let portfolioName = this.selectedPortfolio;
    this.prompt = prompt;
    this.selectedUseCaseName = selectedUsecase;
    // this.resetMultiModelResult()
    this.resetResultData()
    // MULTIMODEL
    if (this.tenantarr.includes('FM-Moderation') && this.filesMultiModel.length > 0 && this.image==true ) {
      this.callMultiModel()
    }

    // text based templates checks 
    if (selectedUsecase == '' || selectedUsecase == 'Navi') {
      if (this.filesMultiModel.length > 0) {
        this.requestModerationTemplates = ["Prompt Injection Check", "Jailbreak Check","Language Critique Coherence Check", "Language Critique Fluency Check", "Language Critique Grammar Check", "Language Critique Politeness Check"]
        
      } else {
        this.requestModerationTemplates = ["Prompt Injection Check", "Jailbreak Check", "Fairness and Bias Check", "Language Critique Coherence Check", "Language Critique Fluency Check", "Language Critique Grammar Check", "Language Critique Politeness Check"] //imp
        

      }
      this.responseModerationTemplates = ["Response Completeness Check", "Response Conciseness Check", "Response Language Critique Coherence Check", "Response Language Critique Fluency Check", "Response Language Critique Grammar Check", "Response Language Critique Politeness Check"]
      // this.templateBasedPayload.userid = this.loggedINuserId
      this.templateBasedPayload.userid = "None"
      if (selectedUsecase == 'Navi') {
        this.callEvalLLMNavi(prompt, 'Navi Tone Correctness Check');
      }
    }

    if (this.tenantarr.includes('FM-Moderation') && hallucinationSwitch && this.selectedEmbeddedFileName == '') {
      const message = 'Please select the embeddings';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    this.llmEvalPayload = {
      "AccountName": accountName,
      "PortfolioName": portfolioName,
      "userid": "None", // KEEPINH "NONE" AS ITS NOT WORKING WITH USERIDS
      // "userid": localStorage.getItem('userid')?localStorage.getItem('userid') : "None",
      "lotNumber": 1,
      "Prompt": this.prompt,
      "model_name": this.selectedLlmModel,
      "temperature": this.tempValue.toString(),
      "PromptTemplate": this.selectPromptTemplate,
    }

    if (!prompt || !prompt.trim()) {
      const message = 'Please enter the prompt';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
      return;
    }


    this.spinner = true;
    this.changeTab('');
    this.privacyResponse = {};
    this.profanityRes = {};
    this.explainabilityRes = {};
    this.coupledModerationRes = {};
    if (this.tenantarr.includes('Privacy')) {
      let { exclusionListPrivacy, fakeDataFlag } = formData.value;
      let accountNamePrivacy = this.selectedAccount;
      let portfolioNamePrivacy = this.selectedPortfolio;
      this.callPrivacyAPI(prompt, accountNamePrivacy, portfolioNamePrivacy, exclusionListPrivacy, fakeDataFlag);
    }
    if (this.tenantarr.includes('Profanity')) {
    let { exclusionListProf } = formData.value;
    let accountNameProf = this.selectedAccount;
    let portfolioNameProf = this.selectedPortfolio;
      this.callProfanityAPI(prompt);
    }
    if (this.tenantarr.includes('Explainability')) {
      this.callExplainabilityAPI(prompt);
    }
    if (this.tenantarr.includes('Fairness')) {
      if (this.filesMultiModel.length > 0) {
        const formPayload = new FormData();
        formPayload.append('prompt', this.prompt);
        formPayload.append('evaluator', "GPT_4o");
        formPayload.append('image', this.filesMultiModel[0]);
        this.fairnessImage(formPayload)
      } else {
        this.callFairnessAPI(prompt);
      }
    }
    if (this.tenantarr.includes('FM-Moderation')) {
      // HANDLE IF PROMPT ENPTY OR numDesc <0 or > 2 ----------- HAVE TO IMPLEMENT
      temp = (temp / 10).toFixed(1);
      let tempStringValue = temp.toString();
    if (tempStringValue == '0.0') {
        tempStringValue = '0';
      }
      if (llmAsEvaluatorSwitch) {
        this.llmBased = ["randomNoiseCheck"];
      } else {
        this.llmBased = [];
      }
      this.serperResponseState = {
        model: this.selectedLlmModel,
        payload: {
          inputPrompt: prompt
        }
      }

      // CHECK textArr.length 0 or not --------------------HAVE TO IMPLEMENT
      if (portfolioName.length == 0 || accountName.length == 0) {
        this.customApipayloadStatus= false
        if (!hallucinationSwitch) {
          console.log("hallucinationSwitch is false");
          if (!this.userRoleSettings.openAiStatusasperUserRole) { //-------------IF OPENAI IS FALSE----------------
            this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch);
          } else if (this.userRoleSettings.openAiStatusasperUserRole) {
            this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch)
            if (!this.roleML) {
              // this.covgetApi(prompt);
              this.covState = {
                active: this.useCaseSelectedFlag ? false : true,
                payload: {
                  text: prompt,
                  complexity: this.selectCoveComplexity,
                  model_name: this.selectedLlmModel
                }
              }
              console.log("covState", this.covState)
              this.cotState = {
                active: this.useCaseSelectedFlag ? false : true,
                payload: {
                  temperature: tempStringValue,
                  Prompt: prompt,
                  model_name: this.selectedLlmModel
                }
              }
              this.cdRef.detectChanges();
              
              this.thotState = {
                active: this.useCaseSelectedFlag ? false : true,
                payload: {
                  temperature: tempStringValue,
                  Prompt: prompt,
                  model_name: this.selectedLlmModel
                }
              }
              // this.openAicotgetApi(prompt, tempStringValue);
              // this.openAiTHOTApi(prompt, tempStringValue)
            }
            this.callOpenAiApi(prompt, tempStringValue)
          }

        } else if (hallucinationSwitch) {
          this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch);
          this.callOpenAiApi(prompt, tempStringValue)
        }
        if (nemoGaurdrail) {
          const fileData = new FormData();
          fileData.append('text', prompt);
          this.callNemoCheckApi(this.apiEndpoints.nemo_TopicalRail, fileData, 'nemoTopicalRailStatus', 'nemoTopicalRailTime');
          this.callNemoCheckApi(this.apiEndpoints.nemo_JailBreakRail, fileData, 'nemoJailbreakCheckStatus', 'nemoJailbreakCheckTime');
          this.callNemoCheckApi(this.apiEndpoints.nemo_FactCheckRail, fileData, 'nemoFactcheckRailStatus', 'nemoFactcheckRailTime');
        }
      } else {

        // if (this.hallucination == true) {
        //   // this.resetHall()
        //   // this.cdr.detectChanges();
        //   this.LLMinteractionValue = 'No';
        // }
        // get attributes based on account/portfolio
        const configPayload = {
          AccountName: accountName,
          PortfolioName: portfolioName,
        };
        this.callFMConfigApi(configPayload, accountName, portfolioName, tempStringValue, prompt).subscribe(
          ({ response, comp_Payload }) => {
            console.log(response);
            if (!hallucinationSwitch) {
              console.log("hallucinationSwitch is false");
              if (!this.userRoleSettings.openAiStatusasperUserRole) { //-------------IF OPENAI IS FALSE----------------
                this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch, comp_Payload);
              } else if (this.userRoleSettings.openAiStatusasperUserRole) {
                this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch, comp_Payload)
                if (!this.roleML) {
                  this.covState = {
                    active: this.useCaseSelectedFlag ? false : true,
                    payload: {
                      text: prompt,
                      complexity: this.selectCoveComplexity,
                      model_name: this.selectedLlmModel
                    }
                  }
                  console.log("covState", this.covState)
                  this.cotState = {
                    active: this.useCaseSelectedFlag ? false : true,
                    payload: {
                      temperature: tempStringValue,
                      Prompt: prompt,
                      model_name: this.selectedLlmModel
                    }
                
                  }
                  this.cdRef.detectChanges();
                  this.thotState = {
                    active: this.useCaseSelectedFlag ? false : true,
                    payload: {
                      temperature: tempStringValue,
                      Prompt: prompt,
                      model_name: this.selectedLlmModel
                    }
                  }
                }
                this.callOpenAiApi(prompt, tempStringValue)
              }
            } else if (hallucinationSwitch) {
              this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch);
              this.callOpenAiApi(prompt, tempStringValue)
            }
          },
          error => {
            this.handleError(error);
          }
        );
      }
      if (!this.roleML) {
        this.tokenImpState = {
          active: this.useCaseSelectedFlag ? false : true,
          payload: {
            "inputPrompt": prompt,
            "modelName": "GPT"
          }
        }
        this.gotState = {
          active: this.useCaseSelectedFlag ? false : true,
          payload: {
            "inputPrompt": prompt,
            "modelName": 'gpt-35-turbo'
          }
        }
        this.llmExplainState = {
          active: this.useCaseSelectedFlag ? false : true,
          payload: {
            "inputPrompt": prompt
          }
        }
        // Checking For Content Derector API
        const a = prompt.replace(/[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]/g, '');
        const words = a.split(' ');
        const filteredWords = words.filter((word: any) => word !== '');
        if (filteredWords.length >= 50) {
          this.contentDetectorState = {
            active: true,
            prompt: prompt
          }
        }
      }
    }
    this.fmlocalselected = false;

    temp = (temp / 10).toFixed(1);
    let tempStringValue = temp.toString();
    if (tempStringValue == '0.0') {
      tempStringValue = '0';
    }
    if (this.document == true) {
      this.RKRes = '';
      const payload = {
        fileupload: true,
        text: this.prompt,
        vectorestoreid: this.vectorId ? this.vectorId : this.bulkRagId ? this.bulkRagId : null
      };    
      this.hallucinateRetrievalKeplerRes.status = true;
      this.https.post(this.apiEndpoints.rag_Retrieval, payload).subscribe(
        (res: any) => {
        if (res && res.rag_response && Array.isArray(res.rag_response)) {
          // Loop through each item in the rag_response array
          res.rag_response.forEach((item: any) => {
              // Check if 'text' exists in the current item and append it to the RKRes
              if (item && item[0] && item[0].text) {
                this.RKRes += item[0].text + "\n";  // Add a newline after each text item for separation
              }
          });
      
          this.hallucinateRetrievalKeplerRes.response.text = this.RKRes.replace(/\n/g, '<br>');
      }
        for (let item of res.rag_response) {
          if (item.Faithfulness_Hallucination_score !== undefined) {
            this.hallucinateRetrievalKeplerRes.response.hallScore = item.Faithfulness_Hallucination_score;
          }
          if (item["source-file"]) {
            this.hallucinateRetrievalKeplerRes.response.source = item["source-file"];
          }  
          if (item["Matching Section From Document"]) {
            this.hallucinateRetrievalKeplerRes.response.section = item["Matching Section From Document"];
          }       
           // Check if the combinedText is not empty or null
           if (this.hallucinateRetrievalKeplerRes.response.text && this.hallucinateRetrievalKeplerRes.response.text.trim() !== "" && item["page_content"]) {       
             let pageContent = item["page_content"];
              // Call the necessary APIs if combined text is valid
              this.callFMApi(this.RKRes, tempStringValue, nemoGaurdrail, true, undefined, true);
                this.getSummarygEval(this.RKRes, pageContent);
             }
        }
        },
        error => {
          console.log("RetrievalKepler Failed");
          this.hallucinateRetrievalKeplerRes.status = false;
          this.hallucinateRetrievalKeplerRes.errorMesssage = 'Hallucination API Failed';
        }
      );
      
    }
    if(this.image==true){
      //this.MMImage();
      this.MultimodalMethod(this.MMImageUrl);
    }
    if(this.audio==true){
      this.MultimodalMethod(this.MMAudioUrl);
    }
    if(this.video==true){
      this.MultimodalMethod(this.MMVideoUrl);
    }
    if(this.isPDFFile == true){
      if(this.LiteRAGSwitchCheck){
        this.callLiteRAG();
      }else{
     this.MultimodalMethod(this.MMPdfUrl);
      }
    }
  }
  
  // Calls the LiteRAG API
  callLiteRAG(){
    this.lightRagRes = '';
    const fileData = new FormData();
    for (let i = 0; i < this.filesMultiModel.length; i++) {
      const file = this.filesMultiModel[i];
      fileData.append('file', file);
    }
    fileData.append('text', this.prompt);
    this.lightRag.status = true;
    this.https.post(this.apiEndpoints.lightRag, fileData).subscribe((res:any) =>{
      if(res  && Array.isArray(res)){
        res.forEach((item: any) =>{
          if(item && item[0] && item[0].Response){
            this.lightRagRes += item[0].Response + "\n";
          }
          if(item && item[0] && item[0].Hallucination_score){
            this.lightRag.response.hallScore = item[0].Hallucination_score;
          }
          if(item && item[0] && item[0]['GEval Metrics']){
            this.lightRag.response.GEval = item[0]['GEval Metrics'];
          }
          if(item && item[0] && item[0]['Time Taken']){
            this.lightRag.response.timeTaken = item[0]['Time Taken'];
          }
        });
        this.lightRag.response.text = this.lightRagRes.replace(/\n/g, '<br>');
        this.callFMApi(this.lightRag.response.text, '0', false, true, undefined, true);

        console.log("this.lightRag.response.text::",this.lightRag.response.text)
      }
    })
  }
  // MMImage() {    
  //   const formData = new FormData();
  //   formData.append('file', this.UploadedFile);
  //   formData.append('text', this.prompt);

  //   this.https.post(this.MMImageUrl, formData)
  //     .subscribe((response: any) => {
  //       if (response && response[0] && response[0][0] && response[0][0].Response) {
  //         this.MMImageResponse = response[0][0].Response[0].replace(/\n/g, '<br>');      
  //         this.callFMApi(this.MMImageResponse, '0', false, true, undefined, true);
  //       } else {
  //         this.MMImageResponse = 'Invalid response format';
  //       }
  //     }); 
  // }

  // Handles multimodal file uploads
  MultimodalMethod(url: any) {
    this.MMImageResponse = '';
    this.isLoadingMMImage = true;
    console.log("UploadedFile", this.UploadedFile);

    const formData = new FormData();
   // formData.append('file', this.UploadedFile);
   for (let i = 0; i < this.filesMultiModel.length; i++) {
    const file = this.filesMultiModel[i];
    formData.append('file', file);
  }
    formData.append('text', this.prompt);

      this.https.post(url, formData) 
      .subscribe((response: any) => {
        this.isLoadingMMImage = false;
   
      if(this.isPDFFile){
        if (response && response[0] && response[0][0] && response[0][0].Response) {
          this.MMImageResponse = response[0][0].Response.replace(/\n/g, '<br>');
          this.callFMApi(this.MMImageResponse, '0', false, true, undefined, true);
      } else {
          this.MMImageResponse = 'Invalid response format';
      }
        if (response && response[1] && response[1].Hallucination_score !== undefined) {
          this.MMImageHallucinationScore = response[1].Hallucination_score;
        } else {
          this.MMImageHallucinationScore = 'Invalid response format';
        }
        if (response && response[2] && response[2][0] && response[2][0]["Reference"]) {
          this.MMPdfReference = response[2][0]["Reference"].replace(/\n/g, '<br>');
      } else {
          this.MMPdfReference = 'Invalid response format';
      }
      if (response && response[3] && response[3][0] && response[3][0]["Chain of Thoughts Response"]) {
        this.MMImageCOT = response[3][0]["Chain of Thoughts Response"][0].replace(/\n/g, '<br>');
    } else {
        this.MMImageCOT = 'Invalid response format';
    }

    if (response && response[4] && response[4][0] && response[4][0]["Thread of Thoughts Response"]) {
        this.MMImageTHOT = response[4][0]["Thread of Thoughts Response"][0].replace(/\n/g, '<br>');
    } else {
        this.MMImageTHOT = 'Invalid response format';
    }

    if (response && response[5] && response[5][0] && response[5][0]["Chain of Verification Response"]) {
        this.MMImageCOV = response[5][0]["Chain of Verification Response"][0].replace(/\n/g, '<br>');
    } else {
        this.MMImageCOV = 'Invalid response format';
    } 

    if (response && response[6] && response[6][0] && response[6][0]["GEval Metrics"]) {
      const metrics = response[6][0]["GEval Metrics"][0];
      this.faithfulnessScore = metrics.faithfulness;
      this.relevanceScore = metrics.relevance;
      this.adhernceScore = metrics.adherance;
      this.correctnessScore = metrics.correctness;
      this.averageScore = metrics.AverageScore;

      const definitions = response[6][0]["GEval Metrics"][1];
      this.faithfulness = definitions.faithfulness;
      this.relevance = definitions.relevance;
      this.adhernce = definitions.adherance;
      this.correctness = definitions.correctness;
      }else {
        this.faithfulness = 'Invalid response format';
        this.relevance = 'Invalid response format';
        this.adhernce = 'Invalid response format';
        this.correctness = 'Invalid response format';
      }
    if(response && response[7] && response[7][0] && response[7][0]["Time Taken"]){
      this.MMTimeTaken = response[7][0]["Time Taken"];
    }
    }
      else{
        if (response && response[0] && response[0][0] && response[0][0].Response) {
          this.MMImageResponse = response[0][0].Response[0].replace(/\n/g, '<br>');
          this.callFMApi(this.MMImageResponse, '0', false, true, undefined, true);
      } else {
          this.MMImageResponse = 'Invalid response format';
      }
        if (response && response[1] && response[1].Hallucination_score !== undefined) {
          this.MMImageHallucinationScore = response[1].Hallucination_score;
        } else {
          this.MMImageHallucinationScore = 'Invalid response format';
        }
      if (response && response[2] && response[2][0] && response[2][0]["Chain of Thoughts Response"]) {
          this.MMImageCOT = response[2][0]["Chain of Thoughts Response"][0].replace(/\n/g, '<br>');
      } else {
          this.MMImageCOT = 'Invalid response format';
      }

      if (response && response[3] && response[3][0] && response[3][0]["Thread of Thoughts Response"]) {
          this.MMImageTHOT = response[3][0]["Thread of Thoughts Response"][0].replace(/\n/g, '<br>');
      } else {
          this.MMImageTHOT = 'Invalid response format';
      }

      if (response && response[4] && response[4][0] && response[4][0]["Chain of Verification Response"]) {
          this.MMImageCOV = response[4][0]["Chain of Verification Response"][0].replace(/\n/g, '<br>');
      } else {
          this.MMImageCOV = 'Invalid response format';
      } 

      if (response && response[5] && response[5][0] && response[5][0]["GEval Metrics"]) {
        const metrics = response[5][0]["GEval Metrics"][0];
        this.faithfulnessScore = metrics.faithfulness;
        this.relevanceScore = metrics.relevance;
        this.adhernceScore = metrics.adherance;
        this.correctnessScore = metrics.correctness;
        this.averageScore = metrics.AverageScore;
  
        const definitions = response[5][0]["GEval Metrics"][1];
        this.faithfulness = definitions.faithfulness;
        this.relevance = definitions.relevance;
        this.adhernce = definitions.adherance;
        this.correctness = definitions.correctness;
        }else {
          this.faithfulness = 'Invalid response format';
          this.relevance = 'Invalid response format';
          this.adhernce = 'Invalid response format';
          this.correctness = 'Invalid response format';
        }
      if(response && response[6] && response[6][0] && response[6][0]["Time Taken"]){
        this.MMTimeTaken = response[6][0]["Time Taken"];
      }
    }




      }, error => {
        this.isLoadingMMImage = false;
        this.MMImageResponse = 'API Failed';
        this.MMImageTHOT = 'API Failed';
        this.MMImageCOT = 'API Failed';
        this.MMImageCOV = 'API Failed';
        this.MMPdfReference = 'API Failed';
      }); 
  }

   // Resets the form data
  resetData(form: any) {
    this.disabledOptions=[]
    this.hallucinationSwitchCheck = false;
    this.enableEmbedding = false;
    this.LiteRAGSwitchCheck = false;
    this.nemoGaurdrailCheck = false;
    this.files = [];
    this.RagMultiFiles=[];
    this.tState = false
    this.selectedTranslate = "no"
    this.selectedNotification = "no"
    this.selectedEmojiVal = "no"
    this.tLoading = false
    this.selectedButton=''
    this.recommendDrop=false 
    form.controls['prompt'].setValue('');
    form.controls['selectedUsecase'].setValue('');
    this.useCaseSelectedFlag = false;
    if (this.roles !== 'ROLE_ML') {
      console.log("ROLE_MLllllllllllllllll")
      this.selectedOptions = [];
      this.tenantarr = [];
    }
    this.spinner = false;
    // this.removeFileMultimodel()
    this.resetFileHandlers()
    this.resetResultData()
    this.optionarr= [];
    this.optionFlag= false;
    this.bulkRagId = '';
    this.dataCuratorMsg = '';
    this.vectorId = '';
    this.fileupload = true;
  }

  // Resets the result data
  resetResultData() {
    this.fmService.resetMultiModal();
    this.setLoadTemplateResMod = false;
    this.activeTab = ''
    this.privacyResponse = {};
    this.profanityRes = {};
    this.explainabilityRes = {};
    this.coupledModerationRes = {};
    this.fairnessRes = {};
    this.openAIRes = {};
    this.COTRes = {};
    this.THOTRes = {};
    this.nemoModerationRailRes = {};
    this.fmTimeApiResult.requestModeration = '';
    this.fmTimeApiResult.responseModeration = '';
    this.fmTimeApiResult.OpenAIInteractionTime = '';
    this.nemoChecksApiResponses = {};
    this.covResponse = {};
    this.covState = {
      active: false,
      hallucination: false,
      payload: {}
    }; console.log("covstate reseted");
    this.cotState = {
      active: false,
      hallucination: false,
      payload: {}
    }
    console.log("cot reseted")
    this.thotState = {
      active: false,
      hallucination: false,
      payload: {}
    }
    this.tokenImpState = {
      active: false,
      payload: {}
    }
    this.gotState = {
      active: false,
      payload: {}
    }
    this.llmExplainState = {
      active: false,
      payload: {}
    }
    this.contentDetectorState = {
      active: false,
      prompt: ''
    }
    this.serperResponseState = {
      model: this.selectedLlmModel,
      payload: {}
    }
    this.hallucinateRetrievalKeplerRes = {
      "status": false,
      "response": {}
    };
    this.lightRag ={
      "status": false,
      "errorMessage": '',
      "response": {}
    }
    // this. RagMultiModalResponse ={
    //   "status": false,
    //   "response": {},
    //   "multiModal": false
    // };
    this.gEvalres = {};
    this.hallucinationResModerationData = {};
    this.llmEvalRes = {
      selectedOption: '',
      response: []
    }
    this.templateBasedPayload.status = false;

    this.resetMultiModelResult()
  }

  requestTemplateGlobal=[]
  responseTemplateGlobal=[]
  globalMultiModeltemplateList:any = []
  globalMultiEvaltemplateList:any = []

  // Handles model selection
  onModelSelect(event: any) {
   this.selectedLlmModel = event?.target.value;
  }
  
   // Handles template selection
  onTemplateSelect(event: any) {
    console.log(event?.target.value)
    console.log("all of the templates",this.allTemplates)

    if (event?.target.value != 'Navi') {
      let selectedTemplate = this.allTemplates.find((template: any) => template.mapId == event?.target.value);
      console.log("selectedTemplate", selectedTemplate)
      if (selectedTemplate.SingleModel) {// if contion for if single model is exists
        if (selectedTemplate.SingleModel && selectedTemplate.SingleModel.Template) {
          this.requestModerationTemplates = selectedTemplate.SingleModel.Template.requestTemplate;
          this.responseModerationTemplates = selectedTemplate.SingleModel.Template.responseTemplate;
          this.templateBasedPayload = {
            AccountName: selectedTemplate.account,
            PortfolioName: selectedTemplate.portfolio,
            userid: "None"
            //userid: this.loggedINuserId
          }
        }else{
          this.requestModerationTemplates = [];
          this.requestModerationTemplates = [];
        }
        if (selectedTemplate.SingleModel && selectedTemplate.SingleModel.Model) {

          // this.requestTemplateGlobal = selectedTemplate.responseTemplate;
  
          this.requestTemplateGlobal = selectedTemplate.SingleModel.Model.requestTemplate;
          this.responseTemplateGlobal = selectedTemplate.SingleModel.Model.responseTemplate;
        }else{
          this.requestTemplateGlobal = [];
          this.responseTemplateGlobal = [];
        }

      }
  }
    
    console.log("Template Based on Select Type", this.templateBasedPayload, this.requestModerationTemplates, this.responseModerationTemplates)
  }

  // -------------GET Initial Embeddings for Hallucination----------------
  getembeddigns() {
    const userIdvalue = this.loggedINuserId
    const body = new URLSearchParams();
    body.set('userId', userIdvalue.toString());
    this.https.post(this.apiEndpoints.Admin_getEmbedings, body, {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    }).subscribe(
      (res: any) => {
        this.allEmbeddingsRes = res;
        // this.dataSource1= res;
        // this.cacheId =  res[0].cacheId;
      }, error => {
        this.handleError(error);
      })
  }

  // Fetches templates for moderation
  CallGetTemplates() {
    this.fmService.getTemplates().subscribe(
      (res: any) => {
        console.log(res)
        this.allTemplates = res?.accList?.sort((a: any, b: any) => a.portfolio.localeCompare(b.portfolio));
      },
      error => {
        this.handleError(error);
      }
    )
  }

  // ----------Handle File Upload For Hallucination---------------------
  // fileBrowseHandler(imgFile: any) {
  //   this.selectedEmbeddedFileName = '';
  //   this.selectedEmbeddedFileId = '';
  //   this.prepareFilesList(imgFile.target.files);
  //   this.demoFile = this.files;
  //   this.file = this.files[0];
  // }

  // Handles file uploads for hallucination checks
  fileBrowseHandler(imgFile: any) {
    console.log("fileBrowseHandler", imgFile.target.files)    
    const supportedTypes = ['application/pdf', 'text/csv', 'text/plain'];
    const file = imgFile.target.files[0];

    if (!file || !supportedTypes.includes(file.type)) {
      this._snackBar.open('Only .pdf, .csv and .txt files are supported', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
      return;
    }
    this.selectedEmbeddedFileName = '';
    this.selectedEmbeddedFileId = '';
    this.demoFile = this.files;
    // this.browseFilesLenth = imgFile.target.files.length;
    this.prepareFilesList(imgFile.target.files);
    // console.log("Files[0]",this.files[0] )
    // const reader = new FileReader();
    // reader.readAsDataURL(this.files[0]);
    // reader.onload = (_event) => {
    //   this.filePreview = reader.result;
    //   console.log("filePreview",this.filePreview )
    // }
  }
  fileBrowseHandler1(imgFile: any) {
    const allowedTypes = ['application/pdf', 'text/csv', 'text/plain'];
    console.log("fileBrowseHandler", imgFile.target.files[0].type)
    if (!allowedTypes.includes(imgFile.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      }); 
      // return;
    }else{
    this.ExplanabilityFileName = '';
    this.ExplanabilityFileId = '';
    this.demoFile1 = this.filesExplainability;
    this.prepareFilesList1(imgFile.target.files);
    console.log("fileBrowseHandler", this.filesExplainability);
    }
  }

  // Deletes a file from the list
  deleteFile(index: number) {
    if (this.files[index].progress < 100) {
      console.log("if of deltefile 1.");
      return;
    }
    console.log("in delete 1")
    this.files.splice(index, 1);
  }
  deleteFile1(index: number) {
    if (this.filesExplainability[index].progress < 100) {
      console.log("if of deltefile 1.");
      return;
    }
    console.log("in delete 1")
    this.filesExplainability.splice(index, 1);
  }
 
  // Prepares the file list for upload
  prepareFilesList(files: Array<any>) {
    for (const item of files) {
      item.progress = 0;
      const reader = new FileReader();
      reader.readAsDataURL(item);
      reader.onload = (_event) => {
          item.preview = reader.result;
          item.type = item.type;
      };
      console.log("item.preview", item.preview)
      console.log("item.type", item.type)
      this.files.push(item);
    }
    // this.fileDropEl.nativeElement.value = "";
    this.uploadFilesSimulator(0);
  }
  prepareFilesList1(filesExplainability: Array<any>) {
    for (const item of filesExplainability) {
      item.progress = 0;
      const reader = new FileReader();
      reader.readAsDataURL(item);
      reader.onload = (_event) => {
          item.preview = reader.result;
          item.type = item.type;
      };
      console.log("item.preview", item.preview)
      console.log("item.type", item.type)
      this.filesExplainability.push(item);
    }
    // this.fileDropEl.nativeElement.value = "";
    this.uploadFilesSimulator1(0);
    console.log("preparedfiles", this.filesExplainability)
  }

 // Simulates file upload progress
  uploadFilesSimulator(index: number) {
    setTimeout(() => {
      if (index === this.files.length) {
        return;
      } else {
        const progressInterval = setInterval(() => {
          if (this.files[index].progress === 100) {
            clearInterval(progressInterval);
            this.uploadFilesSimulator(index + 1);
          } else {
            this.files[index].progress += 20;
          }
        }, 200);
      }
    }, 1000);
  }

  uploadFilesSimulator1(index: number) {
    setTimeout(() => {
      if (index === this.filesExplainability.length) {
        return;
      } else {
        const progressInterval = setInterval(() => {
          if (this.filesExplainability[index].progress === 100) {
            clearInterval(progressInterval);
            this.uploadFilesSimulator1(index + 1);
          } else {
            this.filesExplainability[index].progress += 20;
          }
        }, 200);
      }
    }, 1000);
  }

  // Removes all uploaded files
  removeFile() {
    this.files = [];
    this.RagMultiFiles=[];
    this.demoFile = [];
    this.file = '';
    this.selectedEmbeddedFileName = '';
    this.selectedEmbeddedFileId = '';
    this.ExplanabilityFileName = '';
    this.ExplanabilityFileId = '';
  }

  //-----------------Upload Hallucination File------------------
  async callUploadEmbeddedFile() {
    const fileData = new FormData();
    for (let i = 0; i < this.demoFile.length; i++) {
      fileData.append('files', this.demoFile[i]);
      fileData.append('select_model',"gemini");
      console.log("new  file upload comp.........", fileData)
    }
    return new Promise((resolve, reject) => {
      this.https.post(this.apiEndpoints.rag_FileUpload, fileData).subscribe(
        (res: any) => {
          console.log("data sent to database" + res);
          this.selectedEmbeddedFileId = res;
          resolve(res);
        },
        error => {
          this.handleError(error);
          reject(error);
        }
      );
    });
  }
  async callUploadEmbeddedFile1() {
    const fileData = new FormData();
    for (let i = 0; i < this.demoFile1.length; i++) {
      fileData.append('payload', this.demoFile1[i]);
      fileData.append('select_model',"gemini");
      console.log("new  file upload comp.........", fileData)
    }
    return new Promise((resolve, reject) => {
      this.https.post(this.apiEndpoints.rag_FileUpload, fileData).subscribe(
        (res: any) => {
          console.log("data sent to database" + res);
          this.ExplanabilityFileId = res;
          resolve(res);
        },
        error => {
          this.handleError(error);
          reject(error);
        }
      );
    });
  }
  removeRagFile(){
    this.RagMultiFiles = [];
  }

  // Resets explainability results4
  resetExplainability() {
    this.activeTab = ''
    this.explainabilityRes = {};
    this.filesExplainability = [];
  }
  // ---------------CALLING APIS----------------------
  callEvalLLMNavi(prompt: any, templateName: any) {
    let payload = {
      Prompt: prompt,
      template_name: templateName,
      model_name: this.selectedLlmModel,
      AccountName: this.accountName ? this.accountName : "None",
      "PortfolioName": this.portfolioName ? this.portfolioName : "None",
      "userid": "None", // keepg "none" as its working only with none & not userids
      // "userid": this.loggedINuserId,
      "lotNumber": 1,
      "Context": "None",
      "Concise_Context": "None",
      "Reranked_Context": "None",
      "temperature": this.tempValue.toString(),
      "PromptTemplate": this.selectPromptTemplate,
    }
    this.sharedDataService.updateNaviTonemoderationRes("status", 'LOADING');
    console.log(payload)
    this.https.post(this.apiEndpoints.llm_eval, payload).subscribe(
      (res: any) => {
        let response = res.moderationResults.response[0]
        this.sharedDataService.updateNaviTonemoderationRes("analysis", response.analysis);
        this.sharedDataService.updateNaviTonemoderationRes("context", response.Context);
        this.sharedDataService.updateNaviTonemoderationRes("sentiment", response.Sentiment);
        this.sharedDataService.updateNaviTonemoderationRes("domain", response.Domain);
        this.sharedDataService.updateNaviTonemoderationRes("toneScore", response['Tone Score']);
        this.sharedDataService.updateNaviTonemoderationRes("timetaken", response.timetaken);
        this.sharedDataService.updateNaviTonemoderationRes("status", 'COMPLETED');
      },
      error => {
        this.sharedDataService.updateNaviTonemoderationRes("status", 'FAILED');
      })
  }

  // Handles Privacy API calls
  callPrivacyAPI(prompt: any, accountName: any, portfolioName: any, exclusionList: any, fakeDataFlag: any) {
    console.log("privacy api called", this.nlpOption, "2nd list", this.piiEntitiesToBeRedactedOption.value);
    accountName = this.selectedAccount;
    portfolioName = this.selectedPortfolio;
  
    let payloadAnon: any = {
      inputText: prompt,
      portfolio: portfolioName,
      account: accountName,
      exclusionList: exclusionList,
      user: this.loggedINuserId,
      fakeData: fakeDataFlag ? true : false,
      redactionType: "replace",
      piiEntitiesToBeRedacted: null as string[] | null,
      nlp: null as string | null
    };
  
    let payloadAnalyze: any = {
      inputText: prompt,
      portfolio: portfolioName,
      account: accountName,
      exclusionList: exclusionList,
      user: this.loggedINuserId,
      piiEntitiesToBeRedacted: null as string[] | null,
      nlp: null as string | null
    };
  
    let payloadEncrypt: any = {
      inputText: prompt,
      // portfolio: portfolioName,
      // account: accountName,
      // exclusionList: exclusionList,
      // user: this.loggedINuserId,
      piiEntitiesToBeRedacted: null as string[] | null,
      nlp: null as string | null
    };
    
    if (accountName.length != 0 && portfolioName.length != 0) {
      payloadEncrypt.piiEntitiesToBeRedacted = null;
      payloadEncrypt.nlp = null;
    
      if (this.fmService.checkLocalStorageForKeys()) {
        payloadEncrypt.piiEntitiesToBeRedacted = this.piiEntitiesToBeRedactedOption.value;
        payloadEncrypt.nlp = this.nlpOption;
      }
    } else {
      payloadEncrypt.piiEntitiesToBeRedacted = this.piiEntitiesToBeRedactedOption.value;
      // payloadEncrypt.portfolio = null;
      // payloadEncrypt.account = null;
      payloadEncrypt.nlp = this.nlpOption;
      // payloadEncrypt.exclusionList = '';
    }
  
    let payloadDecrypt = prompt;
  
    if (accountName.length != 0 && portfolioName.length != 0) {
      payloadAnon.fakeData = fakeDataFlag ? true : false;
      payloadAnalyze.piiEntitiesToBeRedacted = null;
      payloadAnalyze.nlp = null;
  
      if (this.fmService.checkLocalStorageForKeys()) {
        payloadAnalyze.piiEntitiesToBeRedacted = this.piiEntitiesToBeRedactedOption.value;
        payloadAnalyze.nlp = this.nlpOption;
      }
    } else {
      payloadAnon.piiEntitiesToBeRedacted = this.piiEntitiesToBeRedactedOption.value;
      payloadAnon.portfolio = null;
      payloadAnon.account = null;
      payloadAnon.nlp = this.nlpOption;
      payloadAnalyze.portfolio = null;
      payloadAnalyze.account = null;
      payloadAnalyze.piiEntitiesToBeRedacted = this.piiEntitiesToBeRedactedOption.value;
      payloadAnalyze.nlp = this.nlpOption;
      payloadAnalyze.exclusionList = '';
    }
  
    if (this.privacyOption == 'Choose Options') {
      this.callPrivacyAnalyze(payloadAnalyze);
      this.callPrivacyAnonymize(payloadAnon);
    } else if (this.privacyOption == 'Privacy-Analyze') {
      this.callPrivacyAnalyze(payloadAnalyze);
    } else if (this.privacyOption == 'Privacy-Anonymize') {
      this.callPrivacyAnonymize(payloadAnon);
    } else if (this.privacyOption == 'Privacy-Encrypt') {
      this.callPrivacyEncrypt(payloadEncrypt);
    } else if (this.privacyOption == 'Privacy-Highlight') {
      this.callPrivacyAnalyze(payloadAnalyze);
    }
    // else if(this.privacyOption == 'Privacy-Decrypt'){
    //   this.callPrivacyDecrypt(payloadDecrypt);
    // }/// privacy decrypt api is being directly called after encrypt api response is recived
  }
  resetPrivacyResult() {
    this.privacyResponse = {};
  }
  
  // Handles Profanity API calls
  callProfanityAPI(prompt: any) {
    let payload = {
      inputText: prompt,
      user: this.loggedINuserId
    }
    this.https.post(this.apiEndpoints.profAnzApiUrl, payload).subscribe((res: any) => {
      console.log(res)
      this.profanityRes.AnazRes = res
    }
      , error => {
        this.handleError(error);
      })
    this.https.post(this.apiEndpoints.profCenApiUrl, payload).subscribe((res: any) => {
      console.log(res)
      this.profanityRes.cenRes = res
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Profanity');
      }
    }
      , error => {
        this.handleError(error);
      })
  }

  // Handles Explainability API calls
  callExplainabilityAPI(prompt: any) {
    if (this.explainabilityOption == 'Sentiment') {
       this.https.post(this.apiEndpoints.explApiUrl, { inputPrompt: prompt,modelName:this.selectedExplainabilityModel }).subscribe((expRes) => {
      this.explainabilityRes = expRes;
      console.log(expRes)
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Explainability');
      }
    }, error => {
      this.handleError(error);
    })
    }
   else if (this.explainabilityOption == 'RAG') {
      this.callUploadEmbeddedFile1().then(res => {
        console.log(res);
        console.log(this.ExplanabilityFileId, "ExplanabilityFileId");
        this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Explainability');
      }
      });
    } else {
      this.isLoadingCOV = true;
      const payload = {
        complexity: 'simple',
        // model_name: 'gpt4',
        model_name: this.selectedExplainabilityModel,
        translate: this.selectedTranslate,
        text: this.prompt
      };
      if (this.activeTab == '') {
        this.changeTab('Explainability');
      }
      this.https.post(this.COVUrl, payload)
      .subscribe((response: any) => {
        this.spinner = false;
        
        console.log('API response:', response);
        this.covFinalAnswer = response.final_answer;
        this.finalAnswer = this.covFinalAnswer;
        let formattedText = response.verification_answers
        .replace(/Question: 1/, 'Question: 1')
        .replace(/Question: 2/, '<br><br>Question: 2')
        .replace(/Question: 3/, '<br><br>Question: 3')
        .replace(/Question: 4/, '<br><br>Question: 4')
        .replace(/Question: 5/, '<br><br>Question: 5')
        .replace(/Answer:/g, '<br>Answer:');
        this.COVAnswer = formattedText;
        this.COVTimeTaken = response.timetaken;
        this.isLoadingCOV = false;
      }, error => {
        console.error('API error:');
        this.isLoadingCOV = false;
      });
    }


  }

  // Handles Fairness API calls
  callFairnessAPI(prompt: any) {
    console.log("in fariness api function")
    let body = new URLSearchParams();
    body.set('response', prompt.toString());
    body.set('evaluator', this.fairnessEvaluator.toString());
    this.https.post(this.apiEndpoints.FairnessApiUrl, body, {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    }).subscribe((fairRes) => {
      this.fairnessRes = fairRes
      console.log(fairRes)
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Fairness');
      }
    }, error => {
      this.handleError(error);
    })
  }

  // Handles OpenAI API calls
  callFMApi(prompt: string, tempStringValue: string, nemoGaurdrail: any, hallucinationSwitch: any, payload?: any, hallucinationPostCall: any = false) {
    console.log("callFMApi");
    let data = payload ? payload : this.comp_Payload(prompt, tempStringValue, this.userRoleSettings.llmInteraction, this.selectPromptTemplate);
    // this.fmService.getFMService(this.apiEndpoints.fm_api, data)?.subscribe()
    this.fmService.getFMService(this.apiEndpoints.fm_api, data, this.fmlocalselected)?.subscribe(
        async (res: any) => {
          this.templateBasedPayload['status'] = true;
          // this.handle_FM_API_Response(res);
          if (hallucinationPostCall) {
            console.log("CALL FM API ---------------------------------------hallucinationPostCall=TRUE ")
            this.hallucinationResModerationData = res.moderationResults.requestModeration;
            console.log(this.hallucinationResModerationData)
          } else {
            console.log("CALL FM API ---------------------------------------hallucinationPostCall=FALSE")
            this.coupledModerationRes = res;
            this.coupledModeration= true;
            this.fmService.updateData(res);
            this.changeTab('Request Moderation');
          }
          let summaryStatus = res.moderationResults.requestModeration.summary.status;
          let reSstatus = res.moderationResults.responseModeration.summary.status;
          console.log("summaryStatus", summaryStatus)
          console.log("reSstatus", reSstatus)
          this.callNemoApi(prompt, nemoGaurdrail, summaryStatus);
          this.callFMTimeApi(hallucinationPostCall);
          this.spinner = false;
          // this.isCollapsed = true; // Collapse Right Panel

          if (hallucinationSwitch && !hallucinationPostCall) {
            if (summaryStatus == 'PASSED' || reSstatus == 'PASSED') {
              this.hallucinateRetrievalKeplerRes.status = true;
               if (this.selectedEmbeddedFileName != '') {
                this.vectorId = this.selectedEmbeddedFileId;
                this.fileupload = false;
                const requestBody = {
                  fileupload: false,
                  text: prompt,
                  vectorestoreid: this.selectedEmbeddedFileId,
                }
                const ragCov = {
                  fileupload: false,
                  text: prompt,
                  vectorestoreid: this.selectedEmbeddedFileId,
                  complexity: this.selectCoveComplexity
                }
                this.hallucinateRetrievalKepler(requestBody, prompt, tempStringValue, nemoGaurdrail, summaryStatus);
                this.cotState = {
                  active: this.useCaseSelectedFlag ? false : true,
                  hallucination: true,
                  payload: requestBody
                }
                this.cdRef.detectChanges();
                this.thotState = {
                  active: this.useCaseSelectedFlag ? false : true,
                  hallucination: true,
                  payload: requestBody
                }
                this.covState = {
                  active: this.useCaseSelectedFlag ? false : true,
                  hallucination: true,
                  payload: ragCov
                }
                console.log("covState", this.covState)
              }
            } else {
              this.hallucinateRetrievalKeplerRes.status = false;
              this.hallucinateRetrievalKeplerRes.errorMesssage = 'Coupled Moderation Checks Failed';
            }
          }
          this.templateBasedPayload['status'] = true;
        },
        error => {
          this.hallucinateRetrievalKeplerRes.status = false;
          this.hallucinateRetrievalKeplerRes.errorMesssage = 'Coupled Moderation API Failed';
          this.spinner = false;
          this.handleError(error, 'Coupled Moderation API Failed')
        }
      );
  }
  gibrishDisplayLabels=[]
  bannedCategoriesDisplay=[]
  customApipayloadStatus:boolean =false
  // Handles FM Config API calls
  callFMConfigApi(configPayload: any, accountName: any, portfolioName: any, tempStringValue: any, prompt: any) {
    accountName = this.selectedAccount;
    portfolioName = this.selectedPortfolio;
    return this.https.post(this.apiEndpoints.fm_config_getAttributes, configPayload).pipe(
      catchError(error => {
        return throwError(error);
      }),
      map((res: any) => {
         
        const response = res.dataList[0];
        console.log("config api res",res.dataList[0] )
        // Store the values in local variables
        const bannedCategories = response.ModerationCheckThresholds.InvisibleTextCountDetails.BannedCategories;
        const gibberishLabels = response.ModerationCheckThresholds.GibberishDetails.GibberishLabels;

        this.gibrishDisplayLabels= gibberishLabels
        this.bannedCategoriesDisplay= bannedCategories
        this.customApipayloadStatus= true


        if (this.selectedUseCaseName) { // Check if the string has any value
          if (this.selectedUseCaseName === 'Navi') {
            const comp_Payload = this.payloadFMConfig(response, accountName, portfolioName, tempStringValue, prompt);
            return { response, comp_Payload };
          } else {
            const comp_Payload = this.payloadFMConfig_templatebase(response, accountName, portfolioName, tempStringValue, prompt);
            return { response, comp_Payload };
          }
        } else {
          // Handle the case where selectedUseCaseName is empty or null
          const comp_Payload = this.payloadFMConfig(response, accountName, portfolioName, tempStringValue, prompt);
            return { response, comp_Payload };
        }
      })
    );
  }

  // Handles OpenAI API calls
  callOpenAiApi(prompt: string, tempStringValue: string) {
    this.https
      .post(this.apiEndpoints.fm_api_openAi, { Prompt: prompt, temperature: tempStringValue, model_name: this.selectedLlmModel })
      .subscribe(
        (res: any) => {
          console.log(res.text.length);
          if (res.textlength == 0) {
            this.openAIRes = 'Open Ai failed Reason :' + res.finishReason;
            const message = 'Open Ai failed Reason :' + res.finishReason;
            const action = 'Close';
            this._snackBar.open(message, action, {
              duration: 5000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
          } else {
            console.log(res)
            const boldRegex = /\*\*(.+?)\*\*/;
            const numberedRegex = /\n/g;
            const replacement = "<br>";
            let processedText = res.text.replace(boldRegex, "<b>$1</b>");
            res.text = processedText.replace(numberedRegex, replacement);
            this.openAIRes = res;
            // this.showCompare = true;
            // this.cdr.detectChanges();
          }
        },
        error => {
          this.handleError(error, "OPENAI API FAILED");
        }
      );
  }
  // --------------------------Hallucination API------------------------------
  hallucinateRetrievalKepler(payload: any, prompt: any, tempStringValue: any, nemoGaurdrail: any, summaryStatus: any) {
    const tempSourceebar: any[] = [];
    this.https.post(this.apiEndpoints.rag_Retrieval, payload).subscribe((data: any) => {
      console.log(this.hallucinateRetrievalKeplerRes)
      // this.showSpinner1 = false;
      const res = data.rag_response;
      let sourceBar = []
      let bites = [];
      let ragText = '';
      let page_content = '';
      console.log(res, "HALLUCINATRION RES")
      for (let i = 0; i < res.length; i++) {
        if (res[i]['Faithfulness_Hallucination_score']) {
          this.hallucinateRetrievalKeplerRes.response.hallScore = res[i]['Faithfulness_Hallucination_score'];
        }
        for (let j = 0; j < res[i].length; j++) {
          if (res[i][j].text && res[i][j].text != 'undefined') {
            ragText = ragText + res[i][j].text;
            bites.push({
              text: res[i][j].text,
              source: res[i][j].source,
              baseurl: res[i][j].base64 ? res[i][j].base64 : undefined,
            });
          }
          if (res[i][j].endsrc) {
            for (let k = 0; k < res[i][j].endsrc.length; k++) {
              const temp = {
                source: res[i][j].endsrc[k].source,
                base64: res[i][j].endsrc[k].base64,
              };
              tempSourceebar.push(temp);
            }
          }
          sourceBar = tempSourceebar;
          if (res[i][j].base64 && res[i][j].base64 != 'undefined') {
            this.hallucinateRetrievalKeplerRes.response.base64 = res[i][j].base64;
          }
          if (res[i][j].source && res[i][j].source != 'undefined') {
            this.hallucinateRetrievalKeplerRes.response.source = res[i][j].source;
          }
        }
      
        // Aggregate page_content if it exists
        if (res[i].page_content && res[i].page_content != 'undefined') {
          page_content = page_content + res[i].page_content;
        }
        if (res[i].openai_score && res[i].openai_score != 'undefined') {
          this.hallucinateRetrievalKeplerRes.response.openAiScore = res[i].openai_score;
        }
        if (res[i]['source-file'] && res[i]['source-file'] != 'undefined') {
          this.hallucinateRetrievalKeplerRes.response.sourceFile = res[i]['source-file'];
        }
        if (res[i]["Matching Section From Document"] && res[i]["Matching Section From Document"] != 'undefined') {
          this.hallucinateRetrievalKeplerRes.response.section = res[i]["Matching Section From Document"];
      }
      }
          
      console.log(this.hallucinateRetrievalKeplerRes.response, "RESPOMSE HALLUCINATION")
      this.hallucinateRetrievalKeplerRes.response.text = ragText.replace(/\n/g, '<br>');
      this.hallucinateRetrievalKeplerRes.response.bites = bites;
      if (ragText !== '')
        this.callFMApi(ragText, tempStringValue, nemoGaurdrail, true, undefined, true);
      this.getSummarygEval(ragText, page_content);
    },
      error => {
        this.hallucinateRetrievalKeplerRes.status = false;
        this.hallucinateRetrievalKeplerRes.errorMesssage = 'Hallucination API Failed';
      })
  }
  //-------Tranform Text------
  transformText(text: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(text.replace(/\n/g, '<br/>'));
  }
  getSummarygEval(ragText: string, page_content: string) {
    let options = {
      "text": this.prompt,
      "response": ragText,
      "sourcetext": page_content
    };
    // this.http.post("http://100.78.13.150:8000/rai/v1/moderations/gEval",options).subscribe
    this.https.post(this.apiEndpoints.RAG_gEval, options).subscribe(
      (res: any) => {
        this.gEvalres = res;
      },
      error => {
        this.handleError(error)
      }
    );
  }

  // Handles FM Time API calls
  callFMTimeApi(hallucinationPostCall: boolean = false) {
    this.https.get(this.apiEndpoints.fm_api_time).subscribe(
      (res: any) => {
        console.log(res);
        if (hallucinationPostCall) {
          console.log("Hallucination Post Call")
          this.fmTimeApiResult.responseModeration = res.requestModeration;
        } else {
          this.fmTimeApiResult = res
        }
      },
      error => {
        this.handleError(error);
      }
    );
  }

  callNemoApi(prompt: any, nemoGaurdrail: any, summaryStatus: any) {
    if (nemoGaurdrail == true) {
      if (summaryStatus == 'PASSED') {
        this.getModerationfornemo(prompt);
      } else {
        // -----------------------------HANDLE FAILED CASE---------------------
        // this.nemoModerationRailRes = 'UNMODERATED';
        // this.nemoModerationRailStatus = 'FAILED';
        // this.nemoModerationRailTime = 'NA';
      }
    }
  }
  getModerationfornemo(prompt: string) {
    const fileData2 = new FormData();
    fileData2.append('text', prompt);
    this.https.post(this.apiEndpoints.nemo_ModerationRail, fileData2).subscribe(
      (res: any) => {
        console.log(res)
        this.nemoModerationRailRes = res
        console.log("NEMO MODERSTION", res)
        // this.nemoModerationRailRes = res.res;
        // this.nemoModerationRailStatus = res.status;
        // this.nemoModerationRailTime = res.time;
      },
      error => {
        this.handleError(error);
      }
    );
  }

  callNemoCheckApi(apiUrl: string, fileData: any, statusProperty: string, timeProperty: string) {
    this.https.post(apiUrl, fileData).subscribe(
      (res: any) => {
        console.log(res)
        this.nemoChecksApiResponses[statusProperty] = res['status'];
        this.nemoChecksApiResponses[timeProperty] = res['time'];
      },
      error => this.handleError(error)
    );
  }

  // Handles error responses from API calls
  handleError(error: any, customErrorMessage?: any) {
    console.log(error.status);
    console.log(error.error.detail);
    this.spinner = false;
    const message = error.error.details || customErrorMessage || 'API has failed';
    const action = 'Close';
    this.openSnackBar(message, action);
  }

  // Handles the switch for hallucination
  handleHallucinationSwitch() {
    console.log("enableEmbedding::",this.enableEmbedding)
    if (this.enableEmbedding) {
      this.getembeddigns();
      this.hallucinationSwitchCheck = true;
    }else {
      this.hallucinationSwitchCheck = false;
    }
  }
 
  // ---------------PAYLOAD--------------------------
  comp_Payload(text: any, temperature: any, LLMinteraction: any, PromptTemplate: any) {
    const payload = {
      AccountName: 'None',
      PortfolioName: 'None',
      // EmojiModeration: this.selectedEmojiVal,
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: temperature,
      model_name: this.selectedLlmModel,
      translate: this.selectedTranslate,
      LLMinteraction: "yes",
      PromptTemplate: PromptTemplate,
      Prompt: text,
      InputModerationChecks: [
        'PromptInjection',
        'JailBreak',
        'Toxicity',
        'Piidetct',
        'Refusal',
        'Profanity',
        'RestrictTopic',
        'TextQuality',
        'CustomizedTheme',
        "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"
      ],
      OutputModerationChecks: ['Toxicity', 'Piidetct', 'Refusal', 'Profanity', 'RestrictTopic', 'TextQuality', 'TextRelevance', "Sentiment",
        "InvisibleText",
        "Gibberish",
        "BanCode"],
      // llm_BasedChecks: ["randomNoiseCheck", "advancedJailbreakCheck"],
      // llm_BasedChecks: this.hallucinationSwitchCheck ? [] : ["randomNoiseCheck", "advancedJailbreakCheck"],
      llm_BasedChecks: this.llmBased,
      ModerationCheckThresholds: {
        PromptinjectionThreshold: 0.7,
        JailbreakThreshold: 0.7,
        PiientitiesConfiguredToBlock: ['IN_AADHAAR', 'IN_PAN', 'US_PASSPORT', 'US_SSN', "AADHAR_NUMBER",
          "PAN_Number"],
        RefusalThreshold: 0.7,
        ToxicityThresholds: {
          ToxicityThreshold: 0.6,
          SevereToxicityThreshold: 0.6,
          ObsceneThreshold: 0.6,
          ThreatThreshold: 0.6,
          InsultThreshold: 0.6,
          IdentityAttackThreshold: 0.6,
          SexualExplicitThreshold: 0.6,
        },
        ProfanityCountThreshold: 1,
        RestrictedtopicDetails: {
          RestrictedtopicThreshold: 0.7,
          Restrictedtopics: ['Terrorism', 'Explosives','Nudity','Cruelty','Cheating','Fraud','Crime','Hacking','Immoral','Unethical','Illegal','Robbery','Forgery'],
        },
        CustomTheme: {
          Themename: 'string',
          Themethresold: 0.6,
          ThemeTexts: [''],
        },
        SmoothLlmThreshold: {
          input_pertubation: 0.1,
          number_of_iteration: 4,
          SmoothLlmThreshold: 0.6
        },
        // newly added payloads 
        "SentimentThreshold": -0.01,
          "InvisibleTextCountDetails": {
            "InvisibleTextCountThreshold": 1,
            "BannedCategories": [
             "Cf",
              "Co",
              "Cn",
              "So",
              "Sc"
            ]
          },
          "GibberishDetails": {
            "GibberishThreshold": 0.7,
            "GibberishLabels": [
             "word salad",
              "noise",
              "mild gibberish",
              "clean"
            ]
         },
          // "BanCodeThreshold": 0.7
          //  end of new payloads
      },
    };

    return payload;
  }

  // Handles FM Config API calls for non-template-based payload
  payloadFMConfig(response: any, accountName: any, portfolioName: any, tempStringValue: any, prompt: any) {
    accountName = this.selectedAccount;
    portfolioName = this.selectedPortfolio;
    let payload = {
      AccountName: accountName,
      PortfolioName: portfolioName,
      // EmojiModeration: this.selectedEmojiVal,
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: tempStringValue,
      translate: this.selectedTranslate,
      model_name: this.selectedLlmModel,
      LLMinteraction: this.userRoleSettings.llmInteraction,
      // HARD CODE VALUE--------------------------------- NEED TO CHANGE IMPORTANT
      // PromptTemplate: this.selectvalue,
      PromptTemplate: this.selectPromptTemplate,
      Prompt: prompt,
      // Harcoded -- needs to be removed once changes done from Admin side
      // InputModerationChecks: [
      //   "PromptInjection",
      //   "JailBreak",
      //   "Toxicity",
      //   "Piidetct",
      //   "Refusal",
      //   "Profanity",
      //   "RestrictTopic",
      //   "TextQuality",
      //   "CustomizedTheme",
      //   "Sentiment",
      //   "InvisibleText",
      //   "Gibberish",
      //   "BanCode"
      // ],
      // OutputModerationChecks: [
      //   "Toxicity",
      //   "Piidetct",
      //   "Refusal",
      //   "Profanity",
      //   "RestrictTopic",
      //   "TextQuality",
      //   "TextRelevance",
      //   "Sentiment",
      //   "InvisibleText",
      //   "Gibberish",
      //   "BanCode"
      // ],
     InputModerationChecks: response.ModerationChecks,
     OutputModerationChecks: response.OutputModerationChecks,
      // llm_BasedChecks: ["randomNoiseCheck", "advancedJailbreakCheck"],
      // llm_BasedChecks: this.hallucinationSwitchCheck ? [] : ["randomNoiseCheck", "advancedJailbreakCheck"],
      llm_BasedChecks: this.llmBased,
      ModerationCheckThresholds: {
        PromptinjectionThreshold: response.ModerationCheckThresholds.PromptinjectionThreshold,
        JailbreakThreshold: response.ModerationCheckThresholds.JailbreakThreshold,
        PiientitiesConfiguredToDetect: response.ModerationCheckThresholds.PiientitiesConfiguredToDetect,
        PiientitiesConfiguredToBlock: response.ModerationCheckThresholds.PiientitiesConfiguredToBlock,
        RefusalThreshold: response.ModerationCheckThresholds.RefusalThreshold,
        ToxicityThresholds: {
          ToxicityThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ToxicityThreshold,
          SevereToxicityThreshold: response.ModerationCheckThresholds.ToxicityThresholds.SevereToxicityThreshold,
          ObsceneThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ObsceneThreshold,
          ThreatThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ThreatThreshold,
          InsultThreshold: response.ModerationCheckThresholds.ToxicityThresholds.InsultThreshold,
          IdentityAttackThreshold: response.ModerationCheckThresholds.ToxicityThresholds.IdentityAttackThreshold,
          SexualExplicitThreshold: response.ModerationCheckThresholds.ToxicityThresholds.SexualExplicitThreshold,
        },
        ProfanityCountThreshold: response.ModerationCheckThresholds.ProfanityCountThreshold,
        RestrictedtopicDetails: {
          RestrictedtopicThreshold: response.ModerationCheckThresholds.RestrictedtopicDetails.RestrictedtopicThreshold,
          Restrictedtopics: response.ModerationCheckThresholds.RestrictedtopicDetails.Restrictedtopics,
        },
        CustomTheme: {
          Themename: response.ModerationCheckThresholds.CustomTheme.Themename,
          Themethresold: response.ModerationCheckThresholds.CustomTheme.Themethresold,
          ThemeTexts: response.ModerationCheckThresholds.CustomTheme.ThemeTexts,
        },
        SmoothLlmThreshold: {
          input_pertubation: 0.1,
          number_of_iteration: 4,
          SmoothLlmThreshold: 0.6
        },

          // newly added payloads
  SentimentThreshold: response.ModerationCheckThresholds.SentimentThreshold,
  InvisibleTextCountDetails: {
     InvisibleTextCountThreshold: response.ModerationCheckThresholds.InvisibleTextCountDetails.InvisibleTextCountThreshold,
    BannedCategories: response.ModerationCheckThresholds.InvisibleTextCountDetails.BannedCategories,
  },
  GibberishDetails: {
    GibberishThreshold: response.ModerationCheckThresholds.GibberishDetails.GibberishThreshold,
    GibberishLabels: response.ModerationCheckThresholds.GibberishDetails.GibberishLabels,
  },
  // BanCodeThreshold: response.ModerationCheckThresholds.BanCodeThreshold,
  // end of new payloads
      },
    };


    return payload
  }

  // Handles FM Config API calls for template-based payload
  payloadFMConfig_templatebase(response: any, accountName: any, portfolioName: any, tempStringValue: any, prompt: any) {
    accountName = this.selectedAccount;
    portfolioName = this.selectedPortfolio;
    let payload = {
      AccountName: accountName,
      PortfolioName: portfolioName,
      // EmojiModeration: this.selectedEmojiVal,
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: tempStringValue,
      translate: this.selectedTranslate,
      model_name: this.selectedLlmModel,
      LLMinteraction: this.userRoleSettings.llmInteraction,
      // HARD CODE VALUE--------------------------------- NEED TO CHANGE IMPORTANT
      // PromptTemplate: this.selectvalue,
      PromptTemplate: this.selectPromptTemplate,
      Prompt: prompt,
      InputModerationChecks: this.requestTemplateGlobal,
      OutputModerationChecks: this.responseTemplateGlobal,
      // llm_BasedChecks: ["randomNoiseCheck", "advancedJailbreakCheck"],
      // llm_BasedChecks: this.hallucinationSwitchCheck ? [] : ["randomNoiseCheck", "advancedJailbreakCheck"],
      llm_BasedChecks: this.llmBased,
      ModerationCheckThresholds: {
        PromptinjectionThreshold: response.ModerationCheckThresholds.PromptinjectionThreshold,
        JailbreakThreshold: response.ModerationCheckThresholds.JailbreakThreshold,
        PiientitiesConfiguredToDetect: response.ModerationCheckThresholds.PiientitiesConfiguredToDetect,
        PiientitiesConfiguredToBlock: response.ModerationCheckThresholds.PiientitiesConfiguredToBlock,
        RefusalThreshold: response.ModerationCheckThresholds.RefusalThreshold,
        ToxicityThresholds: {
          ToxicityThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ToxicityThreshold,
          SevereToxicityThreshold: response.ModerationCheckThresholds.ToxicityThresholds.SevereToxicityThreshold,
          ObsceneThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ObsceneThreshold,
          ThreatThreshold: response.ModerationCheckThresholds.ToxicityThresholds.ThreatThreshold,
          InsultThreshold: response.ModerationCheckThresholds.ToxicityThresholds.InsultThreshold,
          IdentityAttackThreshold: response.ModerationCheckThresholds.ToxicityThresholds.IdentityAttackThreshold,
          SexualExplicitThreshold: response.ModerationCheckThresholds.ToxicityThresholds.SexualExplicitThreshold,
        },
        ProfanityCountThreshold: response.ModerationCheckThresholds.ProfanityCountThreshold,
        RestrictedtopicDetails: {
          RestrictedtopicThreshold: response.ModerationCheckThresholds.RestrictedtopicDetails.RestrictedtopicThreshold,
          Restrictedtopics: response.ModerationCheckThresholds.RestrictedtopicDetails.Restrictedtopics,
        },
        CustomTheme: {
          Themename: response.ModerationCheckThresholds.CustomTheme.Themename,
          Themethresold: response.ModerationCheckThresholds.CustomTheme.Themethresold,
          ThemeTexts: response.ModerationCheckThresholds.CustomTheme.ThemeTexts,
        },
        SmoothLlmThreshold: {
          input_pertubation: 0.1,
          number_of_iteration: 4,
          SmoothLlmThreshold: 0.6
        }
      },
    };


    return payload
  }

  // Handles Privacy API calls
  callPrivacyAnalyze(payloadAnalyze: any) {
    let privacyAnalyzeApi = this.apiEndpoints.privacyAnalyzeApi;
    this.https.post(privacyAnalyzeApi, payloadAnalyze).subscribe((priAnzRes) => {
      // this.edited = true;
      console.log(priAnzRes)
      this.privacyResponse.AnazRes = priAnzRes
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      // You can access status:
      this.handleError(error);
    })
  }
  // Handles Privacy API calls
  callPrivacyAnonymize(payloadAnon: any) {
    let privacyAnonApi = this.apiEndpoints.privacyAnonApi;
    this.https.post(privacyAnonApi, payloadAnon).subscribe((priAnonRes: any) => {
      // this.edited = true;
      // IMPORTANT NEED TO HANDLE THIS
      // this.sanitizeResponseData();
      // console.log(this.resData)
      this.privacyResponse.AnonRes = priAnonRes;
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      // You can access status:
      console.log(error.status);
      this.handleError(error);
    })
  }
  // Handles Privacy API calls
  callPrivacyEncrypt(payloadEncrypt: any) {
    // this.apiEndpoints.privacyEncrypt= this.apiEndpoints.privacyEncrypt+'?language='+this.language;
    let privacyEncryptapi = this.apiEndpoints.privacyEncrypt;
    this.https.post(privacyEncryptapi, payloadEncrypt).subscribe((priEncrypt) => {
      // this.edited = true;
      console.log(priEncrypt)
      this.privacyResponse.EncryptRes = priEncrypt
      this.spinner = false;
      this.callPrivacyDecrypt(priEncrypt)
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      // You can access status:
      this.handleError(error);
    })
  }
  callPrivacyDecrypt(payloadDecrypt: any) {
    this.https.post(this.apiEndpoints.privacyDecrypt, payloadDecrypt).subscribe((priDecrypt) => {
      // this.edited = true;
      console.log(priDecrypt)

      this.privacyResponse.decryptedtoggle = false
      this.privacyResponse.DecryptRes = priDecrypt
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      // You can access status:
      this.handleError(error);
    })
  }
  @ViewChild('p') p!: NgbPopover;
  @ViewChild('pEmoji') pEmoji!: NgbPopover;
  test(p: any) {
    if (this.p.isOpen()) {
      console.log('Popover is open');
      this.p.toggle();
    } else {
      this.p.toggle();
      console.log('Popover is closed');
    }
  }
  // Handles the emoji popover
  openPopOverEmoji() {
    if (this.pEmoji.isOpen()) {
      console.log('Popover is open');
      this.pEmoji.toggle();
    } else {
      this.pEmoji.toggle();
      console.log('Popover is closed');
    }
  }
  selectedEmojiVal: any = 'no';
  selectedNotification!: string;
  tState = false
  tLoading = false

  // Handles the notification preference
  updateNotificationPreference(f: any, tchoice: any) {

    this.selectedTranslate = tchoice
    if (f.controls['prompt'].value.length != 0) {

      this.tState = false

      if (tchoice == "no") {
        this.tState = false
      } else {
        this.tLoading = true


        // Implement your logic here to handle the change in notification preference
        console.log('Notification Preference updated to:', this.selectedNotification);
        console.log('prompt', f.controls['prompt'].value);
        let payload = {
          "Prompt": f.controls['prompt'].value,
          "choice": tchoice
        }
        this.postTranslateApi(payload)
      }
    } else {
      const message = 'Please enter the prompt';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
    }
  }
  translatedText!: any;
  // Handles the translation API call
  postTranslateApi(payload: any) {
    this.https.post(this.apiEndpoints.Moderationlayer_Translate, payload).subscribe((res: any) => {
      console.log(res)
      this.tState = true
      this.tLoading = false
      this.translatedText = res
    }, error => {
      this.tLoading = false
      this.handleError(error)
    })
  }


  // MULTIMODEL

  multiModel: any = false;
  imagePath: any = ''
  selectedFileName: any = ''
  imgShowUrl: any = ''

  privAnonImgUrl2 = '';
  ocrvalue: string = 'Tesseract';
  portfolioName_value = '';
  accountName_value = '';
  exclusionList_value = '';
  privAnzImgUrl2 = '';
  privAnzOutput = '';
  profImageAnalyse = '';
  analyze: any = '';
  fairness_image: any;
  fairness_response: any;
  imagePromptInjection: any;
  imageJailbreak: any;
  imageRestrictedTopic: any;
  imageFailedCases: any = {
    modelBased: [],
    templateBased: []
  };
  demoFileMultimodel: any = [];
  fileMultiModel: any = '';
  UploadedFile: any;
  selectedFileNameMultiModel: any = '';
  filesMultiModel: any = [];

  // Handles the file selection for multimodel
  resetMultiModelResult() {
    this.analyze = ''
    this.privAnzOutput = ''
    this.imagePromptInjection = '';
    this.imageJailbreak = '';
    this.imageRestrictedTopic = '';
    this.fairness_response = '';
    this.imageFailedCases = {
      modelBased: [],
      templateBased: []
    };
    this.MMImageResponse = '';
    this.MMImageHallucinationScore = '';
    this.MMPdfReference = '';
    this.MMImageCOT = '';
    this.MMImageTHOT = '';
    this.MMImageCOV = '';
    this.MMTimeTaken = '';
  }
  
  // Handles the file selection for multimodel
  showFileTypesSnackbar() {
    const message = 'Supported file types: jpg, jpeg, png, gif, bmp, jfif, mp4, 3gp, wav, mp3, flac, mpeg, pdf (10MB), csv (1MB), txt (400KB)';
      this._snackBar.open(message, '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 6000,
        panelClass: ['le-u-bg-black']
      });
      return;
    
  } 

  // Handles the file selection for multimodel
  fileBrowseHandlerMultiModel(event: any) {
    console.log("FILE HANDLER MULTP MODEL");
    this.prepareFilesListMulti(event.target.files);
    this.demoFileMultimodel = this.filesMultiModel;
    this.fileMultiModel = this.filesMultiModel[0];
    this.UploadedFile = this.filesMultiModel[0];
    this.disabledOptions = [];
    console.log("File Name", this.UploadedFile);
    const files = event.target.files;
  
    if (files[0].type.startsWith('image/') || files[0].type.startsWith('application/') || files[0].type.startsWith('text/') || files[0].type.startsWith('audio/') || files[0].type.startsWith('video/')) {
      this.hallucinationSwitchCheck = true;
    } else {
      this.hallucinationSwitchCheck = false;
    }
  
    if (files[0].type.startsWith('image/')) {
      this.image = true;
    } else {
      this.image = false;
    }
  
    if (files[0].type.startsWith('audio/')) {
      this.audio = true;
    } else {
      this.audio = false;
    }
  
    if (files[0].type.startsWith('video/')) {
      this.video = true;
    } else {
      this.video = false;
    }
    if (files[0].type.startsWith('application/')) {
      this.isPDFFile = true;
    }else {
      this.isPDFFile = false;
    }
  
    const supportedDocTypes = ['application/pdf', 'text/csv', 'text/plain'];
    if ((files[0].type.startsWith('application/') || files[0].type.startsWith('text/')) && !supportedDocTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      this._snackBar.open('Only .pdf, .csv and .txt files are supported', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
      return;
    }
    const supportedImageTypes = ['image/jpg', 'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/jfif'];
    if (files[0].type.startsWith('image/') && !supportedImageTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      this._snackBar.open('Only jpg, jpeg, png, gif, bmp, jfif image types are supported', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
      return;
    }
    const supportedVideoTypes = ['video/mp4', 'video/3gp','video/mpeg'];    if (files[0].type.startsWith('video/') && !supportedVideoTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      this._snackBar.open('Only mp4, 3gp video types are supported', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
      return;
    }
    const supportedAudioTypes = ['audio/wav', 'audio/flac', 'audio/mp3', 'audio/mpeg'];
    if (files[0].type.startsWith('audio/') && !supportedAudioTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      this._snackBar.open('Only wav, mp3 and flac audio types are supported', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
      return;
    }
  
    if (files[0].type.startsWith('text/')) {
      this.disabledOptions = ["Privacy", "Profanity", "Explainability", "Fairness"];
      console.log("Disabled Options", this.disabledOptions);
      this.document = true;
      const fileData = new FormData();
      for (let i = 0; i < this.filesMultiModel.length; i++) {
        const file = this.filesMultiModel[i];
        fileData.append('payload', file);
      }
      this.https.post(this.apiEndpoints.rag_FileUpload, fileData).subscribe(
        (res: any) => {
          this.vectorId = res.id;
          console.log("VID", this.vectorId);
        },
        error => {
          this.handleError(error);
        }
      );
    }
  
    if (files.length > 0) {
      this.selectedFileNameMultiModel = files[0].name;
    }
    const reader = new FileReader();
    this.imagePath = files;
    reader.readAsDataURL(files[0]);
    reader.onload = (_event) => {
      this.imgShowUrl = reader.result;
    }
  }
  
  // Handles the file selection for multimodel
  prepareFilesListMulti(files: Array<any>) {
    // this.filesMultiModel = []; /// made this change so we can add mutiple files 
    // this.demoFile = []; // made this change so we can add multiple files
    for (const item of files) {
      item.progress = 0;
      const reader = new FileReader();
      reader.readAsDataURL(item);
      reader.onload = (_event) => {
        item.preview = reader.result;
        item.type = item.type;
      };
      this.filesMultiModel.push(item);
    }
    this.Placeholder = this.tenantarr.includes('Fairness') ? "Enter Context" : "Enter Prompt";
  }

  // Handles the file removal for multimodel
  removeFileMultimodel(index: any) {
    this.filesMultiModel.splice(index, 1);
    if (this.filesMultiModel.length === 0) {
      this.Placeholder = "Enter Prompt";
      this.hallucinationSwitchCheck = false;
      this.image = false;
      this.audio = false;
      this.video = false;
      this.document = false;
      this.isPDFFile = false;
    }
  }
  // Handles the file removal for multimodel
  resetFileHandlers() {
    this.filesMultiModel = [];
    this.demoFileMultimodel = [];
    this.selectedFileNameMultiModel = '';
    this.imagePath = '';
    this.imgShowUrl = '';
    this.hallucinationSwitchCheck = false;
    this.image = false;
    this.audio = false;
    this.video = false;
    this.document = false;
    this.isPDFFile = false;
    this.disabledOptions = [];
  }

  // Handles the multimodel API call
  callMultimodelTemplateAPI() {
    let templateList = ['Prompt Injection', 'Jailbreak', 'Restricted Topic'];
    // the below code is not being used left for multimodel image template
    // let templateList:any = [] 
    // if (this.selectedUseCaseName == '' || this.selectedUseCaseName == 'Navi') {
    //   if (this.filesMultiModel.length > 0) {
    //     templateList =  ['Prompt Injection', 'Jailbreak', 'Toxicity', 'Profanity', 'Restricted Topic']
    //   }}else{
    //     templateList = this.globalMultiModeltemplateList
    //   }
    // 
    this.fmService.updateMultiModal(true, this.loggedINuserId, templateList, this.prompt, this.filesMultiModel[0]);
    // const formPayload1 = new FormData();
    // formPayload1.append('AccountName', 'None');
    // formPayload1.append('PortfolioName', 'None');
    // formPayload1.append('userid', 'None');
    // formPayload1.append('lotNumber', '1');
    // formPayload1.append('Prompt', this.prompt);
    // formPayload1.append('Image', this.filesMultiModel[0]);
    // formPayload1.append('TemplateName', "Prompt Injection");
    // formPayload1.append('Restrictedtopics', "Terrorism,Explosives");
    // formPayload1.append('model_name', "gpt4O");

    // this.http.post(this.apiEndpoints.multimodal, formPayload1)
    //   .subscribe(response => {
    //     this.imagePromptInjection = response;
    //     if (this.imagePromptInjection?.result == "FAILED") {
    //       this.imageFailedCases.templateBased.push("Image Prompt Injection")
    //     }
    //     console.log("imagePromptInjection", this.imagePromptInjection);
    //   }, error => {
    //     console.log(error)
    //   });

    // const formPayload2 = new FormData();
    // formPayload2.append('AccountName', 'None');
    // formPayload2.append('PortfolioName', 'None');
    // formPayload2.append('userid', 'None');
    // formPayload2.append('lotNumber', '1');
    // formPayload2.append('Prompt', this.prompt);
    // formPayload2.append('Image', this.filesMultiModel[0]);
    // formPayload2.append('TemplateName', "Jailbreak");
    // formPayload2.append('Restrictedtopics', "Terrorism,Explosives");
    // formPayload2.append('model_name', "gpt4O");


    // this.http.post(this.apiEndpoints.multimodal, formPayload2)
    //   .subscribe(response => {
    //     this.imageJailbreak = response;
    //     if (this.imageJailbreak?.result == "FAILED") {
    //       this.imageFailedCases.templateBased.push("Image Jailbreak Check")
    //     }
    //     console.log("imageJailbreak", this.imageJailbreak);
    //   }, error => {
    //     console.log(error)
    //   });


    // const formPayload3 = new FormData();
    // formPayload3.append('AccountName', 'None');
    // formPayload3.append('PortfolioName', 'None');
    // formPayload3.append('userid', 'None');
    // formPayload3.append('lotNumber', '1');
    // formPayload3.append('Prompt', this.prompt);
    // formPayload3.append('Image', this.filesMultiModel[0]);
    // formPayload3.append('TemplateName', "Restricted Topic");
    // formPayload3.append('Restrictedtopics', "Terrorism,Explosives");
    // formPayload3.append('model_name', "gpt4O");


    // this.http.post(this.apiEndpoints.multimodal, formPayload3)
    //   .subscribe(response => {
    //     this.imageRestrictedTopic = response;
    //     if (this.imageRestrictedTopic?.result == "FAILED") {
    //       this.imageFailedCases.templateBased.push("Image Restricted Topic Check")
    //     }
    //     console.log("imageRestrictedTopic", this.imageRestrictedTopic);
    //   }, error => {
    //     console.log(error)
    //   });
  }

  
  fairnessImage(formPayload: any) {
    for (let [key, value] of formPayload.entries()) {
      console.log(`${key}: ${value}`);
    }
    this.https.post(this.fairness_image, formPayload).subscribe((res: any) => {
      this.fairness_response = res;
      this.fmService.updateMultiModalKeyVal('fairnessRes', res)
      if (this.tenantarr.includes('Fairness')) {
        this.spinner = false;
        if (this.activeTab == '') {
          this.changeTab('Fairness');
        }
        this.fairnessRes = res; //For Fairness Result Tab
      }

      console.log("FAIR::" + this.fairness_response);
      if (this.fairness_response['percentage bias score'] > 80) {
        this.imageFailedCases.modelBased.push('Image Fairness Check')
      }
    }, error => {
      if (this.tenantarr.includes('Fairness')) {
        this.handleError(error, 'Fairness API Failed')
      }
    })
  }


  // Handles the multimodel API call
  callMultiModel() {
    const fileData = new FormData();
    this.fileMultiModel = this.filesMultiModel[0];
    fileData.append('magnification', 'false');
    fileData.append('rotationFlag', 'false');
    fileData.append('image', this.fileMultiModel);
    fileData.append('portfolio', this.portfolioName_value);
    fileData.append('account', this.accountName_value);
    fileData.append('exclusionList', this.exclusionList_value);
    let h = {
      Accept: 'application/json',
      'Content-Type': 'multipart/form-data',
    };
    let params = new HttpParams();
    params = params.append('ocr', this.ocrvalue);

    this.privacy_Analyze(fileData, h, params); // privacy based multimodel

    this.profanityImageAnalyse(); // model based multimodel

    this.callMultimodelTemplateAPI(); // template based multimodel

    const formPayload = new FormData();
    formPayload.append('prompt', this.prompt);
    formPayload.append('evaluator', "GPT_4o");
    formPayload.append('image', this.filesMultiModel[0]);

    this.fairnessImage(formPayload); // modelbased multimodel

  }
// Handles the multimodel API call
  privacy_Analyze(fileData: any, h: any, params: any) {
    console.log('Privacy - Analyze');
    this.imageService
      .imgApi(this.privAnzImgUrl2 + '?' + params, fileData, h)
      .subscribe({
        next: (data) => {
          let uniquePII: any = new Set()
          let piiEnt = data?.PIIEntities
          for (let i = 0; i < piiEnt.length; i++) {
            if (piiEnt[i].type != 'my') {
              uniquePII.add(piiEnt[i].type)
            }
          }
          console.log('uniquePII===', uniquePII);
          console.log(piiEnt)
          this.privAnzOutput = uniquePII;
          if (piiEnt.length != 0) {
            this.sharedDataService.updateImageBasedModels("Image Privacy Check","",'modelBased')
            // this.imageFailedCases.modelBased.push('Image Privacy Check')
          }
        },
        error: (error) => {
          console.log("Failed");
        },
      });
  }

  // Handles the multimodel API call
  profanityImageAnalyse() {
    const fileData1 = new FormData();
    this.fileMultiModel = this.filesMultiModel[0];
    fileData1.append('image', this.fileMultiModel);
    if(this.portfolioName_value.length === 0){
      // fileData1.append('portfolio', "");
    }else{
      fileData1.append('portfolio', this.portfolioName_value);

    }
    if(this.accountName_value.length === 0){
      // fileData1.append('account', "");
    }else{
      fileData1.append('account', this.accountName_value);
    }
    fileData1.append('accuracy','high');
    this.https.post(this.profImageAnalyse, fileData1).subscribe(
      (data: any) => {
        this.analyze = data.analyze;
        if (
          this.analyze?.hentai > 0.3 ||
          this.analyze?.porn > 0.3 ||
          this.analyze?.sexy > 0.3 ||
          this.analyze?.neutral > 1 ||
          this.analyze?.drawings > 1
        ) {
          // this.imageFailedCases.modelBased.push("Image Safety Check");
          this.sharedDataService.updateImageBasedModels("Image Safety Check","",'modelBased')
        }
        console.log('this.safetydata===', this.analyze);
      },
      (error: any) => {
        console.log("Failed");
      }
    );
  }

  // Handles the dialog opening for different file types 
  openDialog(data: any) {
    console.log("DialogData", data);

    if (data.startsWith('data:application/pdf;base64,')) {
      this.dialog.open(ImageDialogComponent, {
        data: { pdf: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else if (data.startsWith('data:image/')) {
      this.dialog.open(ImageDialogComponent, {
        data: { image: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else if (data.startsWith('data:text/csv;base64,')) {
      this.dialog.open(ImageDialogComponent, {
        data: { csv: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else if (data.startsWith('data:text/plain;base64,')) {
      this.dialog.open(ImageDialogComponent, {
        data: { plainText: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else if (data.startsWith('data:video/')) {
      this.dialog.open(ImageDialogComponent, {
        data: { video: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else if (data.startsWith('data:audio/')) {
      this.dialog.open(ImageDialogComponent, {
        data: { audio: data, flag: true },
        backdropClass: 'custom-backdrop'
      });
    } else {
      console.error('Unsupported data type');
    }
  }

  isCollapsed: boolean = false;

  togglePanel(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  // Handles the selection of portfolio and account
  getSelectedValues(): void {
    this.selectedPortfolio = localStorage.getItem('selectedPortfolio') ?? '';
    this.selectedAccount = localStorage.getItem('selectedAccount') ?? '';
    console.log('Selected Portfolio:', this.selectedPortfolio);
    console.log('Selected Account:', this.selectedAccount);
  }
}

