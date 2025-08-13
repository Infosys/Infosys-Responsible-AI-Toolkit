/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, Validators } from '@angular/forms';
import { NonceService } from '../nonce.service';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { NestedTreeControl } from '@angular/cdk/tree';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import { TemplateBasedGuardrailService } from '../fm-moderation/request-moderation/template-based-guardrail/template-based-guardrail.service';

interface TreeNode {
  id: string;
  label: string;
  children?: TreeNode[];
  expanded?: boolean;
  checked?: boolean;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
  animations: [
    trigger('divAnimation', [
      state(
        'open',
        style({
          opacity: 1,
          transform: 'translateY(0)',
        })
      ),
      state(
        'closed',
        style({
          opacity: 0,
          transform: 'translateY(-100%)',
        })
      ),
      transition('open => closed', [animate('0.5s ease-in')]),
      transition('closed => open', [animate('0.5s ease-out')]),
    ]),
  ],
})
export class ChatbotComponent implements OnInit {
  treeControl = new NestedTreeControl<TreeNode>((node) => node.children);
  dataSource = new MatTreeNestedDataSource<TreeNode>();
  isChatOpen = false;
  submitted = false;
  displayModelPassed = false;
  displayModelFailed = false;
  displayTemplatePassed = false;
  displayTemplateFailed = false;
  chatbotPrompt: string = '';
  fmPrompt: string = '';
  url: any;
  fm_api: any;
  isLoading: boolean = false;
  sample1 = 'What is privacy in Responsible AI?';
  sample2 = 'What is the Purpose of RAG?';
  sample3 = 'What is FM Moderation in RAI?';

  userMessages: string[] = [];
  botResponses: string[] = [];
  fmUserMessages: string[] = [];
  fmBotResponses: string[] = [];

  isChatbotMode: boolean = true;
  isFMMode: boolean = false;
  isFMModeSubmited: boolean = false;
  selectedButtons: string[] = [];
  isListVisible: boolean = true;
  promptControl = new FormControl('', Validators.required);
  loggedINuserId: any;
  selectedLlmModel: any = 'gpt4';
  selectedTranslate: any = 'no';
  llmBased: any = [];
  generatedText: any;

  constructor(
    private https: HttpClient,
    public nonceService: NonceService,
    private cdr: ChangeDetectorRef,
    private templateBasedService: TemplateBasedGuardrailService
  ) { }
  apiEndpoints: any = {};
  // initalizes the component and set up API endpoints
  ngOnInit(): void {
    this.dataSource.data = this.treeData;
    this.divState = 'open';
    let ip_port: any;
    if (localStorage.getItem('res') != null) {
      const x = localStorage.getItem('res');
      if (x != null) {
        ip_port = JSON.parse(x);
      }
      this.url = ip_port.result.chatBot + ip_port.result.chatBotAnswer;
      this.fm_api =
        ip_port.result.FM_Moderation +
        ip_port.result.Moderationlayer_completions;
      this.apiEndpoints.llm_eval =
        ip_port.result.FM_Moderation + ip_port.result.EvalLLM;
    }
    if (localStorage.getItem('userid') != null) {
      const x = localStorage.getItem('userid');
      if (x != null) {
        this.loggedINuserId = JSON.parse(x);
      }
    }

    // Call the batch evaluation function with the provided templates array
    this.globalTemplateResponses = this.globalTemplateResponses || [];
    this.checkAllNodes(this.treeData, true); // Call this method on component initialization
  }
   // Toggles the chatbot visibility
  toggleChat() {
    this.divState = 'open';
    this.isAnotherMode = '';
    this.isDivVisible = true;
    this.isChatOpen = !this.isChatOpen;
    this.userMessages = [];
    this.botResponses = [];
    this.fmUserMessages = [];
    this.fmBotResponses = [];
    this.selectedButtons = [];
    this.sample1 = 'What is privacy in Responsible AI?';
    this.sample2 = 'What is the Purpose of RAG?';
    this.sample3 = 'What is FM Moderation in RAI?';
    if (this.isChatOpen) {
      this.isChatbotMode = true;
      this.isFMMode = false;
    }
  }

