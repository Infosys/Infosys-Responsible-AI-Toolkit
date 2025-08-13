/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NewUseCaseComponent } from './new-use-case.component';
import { SharedModule } from '../shared/shared.module';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { AiAgentComponent } from './ai-agent/ai-agent.component';
import { SowComponent } from './sow/sow.component';
import { UseCaseReportComponent } from '../use-case-report/use-case-report.component';
import { UseCaseParentComponent } from '../use-case-parent/use-case-parent.component';
import { AiCanvasUsecaseComponent } from '../ai-canvas-usecase/ai-canvas-usecase.component';
import { RaiCanvasUsecaseComponent } from '../rai-canvas-usecase/rai-canvas-usecase.component';
import { QuestionnaireUsecaseComponent } from '../questionnaire-usecase/questionnaire-usecase.component';
import { MatStepperModule } from '@angular/material/stepper';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', component: NewUseCaseComponent }
];

@NgModule({
  declarations: [
    NewUseCaseComponent,
    AiAgentComponent,
    SowComponent,
    UseCaseReportComponent,
    UseCaseParentComponent,
    AiCanvasUsecaseComponent,
    RaiCanvasUsecaseComponent,
    QuestionnaireUsecaseComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    NgxSkeletonLoaderModule,
    MatStepperModule,
    RouterModule.forChild(routes)
  ]
})
export class NewUseCaseModule { }
