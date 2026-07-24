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

import { AccCreatePmModalComponent } from './acc-create-pm-modal.component';

describe('AccCreatePmModalComponent', () => {
  let component: AccCreatePmModalComponent;
  let fixture: ComponentFixture<AccCreatePmModalComponent>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<AccCreatePmModalComponent>>;

  beforeEach(async () => {
    const mockResult = { 
      result: {
        Response: [{ length: 0 }],
        Admin: 'http://test.com',
        getAccountDetail: '/api/accounts'
      }
    };
    localStorage.setItem('res', JSON.stringify(mockResult));
    
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    
    await TestBed.configureTestingModule({
      declarations: [ AccCreatePmModalComponent ],
      imports: [ MatSnackBarModule, HttpClientTestingModule ],
      providers: [
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { x: { portfolio: 'TestPortfolio', account: 'TestAccount' } } }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    dialogRef = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<AccCreatePmModalComponent>>;
    fixture = TestBed.createComponent(AccCreatePmModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default tab as "acc"', () => {
    expect(component.tab).toBe('acc');
  });

  it('should toggle tabs when toggleTabs is called', () => {
    component.toggleTabs('privacy');
    expect(component.tab).toBe('privacy');
    
    component.toggleTabs('safety');
    expect(component.tab).toBe('safety');
  });

  it('should close dialog when closeDialog is called', () => {
    component.closeDialog();
    expect(dialogRef.close).toHaveBeenCalled();
  });

  it('should log data on ngOnInit', () => {
    spyOn(console, 'log');
    component.ngOnInit();
    expect(console.log).toHaveBeenCalledWith('data', 'TestPortfolio');
    expect(console.log).toHaveBeenCalledWith('datax', 'TestPortfolio');
  });
});