  // Handles bubble click and sends the question
  onBubbleClick(question: string) {
    this.chatbotPrompt = question;
    this.send();
  }
  // Toggles the selected button state
  showData(button: string) {
    console.log('button==', button);
    this.isListVisible = true;
    this.promptControl.setValue(button);
    if (!this.selectedButtons.includes(button)) {
      this.selectedButtons.push(button);
    } else {
      this.selectedButtons = this.selectedButtons.filter((b) => b !== button);
    }
    console.log('selectedButtons==', this.selectedButtons);
  }

  // Toggles between chatbot and FM moderation modes
  toggleMode(event: any): void {
    this.isChatbotMode = !this.isChatbotMode;
    this.isFMMode = !this.isFMMode;
    if (this.isChatbotMode) {
      this.fmPrompt = '';
      this.fmUserMessages = [];
      this.fmBotResponses = [];
      this.selectedButtons = [];
    } else {
      this.chatbotPrompt = '';
      this.userMessages = [];
      this.botResponses = [];
      this.sample1 = 'What is privacy in Responsible AI?';
      this.sample2 = 'What is the Purpose of RAG?';
      this.sample3 = 'What is FM Moderation in RAI?';
    }
  }

  requestModerationSummary: any = {}; // To store the summary of requestModeration
  responseModerationSummary: any = {}; // To store the summary of responseModeration

  // await this.displaySelectedValues();

  //  Handles FM moderation API call and processes results
  async fmModeration(InputModerationChecksPayload:any, OutputModerationChecksPayload:any) {
    console.log('callFMApi');
    const payloadx = this.comp_Payloadx(InputModerationChecksPayload, OutputModerationChecksPayload);
    this.isLoading = true;
  
    this.https.post(this.fm_api, payloadx.payload).subscribe(
      (response: any) => {
        console.log('API response:', response);
        if (response && response.moderationResults) {
          const moderationResults: Array<{ checkName: string; status: string }> = [];
  
          // Process requestModeration
          if (response.moderationResults.requestModeration?.summary) {
            this.requestModerationSummary = response.moderationResults.requestModeration.summary;
            const failedChecks = this.requestModerationSummary.reason || [];
            const remainingChecks = payloadx.InputModerationChecks.filter(
              (check: string) => !failedChecks.includes(check)
            );
  
            moderationResults.push(
              ...remainingChecks.map((check: any) => ({ checkName: `Request-${check}`, status: 'PASSED' })),
              ...failedChecks.map((check: any) => ({ checkName: `Request-${check}`, status: 'FAILED' }))
            );
          }
  
          // Process responseModeration
          if (response.moderationResults.responseModeration?.summary) {
            this.responseModerationSummary = response.moderationResults.responseModeration.summary;
            const failedChecks = this.responseModerationSummary.reason || [];
            const remainingChecks = payloadx.OutputModerationChecks.filter(
              (check: string) => !failedChecks.includes(check)
            );
  
            moderationResults.push(
              ...remainingChecks.map(check => ({ checkName: `Response-${check}`, status: 'PASSED' })),
              ...failedChecks.map((check: any) => ({ checkName: `Response-${check}`, status: 'FAILED' }))
            );
          }
  
          this.globalmoderationResults = moderationResults;
          console.log('Final Moderation Results:', this.globalmoderationResults);
        }
        this.isLoading = false;
      },
      error => {
        console.error('API error:', error);
        this.isLoading = false;
      }
    );
  }

