/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConfigurationParentComponent } from './configuration-parent.component';
import { RecognizersComponent } from '../recognizers/recognizers.component';
import { AccountMapingComponent } from '../account-maping/account-maping.component';
import { CustomTemplateComponent } from '../custom-template/custom-template.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { ApplicationConfigurationsComponent } from '../application-configurations/application-configurations.component';
import { FMChatConfigurationComponent } from '../fm-chat-configuration/fm-chat-configuration.component';
import { AccountsConfigurationComponent } from '../accounts-configuration/accounts-configuration.component';
import { TemplateMappingComponent } from '../template-mapping/template-mapping.component';
import { SafetyParametersComponent } from '../safety-parameters/safety-parameters.component';
import { FmParametersComponent } from '../fm-parameters/fm-parameters.component';
import { PrivacyParametersComponent } from '../accounts-configuration/privacy-parameters/privacy-parameters.component';
import { AccountsConfigurationModalPrivacyComponent } from '../accounts-configuration/accounts-configuration-modal-privacy/accounts-configuration-modal-privacy.component';
import { AccountsConfigurationModalFmComponent } from '../accounts-configuration/accounts-configuration-modal-fm/accounts-configuration-modal-fm.component';
import { AccountsConfigurationModalSafetyComponent } from '../accounts-configuration/accounts-configuration-modal-safety/accounts-configuration-modal-safety.component';
import { AccountsConfigurationModalCreatePmComponent } from '../accounts-configuration/accounts-configuration-modal-create-pm/accounts-configuration-modal-create-pm.component';
import { AccountsConfigurationModalCreateTemplateUpdateComponent } from '../accounts-configuration/admin-template-update/admin-template-update';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { ChunkPipe } from 'src/app/chunk.pipe';
import { FilterBySubcategoryPipe } from 'src/app/filter-by-subcategory.pipe';
import { RouterModule, Routes } from '@angular/router';
import { ApiConfigurationComponent } from '../api-configuration/api-configuration.component';

const routes: Routes = [
  { path: '', component: ConfigurationParentComponent }
];

@NgModule({
  declarations: [
    ConfigurationParentComponent,
    RecognizersComponent,
    AccountMapingComponent,
    CustomTemplateComponent,
    ApplicationConfigurationsComponent,
    FMChatConfigurationComponent,
    AccountsConfigurationComponent,
    TemplateMappingComponent,
    SafetyParametersComponent,
    FmParametersComponent,
    PrivacyParametersComponent,
    AccountsConfigurationModalPrivacyComponent,
    AccountsConfigurationModalFmComponent,
    AccountsConfigurationModalSafetyComponent,
    AccountsConfigurationModalCreatePmComponent,
    AccountsConfigurationModalCreateTemplateUpdateComponent,
    ChunkPipe,
    FilterBySubcategoryPipe,
    ApiConfigurationComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    NgxSkeletonLoaderModule,
    RouterModule.forChild(routes)
  ]
})
export class ConfigurationParentModule { }
