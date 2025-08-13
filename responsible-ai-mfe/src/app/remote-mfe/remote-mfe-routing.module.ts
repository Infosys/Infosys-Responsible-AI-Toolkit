/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { HomeComponent } from '../home/home.component';
import { SharedModule } from '../shared/shared.module';

export const remoteRoutes: Route[] = [
  { path: '', component: HomeComponent,
    children: [
      { path: 'workbench', 
        loadChildren: () => import('../workbench/workbench.module').then(m => m.WorkbenchModule)
      },
      { path: 'use-cases', 
        loadChildren: () => import('../new-use-case/new-use-case.module').then(m => m.NewUseCaseModule)
      },
      { path: 'admin-configuration', 
        loadChildren: () => import('../Admin-Configuration/configuration-parent/configuration-parent.module').then(m => m.ConfigurationParentModule)
      },
      { path: 'ai-models', 
        loadChildren: () => import('../ai-models/ai-models.module').then(m => m.AiModelsModule)
      },
      { path: 'llm-benchmarking', 
        loadChildren: () => import('../llm-benchmarking/llm-benchmarking.module').then(m => m.LlmBenchmarkingModule)
      },
      { path: 'ai-content-detector', 
        loadChildren: () => import('../ai-content-detector/ai-content-detector.module').then(m => m.AiContentDetectorModule)
      },
      { path: 'document-management', 
        loadChildren: () => import('../semi-structured-text/semi-structured-text.module').then(m => m.SemiStructuredTextModule)
      },
      { path: 'user-management', 
        loadChildren: () => import('../user/user-management/user-management.module').then(m => m.UserManagementModule)
      },
      { path: 'red-teaming', 
        loadChildren: () => import('../llm-red-teaming/llm-red-teaming.module').then(m => m.LlmRedTeamingModule)
      },
      // { path: 'llm-scanner', 
      //   loadChildren: () => import('../llm-scanner/llm-scanner.module').then(m => m.LlmScannerModule)
      // },
      { path: 'compliance-check', 
        loadChildren: () => import('../compliance-check/compliance-check.module').then(m => m.ComplianceCheckModule)
      },
      { path: 'bulk-processing', 
        loadChildren: () => import('../bulk-processing/bulk-processing.module').then(m => m.BulkProcessingModule)
      },
      { path: '',   redirectTo: '/responsible-ui/workbench', pathMatch: 'full' },
      // ====== add routes for wild card ======
      // {path: '**', redirectTo: ''}
    ]
  }
];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    SharedModule,
    RouterModule.forChild(remoteRoutes)
  ],
  exports: [RouterModule]
})
export class RemoteMfeRoutingModule { }