  // Handles the submission of the chatbot prompt
  send() {
    console.log('url::', this.url);
    const userMessage = this.chatbotPrompt;
    this.userMessages.push(userMessage);

    const payload = { text: this.chatbotPrompt };
    this.chatbotPrompt = '';
    this.isLoading = true;

    this.https.post(this.url, payload).subscribe(
      (response) => {
        console.log('chatbotResponse', response);
        if (!response) {
          const defaultResponse = 'Please try again after sometime.';
          this.botResponses.push(defaultResponse);
        } else {
          const responseArray = response as any[];
          if (
            responseArray &&
            responseArray.length > 0 &&
            responseArray[0].text
          ) {
            const text = responseArray[0].text;
            const answerMatch = text.match(
              /Answer:([\s\S]*?)(?=Related questions:|$)/
            );
            if (answerMatch && answerMatch[1]) {
              const botResponse = answerMatch[1].trim();
              this.botResponses.push(botResponse);
            } else {
              const defaultResponse =
                "I'm sorry, I cannot answer that as there is no information related";
              this.botResponses.push(defaultResponse);
            }

            const relatedQuestionsMatch = text.match(
              /Related questions:\n([\s\S]*)/
            );
            if (relatedQuestionsMatch && relatedQuestionsMatch[1]) {
              const relatedQuestions = relatedQuestionsMatch[1]
                .trim()
                .split('\n')
                .map((q: string) => q.replace(/^\s*\d+\.\s*/, '').trim());
              this.sample1 = relatedQuestions[0];
              this.sample2 = relatedQuestions[1];
              this.sample3 = relatedQuestions[2];
            }

          } else {
            const defaultResponse =
              "I'm sorry, I cannot answer that as there is no information related";
            this.botResponses.push(defaultResponse);
          }
        }
        this.isLoading = false;
      },
      (error) => {
        console.error('Error:', error);
        this.isLoading = false;
      }
    );
  }

  // Generates a payload for FM moderation
  comp_Payload() {
    const allChecks = [
      'PromptInjection',
      'JailBreak',
      'Toxicity',
      'Piidetct',
      'Refusal',
      'Profanity',
      'RestrictTopic',
      'Sentiment',
      'InvisibleText',
      'Gibberish',
      'BanCode',
    ];
    const payload = {
      AccountName: 'None',
      PortfolioName: 'None',
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: 0,
      model_name: this.selectedLlmModel,
      translate: this.selectedTranslate,
      LLMinteraction: 'yes',
      PromptTemplate: 'GoalPriority',
      Prompt: this.copyoffmPrompt,
      InputModerationChecks:
        this.selectedButtons.length > 0 ? this.selectedButtons : allChecks,
      OutputModerationChecks: [
        'Toxicity',
        'Piidetct',
        'Refusal',
        'Profanity',
        'RestrictTopic',
        'TextQuality',
        'TextRelevance',
        'Sentiment',
        'InvisibleText',
        'Gibberish',
        'BanCode',
      ],
      llm_BasedChecks: this.llmBased,
      ModerationCheckThresholds: {
        PromptinjectionThreshold: 0.7,
        JailbreakThreshold: 0.7,
        PiientitiesConfiguredToBlock: [
          'IN_AADHAAR',
          'IN_PAN',
          'US_PASSPORT',
          'US_SSN',
          'AADHAR_NUMBER',
          'PAN_Number',
        ],
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
          SmoothLlmThreshold: 0.6,
        },

        // newly added payloads
        SentimentThreshold: -0.01,
        InvisibleTextCountDetails: {
//           InvisibleTextCountThreshold: 1,
          BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
        },
        GibberishDetails: {
          GibberishThreshold: 0.7,
          GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
        },
//         BanCodeThreshold: 0.7,

      },
    };

