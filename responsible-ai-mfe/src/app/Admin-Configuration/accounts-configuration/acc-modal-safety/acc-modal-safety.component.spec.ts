/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AccModalSafetyComponent } from './acc-modal-safety.component';

describe('AccModalSafetyComponent', () => {
  let component: AccModalSafetyComponent;
  let fixture: ComponentFixture<AccModalSafetyComponent>;

  beforeEach(async () => {
    localStorage.setItem('res', JSON.stringify({ result: {} }));
    await TestBed.configureTestingModule({
      declarations: [ AccModalSafetyComponent ],
      imports: [ MatSnackBarModule, HttpClientTestingModule, NoopAnimationsModule ],
      providers: [
        { provide: MatDialogRef, useValue: {} },
        { provide: MAT_DIALOG_DATA, useValue: {} }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccModalSafetyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should close dialog when closeDialog is called', () => {
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    component.dialogRef = dialogRefSpy;

    component.closeDialog();

    expect(dialogRefSpy.close).toHaveBeenCalled();
  });

  it('should call console.log with form value when updateSafetyFormEntity is called', () => {
    const mockFormValue = {
      drawingsThreshold: 0.5,
      hentaiThreshold: 0.25,
      neutralThreshold: 0.5,
      pornThreshold: 0.25,
      sexyThreshold: 0.25
    };
    
    component.SafetyFormUpdateEntity = {
      value: mockFormValue
    } as any;
    
    spyOn(console, 'log');

    component.updateSafetyFormEntity();

    expect(console.log).toHaveBeenCalledWith(mockFormValue);
  });

  it('should fetch safety form entity successfully with valid response', (done) => {
    const mockResponse = {
      dataList: [{ id: 1 }],
      drawings: 0.6,
      hentai: 0.3,
      neutral: 0.7,
      porn: 0.2,
      sexy: 0.4
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    component.SafetyFormUpdateEntity = jasmine.createSpyObj('FormGroup', ['setValue', 'patchValue']);
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.https.post).toHaveBeenCalledWith(
        'http://test.com/api/safety-list',
        { accMasterId: 'test-acc-id' }
      );
      expect(console.log).toHaveBeenCalledWith(mockResponse);
      expect(component.isLoading).toBe(false);
      expect(component.isDataEmpty).toBe(false);
      expect(component.xv).toEqual(mockResponse);
      expect(component.SafetyFormUpdateEntity.setValue).toHaveBeenCalledWith({
        drawingsThreshold: 0.6,
        hentaiThreshold: 0.3,
        neutralThreshold: 0.7,
        pornThreshold: 0.2,
        sexyThreshold: 0.4
      });
      expect(component.SafetyFormUpdateEntity.patchValue).toHaveBeenCalledWith(mockResponse);
      done();
    }, 100);
  });

  it('should handle empty response in getSafetyFormEntity', (done) => {
    const mockResponse = null;
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.isLoading).toBe(false);
      expect(component.isDataEmpty).toBe(true);
      expect(component._snackBar.open).toHaveBeenCalledWith('Value is not set. Create a mapping first.', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should handle empty object response in getSafetyFormEntity', (done) => {
    const mockResponse = {};
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.isDataEmpty).toBe(true);
      expect(component.isLoading).toBe(false);
      expect(component._snackBar.open).toHaveBeenCalledWith('Value is not set. Create a mapping first.', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should handle empty dataList in getSafetyFormEntity', (done) => {
    const mockResponse = {
      dataList: []
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.isDataEmpty).toBe(true);
      expect(component.isLoading).toBe(false);
      expect(component._snackBar.open).toHaveBeenCalledWith('Value is not set. Create a mapping first.', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should handle error with detail in getSafetyFormEntity', (done) => {
    const mockError = {
      status: 430,
      error: {
        detail: 'Safety form error occurred'
      }
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(430);
      expect(component.isLoading).toBe(false);
      expect(component._snackBar.open).toHaveBeenCalledWith('Safety form error occurred', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should handle error with message in getSafetyFormEntity', (done) => {
    const mockError = {
      status: 500,
      error: {
        message: 'Internal server error'
      }
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(500);
      expect(component.isLoading).toBe(false);
      expect(component._snackBar.open).toHaveBeenCalledWith('Internal server error', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should handle error without detail or message in getSafetyFormEntity', (done) => {
    const mockError = {
      status: 404,
      error: {}
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety-list';
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(404);
      expect(component.isLoading).toBe(false);
      expect(component._snackBar.open).toHaveBeenCalledWith('The Api has failed', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black']
      });
      done();
    }, 100);
  });

  it('should initialize with isLoading as true', () => {
    // isLoading is set to true as a property declaration, then set again in ngOnInit
    // Create a new component instance to check before ngOnInit runs
    const newComponent = new AccModalSafetyComponent(
      {} as any, {} as any, {} as any, {} as any, {} as any, { id: 'test' }
    );
    expect(newComponent.isLoading).toBe(true);
  });

  it('should initialize with isDataEmpty as false', () => {
    expect(component.isDataEmpty).toBe(false);
  });

  it('should retrieve userId from localStorage in getLogedInUser', () => {
    const mockUserId = 'safety-user-123';
    localStorage.setItem('userid', JSON.stringify(mockUserId));
    spyOn(console, 'log');

    const result = component.getLogedInUser();

    expect(result).toBe(mockUserId);
    expect(component.userId).toBe(mockUserId);
    expect(console.log).toHaveBeenCalledWith(' userId', mockUserId);
  });

  it('should return undefined when userid is not in localStorage', () => {
    localStorage.removeItem('userid');

    const result = component.getLogedInUser();

    expect(result).toBeUndefined();
  });

  it('should retrieve API configuration from localStorage in getLocalStoreApi', () => {
    const mockConfig = { 
      result: { 
        Admin: 'http://test.com', 
        setSafetyParameter: '/set-safety',
        Admin_SafetyUpdate: '/safety-update',
        Admin_AccSafetyListAccountWise: '/acc-safety-list'
      } 
    };
    localStorage.setItem('res', JSON.stringify(mockConfig));

    const result = component.getLocalStoreApi();

    expect(result).toEqual(mockConfig);
  });

  it('should return undefined when res is not in localStorage', () => {
    localStorage.removeItem('res');

    const result = component.getLocalStoreApi();

    expect(result).toBeUndefined();
  });

  it('should set API list URLs correctly in setApilist', () => {
    const mockIpPort = {
      result: {
        Admin: 'http://test.com',
        setSafetyParameter: '/set-safety',
        Admin_SafetyUpdate: '/safety-update',
        Admin_AccSafetyListAccountWise: '/acc-safety-list'
      }
    };

    component.setApilist(mockIpPort);

    expect(component.Admin_SetSafetyParamter).toBe('http://test.com/set-safety');
    expect(component.Admin_SafetyUpdate).toBe('http://test.com/safety-update');
    expect(component.Admin_AccSafetyListAccountWise).toBe('http://test.com/acc-safety-list');
  });

  it('should initialize slider properties with correct values', () => {
    expect(component.edited).toBe(false);
    expect(component.autoTicks).toBe(false);
    expect(component.disabled).toBe(false);
    expect(component.max).toBe(1);
    expect(component.min).toBe(0);
    expect(component.showTicks).toBe(true);
    expect(component.step).toBe(0.01);
    expect(component.thumbLabel).toBe(true);
  });

  it('should initialize dataSource1 as empty array', () => {
    expect(component.dataSource1).toEqual([]);
  });

  it('should set xv property when getSafetyFormEntity succeeds', (done) => {
    const mockResponse = {
      dataList: [{ id: 1 }],
      drawings: 0.8,
      hentai: 0.5,
      neutral: 0.9,
      porn: 0.3,
      sexy: 0.6
    };
    
    component.data = { id: 'test-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety';
    component.SafetyFormUpdateEntity = jasmine.createSpyObj('FormGroup', ['setValue', 'patchValue']);
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.xv).toEqual(mockResponse);
      done();
    }, 100);
  });

  it('should call setValue with correct threshold values', (done) => {
    const mockResponse = {
      dataList: [{ id: 1 }],
      drawings: 0.55,
      hentai: 0.35,
      neutral: 0.65,
      porn: 0.15,
      sexy: 0.45
    };
    
    component.data = { id: 'test-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety';
    component.SafetyFormUpdateEntity = jasmine.createSpyObj('FormGroup', ['setValue', 'patchValue']);
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(component.SafetyFormUpdateEntity.setValue).toHaveBeenCalledWith({
        drawingsThreshold: 0.55,
        hentaiThreshold: 0.35,
        neutralThreshold: 0.65,
        pornThreshold: 0.15,
        sexyThreshold: 0.45
      });
      done();
    }, 100);
  });

  it('should log response to console in getSafetyFormEntity', (done) => {
    const mockResponse = {
      dataList: [{ id: 1 }],
      drawings: 0.7,
      hentai: 0.4,
      neutral: 0.8,
      porn: 0.2,
      sexy: 0.5
    };
    
    component.data = { id: 'test-id' };
    component.Admin_AccSafetyListAccountWise = 'http://test.com/api/safety';
    component.SafetyFormUpdateEntity = jasmine.createSpyObj('FormGroup', ['setValue', 'patchValue']);
    
    spyOn(component.https, 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getSafetyFormEntity();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(mockResponse);
      done();
    }, 100);
  });

  it('should update safety parameters successfully', (done) => {
    const mockValue = 0.75;
    const mockParameter = 'drawingsThreshold';
    const mockResponse = { status: 'success' };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith('value of e', mockValue, 'valueof x', mockParameter);
      expect(component.https.patch).toHaveBeenCalledWith(
        'http://test.com/api/safety-update',
        {
          accMasterId: 'test-acc-id',
          parameters: mockParameter,
          value: mockValue
        }
      );
      expect(console.log).toHaveBeenCalledWith('value of res', mockResponse);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'drawingsThreshold value Updated Successfully',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should handle 430 error in UpdateSafePars', (done) => {
    const mockValue = 0.5;
    const mockParameter = 'hentaiThreshold';
    const mockError = {
      status: 430,
      error: {
        detail: 'Safety parameter update error'
      }
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(430);
      expect(console.log).toHaveBeenCalledWith('Safety parameter update error');
      expect(console.log).toHaveBeenCalledWith(mockError);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'Safety parameter update error',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should handle other errors in UpdateSafePars', (done) => {
    const mockValue = 0.3;
    const mockParameter = 'neutralThreshold';
    const mockError = {
      status: 500,
      error: {}
    };
    
    component.data = { id: 'test-acc-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(500);
      expect(console.log).toHaveBeenCalledWith(mockError);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should pass correct headers in UpdateSafePars', () => {
    const mockValue = 0.8;
    const mockParameter = 'pornThreshold';
    
    component.data = { id: 'test-acc-123' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: () => {}
    } as any);
    
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    expect(console.log).toHaveBeenCalledWith('value of e', 0.8, 'valueof x', 'pornThreshold');
    expect(component.https.patch).toHaveBeenCalledWith(
      'http://test.com/api/safety-update',
      {
        accMasterId: 'test-acc-123',
        parameters: 'pornThreshold',
        value: 0.8
      }
    );
  });

  it('should display success message with parameter name in UpdateSafePars', (done) => {
    const mockValue = 0.45;
    const mockParameter = 'sexyThreshold';
    const mockResponse = { status: 'success' };
    
    component.data = { id: 'test-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'sexyThreshold value Updated Successfully',
        'Close',
        jasmine.objectContaining({
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        })
      );
      done();
    }, 100);
  });

  it('should log response value in UpdateSafePars', (done) => {
    const mockValue = 0.6;
    const mockParameter = 'testParameter';
    const mockResponse = { status: 'success', data: 'test data' };
    
    component.data = { id: 'test-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith('value of res', mockResponse);
      done();
    }, 100);
  });

  it('should handle error without detail in UpdateSafePars', (done) => {
    const mockValue = 0.7;
    const mockParameter = 'drawings';
    const mockError = {
      status: 404,
      error: {
        message: 'Not found'
      }
    };
    
    component.data = { id: 'test-id' };
    component.Admin_SafetyUpdate = 'http://test.com/api/safety-update';
    
    spyOn(component.https, 'patch').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.UpdateSafePars(mockValue, mockParameter);

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(404);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });
});
