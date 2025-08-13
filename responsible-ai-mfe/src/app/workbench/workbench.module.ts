/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatDialogModule } from '@angular/material/dialog';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

import { WorkbenchComponent } from './workbench.component';
import { UnstructuredTextComponent } from '../unstructured-text/unstructured-text.component';
import { StructureTextParentComponent } from '../structure-text-parent/structure-text-parent.component';
import { ImageParentComponent } from '../image-parent/image-parent.component';
import { VideoComponent } from '../video/video.component';
import { CodePrivacyComponent } from '../code-privacy/code-privacy.component';
import { FmModerationComponent } from '../fm-moderation/fm-moderation.component';
import { StructuredTextComponent } from '../structured-text/structured-text.component';
import { DifferentialPrivacyComponent } from '../differential-privacy/differential-privacy.component';
import { ImageGenerateComponent } from '../image-generate/image-generate.component';
import { ResponseModerationHallucinationComponent } from '../fm-moderation/response-moderation-hallucination/response-moderation-hallucination.component';
import { PrivacyResultComponent } from '../fm-moderation/privacy-result/privacy-result.component';
import { FairnessResultComponent } from '../fm-moderation/fairness-result/fairness-result.component';
import { ExplainabilityResultComponent } from '../fm-moderation/explainability-result/explainability-result.component';
import { ProfanityResultComponent } from '../fm-moderation/profanity-result/profanity-result.component';
import { ImageComponent } from '../image/image.component';
import { ImageDicomComponent } from '../image-dicom/image-dicom.component';
import { DicomViewerModule } from '../dicom-lib/dicom-viewer.module';
import { SharedModule } from '../shared/shared.module';
import { LiveStreamComponent } from '../live-stream/live-stream.component';

const routes: Routes = [
  { path: '', component: WorkbenchComponent }
];

@NgModule({
  declarations: [
    WorkbenchComponent,
    UnstructuredTextComponent,
    StructureTextParentComponent,
    ImageParentComponent,
    VideoComponent,
    CodePrivacyComponent,
    FmModerationComponent,
    StructuredTextComponent,
    DifferentialPrivacyComponent,
    ImageGenerateComponent,
    ResponseModerationHallucinationComponent,
    PrivacyResultComponent,
    ProfanityResultComponent,
    ExplainabilityResultComponent,
    FairnessResultComponent,
    ImageComponent,
    ImageDicomComponent,
    LiveStreamComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    NgxSkeletonLoaderModule,
    DicomViewerModule,
    MatDialogModule,
    RouterModule.forChild(routes)
  ],
  exports: [WorkbenchComponent]
})
export class WorkbenchModule { }