/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UntypedFormBuilder, FormsModule } from '@angular/forms';

import { TemplateDataComponent } from './template-data.component';

describe('TemplateDataComponent', () => {
  let component: TemplateDataComponent;
  let fixture: ComponentFixture<TemplateDataComponent>;
  let httpMock: HttpTestingController;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<TemplateDataComponent>>;
  let httpClient: HttpClient;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin/',
      TemplateUpdate: 'template-update',
      TestTemplate: 'test-template'
    }
  };

  const mockDialogData = {
    dataValue: 'Test template data',
    templateName: 'TestTemplate',
    mode: 'Private',
    userid: 'test@example.com',
    template_type: 'prompting_instructions',
    templateTest: true
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));

    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
      declarations: [ TemplateDataComponent ],
      imports: [ HttpClientTestingModule, MatSnackBarModule, FormsModule ],
      providers: [
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
        { provide: MatSnackBar, useValue: snackBarSpy },
        UntypedFormBuilder
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TemplateDataComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    dialogRef = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<TemplateDataComponent>>;
    httpClient = TestBed.inject(HttpClient);
    
    fixture.detectChanges();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should initialize component with dialog data', () => {
      expect(component.templateData).toBe('Test template data');
      expect(component.templateName).toBe('TestTemplate');
      expect(component.mode).toBe('Private');
      expect(component.userId).toBe('test@example.com');
      expect(component.template_type).toBe('prompting_instructions');
      expect(component.templateTest).toBe(true);
    });

    it('should set API URLs from localStorage', () => {
      expect(component.customTemplateUpdateUrl).toBe('http://localhost:8080/api/admin/template-update');
      expect(component.testPromptUrl).toBe('http://localhost:8080/api/admin/test-template');
    });

    it('should call getLocalStoreApi and setApilist', () => {
      spyOn(component, 'getLocalStoreApi').and.callThrough();
      spyOn(component, 'setApilist').and.callThrough();

      component.ngOnInit();

      expect(component.getLocalStoreApi).toHaveBeenCalled();
      expect(component.setApilist).toHaveBeenCalled();
    });
  });

  describe('closeDialog', () => {
    it('should close the dialog', () => {
      component.closeDialog();

      expect(dialogRef.close).toHaveBeenCalled();
    });
  });

  describe('viewTemplateData', () => {
    it('should set update to true', () => {
      component.update = false;

      component.viewTemplateData();

      expect(component.update).toBe(true);
    });

    it('should change buttonName to Submit', () => {
      component.buttonName = 'Update';

      component.viewTemplateData();

      expect(component.buttonName).toBe('Submit');
    });
  });

  describe('updateData', () => {
    beforeEach(() => {
      component.userId = 'test@example.com';
      component.mode = 'Private';
      component.template_type = 'prompting_instructions';
      component.templateName = 'TestTemplate';
      component.templateData = 'Updated template data';
      component.customTemplateUpdateUrl = 'http://localhost:8080/api/admin/template-update';
    });

    it('should send PATCH request with correct payload', fakeAsync(() => {
      component.updateData();

      const req = httpMock.expectOne('http://localhost:8080/api/admin/template-update');
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual({
        userId: 'test@example.com',
        mode: 'Private',
        templateType: 'prompting_instructions',
        templateName: 'TestTemplate',
        templateData: 'Updated template data'
      });

      req.flush({ success: true });
      tick();

      expect(snackBar.open).toHaveBeenCalledWith('Template Saved Successfully', 'Close', { duration: 2000 });
      expect(dialogRef.close).toHaveBeenCalled();
    }));

    it('should handle successful update response', fakeAsync(() => {
      component.updateData();

      const req = httpMock.expectOne(component.customTemplateUpdateUrl);
      req.flush({ message: 'Updated successfully' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
      expect(dialogRef.close).toHaveBeenCalled();
    }));
  });

  describe('updateTemplate', () => {
    it('should call updateData when update is true', () => {
      component.update = true;
      spyOn(component, 'updateData');

      component.updateTemplate();

      expect(component.updateData).toHaveBeenCalled();
    });

    it('should not call updateData when update is false', () => {
      component.update = false;
      spyOn(component, 'updateData');

      component.updateTemplate();

      expect(component.updateData).not.toHaveBeenCalled();
    });
  });

  describe('submit', () => {
    beforeEach(() => {
      component.userId = 'test@example.com';
      component.templateName = 'TestTemplate';
      component.testPromptUrl = 'http://localhost:8080/api/admin/test-template';
    });

    it('should set promptValidation to true when selectedPrompt is empty', () => {
      component.selectedPrompt = '';
      component.promptValidation = false;

      component.submit();

      expect(component.promptValidation).toBe(true);
    });

    it('should return early when selectedPrompt is empty', () => {
      component.selectedPrompt = '';
      spyOn(httpClient, 'post');

      component.submit();

      expect(httpClient.post).not.toHaveBeenCalled();
    });

    it('should send POST request with correct payload when prompt is provided', fakeAsync(() => {
      component.selectedPrompt = 'Test prompt';
      component.spinner = false;

      component.submit();

      expect(component.spinner).toBe(true);

      const req = httpMock.expectOne('http://localhost:8080/api/admin/test-template');
      expect(req.request.method).toBe('POST');
      expect(req.request.body.Prompt).toBe('Test prompt');
      expect(req.request.body.userid).toBe('test@example.com');
      expect(req.request.body.template_name).toBe('TestTemplate');

      const mockResponse = {
        moderationResults: {
          response: [{
            analysis: 'Test analysis',
            result: 'PASSED'
          }]
        }
      };

      req.flush(mockResponse);
      tick();

      expect(component.testAnalysis).toBe('Test analysis');
      expect(component.testResult).toBe('PASSED');
      expect(component.spinner).toBe(false);
      expect(component.promptTestOutput).toBe(true);
    }));

    it('should handle error response and show snackbar', fakeAsync(() => {
      component.selectedPrompt = 'Test prompt';

      component.submit();

      const req = httpMock.expectOne(component.testPromptUrl);
      req.flush(
        { error: { message: 'Test failed' } },
        { status: 500, statusText: 'Internal Server Error' }
      );
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));

    it('should handle error with detail message', fakeAsync(() => {
      component.selectedPrompt = 'Test prompt';

      component.submit();

      const req = httpMock.expectOne(component.testPromptUrl);
      req.flush(
        { error: { detail: 'Detailed error message' } },
        { status: 400, statusText: 'Bad Request' }
      );
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    }));

    it('should show default error message when no error details provided', fakeAsync(() => {
      component.selectedPrompt = 'Test prompt';

      component.submit();

      const req = httpMock.expectOne(component.testPromptUrl);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    }));

    it('should reset promptValidation before submitting', () => {
      component.selectedPrompt = 'Test prompt';
      component.promptValidation = true;

      component.submit();

      expect(component.promptValidation).toBe(false);

      httpMock.expectOne(component.testPromptUrl);
    });
  });

  describe('resetForm', () => {
    it('should reset selectedPrompt to empty string', () => {
      component.selectedPrompt = 'Test prompt';

      component.resetForm();

      expect(component.selectedPrompt).toBe('');
    });

    it('should clear previously entered prompt', () => {
      component.selectedPrompt = 'Some long prompt text';

      component.resetForm();

      expect(component.selectedPrompt).toBe('');
    });
  });

  describe('getLocalStoreApi', () => {
    it('should return parsed API configuration from localStorage', () => {
      const result = component.getLocalStoreApi();

      expect(result).toEqual(mockApiConfig);
    });

    it('should return undefined when localStorage is empty', () => {
      localStorage.removeItem('res');

      const result = component.getLocalStoreApi();

      expect(result).toBeUndefined();
    });

    it('should handle null localStorage value', () => {
      localStorage.setItem('res', 'null');

      const result = component.getLocalStoreApi();

      expect(result).toBeNull();
    });
  });

  describe('setApilist', () => {
    it('should set customTemplateUpdateUrl correctly', () => {
      component.setApilist(mockApiConfig);

      expect(component.customTemplateUpdateUrl).toBe('http://localhost:8080/api/admin/template-update');
    });

    it('should set testPromptUrl correctly', () => {
      component.setApilist(mockApiConfig);

      expect(component.testPromptUrl).toBe('http://localhost:8080/api/admin/test-template');
    });

    it('should concatenate Admin and TemplateUpdate URLs', () => {
      const customConfig = {
        result: {
          Admin: 'http://example.com/api/',
          TemplateUpdate: 'update-endpoint',
          TestTemplate: 'test-endpoint'
        }
      };

      component.setApilist(customConfig);

      expect(component.customTemplateUpdateUrl).toBe('http://example.com/api/update-endpoint');
      expect(component.testPromptUrl).toBe('http://example.com/api/test-endpoint');
    });
  });

  describe('Component initialization', () => {
    it('should initialize with default values', () => {
      const newComponent = new TemplateDataComponent(
        dialogRef,
        httpClient,
        snackBar,
        new UntypedFormBuilder(),
        {}
      );

      expect(newComponent.selectedPrompt).toBe('');
      expect(newComponent.update).toBe(false);
      expect(newComponent.buttonName).toBe('Update');
      expect(newComponent.promptTestOutput).toBe(false);
      expect(newComponent.spinner).toBe(false);
      expect(newComponent.promptValidation).toBe(false);
    });
  });

  describe('Integration tests', () => {
    it('should complete full update workflow', fakeAsync(() => {
      component.viewTemplateData();
      expect(component.update).toBe(true);
      expect(component.buttonName).toBe('Submit');

      component.templateData = 'New data';
      component.updateTemplate();

      const req = httpMock.expectOne(component.customTemplateUpdateUrl);
      req.flush({ success: true });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
      expect(dialogRef.close).toHaveBeenCalled();
    }));

    it('should complete full test prompt workflow', fakeAsync(() => {
      component.selectedPrompt = 'Test prompt for validation';
      component.submit();

      expect(component.spinner).toBe(true);

      const req = httpMock.expectOne(component.testPromptUrl);
      req.flush({
        moderationResults: {
          response: [{
            analysis: 'Prompt is safe',
            result: 'PASSED'
          }]
        }
      });
      tick();

      expect(component.spinner).toBe(false);
      expect(component.promptTestOutput).toBe(true);
      expect(component.testAnalysis).toBe('Prompt is safe');
      expect(component.testResult).toBe('PASSED');
    }));
  });
});