    return payload;
  }

  divState: string = 'open';

  triggerCloseAnimation() {
    this.divState = 'closed';
  }

  // Selects the Model-Based Guardrails mode
  selectModelBasedGuardrails() {
    console.log('Model-Based Guardrails selected');
    // Add your logic here
    this.triggerCloseAnimation();
    this.isAnotherMode = 'Model-Based Guardrails';
  }

  //  Selects the Template-Based Guardrails mode
  selectTemplateBasedGuardrails() {
    console.log('Template-Based Guardrails selected');
    this.triggerCloseAnimation();
    this.isAnotherMode = 'Template-Based Guardrails';
    // Add your logic here
  }

  group1Options: { id: string; label: string }[] = [
    { id: 'group1_PromptInjection', label: 'PromptInjection' },
    { id: 'group1_JailBreak', label: 'JailBreak' },
    { id: 'group1_Toxicity', label: 'Toxicity' },
    { id: 'group1_Piidetct', label: 'Piidetct' },
    { id: 'group1_Refusal', label: 'Refusal' },
    { id: 'group1_Profanity', label: 'Profanity' },
    { id: 'group1_RestrictTopic', label: 'RestrictTopic' },
    { id: 'group1_TextQuality', label: 'TextQuality' },
    { id: 'group1_CustomizedTheme', label: 'CustomizedTheme' },
    { id: 'group1_Sentiment', label: 'Sentiment' },
    { id: 'group1_InvisibleText', label: 'InvisibleText' },
    { id: 'group1_Gibberish', label: 'Gibberish' },
    { id: 'group1_BanCode', label: 'BanCode' },
  ];

  group2Options: { id: string; label: string }[] = [
    { id: 'group2_Toxicity', label: 'Toxicity' },
    { id: 'group2_Piidetct', label: 'Piidetct' },
    { id: 'group2_Refusal', label: 'Refusal' },
    { id: 'group2_Profanity', label: 'Profanity' },
    { id: 'group2_RestrictTopic', label: 'RestrictTopic' },
    { id: 'group2_TextQuality', label: 'TextQuality' },
    { id: 'group2_TextRelevance', label: 'TextRelevance' },
    { id: 'group2_Sentiment', label: 'Sentiment' },
    { id: 'group2_InvisibleText', label: 'InvisibleText' },
    { id: 'group2_Gibberish', label: 'Gibberish' },
    { id: 'group2_BanCode', label: 'BanCode' },
  ];
  failedChecks: string[] = [
    'Toxicity',
    'Refusal',
    'RestrictTopic',
    'Terrorism',
    'Explosives',
  ]; // replace with actual failed checks
  passedChecks: string[] = [
    'PromptInjection',
    'JailBreak',
    'Toxicity',
    'Piidetct',
    'Refusal',
    'Profanity',
    'RestrictTopic',
    'Sentiment',
    'InvisibleText',
    'Gibberish',
    'BanCode',
  ]; // replace with actual passed checks

  selectedOptions: string[] = [];
  // InputModerationChecks: [
  //   'PromptInjection',
  //   'JailBreak',
  //   'Toxicity',
  //   'Piidetct',
  //   'Refusal',
  //   'Profanity',
  //   'RestrictTopic',
  //   'TextQuality',
  //   'CustomizedTheme',
  //   "Sentiment",
  //   "InvisibleText",
  //   "Gibberish",
  //   "BanCode"
  // ],
  // OutputModerationChecks: ['Toxicity', 'Piidetct', 'Refusal', 'Profanity', 'RestrictTopic', 'TextQuality', 'TextRelevance', "Sentiment",
  //   "InvisibleText",
  //   "Gibberish",
  //   "BanCode"],
  selectedInputModerationOptions: string[] = [
    'PromptInjection',
    'JailBreak',
    'Toxicity',
    'Piidetct',
    'Refusal',
    'Profanity',
    'RestrictTopic',
    'TextQuality',
    'CustomizedTheme',
    'Sentiment',
    'InvisibleText',
    'Gibberish',
    'BanCode',
  ];
  selectedOutputModerationOptions: string[] = [
    'Toxicity',
    'Piidetct',
    'Refusal',
    'Profanity',
    'RestrictTopic',
    'TextQuality',
    'TextRelevance',
    'Sentiment',
    'InvisibleText',
    'Gibberish',
    'BanCode',
  ];

  // Displays selected values from the tree structure
  displaySelectedValues(): Promise<void> {
    return new Promise((resolve) => {
      this.selectedInputModerationOptions = this.selectedOptions
        .filter((option) => option.startsWith('group1_'))
        .map((option) => option.replace('group1_', ''));
      this.selectedOutputModerationOptions = this.selectedOptions
        .filter((option) => option.startsWith('group2_'))
        .map((option) => option.replace('group2_', ''));

      console.log(
        'Selected Group 1 Options:',
        this.selectedInputModerationOptions
      );
      console.log(
        'Selected Group 2 Options:',
        this.selectedOutputModerationOptions
      );

      resolve();
    });
  }

  comp_Payloadx(selectedInputModerationOptions:any,selectedOutputModerationOptions:any) {
    const allChecks = [
      'PromptInjection',
      'JailBreak',
      'Toxicity',
      'Piidetct',
      'Refusal',
      'Profanity',
      'RestrictTopic',
      'Sentiment',
      'InvisibleText',
      'Gibberish',
      'BanCode',
    ];
    const payload = {
      AccountName: 'None',
      PortfolioName: 'None',
      EmojiModeration: 'yes',
      userid: this.loggedINuserId,
      lotNumber: 1,
      temperature: 0,
      model_name: this.selectedLlmModel,
      translate: this.selectedTranslate,
      LLMinteraction: 'yes',
      PromptTemplate: 'GoalPriority',
      Prompt: this.copyoffmPrompt,
      InputModerationChecks: selectedInputModerationOptions,
      OutputModerationChecks: selectedOutputModerationOptions,
      llm_BasedChecks: this.llmBased,
      ModerationCheckThresholds: {
        PromptinjectionThreshold: 0.7,
        JailbreakThreshold: 0.7,
        PiientitiesConfiguredToBlock: [
          'IN_AADHAAR',
          'IN_PAN',
          'US_PASSPORT',
          'US_SSN',
          'AADHAR_NUMBER',
          'PAN_Number',
        ],
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
          SmoothLlmThreshold: 0.6,
        },
        // newly added payloads
        SentimentThreshold: -0.01,
        InvisibleTextCountDetails: {
          InvisibleTextCountThreshold: 1,
          BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
        },
        GibberishDetails: {
          GibberishThreshold: 0.7,
          GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
        },
        BanCodeThreshold: 0.7,
      },
    };
    let master = {
      payload: payload,
      InputModerationChecks: this.selectedInputModerationOptions,
      OutputModerationChecks: this.selectedOutputModerationOptions,
    };

    return master;
  }

  isAnotherMode: string = '';
  isDivVisible: boolean = true;

  // Existing methods...

  toggleAnotherMode(event: any): void {
    this.isAnotherMode =
      this.isAnotherMode === 'Model-Based Guardrails'
        ? 'Template-Based Guardrails'
        : 'Model-Based Guardrails';
    console.log(`Current Mode: ${this.isAnotherMode}`);
  }

  onAnimationDone(event: any) {
    if (this.divState === 'closed') {
      this.isDivVisible = false;
    }
  }

  newGroup1Options: { id: string; label: string }[] = [
    { id: 'newGroup1_PromptInjectionCheck', label: 'Prompt Injection Check' },
    { id: 'newGroup1_JailbreakCheck', label: 'Jailbreak Check' },
    { id: 'newGroup1_FairnessAndBiasCheck', label: 'Fairness and Bias Check' },
    {
      id: 'newGroup1_LanguageCritiqueCoherenceCheck',
      label: 'Language Critique Coherence Check',
    },
    {
      id: 'newGroup1_LanguageCritiqueFluencyCheck',
      label: 'Language Critique Fluency Check',
    },
    {
      id: 'newGroup1_LanguageCritiqueGrammarCheck',
      label: 'Language Critique Grammar Check',
    },
    {
      id: 'newGroup1_LanguageCritiquePolitenessCheck',
      label: 'Language Critique Politeness Check',
    },
  ];

  newGroup2Options: { id: string; label: string }[] = [
    {
      id: 'newGroup2_ResponseCompletenessCheck',
      label: 'Response Completeness Check',
    },
    {
      id: 'newGroup2_ResponseConcisenessCheck',
      label: 'Response Conciseness Check',
    },
    {
      id: 'newGroup2_ResponseLanguageCritiqueCoherenceCheck',
      label: 'Response Language Critique Coherence Check',
    },
    {
      id: 'newGroup2_ResponseLanguageCritiqueFluencyCheck',
      label: 'Response Language Critique Fluency Check',
    },
    {
      id: 'newGroup2_ResponseLanguageCritiqueGrammarCheck',
      label: 'Response Language Critique Grammar Check',
    },
    {
      id: 'newGroup2_ResponseLanguageCritiquePolitenessCheck',
      label: 'Response Language Critique Politeness Check',
    },
  ];

  selectedNewOptions: string[] = [];
  isNavOpen = false; // Add this line

  // Toggles the navigation menu
  toggleNav() {
    this.isNavOpen = !this.isNavOpen;
  }

  treeData: TreeNode[] = [
    {
      id: 'modelBasedGuardrails',
      label: 'Model-Based Guardrails',
      expanded: false,
      checked: false,
      children: [
        {
          id: 'group1',
          label: 'Input Moderation Checks',
          expanded: false,
          checked: false,
          children: this.group1Options,
        },
        {
          id: 'group2',
          label: 'Output Moderation Checks',
          expanded: false,
          checked: false,
          children: this.group2Options,
        },
      ],
    },
    {
      id: 'templateBasedGuardrails',
      label: 'Template-Based Guardrails',
      expanded: false,
      checked: false,
      children: [
        {
          id: 'newGroup1',
          label: 'Request Templates',
          expanded: false,
          checked: false,
          children: this.newGroup1Options,
        },
        {
          id: 'newGroup2',
          label: 'Response Templates',
          expanded: false,
          checked: false,
          children: this.newGroup2Options,
        },
      ],
    },
  ];
  
  toggleSelection(node: TreeNode, checked: boolean) {
    // Update the checked state of the current node
    node.checked = checked;
  
    // Update child nodes
    this.updateChildNodes(node, checked);
  
    // Update parent nodes
    this.updateParentNodes(node);
  
    // Trigger change detection
    this.cdr.detectChanges();
  }
  
  updateChildNodes(node: TreeNode, checked: boolean) {
    if (node.children) {
      node.children.forEach((child) => {
        child.checked = checked; // Update child nodes
        this.updateChildNodes(child, checked); // Recursively update all descendants
      });
    }
  }
  
  updateParentNodes(node: TreeNode) {
    const parent = this.findParentNode(node, this.treeData);
    if (parent) {
      parent.checked = parent.children?.every((child) => child.checked) || false;
      this.updateParentNodes(parent); // Recursively update all ancestors
    }
  }
  
  findParentNode(node: TreeNode, nodes: TreeNode[]): TreeNode | null {
    for (const parent of nodes) {
      if (parent.children?.includes(node)) {
        return parent;
      }
      const found = this.findParentNode(node, parent.children || []);
      if (found) {
        return found;
      }
    }
    return null;
  }
  
  toggleExpand(node: TreeNode) {
    node.expanded = !node.expanded; // Toggle the expanded state
    this.cdr.detectChanges(); // Trigger change detection
  } 
  checkAllNodes(nodes: TreeNode[], checked: boolean): void {
    nodes.forEach(node => {
      node.checked = checked; // Set the checked state of the current node
      if (node.children) {
        this.checkAllNodes(node.children, checked); // Recursively set the checked state for children
      }
    });

  }

  // ...existing code...

  globalmoderationResults: Array<{ checkName: string; status: string }> = [];
  globalTemplateResponses: Array<{ templateName: string; result: string }> = [];

  // Calls the LLM evaluation API in batches
  async callEvalLLMBatch(
    templates: string[],
    type: 'Request' | 'Response'
  ): Promise<void> {
    const batchSize = 3;

    for (let i = 0; i < templates.length; i += batchSize) {
      const batchPromises = [];
      for (let j = i; j < i + batchSize && j < templates.length; j++) {
        batchPromises.push(this.callEvalLLM(templates[j], type));
      }
      await Promise.all(batchPromises)
        .then((results) => {
          console.log('Batch completed all', this.globalTemplateResponses);
        })
        .catch((error) => {
          console.error('Error in batch');
        });
    }
  }

  // Calls the LLM evaluation API for a single template
  callEvalLLM(
    templateName: string,
    type: 'Request' | 'Response'
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const payload = {
        Prompt: this.copyoffmPrompt,
        template_name: templateName,
        model_name: this.selectedLlmModel,
        AccountName: 'None',
        PortfolioName: 'None',
        userid: 'None',
        lotNumber: 1,
        temperature: '0',
        PromptTemplate: 'GoalPriority',
      };

      this.https.post(this.apiEndpoints.llm_eval, payload).subscribe(
        (res: any) => {
          console.log(res, 'Response from evalLLM');
          this.globalTemplateResponses.push({
            templateName: `${type}-${templateName}`, // Concatenate type here
            result: res.moderationResults.result,
            // timeTaken: res.timeTaken
          });
          resolve(res);
        },
        (error) => {
          console.error('Error:', error);
          reject(error);
        }
      );
    });
  }

  // Submits the chatbot and FM moderation requests
  copyoffmPrompt: string = '';
  async submitchatbot() {
    this.fmUserMessages=[]
    this.copyoffmPrompt = this.fmPrompt
    this.fmPrompt = ""
    this.fmUserMessages.push(this.copyoffmPrompt);
    this.displayModelPassed = false;
  this.displayModelFailed = false;
  this.displayTemplatePassed = false;
  this.displayTemplateFailed = false;
    this.globalTemplateResponses = [];
    this.globalmoderationResults = [];
    this.isFMModeSubmited = false
    this.submitted = true
    let selectedValues = this.showSelectedTreeValues()

      // Check if all boolean values are true
  if (
    this.displayModelPassed ||
    this.displayModelFailed ||
    this.displayTemplatePassed ||
    this.displayTemplateFailed ||
    this.displayModelPassed ||
    this.displayModelFailed ||
    this.displayTemplatePassed ||
    this.displayTemplateFailed
  ){
    // if selected from the toggle let InputModerationChecks = this.selectedInputModerationOptions
    console.log("selectedValues== in slected case ",selectedValues)
    let InputModerationChecks = selectedValues.modelBasedInputChecks
    let OutputModerationChecks = selectedValues.modelBasedOutputChecks

  


    // for fm moderation
    this.fmModeration(InputModerationChecks,OutputModerationChecks);

    // for eval llm

    const templatesArrayRequest = selectedValues.templateBasedRequestTemplates


    const responseModerationTemplates = selectedValues.templateBasedResponseTemplates


    console.log('Request Templates Array:', templatesArrayRequest);
    await this.callEvalLLMBatch(templatesArrayRequest, 'Request');

    console.log('Response Templates Array:', responseModerationTemplates);
    await this.callEvalLLMBatch(responseModerationTemplates, 'Response');

    console.log('All batches completed', this.globalTemplateResponses);

    // Start monitoring totalModerationChecks dynamically


  }else {
    // nav menu is un touched
    this.displayModelPassed = true;
  this.displayModelFailed = true;
  this.displayTemplatePassed = true;
  this.displayTemplateFailed = true;
    console.log("selectedValues== in unselected case ",selectedValues)
    let InputModerationChecks = this.selectedInputModerationOptions
    let OutputModerationChecks = this.selectedOutputModerationOptions

  


    // for fm moderation
    this.fmModeration(InputModerationChecks,OutputModerationChecks);

    // for eval llm

    const templatesArrayRequest = [
      'Prompt Injection Check',
      'Jailbreak Check',
      'Fairness and Bias Check',
      'Language Critique Coherence Check',
      'Language Critique Fluency Check',
      'Language Critique Grammar Check',
      'Language Critique Politeness Check',
    ];

    const responseModerationTemplates = [
      'Response Completeness Check',
      'Response Conciseness Check',
      'Response Language Critique Coherence Check',
      'Response Language Critique Fluency Check',
      'Response Language Critique Grammar Check',
      'Response Language Critique Politeness Check',
    ];

    console.log('Request Templates Array:', templatesArrayRequest);
    await this.callEvalLLMBatch(templatesArrayRequest, 'Request');

    console.log('Response Templates Array:', responseModerationTemplates);
    await this.callEvalLLMBatch(responseModerationTemplates, 'Response');

    console.log('All batches completed', this.globalTemplateResponses);

    // Start monitoring totalModerationChecks dynamically

  }
  
  }

  // Displays selected tree values
  showSelectedTreeValues() {
    const selectedValues = this.getSelectedTreeValues();
  
    console.log('Selected Values:');
    console.log('Model-Based Input Checks:', selectedValues.modelBasedInputChecks);
    console.log('Model-Based Output Checks:', selectedValues.modelBasedOutputChecks);
    console.log('Template-Based Request Templates:', selectedValues.templateBasedRequestTemplates);
    console.log('Template-Based Response Templates:', selectedValues.templateBasedResponseTemplates);
  
    // Set boolean values based on the presence of values in respective arrays
    this.displayModelPassed = selectedValues.modelBasedInputChecks.length > 0;
    this.displayModelFailed = selectedValues.modelBasedOutputChecks.length > 0;
    this.displayTemplatePassed = selectedValues.templateBasedRequestTemplates.length > 0;
    this.displayTemplateFailed = selectedValues.templateBasedResponseTemplates.length > 0;

    return selectedValues
  }

  get passedChecksCount(): number {
    return this.globalTemplateResponses.filter(
      (item) => item.result === 'PASSED'
    ).length;
  }

  get totalChecksCount(): number {
    return this.globalTemplateResponses.length;
  }
  get failedChecksCount(): number {
    return this.globalTemplateResponses.filter(
      (item) => item.result === 'FAILED'
    ).length;
  }

  /**
 * Returns the count of passed moderation checks.
 */
