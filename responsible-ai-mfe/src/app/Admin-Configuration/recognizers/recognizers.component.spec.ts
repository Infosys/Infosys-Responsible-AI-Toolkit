/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { NgxPaginationModule } from 'ngx-pagination';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

import { RecognizersComponent } from './recognizers.component';
import { RecognizersService } from './recognizers.service';
import { UserValidationService } from 'src/app/services/user-validation.service';

describe('RecognizersComponent', () => {
  let component: RecognizersComponent;
  let fixture: ComponentFixture<RecognizersComponent>;
  let httpMock: HttpTestingController;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let userValidationService: jasmine.SpyObj<UserValidationService>;

  const mockApiConfig = {
    result: {
      ip_port: 'http://test.com',
      ai_models_entity_recog_endpoint: '/api/entities',
      ai_models_recog_list_endpoint: '/api/recog-list',
      ai_models_recog_create_endpoint: '/api/recog-create',
      ai_models_recog_delete_endpoint: '/api/recog-delete',
      ai_models_recog_update_endpoint: '/api/recog-update',
      ai_models_recog_addfile_endpoint: '/api/recog-add',
      ai_models_entity_endpoint: '/api/entity',
      ai_models_entitydelete_endpoint: '/api/entity-delete'
    }
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));
    localStorage.setItem('userid', JSON.stringify('test@example.com'));

    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const userValidationSpy = jasmine.createSpyObj('UserValidationService', ['isValidEmail', 'isValidName']);
    userValidationSpy.isValidEmail.and.returnValue(true);
    userValidationSpy.isValidName.and.returnValue(true);

    await TestBed.configureTestingModule({
      declarations: [ RecognizersComponent ],
      imports: [ 
        MatSnackBarModule, 
        HttpClientTestingModule, 
        MatDialogModule, 
        NgxPaginationModule,
        ReactiveFormsModule,
        FormsModule
      ],
      providers: [
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: MatDialog, useValue: dialogSpy },
        { provide: UserValidationService, useValue: userValidationSpy },
        RecognizersService
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecognizersComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    dialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    userValidationService = TestBed.inject(UserValidationService) as jasmine.SpyObj<UserValidationService>;
    
    // Don't call detectChanges here - let each test decide when to initialize
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Component Initialization', () => {
    it('should initialize with default pagination config', () => {
      expect(component.pagingConfig).toBeDefined();
      expect(component.pagingConfig.itemsPerPage).toBe(5);
      expect(component.pagingConfig.currentPage).toBe(1);
    });

    it('should initialize with default values', () => {
      expect(component.currentPage).toBe(1);
      expect(component.itemsPerPage).toBe(5);
      expect(component.isSearchOpen).toBe(false);
      expect(component.searchQuery).toBe('');
    });

    it('should initialize recognizer type and value type options', () => {
      expect(component.recognizerTypeOptions).toEqual(['Data', 'Pattern']);
      expect(component.recognizerValueTypeOptions).toEqual(['Single Value', 'Multiple Value']);
    });

    it('should set recoGnizers to true and accountMaping to false by default', () => {
      expect(component.recoGnizers).toBe(true);
      expect(component.accountMaping).toBe(false);
    });
  });

  describe('ngOnInit', () => {
    it('should call getLogedInUser', () => {
      spyOn(userValidationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.ngOnInit();
      expect(userValidationService.getLogedInUser).toHaveBeenCalled();
    });

    it('should call getLocalStoreApi', () => {
      spyOn(userValidationService, 'getLocalStoreApi').and.returnValue(mockApiConfig);
      spyOn(component, 'getRecognizerList');
      component.ngOnInit();
      expect(userValidationService.getLocalStoreApi).toHaveBeenCalled();
    });

    it('should call setApilist with ip_port', () => {
      spyOn(component, 'setApilist');
      spyOn(component, 'getRecognizerList');
      component.ngOnInit();
      expect(component.setApilist).toHaveBeenCalled();
    });

    it('should call getRecognizerList', () => {
      spyOn(component, 'getRecognizerList');
      component.ngOnInit();
      expect(component.getRecognizerList).toHaveBeenCalled();
    });

    it('should call fromCreation', () => {
      spyOn(component, 'fromCreation');
      spyOn(component, 'getRecognizerList');
      component.ngOnInit();
      expect(component.fromCreation).toHaveBeenCalled();
    });
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

    it('should return undefined when localStorage is empty', () => {
      localStorage.removeItem('userid');
      const result = userValidationService.getLogedInUser();
      expect(result).toBeUndefined();
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
      expect(result.result.Admin).toBe('http://test.com/api/');
    });

    it('should return undefined when localStorage is empty', () => {
      localStorage.removeItem('res');
      const result = userValidationService.getLocalStoreApi();
      expect(result).toBeUndefined();
    });
  });

  describe('setApilist', () => {
    it('should set all API URLs correctly', () => {
      component.setApilist(mockApiConfig);
      
      expect(component.admin_list_rec).toBe('http://test.com/api/recog-group');
      expect(component.admin_list_rec_get_list).toBe('http://test.com/api/recog-list');
      expect(component.admin_list_rec_get_list_DataRecogGrpEntites).toBe('http://test.com/api/recog-entities');
      expect(component.admin_list_rec_get_list_Delete_DataRecogGrp).toBe('http://test.com/api/recog-delete');
      expect(component.admin_list_rec_get_list_Update_DataRecogGrpEntity).toBe('http://test.com/api/entity-update');
      expect(component.admin_list_rec_get_list_Update_DataRecogGrp).toBe('http://test.com/api/group-update');
      expect(component.admin_list_rec_get_list_Update_AddnewlistItem).toBe('http://test.com/api/entity-add');
      expect(component.admin_list_rec_get_list_Delete_DataRecogGrpEntites).toBe('http://test.com/api/entity-delete');
    });
  });

  describe('getRecognizerList', () => {
    it('should fetch recognizers and filter by isPreDefined = No', fakeAsync(() => {
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'Custom1', isPreDefined: 'No' },
          { id: 2, name: 'Predefined1', isPreDefined: 'Yes' },
          { id: 3, name: 'Custom2', isPreDefined: 'No' }
        ]
      };

      component.admin_list_rec_get_list = 'http://test.com/api/recog-list';
      component.getRecognizerList();

      const req = httpMock.expectOne('http://test.com/api/recog-list');
      req.flush(mockResponse);
      tick();

      expect(component.dataSource.length).toBe(2);
      expect(component.dataSource[0].name).toBe('Custom1');
      expect(component.dataSource[1].name).toBe('Custom2');
    }));

    it('should handle error response', fakeAsync(() => {
      component.admin_list_rec_get_list = 'http://test.com/api/recog-list';
      component.getRecognizerList();

      const req = httpMock.expectOne('http://test.com/api/recog-list');
      req.flush({ detail: 'Error occurred' }, { status: 500, statusText: 'Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should set filteredDataSource equal to dataSource', fakeAsync(() => {
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'Test', isPreDefined: 'No' }
        ]
      };

      component.admin_list_rec_get_list = 'http://test.com/api/recog-list';
      component.getRecognizerList();

      const req = httpMock.expectOne('http://test.com/api/recog-list');
      req.flush(mockResponse);
      tick();

      expect(component.filteredDataSource).toEqual(component.dataSource);
    }));
  });

  describe('toggleTab', () => {
    it('should toggle recoGnizers and accountMaping', () => {
      const initialRecognizers = component.recoGnizers;
      const initialAccountMaping = component.accountMaping;

      component.toggleTab();

      expect(component.recoGnizers).toBe(!initialRecognizers);
      expect(component.accountMaping).toBe(!initialAccountMaping);
    });
  });

  describe('selectRecognizerType', () => {
    it('should set recognizer_type', () => {
      const event = { value: 'Pattern' };
      component.selectRecognizerType(event);
      expect(component.recognizer_type).toBe('Pattern');
    });
  });

  describe('selectRecognizerValueType', () => {
    it('should set recognizerValue_type', () => {
      const event = { value: 'Multiple Value' };
      component.selectRecognizerValueType(event);
      expect(component.recognizerValue_type).toBe('Multiple Value');
    });
  });

  describe('onTableDataChange', () => {
    it('should update currentPage and pagingConfig', () => {
      component.filteredDataSource = [1, 2, 3, 4, 5];
      component.onTableDataChange(2);

      expect(component.currentPage).toBe(2);
      expect(component.pagingConfig.currentPage).toBe(2);
      expect(component.pagingConfig.totalItems).toBe(5);
    });
  });

  describe('onTableSizeChange', () => {
    it('should update itemsPerPage and reset currentPage', () => {
      component.filteredDataSource = [1, 2, 3];
      const event = { result: { value: 10 } };
      
      component.onTableSizeChange(event);

      expect(component.pagingConfig.itemsPerPage).toBe(10);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(3);
    });
  });

  describe('openRightSideModal', () => {
    it('should open dialog with correct configuration', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialog.open.and.returnValue(dialogRefSpy);

      component.admin_list_rec_get_list_DataRecogGrpEntites = 'http://test.com/entities';
      component.openRightSideModal('test-id');

      expect(dialog.open).toHaveBeenCalled();
    });

    it('should call getRecognizerList after dialog closes', fakeAsync(() => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialog.open.and.returnValue(dialogRefSpy);
      spyOn(component, 'getRecognizerList');

      component.openRightSideModal('test-id');
      tick();

      expect(component.getRecognizerList).toHaveBeenCalled();
    }));
  });

  describe('fileBrowseHandler', () => {
    it('should show error for invalid file type', () => {
      const mockEvent = {
        target: {
          files: [{
            type: 'application/pdf',
            name: 'test.pdf'
          }]
        }
      };

      component.fileBrowseHandler(mockEvent);

      expect(snackBar.open).toHaveBeenCalledWith(
        'Please select a valid file type',
        '✖',
        jasmine.objectContaining({ duration: 3000 })
      );
    });

    it('should process valid text file', () => {
      const mockEvent = {
        target: {
          files: [{
            type: 'text/plain',
            name: 'test.txt'
          }]
        }
      };

      spyOn(component, 'prepareFilesList');
      component.fileBrowseHandler(mockEvent);

      expect(component.prepareFilesList).toHaveBeenCalled();
      expect(component.fileName).toBe('test.txt');
    });
  });

  describe('prepareFilesList', () => {
    it('should add files to the files array', () => {
      const mockFiles = [{ name: 'file1.txt' }, { name: 'file2.txt' }];
      component.prepareFilesList(mockFiles);

      expect(component.files.length).toBe(2);
    });
  });

  describe('fromCreation', () => {
    it('should create form with required fields', () => {
      component.fromCreation();

      expect(component.listForm).toBeDefined();
      expect(component.listForm.get('recognizer_type')).toBeDefined();
      expect(component.listForm.get('recognizer_Name')).toBeDefined();
      expect(component.listForm.get('recognizer_Value')).toBeDefined();
      expect(component.listForm.get('supported_Entity')).toBeDefined();
      expect(component.listForm.get('tempValue')).toBeDefined();
    });

    it('should set default value for recognizer_type', () => {
      component.fromCreation();
      expect(component.listForm.get('recognizer_type')?.value).toBe('DATA');
    });

    it('should add validators to recognizer_Name', () => {
      component.fromCreation();
      const control = component.listForm.get('recognizer_Name');
      
      control?.setValue('');
      expect(control?.hasError('required')).toBe(true);
    });
  });

  describe('onClickApply', () => {
    it('should call payloadonSubmit when form is valid', () => {
      component.fromCreation();
      spyOn(component, 'payloadonSubmit');
      
      component.listForm.patchValue({
        recognizer_type: 'DATA',
        recognizer_Name: 'TestRecognizer',
        recognizer_Value: 'TestValue',
        supported_Entity: 'TestEntity',
        tempValue: 5
      });

      component.onClickApply();

      expect(component.payloadonSubmit).toHaveBeenCalled();
    });

    it('should not call payloadonSubmit when form is invalid', () => {
      component.fromCreation();
      spyOn(component, 'payloadonSubmit');
      
      component.listForm.patchValue({
        recognizer_type: '',
        recognizer_Name: '',
        recognizer_Value: '',
        supported_Entity: '',
        tempValue: 0
      });

      component.onClickApply();

      expect(component.payloadonSubmit).not.toHaveBeenCalled();
    });
  });

  describe('payloadonSubmit', () => {
    it('should create FormData with correct values', () => {
      component.fromCreation();
      component.listForm.patchValue({
        recognizer_type: 'DATA',
        recognizer_Name: 'TestName',
        recognizer_Value: 'TestValue',
        supported_Entity: 'TestEntity',
        tempValue: 10
      });

      spyOn(component, 'postDataRecogGroupApi');
      component.payloadonSubmit();

      expect(component.postDataRecogGroupApi).toHaveBeenCalled();
    });

    it('should divide tempValue by 10 for score', () => {
      component.fromCreation();
      component.listForm.patchValue({
        recognizer_type: 'DATA',
        recognizer_Name: 'Test',
        recognizer_Value: 'Value',
        supported_Entity: 'Entity',
        tempValue: 8
      });

      spyOn(component, 'postDataRecogGroupApi');
      component.payloadonSubmit();

      const call = (component.postDataRecogGroupApi as jasmine.Spy).calls.mostRecent();
      const formData = call.args[0] as FormData;
      expect(formData.get('score')).toBe('0.8');
    });
  });

  describe('postDataRecogGroupApi', () => {
    it('should make POST request with FormData', fakeAsync(() => {
      const mockFormData = new FormData();
      mockFormData.append('name', 'Test');
      
      component.admin_list_rec = 'http://test.com/api/recog-group';
      spyOn(component, 'getRecognizerList');
      
      component.postDataRecogGroupApi(mockFormData);

      const req = httpMock.expectOne('http://test.com/api/recog-group');
      expect(req.request.method).toBe('POST');
      req.flush({ success: true });
      tick();

      expect(component.getRecognizerList).toHaveBeenCalled();
      expect(snackBar.open).toHaveBeenCalled();
    }));
  });

  describe('clickDeleteRecognizer', () => {
    it('should show error for predefined recognizers', () => {
      component.clickDeleteRecognizer('123', 'Yes');

      expect(snackBar.open).toHaveBeenCalledWith(
        "You Can't delete a Pre-Defined List",
        'Close',
        jasmine.objectContaining({ duration: 1000 })
      );
    });

    it('should delete recognizer when isPreDefined is No', fakeAsync(() => {
      component.admin_list_rec_get_list_Delete_DataRecogGrp = 'http://test.com/delete';
      spyOn(component, 'getRecognizerList');

      component.clickDeleteRecognizer('123', 'No');

      const req = httpMock.expectOne('http://test.com/delete');
      expect(req.request.method).toBe('DELETE');
      req.flush({ status: 'True' });
      tick();

      expect(component.getRecognizerList).toHaveBeenCalled();
      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle delete error response', fakeAsync(() => {
      component.admin_list_rec_get_list_Delete_DataRecogGrp = 'http://test.com/delete';

      component.clickDeleteRecognizer('123', 'No');

      const req = httpMock.expectOne('http://test.com/delete');
      req.flush({ detail: 'Delete failed' }, { status: 430, statusText: 'Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));
  });

  describe('edit and update', () => {
    it('should add index to editIndex array', () => {
      component.edit(1);
      expect(component.editIndex).toContain(1);
    });

    it('should remove index from editIndex and call updateRecognizer', () => {
      component.editIndex = [1, 2];
      spyOn(component, 'updateRecognizer');

      component.update(1, '123', 'TestName', 'TestEntity', 'DATA');

      expect(component.editIndex).not.toContain(1);
      expect(component.updateRecognizer).toHaveBeenCalled();
    });
  });

  describe('updateRecognizer', () => {
    it('should make PATCH request with payload', fakeAsync(() => {
      const mockPayload = {
        RecogId: '123',
        RecogName: 'UpdatedName',
        supported_entity: 'UpdatedEntity',
        RecogType: 'DATA'
      };

      component.admin_list_rec_get_list_Update_DataRecogGrp = 'http://test.com/update';
      spyOn(component, 'getRecognizerList');

      component.updateRecognizer(mockPayload);

      const req = httpMock.expectOne('http://test.com/update');
      expect(req.request.method).toBe('PATCH');
      req.flush({ success: true });
      tick();

      expect(component.getRecognizerList).toHaveBeenCalled();
      expect(snackBar.open).toHaveBeenCalled();
    }));
  });

  describe('search', () => {
    beforeEach(() => {
      component.dataSource = [
        { RecogName: 'Person' },
        { RecogName: 'Email' },
        { RecogName: 'Phone' }
      ];
    });

    it('should filter dataSource based on searchQuery', () => {
      component.searchQuery = 'person';
      component.search();

      expect(component.filteredDataSource.length).toBe(1);
      expect(component.filteredDataSource[0].RecogName).toBe('Person');
    });

    it('should reset to full dataSource when searchQuery is empty', () => {
      component.searchQuery = '';
      component.search();

      expect(component.filteredDataSource).toEqual(component.dataSource);
    });

    it('should reset pagination to page 1', () => {
      component.currentPage = 3;
      component.searchQuery = 'email';
      component.search();

      expect(component.currentPage).toBe(1);
      expect(component.pagingConfig.currentPage).toBe(1);
    });
  });

  describe('toggleSearch', () => {
    it('should toggle isSearchOpen', () => {
      component.isSearchOpen = false;
      component.toggleSearch();
      expect(component.isSearchOpen).toBe(true);

      component.toggleSearch();
      expect(component.isSearchOpen).toBe(false);
    });

    it('should reset searchQuery and filteredItems', () => {
      component.searchQuery = 'test';
      component.filteredItems = ['item1'];

      component.toggleSearch();

      expect(component.searchQuery).toBe('');
      expect(component.filteredItems).toEqual([]);
    });
  });

  describe('closeSearch', () => {
    it('should reset search state and dataSource', () => {
      component.dataSource = [{ RecogName: 'Test' }];
      component.isSearchOpen = true;
      component.searchQuery = 'test';

      component.closeSearch();

      expect(component.isSearchOpen).toBe(false);
      expect(component.searchQuery).toBe('');
      expect(component.filteredDataSource).toEqual(component.dataSource);
      expect(component.currentPage).toBe(1);
    });
  });

  describe('Form Getters', () => {
    it('should return recognizer_Name control', () => {
      component.fromCreation();
      const control = component.recognizerName;
      expect(control).toBe(component.listForm.get('recognizer_Name'));
    });

    it('should return supported_Entity control', () => {
      component.fromCreation();
      const control = component.supportedEntity;
      expect(control).toBe(component.listForm.get('supported_Entity'));
    });
  });
});
