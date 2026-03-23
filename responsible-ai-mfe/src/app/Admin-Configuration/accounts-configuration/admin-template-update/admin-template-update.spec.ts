/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { AccountsConfigurationModalCreateTemplateUpdateComponent } from './admin-template-update';

describe('AccountsConfigurationModalCreateTemplateUpdateComponent', () => {
  let component: AccountsConfigurationModalCreateTemplateUpdateComponent;
  let fixture: ComponentFixture<AccountsConfigurationModalCreateTemplateUpdateComponent>;

  beforeEach(async () => {
    // Set up localStorage with proper structure
    localStorage.setItem('res', JSON.stringify({ 
      result: {
        Admin: 'http://test.com',
        Admin_PrivacyEncrypt: '/privacy-encrypt',
        Admin_ThresholdUpdate: '/threshold-update'
      } 
    }));
    localStorage.setItem('userid', JSON.stringify('test-user-123'));

    await TestBed.configureTestingModule({
      declarations: [ AccountsConfigurationModalCreateTemplateUpdateComponent ],
      imports: [ HttpClientTestingModule, MatSnackBarModule, MatDialogModule ],
      providers: [
        { provide: MatDialogRef, useValue: { close: jasmine.createSpy('close') } },
        { provide: MAT_DIALOG_DATA, useValue: { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' } }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccountsConfigurationModalCreateTemplateUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    localStorage.clear();
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

  it('should toggle all selections for select1 when checked is true', () => {
    const mockEvent = { checked: true };
    const mockOption1 = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    const mockOption2 = { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected1 = false;
    component.toggleAllSelection1(mockEvent);

    expect(component.event1).toEqual(mockEvent);
    expect(component.c1).toBe(true);
    expect(component.allSelected1).toBe(true);
    expect(mockOption1.select).toHaveBeenCalled();
    expect(mockOption2.select).toHaveBeenCalled();
    expect(component.listShowlist1.has('option1')).toBe(true);
    expect(component.listShowlist1.has('option2')).toBe(true);
    expect(component.select1.close).toHaveBeenCalled();
  });

  it('should toggle all selections for select1 when checked is false', () => {
    const mockEvent = { checked: false };
    const mockOption1 = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    const mockOption2 = { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected1 = true;
    component.listShowlist1.add('option1');
    component.listShowlist1.add('option2');

    component.toggleAllSelection1(mockEvent);

    expect(component.event1).toEqual(mockEvent);
    expect(component.c1).toBe(false);
    expect(component.allSelected1).toBe(false);
    expect(mockOption1.deselect).toHaveBeenCalled();
    expect(mockOption2.deselect).toHaveBeenCalled();
    expect(component.listShowlist1.has('option1')).toBe(false);
    expect(component.listShowlist1.has('option2')).toBe(false);
  });

  it('should hide listbox element when toggling select1 to select all', () => {
    const mockEvent = { checked: true };
    const mockElement = document.createElement('div');
    mockElement.setAttribute('role', 'listbox');
    document.body.appendChild(mockElement);

    const mockOption = { 
      value: 'option1', 
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected1 = false;
    component.toggleAllSelection1(mockEvent);

    expect(mockElement.style.display).toBe('none');

    document.body.removeChild(mockElement);
  });

  it('should update selection status for select1 when all items are selected', () => {
    const mockOption1 = { value: 'option1', selected: true };
    const mockOption2 = { value: 'option2', selected: true };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      }
    } as any;

    component.allSelected1 = true;
    component.selectRecognizertype();

    expect(component.allSelectedInput).toBe(true);
    expect(component.listShowlist1.has('option1')).toBe(true);
    expect(component.listShowlist1.has('option2')).toBe(true);
  });

  it('should update selection status for select1 when some items are not selected', () => {
    const mockOption1 = { value: 'option1', selected: true };
    const mockOption2 = { value: 'option2', selected: false };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      }
    } as any;

    component.allSelected1 = true;
    component.listShowlist1.add('option1');
    component.listShowlist1.add('option2');
    
    component.selectRecognizertype();

    expect(component.allSelected1).toBe(false);
    expect(component.allSelectedInput).toBe(false);
    expect(component.listShowlist1.has('option1')).toBe(true);
    expect(component.listShowlist1.has('option2')).toBe(false);
  });

  it('should toggle all selections for select2 when checked is true', () => {
    const mockEvent = { checked: true };
    const mockOption1 = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    const mockOption2 = { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected2 = false;
    component.toggleAllSelection2(mockEvent);

    expect(component.event2).toEqual(mockEvent);
    expect(component.c2).toBe(true);
    expect(component.allSelected2).toBe(true);
    expect(mockOption1.select).toHaveBeenCalled();
    expect(mockOption2.select).toHaveBeenCalled();
    expect(component.listShowlist2.has('option1')).toBe(true);
    expect(component.listShowlist2.has('option2')).toBe(true);
    expect(component.select2.close).toHaveBeenCalled();
  });

  it('should toggle all selections for select2 when checked is false', () => {
    const mockEvent = { checked: false };
    const mockOption1 = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    const mockOption2 = { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected2 = true;
    component.listShowlist2.add('option1');
    component.listShowlist2.add('option2');

    component.toggleAllSelection2(mockEvent);

    expect(component.event2).toEqual(mockEvent);
    expect(component.c2).toBe(false);
    expect(component.allSelected2).toBe(false);
    expect(mockOption1.deselect).toHaveBeenCalled();
    expect(mockOption2.deselect).toHaveBeenCalled();
    expect(component.listShowlist2.has('option1')).toBe(false);
    expect(component.listShowlist2.has('option2')).toBe(false);
  });

  it('should hide listbox element when toggling select2 to select all', () => {
    const mockEvent = { checked: true };
    const mockElement = document.createElement('div');
    mockElement.setAttribute('role', 'listbox');
    document.body.appendChild(mockElement);

    const mockOption = { 
      value: 'option1', 
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected2 = false;
    component.toggleAllSelection2(mockEvent);

    expect(mockElement.style.display).toBe('none');

    document.body.removeChild(mockElement);
  });

  it('should update selection status for select2 when all items are selected', () => {
    const mockOption1 = { value: 'option1', selected: true };
    const mockOption2 = { value: 'option2', selected: true };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      }
    } as any;

    component.allSelected2 = true;
    component.selectRecognizertype2();

    expect(component.allSelectedInput2).toBe(true);
    expect(component.listShowlist2.has('option1')).toBe(true);
    expect(component.listShowlist2.has('option2')).toBe(true);
  });

  it('should update selection status for select2 when some items are not selected', () => {
    const mockOption1 = { value: 'option1', selected: true };
    const mockOption2 = { value: 'option2', selected: false };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      }
    } as any;

    component.allSelected2 = true;
    component.listShowlist2.add('option1');
    component.listShowlist2.add('option2');
    
    component.selectRecognizertype2();

    expect(component.allSelected2).toBe(false);
    expect(component.allSelectedInput2).toBe(false);
    expect(component.listShowlist2.has('option1')).toBe(true);
    expect(component.listShowlist2.has('option2')).toBe(false);
  });

  it('should initialize listShowlist1 as empty Set', () => {
    expect(component.listShowlist1).toBeInstanceOf(Set);
    expect(component.listShowlist1.size).toBe(0);
  });

  it('should initialize listShowlist2 as empty Set', () => {
    expect(component.listShowlist2).toBeInstanceOf(Set);
    expect(component.listShowlist2.size).toBe(0);
  });

  it('should initialize boolean flags correctly', () => {
    expect(component.allSelectedInput).toBe(false);
    expect(component.c1).toBe(false);
    expect(component.allSelectedInput2).toBe(false);
    expect(component.c2).toBe(false);
  });

  it('should add multiple items to listShowlist1 when toggling select all', () => {
    const mockEvent = { checked: true };
    const mockOptions = [
      { value: 'val1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
      { value: 'val2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
      { value: 'val3', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') }
    ];
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          mockOptions.forEach(callback);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected1 = false;
    component.toggleAllSelection1(mockEvent);

    expect(component.listShowlist1.size).toBe(3);
    expect(component.listShowlist1.has('val1')).toBe(true);
    expect(component.listShowlist1.has('val2')).toBe(true);
    expect(component.listShowlist1.has('val3')).toBe(true);
  });

  it('should remove all items from listShowlist2 when deselecting all', () => {
    const mockEvent = { checked: false };
    component.listShowlist2.add('val1');
    component.listShowlist2.add('val2');
    component.listShowlist2.add('val3');
    
    const mockOptions = [
      { value: 'val1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
      { value: 'val2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
      { value: 'val3', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') }
    ];
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          mockOptions.forEach(callback);
        }
      },
      close: jasmine.createSpy('close')
    } as any;

    component.allSelected2 = true;
    component.toggleAllSelection2(mockEvent);

    expect(component.listShowlist2.size).toBe(0);
  });

  it('should set newStatus to false in selectRecognizertype when at least one item is not selected', () => {
    const mockOption1 = { value: 'option1', selected: true };
    const mockOption2 = { value: 'option2', selected: false };
    const mockOption3 = { value: 'option3', selected: true };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
          callback(mockOption3);
        }
      }
    } as any;

    component.selectRecognizertype();

    expect(component.allSelectedInput).toBe(false);
    expect(component.allSelected1).toBe(false);
  });

  it('should properly manage listShowlist1 in selectRecognizertype', () => {
    const mockOption1 = { value: 'opt1', selected: true };
    const mockOption2 = { value: 'opt2', selected: false };
    const mockOption3 = { value: 'opt3', selected: true };
    
    component.select1 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
          callback(mockOption3);
        }
      }
    } as any;

    component.listShowlist1.add('opt1');
    component.listShowlist1.add('opt2');
    component.listShowlist1.add('opt3');

    component.selectRecognizertype();

    expect(component.listShowlist1.has('opt1')).toBe(true);
    expect(component.listShowlist1.has('opt2')).toBe(false);
    expect(component.listShowlist1.has('opt3')).toBe(true);
  });

  it('should properly manage listShowlist2 in selectRecognizertype2', () => {
    const mockOption1 = { value: 'opt1', selected: false };
    const mockOption2 = { value: 'opt2', selected: true };
    
    component.select2 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption1);
          callback(mockOption2);
        }
      }
    } as any;

    component.listShowlist2.add('opt1');
    component.listShowlist2.add('opt2');

    component.selectRecognizertype2();

    expect(component.listShowlist2.has('opt1')).toBe(false);
    expect(component.listShowlist2.has('opt2')).toBe(true);
  });

  it('should fetch selected dropdown values successfully', (done) => {
    const mockResponse = [
      { 
        category: 'SingleModel', 
        subcategory: 'Model',
        requestTemplate: 'req1',
        responseTemplate: 'res1',
        comparisonTemplate: 'comp1'
      },
      { 
        category: 'MultiModel', 
        subcategory: 'TextTemplate'
      }
    ];
    
    component.data = { id: 'test-acc-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.isLoading).toBe(false);
      expect(component.isDataEmpty).toBe(false);
      expect(component.singleModelArray.length).toBe(1);
      expect(component.multiModelArray.length).toBe(1);
      expect(component.templetUpdateFrom.patchValue).toHaveBeenCalledWith({
        requestTemplate: 'req1',
        responseTemplate: 'res1',
        comparisonTemplate: 'comp1'
      });
      done();
    }, 100);
  });

  it('should handle empty response in getslectedDropdownvalues', (done) => {
    const mockResponse: any[] = [];
    
    component.data = { id: 'test-acc-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.isLoading).toBe(false);
      expect(component.isDataEmpty).toBe(true);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'Value is not set. Create a mapping first.',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should handle null response in getslectedDropdownvalues', (done) => {
    const mockResponse = null;
    
    component.data = { id: 'test-acc-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.isDataEmpty).toBe(true);
      expect(component._snackBar.open).toHaveBeenCalled();
      done();
    }, 100);
  });

  it('should filter SingleModel and MultiModel categories correctly', (done) => {
    const mockResponse = [
      { category: 'SingleModel', subcategory: 'Model' },
      { category: 'SingleModel', subcategory: 'Template' },
      { category: 'MultiModel', subcategory: 'TextTemplate' },
      { category: 'MultiModel', subcategory: 'TextModel' },
      { category: 'MultiModel', subcategory: 'ImageTemplate' },
      { 
        category: 'SingleModel', 
        subcategory: 'Model',
        requestTemplate: 'req',
        responseTemplate: 'res',
        comparisonTemplate: 'comp'
      }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.singleModelArray.length).toBe(3);
      expect(component.multiModelArray.length).toBe(3);
      expect(console.log).toHaveBeenCalledWith('this.singleModelArray===', component.singleModelArray);
      expect(console.log).toHaveBeenCalledWith('this.multiModelArray===', component.multiModelArray);
      done();
    }, 100);
  });

  it('should segregate SinglemodelSubCetegories and SingletemplateSubCategories', (done) => {
    const mockResponse = [
      { category: 'SingleModel', subcategory: 'Model', requestTemplate: 'r1', responseTemplate: 'res1', comparisonTemplate: 'c1' },
      { category: 'SingleModel', subcategory: 'Template', requestTemplate: 'r1', responseTemplate: 'res1', comparisonTemplate: 'c1' },
      { category: 'SingleModel', subcategory: 'Model', requestTemplate: 'r1', responseTemplate: 'res1', comparisonTemplate: 'c1' }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.SinglemodelSubCetegories.length).toBe(2);
      expect(component.SingletemplateSubCategories.length).toBe(1);
      expect(console.log).toHaveBeenCalledWith('this.SinglemodelSubCetegories===', component.SinglemodelSubCetegories);
      expect(console.log).toHaveBeenCalledWith('this.SingletemplateSubCategories===', component.SingletemplateSubCategories);
      done();
    }, 100);
  });

  it('should segregate TextTemplate and TextModel categories', (done) => {
    const mockResponse = [
      { category: 'MultiModel', subcategory: 'TextTemplate', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'MultiModel', subcategory: 'TextModel', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'MultiModel', subcategory: 'TextTemplate', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.TextTemplateCategories.length).toBe(2);
      expect(component.TextModelCategories.length).toBe(1);
      expect(console.log).toHaveBeenCalledWith('this.TextTemplateCategories===', component.TextTemplateCategories);
      expect(console.log).toHaveBeenCalledWith('this.TextModelCategories===', component.TextModelCategories);
      done();
    }, 100);
  });

  it('should segregate ImageTemplate and ImageModel categories', (done) => {
    const mockResponse = [
      { category: 'MultiModel', subcategory: 'ImageTemplate', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'MultiModel', subcategory: 'ImageModel', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);
    
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.ImageTemplateCategories.length).toBe(1);
      expect(component.ImageModelCategories.length).toBe(1);
      expect(console.log).toHaveBeenCalledWith('this.ImageTemplateCategories===', component.ImageTemplateCategories);
      expect(console.log).toHaveBeenCalledWith('this.ImageModelCategories===', component.ImageModelCategories);
      done();
    }, 100);
  });

  it('should create unique subcategories for singleModelCategories', (done) => {
    const mockResponse = [
      { category: 'SingleModel', subcategory: 'Model', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'SingleModel', subcategory: 'Model', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'SingleModel', subcategory: 'Template', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.singleModelCategories.length).toBe(2);
      expect(component.singleModelCategories).toContain('Model');
      expect(component.singleModelCategories).toContain('Template');
      done();
    }, 100);
  });

  it('should create unique subcategories for multiModelCategories', (done) => {
    const mockResponse = [
      { category: 'MultiModel', subcategory: 'TextTemplate', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'MultiModel', subcategory: 'TextModel', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' },
      { category: 'MultiModel', subcategory: 'TextTemplate', requestTemplate: 'r', responseTemplate: 'res', comparisonTemplate: 'c' }
    ];
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['patchValue']);
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any) => {
        successFn(mockResponse);
      }
    } as any);

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component.multiModelCategories.length).toBe(2);
      expect(component.multiModelCategories).toContain('TextTemplate');
      expect(component.multiModelCategories).toContain('TextModel');
      done();
    }, 100);
  });

  it('should handle error with detail in getslectedDropdownvalues', (done) => {
    const mockError = {
      error: {
        detail: 'Template mapping error occurred'
      }
    };
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(mockError);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'Template mapping error occurred',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should handle error with message in getslectedDropdownvalues', (done) => {
    const mockError = {
      error: {
        message: 'Server error'
      }
    };
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');
    spyOn(console, 'log');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(console.log).toHaveBeenCalledWith(mockError);
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'Server error',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should handle error without detail or message in getslectedDropdownvalues', (done) => {
    const mockError = {
      error: {}
    };
    
    component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: (successFn: any, errorFn: any) => {
        errorFn(mockError);
      }
    } as any);
    
    spyOn(component._snackBar, 'open');

    component.getslectedDropdownvalues();

    setTimeout(() => {
      expect(component._snackBar.open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        {
          duration: 3000,
          panelClass: ['le-u-bg-black']
        }
      );
      done();
    }, 100);
  });

  it('should set correct headers for POST request in getslectedDropdownvalues', () => {
    component.data = { id: 'test-acc-id', account: 'test-account', portfolio: 'test-portfolio' };
    component.template_admin_get_selected_getTempMap = 'http://test.com/api/get-temp-map';
    
    spyOn(component['https'], 'post').and.returnValue({
      subscribe: () => {}
    } as any);

    component.getslectedDropdownvalues();

    expect(component['https'].post).toHaveBeenCalledWith(
      'http://test.com/api/get-temp-map',
      'accMasterId=test-acc-id',
      jasmine.objectContaining({
        headers: jasmine.any(Object)
      })
    );
  });

  describe('Toggle Selection Methods', () => {
    it('should toggle all selections for ModelRequest1 when checked is true', () => {
      const mockEvent = { checked: true };
      const mockOption1 = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      const mockOption2 = { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionModelRequest1(mockEvent);

      expect(mockOption1.select).toHaveBeenCalled();
      expect(mockOption2.select).toHaveBeenCalled();
      expect(component.listShowlistModelRequest1.has('option1')).toBe(true);
      expect(component.listShowlistModelRequest1.has('option2')).toBe(true);
    });

    it('should toggle all selections for ModelResponse1 when checked is false', () => {
      const mockEvent = { checked: false };
      component.listShowlistModelResponse1.add('opt1');
      component.listShowlistModelResponse1.add('opt2');
      (component as any)['allSelectedModelResponse1'] = true;
      
      const mockOption1 = { value: 'opt1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      const mockOption2 = { value: 'opt2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectModelResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionModelResponse1(mockEvent);

      expect(mockOption1.deselect).toHaveBeenCalled();
      expect(mockOption2.deselect).toHaveBeenCalled();
      expect(component.listShowlistModelResponse1.size).toBe(0);
    });

    it('should toggle all selections for TemplateRequest1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'template1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTemplateRequest1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTemplateRequest1.has('template1')).toBe(true);
    });

    it('should toggle all selections for TemplateResponse1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'template1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTemplateResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTemplateResponse1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTemplateResponse1.has('template1')).toBe(true);
    });

    it('should toggle all selections for TextTemplateRequest1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'textTemplate1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTextTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTextTemplateRequest1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTextTemplateRequest1.has('textTemplate1')).toBe(true);
    });

    it('should toggle all selections for TextTemplateResponse1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'textTemplateRes1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTextTemplateResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTextTemplateResponse1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTextTemplateResponse1.has('textTemplateRes1')).toBe(true);
    });

    it('should toggle all selections for TextModelRequest1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'textModel1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTextModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTextModelRequest1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTextModelRequest1.has('textModel1')).toBe(true);
    });

    it('should toggle all selections for TextModelResponse1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'textModelRes1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTextModelResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTextModelResponse1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistTextModelResponse1.has('textModelRes1')).toBe(true);
    });

    it('should toggle all selections for ImageTemplateRequest1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'imageTemplate1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectImageTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionImageTemplateRequest1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistImageTemplateRequest1.has('imageTemplate1')).toBe(true);
    });

    it('should toggle all selections for ImageModelRequest1', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'imageModel1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectImageModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionImageModelRequest1(mockEvent);

      expect(mockOption.select).toHaveBeenCalled();
      expect(component.listShowlistImageModelRequest1.has('imageModel1')).toBe(true);
    });

    it('should hide listbox element when toggling selections', () => {
      const mockEvent = { checked: true };
      const mockElement = document.createElement('div');
      mockElement.setAttribute('role', 'listbox');
      document.body.appendChild(mockElement);

      const mockOption = { 
        value: 'option1', 
        select: jasmine.createSpy('select'),
        deselect: jasmine.createSpy('deselect')
      };
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionModelRequest1(mockEvent);

      expect(mockElement.style.display).toBe('none');
      document.body.removeChild(mockElement);
    });

    it('should close select dropdown after toggling all selections', () => {
      const mockEvent = { checked: true };
      const mockOption = { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTemplateRequest1(mockEvent);

      expect(component.selectTemplateRequest1.close).toHaveBeenCalled();
    });

    it('should clear listShowlist when deselecting all items', () => {
      const mockEvent = { checked: false };
      component.listShowlistTextTemplateRequest1.add('item1');
      component.listShowlistTextTemplateRequest1.add('item2');
      component.listShowlistTextTemplateRequest1.add('item3');
      (component as any)['allSelectedTextTemplateRequest1'] = true;
      
      const mockOptions = [
        { value: 'item1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
        { value: 'item2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
        { value: 'item3', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') }
      ];
      
      component.selectTextTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionTextTemplateRequest1(mockEvent);

      expect(component.listShowlistTextTemplateRequest1.size).toBe(0);
    });

    it('should call deselect on all items when unchecking toggle', () => {
      const mockEvent = { checked: false };
      (component as any)['allSelectedImageTemplateRequest1'] = true;
      const mockOption1 = { value: 'opt1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      const mockOption2 = { value: 'opt2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') };
      
      component.selectImageTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionImageTemplateRequest1(mockEvent);

      expect(mockOption1.deselect).toHaveBeenCalled();
      expect(mockOption2.deselect).toHaveBeenCalled();
    });

    it('should initialize all listShowlist Sets correctly', () => {
      expect(component.listShowlistModelRequest1).toBeInstanceOf(Set);
      expect(component.listShowlistModelResponse1).toBeInstanceOf(Set);
      expect(component.listShowlistTemplateRequest1).toBeInstanceOf(Set);
      expect(component.listShowlistTemplateResponse1).toBeInstanceOf(Set);
      expect(component.listShowlistTextTemplateRequest1).toBeInstanceOf(Set);
      expect(component.listShowlistTextTemplateResponse1).toBeInstanceOf(Set);
      expect(component.listShowlistTextModelRequest1).toBeInstanceOf(Set);
      expect(component.listShowlistTextModelResponse1).toBeInstanceOf(Set);
      expect(component.listShowlistImageTemplateRequest1).toBeInstanceOf(Set);
      expect(component.listShowlistImageModelRequest1).toBeInstanceOf(Set);
    });

    it('should toggle multiple items correctly for ModelRequest1', () => {
      const mockEvent = { checked: true };
      const mockOptions = [
        { value: 'val1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
        { value: 'val2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') },
        { value: 'val3', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect') }
      ];
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            mockOptions.forEach(callback);
          }
        },
        close: jasmine.createSpy('close')
      } as any;

      component.toggleAllSelectionModelRequest1(mockEvent);

      expect(component.listShowlistModelRequest1.size).toBe(3);
      expect(component.listShowlistModelRequest1.has('val1')).toBe(true);
      expect(component.listShowlistModelRequest1.has('val2')).toBe(true);
      expect(component.listShowlistModelRequest1.has('val3')).toBe(true);
    });
  });

  describe('Update Selection Status Methods', () => {
    it('should update selection status for ModelRequest1 when all items are selected', () => {
      const mockOption1 = { value: 'option1', selected: true };
      const mockOption2 = { value: 'option2', selected: true };
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.updateSelectionStatusModelRequest1();

      expect(component.listShowlistModelRequest1.has('option1')).toBe(true);
      expect(component.listShowlistModelRequest1.has('option2')).toBe(true);
      expect((component as any)['allSelectedModelRequest1']).toBe(true);
    });

    it('should update selection status for ModelRequest1 when some items are not selected', () => {
      const mockOption1 = { value: 'option1', selected: true };
      const mockOption2 = { value: 'option2', selected: false };
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.listShowlistModelRequest1.add('option1');
      component.listShowlistModelRequest1.add('option2');

      component.updateSelectionStatusModelRequest1();

      expect(component.listShowlistModelRequest1.has('option1')).toBe(true);
      expect(component.listShowlistModelRequest1.has('option2')).toBe(false);
      expect((component as any)['allSelectedModelRequest1']).toBe(false);
    });

    it('should update selection status for ModelResponse1', () => {
      const mockOption1 = { value: 'resp1', selected: true };
      const mockOption2 = { value: 'resp2', selected: true };
      
      component.selectModelResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.updateSelectionStatusModelResponse1();

      expect(component.listShowlistModelResponse1.has('resp1')).toBe(true);
      expect(component.listShowlistModelResponse1.has('resp2')).toBe(true);
      expect((component as any)['allSelectedModelResponse1']).toBe(true);
    });

    it('should update selection status for TemplateRequest1', () => {
      const mockOption = { value: 'template1', selected: true };
      
      component.selectTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusTemplateRequest1();

      expect(component.listShowlistTemplateRequest1.has('template1')).toBe(true);
      expect((component as any)['allSelectedTemplateRequest1']).toBe(true);
    });

    it('should update selection status for TemplateResponse1', () => {
      const mockOption = { value: 'templateResp1', selected: false };
      
      component.selectTemplateResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.listShowlistTemplateResponse1.add('templateResp1');

      component.updateSelectionStatusTemplateResponse1();

      expect(component.listShowlistTemplateResponse1.has('templateResp1')).toBe(false);
      expect((component as any)['allSelectedTemplateResponse1']).toBe(false);
    });

    it('should update selection status for TextTemplateRequest1', () => {
      const mockOption = { value: 'textTemp1', selected: true };
      
      component.selectTextTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusTextTemplateRequest1();

      expect(component.listShowlistTextTemplateRequest1.has('textTemp1')).toBe(true);
    });

    it('should update selection status for TextTemplateResponse1', () => {
      const mockOption = { value: 'textTempResp1', selected: true };
      
      component.selectTextTemplateResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusTextTemplateResponse1();

      expect(component.listShowlistTextTemplateResponse1.has('textTempResp1')).toBe(true);
    });

    it('should update selection status for TextModelRequest1', () => {
      const mockOption = { value: 'textModel1', selected: true };
      
      component.selectTextModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusTextModelRequest1();

      expect(component.listShowlistTextModelRequest1.has('textModel1')).toBe(true);
    });

    it('should update selection status for TextModelResponse1', () => {
      const mockOption = { value: 'textModelResp1', selected: true };
      
      component.selectTextModelResponse1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusTextModelResponse1();

      expect(component.listShowlistTextModelResponse1.has('textModelResp1')).toBe(true);
    });

    it('should update selection status for ImageTemplateRequest1', () => {
      const mockOption = { value: 'imageTemp1', selected: true };
      
      component.selectImageTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusImageTemplateRequest1();

      expect(component.listShowlistImageTemplateRequest1.has('imageTemp1')).toBe(true);
    });

    it('should update selection status for ImageModelRequest1', () => {
      const mockOption = { value: 'imageModel1', selected: true };
      
      component.selectImageModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption);
          }
        }
      } as any;

      component.updateSelectionStatusImageModelRequest1();

      expect(component.listShowlistImageModelRequest1.has('imageModel1')).toBe(true);
    });

    it('should set allSelected to false when not all items are selected', () => {
      const mockOption1 = { value: 'opt1', selected: true };
      const mockOption2 = { value: 'opt2', selected: false };
      const mockOption3 = { value: 'opt3', selected: true };
      
      component.selectModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
            callback(mockOption3);
          }
        }
      } as any;

      (component as any)['allSelectedModelRequest1'] = true;

      component.updateSelectionStatusModelRequest1();

      expect((component as any)['allSelectedModelRequest1']).toBe(false);
    });

    it('should delete unselected items from listShowlist', () => {
      const mockOption1 = { value: 'opt1', selected: true };
      const mockOption2 = { value: 'opt2', selected: false };
      const mockOption3 = { value: 'opt3', selected: false };
      
      component.selectTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
            callback(mockOption3);
          }
        }
      } as any;

      component.listShowlistTemplateRequest1.add('opt1');
      component.listShowlistTemplateRequest1.add('opt2');
      component.listShowlistTemplateRequest1.add('opt3');

      component.updateSelectionStatusTemplateRequest1();

      expect(component.listShowlistTemplateRequest1.has('opt1')).toBe(true);
      expect(component.listShowlistTemplateRequest1.has('opt2')).toBe(false);
      expect(component.listShowlistTemplateRequest1.has('opt3')).toBe(false);
      expect(component.listShowlistTemplateRequest1.size).toBe(1);
    });

    it('should add selected items to listShowlist', () => {
      const mockOption1 = { value: 'new1', selected: true };
      const mockOption2 = { value: 'new2', selected: true };
      
      component.selectTextTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
          }
        }
      } as any;

      component.listShowlistTextTemplateRequest1.clear();

      component.updateSelectionStatusTextTemplateRequest1();

      expect(component.listShowlistTextTemplateRequest1.has('new1')).toBe(true);
      expect(component.listShowlistTextTemplateRequest1.has('new2')).toBe(true);
      expect(component.listShowlistTextTemplateRequest1.size).toBe(2);
    });

    it('should maintain correct status when all items become selected', () => {
      const mockOption1 = { value: 'item1', selected: true };
      const mockOption2 = { value: 'item2', selected: true };
      const mockOption3 = { value: 'item3', selected: true };
      
      component.selectImageTemplateRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
            callback(mockOption3);
          }
        }
      } as any;

      (component as any)['allSelectedImageTemplateRequest1'] = false;

      component.updateSelectionStatusImageTemplateRequest1();

      expect((component as any)['allSelectedImageTemplateRequest1']).toBe(true);
      expect(component.listShowlistImageTemplateRequest1.size).toBe(3);
    });

    it('should handle empty options correctly', () => {
      component.selectModelResponse1 = {
        options: {
          forEach: (callback: any) => {
            // No options
          }
        }
      } as any;

      component.updateSelectionStatusModelResponse1();

      expect((component as any)['allSelectedModelResponse1']).toBe(true);
      expect(component.listShowlistModelResponse1.size).toBe(0);
    });

    it('should update newStatus correctly throughout iteration', () => {
      const mockOption1 = { value: 'val1', selected: true };
      const mockOption2 = { value: 'val2', selected: true };
      const mockOption3 = { value: 'val3', selected: false };
      const mockOption4 = { value: 'val4', selected: true };
      
      component.selectTextModelRequest1 = {
        options: {
          forEach: (callback: any) => {
            callback(mockOption1);
            callback(mockOption2);
            callback(mockOption3);
            callback(mockOption4);
          }
        }
      } as any;

      component.updateSelectionStatusTextModelRequest1();

      expect((component as any)['allSelectedTextModelRequest1']).toBe(false);
      expect(component.listShowlistTextModelRequest1.has('val1')).toBe(true);
      expect(component.listShowlistTextModelRequest1.has('val2')).toBe(true);
      expect(component.listShowlistTextModelRequest1.has('val3')).toBe(false);
      expect(component.listShowlistTextModelRequest1.has('val4')).toBe(true);
    });
  });

  describe('Submit Single Model Methods', () => {
    beforeEach(() => {
      component.userId = 'test-user-123';
      component.selectedModelRequest = ['req1', 'req2'];
      component.selectedModelResponse = ['resp1', 'resp2'];
      component.selectedTemplateRequest = ['tempReq1', 'tempReq2'];
      component.selectedTemplateResponse = ['tempResp1', 'tempResp2'];
    });

    it('should log selected values in submitSingleModel', () => {
      spyOn(console, 'log');

      component.submitSingleModel();

      expect(console.log).toHaveBeenCalledWith('Selected Model Request:', ['req1', 'req2']);
      expect(console.log).toHaveBeenCalledWith('Selected Model Response:', ['resp1', 'resp2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Request:', ['tempReq1', 'tempReq2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Response:', ['tempResp1', 'tempResp2']);
    });

    it('should create payload with correct structure in submitSingleModel', () => {
      spyOn(console, 'log');
      
      component.submitSingleModel();

      // Verify payload structure through the method execution
      expect(component.userId).toBe('test-user-123');
    });

    it('should submit for Model subcategory in submitSingleModelx', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'TestAccount', portfolio: 'TestPortfolio' };
      component.submitSingleModelx('Model');

      expect(console.log).toHaveBeenCalledWith('Selected Model Request:', ['req1', 'req2']);
      expect(console.log).toHaveBeenCalledWith('Selected Model Response:', ['resp1', 'resp2']);
      expect(console.log).toHaveBeenCalledWith('Submitting for Model');
      expect(component.patchtemplatet).toHaveBeenCalledWith({
        userId: 'test-user-123',
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        category: 'SingleModel',
        subcategory: 'Model',
        requestTemplate: ['req1', 'req2'],
        responseTemplate: ['resp1', 'resp2'],
        comparisonTemplate: []
      });
    });

    it('should submit for Template subcategory in submitSingleModelx', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'TestAccount', portfolio: 'TestPortfolio' };
      component.submitSingleModelx('Template');

      expect(console.log).toHaveBeenCalledWith('Selected Template Request:', ['tempReq1', 'tempReq2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Response:', ['tempResp1', 'tempResp2']);
      expect(console.log).toHaveBeenCalledWith('Submitting for Template');
      expect(component.patchtemplatet).toHaveBeenCalledWith({
        userId: 'test-user-123',
        portfolio: 'TestPortfolio',
        account: 'TestAccount',
        category: 'SingleModel',
        subcategory: 'Template',
        requestTemplate: ['tempReq1', 'tempReq2'],
        responseTemplate: ['tempResp1', 'tempResp2'],
        comparisonTemplate: []
      });
    });

    it('should handle unknown subcategory in submitSingleModelx', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.submitSingleModelx('Unknown');

      expect(console.log).toHaveBeenCalledWith('Unknown value');
      expect(component.patchtemplatet).not.toHaveBeenCalled();
    });

    it('should use correct category for Model submission', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'ACC1', portfolio: 'PORT1' };
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          category: 'SingleModel',
          subcategory: 'Model'
        })
      );
    });

    it('should use correct category for Template submission', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'ACC2', portfolio: 'PORT2' };
      component.submitSingleModelx('Template');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          category: 'SingleModel',
          subcategory: 'Template'
        })
      );
    });

    it('should include userId in payload for Model', () => {
      spyOn(component, 'patchtemplatet');

      component.userId = 'user-456';
      component.data = { id: 'test-id', account: 'TestAcc', portfolio: 'TestPort' };
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          userId: 'user-456'
        })
      );
    });

    it('should include userId in payload for Template', () => {
      spyOn(component, 'patchtemplatet');

      component.userId = 'user-789';
      component.data = { id: 'test-id', account: 'TestAcc', portfolio: 'TestPort' };
      component.submitSingleModelx('Template');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          userId: 'user-789'
        })
      );
    });

    it('should use portfolio and account from data object', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'CustomAccount', portfolio: 'CustomPortfolio' };
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          portfolio: 'CustomPortfolio',
          account: 'CustomAccount'
        })
      );
    });

    it('should pass empty comparisonTemplate array for Model', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          comparisonTemplate: []
        })
      );
    });

    it('should pass empty comparisonTemplate array for Template', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Template');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          comparisonTemplate: []
        })
      );
    });

    it('should call patchtemplatet once for Model submission', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledTimes(1);
    });

    it('should call patchtemplatet once for Template submission', () => {
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Template');

      expect(component.patchtemplatet).toHaveBeenCalledTimes(1);
    });

    it('should log all console messages in correct order for Model', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Model');

      expect(console.log).toHaveBeenCalledWith('Selected Model Request:', ['req1', 'req2']);
      expect(console.log).toHaveBeenCalledWith('Selected Model Response:', ['resp1', 'resp2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Request:', ['tempReq1', 'tempReq2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Response:', ['tempResp1', 'tempResp2']);
      expect(console.log).toHaveBeenCalledWith('Submitting for Model');
    });

    it('should log all console messages in correct order for Template', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      component.submitSingleModelx('Template');

      expect(console.log).toHaveBeenCalledWith('Selected Model Request:', ['req1', 'req2']);
      expect(console.log).toHaveBeenCalledWith('Selected Model Response:', ['resp1', 'resp2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Request:', ['tempReq1', 'tempReq2']);
      expect(console.log).toHaveBeenCalledWith('Selected Template Response:', ['tempResp1', 'tempResp2']);
      expect(console.log).toHaveBeenCalledWith('Submitting for Template');
    });

    it('should handle empty selected arrays', () => {
      spyOn(console, 'log');
      spyOn(component, 'patchtemplatet');

      component.selectedModelRequest = [];
      component.selectedModelResponse = [];
      component.data = { id: 'test-id', account: 'Acc', portfolio: 'Port' };
      
      component.submitSingleModelx('Model');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          requestTemplate: [],
          responseTemplate: []
        })
      );
    });
  });

  describe('Submit Multi Model Methods', () => {
    beforeEach(() => {
      component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
      (component as any).userId = 'test-user-123';
      (component as any).selectedTextTemplateRequest = ['text-template-req-1', 'text-template-req-2'];
      (component as any).selectedTextTemplateResponse = ['text-template-res-1'];
      (component as any).selectedTextModelRequest = ['text-model-req-1'];
      (component as any).selectedTextModelResponse = ['text-model-res-1', 'text-model-res-2'];
      (component as any).selectedImageTemplateRequest = ['image-template-req-1'];
      (component as any).selectedImageModelRequest = ['image-model-req-1'];
      spyOn(component, 'patchtemplatet');
    });

    it('should log all selected values when submitMultiModel is called', () => {
      spyOn(console, 'log');
      
      component.submitMultiModel();

      expect(console.log).toHaveBeenCalledWith('Selected Text Template Request:', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('Selected Text Template Response:', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('Selected Text Model Request:', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('Selected Text Model Response:', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('Selected Image Template Request:', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('Selected Image Model Request:', jasmine.any(Array));
    });

    it('should not call patchtemplatet when submitMultiModel is called', () => {
      component.submitMultiModel();

      // submitMultiModel only logs values, it doesn't call patchtemplatet
      expect(component.patchtemplatet).not.toHaveBeenCalled();
    });

    it('should call submitMultiModelx with "TextTemplate" subcategory', () => {
      spyOn(console, 'log');
      
      component.submitMultiModelx('TextTemplate');

      expect(console.log).toHaveBeenCalledWith('Submitting for TextTemplate');
      expect(component.patchtemplatet).toHaveBeenCalled();
    });

    it('should use TextTemplate request/response when subcategory is TextTemplate', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          category: 'MultiModel',
          subcategory: 'TextTemplate',
          requestTemplate: ['text-template-req-1', 'text-template-req-2'],
          responseTemplate: ['text-template-res-1']
        })
      );
    });

    it('should include userId, portfolio, and account in TextTemplate payload', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          userId: 'test-user-123',
          portfolio: 'test-portfolio',
          account: 'test-account'
        })
      );
    });

    it('should include empty comparisonTemplate in TextTemplate payload', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          comparisonTemplate: []
        })
      );
    });

    it('should log "Unknown value" when subcategory is not recognized', () => {
      spyOn(console, 'log');
      
      component.submitMultiModelx('InvalidSubcategory');

      expect(console.log).toHaveBeenCalledWith('Unknown value');
      expect(component.patchtemplatet).not.toHaveBeenCalled();
    });

    it('should not call patchtemplatet when subcategory is unknown', () => {
      component.submitMultiModelx('UnknownType');

      expect(component.patchtemplatet).not.toHaveBeenCalled();
    });

    it('should log console message before calling patchtemplatet', () => {
      const consoleSpy = spyOn(console, 'log');
      
      component.submitMultiModelx('TextTemplate');

      expect(consoleSpy).toHaveBeenCalledBefore(component.patchtemplatet as jasmine.Spy);
    });

    it('should call patchtemplatet exactly once for TextTemplate', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledTimes(1);
    });

    it('should handle empty selectedTextTemplateRequest array', () => {
      (component as any).selectedTextTemplateRequest = [];
      
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          requestTemplate: []
        })
      );
    });

    it('should handle empty selectedTextTemplateResponse array', () => {
      (component as any).selectedTextTemplateResponse = [];
      
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          responseTemplate: []
        })
      );
    });

    it('should log correct console messages in order for TextTemplate', () => {
      spyOn(console, 'log');
      
      component.submitMultiModelx('TextTemplate');

      const logCalls = (console.log as jasmine.Spy).calls.all();
      const submittingCall = logCalls.find(call => call.args[0] === 'Submitting for TextTemplate');
      
      expect(submittingCall).toBeDefined();
    });

    it('should use correct category "MultiModel" in payload', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          category: 'MultiModel'
        })
      );
    });

    it('should use correct subcategory "TextTemplate" in payload', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          subcategory: 'TextTemplate'
        })
      );
    });

    it('should handle null or undefined subcategory gracefully', () => {
      spyOn(console, 'log');
      
      component.submitMultiModelx(null);

      expect(console.log).toHaveBeenCalledWith('Unknown value');
      expect(component.patchtemplatet).not.toHaveBeenCalled();
    });

    it('should preserve all selected values when creating payload', () => {
      component.submitMultiModelx('TextTemplate');

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          requestTemplate: jasmine.arrayContaining(['text-template-req-1', 'text-template-req-2']),
          responseTemplate: jasmine.arrayContaining(['text-template-res-1'])
        })
      );
    });
  });

  describe('getTemplateDetailSingle Method', () => {
    let httpMock: any;

    beforeEach(() => {
      httpMock = TestBed.inject(HttpTestingController);
      (component as any).userId = 'test-user-123';
      (component as any).customTemplateGetUrl = 'http://test.com/api/template/';
    });

    it('should fetch single template details successfully', (done) => {
      const mockResponse = {
        templates: [
          { templateName: 'template1', id: '1' },
          { templateName: 'template2', id: '2' },
          { templateName: 'template3', id: '3' }
        ]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('http://test.com/api/template/test-user-123') &&
        request.params.get('category') === 'SingleModel'
      );
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('accept')).toBe('application/json');
      
      req.flush(mockResponse);

      setTimeout(() => {
        expect(component.result).toEqual(mockResponse);
        expect((component as any).dataSource_getBatches).toEqual(mockResponse.templates);
        expect((component as any).RequestSingleTemplateDropDownArr).toEqual(['template1', 'template2', 'template3']);
        expect((component as any).ResponseSingleTemplateDropDownArr).toEqual(['template1', 'template2', 'template3']);
        done();
      }, 100);
    });

    it('should log the result when fetching single template details', (done) => {
      spyOn(console, 'log');
      const mockResponse = {
        templates: [{ templateName: 'test-template', id: '1' }]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect(console.log).toHaveBeenCalledWith('inside getTemplateDetail single');
        expect(console.log).toHaveBeenCalledWith('this.result===', mockResponse);
        done();
      }, 100);
    });

    it('should handle empty templates array', (done) => {
      const mockResponse = {
        templates: []
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect((component as any).RequestSingleTemplateDropDownArr).toEqual([]);
        expect((component as any).ResponseSingleTemplateDropDownArr).toEqual([]);
        done();
      }, 100);
    });

    it('should populate RequestSingleTemplateDropDownArr with template names', (done) => {
      const mockResponse = {
        templates: [
          { templateName: 'template-A', id: '1' },
          { templateName: 'template-B', id: '2' }
        ]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect((component as any).RequestSingleTemplateDropDownArr).toContain('template-A');
        expect((component as any).RequestSingleTemplateDropDownArr).toContain('template-B');
        expect((component as any).RequestSingleTemplateDropDownArr.length).toBe(2);
        done();
      }, 100);
    });

    it('should populate ResponseSingleTemplateDropDownArr with template names', (done) => {
      const mockResponse = {
        templates: [
          { templateName: 'template-X', id: '1' },
          { templateName: 'template-Y', id: '2' }
        ]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect((component as any).ResponseSingleTemplateDropDownArr).toContain('template-X');
        expect((component as any).ResponseSingleTemplateDropDownArr).toContain('template-Y');
        expect((component as any).ResponseSingleTemplateDropDownArr.length).toBe(2);
        done();
      }, 100);
    });

    it('should handle API error with error.detail message', (done) => {
      const mockErrorBody = {
        detail: 'Custom error detail'
      };
      
      spyOn(component['_snackBar'], 'open');
      spyOn(console, 'log');

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockErrorBody, { status: 400, statusText: 'Bad Request' });

      setTimeout(() => {
        expect(console.log).toHaveBeenCalled();
        expect(component['_snackBar'].open).toHaveBeenCalledWith(
          'Custom error detail',
          'Close',
          jasmine.objectContaining({ duration: 3000, panelClass: ['le-u-bg-black'] })
        );
        done();
      }, 100);
    });

    it('should handle API error with error.message', (done) => {
      const mockErrorBody = {
        message: 'Custom error message'
      };
      
      spyOn(component['_snackBar'], 'open');

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockErrorBody, { status: 500, statusText: 'Server Error' });

      setTimeout(() => {
        expect(component['_snackBar'].open).toHaveBeenCalledWith(
          'Custom error message',
          'Close',
          jasmine.any(Object)
        );
        done();
      }, 100);
    });

    it('should handle API error with default message', (done) => {
      const mockError = {};
      
      spyOn(component['_snackBar'], 'open');

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockError, { status: 404, statusText: 'Not Found' });

      setTimeout(() => {
        expect(component['_snackBar'].open).toHaveBeenCalledWith(
          'The Api has failed',
          'Close',
          jasmine.any(Object)
        );
        done();
      }, 100);
    });

    it('should set correct HTTP headers', () => {
      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      
      expect(req.request.headers.get('accept')).toBe('application/json');
      req.flush({ templates: [] });
    });

    it('should send category parameter as SingleModel', () => {
      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      
      expect(req.request.params.get('category')).toBe('SingleModel');
      req.flush({ templates: [] });
    });

    it('should use customTemplateGetUrl with userId in URL', () => {
      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url === 'http://test.com/api/template/test-user-123'
      );
      
      expect(req.request.url).toBe('http://test.com/api/template/test-user-123');
      req.flush({ templates: [] });
    });

    it('should store response in result property', (done) => {
      const mockResponse = {
        templates: [{ templateName: 'test', id: '1' }],
        someOtherData: 'value'
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect(component.result).toEqual(mockResponse);
        done();
      }, 100);
    });

    it('should store templates in dataSource_getBatches', (done) => {
      const mockTemplates = [
        { templateName: 'temp1', id: '1' },
        { templateName: 'temp2', id: '2' }
      ];
      const mockResponse = { templates: mockTemplates };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        expect((component as any).dataSource_getBatches).toEqual(mockTemplates);
        done();
      }, 100);
    });

    it('should loop through all templates and extract names', (done) => {
      const mockResponse = {
        templates: [
          { templateName: 'name1', id: '1' },
          { templateName: 'name2', id: '2' },
          { templateName: 'name3', id: '3' },
          { templateName: 'name4', id: '4' }
        ]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        const requestArr = (component as any).RequestSingleTemplateDropDownArr;
        expect(requestArr.length).toBe(4);
        expect(requestArr).toEqual(['name1', 'name2', 'name3', 'name4']);
        done();
      }, 100);
    });

    it('should show snackbar with correct styling on error', (done) => {
      const mockErrorBody = { detail: 'Error occurred' };
      spyOn(component['_snackBar'], 'open');

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockErrorBody, { status: 500, statusText: 'Error' });

      setTimeout(() => {
        expect(component['_snackBar'].open).toHaveBeenCalledWith(
          'Error occurred',
          'Close',
          { duration: 3000, panelClass: ['le-u-bg-black'] }
        );
        done();
      }, 100);
    });

    it('should log console message before making HTTP request', () => {
      spyOn(console, 'log');
      
      component.getTemplateDetailSingle();

      expect(console.log).toHaveBeenCalledWith('inside getTemplateDetail single');
      
      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush({ templates: [] });
    });

    it('should handle template objects with additional properties', (done) => {
      const mockResponse = {
        templates: [
          { templateName: 'template1', id: '1', additionalProp: 'value1' },
          { templateName: 'template2', id: '2', additionalProp: 'value2' }
        ]
      };

      component.getTemplateDetailSingle();

      const req = httpMock.expectOne((request: any) => 
        request.url.includes('test-user-123')
      );
      req.flush(mockResponse);

      setTimeout(() => {
        // Should only extract templateName, not other properties
        expect((component as any).RequestSingleTemplateDropDownArr).toEqual(['template1', 'template2']);
        expect((component as any).RequestSingleTemplateDropDownArr).not.toContain('value1');
        done();
      }, 100);
    });
  });

  describe('test Method - Popover Toggle', () => {
    let mockPopover: any;

    beforeEach(() => {
      mockPopover = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      
      (component as any).p = mockPopover;
      (component as any).p2 = mockPopover;
      (component as any).p3 = mockPopover;
      (component as any).p4 = mockPopover;
      (component as any).p5 = mockPopover;
      (component as any).p6 = mockPopover;
    });

    it('should log subcategory when test is called', () => {
      spyOn(console, 'log');
      
      component.test('Model');

      expect(console.log).toHaveBeenCalledWith('Subcategory:', 'Model');
    });

    it('should toggle p popover when subcategory is Model', () => {
      component.test('Model');

      expect(mockPopover.isOpen).toHaveBeenCalled();
      expect(mockPopover.toggle).toHaveBeenCalled();
    });

    it('should toggle p2 popover when subcategory is Template', () => {
      const mockP2 = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      (component as any).p2 = mockP2;
      
      component.test('Template');

      expect(mockP2.isOpen).toHaveBeenCalled();
      expect(mockP2.toggle).toHaveBeenCalled();
    });

    it('should toggle p3 popover when subcategory is TextTemplate', () => {
      const mockP3 = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      (component as any).p3 = mockP3;
      
      component.test('TextTemplate');

      expect(mockP3.isOpen).toHaveBeenCalled();
      expect(mockP3.toggle).toHaveBeenCalled();
    });

    it('should toggle p4 popover when subcategory is TextModel', () => {
      const mockP4 = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      (component as any).p4 = mockP4;
      
      component.test('TextModel');

      expect(mockP4.isOpen).toHaveBeenCalled();
      expect(mockP4.toggle).toHaveBeenCalled();
    });

    it('should toggle p5 popover when subcategory is ImageTemplate', () => {
      const mockP5 = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      (component as any).p5 = mockP5;
      
      component.test('ImageTemplate');

      expect(mockP5.isOpen).toHaveBeenCalled();
      expect(mockP5.toggle).toHaveBeenCalled();
    });

    it('should toggle p6 popover when subcategory is ImageModel', () => {
      const mockP6 = {
        isOpen: jasmine.createSpy('isOpen').and.returnValue(false),
        toggle: jasmine.createSpy('toggle')
      };
      (component as any).p6 = mockP6;
      
      component.test('ImageModel');

      expect(mockP6.isOpen).toHaveBeenCalled();
      expect(mockP6.toggle).toHaveBeenCalled();
    });

    it('should log Unknown subcategory for unrecognized subcategory', () => {
      spyOn(console, 'log');
      
      component.test('InvalidSubcategory');

      expect(console.log).toHaveBeenCalledWith('Unknown subcategory');
    });

    it('should not toggle any popover for unknown subcategory', () => {
      component.test('UnknownType');

      // mockPopover should not be called for unknown subcategory
      expect(mockPopover.toggle).not.toHaveBeenCalled();
    });

    it('should call togglePopover with correct popover for each subcategory', () => {
      spyOn<any>(component, 'togglePopover');
      
      component.test('Model');
      expect(component['togglePopover']).toHaveBeenCalledWith((component as any).p);
    });

    it('should handle null or undefined subcategory', () => {
      spyOn(console, 'log');
      
      component.test(null as any);

      expect(console.log).toHaveBeenCalledWith('Unknown subcategory');
    });
  });

  describe('togglePopover Method', () => {
    let mockPopover: any;

    beforeEach(() => {
      mockPopover = {
        isOpen: jasmine.createSpy('isOpen'),
        toggle: jasmine.createSpy('toggle')
      };
    });

    it('should log Popover when togglePopover is called', () => {
      spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      expect(console.log).toHaveBeenCalledWith('Popover:', mockPopover);
    });

    it('should toggle and log when popover is open', () => {
      spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(true);
      
      component['togglePopover'](mockPopover);

      expect(mockPopover.isOpen).toHaveBeenCalled();
      expect(console.log).toHaveBeenCalledWith('Popover is open');
      expect(mockPopover.toggle).toHaveBeenCalled();
    });

    it('should toggle and log when popover is closed', () => {
      spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      expect(mockPopover.isOpen).toHaveBeenCalled();
      expect(mockPopover.toggle).toHaveBeenCalled();
      expect(console.log).toHaveBeenCalledWith('Popover is closed');
    });

    it('should call isOpen before toggle', () => {
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      expect(mockPopover.isOpen).toHaveBeenCalledBefore(mockPopover.toggle);
    });

    it('should always call toggle regardless of popover state', () => {
      mockPopover.isOpen.and.returnValue(true);
      component['togglePopover'](mockPopover);
      expect(mockPopover.toggle).toHaveBeenCalledTimes(1);

      mockPopover.toggle.calls.reset();
      mockPopover.isOpen.and.returnValue(false);
      component['togglePopover'](mockPopover);
      expect(mockPopover.toggle).toHaveBeenCalledTimes(1);
    });

    it('should check if popover is open before toggling', () => {
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      expect(mockPopover.isOpen).toHaveBeenCalled();
    });

    it('should log correct message for open state', () => {
      const consoleSpy = spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(true);
      
      component['togglePopover'](mockPopover);

      expect(consoleSpy).toHaveBeenCalledWith('Popover is open');
      expect(consoleSpy).not.toHaveBeenCalledWith('Popover is closed');
    });

    it('should log correct message for closed state', () => {
      const consoleSpy = spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      expect(consoleSpy).toHaveBeenCalledWith('Popover is closed');
      expect(consoleSpy).not.toHaveBeenCalledWith('Popover is open');
    });

    it('should handle multiple toggle calls', () => {
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);
      component['togglePopover'](mockPopover);

      expect(mockPopover.toggle).toHaveBeenCalledTimes(2);
    });

    it('should log console messages in correct order for open state', () => {
      const consoleSpy = spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(true);
      
      component['togglePopover'](mockPopover);

      const calls = consoleSpy.calls.all();
      expect(calls[0].args[0]).toBe('Popover:');
      expect(calls[1].args[0]).toBe('Popover is open');
    });

    it('should log console messages in correct order for closed state', () => {
      const consoleSpy = spyOn(console, 'log');
      mockPopover.isOpen.and.returnValue(false);
      
      component['togglePopover'](mockPopover);

      const calls = consoleSpy.calls.all();
      expect(calls[0].args[0]).toBe('Popover:');
      expect(calls[1].args[0]).toBe('Popover is closed');
    });
  });

  describe('clickDeleteValue Method', () => {
    beforeEach(() => {
      component.data = { id: 'test-id', account: 'test-account', portfolio: 'test-portfolio' };
      (component as any).userId = 'test-user-123';
      (component as any).template_admin_delete_selected_removeTempMap = 'http://test.com/api/delete-template';
      spyOn(component, 'getslectedDropdownvalues').and.stub();
    });

    it('should call delete API with correct parameters', () => {
      spyOn(component['https'], 'delete').and.returnValue({ subscribe: jasmine.createSpy('subscribe') } as any);
      
      component.clickDeleteValue('SingleModel', 'Template', 'request', 'template-name-1');

      expect(component['https'].delete).toHaveBeenCalled();
    });

    it('should include userId in request body', () => {
      let capturedBody: any;
      spyOn(component['https'], 'delete').and.callFake((url: string, options: any) => {
        capturedBody = options.body;
        return { subscribe: () => {} } as any;
      });

      component.clickDeleteValue('SingleModel', 'Model', 'request', 'template-x');

      expect(capturedBody.userId).toBe('test-user-123');
    });

    it('should include portfolio and account in request body', () => {
      let capturedBody: any;
      spyOn(component['https'], 'delete').and.callFake((url: string, options: any) => {
        capturedBody = options.body;
        return { subscribe: () => {} } as any;
      });

      component.clickDeleteValue('SingleModel', 'Model', 'request', 'template-y');

      expect(capturedBody.portfolio).toBe('test-portfolio');
      expect(capturedBody.account).toBe('test-account');
    });

    it('should pass category and subcategory to request body', () => {
      let capturedBody: any;
      spyOn(component['https'], 'delete').and.callFake((url: string, options: any) => {
        capturedBody = options.body;
        return { subscribe: () => {} } as any;
      });

      component.clickDeleteValue('TestCategory', 'TestSubcategory', 'request', 'template-1');

      expect(capturedBody.category).toBe('TestCategory');
      expect(capturedBody.subcategory).toBe('TestSubcategory');
    });

    it('should pass type as tempType and value as templateName', () => {
      let capturedBody: any;
      spyOn(component['https'], 'delete').and.callFake((url: string, options: any) => {
        capturedBody = options.body;
        return { subscribe: () => {} } as any;
      });

      component.clickDeleteValue('Category', 'Subcategory', 'comparison', 'my-template');

      expect(capturedBody.tempType).toBe('comparison');
      expect(capturedBody.templateName).toBe('my-template');
    });
  });

  describe('toggleAllSelection3 Method', () => {
    let mockSelect: any;
    let mockOptions: any[];

    beforeEach(() => {
      mockOptions = [
        { value: 'option1', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), selected: false },
        { value: 'option2', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), selected: false },
        { value: 'option3', select: jasmine.createSpy('select'), deselect: jasmine.createSpy('deselect'), selected: false }
      ];

      mockSelect = {
        options: { forEach: (callback: any) => mockOptions.forEach(callback) },
        close: jasmine.createSpy('close')
      };

      (component as any).select3 = mockSelect;
      (component as any).listShowlist3 = new Set();
      (component as any).allSelected3 = false;
    });

    it('should toggle allSelected3 flag', () => {
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).allSelected3).toBe(true);
    });

    it('should store event and checked status', () => {
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).event3).toEqual(mockEvent);
      expect((component as any).c3).toBe(true);
    });

    it('should select all options when checked is true', () => {
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      mockOptions.forEach(option => {
        expect(option.select).toHaveBeenCalled();
      });
    });

    it('should add all values to listShowlist3 when checked is true', () => {
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).listShowlist3.has('option1')).toBe(true);
      expect((component as any).listShowlist3.has('option2')).toBe(true);
      expect((component as any).listShowlist3.has('option3')).toBe(true);
    });

    it('should close select3 dropdown when checked is true', () => {
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect(mockSelect.close).toHaveBeenCalled();
    });

    it('should hide listbox element when checked is true', () => {
      const mockElement = document.createElement('div');
      mockElement.setAttribute('role', 'listbox');
      document.body.appendChild(mockElement);
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect(mockElement.style.display).toBe('none');
      document.body.removeChild(mockElement);
    });

    it('should deselect all options when checked is false', () => {
      (component as any).allSelected3 = true;
      const mockEvent = { checked: false };
      
      component.toggleAllSelection3(mockEvent);

      mockOptions.forEach(option => {
        expect(option.deselect).toHaveBeenCalled();
      });
    });

    it('should remove all values from listShowlist3 when checked is false', () => {
      (component as any).listShowlist3.add('option1');
      (component as any).listShowlist3.add('option2');
      (component as any).allSelected3 = true;
      const mockEvent = { checked: false };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).listShowlist3.has('option1')).toBe(false);
      expect((component as any).listShowlist3.has('option2')).toBe(false);
    });

    it('should handle toggle from false to true', () => {
      expect((component as any).allSelected3).toBe(false);
      const mockEvent = { checked: true };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).allSelected3).toBe(true);
    });

    it('should handle toggle from true to false', () => {
      (component as any).allSelected3 = true;
      expect((component as any).allSelected3).toBe(true);
      const mockEvent = { checked: false };
      
      component.toggleAllSelection3(mockEvent);

      expect((component as any).allSelected3).toBe(false);
    });
  });

  describe('selectRecognizertype3 Method', () => {
    let mockSelect: any;
    let mockOptions: any[];

    beforeEach(() => {
      mockOptions = [
        { value: 'option1', selected: true },
        { value: 'option2', selected: true },
        { value: 'option3', selected: true }
      ];

      mockSelect = {
        options: { forEach: (callback: any) => mockOptions.forEach(callback) }
      };

      (component as any).select3 = mockSelect;
      (component as any).listShowlist3 = new Set();
      (component as any).allSelected3 = false;
      (component as any).allSelectedInput3 = false;
    });

    it('should set allSelectedInput3 to true when all options are selected', () => {
      component.selectRecognizertype3();

      expect((component as any).allSelectedInput3).toBe(true);
    });

    it('should add all selected values to listShowlist3', () => {
      component.selectRecognizertype3();

      expect((component as any).listShowlist3.has('option1')).toBe(true);
      expect((component as any).listShowlist3.has('option2')).toBe(true);
      expect((component as any).listShowlist3.has('option3')).toBe(true);
    });

    it('should set allSelectedInput3 to false when not all options are selected', () => {
      mockOptions[1].selected = false;

      component.selectRecognizertype3();

      expect((component as any).allSelectedInput3).toBe(false);
    });

    it('should set allSelected3 to false when not all options are selected', () => {
      mockOptions[0].selected = false;

      component.selectRecognizertype3();

      expect((component as any).allSelected3).toBe(false);
    });

    it('should delete unselected values from listShowlist3', () => {
      (component as any).listShowlist3.add('option1');
      (component as any).listShowlist3.add('option2');
      mockOptions[1].selected = false;

      component.selectRecognizertype3();

      expect((component as any).listShowlist3.has('option1')).toBe(true);
      expect((component as any).listShowlist3.has('option2')).toBe(false);
    });

    it('should handle all options unselected', () => {
      mockOptions.forEach(opt => opt.selected = false);

      component.selectRecognizertype3();

      expect((component as any).allSelectedInput3).toBe(false);
      expect((component as any).allSelected3).toBe(false);
      expect((component as any).listShowlist3.size).toBe(0);
    });

    it('should handle mixed selection state', () => {
      mockOptions[0].selected = true;
      mockOptions[1].selected = false;
      mockOptions[2].selected = true;

      component.selectRecognizertype3();

      expect((component as any).allSelectedInput3).toBe(false);
      expect((component as any).listShowlist3.has('option1')).toBe(true);
      expect((component as any).listShowlist3.has('option2')).toBe(false);
      expect((component as any).listShowlist3.has('option3')).toBe(true);
    });
  });

  describe('submit Method', () => {
    beforeEach(() => {
      (component as any).mapId = 'test-map-id-123';
      (component as any).userId = 'test-user-456';
      
      component.templetUpdateFrom = jasmine.createSpyObj('FormGroup', ['get']);
      (component.templetUpdateFrom.get as jasmine.Spy).and.callFake((key: string) => {
        const values: any = {
          'requestTemplate': { value: ['req-template-1', 'req-template-2'] },
          'responseTemplate': { value: ['res-template-1'] },
          'comparisonTemplate': { value: ['comp-template-1', 'comp-template-2'] }
        };
        return values[key];
      });

      spyOn(component, 'patchtemplatet');
      spyOn(console, 'log');
    });

    it('should log payload before calling patchtemplatet', () => {
      component.submit();

      expect(console.log).toHaveBeenCalledWith('payload===', jasmine.any(Object));
    });

    it('should create payload with mapId', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({ mapId: 'test-map-id-123' })
      );
    });

    it('should create payload with userId', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({ userId: 'test-user-456' })
      );
    });

    it('should create payload with requestTemplate from form', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          requestTemplate: ['req-template-1', 'req-template-2']
        })
      );
    });

    it('should create payload with responseTemplate from form', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          responseTemplate: ['res-template-1']
        })
      );
    });

    it('should create payload with comparisonTemplate from form', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith(
        jasmine.objectContaining({
          comparisonTemplate: ['comp-template-1', 'comp-template-2']
        })
      );
    });

    it('should call patchtemplatet with complete payload', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith({
        mapId: 'test-map-id-123',
        userId: 'test-user-456',
        requestTemplate: ['req-template-1', 'req-template-2'],
        responseTemplate: ['res-template-1'],
        comparisonTemplate: ['comp-template-1', 'comp-template-2']
      });
    });

    it('should call patchtemplatet exactly once', () => {
      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledTimes(1);
    });

    it('should handle empty template arrays', () => {
      (component.templetUpdateFrom.get as jasmine.Spy).and.callFake((key: string) => {
        const values: any = {
          'requestTemplate': { value: [] },
          'responseTemplate': { value: [] },
          'comparisonTemplate': { value: [] }
        };
        return values[key];
      });

      component.submit();

      expect(component.patchtemplatet).toHaveBeenCalledWith({
        mapId: 'test-map-id-123',
        userId: 'test-user-456',
        requestTemplate: [],
        responseTemplate: [],
        comparisonTemplate: []
      });
    });

    it('should get form values using correct keys', () => {
      component.submit();

      expect(component.templetUpdateFrom.get).toHaveBeenCalledWith('requestTemplate');
      expect(component.templetUpdateFrom.get).toHaveBeenCalledWith('responseTemplate');
      expect(component.templetUpdateFrom.get).toHaveBeenCalledWith('comparisonTemplate');
    });
  });

  describe('patchtemplatet Method', () => {
    beforeEach(() => {
      (component as any).template_admin_update_addTempMap = 'http://test.com/api/update-template';
      spyOn(component, 'getslectedDropdownvalues').and.stub();
    });

    it('should call PATCH API with correct URL and payload', () => {
      const mockPayload = {
        mapId: 'map-123',
        userId: 'user-456',
        requestTemplate: ['req1', 'req2'],
        responseTemplate: ['res1'],
        comparisonTemplate: ['comp1']
      };
      
      spyOn(component['https'], 'patch').and.returnValue({ subscribe: () => {} } as any);

      component.patchtemplatet(mockPayload);

      expect(component['https'].patch).toHaveBeenCalledWith(
        'http://test.com/api/update-template',
        mockPayload,
        jasmine.objectContaining({ headers: jasmine.any(Object) })
      );
    });

    it('should set correct headers for PATCH request', () => {
      const mockPayload = { userId: 'test-user' };
      let capturedHeaders: any;
      
      spyOn(component['https'], 'patch').and.callFake((url: string, payload: any, options: any) => {
        capturedHeaders = options.headers;
        return { subscribe: () => {} } as any;
      });

      component.patchtemplatet(mockPayload);

      expect(capturedHeaders.get('Content-Type')).toBe('application/json');
    });

    it('should log response on successful update', () => {
      const mockResponse = { success: true, id: '123' };
      spyOn(console, 'log');
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(console.log).toHaveBeenCalledWith('res===', mockResponse);
    });

    it('should call getslectedDropdownvalues after successful update', () => {
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any) => success({ success: true })
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component.getslectedDropdownvalues).toHaveBeenCalled();
    });

    it('should show success snackbar after successful update', () => {
      spyOn(component['_snackBar'], 'open');
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any) => success({ success: true })
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'Template Updated Successfully',
        'Close',
        jasmine.objectContaining({ duration: 3000, panelClass: ['le-u-bg-black'] })
      );
    });

    it('should log error on failed update', () => {
      const mockError = { error: { detail: 'Update failed' } };
      spyOn(console, 'log');
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(console.log).toHaveBeenCalledWith(mockError);
    });

    it('should show error snackbar with error.detail message', () => {
      const mockError = { error: { detail: 'Custom error detail' } };
      spyOn(component['_snackBar'], 'open');
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'Custom error detail',
        'Close',
        jasmine.objectContaining({ duration: 3000, panelClass: ['le-u-bg-black'] })
      );
    });

    it('should show error snackbar with error.message when detail not available', () => {
      const mockError = { error: { message: 'Custom error message' } };
      spyOn(component['_snackBar'], 'open');
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'Custom error message',
        'Close',
        jasmine.any(Object)
      );
    });

    it('should show default error message when error details not available', () => {
      const mockError = { error: {} };
      spyOn(component['_snackBar'], 'open');
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    });

    it('should not call getslectedDropdownvalues on error', () => {
      const mockError = { error: { detail: 'Error occurred' } };
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'patch').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.patchtemplatet({ userId: 'test' });

      expect(component.getslectedDropdownvalues).not.toHaveBeenCalled();
    });
  });

  describe('getTemplateDetail Method', () => {
    beforeEach(() => {
      (component as any).customTemplateGetUrl = 'http://test.com/api/template/';
      (component as any).userId = 'test-user-789';
      (component as any).tempalteArray = [];
      (component as any).masterTemplateArr = ['master-template-1', 'master-template-2'];
    });

    it('should call GET API with correct URL', () => {
      spyOn(component['https'], 'get').and.returnValue({ subscribe: () => {} } as any);

      component.getTemplateDetail();

      expect(component['https'].get).toHaveBeenCalledWith('http://test.com/api/template/test-user-789');
    });

    it('should store response in result property', () => {
      const mockResponse = {
        templates: [
          { templateName: 'template1' },
          { templateName: 'template2' }
        ]
      };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect(component.result).toEqual(mockResponse);
    });

    it('should log the result', () => {
      const mockResponse = { templates: [{ templateName: 'test' }] };
      spyOn(console, 'log');
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect(console.log).toHaveBeenCalledWith('this.result===', mockResponse);
    });

    it('should populate dataSource_getBatches with templates', () => {
      const mockTemplates = [
        { templateName: 'template1', id: '1' },
        { templateName: 'template2', id: '2' }
      ];
      const mockResponse = { templates: mockTemplates };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect((component as any).dataSource_getBatches).toEqual(mockTemplates);
    });

    it('should extract template names into tempalteArray', () => {
      const mockResponse = {
        templates: [
          { templateName: 'template-A' },
          { templateName: 'template-B' },
          { templateName: 'template-C' }
        ]
      };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect((component as any).tempalteArray).toContain('template-A');
      expect((component as any).tempalteArray).toContain('template-B');
      expect((component as any).tempalteArray).toContain('template-C');
    });

    it('should set comparsionDropDownArr to tempalteArray', () => {
      const mockResponse = {
        templates: [
          { templateName: 'template1' },
          { templateName: 'template2' }
        ]
      };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect((component as any).comparsionDropDownArr).toEqual(['template1', 'template2']);
    });

    it('should concatenate masterTemplateArr with tempalteArray', () => {
      const mockResponse = {
        templates: [
          { templateName: 'user-template-1' },
          { templateName: 'user-template-2' }
        ]
      };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      const expectedArray = ['master-template-1', 'master-template-2', 'user-template-1', 'user-template-2'];
      expect((component as any).tempalteArray).toEqual(expectedArray);
    });

    it('should log masterTemplateArr and final tempalteArray', () => {
      const mockResponse = { templates: [{ templateName: 'test' }] };
      spyOn(console, 'log');
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect(console.log).toHaveBeenCalledWith('this.masterTemplateArr===', jasmine.any(Array));
      expect(console.log).toHaveBeenCalledWith('this.tempalteArray===', jasmine.any(Array));
    });

    it('should handle empty templates array', () => {
      const mockResponse = { templates: [] };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect((component as any).tempalteArray).toEqual(['master-template-1', 'master-template-2']);
    });

    it('should log error on failed request', () => {
      const mockError = { error: { detail: 'Failed to fetch' } };
      spyOn(console, 'log');
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.getTemplateDetail();

      expect(console.log).toHaveBeenCalledWith(mockError);
    });

    it('should show error snackbar with error.detail on failure', () => {
      const mockError = { error: { detail: 'Template fetch failed' } };
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.getTemplateDetail();

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'Template fetch failed',
        'Close',
        jasmine.objectContaining({ duration: 3000, panelClass: ['le-u-bg-black'] })
      );
    });

    it('should show error snackbar with error.message when detail not available', () => {
      const mockError = { error: { message: 'Network error' } };
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.getTemplateDetail();

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'Network error',
        'Close',
        jasmine.any(Object)
      );
    });

    it('should show default error message when error details not available', () => {
      const mockError = { error: {} };
      spyOn(component['_snackBar'], 'open').and.stub();
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any, error: any) => error(mockError)
      } as any);

      component.getTemplateDetail();

      expect(component['_snackBar'].open).toHaveBeenCalledWith(
        'The Api has failed',
        'Close',
        jasmine.any(Object)
      );
    });

    it('should process each template in the loop', () => {
      const mockResponse = {
        templates: [
          { templateName: 'template1', id: '1' },
          { templateName: 'template2', id: '2' },
          { templateName: 'template3', id: '3' }
        ]
      };
      
      spyOn(component['https'], 'get').and.returnValue({
        subscribe: (success: any) => success(mockResponse)
      } as any);

      component.getTemplateDetail();

      expect((component as any).tempalteArray.length).toBe(5); // 2 master + 3 user templates
    });
  });
});