getPassedModerationChecksCount(): number {
  return this.globalmoderationResults.filter(item => item.status === 'PASSED').length;
}

/**
 * Returns the total count of moderation checks.
 */
getTotalModerationChecksCount(): number {
  return this.globalmoderationResults.length;
}

/**
 * Returns an array of passed moderation checks.
 */
getPassedModerationChecks(): Array<{ checkName: string; status: string }> {
  return this.globalmoderationResults.filter(item => item.status === 'PASSED');
}

/**
 * Returns the count of failed moderation checks.
 */
getFailedModerationChecksCount(): number {
  return this.globalmoderationResults.filter(item => item.status === 'FAILED').length;
}

/**
 * Returns an array of failed moderation checks.
 */
getFailedModerationChecks(): Array<{ checkName: string; status: string }> {
  return this.globalmoderationResults.filter(item => item.status === 'FAILED');
}


/**
 * Dynamically merges globalmoderationResults and globalTemplateResponses into a single array with keys 'name' and 'status'.
 */
get mergedModerationAndTemplateResults(): Array<{ name: string; status: string }> {
  const moderationResults = this.globalmoderationResults.map(item => ({
    name: item.checkName,
    status: item.status,
  }));

  const templateResponses = this.globalTemplateResponses.map(item => ({
    name: item.templateName,
    status: item.result,
  }));


  return [...moderationResults, ...templateResponses];
}

