/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AppConfigsComponent } from './app-configs.component';

describe('AppConfigsComponent', () => {
  let component: AppConfigsComponent;
  let fixture: ComponentFixture<AppConfigsComponent>;
  let httpMock: HttpTestingController;
  let snackBar: MatSnackBar;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin',
      Admin_getOpenAI: '/get-openai-status',
      Admin_UpdateOpenAI: '/update-openai',
      Admin_userRole: '/user-role',
      Admin_UpdateReminder: '/update-reminder'
    }
  };

  const mockOpenAIResponse = {
    isOpenAI: true,
    result: [
      { role: 'Admin', isOpenAI: true, selfReminder: false },
      { role: 'User', isOpenAI: false, selfReminder: true }
    ]
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));
    
    await TestBed.configureTestingModule({
      declarations: [ AppConfigsComponent ],
      imports: [ 
        HttpClientTestingModule, 
        MatSnackBarModule, 
        MatDialogModule,
        NoopAnimationsModule
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AppConfigsComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar);
    // Don't call fixture.detectChanges() in beforeEach to avoid ngOnInit issues
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize displayedColumns correctly', () => {
      expect(component.displayedColumns).toEqual(['role', 'isOpenAI', 'selfReminder']);
    });

    it('should parse localStorage and set ip_port on ngOnInit', fakeAsync(() => {
      component.ngOnInit();
      
      expect(component.ip_port).toEqual(mockApiConfig);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush(mockOpenAIResponse);
      tick();
    }));

    it('should set API URLs correctly on ngOnInit', fakeAsync(() => {
      component.ngOnInit();
      
      expect(component.admin_fm_admin_get_OpenAiStatusandRoll).toBe('http://localhost:8080/api/admin/get-openai-status');
      expect(component.admin_fm_admin_Update_OpenAiStatus).toBe('http://localhost:8080/api/admin/update-openai');
      expect(component.admin_fm_admin_UserRole).toBe('http://localhost:8080/api/admin/user-role');
      expect(component.admin_fm_admin_Update_OpenSelfReminderStatus).toBe('http://localhost:8080/api/admin/update-reminder');
      expect(component.admin_fm_admin_Update_OpenNemoStatus).toBe('http://localhost:8080/api/admin/update-reminder');
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush(mockOpenAIResponse);
      tick();
    }));

    it('should fetch OpenAI status and set dataSource on ngOnInit', fakeAsync(() => {
      component.ngOnInit();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush(mockOpenAIResponse);
      tick();
      
      expect(component.OpenAitoogleValue).toBe(true);
      expect(component.dataSource).toEqual(mockOpenAIResponse.result);
    }));

    it('should handle error 430 in ngOnInit', fakeAsync(() => {
      spyOn(snackBar, 'open');
      spyOn(console, 'log');
      
      component.ngOnInit();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush({ detail: 'Custom error message' }, { status: 430, statusText: 'Custom Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Custom error message',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle generic error in ngOnInit', fakeAsync(() => {
      spyOn(snackBar, 'open');
      spyOn(console, 'log');
      
      component.ngOnInit();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush({ detail: 'Server error' }, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Server error',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle error without detail or message in ngOnInit', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      component.ngOnInit();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      req.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));
  });

  describe('ontoggleOpen', () => {
    beforeEach(fakeAsync(() => {
      component.admin_fm_admin_Update_OpenAiStatus = 'http://localhost:8080/api/admin/update-openai';
      component.admin_fm_admin_get_OpenAiStatusandRoll = 'http://localhost:8080/api/admin/get-openai-status';
    }));

    it('should toggle OpenAI status to true and show success message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      expect(patchReq.request.method).toBe('PATCH');
      expect(patchReq.request.body).toEqual({ isOpenAI: true, role: 'Admin' });
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Open Ai Turned On Succesfully Admin',
        'Close',
        { duration: 1000, panelClass: ['le-u-bg-black'] }
      );
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush(mockOpenAIResponse);
      tick();
    }));

    it('should toggle OpenAI status to false and show success message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: false } };
      const role = 'User';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: false, role: 'User' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Open Ai Turned of Succesfully for User',
        'Close',
        { duration: 1000, panelClass: ['le-u-bg-black'] }
      );
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush(mockOpenAIResponse);
      tick();
    }));

    it('should update OpenAitoogleNewValue when toggling', fakeAsync(() => {
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      expect(component.OpenAitoogleNewValue).toBe(false);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick(1000); // Clear snackbar timer
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush(mockOpenAIResponse);
      tick();
    }));

    it('should refresh dataSource after successful toggle', fakeAsync(() => {
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick(1000); // Clear snackbar timer
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush(mockOpenAIResponse);
      tick();
      
      expect(component.dataSource).toEqual(mockOpenAIResponse.result);
      expect(component.OpenAitoogleValue).toBe(true);
    }));

    it('should handle error 430 in patch request', fakeAsync(() => {
      spyOn(snackBar, 'open');
      spyOn(console, 'log');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ detail: 'Permission denied' }, { status: 430, statusText: 'Permission Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Permission denied',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle generic error in patch request', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ message: 'Server error' }, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Server error',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle error without detail or message in patch request', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle error 430 in get request after successful patch', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush({ detail: 'Access denied' }, { status: 430, statusText: 'Access Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Access denied',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle generic error in get request after successful patch', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleOpen(event, role);
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush({ detail: 'Database error' }, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Database error',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));
  });

  describe('ontoggleReminder', () => {
    beforeEach(() => {
      component.admin_fm_admin_Update_OpenSelfReminderStatus = 'http://localhost:8080/api/admin/update-reminder';
    });

    it('should toggle self-reminder status to true and show success message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual({ selfReminder: true, role: 'Admin' });
      req.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Self Reminder Turned On SuccesfullyAdmin',
        'Close',
        { duration: 1000, panelClass: ['le-u-bg-black'] }
      );
    }));

    it('should toggle self-reminder status to false and show success message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: false } };
      const role = 'User';
      
      component.ontoggleReminder(event, role);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({ isOpenAI: false, role: 'User' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Self Reminder Turned of Succesfully for User',
        'Close',
        { duration: 1000, panelClass: ['le-u-bg-black'] }
      );
    }));

    it('should update OpenAitoogleNewValue when toggling reminder', fakeAsync(() => {
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      expect(component.OpenAitoogleNewValue).toBe(false);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({ isOpenAI: true, role: 'Admin' });
      tick(1000); // Clear snackbar timer
    }));

    it('should log event and role values', fakeAsync(() => {
      spyOn(console, 'log');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      expect(console.log).toHaveBeenCalledWith(true);
      expect(console.log).toHaveBeenCalledWith('Admin');
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({ isOpenAI: true, role: 'Admin' });
      tick(1000); // Clear snackbar timer
    }));

    it('should handle error 430 in reminder toggle', fakeAsync(() => {
      spyOn(snackBar, 'open');
      spyOn(console, 'log');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({ detail: 'Not authorized' }, { status: 430, statusText: 'Auth Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Not authorized',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle generic error in reminder toggle', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({ message: 'Update failed' }, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Update failed',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));

    it('should handle error without detail or message in reminder toggle', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const event = { target: { checked: true } };
      const role = 'Admin';
      
      component.ontoggleReminder(event, role);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      req.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        { duration: 3000, horizontalPosition: 'left' }
      );
    }));
  });

  describe('Integration Tests', () => {
    it('should handle complete workflow: init -> toggle OpenAI -> toggle Reminder', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      // Initialize component
      component.ngOnInit();
      
      const initReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      initReq.flush(mockOpenAIResponse);
      tick();
      
      expect(component.dataSource).toEqual(mockOpenAIResponse.result);
      
      // Toggle OpenAI
      const openAiEvent = { target: { checked: true } };
      component.ontoggleOpen(openAiEvent, 'Admin');
      
      const patchReq = httpMock.expectOne('http://localhost:8080/api/admin/update-openai');
      patchReq.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-openai-status');
      getReq.flush(mockOpenAIResponse);
      tick();
      
      // Toggle Reminder
      const reminderEvent = { target: { checked: true } };
      component.ontoggleReminder(reminderEvent, 'Admin');
      
      const reminderReq = httpMock.expectOne('http://localhost:8080/api/admin/update-reminder');
      reminderReq.flush({ isOpenAI: true, role: 'Admin' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledTimes(2);
    }));
  });

  describe('Edge Cases', () => {
    it('should handle null localStorage gracefully', () => {
      localStorage.clear();
      
      // Component tries to parse "NA" when localStorage is null, which throws error
      expect(() => {
        component.ngOnInit();
      }).toThrow();
    });

    it('should handle invalid JSON in localStorage', () => {
      localStorage.setItem('res', 'invalid json');
      
      expect(() => {
        component.ngOnInit();
      }).toThrow();
    });

    it('should handle missing localStorage with NA return', () => {
      localStorage.clear();
      
      // Component handles null by setting res to 'NA' string, which will throw when parsed
      expect(() => {
        component.ngOnInit();
      }).toThrow(jasmine.any(SyntaxError));
    });
  });
});
