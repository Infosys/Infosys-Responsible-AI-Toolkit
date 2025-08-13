/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, ChangeDetectorRef } from '@angular/core';
import { FmModerationService } from '../services/fm-moderation.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { DomSanitizer } from '@angular/platform-browser';
import { RoleManagerService } from '../services/role-maganer.service';
import { SharedDataService } from '../services/shared-data.service';
import { FormArray, FormBuilder, NgModel, Validators, FormGroup, FormControl } from '@angular/forms';
import { ImageService } from '../image/image.service';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-llm-scanner',
  templateUrl: './llm-scanner.component.html',
  styleUrls: ['./llm-scanner.component.css']
})

export class LlmScannerComponent {

  constructor(
    private imageService: ImageService,
    public roleService: RoleManagerService,
    private sharedDataService: SharedDataService,
    private sanitizer: DomSanitizer,
    private https: HttpClient,
    private fmService: FmModerationService,
    public _snackBar: MatSnackBar,
    public dialog: MatDialog,
    private fb: FormBuilder,
    public nonceService: NonceService,
    private cdr: ChangeDetectorRef
  ) {
    this.Form = this.fb.group({
      payloadList: this.fb.array([])
    });
  }

  // Variables start -----
  matToolTip: any;
  promptvariable = 'prompt'
  scannerres: any;
  shimmerLoader: boolean = false;
  targetLoader: boolean = false;
  isArrowLeft = true;
  selectedmodeltype: any = 'azure';
  Models: any;
  selectedModel: any = 'GPT_4_Turbo_Preview';
  selectedProbesCategory: any = 'encoding';
  isChecked: any = false;
  modelendpointavailable: any = false;
  endpointurl: any = "https://mlops-aicloud.ad.infosys.com/v1/completions/models/mify-2b/versions/1/infer"
  headers: any = "'Content-Type': 'application/json',\n'Accept': '*',\n'X-Cluster': 'H100'"
  newheaders: any;
  Form!: FormGroup;
  payload: any;
  probesList: any;
  selectedProbesList: any;
  getProbeList: any;
  getGarakResult: any;

  modelType = [
    { name: "AZURE", value: "azure" },
  ]
  gptModel = [
    { name: "GPT-4", value: "GPT_4_Turbo_Preview" },
    { name: "GPT-4o", value: "gpt-4o-westus" },
    { name: "GPT-3.5", value: "gpt-35-turbo_new" }
  ]
  MifyModel = [
    { name: "MIFY", value: "/models/mify/hf/mify-2b" },
  ]
  probesCategory = [
    { name: "Misleading", value: "misleading" },
    { name: "Encoding", value: "encoding" },
    { name: "PromptInject", value: "promptinject" },
    { name: "Donotanswer", value: "donotanswer" },
    { name: "Continuation", value: "continuation" },
    { name: "RealToxicityPrompts", value: "realtoxicityprompts" },
    { name: "Snowball", value: "snowball" },
    { name: "Grandma", value: "grandma" },
    { name: "Lmrc", value: "lmrc" },
    { name: "Malwaregen", value: "malwaregen" },
    { name: "Xss", value: "xss" },
    { name: "Av_Spam_Scanning", value: "av_spam_scanning" },
    { name: "Glitch", value: "glitch" },
    { name: "Divergence", value: "divergence" },
    { name: "Goodside", value: "goodside" },
    { name: "Latentinjection", value: "latentinjection" },
    { name: "Dan", value: "dan" },
    { name: "Packagehallucination", value: "packagehallucination" },
    { name: "Atkgen", value: "atkgen" }
  ]

  // Initially, the left panel is not collapsed
  isCollapsed: boolean = false;

  moderationCheck: Boolean = false;
  selectedTab: any = 1;
  promptLoader: any
  activeTab = '';
  apiEndpoints: any = {}

  scannerResAttempts: any = [];
  attemptSeverity: any = [];
  attemptProbe: any = [];
  attemptPrompt: any = [];
  attemptResponse: any = [];

  // Moderation Code===============

