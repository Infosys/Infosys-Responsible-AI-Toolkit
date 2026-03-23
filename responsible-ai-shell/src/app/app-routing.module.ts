/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { errorRoute } from './layouts/error/error.route';
import { sidebarRoute } from './layouts/sidebar/sidebar.route';
import { DEBUG_INFO_ENABLED } from '../app/app.constants';
import { Authority } from '../app/config/authority.constants';
import { navbarRoute } from './layouts/navbar/navbar.route';
import { LoginComponent } from '../app/login/login.component';

import { UserRouteAccessService } from '../app/core/auth/user-route-access.service';

import { loadRemoteModule } from '@angular-architects/module-federation-runtime';
import { HomeComponent } from './home/home.component';
import { environment } from 'src/environments/environment';
import { urlList } from './utils/urlList';
import { MsalGuard } from '@azure/msal-angular';
const LAYOUT_ROUTES = [navbarRoute, ...errorRoute];


const routes: Routes = [
  // {
  //   path:'login',canActivate: [UserRouteAccessService],
  //   component:LoginComponent,
  //   data: {
  //     authorities: [Authority.USER],
  //     pageTitle: 'Shell',
  //   },
  // },




  {
    path: "login",
    component : LoginComponent,
   // canActivate: [UserRouteAccessService],
  //  loadChildren: () => import('./login/login.module').then(m => m.LoginModule)
  },
  {
    path: 'admin',
    data: {
      authorities: [Authority.ADMIN],
    },
    canActivate: [UserRouteAccessService,MsalGuard],
    loadChildren: () => import('./admin/admin-routing.module').then(m => m.AdminRoutingModule),
  },
  {
    path: 'account',
    loadChildren: () => import('./account/account.module').then(m => m.AccountModule),
  },
  {
    path: 'landing',
    canActivate: [UserRouteAccessService],
    loadChildren: () => import('./landing/landing.module').then(m => m.LandingModule)
  },
  {
    path: 'responsible-ui',
    canActivate: [UserRouteAccessService],
    loadChildren: () => loadRemoteModule({
      type: "module",
      remoteEntry: urlList.mfe_url + '/remoteEntry.js',
      exposedModule: './RemoteMfeModule'
      })
      .then(m => m.RemoteMfeModule),
      data: {
        pageTitle: 'responsible-ui',
      },
  },

  // {
  //   path: 'responsible-ui',
  //   //canActivate: [UserRouteAccessService],
  //   loadChildren: () => loadRemoteModule({
  //     type: "module",
  //       remoteEntry: 'http://localhost:30025/remoteEntry.js',
  //       exposedModule: './mainModule'
  //     })
  //     .then(m => m.MainModule),
  //     data: {
  //       pageTitle: 'responsible-ui',
  //     },
  // },
 
   ...LAYOUT_ROUTES
];

@NgModule({
   // The initalNavigation has to be disabled, this is required for OAUTH
   imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