/**
 * Returns the count of passed checks from mergedModerationAndTemplateResults.
 */
get totalPassedChecks(): number {
  return this.mergedModerationAndTemplateResults.filter(item => item.status === 'PASSED').length;
}

/**
 * Returns the count of failed checks from mergedModerationAndTemplateResults.
 */
get totalFailedChecks(): number {
  return this.mergedModerationAndTemplateResults.filter(item => item.status === 'FAILED').length;
}

/**
 * Returns the total count of checks from mergedModerationAndTemplateResults.
 */
get totalModerationChecks(): number {
  return this.mergedModerationAndTemplateResults.length;
}


 //* Returns all selected values from the tree structure.



getSelectedTreeValues(): { 
  modelBasedInputChecks: string[], 
  modelBasedOutputChecks: string[], 
  templateBasedRequestTemplates: string[], 
  templateBasedResponseTemplates: string[] 
} {
  const selectedValues = {
    modelBasedInputChecks: [] as string[],
    modelBasedOutputChecks: [] as string[],
    templateBasedRequestTemplates: [] as string[],
    templateBasedResponseTemplates: [] as string[]
  };

  const traverseTree = (nodes: TreeNode[], parentCategory: string = '') => {
    nodes.forEach(node => {
      let currentCategory = parentCategory;

      if (node.id === 'group1') {
        currentCategory = 'modelBasedInputChecks';
      } else if (node.id === 'group2') {
        currentCategory = 'modelBasedOutputChecks';
      } else if (node.id === 'newGroup1') {
        currentCategory = 'templateBasedRequestTemplates';
      } else if (node.id === 'newGroup2') {
        currentCategory = 'templateBasedResponseTemplates';
      }

      if (node.checked && (!node.children || node.children.length === 0)) {
        switch (currentCategory) {
          case 'modelBasedInputChecks':
            selectedValues.modelBasedInputChecks.push(node.label);
            break;
          case 'modelBasedOutputChecks':
            selectedValues.modelBasedOutputChecks.push(node.label);
            break;
          case 'templateBasedRequestTemplates':
            selectedValues.templateBasedRequestTemplates.push(node.label);
            break;
          case 'templateBasedResponseTemplates':
            selectedValues.templateBasedResponseTemplates.push(node.label);
            break;
        }
      }

      // Recursively traverse children nodes
      if (node.children && node.children.length > 0) {
        traverseTree(node.children, currentCategory);
      }
    });
  };

  traverseTree(this.treeData);
  return selectedValues;
}


}