import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComplianceCheckComponent } from './compliance-check.component';

describe('ComplianceCheckComponent', () => {
  let component: ComplianceCheckComponent;
  let fixture: ComponentFixture<ComplianceCheckComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ComplianceCheckComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComplianceCheckComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
