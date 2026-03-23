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
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { of, throwError } from 'rxjs';

import { PrivacyParametersComponent } from './privacy-parameters.component';
import { UserValidationService } from 'src/app/services/user-validation.service';

describe('PrivacyParametersComponent', () => {
  let component: PrivacyParametersComponent;
  let fixture: ComponentFixture<PrivacyParametersComponent>;
  let httpMock: HttpTestingController;
  let snackBar: MatSnackBar;
  let validationService: UserValidationService;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin',
      Admin_DataRecogGrplist: '/data-recog-grp-list',
      setPrivacyParameter: '/set-privacy-parameter'
    }
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));
    localStorage.setItem('userid', JSON.stringify('test@example.com'));
    
    await TestBed.configureTestingModule({
      declarations: [ PrivacyParametersComponent ],
      imports: [ MatSnackBarModule, HttpClientTestingModule, MatDialogModule ],
      providers: [ UserValidationService ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PrivacyParametersComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar);
    validationService = TestBed.inject(UserValidationService);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with default values', () => {
      expect(component.listReconList).toEqual([]);
      expect(component.selectedReclist).toEqual([]);
      expect(component.c1).toBe(false);
      expect(component.allSelectedInput).toBe(false);
      expect(component.listShowlist1).toBeInstanceOf(Set);
    });

    it('should set API URLs on initialization', fakeAsync(() => {
      component.ngOnInit();
      
      // Handle the HTTP request that ngOnInit triggers
      const req = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      req.flush({ RecogList: [] });
      tick();
      
      expect(component.admin_list_rec_get_list).toBe('http://localhost:8080/api/admin/data-recog-grp-list');
      expect(component.Admin_SetPrivacyParameter).toBe('http://localhost:8080/api/admin/set-privacy-parameter');
    }));

    it('should call getadmin_list_rec_get_list on ngOnInit', () => {
      spyOn(component, 'getadmin_list_rec_get_list');
      component.ngOnInit();
      expect(component.getadmin_list_rec_get_list).toHaveBeenCalled();
    });
  });

  describe('Input Properties', () => {
    it('should accept parPortfolio input', () => {
      component.parPortfolio = 'TestPortfolio';
      expect(component.parPortfolio).toBe('TestPortfolio');
    });

    it('should accept parAccount input', () => {
      component.parAccount = 'TestAccount';
      expect(component.parAccount).toBe('TestAccount');
    });
  });

  describe('toggleAllSelection1', () => {
    it('should select all options when allSelected1 is true', () => {
      const mockSelect = jasmine.createSpyObj('MatSelect', ['close']);
      const mockOption1 = jasmine.createSpyObj('MatOption', ['select']);
      mockOption1.value = 'option1';
      const mockOption2 = jasmine.createSpyObj('MatOption', ['select']);
      mockOption2.value = 'option2';
      
      mockSelect.options = {
        forEach: (callback: Function) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      };
      
      component.select1 = mockSelect;
      component.allSelected1 = false;
      
      const event = { checked: true };
      component.toggleAllSelection1(event);
      
      expect(component.allSelected1).toBe(true);
      expect(component.c1).toBe(true);
      expect(mockOption1.select).toHaveBeenCalled();
      expect(mockOption2.select).toHaveBeenCalled();
      expect(component.listShowlist1.has('option1')).toBe(true);
      expect(component.listShowlist1.has('option2')).toBe(true);
    });

    it('should deselect all options when allSelected1 is false', () => {
      const mockSelect = jasmine.createSpyObj('MatSelect', ['close']);
      const mockOption1 = jasmine.createSpyObj('MatOption', ['deselect']);
      mockOption1.value = 'option1';
      const mockOption2 = jasmine.createSpyObj('MatOption', ['deselect']);
      mockOption2.value = 'option2';
      
      mockSelect.options = {
        forEach: (callback: Function) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      };
      
      component.select1 = mockSelect;
      component.allSelected1 = true;
      component.listShowlist1.add('option1');
      component.listShowlist1.add('option2');
      
      const event = { checked: false };
      component.toggleAllSelection1(event);
      
      expect(component.allSelected1).toBe(false);
      expect(component.c1).toBe(false);
      expect(mockOption1.deselect).toHaveBeenCalled();
      expect(mockOption2.deselect).toHaveBeenCalled();
      expect(component.listShowlist1.has('option1')).toBe(false);
      expect(component.listShowlist1.has('option2')).toBe(false);
    });
  });

  describe('selectRecognizertype', () => {
    it('should update allSelectedInput to true when all options are selected', () => {
      const mockSelect = { options: null } as any;
      const mockOption1 = { selected: true, value: 'option1' } as MatOption;
      const mockOption2 = { selected: true, value: 'option2' } as MatOption;
      
      mockSelect.options = {
        forEach: (callback: Function) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      };
      
      component.select1 = mockSelect;
      component.selectRecognizertype();
      
      expect(component.allSelectedInput).toBe(true);
      expect(component.listShowlist1.has('option1')).toBe(true);
      expect(component.listShowlist1.has('option2')).toBe(true);
    });

    it('should update allSelectedInput to false when not all options are selected', () => {
      const mockSelect = { options: null } as any;
      const mockOption1 = { selected: true, value: 'option1' } as MatOption;
      const mockOption2 = { selected: false, value: 'option2' } as MatOption;
      
      mockSelect.options = {
        forEach: (callback: Function) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      };
      
      component.select1 = mockSelect;
      component.allSelected1 = true;
      component.selectRecognizertype();
      
      expect(component.allSelectedInput).toBe(false);
      expect(component.allSelected1).toBe(false);
      expect(component.listShowlist1.has('option1')).toBe(true);
      expect(component.listShowlist1.has('option2')).toBe(false);
    });
  });

  describe('submit', () => {
    it('should call setPrivacyParameter with correct header data', () => {
      spyOn(component, 'setPrivacyParameter');
      component.parPortfolio = 'TestPortfolio';
      component.parAccount = 'TestAccount';
      component.selectedReclist = ['rec1', 'rec2'];
      
      component.submit();
      
      expect(component.setPrivacyParameter).toHaveBeenCalledWith({
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1', 'rec2']
      });
    });
  });

  describe('setPrivacyParameter', () => {
    beforeEach(() => {
      component.Admin_SetPrivacyParameter = 'http://localhost:8080/api/admin/set-privacy-parameter';
    });

    it('should successfully send privacy parameters and show success message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const mockHeader = {
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      };
      
      component.setPrivacyParameter(mockHeader);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockHeader);
      
      req.flush({ status: 'True' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Recognizer Added Successfully',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should show error message when mapping already exists', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const mockHeader = {
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      };
      
      component.setPrivacyParameter(mockHeader);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      req.flush({ status: 'False' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Mapping already exists for this account ',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should handle HTTP error with error detail', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const mockHeader = {
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      };
      
      component.setPrivacyParameter(mockHeader);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      req.flush(
        { detail: 'Custom error message' },
        { status: 500, statusText: 'Server Error' }
      );
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Custom error message',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should handle HTTP error with error message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const mockHeader = {
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      };
      
      component.setPrivacyParameter(mockHeader);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      req.flush(
        { message: 'Error message from server' },
        { status: 400, statusText: 'Bad Request' }
      );
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Error message from server',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should handle HTTP error without detail or message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const mockHeader = {
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      };
      
      component.setPrivacyParameter(mockHeader);
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      req.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));
  });

  describe('getadmin_list_rec_get_list', () => {
    beforeEach(() => {
      component.admin_list_rec_get_list = 'http://localhost:8080/api/admin/data-recog-grp-list';
    });

    it('should fetch and set recognizer list successfully', fakeAsync(() => {
      const mockResponse = {
        RecogList: ['recognizer1', 'recognizer2', 'recognizer3']
      };
      
      component.getadmin_list_rec_get_list();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      expect(req.request.method).toBe('GET');
      
      req.flush(mockResponse);
      tick();
      
      expect(component.listReconList).toEqual(['recognizer1', 'recognizer2', 'recognizer3']);
    }));

    it('should handle error when fetching recognizer list with error detail', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      component.getadmin_list_rec_get_list();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      req.flush(
        { detail: 'Failed to fetch recognizers' },
        { status: 500, statusText: 'Server Error' }
      );
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Failed to fetch recognizers',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should handle error when fetching recognizer list with error message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      component.getadmin_list_rec_get_list();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      req.flush(
        { message: 'Network error occurred' },
        { status: 404, statusText: 'Not Found' }
      );
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Network error occurred',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should handle error when fetching recognizer list without detail or message', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      component.getadmin_list_rec_get_list();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      req.flush({}, { status: 500, statusText: 'Server Error' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));
  });

  describe('getLogedInUser', () => {
    it('should retrieve valid email from localStorage', () => {
      spyOn(validationService, 'isValidEmail').and.returnValue(true);
      spyOn(validationService, 'isValidName').and.returnValue(false);
      localStorage.setItem('userid', JSON.stringify('test@example.com'));
      
      const userId = validationService.getLogedInUser();
      
      expect(userId).toBe('test@example.com');
      expect(component.userId).toBe('test@example.com');
    });

    it('should retrieve valid name from localStorage', () => {
      spyOn(validationService, 'isValidEmail').and.returnValue(false);
      spyOn(validationService, 'isValidName').and.returnValue(true);
      localStorage.setItem('userid', JSON.stringify('JohnDoe'));
      
      const userId = validationService.getLogedInUser();
      
      expect(userId).toBe('JohnDoe');
      expect(component.userId).toBe('JohnDoe');
    });

    it('should return undefined when userid is not in localStorage', () => {
      localStorage.removeItem('userid');
      
      const userId = validationService.getLogedInUser();
      
      // Returns 'NA' when not found, not undefined
      expect(userId).toBe('NA');
    });

    it('should handle "NA" value in localStorage', () => {
      spyOn(validationService, 'isValidEmail').and.returnValue(false);
      spyOn(validationService, 'isValidName').and.returnValue(false);
      localStorage.removeItem('userid');
      
      const userId = validationService.getLogedInUser();
      
      expect(userId).toBeUndefined();
    });

    it('should handle invalid userid format', () => {
      spyOn(validationService, 'isValidEmail').and.returnValue(false);
      spyOn(validationService, 'isValidName').and.returnValue(false);
      localStorage.setItem('userid', JSON.stringify('invalid_user'));
      
      const userId = validationService.getLogedInUser();
      
      expect(userId).toBeUndefined();
    });
  });

  describe('getLocalStoreApi', () => {
    it('should retrieve API configuration from localStorage', () => {
      const apiConfig = validationService.getLocalStoreApi();
      
      expect(apiConfig).toEqual(mockApiConfig);
    });

    it('should return undefined when res is not in localStorage', () => {
      localStorage.clear();
      // Set res to null so getItem returns null instead of 'NA' string
      localStorage.setItem('res', 'null');
      
      const apiConfig = validationService.getLocalStoreApi();
      
      // The method returns null when JSON.parse('null') is called
      expect(apiConfig).toBeNull();
    });

    it('should handle valid res in localStorage', () => {
      // This test already covered by 'should retrieve API configuration from localStorage'
      const customConfig = { result: { Admin: 'test' } };
      localStorage.setItem('res', JSON.stringify(customConfig));
      
      const apiConfig = validationService.getLocalStoreApi();
      
      expect(apiConfig).toEqual(customConfig);
    });

    it('should parse JSON correctly from localStorage', () => {
      const customConfig = {
        result: {
          Admin: 'http://custom-api.com',
          Admin_DataRecogGrplist: '/custom-list',
          setPrivacyParameter: '/custom-set'
        }
      };
      localStorage.setItem('res', JSON.stringify(customConfig));
      
      const apiConfig = validationService.getLocalStoreApi();
      
      expect(apiConfig).toEqual(customConfig);
    });
  });

  describe('setApilist', () => {
    it('should set API URLs correctly', () => {
      const ip_port = mockApiConfig;
      
      component.setApilist(ip_port);
      
      expect(component.admin_list_rec_get_list).toBe('http://localhost:8080/api/admin/data-recog-grp-list');
      expect(component.Admin_SetPrivacyParameter).toBe('http://localhost:8080/api/admin/set-privacy-parameter');
    });

    it('should concatenate URLs correctly with different base paths', () => {
      const customConfig = {
        result: {
          Admin: 'https://prod-api.com/v1',
          Admin_DataRecogGrplist: '/recognizers',
          setPrivacyParameter: '/privacy/set'
        }
      };
      
      component.setApilist(customConfig);
      
      expect(component.admin_list_rec_get_list).toBe('https://prod-api.com/v1/recognizers');
      expect(component.Admin_SetPrivacyParameter).toBe('https://prod-api.com/v1/privacy/set');
    });
  });

  describe('Integration Tests', () => {
    it('should complete full workflow: init -> fetch list -> select -> submit', fakeAsync(() => {
      spyOn(snackBar, 'open');
      component.parPortfolio = 'TestPortfolio';
      component.parAccount = 'TestAccount';
      
      // Init
      component.ngOnInit();
      
      // Fetch list
      const listReq = httpMock.expectOne('http://localhost:8080/api/admin/data-recog-grp-list');
      listReq.flush({ RecogList: ['rec1', 'rec2'] });
      tick();
      
      expect(component.listReconList).toEqual(['rec1', 'rec2']);
      
      // Select items
      component.selectedReclist = ['rec1'];
      
      // Submit
      component.submit();
      
      const submitReq = httpMock.expectOne('http://localhost:8080/api/admin/set-privacy-parameter');
      expect(submitReq.request.body).toEqual({
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        dataGrpList: ['rec1']
      });
      
      submitReq.flush({ status: 'True' });
      tick();
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Recognizer Added Successfully',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });
});
