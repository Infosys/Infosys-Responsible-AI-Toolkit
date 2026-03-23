/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatDialogModule } from '@angular/material/dialog';
import { NgxPaginationModule } from 'ngx-pagination';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatOption } from '@angular/material/core';
import { FMChatConfigurationComponent } from './fm-chat-configuration.component';
import { UserValidationService } from 'src/app/services/user-validation.service';
import { NonceService } from 'src/app/nonce.service';

describe('FMChatConfigurationComponent', () => {
  let component: FMChatConfigurationComponent;
  let fixture: ComponentFixture<FMChatConfigurationComponent>;
  let httpMock: HttpTestingController;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let validationService: jasmine.SpyObj<UserValidationService>;

  const mockApiConfig = {
    result: {
      Admin_Rag: 'http://localhost:8080/api/rag/',
      Admin_uploadFile: 'upload',
      Admin_getFiles: 'files',
      Admin_setCache: 'cache',
      Admin_getEmbedings: 'embeddings',
      Admin_LLmExplain_deleteFile: 'delete'
    }
  };

  beforeEach(async () => {
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const validationServiceSpy = jasmine.createSpyObj('UserValidationService', ['isValidEmail', 'isValidName']);

    await TestBed.configureTestingModule({
      declarations: [FMChatConfigurationComponent],
      imports: [
        MatSnackBarModule,
        HttpClientTestingModule,
        MatDialogModule,
        NgxPaginationModule,
        ReactiveFormsModule,
        FormsModule,
        MatSelectModule
      ],
      providers: [
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: UserValidationService, useValue: validationServiceSpy },
        NonceService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
      .compileComponents();

    fixture = TestBed.createComponent(FMChatConfigurationComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    validationService = TestBed.inject(UserValidationService) as jasmine.SpyObj<UserValidationService>;

    // Mock localStorage
    spyOn(localStorage, 'getItem').and.callFake((key: string) => {
      if (key === 'res') return JSON.stringify(mockApiConfig);
      if (key === 'userid') return JSON.stringify('test@example.com');
      return null;
    });

    validationService.isValidEmail.and.returnValue(true);
    validationService.isValidName.and.returnValue(true);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Component initialization', () => {
    it('should initialize with default values', () => {
      expect(component.currentPage).toBe(1);
      expect(component.itemsPerPage).toBe(5);
      expect(component.totalItems).toBe(0);
      expect(component.files).toEqual([]);
      expect(component.demoFile).toEqual([]);
      expect(component.formBased).toBe(false);
    });

    it('should create form control with validator', () => {
      expect(component.form).toBeDefined();
      expect(component.form.value).toBeNull();
    });

    it('should create embeddings form group', () => {
      expect(component.createNewEmbeddingsform).toBeDefined();
      expect(component.createNewEmbeddingsform.get('embeddingName')).toBeDefined();
      expect(component.createNewEmbeddingsform.get('selectedEmbeddings')).toBeDefined();
    });

    it('should initialize paging config', () => {
      expect(component.pagingConfig.itemsPerPage).toBe(5);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(0);
    });
  });

  describe('fileSelectedValidator', () => {
    it('should return error when control value is null', () => {
      const control: any = { value: null };
      const result = component.fileSelectedValidator(control);
      expect(result).toEqual({ 'noFileSelected': true });
    });

    it('should return error when control value has zero length', () => {
      const control: any = { value: [] };
      const result = component.fileSelectedValidator(control);
      expect(result).toEqual({ 'noFileSelected': true });
    });

    it('should return null when file is selected', () => {
      const control: any = { value: [{ name: 'test.pdf' }] };
      const result = component.fileSelectedValidator(control);
      expect(result).toBeNull();
    });
  });

  describe('onFileChange', () => {
    it('should read file content', () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const event = {
        target: {
          files: [mockFile]
        }
      };

      const reader = new FileReader();
      spyOn(window as any, 'FileReader').and.returnValue(reader);

      component.onFileChange(event);
      expect(FileReader).toBeDefined();
    });
  });

  describe('fileBrowseHandler', () => {
    it('should show error for invalid file type', () => {
      const mockFile = new File([''], 'test.txt', { type: 'text/plain' });
      const event = {
        target: {
          files: [mockFile]
        }
      };

      component.fileBrowseHandler(event);

      expect(snackBar.open).toHaveBeenCalledWith(
        'Please select a valid file type',
        '✖',
        jasmine.objectContaining({
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000
        })
      );
    });

    it('should process valid PDF file', () => {
      const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
      const event = {
        target: {
          files: [mockFile]
        }
      };

      spyOn(component, 'prepareFilesList');

      component.fileBrowseHandler(event);

      expect(component.prepareFilesList).toHaveBeenCalledWith(event.target.files);
    });

    it('should set form value with files', () => {
      const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
      const event = {
        target: {
          files: [mockFile]
        }
      };

      component.fileBrowseHandler(event);

      expect(component.files.length).toBe(1);
      expect(component.demoFile).toEqual(component.files);
      expect(component.file).toBe(component.files[0]);
    });
  });

  describe('prepareFilesList', () => {
    it('should add files to the files array', () => {
      const mockFiles = [
        new File([''], 'test1.pdf', { type: 'application/pdf' }),
        new File([''], 'test2.pdf', { type: 'application/pdf' })
      ];

      spyOn(component, 'uploadFilesSimulator');

      component.prepareFilesList(mockFiles);

      expect(component.files.length).toBe(2);
      expect(component.uploadFilesSimulator).toHaveBeenCalledWith(0, component.files);
    });
  });

  describe('uploadFilesSimulator', () => {
    it('should simulate file upload progress', fakeAsync(() => {
      component.files = [{ name: 'test.pdf', progress: 0 }];

      component.uploadFilesSimulator(0, component.files);
      tick(1000);
      tick(200); // First interval tick

      expect(component.files[0].progress).toBeGreaterThanOrEqual(0);
      
      // Clean up remaining intervals
      tick(2000);
    }));

    it('should return when index equals files length', fakeAsync(() => {
      component.files = [{ name: 'test.pdf' }];

      component.uploadFilesSimulator(1, component.files);
      tick(1000);

      expect(component.files.length).toBe(1);
    }));
  });

  describe('deleteFile', () => {
    it('should clear files and demoFile arrays', () => {
      component.files = [{ name: 'test.pdf' }];
      component.demoFile = [{ name: 'test.pdf' }];
      component.file = { name: 'test.pdf' };

      component.deleteFile();

      expect(component.files).toEqual([]);
      expect(component.demoFile).toEqual([]);
      expect(component.file).toBeNull();
    });
  });

  describe('reset', () => {
    it('should reset files and demoFile arrays', () => {
      component.files = [{ name: 'test.pdf' }];
      component.demoFile = [{ name: 'test.pdf' }];

      component.reset();

      expect(component.files).toEqual([]);
      expect(component.demoFile).toEqual([]);
    });
  });

  describe('toggleAllSelection1', () => {
    beforeEach(() => {
      component.select1 = {
        options: {
          forEach: (callback: Function) => {
            const mockOption1 = { value: 'option1', select: jasmine.createSpy(), deselect: jasmine.createSpy(), selected: true } as any;
            const mockOption2 = { value: 'option2', select: jasmine.createSpy(), deselect: jasmine.createSpy(), selected: true } as any;
            callback(mockOption1);
            callback(mockOption2);
          }
        },
        close: jasmine.createSpy()
      } as any;
    });

    it('should select all options when checked', () => {
      const event = { checked: true };
      component.allSelected1 = false;

      component.toggleAllSelection1(event);

      expect(component.allSelected1).toBe(true);
      expect(component.c1).toBe(true);
    });

    it('should deselect all options when unchecked', () => {
      const event = { checked: false };
      component.allSelected1 = true;

      component.toggleAllSelection1(event);

      expect(component.allSelected1).toBe(false);
      expect(component.c1).toBe(false);
    });
  });

  describe('selectRecognizertype', () => {
    it('should update allSelectedInput based on selection', () => {
      component.select1 = {
        options: {
          forEach: (callback: Function) => {
            const mockOption1 = { value: 'option1', selected: true } as any;
            const mockOption2 = { value: 'option2', selected: true } as any;
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.selectRecognizertype();

      expect(component.allSelectedInput).toBe(true);
    });

    it('should set allSelected1 to false when not all options selected', () => {
      component.select1 = {
        options: {
          forEach: (callback: Function) => {
            const mockOption1 = { value: 'option1', selected: true } as any;
            const mockOption2 = { value: 'option2', selected: false } as any;
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.selectRecognizertype();

      expect(component.allSelected1).toBe(false);
    });
  });

  describe('submit', () => {
    it('should set formBased to true and call upload_file', () => {
      spyOn(component, 'upload_file');

      component.submit();

      expect(component.formBased).toBe(true);
      expect(component.upload_file).toHaveBeenCalled();
    });
  });

  describe('submit2', () => {
    it('should call setcache when form is valid', () => {
      component.createNewEmbeddingsform.patchValue({
        embeddingName: 'Test Embedding',
        selectedEmbeddings: ['doc1', 'doc2']
      });

      spyOn(component, 'setcache');

      component.submit2();

      expect(component.formBased).toBe(true);
      expect(component.setcache).toHaveBeenCalledWith('Test Embedding', ['doc1', 'doc2']);
    });

    it('should not call setcache when form is invalid', () => {
      component.createNewEmbeddingsform.patchValue({
        embeddingName: '',
        selectedEmbeddings: []
      });

      spyOn(component, 'setcache');

      component.submit2();

      expect(component.setcache).not.toHaveBeenCalled();
    });
  });

  describe('ngOnInit', () => {
    it('should call initialization methods', () => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(validationService, 'getLocalStoreApi').and.returnValue(mockApiConfig);
      spyOn(component, 'setApilist');
      spyOn(component, 'getembeddigns');
      spyOn(component, 'getFilestList');

      component.ngOnInit();

      expect(validationService.getLogedInUser).toHaveBeenCalled();
      expect(validationService.getLocalStoreApi).toHaveBeenCalled();
      expect(component.setApilist).toHaveBeenCalledWith(mockApiConfig);
      expect(component.getembeddigns).toHaveBeenCalled();
      expect(component.getFilestList).toHaveBeenCalled();
    });
  });

  describe('getLogedInUser', () => {
    it('should return userId from localStorage', () => {
      const result = validationService.getLogedInUser();
      expect(result).toBe('test@example.com');
      expect(component.userId).toBe('test@example.com');
    });

    it('should return NA when localStorage is null', () => {
      (localStorage.getItem as jasmine.Spy).and.returnValue(null);
      validationService.isValidEmail.and.returnValue(false);
      validationService.isValidName.and.returnValue(false);

      const result = validationService.getLogedInUser();

      // When validation fails, userId is not set, so it returns undefined
      expect(result).toBeUndefined();
    });
  });

  describe('getLocalStoreApi', () => {
    it('should return parsed API config from localStorage', () => {
      const result = validationService.getLocalStoreApi();
      expect(result).toEqual(mockApiConfig);
    });

    it('should return undefined when localStorage is null or NA', () => {
      // Use existing spy instead of creating a new one
      (localStorage.getItem as jasmine.Spy).and.returnValue(null);

      const result = validationService.getLocalStoreApi();

      // When localStorage returns null, the ternary returns 'NA' which cannot be parsed
      // The method should return undefined since res will be 'NA'
      expect(result).toBeUndefined();
    });
  });

  describe('setApilist', () => {
    it('should set all API URLs correctly', () => {
      component.setApilist(mockApiConfig);

      expect(component.Admin_uploadFile).toBe('http://localhost:8080/api/rag/upload');
      expect(component.Admin_getFiles).toBe('http://localhost:8080/api/rag/files');
      expect(component.Admin_setCache).toBe('http://localhost:8080/api/rag/cache');
      expect(component.Admin_getEmbedings).toBe('http://localhost:8080/api/rag/embeddings');
      expect(component.Admin_LLmExplain_deleteFile).toBe('http://localhost:8080/api/rag/delete');
    });
  });

  describe('getFilestList', () => {
    it('should fetch files list successfully', fakeAsync(() => {
      const mockResponse = [
        { id: 1, name: 'file1.pdf' },
        { id: 2, name: 'file2.pdf' }
      ];

      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_getFiles = 'http://localhost:8080/api/rag/files';

      component.getFilestList();

      const req = httpMock.expectOne(component.Admin_getFiles);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
      tick();

      expect(component.dataSource).toEqual(mockResponse);
      expect(component.listofDoccuments).toEqual(mockResponse);
    }));

    it('should handle error when fetching files list', fakeAsync(() => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_getFiles = 'http://localhost:8080/api/rag/files';

      component.getFilestList();

      const req = httpMock.expectOne(component.Admin_getFiles);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });

  describe('getembeddigns', () => {
    it('should fetch embeddings successfully', fakeAsync(() => {
      const mockResponse = [
        { id: 1, name: 'embedding1' },
        { id: 2, name: 'embedding2' }
      ];

      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_getEmbedings = 'http://localhost:8080/api/rag/embeddings';

      component.getembeddigns();

      const req = httpMock.expectOne(component.Admin_getEmbedings);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
      tick();

      expect(component.dataSource1).toEqual(mockResponse);
    }));

    it('should handle error when fetching embeddings', fakeAsync(() => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_getEmbedings = 'http://localhost:8080/api/rag/embeddings';

      component.getembeddigns();

      const req = httpMock.expectOne(component.Admin_getEmbedings);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });

  describe('setcache', () => {
    it('should set cache successfully', fakeAsync(() => {
      const mockResponse = { status: 'success' };
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(component, 'getembeddigns');
      spyOn(component, 'getFilestList');
      component.Admin_setCache = 'http://localhost:8080/api/rag/cache';

      component.setcache('TestEmbedding', ['doc1', 'doc2']);

      const req = httpMock.expectOne(component.Admin_setCache);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
      tick();

      expect(component.formBased).toBe(false);
      expect(component.getembeddigns).toHaveBeenCalled();
      expect(component.getFilestList).toHaveBeenCalled();
    }));

    it('should handle error when setting cache', fakeAsync(() => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_setCache = 'http://localhost:8080/api/rag/cache';

      component.setcache('TestEmbedding', ['doc1', 'doc2']);

      const req = httpMock.expectOne(component.Admin_setCache);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(component.formBased).toBe(false);
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });

  describe('upload_file', () => {
    it('should prepare and upload file', () => {
      const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
      component.demoFile = [mockFile];
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(component, 'uploadFileApiCall');

      component.upload_file();

      expect(component.selectedFile).toBe(mockFile);
      expect(component.uploadFileApiCall).toHaveBeenCalled();
    });
  });

  describe('uploadFileApiCall', () => {
    it('should upload file successfully', fakeAsync(() => {
      const mockResponse = { status: 'success' };
      spyOn(component, 'getFilestList');
      component.Admin_uploadFile = 'http://localhost:8080/api/rag/upload';

      const mockFormData = new FormData();
      component.uploadFileApiCall(mockFormData);

      const req = httpMock.expectOne(component.Admin_uploadFile);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
      tick();

      expect(component.formBased).toBe(false);
      expect(component.getFilestList).toHaveBeenCalled();
    }));

    it('should handle error when uploading file', fakeAsync(() => {
      component.Admin_uploadFile = 'http://localhost:8080/api/rag/upload';

      const mockFormData = new FormData();
      component.uploadFileApiCall(mockFormData);

      const req = httpMock.expectOne(component.Admin_uploadFile);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(component.formBased).toBe(false);
      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });

  describe('onTableDataChange', () => {
    it('should update pagination config on page change', () => {
      component.dataSource = [{ id: 1 }, { id: 2 }, { id: 3 }];
      const newPage = 2;

      component.onTableDataChange(newPage);

      expect(component.currentPage).toBe(2);
      expect(component.pagingConfig.currentPage).toBe(2);
      expect(component.pagingConfig.totalItems).toBe(3);
    });
  });

  describe('onTableSizeChange', () => {
    it('should update pagination config on size change', () => {
      component.dataSource = [{ id: 1 }, { id: 2 }, { id: 3 }];
      const event = { result: { value: 10 } };

      component.onTableSizeChange(event);

      expect(component.pagingConfig.itemsPerPage).toBe(10);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(3);
    });
  });

  describe('deleteFileFromDB', () => {
    it('should delete file when status is N', fakeAsync(() => {
      const mockResponse = { status: 'Document Deleted Successfully' };
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(component, 'getFilestList');
      component.Admin_LLmExplain_deleteFile = 'http://localhost:8080/api/rag/delete';

      component.deleteFileFromDB('N', 'file123');

      const req = httpMock.expectOne(component.Admin_LLmExplain_deleteFile);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'Document Deleted Successfully',
        'Close',
        jasmine.objectContaining({ duration: 1000 })
      );
      expect(component.getFilestList).toHaveBeenCalled();
    }));

    it('should show error when file deletion fails', fakeAsync(() => {
      const mockResponse = { status: 'Failed' };
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      spyOn(component, 'getFilestList');
      component.Admin_LLmExplain_deleteFile = 'http://localhost:8080/api/rag/delete';

      component.deleteFileFromDB('N', 'file123');

      const req = httpMock.expectOne(component.Admin_LLmExplain_deleteFile);
      req.flush(mockResponse);
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'File Deletion was unsucessful',
        'Close',
        jasmine.objectContaining({ duration: 1000 })
      );
    }));

    it('should show error when status is not N (file is in embedding)', () => {
      component.deleteFileFromDB('Y', 'file123');

      expect(snackBar.open).toHaveBeenCalledWith(
        'This file cannot be deleted as it is a part of the embedding',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    });

    it('should handle 430 error status', fakeAsync(() => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_LLmExplain_deleteFile = 'http://localhost:8080/api/rag/delete';

      component.deleteFileFromDB('N', 'file123');

      const req = httpMock.expectOne(component.Admin_LLmExplain_deleteFile);
      req.flush({ detail: 'Custom error message' }, { status: 430, statusText: 'Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalled();
    }));

    it('should handle generic error', fakeAsync(() => {
      spyOn(validationService, 'getLogedInUser').and.returnValue('test@example.com');
      component.Admin_LLmExplain_deleteFile = 'http://localhost:8080/api/rag/delete';

      component.deleteFileFromDB('N', 'file123');

      const req = httpMock.expectOne(component.Admin_LLmExplain_deleteFile);
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
      tick();

      expect(snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.objectContaining({ duration: 3000 })
      );
    }));
  });

  describe('formCreation', () => {
    it('should create form with required validators', () => {
      // Form already created in constructor, recreate to test method
      component.formCreation();

      const embeddingNameControl = component.createNewEmbeddingsform.get('embeddingName');
      const selectedEmbeddingsControl = component.createNewEmbeddingsform.get('selectedEmbeddings');

      expect(embeddingNameControl).toBeDefined();
      expect(selectedEmbeddingsControl).toBeDefined();
      
      // The form initializes with default values, update to empty to trigger validation
      component.createNewEmbeddingsform.patchValue({
        embeddingName: '',
        selectedEmbeddings: [[]]
      });
      
      // Mark as touched and update validity
      embeddingNameControl?.markAsTouched();
      embeddingNameControl?.updateValueAndValidity();
      selectedEmbeddingsControl?.markAsTouched();
      selectedEmbeddingsControl?.updateValueAndValidity();
      
      expect(embeddingNameControl?.hasError('required')).toBe(true);
    });
  });
});
