import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApiConfigurationComponent } from './api-configuration.component';

describe('ApiConfigurationComponent', () => {
  let component: ApiConfigurationComponent;
  let fixture: ComponentFixture<ApiConfigurationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ApiConfigurationComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApiConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
