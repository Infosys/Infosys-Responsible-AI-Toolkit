/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MatSelectModule} from '@angular/material/select';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import {MatSidenavModule} from '@angular/material/sidenav';
import {MatTabsModule} from '@angular/material/tabs';
import {MatListModule} from '@angular/material/list';
import {MatRadioModule} from '@angular/material/radio';
import {MatButtonModule} from '@angular/material/button';
import {MatTableModule} from '@angular/material/table';
import {MatIconModule} from '@angular/material/icon';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import {MatInputModule} from '@angular/material/input';
import {NgxPaginationModule} from 'ngx-pagination';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatCardModule} from '@angular/material/card';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import {MatDialogModule} from '@angular/material/dialog';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import {MatSliderModule} from '@angular/material/slider';
import { MatPseudoCheckboxModule } from '@angular/material/core';
import { MatTreeModule } from '@angular/material/tree';

import { MatStepperModule } from '@angular/material/stepper';

import { LoggerModule, NgxLoggerLevel } from 'ngx-logger';


import { HasAnyAuthorityDirective } from '../remote-mfe/has-any-authority.directive';
import { RequestModerationComponent } from '../fm-moderation/request-moderation/request-moderation.component';
import { TemplateBasedGuardrailComponent } from '../fm-moderation/request-moderation/template-based-guardrail/template-based-guardrail.component';
import { TruncateDecimalPipe } from '../decimal.pipe';
import { MultiModalComponent } from '../fm-moderation/request-moderation/multi-modal/multi-modal.component';
import { ResponseModerationComponent } from '../fm-moderation/response-moderation/response-moderation.component';
import { TemplateBasedGuardrailResponseComponent } from '../fm-moderation/response-moderation/template-based-guardrail-response/template-based-guardrail-response.component';
import { ResponseComparisonComponent } from '../fm-moderation/response-comparison/response-comparison.component';
import { LlmScannerComponent } from '../llm-scanner/llm-scanner.component';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

// import { ReactiveFormsModule } from '@angular/forms';




@NgModule({
  declarations: [
    HasAnyAuthorityDirective, 
    RequestModerationComponent, 
    TemplateBasedGuardrailComponent, 
    TruncateDecimalPipe, 
    MultiModalComponent,
    
    ResponseModerationComponent,
    TemplateBasedGuardrailResponseComponent,

    ResponseComparisonComponent,
    LlmScannerComponent
  ],
  imports: [
    CommonModule,
    MatCheckboxModule,
    NgxPaginationModule,
    FormsModule,
    MatSidenavModule,
    MatTabsModule,
    MatListModule,
    MatSelectModule,
    MatRadioModule,
    MatButtonModule,
    MatTableModule,
    MatIconModule,
    MatSlideToggleModule,
    MatInputModule,
    MatProgressBarModule,
    MatExpansionModule,
    MatCardModule,
    MatSnackBarModule,
    NgbModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatSliderModule,
    MatPseudoCheckboxModule,
    MatTreeModule,


    MatStepperModule,
    ReactiveFormsModule,
    NgxSkeletonLoaderModule,
    LoggerModule.forRoot({
      level: NgxLoggerLevel.DEBUG,
      serverLogLevel: NgxLoggerLevel.OFF,
      disableConsoleLogging: false
    }),
  ],
  exports:[
    MatCheckboxModule,
    NgxPaginationModule,
    FormsModule,
    MatSidenavModule,
    MatTabsModule,
    MatListModule,
    MatSelectModule,
    MatRadioModule,
    MatButtonModule,
    MatTableModule,
    MatIconModule,
    MatSlideToggleModule,
    MatInputModule,
    MatProgressBarModule,
    MatExpansionModule,
    MatCardModule,
    MatSnackBarModule,
    MatSliderModule,
    NgbModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    ReactiveFormsModule,
    HasAnyAuthorityDirective,
    MatTreeModule,
    RequestModerationComponent,
    TemplateBasedGuardrailComponent,
    TruncateDecimalPipe,
    MultiModalComponent,
    ResponseModerationComponent,
    TemplateBasedGuardrailResponseComponent,
    ResponseComparisonComponent,
    LlmScannerComponent

  ]
})
export class SharedModule { }
