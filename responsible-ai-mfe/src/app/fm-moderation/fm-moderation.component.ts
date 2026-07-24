/** MIT
Copyright 2025 - 2026 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpHeaders, HttpParams } from '@angular/common/http';
import { Component, ViewChild, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { FmModerationService } from '../services/fm-moderation.service';
import { catchError, map, throwError, Subject, takeUntil } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { RoleManagerService } from '../services/role-maganer.service';
import { SharedDataService } from '../services/shared-data.service';
import { NgbPopover } from '@ng-bootstrap/ng-bootstrap';
import { ImageService } from '../image/image.service';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { FormControl } from '@angular/forms';
import { NonceService } from '../nonce.service';
import { UserValidationService } from '../services/user-validation.service';
import {
  PrivacyAnalyzePayload,
  PrivacyAnonymizePayload,
  PrivacyEncryptPayload,
  ProfanityPayload,
  ExplainabilityPayload,
  COVPayload,
  FairnessPayload,
  LLMEvalPayload,
  OpenAIPayload,
  RAGRetrievalPayload,
  GEvalPayload,
  NemoCheckPayload,
  UserRolePayload,
  EmbeddingPayload,
  SummaryEvalPayload
} from '../services/interfaces/fm-moderation.interface';

@Component({
  selector: 'app-fm-moderation',
  templateUrl: './fm-moderation.component.html',
  styleUrls: ['./fm-moderation.component.css']
})
export class FmModerationComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ====== UI STATE VARIABLES ======
  isLoadingSelectType: boolean = true;
  isLoadingPrompt: boolean = true;
  spinner: boolean = false;
  activeTab: string = '';
  isCollapsed: boolean = false;
  panelOpenState: boolean = false;
  isLoadingMMImage: boolean = false;
  isLoadingCOV: boolean = false;

  // ====== FORM CONTROLS ======
  selectedAccount: string = '';
  selectedPortfolio: string = '';
  Placeholder: string = 'Enter Prompt (supports prompt with emojis also)';
  tempValue: number = 0;
  prompt: any = '';
  selectedLlmModel: any = 'gpt4';
  selectedTranslate: any = 'no';
  selectCoveComplexity: any = 'simple';
  selectPromptTemplate: any = 'GoalPriority';
  selectedExplainabilityModel: string = 'gpt-4o';
  explainabilityOption: string = 'LLM';
  selectedEmojiVal: any = 'no';
  selectedNotification!: string;
  ocrvalue: string = 'Tesseract';
  fairnessEvaluator: any = '';

  // ====== SWITCHES AND FLAGS ======
  hallucinationSwitchCheck: boolean = false;
  LiteRAGSwitchCheck: boolean = false;
  nemoGaurdrailCheck: boolean = false;
  roleMlChecked: boolean = false;
  roleML: boolean = false;
  fmlocalselected: boolean = false;
  submitFlag: boolean = false;
  optionFlag: boolean = false;
  coupledModeration: boolean = false;
  useCaseSelectedFlag: boolean = false;
  customApipayloadStatus: boolean = false;
  multiModel: any = false;
  tState = false;
  tLoading = false;
  setLoadTemplateResMod: boolean = false;
  enableSearch = false;

  // ====== API ENDPOINTS ======
  apiEndpoints: any = {};

  // ====== USER AND ROLE SETTINGS ======
  roles: any;
  loggedINuserId: any;
  userRoleSettings: any = {
    openAiStatusasperUserRole: '',
    selfReminder: '',
    llmInteraction: '',
  };

  // ====== OPTIONS AND SELECTIONS ======
  tenantarr: any = [];
  optionarr: any = [];
  selectedOptions: any = [];
  options: any = ["Privacy", "Profanity", "FM-Moderation", "Explainability", "Fairness"];
  disabledOptions: any = [];
  selectUsecaseOptions: any = ["Demo", "Navi"];
  exclusionList: any = [];
  portfolioName: any = '';
  accountName: any = '';
  enableEmbedding: boolean = false;

  // ====== MODEL CONFIGURATIONS ======
  Models: any = [
    { name: "GPT-4o", value: "gpt4" },
    { name: "GPT-3", value: "gpt3" },
    { name: "AWS Anthropic", value: "AWS_CLAUDE_V3_5" },
    { name: "LLAMA", value: "Llama3-70b" },
    { name: "GEMINI-2.5-FLASH", value: "Gemini-Flash" },
    { name: "GEMINI-2.5-PRO", value: "Gemini-Pro" },
  ];
  llmBased: any = [];
  explainabilityModels: any = [
    { name: "GEMINI-2.5- FLASH", value: "gemini-flash" },
    { name: "GEMINI-2.5-PRO", value: "gemini-pro" },
    { name: "AWS Anthropic", value: "aws" },
    { name: "GPT-4o", value: "gpt-4o" }
  ];
  fairnessEvaluators = [
    { name: 'GPT-4o', value: 'GPT_4' },
    { name: 'LLAMA', value: 'LLAMA' },
    { name: 'GEMINI-2.5-FLASH', value: 'GEMINI_2.5_FLASH' },
    { name: 'GEMINI-2.5-PRO', value: 'GEMINI_2.5_PRO' },
    { name: 'AWS Anthropic', value: 'AWS' },
  ];

  // ====== FILE HANDLING ======
  vectorId: any;
  fileupload: boolean = true;
  document: boolean = false;
  image: boolean = false;
  audio: boolean = false;
  video: boolean = false;
  isPDFFile: boolean = false;
  files: any = [];
  filesExplainability: any = [];
  demoFile: any = [];
  demoFile1: any = [];
  ExplanabilityFileId: any;
  ExplanabilityFileName: any = '';
  file: any;
  selectedEmbeddedFileName: any = '';
  selectedEmbeddedFileId: any;
  bulkRagId: any;
  dataCuratorMsg: string = '';

  // ====== MULTIMODAL HANDLING ======
  MMImageUrl: string = '';
  MMAudioUrl: string = '';
  MMVideoUrl: string = '';
  MMPdfUrl: string = '';
  MMImageTHOT: any;
  MMImageCOV: any;
  MMImageCOT: any;
  MMImageHallucinationScore: any;
  MMImageResponse: any;
  MMPdfReference: any;
  MMTimeTaken: any;
  lightRagRes: any = '';
  translatedText!: any;
  imagePath: any = '';
  selectedFileName: any = '';
  imgShowUrl: any = '';
  demoFileMultimodel: any = [];
  fileMultiModel: any = '';
  UploadedFile: any;
  selectedFileNameMultiModel: any = '';
  filesMultiModel: any = [];
  RagMultimodal: any = ["jpg", "jpeg", "png", "gif", "bmp", "jfif"];
  RagMultiVideo: any = ["mp4", "3gp"];
  RagMultiFiles: any = [];

  // ====== SCORING AND METRICS ======
  faithfulnessScore: any;
  relevanceScore: any;
  adhernceScore: any;
  correctnessScore: any;
  averageScore: any;
  faithfulness: any;
  relevance: any;
  adhernce: any;
  correctness: any;

  // ====== API RESPONSES AND RESULTS ======
  RKRes: any = '';
  openAIRes: any = {};
  COTRes: any = {};
  THOTRes: any = {};
  privacyResponse: any = {};
  profanityRes: any = {};
  explainabilityRes: any = {};
  fairnessRes: any = {};
  coupledModerationRes: any = {};
  nemoModerationRailRes: any = {};
  nemoChecksApiResponses: any = {};
  covResponse: any;
  allEmbeddingsRes: any = [];
  hallucinateRetrievalKeplerRes: any = {
    status: false,
    errorMesssage: '',
    response: {}
  };
  lightRag: any = {
    status: false,
    errorMessage: '',
    response: {}
  };
  gEvalres: any = {};
  hallucinationResModerationData: any = {};
  llmEvalRes: any = {
    selectedOption: '',
    response: []
  };
  fmTimeApiResult: any = {
    OpenAIInteractionTime: '',
    requestModeration: '',
    responseModeration: ''
  };

  // ====== PRIVACY SETTINGS ======
  privacyOption: string = 'Choose Options';
  nlpOption: any = '';
  piiEntitiesToBeRedactedOption = new FormControl([]);
  privacy_options: string[] = ["Privacy-Analyze", "Privacy-Anonymize", "Privacy-Encrypt", "Privacy-Highlight"];
  available_Recognizers: any[] = [];
  nlp_options: { viewValue: string; value: string }[] = [
    { viewValue: 'Spacy-wb-lg (Basic)', value: 'basic' },
    { viewValue: 'Spacy-wb-trf (Good)', value: 'good' },
    { viewValue: 'PIIRanha (Medium)', value: 'ranha' },
    { viewValue: 'Roberta (High)', value: 'roberta' }
  ];
  nlptooltip = `Spacy-wb-lg (low accuracy & faster response),\n
  Spacy-wb-trf (medium accuracy & faster response) - Recommended,\n
  Roberta (high accuracy & slower response),\n
  PIIRanha (medium accuracy & medium response)`;
  Language_options: string[] = ["en", "fr"];

  // ====== STATE MANAGEMENT ======
  covState: any = {
    active: false,
    hallucination: false,
    payload: {}
  };
  cotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  };
  thotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  };
  tokenImpState: any = {
    active: false,
    payload: {}
  };
  gotState: any = {
    active: false,
    payload: {}
  };
  llmExplainState: any = {
    active: false,
    payload: {}
  };
  contentDetectorState: any = {
    active: false,
    propmt: ''
  };
  serperResponseState: any = {
    model: this.selectedLlmModel,
    payload: {}
  };

  // ====== TEMPLATE AND PAYLOAD MANAGEMENT ======
  llmEvalPayload: any = {
    AccountName: "None",
    PortfolioName: "None",
    userid: "None",
    lotNumber: 1,
    Prompt: this.prompt,
    model_name: this.selectedLlmModel,
    temperature: this.tempValue.toString(),
    PromptTemplate: this.selectPromptTemplate,
  };
  requestModerationTemplates: any = [];
  responseModerationTemplates: any = [];
  templateBasedPayload: any = {
    status: false,
  };
  allTemplates: any = [];
  requestTemplateGlobal = [];
  responseTemplateGlobal = [];
  globalMultiModeltemplateList: any = [];
  globalMultiEvaltemplateList: any = [];

  // ====== RECOMMENDATION SYSTEM ======
  res: any;
  recommandedKey: any = [];
  displayedKeys: any = [];
  showAll = false;
  recommendedContent: any;
  recommend: any = true;
  promptTest: any = '';
  recommendDrop = false;
  selectedButton!: any;
  isListVisible = true;

  // ====== EXPLAINABILITY VARIABLES ======
  private COVUrl: any;
  covFinalAnswer: any;
  finalAnswer: string = '';
  COVAnswer: string = '';
  COVTimeTaken: any;
  tooltipContent: any;

  // ====== IMAGE PROCESSING ======
  privAnonImgUrl2 = '';
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

  // ====== DEPRECATED/LEGACY VARIABLES ======
  portfolioName_value = '';
  accountName_value = '';
  exclusionList_value = '';
  selectedUseCaseName: any = '';
  gibrishDisplayLabels = [];
  bannedCategoriesDisplay = [];
  filePreview: any = '';

  // ====== VIEW CHILD REFERENCES ======
  @ViewChild('p') p!: NgbPopover;
  @ViewChild('pEmoji') pEmoji!: NgbPopover;

  constructor(private imageService: ImageService,
    public roleService: RoleManagerService,
    private sharedDataService: SharedDataService,
    private sanitizer: DomSanitizer,
    public fmService: FmModerationService,
    public _snackBar: MatSnackBar,
    public dialog: MatDialog,
    public nonceService: NonceService,
    private validationService: UserValidationService,
    private cdRef: ChangeDetectorRef) { }

  // ====== LIFECYCLE METHODS ======
  
  ngOnInit(): void {
    this.roles = this.roleService.getLocalStoreUserRole()
    this.options = this.roleService.getSelectedTypeOptions("Workbench", "Unstructured-Text", "Generative-AI")
    // FOR HACKATHON
    this.settingSelectOptions();

    this.fmService.fetchApiUrl();

    this.CallGetTemplates();
    let { ip_port, Account_Role } = this.retrieveLocalStorageData();

    this.setApiList(ip_port);
    this.initializeUserRole(Account_Role);

    // set timeout for is loading
    this.isLoadingSelectType = false;
    this.isLoadingPrompt = false;

    this.selectedNotification = 'None';

    this.getRecommmendation();
    this.getRecognizers()

    this.bulkRagId = sessionStorage.getItem('vectorId');
    sessionStorage.removeItem('vectorId');
    this.assignBulkValue();
  }

  ngAfterViewInit() {
    const tooltipDiv = document.getElementById('tooltip-content');
    if (tooltipDiv) {
      this.tooltipContent = tooltipDiv.innerHTML;
    }
  }

  // ====== INITIALIZATION & SETUP METHODS ======
  
  // Assigns bulk values for FM moderation
  assignBulkValue() {
    // making FM moderation checked by deafult
    this.tenantarr.push("FM-Moderation");
    this.selectedOptions["FM-Moderation"] = true;

    if (this.bulkRagId !== '' && this.bulkRagId !== undefined && this.bulkRagId !== null) {
      this.document = true;
      this.hallucinationSwitchCheck = true;
      this.fileupload = true;
      let totalFiles = Number(sessionStorage.getItem('totalRagFiles'))
      this.dataCuratorMsg = 'Uploaded with ' + totalFiles + ' RAG file' + (totalFiles > 1 ? 's' : '') + ' from Data Curator';
      this.openSnackBar(this.dataCuratorMsg, '✖');
      sessionStorage.removeItem('totalRagFiles');
    }
    else {
      this.dataCuratorMsg = '';
      this.document = false;
      this.hallucinationSwitchCheck = false;
    }
  }

  // FOR HACKATHON ONLY
  settingSelectOptions() {
    if (this.roles == 'ROLE_ML') {
      this.options = ["FM-Moderation"];
      this.selectedOptions["FM-Moderation"] = true;
      this.roleMlChecked = true;
      this.viewoptions();
    }
  }

  // ====== DATA RETRIEVAL & API SETUP METHODS ======
  
  // Fetches templates for moderation
  CallGetTemplates() {
    this.fmService.getTemplates().pipe(takeUntil(this.destroy$)).subscribe(
      (res: any) => {
        this.allTemplates = res?.accList?.sort((a: any, b: any) => a.portfolio.localeCompare(b.portfolio));
      },
      error => {
        this.handleError(error);
      }
    );
  }

  // Fetches available recognizers for privacy checks
  getRecognizers() {
    this.fmService.getRecognizers().pipe(takeUntil(this.destroy$)).subscribe(
      (response: any) => {
        const availableRecognizers = response['Available Recognizers'];
        this.available_Recognizers = availableRecognizers;
      },
      (error) => {
        this.handleError(error);
      }
    );
  }

  // Fetches recommendations for prompts
  getRecommmendation() {
    this.fmService.getRecommendations().pipe(takeUntil(this.destroy$)).subscribe(
      (data) => {
        this.res = data;
        this.recommandedFiles();
      },
      (error) => {
        this.handleError(error);
      }
    );
  }

  // Populates the list of recommended files
  recommandedFiles() {
    Object.keys(this.res.prompts).forEach((key) => {
      if (this.res.prompts[key].length > 0) {
        this.recommandedKey.push(key);
      }
    });
    this.displayedKeys = this.recommandedKey.slice(0, 3);
  }

  // Get Initial Embeddings for Hallucination
  getembeddigns() {
    const payload: EmbeddingPayload = { userId: this.loggedINuserId.toString() };
    this.fmService.getEmbeddings(payload).pipe(takeUntil(this.destroy$)).subscribe(
      (res: any) => {
        this.allEmbeddingsRes = res;
      }, error => {
        this.handleError(error);
      })
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
      }
    }
    this.loggedINuserId = this.validationService.getLogedInUser();
    return { ip_port, Account_Role };
  }

  // Sets the API endpoints based on the configuration
  setApiList(ip_port: any) {
    this.privAnzImgUrl2 = ip_port.result.Privacy + ip_port.result.Privacy_image_analyze;
    this.profImageAnalyse = ip_port.result.Profanity + ip_port.result.Profan_Image_Analyse;
    this.fairness_image = ip_port.result.Fairness + ip_port.result.FairnessImage;
    this.apiEndpoints.nemo_TopicalRail = ip_port.result.Nemo + ip_port.result.Nemo_TopicalRail;
    this.apiEndpoints.nemo_JailBreakRail = ip_port.result.Nemo + ip_port.result.Nemo_JailBreakRail;
    this.apiEndpoints.nemo_FactCheckRail = ip_port.result.Nemo + ip_port.result.Nemo_FactCheckRail;
    this.MMImageUrl = ip_port.result.Rag + ip_port.result.MMImageUrl;
    this.MMAudioUrl = ip_port.result.Rag + ip_port.result.MMAudioUrl;
    this.MMVideoUrl = ip_port.result.Rag + ip_port.result.MMVideoUrl;
    this.MMPdfUrl = ip_port.result.Rag + ip_port.result.MMPdfUrl;
  }

  // Initializes user role settings
  initializeUserRole(Account_Role: any) {
    const payload: UserRolePayload = { role: Account_Role };
    
    this.fmService.getUserRole(payload).pipe(takeUntil(this.destroy$)).subscribe(
      (res) => {
        this.userRoleSettings.openAiStatusasperUserRole = res.isOpenAI;
        this.userRoleSettings.selfReminder = res.selfReminder;
        this.userRoleSettings.llmInteraction = res.isOpenAI ? 'yes' : 'no';
      },
      error => {
        if (error.status == 430) {
          const message = error.error.detail;
          this.openSnackBar(message, '✖');
        } else {
          let message
          if (error.status === 500) {
            message = "Internal Server Error. Please try again later.";
          } else {
            message = error.error.detail || error.error.message || "API has failed";
          }
          this.openSnackBar(message, '✖');
        }
      });
  }

  // Fetches templates for moderation


  // ====== USER INTERFACE & NAVIGATION METHODS ======
  
  // Changes the active tab
  changeTab(tab: string) {
    this.activeTab = tab;
  }

  // Sets the flag for loading template-based moderation
  setLoadTemplateResModTrue() {
    this.setLoadTemplateResMod = true;
  }

  // Updates the tenant array based on selected options
  viewoptions() {
    const myObject = { ...this.selectedOptions };
    const filteredKeys = this.filterKeysByBoolean(myObject);
    this.tenantarr = filteredKeys;
    if (this.tenantarr.includes('Fairness') && this.filesMultiModel.length > 0) {
      this.Placeholder = "Enter Context";
    } else {
      this.Placeholder = "Enter Prompt";
    }
    if (!(this.tenantarr.includes('FM-Moderation'))) {
      this.hallucinationSwitchCheck = false; // file upload needs to be reset if fm not in list
      this.coupledModeration = false;
      this.enableEmbedding = false;
    }
    if ((this.tenantarr.includes('FM-Moderation'))) {
      this.coupledModeration = true;
    }
  }

  // Toggles the visibility of all recommended keys
  toggleShowAll() {
    this.showAll = true;
    this.displayedKeys = this.recommandedKey;
  }

  // Displays recommended content for a selected button
  showRecommand(btn: any) {
    this.isListVisible = true;
    this.recommendedContent = this.res.prompts[btn];
    this.recommendDrop = true;
    this.selectedButton = btn;
  }

  // Adds a recommended prompt to the input field
  addToPrompt(data: any) {
    this.isListVisible = false;
    this.prompt = data;
    this.promptTest = data;
  }

  // Selects an embedded method for file processing
  selectEmbeddedMethod(data: any) {
    this.files = []
    this.RagMultiFiles = [];
    let selectedOption = data.options[data.options.selectedIndex];
    this.selectedEmbeddedFileName = selectedOption.value;
    this.selectedEmbeddedFileId = selectedOption.id;
  }

  // Opens a snackbar with a message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // ====== UTILITY METHODS ======
  
  // Filters keys from an object based on their boolean values
  filterKeysByBoolean(obj: Record<string, boolean>): string[] {
    return Object.keys(obj).filter((key) => obj[key]);
  }

  // Setting local flag value
  SettingValue(): void {
    this.fmlocalselected = true;
  }

  // Handles the selection of portfolio and account
  getSelectedValues(): void {
    this.selectedPortfolio = localStorage.getItem('selectedPortfolio') ?? '';
    this.selectedAccount = localStorage.getItem('selectedAccount') ?? '';
  }

  // ====== FORM HANDLING & BUSINESS LOGIC METHODS ======
  
  // Handles the form submission
  onSubmit(formData: any) {
    this.getSelectedValues();
    if (this.tenantarr == undefined || this.tenantarr.length == 0) {
      const message = 'Please select Select Type';
      this.openSnackBar(message, '✖');
      return;
    }
    if (this.tenantarr.includes('Fairness') && this.fairnessEvaluator.length == 0) {
      const message = 'Please select Evaluator for fairness';
      this.openSnackBar(message, '✖');
      return;
    }

    this.optionarr = this.tenantarr;
    this.optionFlag = true;
    if ((this.tenantarr.includes('FM-Moderation'))) {
      this.coupledModeration = true;
      this.submitFlag = true
    } else {
      this.submitFlag = false
    }

    // Rempoving the template Bsased Responses from Service
    this.sharedDataService.clearResponses();
    this.setLoadTemplateResMod = false;

    let { hallucinationSwitch, nemoGaurdrail, selectedUsecase, prompt, temp, llmAsEvaluatorSwitch } = formData.value;
    let accountName = this.selectedAccount;
    let portfolioName = this.selectedPortfolio;
    this.prompt = prompt;
    this.selectedUseCaseName = selectedUsecase;
    this.resetResultData()
    // MULTIMODEL
    if (this.tenantarr.includes('FM-Moderation') && this.filesMultiModel.length > 0 && this.image == true) {
      this.callMultiModel()
    }

    // text based templates checks 
    if (selectedUsecase == '' || selectedUsecase == 'Navi') {
      if (this.filesMultiModel.length > 0) {
        this.requestModerationTemplates = ["Prompt Injection Check", "Jailbreak Check", "Language Critique Coherence Check", "Language Critique Fluency Check", "Language Critique Grammar Check", "Language Critique Politeness Check"]

      } else {
        this.requestModerationTemplates = ["Prompt Injection Check", "Jailbreak Check", "Fairness and Bias Check", "Language Critique Coherence Check", "Language Critique Fluency Check", "Language Critique Grammar Check", "Language Critique Politeness Check"] //imp
      }
      this.responseModerationTemplates = ["Response Completeness Check", "Response Conciseness Check", "Response Language Critique Coherence Check", "Response Language Critique Fluency Check", "Response Language Critique Grammar Check", "Response Language Critique Politeness Check"]
      this.templateBasedPayload.userid = "None"
      if (selectedUsecase == 'Navi') {
        this.callEvalLLMNavi(prompt, 'Navi Tone Correctness Check');
      }
    }

    if (this.tenantarr.includes('FM-Moderation') && hallucinationSwitch && this.selectedEmbeddedFileName == '') {
      const message = 'Please select the embeddings';
      this.openSnackBar(message, '✖');
      return;
    }
    this.llmEvalPayload = {
      AccountName: accountName,
      PortfolioName: portfolioName,
      userid: "None", // KEEPINH "NONE" AS ITS NOT WORKING WITH USERIDS
      lotNumber: 1,
      Prompt: this.prompt,
      model_name: this.selectedLlmModel,
      temperature: this.tempValue.toString(),
      PromptTemplate: this.selectPromptTemplate,
    }

    if (!prompt || !prompt.trim()) {
      const message = 'Please enter the prompt';
      this.openSnackBar(message, '✖');
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
        this.customApipayloadStatus = false
        if (!hallucinationSwitch) {
          if (!this.userRoleSettings.openAiStatusasperUserRole) { //-------------IF OPENAI IS FALSE----------------
            this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch);
          } else if (this.userRoleSettings.openAiStatusasperUserRole) {
            this.callFMApi(prompt, tempStringValue, nemoGaurdrail, hallucinationSwitch)
            if (!this.roleML) {
              this.covState = {
                active: this.useCaseSelectedFlag ? false : true,
                payload: {
                  text: prompt,
                  complexity: this.selectCoveComplexity,
                  model_name: this.selectedLlmModel
                }
              }
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
        if (nemoGaurdrail) {
          const fileData = new FormData();
          fileData.append('text', prompt);
          this.callNemoCheckApi(this.apiEndpoints.nemo_TopicalRail, fileData, 'nemoTopicalRailStatus', 'nemoTopicalRailTime');
          this.callNemoCheckApi(this.apiEndpoints.nemo_JailBreakRail, fileData, 'nemoJailbreakCheckStatus', 'nemoJailbreakCheckTime');
          this.callNemoCheckApi(this.apiEndpoints.nemo_FactCheckRail, fileData, 'nemoFactcheckRailStatus', 'nemoFactcheckRailTime');
        }
      } else {
        const configPayload = {
          AccountName: accountName,
          PortfolioName: portfolioName,
        };
        this.callFMConfigApi(configPayload, accountName, portfolioName, tempStringValue, prompt        ).subscribe(
          ({ response, comp_Payload }) => {
            if (!hallucinationSwitch) {
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
            inputPrompt: prompt,
            modelName: "GPT"
          }
        }
        this.gotState = {
          active: this.useCaseSelectedFlag ? false : true,
          payload: {
            inputPrompt: prompt,
            modelName: 'gpt-35-turbo'
          }
        }
        this.llmExplainState = {
          active: this.useCaseSelectedFlag ? false : true,
          payload: {
            inputPrompt: prompt
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
      const payload: RAGRetrievalPayload = {
        fileupload: true,
        text: this.prompt,
        llmtype:"openai",
        embeddingmodel:"local",
        vectorstoreid: this.vectorId ? this.vectorId : this.bulkRagId ? this.bulkRagId : null
      };
      this.hallucinateRetrievalKeplerRes.status = true;
      this.fmService.callRAGRetrieval(payload).subscribe(
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
          this.handleError(error);
          this.hallucinateRetrievalKeplerRes.status = false;
          this.hallucinateRetrievalKeplerRes.errorMesssage = 'Hallucination API Failed';
        }
      );

    }
    if (this.image == true) {
      this.MultimodalMethod(this.MMImageUrl);
    }
    if (this.audio == true) {
      this.MultimodalMethod(this.MMAudioUrl);
    }
    if (this.video == true) {
      this.MultimodalMethod(this.MMVideoUrl);
    }
    if(this.LiteRAGSwitchCheck){
        this.callLiteRAG();
      }
  }

  // ====== API CALL METHODS ======
  
  // Calls the LiteRAG API
  callLiteRAG() {
    this.lightRagRes = '';
    const fileData = this.fmService.createFileFormData(this.filesMultiModel, { text: this.prompt });
    this.lightRag.status = true;
    this.fmService.callLightRAG(fileData).subscribe((res: any) => {
      if (res && Array.isArray(res)) {
        res.forEach((item: any) => {
          if (item && item[0] && item[0].Response) {
            this.lightRagRes += item[0].Response + "\n";
          }
          if (item && item[0] && item[0].Hallucination_score) {
            this.lightRag.response.hallScore = item[0].Hallucination_score;
          }
          if (item && item[0] && item[0]['GEval Metrics']) {
            this.lightRag.response.GEval = item[0]['GEval Metrics'];
          }
          if (item && item[0] && item[0]['Time Taken']) {
            this.lightRag.response.timeTaken = item[0]['Time Taken'];
          }
        });
        this.lightRag.response.text = this.lightRagRes.replace(/\n/g, '<br>');
        this.callFMApi(this.lightRag.response.text, '0', false, true, undefined, true);
      }
    })
  }

  // Handles multimodal file uploads
  MultimodalMethod(url: any) {
    this.MMImageResponse = '';
    this.isLoadingMMImage = true;

    //const formData = this.fmService.createFileFormData(this.filesMultiModel, { text: this.prompt });
   const formData = new FormData();
   for (let i = 0; i < this.filesMultiModel.length; i++) {
    const file = this.filesMultiModel[i];
    formData.append('file', file);
  }
    formData.append('text', this.prompt);
    formData.append('cov_complexity',"medium");
    formData.append('llmtype',"openai");
    this.fmService.callMultimodal(url, formData)
      .subscribe((response: any) => {
        this.isLoadingMMImage = false;

        if (this.isPDFFile) {
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
          } else {
            this.faithfulness = 'Invalid response format';
            this.relevance = 'Invalid response format';
            this.adhernce = 'Invalid response format';
            this.correctness = 'Invalid response format';
          }
          if (response && response[7] && response[7][0] && response[7][0]["Time Taken"]) {
            this.MMTimeTaken = response[7][0]["Time Taken"];
          }
        }
        else {
          if (response && response[0] && response[0][0] && response[0][0].response) {
            this.MMImageResponse = response[0][0].response[0].replace(/\n/g, '<br>');
            this.callFMApi(this.MMImageResponse, '0', false, true, undefined, true);
          } else {
            this.MMImageResponse = 'Invalid response format';
          }
          if (response && response[1] && response[1].hallucinationScore !== undefined) {
            this.MMImageHallucinationScore = response[1].hallucinationScore;
          } else {
            this.MMImageHallucinationScore = 'Invalid response format';
          }
          if (response && response[2] && response[2][0] && response[2][0]["chainOfThoughtsResponse"]) {
            this.MMImageCOT = response[2][0]["chainOfThoughtsResponse"][0].replace(/\n/g, '<br>');
          } else {
            this.MMImageCOT = 'Invalid response format';
          }

          if (response && response[3] && response[3][0] && response[3][0]["threadOfThoughtsResponse"]) {
            this.MMImageTHOT = response[3][0]["threadOfThoughtsResponse"][0].replace(/\n/g, '<br>');
          } else {
            this.MMImageTHOT = 'Invalid response format';
          }

          if (response && response[4] && response[4][0] && response[4][0]["chainOfVerificationResponse"]) {
            this.MMImageCOV = response[4][0]["chainOfVerificationResponse"][0].replace(/\n/g, '<br>');
          } else {
            this.MMImageCOV = 'Invalid response format';
          }

          if (response && response[5] && response[5][0] && response[5][0]["gEvalMetrics"]) {
            const metrics = response[5][0]["gEvalMetrics"][0];
            this.faithfulnessScore = metrics.faithfulness;
            this.relevanceScore = metrics.relevance;
            this.adhernceScore = metrics.adherance;
            this.correctnessScore = metrics.correctness;
            this.averageScore = metrics.AverageScore;

            const definitions = response[5][0]["gEvalMetrics"][1];
            this.faithfulness = definitions.faithfulness;
            this.relevance = definitions.relevance;
            this.adhernce = definitions.adherance;
            this.correctness = definitions.correctness;
          } else {
            this.faithfulness = 'Invalid response format';
            this.relevance = 'Invalid response format';
            this.adhernce = 'Invalid response format';
            this.correctness = 'Invalid response format';
          }
          if (response && response[6] && response[6][0] && response[6][0]["Time Taken"]) {
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

  // ====== DATA RESET & FORM UTILITY METHODS ======
  
  // Resets the form data
  resetData(form: any) {
    this.disabledOptions = []
    this.hallucinationSwitchCheck = false;
    this.enableEmbedding = false;
    this.LiteRAGSwitchCheck = false;
    this.nemoGaurdrailCheck = false;
    this.files = [];
    this.RagMultiFiles = [];
    this.tState = false
    this.selectedTranslate = "no"
    this.selectedNotification = "no"
    this.selectedEmojiVal = "no"
    this.tLoading = false
    this.selectedButton = ''
    this.recommendDrop = false
    form.controls['prompt'].setValue('');
    form.controls['selectedUsecase'].setValue('');
    this.useCaseSelectedFlag = false;
    if (this.roles !== 'ROLE_ML') {
      this.selectedOptions = [];
      this.tenantarr = [];
    }
    this.spinner = false;
    this.resetFileHandlers()
    this.resetResultData()
    this.optionarr = [];
    this.optionFlag = false;
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
    };
    this.cotState = {
      active: false,
      hallucination: false,
      payload: {}
    }
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
      status: false,
      response: {}
    };
    this.lightRag = {
      status: false,
      errorMessage: '',
      response: {}
    }
    this.gEvalres = {};
    this.hallucinationResModerationData = {};
    this.llmEvalRes = {
      selectedOption: '',
      response: []
    }
    this.templateBasedPayload.status = false;
    this.resetMultiModelResult();
  }

  // Handles model selection
  onModelSelect(event: any) {
    this.selectedLlmModel = event?.target.value;
  }

  // Handles template selection
  onTemplateSelect(event: any) {
    if (event?.target.value != 'Navi') {
      let selectedTemplate = this.allTemplates.find((template: any) => template.mapId == event?.target.value);
      if (selectedTemplate.SingleModel) {// if contion for if single model is exists
        if (selectedTemplate.SingleModel && selectedTemplate.SingleModel.Template) {
          this.requestModerationTemplates = selectedTemplate.SingleModel.Template.requestTemplate;
          this.responseModerationTemplates = selectedTemplate.SingleModel.Template.responseTemplate;
          this.templateBasedPayload = {
            AccountName: selectedTemplate.account,
            PortfolioName: selectedTemplate.portfolio,
            userid: "None"
          }
        } else {
          this.requestModerationTemplates = [];
          this.requestModerationTemplates = [];
        }
        if (selectedTemplate.SingleModel && selectedTemplate.SingleModel.Model) {
          this.requestTemplateGlobal = selectedTemplate.SingleModel.Model.requestTemplate;
          this.responseTemplateGlobal = selectedTemplate.SingleModel.Model.responseTemplate;
        } else {
          this.requestTemplateGlobal = [];
          this.responseTemplateGlobal = [];
        }
      }
    }
  }


  // ====== FILE HANDLING METHODS ======
  
  // Handle File Upload For Hallucination
  fileBrowseHandler(imgFile: any) {
    const allowedTypes = ['application/pdf', 'text/csv', 'text/plain'];
    if (!allowedTypes.includes(imgFile.target.files[0].type)) {
      let message = 'Please select a valid file type';
      this.openSnackBar(message, '✖');
    } else {
      this.ExplanabilityFileName = '';
      this.ExplanabilityFileId = '';
      this.demoFile1 = this.filesExplainability;
      this.prepareFilesList1(imgFile.target.files);
    }
  }

  deleteFile1(index: number) {
    if (this.filesExplainability[index]?.progress && this.filesExplainability[index].progress < 100) {
      return;
    }
    this.filesExplainability.splice(index, 1);
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
      this.filesExplainability.push(item);
    }
    this.uploadFilesSimulator1(0);
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
            if (this.filesExplainability[index]?.progress !== undefined) {
              this.filesExplainability[index].progress += 20;
            }
          }
        }, 200);
      }
    }, 1000);
  }

  async callUploadEmbeddedFile1() {
    return new Promise((resolve, reject) => {
      this.fmService.uploadMultipleFiles(this.demoFile1, "openai").subscribe(
        (res: any) => {
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

  removeRagFile() {
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
    const payload: LLMEvalPayload = {
      Prompt: prompt,
      template_name: templateName,
      model_name: this.selectedLlmModel,
      AccountName: this.accountName ? this.accountName : "None",
      PortfolioName: this.portfolioName ? this.portfolioName : "None",
      userid: "None", // keep "none" as its working only with none & not userids
      lotNumber: 1,
      Context: "None",
      Concise_Context: "None",
      Reranked_Context: "None",
      temperature: this.tempValue.toString(),
      PromptTemplate: this.selectPromptTemplate,
    }
    this.sharedDataService.updateNaviTonemoderationRes("status", 'LOADING');
    this.fmService.callLLMEval(payload).subscribe(
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
      piiEntitiesToBeRedacted: null as string[] | null,
      nlp: null as string | null,
      fakeData: false,
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
      payloadEncrypt.nlp = this.nlpOption;
    }

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
  }
  
  resetPrivacyResult() {
    this.privacyResponse = {};
  }

  // Handles Profanity API calls
  callProfanityAPI(prompt: any) {
    const payload: ProfanityPayload = {
      inputText: prompt,
      user: this.loggedINuserId
    }
    
    this.fmService.callProfanityAnalyze(payload).subscribe((res: any) => {
      this.profanityRes.AnazRes = res;
    },
    error => {
      this.handleError(error);
    });

    this.fmService.callProfanityCensor(payload).subscribe((res: any) => {
      this.profanityRes.cenRes = res;
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Profanity');
      }
    }, error => {
      this.handleError(error);
    });
  }

  // Handles Explainability API calls
  callExplainabilityAPI(prompt: any) {
    if (this.explainabilityOption == 'Sentiment') {
      const payload: ExplainabilityPayload = { inputPrompt: prompt, modelName: this.selectedExplainabilityModel };
      this.fmService.callExplainability(payload).subscribe((expRes) => {
        this.explainabilityRes = expRes;
        this.spinner = false;
        if (this.activeTab == '') {
          this.changeTab('Explainability');
        }
      }, error => {
        this.handleError(error);
      });
    }
    else if (this.explainabilityOption == 'RAG') {
      this.callUploadEmbeddedFile1().then(res => {
        this.spinner = false;
        if (this.activeTab == '') {
          this.changeTab('Explainability');
        }
      });
    } else {
      this.isLoadingCOV = true;
      const payload: COVPayload = {
        complexity: 'simple',
        modelName: this.selectedExplainabilityModel,
        translate: this.selectedTranslate,
        inputPrompt: this.prompt
      };
      if (this.activeTab == '') {
        this.changeTab('Explainability');
      }
      this.fmService.callExplain_COV(payload)
        .subscribe((response: any) => {
          this.spinner = false;
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
          this.handleError(error);
          this.isLoadingCOV = false;
        });
    }
  }

  // Handles Fairness API calls
  callFairnessAPI(prompt: any) {
    const payload: FairnessPayload = {
      response: prompt.toString(),
      evaluator: this.fairnessEvaluator.toString()
    };
    this.fmService.callFairness(payload).subscribe((fairRes) => {
      this.fairnessRes = fairRes
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
    let data = payload ? payload : this.comp_Payload(prompt, tempStringValue, this.userRoleSettings.llmInteraction, this.selectPromptTemplate);
    this.fmService.getFMService(data, this.fmlocalselected)?.subscribe(
      async (res: any) => {
        this.templateBasedPayload['status'] = true;
        if (hallucinationPostCall) {
          this.hallucinationResModerationData = res.moderationResults.requestModeration;
        } else {
          this.coupledModerationRes = res;
          this.coupledModeration = true;
          this.fmService.updateData(res);
          this.changeTab('Request Moderation');
        }
        let summaryStatus = res.moderationResults.requestModeration.summary.status;
        let reSstatus = res.moderationResults.responseModeration.summary.status;
        this.callNemoApi(prompt, nemoGaurdrail, summaryStatus);
        this.callFMTimeApi(hallucinationPostCall);
        this.spinner = false;

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

  // Handles FM Config API calls
  callFMConfigApi(configPayload: any, accountName: any, portfolioName: any, tempStringValue: any, prompt: any) {
    accountName = this.selectedAccount;
    portfolioName = this.selectedPortfolio;
    return this.fmService.callFMConfig(configPayload).pipe(
      catchError(error => {
        return throwError(error);
      }),
      map((res: any) => {

        const response = res.dataList[0];
        // Store the values in local variables
        const bannedCategories = response.ModerationCheckThresholds.InvisibleTextCountDetails.BannedCategories;
        const gibberishLabels = response.ModerationCheckThresholds.GibberishDetails.GibberishLabels;

        this.gibrishDisplayLabels = gibberishLabels
        this.bannedCategoriesDisplay = bannedCategories
        this.customApipayloadStatus = true

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
    const payload: OpenAIPayload = { Prompt: prompt, temperature: tempStringValue, model_name: this.selectedLlmModel };
    this.fmService.callOpenAI(payload)
      .subscribe(
        (res: any) => {
          if (res.textlength == 0) {
            this.openAIRes = 'Open Ai failed Reason :' + res.finishReason;
            const message = 'Open Ai failed Reason :' + res.finishReason;
            this.openSnackBar(message, '✖');
          } else {
            const boldRegex = /\*\*(.+?)\*\*/;
            const numberedRegex = /\n/g;
            const replacement = "<br>";
            let processedText = res.text.replace(boldRegex, "<b>$1</b>");
            res.text = processedText.replace(numberedRegex, replacement);
            this.openAIRes = res;
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
    this.fmService.callRAGRetrieval(payload).subscribe((data: any) => {
      const res = data.rag_response;
      let sourceBar = []
      let bites = [];
      let ragText = '';
      let page_content = '';
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
    const payload: SummaryEvalPayload = {
      text: this.prompt,
      response: ragText,
      sourcetext: page_content,
      llmtype: "openai",
    };
    this.fmService.callGEval(payload).subscribe(
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
    this.fmService.getFMTime().subscribe(
      (res: any) => {
        if (hallucinationPostCall) {
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
      }
    }
  }
  
  getModerationfornemo(prompt: string) {
    const fileData2 = new FormData();
    fileData2.append('text', prompt);
    this.fmService.callNemoModerationRail(fileData2).subscribe(
      (res: any) => {
        this.nemoModerationRailRes = res
      },
      error => {
        this.handleError(error);
      }
    );
  }

  callNemoCheckApi(apiUrl: string, fileData: any, statusProperty: string, timeProperty: string) {
    this.fmService.callNemoCheck(apiUrl, fileData).subscribe(
      (res: any) => {
        this.nemoChecksApiResponses[statusProperty] = res['status'];
        this.nemoChecksApiResponses[timeProperty] = res['time'];
      },
      error => this.handleError(error)
    );
  }

  // ====== ERROR HANDLING METHODS ======
  
  // Handles error responses from API calls
  handleError(error: any, customErrorMessage?: any) {
    this.spinner = false;
    const message = error.error.details || customErrorMessage || 'API has failed';
    const action = 'Close';
    this.openSnackBar(message, action);
  }

  // Handles the switch for hallucination
  handleHallucinationSwitch() {
    if (this.enableEmbedding) {
      this.getembeddigns();
      this.hallucinationSwitchCheck = true;
    } else {
      this.hallucinationSwitchCheck = false;
    }
  }

  // ---------------PAYLOAD--------------------------
  comp_Payload(text: any, temperature: any, LLMinteraction: any, PromptTemplate: any) {
    const payload = {
      AccountName: 'None',
      PortfolioName: 'None',
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
          Restrictedtopics: ['Terrorism', 'Explosives', 'Nudity', 'Cruelty', 'Cheating', 'Fraud', 'Crime', 'Hacking', 'Immoral', 'Unethical', 'Illegal', 'Robbery', 'Forgery'],
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
        SentimentThreshold: -0.01,
        InvisibleTextCountDetails: {
          InvisibleTextCountThreshold: 1,
          BannedCategories: [
            "Cf",
            "Co",
            "Cn",
            "So",
            "Sc"
          ]
        },
        GibberishDetails: {
          GibberishThreshold: 0.7,
          GibberishLabels: [
            "word salad",
            "noise",
            "mild gibberish",
            "clean"
          ]
        },
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
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: tempStringValue,
      translate: this.selectedTranslate,
      model_name: this.selectedLlmModel,
      LLMinteraction: this.userRoleSettings.llmInteraction,
      PromptTemplate: this.selectPromptTemplate,
      Prompt: prompt,
      InputModerationChecks: response.ModerationChecks,
      OutputModerationChecks: response.OutputModerationChecks,
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
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: tempStringValue,
      translate: this.selectedTranslate,
      model_name: this.selectedLlmModel,
      LLMinteraction: this.userRoleSettings.llmInteraction,
      PromptTemplate: this.selectPromptTemplate,
      Prompt: prompt,
      InputModerationChecks: this.requestTemplateGlobal,
      OutputModerationChecks: this.responseTemplateGlobal,
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
    this.fmService.callPrivacyAnalyze(payloadAnalyze).subscribe((priAnzRes) => {
      this.privacyResponse.AnazRes = priAnzRes
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      this.handleError(error);
    })
  }

  // Handles Privacy API calls
  callPrivacyAnonymize(payloadAnon: any) {
    this.fmService.callPrivacyAnonymize(payloadAnon).subscribe((priAnonRes: any) => {
      this.privacyResponse.AnonRes = priAnonRes;
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      this.handleError(error);
    })
  }

  // Handles Privacy API calls
  callPrivacyEncrypt(payloadEncrypt: any) {
    this.fmService.callPrivacyEncrypt(payloadEncrypt).subscribe((priEncrypt) => {
      this.privacyResponse.EncryptRes = priEncrypt
      this.spinner = false;
      this.callPrivacyDecrypt(priEncrypt)
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      this.handleError(error);
    })
  }

  callPrivacyDecrypt(payloadDecrypt: any) {
    this.fmService.callPrivacyDecrypt(payloadDecrypt).subscribe((priDecrypt) => {
      this.privacyResponse.decryptedtoggle = false
      this.privacyResponse.DecryptRes = priDecrypt
      this.spinner = false;
      if (this.activeTab == '') {
        this.changeTab('Privacy Result');
      }
    }, error => {
      this.handleError(error);
    })
  }

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
      this.pEmoji.toggle();
    } else {
      this.pEmoji.toggle();
    }
  }

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
        let payload = {
          Prompt: f.controls['prompt'].value,
          choice: tchoice
        }
        this.postTranslateApi(payload)
      }
    } else {
      const message = 'Please enter the prompt';
      this.openSnackBar(message, '✖');
    }
  }
  safeTranslatedText!: SafeHtml;
  // Handles the translation API call
  postTranslateApi(payload: any) {
    this.fmService.callTranslate(payload).subscribe((res: any) => {
      this.tState = true
      this.tLoading = false
      this.translatedText = res
      // Sanitize the translated text for safe HTML binding
      if (res && res.text) {
        this.safeTranslatedText = this.sanitizer.bypassSecurityTrustHtml(this.escapeHtml(res.text));
      }
    }, error => {
      this.tLoading = false
      this.handleError(error)
    })

  }

  // Escape HTML special characters
  escapeHtml(text: string): string {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;')
      .replace(/\n/g, '<br>');
  }


  // MULTIMODEL

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
    this.openSnackBar(message, '✖');
    return;
  }

  // Handles the file selection for multimodel
  fileBrowseHandlerMultiModel(event: any) {
    this.prepareFilesListMulti(event.target.files);
    this.demoFileMultimodel = this.filesMultiModel;
    this.fileMultiModel = this.filesMultiModel[0];
    this.UploadedFile = this.filesMultiModel[0];
    this.disabledOptions = [];
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
    // if (files[0].type.startsWith('application/')) {
    //   this.isPDFFile = true;
    // } else {
    //   this.isPDFFile = false;
    // }

    const supportedDocTypes = ['application/pdf', 'text/csv', 'text/plain'];
    if ((files[0].type.startsWith('application/') || files[0].type.startsWith('text/')) && !supportedDocTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      let message = 'Only .pdf, .csv and .txt files are supported';
      this.openSnackBar(message, '✖');
      return;
    }
    const supportedImageTypes = ['image/jpg', 'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/jfif'];
    if (files[0].type.startsWith('image/') && !supportedImageTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      let message = 'Only jpg, jpeg, png, gif, bmp, jfif image types are supported';
      this.openSnackBar(message, '✖');
      return;
    }
    const supportedVideoTypes = ['video/mp4', 'video/3gp', 'video/mpeg']; if (files[0].type.startsWith('video/') && !supportedVideoTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      let message = 'Only mp4, 3gp video types are supported';
      this.openSnackBar(message, '✖');
      return;
    }
    const supportedAudioTypes = ['audio/wav', 'audio/flac', 'audio/mp3', 'audio/mpeg'];
    if (files[0].type.startsWith('audio/') && !supportedAudioTypes.includes(files[0].type)) {
      this.filesMultiModel = [];
      this.demoFileMultimodel = [];
      this.selectedFileNameMultiModel = '';
      this.imagePath = '';
      this.imgShowUrl = '';
      let message = 'Only wav, mp3 and flac audio types are supported';
      this.openSnackBar(message, '✖');
      return;
    }

    if (files[0].type.startsWith('application/') || files[0].type.startsWith('text/')) {
      this.disabledOptions = ["Privacy", "Profanity", "Explainability", "Fairness"];
      this.document = true;
      this.fmService.uploadRAGFile(this.fmService.createFileFormData(this.filesMultiModel)).subscribe(
        (res: any) => {
          this.vectorId = res.id;
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
    this.fmService.updateMultiModal(true, this.loggedINuserId, templateList, this.prompt, this.filesMultiModel[0]);
  }

  fairnessImage(formPayload: any) {
    this.fmService.processFairnessImage(formPayload, this.fairness_image).subscribe((res: any) => {
      this.fairness_response = res;
      this.fmService.updateMultiModalKeyVal('fairnessRes', res)
      if (this.tenantarr.includes('Fairness')) {
        this.spinner = false;
        if (this.activeTab == '') {
          this.changeTab('Fairness');
        }
        this.fairnessRes = res; //For Fairness Result Tab
      }
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
    this.imageService.imgApi(this.privAnzImgUrl2 + '?' + params, fileData, h)
      .subscribe({
        next: (data) => {
          let uniquePII: any = new Set()
          let piiEnt = data?.PIIEntities
          for (let i = 0; i < piiEnt.length; i++) {
            if (piiEnt[i].type != 'my') {
              uniquePII.add(piiEnt[i].type)
            }
          }
          this.privAnzOutput = uniquePII;
          if (piiEnt.length != 0) {
            this.sharedDataService.updateImageBasedModels("Image Privacy Check", "", 'modelBased')
          }
        },
        error: (error) => {
          this.handleError(error);
        },
      });
  }

  // Handles the multimodel API call
  profanityImageAnalyse() {
    const fileData = new FormData();
    this.fileMultiModel = this.filesMultiModel[0];
    fileData.append('image', this.fileMultiModel);
    if (this.portfolioName_value.length === 0) {
    } else {
      fileData.append('portfolio', this.portfolioName_value);
    }

    if (this.accountName_value.length === 0) {
    } else {
      fileData.append('account', this.accountName_value);
    }

    fileData.append('accuracy', 'high');
    this.fmService.analyzeProfanityImageAdvanced(fileData, this.profImageAnalyse).subscribe(
      (data: any) => {
        this.analyze = data.analyze;
        if (
          this.analyze?.hentai > 0.3 ||
          this.analyze?.porn > 0.3 ||
          this.analyze?.sexy > 0.3 ||
          this.analyze?.neutral > 1 ||
          this.analyze?.drawings > 1
        ) {
          this.sharedDataService.updateImageBasedModels("Image Safety Check", "", 'modelBased')
        }
      },
      (error: any) => {
        this.handleError(error);
      }
    );
  }

  // Handles the dialog opening for different file types 
  openDialog(data: any) {
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
      // Handle unsupported data type - could throw error or show user notification
      throw new Error('Unsupported data type');
    }
  }

  togglePanel(): void {
    this.isCollapsed = !this.isCollapsed;
  }
}