  // RequestModeration
  tempValue: number = 7;
  fmTimeApiResult = {
    "OpenAIInteractionTime": '',
    "requestModeration": '',
    "responseModeration": ''
  }
  templateBasedPayload: any = {
    status: false,
    userid: "None"
  }
  contentDetectorState = {
    active: true,
    prompt: prompt
  }
  requestModerationTemplates: any = [
    "Prompt Injection Check",
    "Jailbreak Check",
    "Fairness and Bias Check",
    "Language Critique Coherence Check",
    "Language Critique Fluency Check",
    "Language Critique Grammar Check",
    "Language Critique Politeness Check"
  ];
  openAIRes = {}
  coupledModerationRes: any;
  coupledModerationCheck: boolean = false;
  hallucinationSwitchCheck: boolean = false;
  selectedLlmModel: any = 'gpt4';
  selectedTranslate: any = 'no';
  llmBased: any = [];
  nemoChecksApiResponses: any = {};
  selectPromptTemplate: any = 'GoalPriority';
  llmEvalPayload: any = {
    "AccountName": "None",
    "PortfolioName": "None",
    "userid": "None",
    "lotNumber": 1,
    "Prompt": '',
    "model_name": this.selectedLlmModel,
    "temperature": this.tempValue.toString(),
    "PromptTemplate": this.selectPromptTemplate,
  }

  // ResponseModeration
  nemoModerationRailRes = {}
  responseModerationTemplates: any = [
    "Response Completeness Check",
    "Response Conciseness Check",
    "Response Language Critique Coherence Check",
    "Response Language Critique Fluency Check",
    "Response Language Critique Grammar Check",
    "Response Language Critique Politeness Check"
  ]
  selectedUseCaseName: any = '';
  setLoadTemplateResMod: boolean = false;

