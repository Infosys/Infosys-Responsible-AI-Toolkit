/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LandingComponent } from './landing.component';
import { loadRemoteModule } from '@angular-architects/module-federation';
import { UserRouteAccessService } from '../core/auth/user-route-access.service';


const routes: Routes = [
  {
    path: '', component: LandingComponent, children: [
      // {
      //   path: '', canActivate: [AuthGuardService], component: AppHomeComponent
      // },
      
  // {
  //   path: 'responsible-ui',
  //   //canActivate: [UserRouteAccessService],
  //   loadChildren: () => loadRemoteModule({
  //     type: "module",
  //       remoteEntry: 'http://10.66.155.13:30025/remoteEntry.js',
  //       exposedModule: './mainModule'
  //     })
  //     .then(m => m.MainModule),
  //     data: {
  //       pageTitle: 'responsible-ui',
  //     },
  // },

  {
    path: 'responsible-ui',
    //canActivate: [UserRouteAccessService],
    loadChildren: () => loadRemoteModule({
      type: "module",
        remoteEntry: 'http://10.66.155.13:30025/remoteEntry.js',
        exposedModule: './AppModule'
      })
      .then(m => m.AppModule),
      data: {
        pageTitle: 'responsible-ui',
      },
  },
     

      
     
     

      
      
    
    ]
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LandingRoutingModule { }
