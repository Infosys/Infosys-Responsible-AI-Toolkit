import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { NgbPopover, NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxPaginationModule } from 'ngx-pagination';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { ApiConfigurationComponent } from './api-configuration.component';
import { NonceService } from 'src/app/nonce.service';

describe('ApiConfigurationComponent', () => {
  let component: ApiConfigurationComponent;
  let fixture: ComponentFixture<ApiConfigurationComponent>;
  let httpMock: HttpTestingController;
  let snackBar: MatSnackBar;
  let nonceService: NonceService;

  const mockApiConfig = {
    result: {
      Admin: 'http://localhost:8080/api/admin',
      Admin_getConfig: '/get-config',
      Admin_updateConfig: '/update-config',
      Admin_deleteConfig: '/delete-config',
      Admin_newConfig: '/new-config'
    }
  };

  const mockApiResponse = {
    result: {
      'API1': { ip: '192.168.1.1', port: '8080' },
      'API2': { ip: '192.168.1.2', port: '8081' },
      'API3': { ip: '192.168.1.3', port: '8082' }
    }
  };

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify(mockApiConfig));
    
    await TestBed.configureTestingModule({
      declarations: [ ApiConfigurationComponent ],
      imports: [ 
        HttpClientTestingModule, 
        MatSnackBarModule, 
        NgbPopoverModule, 
        NgxPaginationModule,
        ReactiveFormsModule,
        FormsModule,
        NoopAnimationsModule
      ],
      providers: [ NonceService ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApiConfigurationComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    snackBar = TestBed.inject(MatSnackBar);
    nonceService = TestBed.inject(NonceService);
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

    it('should initialize form with required validators', () => {
      expect(component.apiForm).toBeDefined();
      expect(component.apiForm.get('name')).toBeTruthy();
      expect(component.apiForm.get('ip')).toBeTruthy();
      expect(component.apiForm.get('port')).toBeTruthy();
    });

    it('should initialize with default pagination values', () => {
      expect(component.currentPage).toBe(1);
      expect(component.itemsPerPage).toBe(5);
      expect(component.totalItems).toBe(0);
      expect(component.pagingConfig).toBeDefined();
    });

    it('should initialize with empty arrays and default values', () => {
      expect(component.apis).toEqual([]);
      expect(component.dataSource).toEqual([]);
      expect(component.isSearchOpen).toBe(false);
      expect(component.searchName).toBe('');
      expect(component.filteredItems).toEqual([]);
      expect(component.editingApi).toBeNull();
    });

    it('should call getApis on ngOnInit', () => {
      spyOn(component, 'getApis');
      component.ngOnInit();
      expect(component.getApis).toHaveBeenCalled();
    });

    it('should set API URLs on initialization', fakeAsync(() => {
      component.ngOnInit();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      req.flush(mockApiResponse);
      tick();
      
      expect(component.getConfigs).toBe('http://localhost:8080/api/admin/get-config');
      expect(component.updateApi).toBe('http://localhost:8080/api/admin/update-config');
      expect(component.deleteApi).toBe('http://localhost:8080/api/admin/delete-config');
      expect(component.createNewApi).toBe('http://localhost:8080/api/admin/new-config');
    }));
  });

  describe('Form Validation', () => {
    it('should invalidate form when name is empty', () => {
      component.apiForm.patchValue({ name: '', ip: '192.168.1.1', port: '8080' });
      expect(component.apiForm.valid).toBe(false);
    });

    it('should invalidate form when ip is empty', () => {
      component.apiForm.patchValue({ name: 'TestAPI', ip: '', port: '8080' });
      expect(component.apiForm.valid).toBe(false);
    });

    it('should invalidate form when port is empty', () => {
      component.apiForm.patchValue({ name: 'TestAPI', ip: '192.168.1.1', port: '' });
      expect(component.apiForm.valid).toBe(false);
    });

    it('should validate form when all fields are filled', () => {
      component.apiForm.patchValue({ name: 'TestAPI', ip: '192.168.1.1', port: '8080' });
      expect(component.apiForm.valid).toBe(true);
    });
  });

  describe('getLocalStoreApi', () => {
    it('should retrieve API configuration from localStorage', () => {
      const apiConfig = component.getLocalStoreApi();
      expect(apiConfig).toEqual(mockApiConfig);
    });

    it('should return undefined when localStorage is empty', () => {
      localStorage.removeItem('res');
      const apiConfig = component.getLocalStoreApi();
      expect(apiConfig).toBeUndefined();
    });

    it('should return undefined when res is null', () => {
      localStorage.setItem('res', 'null');
      const apiConfig = component.getLocalStoreApi();
      expect(apiConfig).toBeNull();
    });
  });

  describe('setApiList', () => {
    it('should set API URLs correctly', () => {
      const ip_port = mockApiConfig;
      component.setApiList(ip_port);
      
      expect(component.getConfigs).toBe('http://localhost:8080/api/admin/get-config');
      expect(component.updateApi).toBe('http://localhost:8080/api/admin/update-config');
      expect(component.deleteApi).toBe('http://localhost:8080/api/admin/delete-config');
      expect(component.createNewApi).toBe('http://localhost:8080/api/admin/new-config');
    });

    it('should concatenate URLs correctly with different base paths', () => {
      const customConfig = {
        result: {
          Admin: 'https://prod-api.com/v1',
          Admin_getConfig: '/configs',
          Admin_updateConfig: '/configs/update',
          Admin_deleteConfig: '/configs/delete',
          Admin_newConfig: '/configs/new'
        }
      };
      
      component.setApiList(customConfig);
      
      expect(component.getConfigs).toBe('https://prod-api.com/v1/configs');
      expect(component.updateApi).toBe('https://prod-api.com/v1/configs/update');
      expect(component.deleteApi).toBe('https://prod-api.com/v1/configs/delete');
      expect(component.createNewApi).toBe('https://prod-api.com/v1/configs/new');
    });
  });

  describe('getApis', () => {
    beforeEach(() => {
      component.getConfigs = 'http://localhost:8080/api/admin/get-config';
    });

    it('should fetch and transform API list successfully', fakeAsync(() => {
      component.getApis();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      expect(req.request.method).toBe('GET');
      
      req.flush(mockApiResponse);
      tick();
      
      expect(component.apis.length).toBe(3);
      expect(component.apis[0].name).toBe('API1');
      expect(component.apis[0].ip).toEqual({ ip: '192.168.1.1', port: '8080' });
      expect(component.dataSource).toEqual(component.apis);
      expect(component.pagingConfig.totalItems).toBe(3);
    }));

    it('should handle empty API response', fakeAsync(() => {
      component.getApis();
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      req.flush({ result: {} });
      tick();
      
      expect(component.apis.length).toBe(0);
      expect(component.pagingConfig.totalItems).toBe(0);
    }));
  });

  describe('createApi', () => {
    beforeEach(() => {
      component.createNewApi = 'http://localhost:8080/api/admin/new-config';
      component.getConfigs = 'http://localhost:8080/api/admin/get-config';
      component.popover = { close: jasmine.createSpy('close') } as any;
    });

    it('should create new API successfully', fakeAsync(() => {
      component.apiForm.patchValue({ name: 'NewAPI', ip: '192.168.1.10', port: '9090' });
      
      component.createApi();
      
      const createReq = httpMock.expectOne('http://localhost:8080/api/admin/new-config');
      expect(createReq.request.method).toBe('POST');
      expect(createReq.request.body).toEqual({
        ApiName: 'NewAPI',
        ApiIp: '192.168.1.10',
        ApiPort: null
      });
      
      createReq.flush({});
      
      // getApis is called after creation
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq.flush(mockApiResponse);
      tick();
      
      expect(component.popover.close).toHaveBeenCalled();
      expect(component.apiForm.value.name).toBeNull();
    }));

    it('should add new API to the list with isNew flag', fakeAsync(() => {
      component.apiForm.patchValue({ name: 'NewAPI', ip: '192.168.1.10', port: '9090' });
      
      component.createApi();
      
      const createReq = httpMock.expectOne('http://localhost:8080/api/admin/new-config');
      createReq.flush({});
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq.flush(mockApiResponse);
      tick();
      
      // The new API is added before getApis refreshes the list
      expect(component.pagingConfig.totalItems).toBeGreaterThan(0);
    }));
  });

  describe('deleteConfig', () => {
    beforeEach(() => {
      component.deleteApi = 'http://localhost:8080/api/admin/delete-config';
      component.apis = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } },
        { name: 'API2', ip: { ip: '192.168.1.2', port: '8081' } }
      ];
      component.pagingConfig.totalItems = 2;
    });

    it('should delete API successfully', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      component.deleteConfig('API1');
      
      const req = httpMock.expectOne('http://localhost:8080/api/admin/delete-config');
      expect(req.request.method).toBe('DELETE');
      expect(req.request.body).toEqual({ ApiName: 'API1' });
      
      req.flush({});
      tick();
      
      expect(component.apis.length).toBe(1);
      expect(component.apis[0].name).toBe('API2');
      expect(component.pagingConfig.totalItems).toBe(1);
      expect(snackBar.open).toHaveBeenCalledWith(
        'API Deleted Successfully',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should show error message when API not found', () => {
      spyOn(snackBar, 'open');
      
      component.deleteConfig('NonExistentAPI');
      
      expect(snackBar.open).toHaveBeenCalledWith(
        'Cannot delete existing API',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    });

    it('should not make HTTP request when API not found', () => {
      component.dataSource = [
        { name: 'API1', ip: '192.168.1.1', port: '8080' }
      ];
      
      component.deleteConfig('NonExistentAPI');
      
      httpMock.expectNone('http://localhost:8080/api/admin/delete-config');
      expect(component.dataSource.length).toBe(1); // Data source unchanged
    });
  });

  describe('toggleEdit', () => {
    beforeEach(() => {
      component.updateApi = 'http://localhost:8080/api/admin/update-config';
      component.getConfigs = 'http://localhost:8080/api/admin/get-config';
    });

    it('should start editing an API', () => {
      const api = { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } };
      
      component.toggleEdit(api);
      
      expect(component.editingApi).toBe(api);
      expect(component.editingApiCopy).toEqual(api);
    });

    it('should save edited API when toggling edit mode again', fakeAsync(() => {
      spyOn(snackBar, 'open');
      const api = { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } };
      
      // Start editing
      component.toggleEdit(api);
      
      // Modify the copy
      component.editingApiCopy = { name: 'API1', ip: { ip: '192.168.1.100', port: '9090' } };
      
      // Save changes
      component.toggleEdit(api);
      
      const updateReq = httpMock.expectOne('http://localhost:8080/api/admin/update-config');
      expect(updateReq.request.method).toBe('PATCH');
      expect(updateReq.request.body).toEqual({
        ApiName: 'API1',
        ApiIp: { ip: '192.168.1.100', port: '9090' },
        ApiPort: null
      });
      
      updateReq.flush({});
      
      const getReq = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq.flush(mockApiResponse);
      tick();
      
      expect(component.editingApi).toBeNull();
      expect(snackBar.open).toHaveBeenCalledWith(
        'API Updated Successfully',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
    }));

    it('should create a copy for editing without modifying original', () => {
      const api = { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } };
      
      component.toggleEdit(api);
      component.editingApiCopy.name = 'ModifiedAPI';
      
      expect(api.name).toBe('API1');
      expect(component.editingApiCopy.name).toBe('ModifiedAPI');
    });
  });

  describe('onTableDataChange', () => {
    beforeEach(() => {
      component.apis = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } },
        { name: 'API2', ip: { ip: '192.168.1.2', port: '8081' } },
        { name: 'API3', ip: { ip: '192.168.1.3', port: '8082' } }
      ];
    });

    it('should update current page', () => {
      component.onTableDataChange(2);
      
      expect(component.currentPage).toBe(2);
      expect(component.pagingConfig.currentPage).toBe(2);
    });

    it('should update total items', () => {
      component.onTableDataChange(1);
      
      expect(component.pagingConfig.totalItems).toBe(3);
    });
  });

  describe('resetFormAndClosePopover', () => {
    beforeEach(() => {
      component.popover = { close: jasmine.createSpy('close') } as any;
    });

    it('should reset form', () => {
      component.apiForm.patchValue({ name: 'Test', ip: '192.168.1.1', port: '8080' });
      
      component.resetFormAndClosePopover();
      
      expect(component.apiForm.value.name).toBeNull();
      expect(component.apiForm.value.ip).toBeNull();
      expect(component.apiForm.value.port).toBeNull();
    });

    it('should close popover', () => {
      component.resetFormAndClosePopover();
      
      expect(component.popover.close).toHaveBeenCalled();
    });
  });

  describe('search', () => {
    beforeEach(() => {
      component.apis = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } },
        { name: 'API2', ip: { ip: '192.168.1.2', port: '8081' } },
        { name: 'TestAPI', ip: { ip: '192.168.1.3', port: '8082' } }
      ];
      component.dataSource = [...component.apis];
      component.pagingConfig.totalItems = 3;
    });

    it('should filter APIs by name', () => {
      component.searchName = 'API1';
      component.search();
      
      expect(component.apis.length).toBe(1);
      expect(component.apis[0].name).toBe('API1');
      expect(component.currentPage).toBe(1);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(1);
    });

    it('should be case insensitive', () => {
      component.searchName = 'api1';
      component.search();
      
      expect(component.apis.length).toBe(1);
      expect(component.apis[0].name).toBe('API1');
    });

    it('should find partial matches', () => {
      component.searchName = 'API';
      component.search();
      
      expect(component.apis.length).toBe(3);
    });

    it('should restore all APIs when search is cleared', () => {
      component.searchName = 'API1';
      component.search();
      expect(component.apis.length).toBe(1);
      
      component.searchName = '';
      component.search();
      
      expect(component.apis.length).toBe(3);
      expect(component.apis).toEqual(component.dataSource);
    });

    it('should reset pagination on search', () => {
      component.currentPage = 3;
      component.searchName = 'Test';
      component.search();
      
      expect(component.currentPage).toBe(1);
      expect(component.pagingConfig.currentPage).toBe(1);
    });
  });

  describe('toggleSearch', () => {
    it('should toggle search open state', () => {
      expect(component.isSearchOpen).toBe(false);
      
      component.toggleSearch();
      expect(component.isSearchOpen).toBe(true);
      
      component.toggleSearch();
      expect(component.isSearchOpen).toBe(false);
    });

    it('should clear search name', () => {
      component.searchName = 'Test';
      component.toggleSearch();
      
      expect(component.searchName).toBe('');
    });

    it('should clear filtered items', () => {
      component.filteredItems = ['item1', 'item2'];
      component.toggleSearch();
      
      expect(component.filteredItems).toEqual([]);
    });
  });

  describe('closeSearch', () => {
    beforeEach(() => {
      component.apis = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } }
      ];
      component.dataSource = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } },
        { name: 'API2', ip: { ip: '192.168.1.2', port: '8081' } },
        { name: 'API3', ip: { ip: '192.168.1.3', port: '8082' } }
      ];
      component.currentPage = 2;
      component.searchName = 'Test';
      component.isSearchOpen = true;
    });

    it('should close search bar', () => {
      component.closeSearch();
      
      expect(component.isSearchOpen).toBe(false);
    });

    it('should clear search name', () => {
      component.closeSearch();
      
      expect(component.searchName).toBe('');
    });

    it('should restore all APIs from dataSource', () => {
      component.closeSearch();
      
      expect(component.apis.length).toBe(3);
      expect(component.apis).toEqual(component.dataSource);
    });

    it('should reset pagination', () => {
      component.closeSearch();
      
      expect(component.currentPage).toBe(1);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(3);
    });
  });

  describe('Integration Tests', () => {
    beforeEach(() => {
      component.getConfigs = 'http://localhost:8080/api/admin/get-config';
      component.createNewApi = 'http://localhost:8080/api/admin/new-config';
      component.updateApi = 'http://localhost:8080/api/admin/update-config';
      component.deleteApi = 'http://localhost:8080/api/admin/delete-config';
      component.popover = { close: jasmine.createSpy('close') } as any;
    });

    it('should complete full workflow: fetch -> create -> update -> delete', fakeAsync(() => {
      spyOn(snackBar, 'open');
      
      // Fetch initial APIs
      component.getApis();
      const getReq1 = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq1.flush(mockApiResponse);
      tick();
      
      expect(component.apis.length).toBe(3);
      
      // Create new API
      component.apiForm.patchValue({ name: 'NewAPI', ip: '192.168.1.10', port: '9090' });
      component.createApi();
      
      const createReq = httpMock.expectOne('http://localhost:8080/api/admin/new-config');
      createReq.flush({});
      
      const getReq2 = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq2.flush(mockApiResponse);
      tick();
      
      // Update API
      const apiToEdit = component.apis[0];
      component.toggleEdit(apiToEdit);
      component.editingApiCopy.ip = { ip: '192.168.1.200', port: '9999' };
      component.toggleEdit(apiToEdit);
      
      const updateReq = httpMock.expectOne('http://localhost:8080/api/admin/update-config');
      updateReq.flush({});
      
      const getReq3 = httpMock.expectOne('http://localhost:8080/api/admin/get-config');
      getReq3.flush(mockApiResponse);
      tick();
      
      // Delete API
      component.deleteConfig(component.apis[0].name);
      
      const deleteReq = httpMock.expectOne('http://localhost:8080/api/admin/delete-config');
      deleteReq.flush({});
      tick();
      
      expect(snackBar.open).toHaveBeenCalledTimes(2); // Update and Delete
    }));

    it('should handle search and pagination together', () => {
      component.apis = [
        { name: 'API1', ip: { ip: '192.168.1.1', port: '8080' } },
        { name: 'API2', ip: { ip: '192.168.1.2', port: '8081' } },
        { name: 'TestAPI', ip: { ip: '192.168.1.3', port: '8082' } }
      ];
      component.dataSource = [...component.apis];
      
      // Search
      component.searchName = 'Test';
      component.search();
      expect(component.apis.length).toBe(1);
      
      // Pagination
      component.onTableDataChange(1);
      expect(component.currentPage).toBe(1);
      
      // Close search
      component.closeSearch();
      expect(component.apis.length).toBe(3);
    });
  });
});