  // ResponseComparison
  cotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  }
  covState: any = {
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
  thotState: any = {
    active: false,
    hallucination: false,
    payload: {}
  }
  gEvalres: any = {};
  hallucinateRetrievalKeplerRes: any = {
    "status": false,
    "errorMesssage": '',
    "response": {}
  };
  serperResponseState: any = {
    model: this.selectedLlmModel,
    payload: {}
  }
  llmExplainState: any = {
    active: false,
    payload: {}
  }
  submitFlag: boolean = false;
  UploadedFile: any;
  vectorId: any;

  // Variable end -----

  // Initializes the component and sets up API calls
  ngOnInit(): void {
    let ip_port: any;
    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port);
    this.Models = this.gptModel
    this.getProbesList();
    this.addInitialPayload();
    this.matToolTip = 'Tests if prompt injection can occur through text encoding manipulations.'
  }

  // Method to toggle the collapse state
  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
  }

  // Toggles the arrow direction and collapse state
  methodforCollapse() {
    this.isArrowLeft = !this.isArrowLeft
    this.isCollapsed = !this.isCollapsed;
  }

  getLocalStoreApi() {
    let ip_port
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        return ip_port = JSON.parse(x)
      }
    }
  }

   // Retrieves API configuration from local storage
  setApilist(ip_port: any) {
    this.getProbeList = ip_port.result.llmGarakScanner + ip_port.result.llmGarakProbes;
    this.getGarakResult = ip_port.result.llmGarakScanner + ip_port.result.llmGarakDetails;
    this.apiEndpoints.fm_api = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_completions;
    this.apiEndpoints.fm_api_time = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_ModerationTime;
    this.apiEndpoints.fm_api_openAi = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_openai;
  }

  // Checks if the endpoint is available and updates the model list
  checkendpointavailable() {
    if (!this.isChecked) {
      this.modelendpointavailable = false
      this.Models = this.gptModel
      this.selectedModel = 'GPT_4_Turbo_Preview'
    }
    else {
      this.modelendpointavailable = true
      this.Models = this.MifyModel
      this.selectedModel = '/models/mify/hf/mify-2b'
    }
  }

  // Resets the endpoint URL
  resetendpointurl() {
    this.endpointurl = ''
  }

  // Resets the headers
  resetheaders() {
    this.headers = ''
  }

   // Formats and parses the headers
  headersmethod() {
    if (this.headers != '') {
      const str = this.headers.trim().replace(/^"(.*)"$/, '$1')
      const str1 = str.replace(/\n/g, '').replace(/\s+/g, '')
      let formattedStr = str1.replace(/'([^']+)'/g, '"$1"');
      formattedStr = `{${formattedStr}}`;
      console.log('formattedstr', formattedStr)
      this.newheaders = JSON.parse(formattedStr);
      console.log('newheaders', this.newheaders)
    }
  }

  // Returns the payload list form array
  get payloadList() {
    return this.Form.get('payloadList') as FormArray;
  }

   // Adds a new payload to the payload list
  addPayload() {
    const payloadForm = this.fb.group({
      key: ['', Validators.required],
      value: ['', Validators.required]
    });
    this.payloadList.push(payloadForm);
  }

  // Removes a payload from the payload list
  removePayload(index: number) {
    if (index !== 0) {
      this.payloadList.removeAt(index);
    }
  }

  // Retrieves and logs payload values
  getPayloadValues() {
    const payloadValues = this.payloadList.value;
    payloadValues.forEach((payload: { key: string, value: string }, index: number) => {
      console.log(`Payload ${index + 1}: Key = ${payload.key}, Value = ${payload.value}`);
    });

    this.payload = this.convertListToJsonObject(payloadValues);

  }

  // Converts a list of key-value pairs to a JSON object
  convertListToJsonObject(list: { key: string, value: any }[]): { [key: string]: any } {
    return list.reduce<{ [key: string]: any }>((acc, { key, value }) => {
      acc[key] = value;
      return acc;
    }, {});
  }

  // Adds initial payloads to the payload list
  addInitialPayload() {
    const initialPayloads = [
      { key: 'model', value: '/models/mify/hf/mify-2b' },
      { key: 'temperature', value: 0.7 },
      { key: 'top_p', value: 0.95 },
      { key: 'frequency_penalty', value: 0 },
      { key: 'presence_penalty', value: 0 },
      { key: 'max_tokens', value: 800 }
    ];

    initialPayloads.forEach(payload => {
      const payloadForm = this.fb.group({
        key: [payload.key, Validators.required],
        value: [payload.value, Validators.required]
      });
      this.payloadList.push(payloadForm);
    });
  }

  // Handles form submission and triggers scanner details
  onSubmit() {
    this.selectedTab = 1;
    this.getPayloadValues();
    this.headersmethod();
    this.scannerDetails();

    // Scroll to the output section of the page after a delay
    setTimeout(() => {
      const outputSection = document.getElementById('outputSection');
      if (outputSection) {
        outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 1);
  }

   // Fetches the list of probes based on the selected category
  getProbesList() {
    const probeData = new FormData();
    probeData.append('category', this.selectedProbesCategory);
    this.https.post(this.getProbeList, probeData).subscribe
      ((res: any) => {
        this.probesList = res
        if (this.probesList.length > 1) {
          this.selectedProbesList = res[1]
        }
        else {
          this.selectedProbesList = res[0]
        }
      }
        , error => {
          const message = "The Api has failed"
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        })
  }

  // Fetches scanner details and processes the response
  scannerDetails() {
    if (!this.modelendpointavailable) {
      this.shimmerLoader = true
      this.targetLoader = false
      this.resetResponse();
      const payload = {
        "modeltype": "azure",
        "modelname": this.selectedModel,
        "probes": this.selectedProbesCategory + '.' + this.selectedProbesList
      }
      this.https.post(this.getGarakResult, payload).subscribe
        ((res: any) => {
          this.scannerres = res
          // this.scannerres.attempt.sort((a: { score: string[] }, b: { score: string[] }) => {
          //   if (a.score[0] === '1' && b.score[0] === '0') {
          //     return -1;
          //   } else if (a.score[0] === '0' && b.score[0] === '1') {
          //     return 1; 
          //   }
          //   return 0;
          // });

          this.scannerResAttempts = this.scannerres.attempt;
          if (this.scannerResAttempts.length > 0) {
            this.scannerResAttempts.forEach((attempt: any) => {
              this.attemptSeverity.push(this.checkSeverityLevel(attempt.detector_results[0]));
              this.attemptProbe.push(this.splitProbe(attempt.probe_classname));
              this.attemptPrompt.push(attempt.prompt);
              this.attemptResponse.push(attempt.response[0]);

            });

            // Call for Moderation API's
            this.moderationCheck ? this.moderationCall() : this.moderationCheck = false;
          }
          else if (this.scannerResAttempts.length == 0) {
            this._snackBar.open('No results found', 'Close', {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
            this.resetResponse();
          }

          this.shimmerLoader = false;
          this.targetLoader = true;
          this.isCollapsed = true;
          this.isArrowLeft = !this.isArrowLeft
        }
          , error => {
            this.shimmerLoader = false;
            this.targetLoader = true;
            const message = "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
          })
    }
    else {
      this.shimmerLoader = true
      this.targetLoader = false
      this.resetResponse();
      const payload = {
        "modeltype": "aicloud",
        "modelname": this.selectedModel,
        "probes": this.selectedProbesCategory + '.' + this.selectedProbesList,
        "model_endpoint_url": this.endpointurl,
        "headers": this.newheaders,
        "model_payload": this.payload,
        "model_prompt_variable": this.promptvariable
      }
      this.https.post(this.getGarakResult, payload).subscribe
        ((res: any) => {
          this.scannerres = res
          this.shimmerLoader = false;
          this.targetLoader = true;
          this.setLoadTemplateResMod = true;
          this.llmEvalPayload = {
            "AccountName": "None",
            "PortfolioName": "None",
            "userid": "None",
            "lotNumber": 1,
            "Prompt": this.attemptPrompt[this.selectedTab - 1],
            "model_name": this.selectedLlmModel,
            "temperature": this.tempValue.toString(),
            "PromptTemplate": this.selectPromptTemplate,
          }
        }
          , error => {
            this.shimmerLoader = false;
            this.targetLoader = true;
            const message = "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
          })
    }
  }

  // Resets the scanner response data
  resetResponse() {
    this.scannerres = {};
    this.scannerResAttempts = [];
    this.attemptSeverity = [];
    this.attemptProbe = [];
    this.attemptPrompt = [];
    this.attemptResponse = [];
    this.setLoadTemplateResMod = false;
  }

  // Checks the severity level of a value
  checkSeverityLevel(value: any): string {
    // if(value ==='1'){
    //   return 'HIGH';
    // }
    // else{
    //   return 'NONE';
    // }
    return value === '1' ? 'HIGH' : 'NONE';
  }

  // Performs a bitwise OR operation on an array of strings
  bitOr(arr: string[]): string {
    return arr.some(value => value === '1') ? '1' : '0';
  }

  // Splits the probe class name to extract the probe name
  splitProbe(probeClass: string): string {
    return probeClass.split('.')[1];
  }

  // Updates the tooltip based on the selected probe category
  changeMatToolTip() {
    if (this.selectedProbesCategory == 'encoding') {
      this.matToolTip = 'Tests if prompt injection can occur through text encoding manipulations.'
    }
    else if (this.selectedProbesCategory == 'misleading') {
      this.matToolTip = 'Attempts to make the model generate misleading or false information.'
    }
    else if (this.selectedProbesCategory == 'promptinject') {
      this.matToolTip = 'Identifies if the model is vulnerable to injected commands or prompts that alter its responses.'
    }
    else if (this.selectedProbesCategory == 'donotanswer') {
      this.matToolTip = 'Probes if the model correctly refuses to answer certain unethical or harmful questions.'
    }
    else if (this.selectedProbesCategory == 'continuation') {
      this.matToolTip = 'Tests if the model continues undesirable or harmful words or ideas.'
    }
    else if (this.selectedProbesCategory == 'realtoxicityprompts') {
      this.matToolTip = 'Tests the model response to prompts that induce toxic or harmful language.'
    }
    else if (this.selectedProbesCategory == 'snowball') {
      this.matToolTip = 'Challenges the model with complex questions to test if it generates inaccurate or hallucinated answers.'
    }
    else if (this.selectedProbesCategory == 'grandma') {
      this.matToolTip = 'Probes for prompts that appeal to sentimental or nostalgic responses related to grandmothers.'
    }
    else if (this.selectedProbesCategory == 'lmrc') {
      this.matToolTip = 'Assesses responses based on the Language Model Risk Cards Framework for ethical considerations.'
    }
    else if (this.selectedProbesCategory == 'malwaregen') {
      this.matToolTip = 'Attempts to trick the model into generating code related to malware creation.'
    }
    else if (this.selectedProbesCategory == 'xss') {
      this.matToolTip = 'Tests for vulnerabilities that could lead to cross-site scripting or data leakage attacks.'
    }
    else if (this.selectedProbesCategory == 'av_spam_scanning') {
      this.matToolTip = 'Probes to check if the model outputs malicious or spam-like content signatures.'
    }
    else if (this.selectedProbesCategory == 'glitch') {
      this.matToolTip = 'Looks for unusual behavior in the model triggered by strange or unexpected inputs (glitch tokens).'
    }
    else if (this.selectedProbesCategory == 'divergence') {
      this.matToolTip = 'Checks if the model deviates from expected output when asked to repeat a string indefinitely.'
    }
    else if (this.selectedProbesCategory == 'goodside') {
      this.matToolTip = 'Implements Riley Goodside’s attack methods to assess model behavior under adversarial inputs.'
    }
    else if (this.selectedProbesCategory == 'latentinjection') {
      this.matToolTip = 'Probes if the model can be manipulated through hidden prompt injections embedded in other contexts.'
    }
    else if (this.selectedProbesCategory == 'dan') {
      this.matToolTip = 'Probes that explore various attack vectors related to DAN (Do Anything Now) exploits.'
    }
    else if (this.selectedProbesCategory == 'packagehallucination') {
      this.matToolTip = 'Attempts to make the model generate code involving non-existent or insecure software packages.'
    }
    else if (this.selectedProbesCategory == 'atkgen') {
      this.matToolTip = 'Tests if the model can be manipulated into generating harmful or adversarial inputs designed to attack or exploit vulnerabilities.'
    }
  }

  // new ui code=====
  selectTab(tab: any) {
    this.selectedTab = tab;
    this.moderationCheck ? this.moderationCall() : this.moderationCheck = false;
    this.cdr.detectChanges();
  }

   // Returns the background color based on severity
  getBackgroundColor(severity: any) {
    return severity === 'HIGH' ? '#FF0000' : '#00FF00'; // Red for HIGH, Green for NONE
  }

   // Changes the active tab
  changeTab(tab: string) {
    this.activeTab = tab;
  }

  // Calls the FM API for moderation
  callFMApi(prompt: string, tempStringValue: string, nemoGaurdrail: any, hallucinationSwitch: any, payload?: any, hallucinationPostCall: any = false) {
    console.log("callFMApi");
    this.promptLoader = true;
    let data = payload ? payload : this.comp_Payload(prompt, tempStringValue, 'yes', 'GoalPriority');
    this.fmService.getFMService(this.apiEndpoints.fm_api, data, false)?.subscribe(
      async (res: any) => {
        this.templateBasedPayload['status'] = true;
        this.coupledModerationRes = res;
        this.coupledModerationCheck = true;
        this.fmService.updateData(res);
        this.changeTab('Request Moderation');
        let summaryStatus = res.moderationResults.requestModeration.summary.status;
        let reSstatus = res.moderationResults.responseModeration.summary.status;
        console.log("summaryStatus", summaryStatus)
        console.log("reSstatus", reSstatus)
        this.callFMTimeApi(hallucinationPostCall, prompt);
        this.promptLoader = false;
        this.templateBasedPayload['status'] = true;
      },
      error => {
        console.log(error);
      }
    );
  }

  // Composes the payload for FM API calls
  comp_Payload(text: any, temperature: any, LLMinteraction: any, PromptTemplate: any) {
    const payload = {
      AccountName: 'None',
      PortfolioName: 'None',
      // EmojiModeration: this.selectedEmojiVal,
      EmojiModeration: 'yes',
      userid: 'admin',
      lotNumber: 1,
      temperature: temperature,
      model_name: this.selectedLlmModel,
      translate: this.selectedTranslate,
      LLMinteraction: LLMinteraction,
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
          Restrictedtopics: ['Terrorism', 'Explosives'],
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
        "BanCodeThreshold": 0.7
        //  end of new payloads
      },
    };

    return payload;
  }

  callFMTimeApi(hallucinationPostCall: boolean = false, prompt: any) {
    this.https.get(this.apiEndpoints.fm_api_time).subscribe((res: any) => {
      console.log(res);
      if (hallucinationPostCall) {
        console.log("Hallucination Post Call")
        this.fmTimeApiResult.responseModeration = res.requestModeration;
      } else {
        this.fmTimeApiResult = res;
      }
    },
      error => {
        console.log(error);
        // this.handleError(error);
      }
    );
  }

  callOpenAiApi(prompt: string, tempStringValue: string) {
    this.promptLoader = true;
    this.https.post(this.apiEndpoints.fm_api_openAi, { Prompt: prompt, temperature: tempStringValue, model_name: this.selectedLlmModel })
      .subscribe((res: any) => {
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
          this.promptLoader = false;
        }
      },
        error => {
          console.log(error);
          // this.handleError(error, "OPENAI API FAILED");
        });
  }

  // Handles the click event for the moderation checkbox
  moderationCall() {
    this.callFMApi(this.attemptPrompt[this.selectedTab - 1], '0', '', false);
    this.callOpenAiApi(this.attemptPrompt[this.selectedTab - 1], '0');
    this.setLoadTemplateResMod = true;
    this.llmEvalPayload = {
      "AccountName": "None",
      "PortfolioName": "None",
      "userid": "None",
      "lotNumber": 1,
      "Prompt": this.attemptPrompt[this.selectedTab - 1],
      "model_name": this.selectedLlmModel,
      "temperature": this.tempValue.toString(),
      "PromptTemplate": this.selectPromptTemplate,
    }
  }
  
// Checks if the moderation API is called
  checksModeration(ev: any) {
    if (this.moderationCheck) {
      this.moderationCall();
    }
    else ev.stopPropagation();
  }

}
