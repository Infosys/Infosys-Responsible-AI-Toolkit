/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HomeComponent } from '../home/home.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from '../shared/shared.module';
import { StructuredTextModalComponent } from '../structured-text-modal/structured-text-modal.component';
import { HomeParentComponent } from '../home-parent/home-parent.component';
import { RecognizersModalAComponent } from '../Admin-Configuration/recognizers/recognizers-modal-a/recognizers-modal-a.component';
import { ImageReportChartComponent } from '../image-report-chart/image-report-chart.component';
import { AddDataModelComponent } from '../add-data-model/add-data-model.component';
import { AddModelComponent } from '../add-model/add-model.component';
import { AddvectorComponent } from '../addvector/addvector.component';
import { RightSidePopupComponent } from '../fm-moderation/right-side-popup/right-side-popup.component';
import { MagnifyImageReportComponent } from '../magnify-image-report/magnify-image-report.component';
import { ModelValidationComponent } from '../llm-benchmarking/model-validation/model-validation.component';
import { InfosysLeaderboardComponent } from '../llm-benchmarking/infosys-leaderboard/infosys-leaderboard.component';
import { PreviewModalComponent } from '../llm-benchmarking/model-validation/preview-modal/preview-modal.component';
import { ChatbotComponent } from '../chatbot/chatbot.component';
import { PageRoleAccessComponent } from '../user/user-management/page-role-access/page-role-access.component';
import { TemplateDataComponent } from '../Admin-Configuration/template-data/template-data.component';
import { NewUserComponent } from '../new-user/new-user.component';
import { FormatTemplateNamePipe } from '../pipes/format-template-name.pipe';
import { ImageHashifyRightModalComponent } from '../image/image-hashify-right-modal/image-hashify-right-modal.component';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { FairnessSideModalComponent } from '../image-generate/fairness-side-modal/fairness-side-modal.component';
import { LegalAgentComponent } from '../new-use-case/legal-agent/legal-agent.component';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTreeModule } from '@angular/material/tree';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatStepperModule } from '@angular/material/stepper';
import { NgxGraphModule } from '@swimlane/ngx-graph';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { RemoteMfeRoutingModule } from './remote-mfe-routing.module';

@NgModule({
  declarations: [
    HomeComponent,
    StructuredTextModalComponent,
    HomeParentComponent,
    RecognizersModalAComponent,
    ImageReportChartComponent,
    AddDataModelComponent,
    AddModelComponent,
    AddvectorComponent,
    RightSidePopupComponent,
    MagnifyImageReportComponent,
    ModelValidationComponent,
    InfosysLeaderboardComponent,
    PreviewModalComponent,
    ChatbotComponent,
    PageRoleAccessComponent,
    TemplateDataComponent,
    NewUserComponent,
    FormatTemplateNamePipe,
    ImageHashifyRightModalComponent,
    ImageDialogComponent,
    FairnessSideModalComponent,
    LegalAgentComponent,
  ],
  imports: [
    CommonModule,
    SharedModule,
    HttpClientModule,
    NgxGraphModule,
    FormsModule,
    ReactiveFormsModule,
    MatStepperModule,
    MatDialogModule,
    MatTreeModule,
    MatCheckboxModule,
    MatSelectModule,
    MatOptionModule,
    MatIconModule,
    MatExpansionModule,
    NgxSkeletonLoaderModule,
    RemoteMfeRoutingModule,
  ]
})
export class RemoteMfeModule { }