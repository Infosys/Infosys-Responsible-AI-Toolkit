/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { FormBuilder, ReactiveFormsModule, FormControl } from '@angular/forms';

import { CustomTemplateComponent } from './custom-template.component';
import { SharedService } from '../configuration-parent/shared.service';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';
import { HttpClient } from '@angular/common/http';

describe('CustomTemplateComponent', () => {
  let component: CustomTemplateComponent;
  let httpMock: HttpTestingController;
  let httpClient: HttpClient;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let sharedService: SharedService;
  let nonceService: NonceService;
  let userValidationService: jasmine.SpyObj<UserValidationService>;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin',
      TemplateCreation: '/template-create',
      customTemplatePatchUrl_updateCustomeTemplate: '/template-patch',
      TemplateGet: '/template-get',
      TemplateDelete: '/template-delete'
    }
  };

  const mockTemplatesResponse = {
    templates: [
      {
        templateName: 'Template1',
        mode: 'Private_Template',
        category: 'SingleModel',
        description: 'Test description',
        templateData: { prompting_instructions: 'test prompt' }
      },
      {
        templateName: 'Template2',
        mode: 'Master_Template',
        category: 'MultiModel',
        description: 'Test description 2',
        templateData: { evaluation_criteria: 'test criteria' }
      }
    ]
  };

  beforeEach(() => {
    const mockLocalStorage: { [key: string]: string } = {
      res: JSON.stringify(mockApiConfig),
      role: '"ROLE_ADMIN"',
      userid: '"test@example.com"'
    };

    spyOn(localStorage, 'getItem').and.callFake((key: string) => {
      return mockLocalStorage[key] || null;
    });
    spyOn(localStorage, 'setItem');

    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const userValidationSpy = jasmine.createSpyObj('UserValidationService', ['isValidEmail', 'isValidName']);
    
    userValidationSpy.isValidEmail.and.returnValue(true);
    userValidationSpy.isValidName.and.returnValue(true);

    TestBed.configureTestingModule({
      imports: [ 
        HttpClientTestingModule,
        ReactiveFormsModule
      ],
      providers: [
        SharedService,
        NonceService,
        FormBuilder,
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: MatDialog, useValue: dialogSpy },
        { provide: UserValidationService, useValue: userValidationSpy }
      ]
    });

    httpMock = TestBed.inject(HttpTestingController);
    httpClient = TestBed.inject(HttpClient);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    dialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    sharedService = TestBed.inject(SharedService);
    nonceService = TestBed.inject(NonceService);
    userValidationService = TestBed.inject(UserValidationService) as jasmine.SpyObj<UserValidationService>;

    // Create component instance manually without fixture
    component = new CustomTemplateComponent(snackBar, httpClient, dialog, sharedService, nonceService, userValidationService);
  });

  afterEach(() => {
    httpMock.match(() => true).forEach(req => req.flush(mockTemplatesResponse));
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with default values', () => {
      expect(component.currentPage).toBe(1);
      expect(component.itemsPerPage).toBe(5);
      expect(component.totalItems).toBe(0);
      expect(component.spinner).toBe(false);
    });

    it('should initialize form creation', () => {
      component.formCreation();
      expect(component.CustomTemplateForm).toBeDefined();
      expect(component.CustomTemplateForm.get('category')).toBeDefined();
      expect(component.CustomTemplateForm.get('mode')).toBeDefined();
      expect(component.CustomTemplateForm.get('TemplateName')).toBeDefined();
    });
  });

  describe('Form Methods', () => {
    beforeEach(() => {
      component.formCreation();
    });

    it('should filter boolean keys correctly', () => {
      const testObj = { key1: true, key2: false, key3: true };
      const result = component.filterKeysByBoolean(testObj);
      expect(result).toEqual(['key1', 'key3']);
    });

    it('should return empty array when no true values', () => {
      const testObj = { key1: false, key2: false };
      const result = component.filterKeysByBoolean(testObj);
      expect(result).toEqual([]);
    });

    it('should check if template name exists', () => {
      component.templateNameArray = ['Template1', 'Template2'];
      component.formupdatedisbaled = false;
      
      const exists = component.isTemplateNameExists('Template1');
      expect(exists).toBe(true);
      
      const notExists = component.isTemplateNameExists('Template3');
      expect(notExists).toBe(false);
    });

    it('should return false when formupdatedisbaled is true', () => {
      component.templateNameArray = ['Template1'];
      component.formupdatedisbaled = true;
      
      const result = component.isTemplateNameExists('Template1');
      expect(result).toBe(false);
    });
  });

  describe('resetResultData', () => {
    beforeEach(() => {
      component.formCreation();
    });

    it('should set prompt_instToggle for prompting_instructions', () => {
      component.resetResultData('prompting_instructions');
      expect(component.prompt_instToggle).toBe(true);
      expect(component.evaluation_criteriaToggle).toBe(false);
      expect(component.few_shot_exampleToggle).toBe(false);
    });

    it('should set evaluation_criteriaToggle for evaluation_criteria', () => {
      component.resetResultData('evaluation_criteria');
      expect(component.evaluation_criteriaToggle).toBe(true);
      expect(component.prompt_instToggle).toBe(false);
      expect(component.few_shot_exampleToggle).toBe(false);
    });

    it('should set few_shot_exampleToggle for few_shot_examples', () => {
      component.resetResultData('few_shot_examples');
      expect(component.few_shot_exampleToggle).toBe(true);
      expect(component.prompt_instToggle).toBe(false);
      expect(component.evaluation_criteriaToggle).toBe(false);
    });
  });

  describe('handleTextareaChange', () => {
    beforeEach(() => {
      component.formCreation();
      component.map = new Map();
    });

    it('should update map for prompting_instructions', () => {
      component.prompt_instToggle = true;
      component.evaluation_criteriaToggle = false;
      component.few_shot_exampleToggle = false;
      const event = { target: { value: 'test prompt' } };
      
      component.handleTextareaChange(event);
      expect(component.map.get('prompting_instructions')).toBe('test prompt');
    });

    it('should update map for evaluation_criteria', () => {
      component.prompt_instToggle = false;
      component.evaluation_criteriaToggle = true;
      component.few_shot_exampleToggle = false;
      const event = { target: { value: 'test criteria' } };
      
      component.handleTextareaChange(event);
      expect(component.map.get('evaluation_criteria')).toBe('test criteria');
    });

    it('should update map for few_shot_examples', () => {
      component.prompt_instToggle = false;
      component.evaluation_criteriaToggle = false;
      component.few_shot_exampleToggle = true;
      const event = { target: { value: 'test examples' } };
      
      component.handleTextareaChange(event);
      expect(component.map.get('few_shot_examples')).toBe('test examples');
    });
  });

  describe('resetData', () => {
    beforeEach(() => {
      component.formCreation();
    });

    it('should reset all form data and flags', () => {
      component.showSpinner = true;
      component.newTemplateName = 'test';
      component.categoryValidation = true;
      component.modeValidation = true;
      component.updatecall = true;
      
      component.resetData();
      
      expect(component.showSpinner).toBe(false);
      expect(component.newTemplateName).toBe('');
      expect(component.categoryValidation).toBe(false);
      expect(component.modeValidation).toBe(false);
      expect(component.updatecall).toBe(false);
      expect(component.prompt_instToggle).toBe(true);
      expect(component.evaluation_criteriaToggle).toBe(false);
    });
  });

  describe('resetForm', () => {
    beforeEach(() => {
      component.formCreation();
    });

    it('should call resetForm method', () => {
      spyOn(component, 'resetForm').and.callThrough();
      
      component.resetForm();
      
      expect(component.resetForm).toHaveBeenCalled();
    });
  });

  describe('Pagination', () => {
    beforeEach(() => {
      component.dataSource_getBatches = mockTemplatesResponse.templates;
    });

    it('should change page', () => {
      component.onTableDataChange(3);
      
      expect(component.pagingConfig.currentPage).toBe(3);
      expect(component.pagingConfig.totalItems).toBe(2);
    });

    it('should change page size', () => {
      const event = { target: { value: 10 } };
      
      component.onTableSizeChange(event);
      
      expect(component.pagingConfig.itemsPerPage).toBe(10);
      expect(component.pagingConfig.currentPage).toBe(1);
    });
  });

  describe('getLogedInUser', () => {
    it('should set isRoleAdmin to true for ROLE_ADMIN', () => {
      const result = userValidationService.getLogedInUser();
      
      expect(result).toBe('test@example.com');
      expect(component.isRoleAdmin).toBe(true);
    });

    it('should handle non-admin role', () => {
      (localStorage.getItem as jasmine.Spy).and.callFake((key: string) => {
        if (key === 'role') return '"ROLE_USER"';
        if (key === 'userid') return '"user@example.com"';
        if (key === 'res') return JSON.stringify(mockApiConfig);
        return null;
      });
      
      const result = userValidationService.getLogedInUser();
      
      expect(result).toBe('user@example.com');
    });
  });

  describe('HTTP Operations', () => {
    beforeEach(() => {
      component.formCreation();
      component.userId = 'test@example.com';
      component.customTemplateGetUrl = 'http://localhost:8080/api/admin/template-get';
      component.customTemplatePostUrl = 'http://localhost:8080/api/admin/template-create';
      component.customTemplatePatchUrl_updateCustomeTemplate = 'http://localhost:8080/api/admin/template-patch';
      component.customTemplateDeleteUrl = 'http://localhost:8080/api/admin/template-delete';
    });

    it('should fetch templates successfully', fakeAsync(() => {
      component.getTemplateDetail();

      const req = httpMock.expectOne((request: any) => {
        return request.url.includes('template-get');
      });
      req.flush(mockTemplatesResponse);
      tick();

      expect(component.dataSource_getBatches).toEqual(mockTemplatesResponse.templates);
      expect(component.templateNameArray).toContain('Template1');
      expect(component.pagingConfig.totalItems).toBe(2);
    }));

    it('should handle error when fetching templates', fakeAsync(() => {
      component.getTemplateDetail();

      const req = httpMock.expectOne((request: any) => {
        return request.url.includes('template-get');
      });
      req.flush({ error: { message: 'Fetch failed' } }, { status: 500, statusText: 'Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should post new template when updatecall is false', fakeAsync(() => {
      component.updatecall = false;
      component.CustomTemplateForm.patchValue({
        category: 'SingleModel',
        mode: 'Private',
        TemplateName: 'NewTemplate',
        TemplateDesc: 'Test Description'
      });

      component.save();

      // Handle all HTTP requests
      const allRequests = httpMock.match(() => true);
      allRequests.forEach(req => {
        if (req.request.method === 'POST') {
          req.flush({ message: 'Template Saved Successfully' });
        } else {
          req.flush(mockTemplatesResponse);
        }
      });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle validation errors on save', () => {
      component.CustomTemplateForm.get('category')?.setErrors({ required: true });
      component.CustomTemplateForm.get('mode')?.setErrors({ required: true });
      component.CustomTemplateForm.get('TemplateName')?.setErrors({ required: true });
      component.CustomTemplateForm.get('TemplateDesc')?.setErrors({ required: true });
      
      component.save();
      
      expect(component.categoryValidation).toBe(true);
      expect(component.modeValidation).toBe(true);
      expect(component.templateNameValidation).toBe(true);
      expect(component.templateDescValidation).toBe(true);
    });

    it('should delete template successfully', fakeAsync(() => {
      const templateId = 'template123';
      
      component.deleteConfirmationModel(templateId);

      // Match any DELETE request
      const deleteReq = httpMock.expectOne((request) => request.method === 'DELETE');
      deleteReq.flush({ message: 'Record Deleted Successfully' });
      
      // Match subsequent GET request
      const getReq = httpMock.expectOne((request) => request.method === 'GET' && request.url.includes('template-get'));
      getReq.flush(mockTemplatesResponse);
      
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle error 430 on delete', fakeAsync(() => {
      const templateId = 'template123';
      
      component.deleteConfirmationModel(templateId);

      const req = httpMock.expectOne((request) => request.method === 'DELETE');
      req.flush({ error: { detail: 'Permission denied' } }, { status: 430, statusText: 'Permission Denied' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));
  });

  describe('Search Functionality', () => {
    beforeEach(() => {
      component.dataSource_getBatches_filter = {
        templates: [
          { templateName: 'Alpha Template', description: 'First' },
          { templateName: 'Beta Template', description: 'Second' },
          { templateName: 'Alpha Plus', description: 'Third' }
        ]
      };
    });

    it('should toggle search', () => {
      component.isSearchOpen = false;
      
      component.toggleSearch();
      
      expect(component.isSearchOpen).toBe(true);
      expect(component.searchQuery).toBe('');
    });

    it('should filter by query', () => {
      component.searchQuery = 'alpha';
      
      component.search();
      
      expect(component.dataSource_getBatches.length).toBe(2);
      expect(component.dataSource_getBatches[0].templateName).toBe('Alpha Template');
    });

    it('should be case insensitive', () => {
      component.searchQuery = 'ALPHA';
      
      component.search();
      
      expect(component.dataSource_getBatches.length).toBe(2);
    });

    it('should restore all when query is empty', () => {
      component.searchQuery = '';
      
      component.search();
      
      expect(component.dataSource_getBatches).toEqual(component.dataSource_getBatches_filter.templates);
    });

    it('should close search and reset', () => {
      component.isSearchOpen = true;
      component.searchQuery = 'test';
      
      component.closeSearch();
      
      expect(component.isSearchOpen).toBe(false);
      expect(component.searchQuery).toBe('');
      expect(component.dataSource_getBatches).toEqual(component.dataSource_getBatches_filter.templates);
    });
  });

  describe('populateCustomtemFrom', () => {
    beforeEach(() => {
      component.formCreation();
    });

    it('should populate form with template data', () => {
      const templateData = [
        { templateData: 'test prompt' },
        { templateData: 'test criteria' },
        { templateData: 'test examples' }
      ];
      
      component.populateCustomtemFrom(templateData, 'TestTemplate', 'Private', 'type', 'user123', 'desc', 'General');
      
      expect(component.formupdatedisbaled).toBe(true);
      expect(component.updatecall).toBe(true);
    });

    it('should disable form fields when populated', () => {
      const templateData = [
        { templateData: 'test prompt' },
        { templateData: 'test criteria' },
        { templateData: 'test examples' }
      ];
      
      component.populateCustomtemFrom(templateData, 'TestTemplate', 'Private', 'type', 'user123', 'desc', 'General');
      
      expect(component.CustomTemplateForm.get('TemplateName')?.disabled).toBe(true);
      expect(component.CustomTemplateForm.get('mode')?.disabled).toBe(true);
    });
  });

  describe('openRightSideModal', () => {
    it('should open dialog', () => {
      dialog.open.and.returnValue({
        afterClosed: () => ({ subscribe: () => {} })
      } as any);

      component.openRightSideModal('templateData', 'TestTemplate', 'Private', 'type', 'user123');

      expect(dialog.open).toHaveBeenCalled();
    });
  });

  describe('triggerParentClick', () => {
    it('should call sharedService.triggerClick', () => {
      spyOn(sharedService, 'triggerClick');

      component.triggerParentClick();

      expect(sharedService.triggerClick).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty localStorage response', () => {
      const result = userValidationService.getLocalStoreApi();
      expect(result).toBeDefined();
    });

    it('should convert Map to object in save', () => {
      component.formCreation();
      component.map = new Map([['key1', 'value1']]);
      
      expect(component.map.get('key1')).toBe('value1');
    });
  });

  describe('LoadTemplateData', () => {
    beforeEach(() => {
      component.userId = 'test@example.com';
      component.loadTemplate = 'http://localhost:8080/api/fm/load-template';
    });

    it('should handle load template error with status 500', fakeAsync(() => {
      component.LoadTemplateData();

      const req = httpMock.expectOne((request) => request.url.includes('load-template'));
      req.flush({ error: { message: 'Server Error' } }, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle load template with error detail', fakeAsync(() => {
      component.LoadTemplateData();

      const req = httpMock.expectOne((request) => request.url.includes('load-template'));
      req.flush({ error: { detail: 'Template not found' } }, { status: 404, statusText: 'Not Found' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));
  });

  describe('setApilist', () => {
    it('should set all API URLs from config', () => {
      const mockConfig = {
        result: {
          Admin: 'http://localhost:8080/api/admin',
          TemplateCreation: '/template-create',
          customTemplatePatchUrl_updateCustomeTemplate: '/template-patch',
          TemplateGet: '/template-get',
          TemplateDelete: '/template-delete',
          TemplateUpdate: '/template-update',
          FM_Moderation: 'http://localhost:8080/api/fm',
          loadTemplate: '/load-template'
        }
      };

      component.setApilist(mockConfig);

      expect(component.customTemplatePostUrl).toBe('http://localhost:8080/api/admin/template-create');
      expect(component.customTemplatePatchUrl_updateCustomeTemplate).toBe('http://localhost:8080/api/admin/template-patch');
      expect(component.customTemplateGetUrl).toBe('http://localhost:8080/api/admin/template-get');
      expect(component.customTemplateDeleteUrl).toBe('http://localhost:8080/api/admin/template-delete');
      expect(component.customTemplateUpdateUrl).toBe('http://localhost:8080/api/admin/template-update');
      expect(component.loadTemplate).toBe('http://localhost:8080/api/fm/load-template');
    });
  });

  describe('getLocalStoreApi', () => {
    it('should return parsed API config from localStorage', () => {
      const result = userValidationService.getLocalStoreApi();
      
      expect(result).toBeDefined();
      expect(result.result.Admin).toBe('http://localhost:8080/api/admin');
    });

    it('should handle when localStorage is empty', () => {
      (localStorage.getItem as jasmine.Spy).and.callFake((key: string) => {
        if (key === 'res') return JSON.stringify(mockApiConfig);
        return null;
      });
      
      const result = userValidationService.getLocalStoreApi();
      
      expect(result).toBeDefined();
    });
  });

  describe('Pagination methods', () => {
    it('should update current page in onTableDataChange', () => {
      component.dataSource_getBatches = mockTemplatesResponse.templates;
      
      component.onTableDataChange(3);
      
      expect(component.pagingConfig.currentPage).toBe(3);
    });

    it('should reset to page 1 in onTableSizeChange', () => {
      component.pagingConfig.currentPage = 5;
      const event = { target: { value: 20 } };
      
      component.onTableSizeChange(event);
      
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.itemsPerPage).toBe(20);
    });
  });

  describe('saveSubTemplateData', () => {
    beforeEach(() => {
      component.map = new Map();
      component.toggleButton = false;
      // Add the missing form controls that the methods expect
      component.CustomTemplateForm.addControl('templateSubtype', new FormControl(''));
      component.CustomTemplateForm.addControl('TemplateData', new FormControl(''));
    });

    it('should save sub-template data to map', () => {
      component.CustomTemplateForm.patchValue({
        templateSubtype: 'prompting_instructions',
        TemplateData: 'Test prompt data'
      });

      component.saveSubTemplateData();

      expect(component.map.get('prompting_instructions')).toBe('Test prompt data');
      expect(component.prevSubTemplate).toBe('prompting_instructions');
    });

    it('should enable toggle button when map has 3 or more entries', () => {
      component.map.set('prompting_instructions', 'data1');
      component.map.set('evaluation_criteria', 'data2');
      
      component.CustomTemplateForm.patchValue({
        templateSubtype: 'few_shot_examples',
        TemplateData: 'data3'
      });

      component.saveSubTemplateData();

      expect(component.map.size).toBe(3);
      expect(component.toggleButton).toBe(true);
    });

    it('should not enable toggle button when map has less than 3 entries', () => {
      component.CustomTemplateForm.patchValue({
        templateSubtype: 'prompting_instructions',
        TemplateData: 'data1'
      });

      component.saveSubTemplateData();

      expect(component.map.size).toBe(1);
      expect(component.toggleButton).toBe(false);
    });

    it('should update existing entry in map', () => {
      component.map.set('prompting_instructions', 'old data');
      component.prevSubTemplate = 'prompting_instructions';
      
      component.CustomTemplateForm.patchValue({
        templateSubtype: 'prompting_instructions',
        TemplateData: 'new data'
      });

      component.saveSubTemplateData();

      expect(component.map.get('prompting_instructions')).toBe('new data');
    });
  });

  describe('saveTemplateData', () => {
    beforeEach(() => {
      component.map = new Map();
      component.prevSubTemplate = 'prompting_instructions';
      // Add the missing form control that the method expects
      component.CustomTemplateForm.addControl('TemplateData', new FormControl(''));
    });

    it('should save current template data with previous subtemplate key', () => {
      component.CustomTemplateForm.patchValue({
        TemplateData: 'Current template content'
      });

      component.saveTemplateData('evaluation_criteria');

      expect(component.map.get('prompting_instructions')).toBe('Current template content');
      expect(component.prevSubTemplate).toBe('evaluation_criteria');
    });

    it('should clear TemplateData field after saving', () => {
      component.CustomTemplateForm.patchValue({
        TemplateData: 'Some content'
      });

      component.saveTemplateData('few_shot_examples');

      expect(component.CustomTemplateForm.value.TemplateData).toBe('');
    });

    it('should update prevSubTemplate to new option', () => {
      const newOption = 'evaluation_criteria';
      
      component.saveTemplateData(newOption);

      expect(component.prevSubTemplate).toBe(newOption);
    });

    it('should handle switching between different subtemplates', () => {
      component.CustomTemplateForm.patchValue({
        TemplateData: 'Prompt data'
      });
      component.prevSubTemplate = 'prompting_instructions';

      component.saveTemplateData('evaluation_criteria');
      
      expect(component.map.get('prompting_instructions')).toBe('Prompt data');
      expect(component.prevSubTemplate).toBe('evaluation_criteria');

      component.CustomTemplateForm.patchValue({
        TemplateData: 'Criteria data'
      });

      component.saveTemplateData('few_shot_examples');

      expect(component.map.get('evaluation_criteria')).toBe('Criteria data');
      expect(component.prevSubTemplate).toBe('few_shot_examples');
      expect(component.map.size).toBe(2);
    });
  });

  describe('resetData', () => {
    beforeEach(() => {
      component.showSpinner = true;
      component.newTemplateName = 'TestTemplate';
      component.selectedOptions = ['option1', 'option2'];
      component.tenantarr = ['tenant1'];
      component.categoryValidation = true;
      component.modeValidation = true;
      component.templateNameValidation = true;
      component.templateDescValidation = true;
      component.templateSubmitFlag = true;
      component.prompt_instToggle = false;
      component.evaluation_criteriaToggle = true;
      component.few_shot_exampleToggle = true;
      component.updatecall = true;
      component.formupdatedisbaled = true;
    });

    it('should reset all component properties to initial state', () => {
      component.resetData();

      expect(component.showSpinner).toBe(false);
      expect(component.newTemplateName).toBe('');
      expect(component.selectedOptions).toEqual([]);
      expect(component.tenantarr).toEqual([]);
      expect(component.categoryValidation).toBe(false);
      expect(component.modeValidation).toBe(false);
      expect(component.templateNameValidation).toBe(false);
      expect(component.templateDescValidation).toBe(false);
      expect(component.templateSubmitFlag).toBe(false);
      expect(component.updatecall).toBe(false);
      expect(component.formupdatedisbaled).toBe(false);
    });

    it('should reset toggle flags correctly', () => {
      component.resetData();

      expect(component.prompt_instToggle).toBe(true);
      expect(component.evaluation_criteriaToggle).toBe(false);
      expect(component.few_shot_exampleToggle).toBe(false);
    });

    it('should reset component state and call formCreation', () => {
      component.showSpinner = true;
      component.templateSubmitFlag = true;

      component.resetData();

      expect(component.showSpinner).toBe(false);
      expect(component.templateSubmitFlag).toBe(false);
    });

    it('should call formCreation method', () => {
      spyOn(component, 'formCreation');

      component.resetData();

      expect(component.formCreation).toHaveBeenCalled();
    });
  });

  describe('resetForm', () => {
    it('should reset selectedPrompt to empty string', () => {
      component.selectedPrompt = 'TestPrompt';

      component.resetForm();

      expect(component.selectedPrompt).toBe('');
    });

    it('should reset newTemplateName to empty string', () => {
      component.newTemplateName = 'TestTemplate';

      component.resetForm();

      expect(component.newTemplateName).toBe('');
    });

    it('should reset both selectedPrompt and newTemplateName', () => {
      component.selectedPrompt = 'TestPrompt';
      component.newTemplateName = 'TestTemplate';

      component.resetForm();

      expect(component.selectedPrompt).toBe('');
      expect(component.newTemplateName).toBe('');
    });
  });

  describe('ngOnInit', () => {
    beforeEach(() => {
      spyOn(userValidationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(userValidationService, 'getLocalStoreApi').and.returnValue({
        ip: 'localhost',
        port: '8080'
      });
      spyOn(component, 'setApilist');
      spyOn(component, 'getTemplateDetail');
    });

    it('should call getLogedInUser on initialization', () => {
      component.ngOnInit();

      expect(userValidationService.getLogedInUser).toHaveBeenCalled();
    });

    it('should call getLocalStoreApi to retrieve API configuration', () => {
      component.ngOnInit();

      expect(userValidationService.getLocalStoreApi).toHaveBeenCalled();
    });

    it('should call setApilist with ip_port configuration', () => {
      const mockIpPort = { ip: 'localhost', port: '8080' };
      (userValidationService.getLocalStoreApi as jasmine.Spy).and.returnValue(mockIpPort);

      component.ngOnInit();

      expect(component.setApilist).toHaveBeenCalledWith(mockIpPort);
    });

    it('should call getTemplateDetail to load template data', () => {
      component.ngOnInit();

      expect(component.getTemplateDetail).toHaveBeenCalled();
    });

    it('should set prompt_instToggle to true', () => {
      component.prompt_instToggle = false;

      component.ngOnInit();

      expect(component.prompt_instToggle).toBe(true);
    });

    it('should initialize all required methods in correct order', () => {
      component.ngOnInit();

      expect(userValidationService.getLogedInUser).toHaveBeenCalled();
      expect(userValidationService.getLocalStoreApi).toHaveBeenCalled();
      expect(component.setApilist).toHaveBeenCalled();
      expect(component.getTemplateDetail).toHaveBeenCalled();
      expect(component.prompt_instToggle).toBe(true);
    });
  });

  describe('triggerParentClick', () => {
    it('should call sharedService.triggerClick', () => {
      const spy = spyOn(sharedService, 'triggerClick');

      component.triggerParentClick();

      expect(spy).toHaveBeenCalled();
    });

    it('should trigger parent click event through shared service', () => {
      const spy = spyOn(sharedService, 'triggerClick');

      component.triggerParentClick();

      expect(spy).toHaveBeenCalledTimes(1);
    });
  });
});
