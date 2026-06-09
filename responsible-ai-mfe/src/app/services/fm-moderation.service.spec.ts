/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { FmModerationService } from './fm-moderation.service';
import { NonceService } from '../nonce.service';

describe('FmModerationService', () => {
  let service: FmModerationService;
  let httpMock: HttpTestingController;
  let nonceService: NonceService;

  const mockIpPortData = {
    result: {
      FM_Moderation: 'http://test.com/fm',
      Moderationlayer_completions: '/completions',
      Moderationlayer_openai: '/openai',
      EvalLLM: '/eval',
      Moderationlayer_ModerationTime: '/time',
      Admin: 'http://test.com/admin',
      Admin_userRole: '/userRole',
      Nemo: 'http://test.com/nemo',
      Nemo_TopicalRail: '/topical',
      Nemo_JailBreakRail: '/jailbreak',
      Nemo_ModerationRail: '/moderation',
      Nemo_FactCheckRail: '/factcheck',
      Rag: 'http://test.com/rag',
      RAG_RetrievalKepler: '/retrieval',
      Moderationlayer_COV: '/cov',
      Moderationlayer_openaiCOT: '/cot',
      Moderationlayer_gEval: '/geval',
      Fm_GETTEMPLATES: '/templates',
      Moderationlayer_Translate: '/translate',
      Fm_Config_GetAttributes: '/config',
      Llm_Explain: 'http://test.com/explain',
      Token_Importance: '/token',
      Uncertainty: '/uncertain',
      OpenAiThot: '/thot',
      Privacy: 'http://test.com/privacy',
      Privacy_text_anonymize: '/anonymize',
      Privacy_text_analyze: '/analyze',
      Privacy_encrypt: '/encrypt',
      Privacy_decrypt: '/decrypt',
      Profanity: 'http://test.com/profanity',
      Profanity_text_analyze: '/analyze',
      Profanity_text_censor: '/censor',
      Explainability: 'http://test.com/explainability',
      FairnessAzure: 'http://test.com/fairness',
      FairUnstructure: '/unstructured',
      Admin_Rag: 'http://test.com/admin-rag',
      Admin_getEmbedings: '/embeddings',
      RAG_FileUpload: '/upload',
      RagCOV: '/cov',
      RagCOT: '/cot',
      RagTHOT: '/thot',
      GETACCTEMPMAP: '/templates',
      PromptRecommendation: '/recommendation',
      Privacy_getRecognizer: '/recognizers',
      RagGEVAL: '/geval',
      LiteRAG: '/lightrag'
    }
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        FmModerationService,
        { provide: NonceService, useValue: { getNonce: () => 'test-nonce' } }
      ]
    });
    service = TestBed.inject(FmModerationService);
    httpMock = TestBed.inject(HttpTestingController);
    nonceService = TestBed.inject(NonceService);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('retrieveLocalStorageData', () => {
    it('should retrieve data from localStorage when all keys exist', () => {
      localStorage.setItem('role', JSON.stringify('ROLE_ML'));
      localStorage.setItem('res', JSON.stringify(mockIpPortData));
      localStorage.setItem('userid', JSON.stringify('user123'));

      const result = service.retrieveLocalStorageData();

      expect(result.ip_port).toEqual(mockIpPortData);
      expect(result.Account_Role).toBe('ROLE_ML');
      expect(service.roleML).toBe(true);
      expect(service.loggedINuserId).toBe('user123');
    });

    it('should handle missing role in localStorage', () => {
      localStorage.removeItem('role');
      
      const result = service.retrieveLocalStorageData();
      
      expect(result.Account_Role).toBeUndefined();
      expect(service.roleML).toBe(false);
    });

    it('should handle missing res in localStorage', () => {
      localStorage.removeItem('res');
      
      const result = service.retrieveLocalStorageData();
      
      expect(result.ip_port).toBeUndefined();
    });

    it('should set roleML to true when role is ROLE_ML', () => {
      localStorage.setItem('role', JSON.stringify('ROLE_ML'));
      
      service.retrieveLocalStorageData();
      
      expect(service.roleML).toBe(true);
    });

    it('should not set roleML to true when role is not ROLE_ML', () => {
      localStorage.setItem('role', JSON.stringify('ROLE_USER'));
      service.roleML = false;
      
      service.retrieveLocalStorageData();
      
      expect(service.roleML).toBe(false);
    });
  });

  describe('setApiList', () => {
    it('should set all API endpoints correctly', () => {
      service.setApiList(mockIpPortData);

      expect(service.apiEndpoints.fm_api).toBe('http://test.com/fm/completions');
      expect(service.apiEndpoints.fm_api_openAi).toBe('http://test.com/fm/openai');
      expect(service.apiEndpoints.llm_eval).toBe('http://test.com/fm/eval');
      expect(service.apiEndpoints.privacyAnalyzeApi).toBe('http://test.com/privacy/analyze');
      expect(service.apiEndpoints.FairnessApiUrl).toBe('http://test.com/fairness/unstructured');
    });

    it('should set nemo endpoints correctly', () => {
      service.setApiList(mockIpPortData);

      expect(service.apiEndpoints.nemo_TopicalRail).toBe('http://test.com/nemo/topical');
      expect(service.apiEndpoints.nemo_JailBreakRail).toBe('http://test.com/nemo/jailbreak');
      expect(service.apiEndpoints.nemo_ModerationRail).toBe('http://test.com/nemo/moderation');
    });
  });

  describe('fetchApiUrl', () => {
    it('should call retrieveLocalStorageData and setApiList', () => {
      spyOn(service, 'retrieveLocalStorageData').and.returnValue({ ip_port: mockIpPortData, Account_Role: 'ROLE_ML' });
      spyOn(service, 'setApiList');

      service.fetchApiUrl();

      expect(service.retrieveLocalStorageData).toHaveBeenCalled();
      expect(service.setApiList).toHaveBeenCalledWith(mockIpPortData);
    });
  });

  describe('updateData', () => {
    it('should update the dataSource with new data', (done) => {
      const testData = { test: 'data' };

      service.currentData.subscribe(data => {
        if (data !== null) {
          expect(data).toEqual(testData);
          done();
        }
      });

      service.updateData(testData);
    });
  });

  describe('updateNemoGaurrailResponse', () => {
    it('should update the nemoGaurrailResponse with new data', (done) => {
      const testData = { nemo: 'response' };

      service.currentNemoGaurrailResponse.subscribe(data => {
        if (data !== null) {
          expect(data).toEqual(testData);
          done();
        }
      });

      service.updateNemoGaurrailResponse(testData);
    });
  });

  describe('MultiModal operations', () => {
    it('should update MultiModal with all parameters', () => {
      service.updateMultiModal(true, 'user123', ['template1'], 'test prompt', 'file.jpg');

      const multiModal = service.getMultiModal();
      expect(multiModal.show).toBe(true);
      expect(multiModal.userId).toBe('user123');
      expect(multiModal.templateList).toEqual(['template1']);
      expect(multiModal.prompt).toBe('test prompt');
      expect(multiModal.file).toBe('file.jpg');
    });

    it('should update specific key-value pair in MultiModal', () => {
      service.updateMultiModalKeyVal('show', true);
      service.updateMultiModalKeyVal('userId', 'newUser');

      const multiModal = service.getMultiModal();
      expect(multiModal.show).toBe(true);
      expect(multiModal.userId).toBe('newUser');
    });

    it('should reset MultiModal to default state', () => {
      service.updateMultiModal(true, 'user123', ['template1'], 'test', 'file');
      service.resetMultiModal();

      const multiModal = service.getMultiModal();
      expect(multiModal.show).toBe(false);
      expect(multiModal.userId).toBe('');
      expect(multiModal.templateList).toEqual([]);
      expect(multiModal.prompt).toBe('');
      expect(multiModal.file).toBe('');
      expect(multiModal.fairnessRes).toBeNull();
    });

    it('should get current MultiModal state', () => {
      service.updateMultiModal(true, 'user456', ['temp1', 'temp2'], 'prompt', 'image.png');
      
      const result = service.getMultiModal();
      
      expect(result.show).toBe(true);
      expect(result.userId).toBe('user456');
      expect(result.templateList.length).toBe(2);
    });
  });

  describe('getTemplates', () => {
    it('should call GET API with logged-in user ID', () => {
      service.loggedINuserId = 'user123';
      service.apiEndpoints.GetTemplates = 'http://test.com/templates/';

      service.getTemplates().subscribe();

      const req = httpMock.expectOne('http://test.com/templates/user123');
      expect(req.request.method).toBe('GET');
      req.flush({ templates: [] });
    });
  });

  describe('moderationGetTemplates', () => {
    it('should call GET API with correct endpoint', () => {
      service.loggedINuserId = 'user123';
      service.apiEndpoints.Moderationlayer_getTemplates = 'http://test.com/mod-templates';

      service.moderationGetTemplates().subscribe();

      const req = httpMock.expectOne('http://test.com/mod-templates/user123');
      expect(req.request.method).toBe('GET');
      req.flush({ templates: [] });
    });
  });

  describe('getFMService', () => {
    beforeEach(() => {
      service.apiEndpoints.fm_api = 'http://test.com/fm';
    });

    it('should call deployed API when fmlocalselected is false', () => {
      const testData = { prompt: 'test' };
      
      service.getFMService(testData, false)?.subscribe();

      const req = httpMock.expectOne('http://test.com/fm');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(testData);
      req.flush({ result: 'success' });
    });

    it('should return null when fmlocalselected is neither true nor false', () => {
      const result = service.getFMService({}, 'invalid' as any);
      
      expect(result).toBeNull();
    });
  });

  describe('checkLocalStorageForKeys', () => {
    it('should return true when both keys exist', () => {
      localStorage.setItem('selectedPortfolio', 'portfolio1');
      localStorage.setItem('selectedAccount', 'account1');

      const result = service.checkLocalStorageForKeys();

      expect(result).toBe(true);
    });

    it('should return false when selectedPortfolio is missing', () => {
      localStorage.removeItem('selectedPortfolio');
      localStorage.setItem('selectedAccount', 'account1');

      const result = service.checkLocalStorageForKeys();

      expect(result).toBe(false);
    });

    it('should return false when selectedAccount is missing', () => {
      localStorage.setItem('selectedPortfolio', 'portfolio1');
      localStorage.removeItem('selectedAccount');

      const result = service.checkLocalStorageForKeys();

      expect(result).toBe(false);
    });

    it('should return false when both keys are missing', () => {
      localStorage.removeItem('selectedPortfolio');
      localStorage.removeItem('selectedAccount');

      const result = service.checkLocalStorageForKeys();

      expect(result).toBe(false);
    });
  });

  describe('Privacy API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.privacyAnalyzeApi = 'http://test.com/privacy/analyze';
      service.apiEndpoints.privacyAnonApi = 'http://test.com/privacy/anonymize';
      service.apiEndpoints.privacyEncrypt = 'http://test.com/privacy/encrypt';
      service.apiEndpoints.privacyDecrypt = 'http://test.com/privacy/decrypt';
      service.apiEndpoints.privacyRecognizersList = 'http://test.com/privacy/recognizers';
    });

    it('should call Privacy Analyze API', () => {
      const payload = { inputText: 'test text', user: 'user123' };
      
      service.callPrivacyAnalyze(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/privacy/analyze');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(payload);
      req.flush({ result: 'analyzed' });
    });

    it('should call Privacy Anonymize API', () => {
      const payload = { inputText: 'test text', user: 'user123', fakeData: true, redactionType: 'mask' };
      
      service.callPrivacyAnonymize(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/privacy/anonymize');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'anonymized' });
    });

    it('should call Privacy Encrypt API', () => {
      const payload = { inputText: 'test text' };
      
      service.callPrivacyEncrypt(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/privacy/encrypt');
      expect(req.request.method).toBe('POST');
      req.flush({ encrypted: 'data' });
    });

    it('should call Privacy Decrypt API', () => {
      const payload = { encryptedText: 'encrypted' };
      
      service.callPrivacyDecrypt(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/privacy/decrypt');
      expect(req.request.method).toBe('POST');
      req.flush({ decrypted: 'data' });
    });

    it('should get recognizers list', () => {
      service.getRecognizers().subscribe();

      const req = httpMock.expectOne('http://test.com/privacy/recognizers');
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('accept')).toBe('application/json');
      req.flush({ recognizers: [] });
    });
  });

  describe('Profanity API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.profAnzApiUrl = 'http://test.com/profanity/analyze';
      service.apiEndpoints.profCenApiUrl = 'http://test.com/profanity/censor';
    });

    it('should call Profanity Analyze API', () => {
      const payload = { inputText: 'test text', user: 'user123' };
      
      service.callProfanityAnalyze(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/profanity/analyze');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'analyzed' });
    });

    it('should call Profanity Censor API', () => {
      const payload = { inputText: 'test text', user: 'user123' };
      
      service.callProfanityCensor(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/profanity/censor');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'censored' });
    });
  });

  describe('Explainability API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.explApiUrl = 'http://test.com/explainability';
      service.apiEndpoints.Moderationlayer_COV = 'http://test.com/cov';
    });

    it('should call Explainability API', () => {
      const payload = { inputPrompt: 'test', modelName: 'gpt-4' };
      
      service.callExplainability(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/explainability');
      expect(req.request.method).toBe('POST');
      req.flush({ explanation: 'result' });
    });

    it('should call COV API', () => {
      const payload = { complexity: 'high', model_name: 'gpt-4', translate: 'true', text: 'test text' };
      
      service.callCOV(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/cov');
      expect(req.request.method).toBe('POST');
      req.flush({ cov_result: 'result' });
    });
  });

  describe('Fairness API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.FairnessApiUrl = 'http://test.com/fairness/';
    });

    it('should call Fairness API with URL-encoded body', () => {
      const payload = { response: 'test response', evaluator: 'evaluator1' };
      
      service.callFairness(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/fairness/');
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Content-Type')).toBe('application/x-www-form-urlencoded');
      req.flush({ fairness: 'result' });
    });

    it('should call Fairness Image API', () => {
      const formData = new FormData();
      formData.append('image', new Blob(['test']));
      
      service.callFairnessImage(formData).subscribe();

      const req = httpMock.expectOne('http://test.com/fairness/fairness_image');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'success' });
    });
  });

  describe('FM Moderation API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.fm_config_getAttributes = 'http://test.com/config';
      service.apiEndpoints.llm_eval = 'http://test.com/eval';
      service.apiEndpoints.fm_api_openAi = 'http://test.com/openai';
      service.apiEndpoints.admin_fm_admin_UserRole = 'http://test.com/userrole';
      service.apiEndpoints.fm_api_time = 'http://test.com/time';
    });

    it('should call FM Config API and map response', () => {
      const payload = { AccountName: 'testAccount', PortfolioName: 'testPortfolio' };
      
      service.callFMConfig(payload).subscribe(result => {
        expect(result.response).toBeDefined();
        expect(result.comp_Payload).toBeDefined();
      });

      const req = httpMock.expectOne('http://test.com/config');
      expect(req.request.method).toBe('POST');
      req.flush({ config: 'data' });
    });

    it('should call LLM Eval API', () => {
      const payload = { 
        Prompt: 'test', 
        template_name: 'template1',
        model_name: 'gpt-4',
        AccountName: 'testAccount',
        PortfolioName: 'testPortfolio',
        userid: 'user123',
        lotNumber: 1,
        Context: 'context',
        Concise_Context: 'concise',
        Reranked_Context: 'reranked',
        temperature: '0.7',
        PromptTemplate: 'template'
      };
      
      service.callLLMEval(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/eval');
      expect(req.request.method).toBe('POST');
      req.flush({ evaluation: 'result' });
    });

    it('should call OpenAI API', () => {
      const payload = { Prompt: 'test prompt', temperature: '0.7', model_name: 'gpt-4' };
      
      service.callOpenAI(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/openai');
      expect(req.request.method).toBe('POST');
      req.flush({ response: 'result' });
    });

    it('should get user role', () => {
      const payload = { role: 'admin' };
      
      service.getUserRole(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/userrole');
      expect(req.request.method).toBe('POST');
      req.flush({ role: 'admin' });
    });

    it('should get FM API time', () => {
      service.getFMTime().subscribe();

      const req = httpMock.expectOne('http://test.com/time');
      expect(req.request.method).toBe('GET');
      req.flush({ time: '2026-01-02' });
    });
  });

  describe('RAG API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.rag_Retrieval = 'http://test.com/rag/retrieval';
      service.apiEndpoints.lightRag = 'http://test.com/rag/lightrag';
      service.apiEndpoints.RAG_gEval = 'http://test.com/rag/geval';
      service.apiEndpoints.rag_FileUpload = 'http://test.com/rag/upload';
      service.apiEndpoints.Admin_getEmbedings = 'http://test.com/embeddings';
    });

    it('should call RAG Retrieval API', () => {
      const payload = { fileupload: false, text: 'test query' };
      
      service.callRAGRetrieval(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/rag/retrieval');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'retrieved' });
    });

    it('should call Light RAG API', () => {
      const formData = new FormData();
      
      service.callLightRAG(formData).subscribe();

      const req = httpMock.expectOne('http://test.com/rag/lightrag');
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'success' });
    });

    it('should call G-Eval API', () => {
      const payload = { text: 'test text', response: 'test response', sourcetext: 'source text' };
      
      service.callGEval(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/rag/geval');
      expect(req.request.method).toBe('POST');
      req.flush({ score: 0.9 });
    });

    it('should upload RAG file', () => {
      const formData = new FormData();
      
      service.uploadRAGFile(formData).subscribe();

      const req = httpMock.expectOne('http://test.com/rag/upload');
      expect(req.request.method).toBe('POST');
      req.flush({ uploaded: true });
    });

    it('should get embeddings with URL-encoded body', () => {
      const payload = { userId: 'user123' };
      
      service.getEmbeddings(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/embeddings');
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Content-Type')).toBe('application/x-www-form-urlencoded');
      req.flush({ embeddings: [] });
    });
  });

  describe('Multimodal and Nemo API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.nemo_ModerationRail = 'http://test.com/nemo/moderation';
    });

    it('should call Multimodal API', () => {
      const url = 'http://test.com/multimodal';
      const formData = new FormData();
      
      service.callMultimodal(url, formData).subscribe();

      const req = httpMock.expectOne(url);
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'success' });
    });

    it('should call Nemo Check API', () => {
      const apiUrl = 'http://test.com/nemo/check';
      const formData = new FormData();
      
      service.callNemoCheck(apiUrl, formData).subscribe();

      const req = httpMock.expectOne(apiUrl);
      expect(req.request.method).toBe('POST');
      req.flush({ checked: true });
    });

    it('should call Nemo Moderation Rail API', () => {
      const formData = new FormData();
      
      service.callNemoModerationRail(formData).subscribe();

      const req = httpMock.expectOne('http://test.com/nemo/moderation');
      expect(req.request.method).toBe('POST');
      req.flush({ moderated: true });
    });
  });

  describe('Recommendation and Translation API Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.promptRecommendation = 'http://test.com/recommendation';
      service.apiEndpoints.Moderationlayer_Translate = 'http://test.com/translate';
    });

    it('should get recommendations', () => {
      service.getRecommendations().subscribe();

      const req = httpMock.expectOne('http://test.com/recommendation');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({});
      req.flush({ recommendations: [] });
    });

    it('should call Translation API', () => {
      const payload = { text: 'Hello', target_language: 'es' };
      
      service.callTranslate(payload).subscribe();

      const req = httpMock.expectOne('http://test.com/translate');
      expect(req.request.method).toBe('POST');
      req.flush({ translated: 'Hola' });
    });
  });

  describe('File Upload Methods', () => {
    beforeEach(() => {
      service.apiEndpoints.rag_FileUpload = 'http://test.com/upload';
    });

    it('should upload file with payload structure', () => {
      const file = new File(['content'], 'test.txt');
      
      service.uploadFileWithPayload(file, 'gpt-4').subscribe();

      const req = httpMock.expectOne('http://test.com/upload');
      expect(req.request.method).toBe('POST');
      req.flush({ uploaded: true });
    });

    it('should upload file with default model', () => {
      const file = new File(['content'], 'test.txt');
      
      service.uploadFileWithPayload(file).subscribe();

      const req = httpMock.expectOne('http://test.com/upload');
      expect(req.request.method).toBe('POST');
      req.flush({ uploaded: true });
    });

    it('should upload multiple files', () => {
      const files = [
        new File(['content1'], 'test1.txt'),
        new File(['content2'], 'test2.txt')
      ];
      
      service.uploadMultipleFiles(files, 'gpt-4').subscribe();

      const req = httpMock.expectOne('http://test.com/upload');
      expect(req.request.method).toBe('POST');
      req.flush({ uploaded: true });
    });
  });

  describe('Image Processing API Methods', () => {
    it('should analyze profanity in image', () => {
      const endpoint = 'http://test.com/profanity-image';
      const formData = new FormData();
      
      service.analyzeProfanityImageAdvanced(formData, endpoint).subscribe();

      const req = httpMock.expectOne(endpoint);
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'analyzed' });
    });

    it('should analyze privacy in image', () => {
      const endpoint = 'http://test.com/privacy-image';
      const formData = new FormData();
      
      service.analyzePrivacyImageAdvanced(formData, endpoint).subscribe();

      const req = httpMock.expectOne(endpoint);
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'analyzed' });
    });

    it('should anonymize privacy in image', () => {
      const endpoint = 'http://test.com/anonymize-image';
      const formData = new FormData();
      
      service.anonymizePrivacyImageAdvanced(formData, endpoint).subscribe();

      const req = httpMock.expectOne(endpoint);
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'anonymized' });
    });

    it('should process fairness for image', () => {
      const endpoint = 'http://test.com/fairness-image';
      const formData = new FormData();
      
      service.processFairnessImage(formData, endpoint).subscribe();

      const req = httpMock.expectOne(endpoint);
      expect(req.request.method).toBe('POST');
      req.flush({ result: 'processed' });
    });
  });

  describe('Utility Methods', () => {
    it('should create form data with files', () => {
      const files = [new File(['test'], 'test.txt')];
      
      const formData = service.createFileFormData(files);
      
      expect(formData).toBeInstanceOf(FormData);
    });

    it('should create form data with files and additional data', () => {
      const files = [new File(['test'], 'test.txt')];
      const additionalData = { key1: 'value1', key2: 'value2' };
      
      const formData = service.createFileFormData(files, additionalData);
      
      expect(formData).toBeInstanceOf(FormData);
    });
  });

  describe('Error Handling', () => {
    it('should handle 430 error with detail message', () => {
      const error = { status: 430, error: { detail: 'Custom error' } };
      
      service.handleError(error).subscribe(
        () => fail('should have thrown an error'),
        (err) => {
          expect(err.success).toBe(false);
          expect(err.error).toBe('Custom error');
          expect(err.status).toBe(430);
        }
      );
    });

    it('should handle 500 error with generic message', () => {
      const error = { status: 500, error: {} };
      
      service.handleError(error).subscribe(
        () => fail('should have thrown an error'),
        (err) => {
          expect(err.error).toBe('Internal Server Error. Please try again later.');
          expect(err.status).toBe(500);
        }
      );
    });

    it('should handle error with fallback message', () => {
      const error = { status: 400, error: {} };
      
      service.handleError(error).subscribe(
        () => fail('should have thrown an error'),
        (err) => {
          expect(err.error).toBe('API has failed');
        }
      );
    });

    it('should extract error.error.message when available', () => {
      const error = { status: 400, error: { message: 'Validation failed' } };
      
      service.handleError(error).subscribe(
        () => fail('should have thrown an error'),
        (err) => {
          expect(err.error).toBe('Validation failed');
        }
      );
    });
  });
});
