/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';

import { FmParametersComponent } from './fm-parameters.component';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';

describe('FmParametersComponent', () => {
  let component: FmParametersComponent;
  let fixture: ComponentFixture<FmParametersComponent>;
  let httpMock: HttpTestingController;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let userValidationService: jasmine.SpyObj<UserValidationService>;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin/',
      Admin_DataRecogGrplist: 'recog-list',
      Admin_AccMasterList: 'acc-master',
      Fm_Config_Entry: 'fm-config-entry',
      Fm_Config_EntryList: 'fm-config-entrylist',
      Fm_Config_Data: 'fm-config-data',
      Fm_Config_DataUpdate: 'fm-config-update',
      Fm_Config_Delete: 'fm-config-delete',
      Fm_Config_ModCheck: 'fm-config-modcheck',
      Fm_Config_TopicList: 'fm-config-topiclist',
      Fm_Config_OutputModCheck: 'fm-config-outputmodcheck'
    }
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));
    localStorage.setItem('userid', JSON.stringify('test@example.com'));

    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const userValidationSpy = jasmine.createSpyObj('UserValidationService', ['isValidEmail', 'isValidName']);
    userValidationSpy.isValidEmail.and.returnValue(true);
    userValidationSpy.isValidName.and.returnValue(true);

    await TestBed.configureTestingModule({
      declarations: [ FmParametersComponent ],
      imports: [ 
        MatSnackBarModule, 
        HttpClientTestingModule, 
        MatDialogModule,
        ReactiveFormsModule
      ],
      providers: [
        { provide: MatSnackBar, useValue: snackBarSpy },
        NonceService,
        { provide: UserValidationService, useValue: userValidationSpy }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FmParametersComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    userValidationService = TestBed.inject(UserValidationService) as jasmine.SpyObj<UserValidationService>;
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Component Initialization', () => {
    it('should initialize form with default values', () => {
      expect(component.FmConfigResponseForm).toBeDefined();
      expect(component.FmConfigResponseForm.get('PromptInjectionThreshold')?.value).toBe(7);
      expect(component.FmConfigResponseForm.get('JailbreakThreshold')?.value).toBe(7);
      expect(component.FmConfigResponseForm.get('RefusalThreshold')?.value).toBe(7);
    });

    it('should have all required recognizer list items', () => {
      expect(component.recognizerList).toContain('PERSON');
      expect(component.recognizerList).toContain('LOCATION');
      expect(component.recognizerList).toContain('EMAIL_ADDRESS');
      expect(component.recognizerList).toContain('CREDIT_CARD');
    });

    it('should have gibberish labels defined', () => {
      expect(component.gibberishLabels).toEqual(['word salad', 'noise', 'mild gibberish', 'clean']);
    });

    it('should have banned categories defined', () => {
      expect(component.bannedCategories).toEqual(['Cf', 'Co', 'Cn', 'So', 'Sc']);
    });

    it('should initialize all selection flags to false', () => {
      expect(component.allSelectedInput).toBe(false);
      expect(component.allSelectedInput2).toBe(false);
      expect(component.allSelectedInput3).toBe(false);
      expect(component.allSelectedInput4).toBe(false);
      expect(component.allSelectedInput5).toBe(false);
    });
  });

  describe('fromCreation', () => {
    it('should create form with all required controls', () => {
      component.fromCreation();
      
      expect(component.FmConfigResponseForm.get('inputModChecks')).toBeDefined();
      expect(component.FmConfigResponseForm.get('outputModChecks')).toBeDefined();
      expect(component.FmConfigResponseForm.get('PromptInjectionThreshold')).toBeDefined();
      expect(component.FmConfigResponseForm.get('recognizerNamesToDetect')).toBeDefined();
    });

    it('should set all controls as required', () => {
      component.fromCreation();
      
      const inputModChecks = component.FmConfigResponseForm.get('inputModChecks');
      const toxicityThreshold = component.FmConfigResponseForm.get('ToxicityThreshold');
      
      expect(inputModChecks?.hasError('required')).toBeDefined();
      expect(toxicityThreshold?.hasError('required')).toBeDefined();
    });

    it('should initialize threshold values correctly', () => {
      component.fromCreation();
      
      expect(component.FmConfigResponseForm.get('ToxicityThreshold')?.value).toBe(6);
      expect(component.FmConfigResponseForm.get('ProfanityCountThreshold')?.value).toBe(10);
      expect(component.FmConfigResponseForm.get('SentimentThreshold')?.value).toBe(-0.01);
    });
  });

  describe('ngOnInit', () => {
    it('should call getLogedInUser', fakeAsync(() => {
      spyOn(userValidationService, 'getLogedInUser');
      spyOn(component, 'getSelectDRopDownArrray').and.stub();
      component.ngOnInit();
      expect(userValidationService.getLogedInUser).toHaveBeenCalled();
    }));

    it('should call getLocalStoreApi', fakeAsync(() => {
      spyOn(userValidationService, 'getLocalStoreApi').and.callThrough();
      spyOn(component, 'getSelectDRopDownArrray').and.stub();
      component.ngOnInit();
      expect(userValidationService.getLocalStoreApi).toHaveBeenCalled();
    }));

    it('should call setApilist with ip_port', fakeAsync(() => {
      spyOn(component, 'setApilist');
      spyOn(component, 'getSelectDRopDownArrray').and.stub();
      component.ngOnInit();
      expect(component.setApilist).toHaveBeenCalled();
    }));

    it('should call getSelectDRopDownArrray', fakeAsync(() => {
      spyOn(component, 'getSelectDRopDownArrray').and.stub();
      component.ngOnInit();
      expect(component.getSelectDRopDownArrray).toHaveBeenCalled();
    }));
  });

  describe('getLogedInUser', () => {
    it('should retrieve user from localStorage', () => {
      const result = userValidationService.getLogedInUser();
      expect(result).toBe('test@example.com');
    });

    it('should return userId when valid email', () => {
      localStorage.setItem('userid', JSON.stringify('user@test.com'));
      const result = userValidationService.getLogedInUser();
      expect(component.userId).toBe('user@test.com');
    });

    it('should return "NA" when localStorage is empty', () => {
      localStorage.removeItem('userid');
      const result = userValidationService.getLogedInUser();
      expect(result).toBe('NA');
    });

    it('should validate email using validation service', () => {
      userValidationService.getLogedInUser();
      expect(userValidationService.isValidEmail).toHaveBeenCalled();
    });
  });

  describe('getLocalStoreApi', () => {
    it('should retrieve API config from localStorage', () => {
      const result = userValidationService.getLocalStoreApi();
      expect(result).toEqual(mockApiConfig);
    });

    it('should return parsed JSON from localStorage', () => {
      const result = userValidationService.getLocalStoreApi();
      expect(result.result.Admin).toBe('http://localhost:8080/api/admin/');
    });
  });

  describe('setApilist', () => {
    it('should set all API URLs', () => {
      component.setApilist(mockApiConfig);
      
      expect(component.admin_list_rec_get_list).toBe('http://localhost:8080/api/admin/recog-list');
      expect(component.fm_config_entry).toBe('http://localhost:8080/api/admin/fm-config-entry');
      expect(component.fm_config_modCheck).toBe('http://localhost:8080/api/admin/fm-config-modcheck');
    });

    it('should concatenate Admin and endpoint URLs', () => {
      component.setApilist(mockApiConfig);
      expect(component.fm_config_topicList).toContain('http://localhost:8080/api/admin/');
      expect(component.fm_config_outputModCheck).toContain('fm-config-outputmodcheck');
    });
  });

  describe('submit', () => {
    beforeEach(() => {
      component.parAccount = 'TestAccount';
      component.parPortfolio = 'TestPortfolio';
      component.FmConfigResponseForm.patchValue({
        inputModChecks: ['check1'],
        outputModChecks: ['check2'],
        PromptInjectionThreshold: 7,
        JailbreakThreshold: 7,
        recognizerNamesToDetect: ['PERSON'],
        recognizerNamesToBlock: ['EMAIL'],
        RefusalThreshold: 7,
        ToxicityThreshold: 6,
        SevereToxicityThreshold: 6,
        ObsceneThreshold: 6,
        ThreatThreshold: 6,
        InsultThreshold: 6,
        IdentityAttackThreshold: 6,
        SexualExplicitThreshold: 6,
        ProfanityCountThreshold: 10,
        RestrictedtopicThreshold: 7,
        SentimentThreshold: -0.01,
        BanCodeThreshold: 7,
        InvisibleTextCountThreshold: 10,
        GibberishThreshold: 7,
        Restrictedtopics: ['topic1'],
        ThemeName: 'TestTheme',
        Themethresold: 6,
        ThemeTexts: 'text1,text2',
        gibberishLabels: ['noise'],
        bannedCategories: ['Cf']
      });
    });

    it('should call setFMConfigData with correct payload', () => {
      spyOn(component, 'setFMConfigData');
      component.submit();
      expect(component.setFMConfigData).toHaveBeenCalled();
    });

    it('should divide thresholds by 10 in payload', () => {
      spyOn(component, 'setFMConfigData');
      component.submit();
      
      const call = (component.setFMConfigData as jasmine.Spy).calls.mostRecent();
      const payload = call.args[0];
      
      expect(payload.ModerationCheckThresholds.PromptinjectionThreshold).toBe(0.7);
      expect(payload.ModerationCheckThresholds.ToxicityThresholds.ToxicityThreshold).toBe(0.6);
    });

    it('should split ThemeTexts by comma', () => {
      spyOn(component, 'setFMConfigData');
      component.submit();
      
      const call = (component.setFMConfigData as jasmine.Spy).calls.mostRecent();
      const payload = call.args[0];
      
      expect(payload.ModerationCheckThresholds.CustomTheme.ThemeTexts).toEqual(['text1', 'text2']);
    });

    it('should include account and portfolio in payload', () => {
      spyOn(component, 'setFMConfigData');
      component.submit();
      
      const call = (component.setFMConfigData as jasmine.Spy).calls.mostRecent();
      const payload = call.args[0];
      
      expect(payload.AccountName).toBe('TestAccount');
      expect(payload.PortfolioName).toBe('TestPortfolio');
    });

    it('should handle empty ThemeTexts', () => {
      component.FmConfigResponseForm.patchValue({ ThemeTexts: '' });
      spyOn(component, 'setFMConfigData');
      
      component.submit();
      
      const call = (component.setFMConfigData as jasmine.Spy).calls.mostRecent();
      const payload = call.args[0];
      
      expect(payload.ModerationCheckThresholds.CustomTheme.ThemeTexts).toEqual([]);
    });
  });

  describe('setFMConfigData', () => {
    const mockPayload = {
      AccountName: 'Test',
      PortfolioName: 'Portfolio',
      ModerationChecks: [],
      OutputModerationChecks: [],
      ModerationCheckThresholds: {}
    };

    beforeEach(() => {
      component.fm_config_entry = 'http://localhost:8080/api/admin/fm-config-entry';
    });

    it('should make POST request to fm_config_entry', () => {
      component.setFMConfigData(mockPayload);
      
      const req = httpMock.expectOne(component.fm_config_entry);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockPayload);
      req.flush({ status: 'True' });
    });

    it('should show success snackbar when status is True', fakeAsync(() => {
      component.setFMConfigData(mockPayload);
      
      const req = httpMock.expectOne(component.fm_config_entry);
      req.flush({ status: 'True' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Mapping Added Successfully',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));

    it('should show error snackbar when status is False', fakeAsync(() => {
      component.setFMConfigData(mockPayload);
      
      const req = httpMock.expectOne(component.fm_config_entry);
      req.flush({ status: 'False' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Mapping already exists for this Account',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));

    it('should handle HTTP error', fakeAsync(() => {
      component.setFMConfigData(mockPayload);
      
      const req = httpMock.expectOne(component.fm_config_entry);
      req.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    }));
  });

  describe('getSelectDRopDownArrray', () => {
    beforeEach(() => {
      component.fm_config_modCheck = 'http://localhost:8080/modcheck';
      component.fm_config_topicList = 'http://localhost:8080/topiclist';
      component.fm_config_outputModCheck = 'http://localhost:8080/outputmodcheck';
    });

    it('should fetch InputModerationChecks', fakeAsync(() => {
      component.getSelectDRopDownArrray();
      
      const req1 = httpMock.expectOne(component.fm_config_modCheck);
      req1.flush({ dataList: ['check1', 'check2'] });
      
      const req2 = httpMock.expectOne(component.fm_config_topicList);
      req2.flush({ dataList: [] });
      
      const req3 = httpMock.expectOne(component.fm_config_outputModCheck);
      req3.flush({ dataList: [] });
      
      tick();
      
      expect(component.InputModerationChecks).toEqual(['check1', 'check2']);
    }));

    it('should fetch Restrictedtopics', fakeAsync(() => {
      component.getSelectDRopDownArrray();
      
      httpMock.expectOne(component.fm_config_modCheck).flush({ dataList: [] });
      httpMock.expectOne(component.fm_config_topicList).flush({ dataList: ['topic1', 'topic2'] });
      httpMock.expectOne(component.fm_config_outputModCheck).flush({ dataList: [] });
      tick();
      
      expect(component.Restrictedtopics).toEqual(['topic1', 'topic2']);
    }));

    it('should fetch OutputModerationChecks', fakeAsync(() => {
      component.getSelectDRopDownArrray();
      
      httpMock.expectOne(component.fm_config_modCheck).flush({ dataList: [] });
      httpMock.expectOne(component.fm_config_topicList).flush({ dataList: [] });
      
      const req = httpMock.expectOne(component.fm_config_outputModCheck);
      req.flush({ dataList: ['output1', 'output2'] });
      tick();
      
      expect(component.OutputModerationChecks).toEqual(['output1', 'output2']);
    }));

    it('should handle error with status 430', fakeAsync(() => {
      component.getSelectDRopDownArrray();
      
      const req = httpMock.expectOne(component.fm_config_modCheck);
      req.flush({}, { status: 430, statusText: 'Error' });
      
      httpMock.expectOne(component.fm_config_topicList).flush({ dataList: [] });
      httpMock.expectOne(component.fm_config_outputModCheck).flush({ dataList: [] });
      tick();
      
      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle generic error', fakeAsync(() => {
      component.getSelectDRopDownArrray();
      
      const req = httpMock.expectOne(component.fm_config_modCheck);
      req.flush({}, { status: 500, statusText: 'Server Error' });
      
      httpMock.expectOne(component.fm_config_topicList).flush({ dataList: [] });
      httpMock.expectOne(component.fm_config_outputModCheck).flush({ dataList: [] });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    }));
  });

  describe('toggleAllSelection1 - Input Moderation', () => {
    beforeEach(() => {
      component.select1 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), value: 'opt1' },
              { select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), value: 'opt2' }
            ];
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy('close')
      } as any;
    });

    it('should select all options when checked', () => {
      const event = { checked: true };
      component.toggleAllSelection1(event);
      
      expect(component.allSelected1).toBe(true);
      expect(component.listShowlist1.size).toBe(2);
    });

    it('should deselect all options when unchecked', () => {
      component.allSelected1 = true;
      component.listShowlist1.add('opt1');
      const event = { checked: false };
      
      component.toggleAllSelection1(event);
      
      expect(component.allSelected1).toBe(false);
    });
  });

  describe('selectInputModeration', () => {
    it('should update allSelectedInput status', () => {
      component.select1 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'opt1' },
              { selected: true, value: 'opt2' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectInputModeration();
      
      expect(component.allSelectedInput).toBe(true);
    });

    it('should set allSelected1 to false when not all selected', () => {
      component.select1 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'opt1' },
              { selected: false, value: 'opt2' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectInputModeration();
      
      expect(component.allSelectedInput).toBe(false);
      expect(component.allSelected1).toBe(false);
    });
  });

  describe('toggleAllSelection2 - Output Moderation', () => {
    beforeEach(() => {
      component.select2 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), value: 'opt1' }
            ];
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy('close')
      } as any;
    });

    it('should toggle allSelected2 flag', () => {
      const event = { checked: true };
      component.toggleAllSelection2(event);
      expect(component.allSelected2).toBe(true);
    });
  });

  describe('selectOutputModeration', () => {
    it('should update selection status', () => {
      component.select2 = {
        options: {
          forEach: (callback: any) => {
            [{ selected: true, value: 'opt1' }].forEach(callback);
          }
        }
      } as any;
      
      component.selectOutputModeration();
      expect(component.allSelectedInput2).toBe(true);
    });
  });

  describe('toggleAllSelection3 - Recognizer List', () => {
    beforeEach(() => {
      component.select3 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), value: 'PERSON' },
              { select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), value: 'EMAIL_ADDRESS' }
            ];
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy('close')
      } as any;
    });

    it('should select all recognizers when checked', () => {
      const event = { checked: true };
      component.toggleAllSelection3(event);
      expect(component.allSelected3).toBe(true);
      expect(component.listShowlist3.size).toBe(2);
      expect(component.c3).toBe(true);
    });

    it('should deselect all recognizers when unchecked', () => {
      component.allSelected3 = true;
      component.listShowlist3.add('PERSON');
      const event = { checked: false };
      
      component.toggleAllSelection3(event);
      
      expect(component.allSelected3).toBe(false);
      expect(component.c3).toBe(false);
    });

    it('should hide listbox element when selecting all', () => {
      const mockElement = document.createElement('div');
      mockElement.setAttribute('role', 'listbox');
      document.body.appendChild(mockElement);
      
      const event = { checked: true };
      component.toggleAllSelection3(event);
      
      expect(mockElement.style.display).toBe('none');
      document.body.removeChild(mockElement);
    });
  });

  describe('toggleAllSelection4 - Recognizer Block List', () => {
    beforeEach(() => {
      component.select4 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { select: jasmine.createSpy(), deselect: jasmine.createSpy(), value: 'EMAIL' },
              { select: jasmine.createSpy(), deselect: jasmine.createSpy(), value: 'CREDIT_CARD' }
            ];
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy()
      } as any;
    });

    it('should select all block list items when checked', () => {
      const event = { checked: true };
      component.toggleAllSelection4(event);
      expect(component.allSelected4).toBe(true);
      expect(component.listShowlist4.size).toBe(2);
    });

    it('should deselect all block list items when unchecked', () => {
      component.allSelected4 = true;
      component.listShowlist4.add('EMAIL');
      const event = { checked: false };
      
      component.toggleAllSelection4(event);
      
      expect(component.allSelected4).toBe(false);
    });
  });

  describe('selectrecognizerList', () => {
    it('should update allSelectedInput3 when all items selected', () => {
      component.select3 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'PERSON' },
              { selected: true, value: 'EMAIL' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerList();
      
      expect(component.allSelectedInput3).toBe(true);
    });

    it('should set allSelected3 to false when not all selected', () => {
      component.select3 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'PERSON' },
              { selected: false, value: 'EMAIL' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerList();
      
      expect(component.allSelectedInput3).toBe(false);
      expect(component.allSelected3).toBe(false);
    });

    it('should manage listShowlist3 correctly', () => {
      component.listShowlist3.add('OLD_VALUE');
      component.select3 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'PERSON' },
              { selected: false, value: 'EMAIL' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerList();
      
      expect(component.listShowlist3.has('PERSON')).toBe(true);
      expect(component.listShowlist3.has('EMAIL')).toBe(false);
    });
  });

  describe('selectrecognizerListtoblock', () => {
    it('should update allSelectedInput4 when all items selected', () => {
      component.select4 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'EMAIL' },
              { selected: true, value: 'PHONE' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerListtoblock();
      
      expect(component.allSelectedInput4).toBe(true);
    });

    it('should set allSelected4 to false when not all selected', () => {
      component.select4 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'EMAIL' },
              { selected: false, value: 'PHONE' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerListtoblock();
      
      expect(component.allSelectedInput4).toBe(false);
      expect(component.allSelected4).toBe(false);
    });

    it('should manage listShowlist4 correctly', () => {
      component.listShowlist4.add('OLD_VALUE');
      component.select4 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'EMAIL' },
              { selected: false, value: 'PHONE' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectrecognizerListtoblock();
      
      expect(component.listShowlist4.has('EMAIL')).toBe(true);
      expect(component.listShowlist4.has('PHONE')).toBe(false);
    });
  });

  describe('toggleAllSelection5 - Restricted Topics', () => {
    beforeEach(() => {
      component.select5 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { select: jasmine.createSpy(), deselect: jasmine.createSpy(), value: 'topic1' },
              { select: jasmine.createSpy(), deselect: jasmine.createSpy(), value: 'topic2' }
            ];
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy()
      } as any;
      
      component.select4 = {
        options: {
          forEach: jasmine.createSpy()
        }
      } as any;
    });

    it('should select all restricted topics when checked', () => {
      const event = { checked: true };
      component.toggleAllSelection5(event);
      expect(component.allSelected5).toBe(true);
      expect(component.listShowlist5.size).toBe(2);
    });

    it('should deselect all restricted topics when unchecked', () => {
      component.allSelected5 = true;
      component.listShowlist5.add('topic1');
      const event = { checked: false };
      
      component.toggleAllSelection5(event);
      
      expect(component.allSelected5).toBe(false);
    });
  });

  describe('selectRestrictedtopics', () => {
    it('should update allSelectedInput5 when all topics selected', () => {
      component.select5 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'topic1' },
              { selected: true, value: 'topic2' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectRestrictedtopics();
      
      expect(component.allSelectedInput5).toBe(true);
    });

    it('should set allSelected5 to false when not all selected', () => {
      component.select5 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'topic1' },
              { selected: false, value: 'topic2' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectRestrictedtopics();
      
      expect(component.allSelectedInput5).toBe(false);
      expect(component.allSelected5).toBe(false);
    });

    it('should manage listShowlist5 correctly', () => {
      component.listShowlist5.add('OLD_TOPIC');
      component.select5 = {
        options: {
          forEach: (callback: any) => {
            const mockOptions = [
              { selected: true, value: 'topic1' },
              { selected: false, value: 'topic2' }
            ];
            mockOptions.forEach(callback);
          }
        }
      } as any;
      
      component.selectRestrictedtopics();
      
      expect(component.listShowlist5.has('topic1')).toBe(true);
      expect(component.listShowlist5.has('topic2')).toBe(false);
    });
  });

  describe('Gibberish Labels Selection', () => {
    beforeEach(() => {
      component.selectGibberishLabels = {
        options: {
          forEach: (callback: any) => {
            const options = [
              { select: jasmine.createSpy(), deselect: jasmine.createSpy(), selected: true }
            ];
            options.forEach(callback);
          }
        }
      } as any;
    });

    it('should toggle all gibberish labels', () => {
      const event = { checked: true };
      component.toggleAllSelectionGibberishLabels(event);
      expect(component.allSelectedGibberishLabels).toBe(true);
    });

    it('should update gibberish labels selection status', () => {
      component.selectsGibberishLabels();
      expect(component.allSelectedGibberishLabels).toBe(true);
    });
  });

  describe('Banned Categories Selection', () => {
    beforeEach(() => {
      component.selectBannedCategories = {
        options: {
          forEach: (callback: any) => {
            [{ select: jasmine.createSpy(), deselect: jasmine.createSpy(), selected: true }].forEach(callback);
          }
        }
      } as any;
    });

    it('should toggle all banned categories', () => {
      const event = { checked: true };
      component.toggleAllSelectionBannedCategories(event);
      expect(component.allSelectedBannedCategories).toBe(true);
    });

    it('should update banned categories selection status', () => {
      component.selectsBannedCategories();
      expect(component.allSelectedBannedCategories).toBe(true);
    });
  });
});
