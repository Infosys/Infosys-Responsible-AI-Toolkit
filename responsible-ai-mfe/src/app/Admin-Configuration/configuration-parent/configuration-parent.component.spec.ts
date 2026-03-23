/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA, ElementRef } from '@angular/core';
import { Subject } from 'rxjs';

import { ConfigurationParentComponent } from './configuration-parent.component';
import { SharedService } from './shared.service';

describe('ConfigurationParentComponent', () => {
  let component: ConfigurationParentComponent;
  let fixture: ComponentFixture<ConfigurationParentComponent>;
  let sharedService: SharedService;
  let clickEventSubject: Subject<void>;

  beforeEach(async () => {
    clickEventSubject = new Subject<void>();

    const sharedServiceSpy = jasmine.createSpyObj('SharedService', [], {
      clickEvent$: clickEventSubject.asObservable()
    });

    await TestBed.configureTestingModule({
      declarations: [ ConfigurationParentComponent ],
      providers: [
        { provide: SharedService, useValue: sharedServiceSpy }
      ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfigurationParentComponent);
    component = fixture.componentInstance;
    sharedService = TestBed.inject(SharedService);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Component initialization', () => {
    it('should initialize with default values', () => {
      expect(component.selectedTab).toBe(0);
      expect(component.recoGnizers).toBe(true);
      expect(component.accountMaping).toBe(false);
      expect(component.subscription).toBeDefined();
    });

    it('should have subscription property', () => {
      expect(component.subscription).toBeDefined();
    });

    it('should inject SharedService in constructor', () => {
      expect(sharedService).toBeDefined();
    });

    it('should create component with proper dependencies', () => {
      const newComponent = new ConfigurationParentComponent(sharedService);
      expect(newComponent).toBeTruthy();
      expect(newComponent.selectedTab).toBe(0);
      expect(newComponent.recoGnizers).toBe(true);
      expect(newComponent.accountMaping).toBe(false);
    });
  });

  describe('ngOnInit', () => {
    it('should subscribe to sharedService clickEvent$', () => {
      const clickAccountMappingSpy = spyOn(component, 'clickAccountMapping');
      
      component.ngOnInit();
      
      expect(component.subscription).toBeDefined();
      
      // Trigger the event
      clickEventSubject.next();
      
      expect(clickAccountMappingSpy).toHaveBeenCalled();
    });

    it('should set up subscription that calls clickAccountMapping when event emitted', () => {
      // Mock the accountMapping ViewChild
      component.accountMapping = {
        nativeElement: {
          click: jasmine.createSpy('click')
        }
      } as any;

      component.ngOnInit();
      
      // Emit event
      clickEventSubject.next();
      
      expect(component.accountMapping.nativeElement.click).toHaveBeenCalled();
    });

    it('should create a new subscription instance', () => {
      const initialSubscription = component.subscription;
      
      component.ngOnInit();
      
      expect(component.subscription).toBeDefined();
      expect(component.subscription).not.toBe(initialSubscription);
    });

    it('should properly set up observable subscription', () => {
      component.ngOnInit();
      
      expect(component.subscription.closed).toBe(false);
    });

    it('should handle subscription callback properly', () => {
      let callbackExecuted = false;
      spyOn(component, 'clickAccountMapping').and.callFake(() => {
        callbackExecuted = true;
      });
      
      component.ngOnInit();
      clickEventSubject.next();
      
      expect(callbackExecuted).toBe(true);
    });
  });

  describe('ngOnDestroy', () => {
    it('should unsubscribe from subscription', () => {
      component.ngOnInit();
      spyOn(component.subscription, 'unsubscribe');
      
      component.ngOnDestroy();
      
      expect(component.subscription.unsubscribe).toHaveBeenCalled();
    });

    it('should not throw error if subscription is already unsubscribed', () => {
      component.ngOnInit();
      component.subscription.unsubscribe();
      
      expect(() => component.ngOnDestroy()).not.toThrow();
    });

    it('should clean up subscription to prevent memory leaks', () => {
      component.ngOnInit();
      
      component.ngOnDestroy();
      
      expect(component.subscription.closed).toBe(true);
    });
  });

  describe('toggleTab', () => {
    it('should toggle recoGnizers from true to false', () => {
      component.recoGnizers = true;
      
      component.toggleTab();
      
      expect(component.recoGnizers).toBe(false);
    });

    it('should toggle recoGnizers from false to true', () => {
      component.recoGnizers = false;
      
      component.toggleTab();
      
      expect(component.recoGnizers).toBe(true);
    });

    it('should toggle accountMaping from false to true', () => {
      component.accountMaping = false;
      
      component.toggleTab();
      
      expect(component.accountMaping).toBe(true);
    });

    it('should toggle accountMaping from true to false', () => {
      component.accountMaping = true;
      
      component.toggleTab();
      
      expect(component.accountMaping).toBe(false);
    });

    it('should toggle both properties simultaneously', () => {
      component.recoGnizers = true;
      component.accountMaping = false;
      
      component.toggleTab();
      
      expect(component.recoGnizers).toBe(false);
      expect(component.accountMaping).toBe(true);
    });

    it('should toggle back to original state when called twice', () => {
      const initialRecoGnizers = component.recoGnizers;
      const initialAccountMaping = component.accountMaping;
      
      component.toggleTab();
      component.toggleTab();
      
      expect(component.recoGnizers).toBe(initialRecoGnizers);
      expect(component.accountMaping).toBe(initialAccountMaping);
    });
  });

  describe('clickAccountMapping', () => {
    it('should call click on accountMapping nativeElement', () => {
      const mockNativeElement = {
        click: jasmine.createSpy('click')
      };
      
      component.accountMapping = {
        nativeElement: mockNativeElement
      } as any;
      
      component.clickAccountMapping();
      
      expect(mockNativeElement.click).toHaveBeenCalled();
    });

    it('should call click method once', () => {
      const mockNativeElement = {
        click: jasmine.createSpy('click')
      };
      
      component.accountMapping = {
        nativeElement: mockNativeElement
      } as any;
      
      component.clickAccountMapping();
      
      expect(mockNativeElement.click).toHaveBeenCalledTimes(1);
    });

    it('should trigger click on the correct element reference', () => {
      const mockElement = document.createElement('div');
      spyOn(mockElement, 'click');
      
      component.accountMapping = {
        nativeElement: mockElement
      } as ElementRef;
      
      component.clickAccountMapping();
      
      expect(mockElement.click).toHaveBeenCalled();
    });
  });

  describe('Integration tests', () => {
    it('should handle complete lifecycle: init, toggle, destroy', () => {
      // Mock ViewChild
      component.accountMapping = {
        nativeElement: {
          click: jasmine.createSpy('click')
        }
      } as any;

      // Initialize
      component.ngOnInit();
      expect(component.recoGnizers).toBe(true);
      expect(component.accountMaping).toBe(false);
      
      // Toggle
      component.toggleTab();
      expect(component.recoGnizers).toBe(false);
      expect(component.accountMaping).toBe(true);
      
      // Trigger event
      clickEventSubject.next();
      expect(component.accountMapping.nativeElement.click).toHaveBeenCalled();
      
      // Destroy
      const unsubscribeSpy = spyOn(component.subscription, 'unsubscribe');
      component.ngOnDestroy();
      expect(unsubscribeSpy).toHaveBeenCalled();
    });

    it('should handle multiple toggle operations', () => {
      component.recoGnizers = true;
      component.accountMaping = false;
      
      component.toggleTab(); // 1st toggle
      expect(component.recoGnizers).toBe(false);
      expect(component.accountMaping).toBe(true);
      
      component.toggleTab(); // 2nd toggle
      expect(component.recoGnizers).toBe(true);
      expect(component.accountMaping).toBe(false);
      
      component.toggleTab(); // 3rd toggle
      expect(component.recoGnizers).toBe(false);
      expect(component.accountMaping).toBe(true);
    });

    it('should properly subscribe and handle events throughout component lifecycle', () => {
      component.accountMapping = {
        nativeElement: {
          click: jasmine.createSpy('click')
        }
      } as any;

      component.ngOnInit();
      
      // Emit multiple events
      clickEventSubject.next();
      clickEventSubject.next();
      clickEventSubject.next();
      
      expect(component.accountMapping.nativeElement.click).toHaveBeenCalledTimes(3);
      
      component.ngOnDestroy();
      
      // After destroy, no more events should be handled
      clickEventSubject.next();
      expect(component.accountMapping.nativeElement.click).toHaveBeenCalledTimes(3);
    });
  });

  describe('ViewChild', () => {
    it('should have accountMapping ViewChild defined after view init', () => {
      fixture.detectChanges();
      
      // ViewChild should be initialized after view init
      expect(component.accountMapping).toBeDefined();
    });
  });

  describe('Properties', () => {
    it('should have selectedTab property', () => {
      expect(component.selectedTab).toBeDefined();
      expect(typeof component.selectedTab).toBe('number');
    });

    it('should allow changing selectedTab value', () => {
      component.selectedTab = 5;
      expect(component.selectedTab).toBe(5);
      
      component.selectedTab = 0;
      expect(component.selectedTab).toBe(0);
    });

    it('should have boolean properties for tab states', () => {
      expect(typeof component.recoGnizers).toBe('boolean');
      expect(typeof component.accountMaping).toBe('boolean');
    });
  });
});
