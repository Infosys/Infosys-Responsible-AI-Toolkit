import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import { BaseHrefService } from './base-href.service';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

describe('AppComponent', () => {
  let mockBaseHrefService: jasmine.SpyObj<BaseHrefService>;

  beforeEach(async () => {
    mockBaseHrefService = jasmine.createSpyObj('BaseHrefService', ['setBaseHref', 'getBaseHref']);
    mockBaseHrefService.getBaseHref.and.returnValue('/shell/');

    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule
      ],
      declarations: [
        AppComponent
      ],
      providers: [
        { provide: BaseHrefService, useValue: mockBaseHrefService }
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should have title AI_Demo', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app.title).toEqual('AI_Demo');
  });

  it('should call setBaseHref with environment.isSSO on ngOnInit', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges(); // triggers ngOnInit
    
    expect(mockBaseHrefService.setBaseHref).toHaveBeenCalledWith(false);
  });

  it('should call getBaseHref and set base element href on ngOnInit', () => {
    const fixture = TestBed.createComponent(AppComponent);
    
    // Create a base element in the DOM
    const baseElement = document.createElement('base');
    baseElement.setAttribute('href', '/');
    document.head.appendChild(baseElement);
    
    fixture.detectChanges(); // triggers ngOnInit
    
    expect(mockBaseHrefService.getBaseHref).toHaveBeenCalled();
    expect(baseElement.getAttribute('href')).toBe('/shell/');
    
    // Cleanup
    document.head.removeChild(baseElement);
  });

  it('should not throw error if base element does not exist', () => {
    const fixture = TestBed.createComponent(AppComponent);
    
    // Ensure no base element exists
    const baseElement = document.querySelector('base');
    if (baseElement) {
      document.head.removeChild(baseElement);
    }
    
    expect(() => fixture.detectChanges()).not.toThrow();
  });
});
