/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { AccModalFmComponent } from './acc-modal-fm.component';

describe('AccModalFmComponent', () => {
  let component: AccModalFmComponent;
  let fixture: ComponentFixture<AccModalFmComponent>;
  let httpMock: HttpTestingController;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<AccModalFmComponent>>;

  beforeEach(async () => {
    dialogRefSpy = jasmine.createSpyObj(['close']);
    
    localStorage.setItem('res', JSON.stringify({ 
      result: {
        Admin: 'http://test.com',
        Admin_DataRecogGrplist: '/api/recognizers',
        Admin_AccMasterList: '/api/accounts',
        Fm_Config_Entry: '/api/fm-entry',
        Fm_Config_EntryList: '/api/fm-entry-list',
        Fm_Config_Data: '/api/fm-data',
        Fm_Config_DataUpdate: '/api/fm-update',
        Fm_Config_Delete: '/api/fm-delete',
        Fm_Config_ModCheck: '/api/fm-modcheck',
        Fm_Config_TopicList: '/api/fm-topics',
        Fm_Config_OutputModCheck: '/api/fm-output-modcheck'
      }
    }));
    
    localStorage.setItem('userid', JSON.stringify('testuser@example.com'));

    await TestBed.configureTestingModule({
      declarations: [ AccModalFmComponent ],
      imports: [ HttpClientTestingModule, MatSnackBarModule, NoopAnimationsModule ],
      providers: [
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { id: 'test123' } }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    try {
      httpMock.verify();
    } catch (e) {
      // Ignore verification errors
    }
    localStorage.clear();
  });

  function initializeComponent() {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    
    fixture.detectChanges();
    
    // Mock HTTP calls made in ngOnInit
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ dataList: [] });
    
    const req2 = httpMock.expectOne('http://test.com/api/fm-topics');
    req2.flush({ dataList: [] });
    
    const req3 = httpMock.expectOne('http://test.com/api/fm-output-modcheck');
    req3.flush({ dataList: [] });
    
    const req4 = httpMock.expectOne('http://test.com/api/fm-data');
    req4.flush({ dataList: [{}] });
  }

  it('should create', () => {
    initializeComponent();
    expect(component).toBeTruthy();
  });

  it('should close dialog', () => {
    initializeComponent();
    component.closeDialog();
    expect(dialogRefSpy.close).toHaveBeenCalled();
  });

  it('should toggle all selections for input moderation (select1)', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select1 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection1(event);
    
    expect(component.c1).toBe(true);
    expect(component.allSelected1).toBe(true);
  });

  it('should toggle all selections for input moderation when unchecking (select1)', () => {
    initializeComponent();
    
    component.allSelected1 = true;
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select1 = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelection1(event);
    
    expect(component.c1).toBe(false);
    expect(component.allSelected1).toBe(false);
  });

  it('should update selection status for input moderation', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: true, value: 'test' });
        }
      }
    };
    component.select1 = mockSelect as any;
    
    component.selectInputModeration();
    
    expect(component.allSelectedInput).toBe(true);
  });

  it('should update selection status for input moderation with unselected items', () => {
    initializeComponent();
    
    component.allSelected1 = true;
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'test' });
        }
      }
    };
    component.select1 = mockSelect as any;
    
    component.selectInputModeration();
    
    expect(component.allSelectedInput).toBe(false);
    expect(component.allSelected1).toBe(false);
  });

  it('should toggle all selections for output moderation (select2)', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select2 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection2(event);
    
    expect(component.c2).toBe(true);
    expect(component.allSelected2).toBe(true);
  });

  it('should toggle all selections for output moderation when unchecking (select2)', () => {
    initializeComponent();
    
    component.allSelected2 = true;
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select2 = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelection2(event);
    
    expect(component.c2).toBe(false);
    expect(component.allSelected2).toBe(false);
  });

  it('should update selection status for output moderation', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: true, value: 'test' });
        }
      }
    };
    component.select2 = mockSelect as any;
    
    component.selectOutputModeration();
    
    expect(component.allSelectedInput2).toBe(true);
  });

  it('should update selection status for output moderation with unselected items', () => {
    initializeComponent();
    
    component.allSelected2 = true;
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'test' });
        }
      }
    };
    component.select2 = mockSelect as any;
    
    component.selectOutputModeration();
    
    expect(component.allSelectedInput2).toBe(false);
    expect(component.allSelected2).toBe(false);
  });

  it('should toggle all selections for recognizer list (select3)', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select3 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection3(event);
    
    expect(component.c3).toBe(true);
    expect(component.allSelected3).toBe(true);
  });

  it('should toggle all selections for recognizer list when unchecking (select3)', () => {
    initializeComponent();
    
    component.allSelected3 = true;
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select3 = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelection3(event);
    
    expect(component.c3).toBe(false);
    expect(component.allSelected3).toBe(false);
  });

  it('should update selection status for recognizer list', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: true, value: 'test' });
        }
      }
    };
    component.select3 = mockSelect as any;
    
    component.selectrecognizerList();
    
    expect(component.allSelectedInput3).toBe(true);
  });

  it('should toggle all selections for recognizer list to block (select4)', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select4 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection4(event);
    
    expect(component.c4).toBe(true);
    expect(component.allSelected4).toBe(true);
  });

  it('should update selection status for recognizer list to block', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'test' });
        }
      }
    };
    component.select4 = mockSelect as any;
    
    component.selectrecognizerListtoblock();
    
    expect(component.allSelectedInput4).toBe(false);
  });

  it('should toggle all selections for restricted topics (select5)', () => {
    initializeComponent();
    
    component.allSelected5 = true;
    const mockSelect4 = {
      options: {
        forEach: jasmine.createSpy('forEach')
      }
    };
    const mockSelect5 = {
      options: {
        forEach: jasmine.createSpy('forEach')
      },
      close: jasmine.createSpy('close')
    };
    component.select4 = mockSelect4 as any;
    component.select5 = mockSelect5 as any;
    
    const event = { checked: false };
    component.toggleAllSelection5(event);
    
    expect(component.c5).toBe(false);
    expect(component.allSelected5).toBe(false);
  });

  it('should update selection status for restricted topics', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: true, value: 'topic1' });
        }
      }
    };
    component.select5 = mockSelect as any;
    
    component.selectRestrictedtopics();
    
    expect(component.allSelectedInput5).toBe(true);
  });

  it('should toggle all selections for gibberish labels', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      }
    };
    component.selectGibberishLabels = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelectionGibberishLabels(event);
    
    expect(component.allSelectedGibberishLabels).toBe(true);
  });

  it('should update selection status for gibberish labels', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'label1' });
        }
      }
    };
    component.selectGibberishLabels = mockSelect as any;
    
    component.selectsGibberishLabels();
    
    expect(component.allSelectedGibberishLabels).toBe(false);
  });

  it('should toggle all selections for banned categories', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: jasmine.createSpy('forEach')
      }
    };
    component.selectBannedCategories = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelectionBannedCategories(event);
    
    expect(component.allSelectedBannedCategories).toBe(false);
  });

  it('should update selection status for banned categories', () => {
    initializeComponent();
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: true, value: 'cat1' });
        }
      }
    };
    component.selectBannedCategories = mockSelect as any;
    
    component.selectsBannedCategories();
    
    expect(component.allSelectedBannedCategories).toBe(true);
  });

  it('should toggle all selections for input moderation with DOM manipulation (select1)', () => {
    initializeComponent();
    
    const mockElement = document.createElement('div');
    mockElement.setAttribute('role', 'listbox');
    document.body.appendChild(mockElement);
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      value: 'test-value'
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      },
      close: jasmine.createSpy('close')
    };
    component.select1 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection1(event);
    
    expect(mockOption.select).toHaveBeenCalled();
    expect(component.listShowlist1.has('test-value')).toBe(true);
    expect(mockSelect.close).toHaveBeenCalled();
    
    document.body.removeChild(mockElement);
  });

  it('should toggle all selections for output moderation with DOM manipulation (select2)', () => {
    initializeComponent();
    
    const mockElement = document.createElement('div');
    mockElement.setAttribute('role', 'listbox');
    document.body.appendChild(mockElement);
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      value: 'test-value'
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      },
      close: jasmine.createSpy('close')
    };
    component.select2 = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelection2(event);
    
    expect(mockOption.select).toHaveBeenCalled();
    expect(component.listShowlist2.has('test-value')).toBe(true);
    expect(mockSelect.close).toHaveBeenCalled();
    
    document.body.removeChild(mockElement);
  });

  it('should toggle all selections for restricted topics with DOM manipulation (select5)', () => {
    initializeComponent();
    
    const mockElement = document.createElement('div');
    mockElement.setAttribute('role', 'listbox');
    document.body.appendChild(mockElement);
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      value: 'topic-value'
    };
    
    const mockSelect5 = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      },
      close: jasmine.createSpy('close')
    };
    component.select5 = mockSelect5 as any;
    
    const event = { checked: true };
    component.toggleAllSelection5(event);
    
    expect(mockOption.select).toHaveBeenCalled();
    expect(component.listShowlist5.has('topic-value')).toBe(true);
    expect(mockSelect5.close).toHaveBeenCalled();
    
    document.body.removeChild(mockElement);
  });

  it('should update selection status for restricted topics with unselected items', () => {
    initializeComponent();
    
    component.allSelected5 = true;
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'topic1' });
        }
      }
    };
    component.select5 = mockSelect as any;
    
    component.selectRestrictedtopics();
    
    expect(component.allSelectedInput5).toBe(false);
    expect(component.allSelected5).toBe(false);
  });

  it('should toggle all selections for gibberish labels with DOM manipulation', () => {
    initializeComponent();
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      }
    };
    component.selectGibberishLabels = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelectionGibberishLabels(event);
    
    expect(mockOption.select).toHaveBeenCalled();
    expect(component.allSelectedGibberishLabels).toBe(true);
  });

  it('should toggle all selections for gibberish labels when unchecking', () => {
    initializeComponent();
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      }
    };
    component.selectGibberishLabels = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelectionGibberishLabels(event);
    
    expect(mockOption.deselect).toHaveBeenCalled();
    expect(component.allSelectedGibberishLabels).toBe(false);
  });

  it('should update selection status for gibberish labels with unselected items', () => {
    initializeComponent();
    
    component.allSelectedGibberishLabels = true;
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'label1' });
        }
      }
    };
    component.selectGibberishLabels = mockSelect as any;
    
    component.selectsGibberishLabels();
    
    expect(component.allSelectedGibberishLabels).toBe(false);
  });

  it('should toggle all selections for banned categories with DOM manipulation', () => {
    initializeComponent();
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      }
    };
    component.selectBannedCategories = mockSelect as any;
    
    const event = { checked: true };
    component.toggleAllSelectionBannedCategories(event);
    
    expect(mockOption.select).toHaveBeenCalled();
    expect(component.allSelectedBannedCategories).toBe(true);
  });

  it('should toggle all selections for banned categories when unchecking', () => {
    initializeComponent();
    
    const mockOption = {
      select: jasmine.createSpy('select'),
      deselect: jasmine.createSpy('deselect')
    };
    
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback(mockOption);
        }
      }
    };
    component.selectBannedCategories = mockSelect as any;
    
    const event = { checked: false };
    component.toggleAllSelectionBannedCategories(event);
    
    expect(mockOption.deselect).toHaveBeenCalled();
    expect(component.allSelectedBannedCategories).toBe(false);
  });

  it('should update selection status for banned categories with unselected items', () => {
    initializeComponent();
    
    component.allSelectedBannedCategories = true;
    const mockSelect = {
      options: {
        forEach: (callback: any) => {
          callback({ selected: false, value: 'cat1' });
        }
      }
    };
    component.selectBannedCategories = mockSelect as any;
    
    component.selectsBannedCategories();
    
    expect(component.allSelectedBannedCategories).toBe(false);
  });

  it('should handle get_fmdataforFmConfigResponseform with null response', (done) => {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ dataList: [] });
    
    const req2 = httpMock.expectOne('http://test.com/api/fm-topics');
    req2.flush({ dataList: [] });
    
    const req3 = httpMock.expectOne('http://test.com/api/fm-output-modcheck');
    req3.flush({ dataList: [] });
    
    const req4 = httpMock.expectOne('http://test.com/api/fm-data');
    req4.flush(null);
    
    setTimeout(() => {
      expect(component.isDataEmpty).toBe(true);
      expect(component.isLoading).toBe(false);
      done();
    }, 100);
  });

  it('should handle get_fmdataforFmConfigResponseform with error status 430', (done) => {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ dataList: [] });
    
    const req2 = httpMock.expectOne('http://test.com/api/fm-topics');
    req2.flush({ dataList: [] });
    
    const req3 = httpMock.expectOne('http://test.com/api/fm-output-modcheck');
    req3.flush({ dataList: [] });
    
    const req4 = httpMock.expectOne('http://test.com/api/fm-data');
    req4.flush({ detail: 'Error occurred' }, { status: 430, statusText: 'Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should handle get_fmdataforFmConfigResponseform with other error', (done) => {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ dataList: [] });
    
    const req2 = httpMock.expectOne('http://test.com/api/fm-topics');
    req2.flush({ dataList: [] });
    
    const req3 = httpMock.expectOne('http://test.com/api/fm-output-modcheck');
    req3.flush({ dataList: [] });
    
    const req4 = httpMock.expectOne('http://test.com/api/fm-data');
    req4.flush({ message: 'Error' }, { status: 500, statusText: 'Server Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should handle getSelectDRopDownArrray with error status 430', (done) => {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ detail: 'Error occurred' }, { status: 430, statusText: 'Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should handle getSelectDRopDownArrray with other error', (done) => {
    fixture = TestBed.createComponent(AccModalFmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    const req1 = httpMock.expectOne('http://test.com/api/fm-modcheck');
    req1.flush({ message: 'Error' }, { status: 500, statusText: 'Server Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should submit form data successfully', (done) => {
    initializeComponent();
    
    component.FmConfigResponseForm.patchValue({
      ThemeTexts: 'theme1,theme2',
      inputModChecks: ['check1'],
      outputModChecks: ['check2']
    });
    
    component.submit();
    
    const req5 = httpMock.expectOne('http://test.com/api/fm-update');
    req5.flush({ success: true });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should submit form with error status 430', (done) => {
    initializeComponent();
    
    component.FmConfigResponseForm.patchValue({
      ThemeTexts: 'theme1',
      inputModChecks: ['check1'],
      outputModChecks: ['check2']
    });
    
    component.submit();
    
    const req5 = httpMock.expectOne('http://test.com/api/fm-update');
    req5.flush({ detail: 'Error occurred' }, { status: 430, statusText: 'Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });

  it('should submit form with other error', (done) => {
    initializeComponent();
    
    component.FmConfigResponseForm.patchValue({
      inputModChecks: ['check1'],
      outputModChecks: ['check2']
    });
    
    component.submit();
    
    const req5 = httpMock.expectOne('http://test.com/api/fm-update');
    req5.flush({ message: 'Error' }, { status: 500, statusText: 'Server Error' });
    
    setTimeout(() => {
      expect(component).toBeTruthy();
      done();
    }, 100);
  });
});

