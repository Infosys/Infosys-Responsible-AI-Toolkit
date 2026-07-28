/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/

// ====== API REQUEST INTERFACES ======
export interface ApiEndpoints {
  fm_api?: string;
  fm_api_openAi?: string;
  llm_eval?: string;
  fm_api_time?: string;
  admin_fm_admin_UserRole?: string;
  nemo_TopicalRail?: string;
  nemo_JailBreakRail?: string;
  nemo_ModerationRail?: string;
  nemo_FactCheckRail?: string;
  rag_Retrieval?: string;
  Moderationlayer_COV?: string;
  Moderationlayer_openaiCOT?: string;
  Moderationlayer_gEval?: string;
  RAG_gEval?: string;
  Moderationlayer_Translate?: string;
  fm_config_getAttributes?: string;
  tokenImp?: string;
  UncertainApi?: string;
  thotApi?: string;
  privacyAnonApi?: string;
  privacyAnalyzeApi?: string;
  privacyEncrypt?: string;
  privacyDecrypt?: string;
  privacyRecognizersList?: string;
  profAnzApiUrl?: string;
  profCenApiUrl?: string;
  explApiUrl?: string;
  FairnessApiUrl?: string;
  lightRag?: string;
  Admin_getEmbedings?: string;
  rag_FileUpload?: string;
  hall_cov?: string;
  hall_cot?: string;
  hall_thot?: string;
  rag_image?: string;
  rag_video?: string;
  promptRecommendation?: string;
  GetTemplates?: string;
  Moderationlayer_getTemplates?: string;
}

// ====== PRIVACY API INTERFACES ======
export interface PrivacyAnalyzePayload {
  inputText: string;
  portfolio?: string | null;
  account?: string | null;
  exclusionList?: string;
  user: string;
  piiEntitiesToBeRedacted?: string[] | null;
  nlp?: string | null;
}

export interface PrivacyAnonymizePayload extends PrivacyAnalyzePayload {
  fakeData: boolean;
  redactionType: string;
}

export interface PrivacyEncryptPayload {
  inputText: string;
  piiEntitiesToBeRedacted?: string[] | null;
  nlp?: string | null;
}

// ====== PROFANITY API INTERFACES ======
export interface ProfanityPayload {
  inputText: string;
  user: string;
}

// ====== EXPLAINABILITY API INTERFACES ======
export interface ExplainabilityPayload {
  inputPrompt: string;
  modelName: string;
}

export interface COVPayload {
  complexity: string;
  modelName: string;
  translate: string;
  inputPrompt: string;
}

// ====== FAIRNESS API INTERFACES ======
export interface FairnessPayload {
  response: string;
  evaluator: string;
}

// ====== FM API INTERFACES ======
export interface FMConfigPayload {
  AccountName: string;
  PortfolioName: string;
}

export interface LLMEvalPayload {
  Prompt: string;
  template_name: string;
  model_name: string;
  AccountName: string;
  PortfolioName: string;
  userid: string;
  lotNumber: number;
  Context: string;
  Concise_Context: string;
  Reranked_Context: string;
  temperature: string;
  PromptTemplate: string;
}

export interface OpenAIPayload {
  Prompt: string;
  temperature: string;
  model_name: string;
}

// ====== RAG API INTERFACES ======
export interface RAGRetrievalPayload {
  fileupload: boolean;
  text: string;
  vectorstoreid?: string | null;
  llmtype? :string | null;
  embeddingmodel? :string | null;
}

export interface GEvalPayload {
  context: string;
  content: string;
  model_name: string;
}

export interface SummaryEvalPayload {
  text: string;
  response: string;
  sourcetext: string;
  llmtype?: string;
}

// ====== MULTIMODAL API INTERFACES ======
export interface MultimodalUploadData {
  files: File[];
  text: string;
}

// ====== NEMO API INTERFACES ======
export interface NemoCheckPayload {
  text: string;
}

// ====== USER ROLE INTERFACES ======
export interface UserRolePayload {
  role: string;
}

export interface UserRoleResponse {
  isOpenAI: boolean;
  selfReminder: string;
}

// ====== API RESPONSE INTERFACES ======
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface HallucinationResponse {
  status: boolean;
  errorMessage?: string;
  response: {
    text?: string;
    hallScore?: number;
    source?: string;
    section?: string;
    [key: string]: any;
  };
}

export interface LightRagResponse {
  status: boolean;
  errorMessage?: string;
  response: {
    text?: string;
    hallScore?: number;
    GEval?: any;
    timeTaken?: string;
    [key: string]: any;
  };
}

// ====== FILE UPLOAD INTERFACES ======
export interface FileUploadPayload {
  payload: File;
  select_model: string;
}

export interface EmbeddingPayload {
  userId: string;
}

// ====== TIME API RESPONSE ======
export interface TimeApiResponse {
  OpenAIInteractionTime: string;
  requestModeration: string;
  responseModeration: string;
}

// ====== RECOMMENDATION API ======
export interface RecommendationResponse {
  prompts: { [key: string]: string[] };
}

// ====== RECOGNITION LIST RESPONSE ======
export interface RecognizerResponse {
  'Available Recognizers': string[];
}
