/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { NgModule, LOCALE_ID } from '@angular/core';
import { APP_BASE_HREF, registerLocaleData } from '@angular/common';
import { HttpClient, HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import locale from '@angular/common/locales/en';
import { BrowserModule, Title } from '@angular/platform-browser';
import { ServiceWorkerModule } from '@angular/service-worker';
import { FaIconLibrary } from '@fortawesome/angular-fontawesome';
import { NgxWebstorageModule } from 'ngx-webstorage';
import dayjs from 'dayjs/esm';
import {
  NgbDateAdapter,
  NgbDatepickerConfig,
} from '@ng-bootstrap/ng-bootstrap';

import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { PopoverModule } from 'ngx-bootstrap/popover';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { RouterModule } from '@angular/router';
//import { TranslationModule } from '../app/shared/language/translation.module';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { ActiveMenuDirective } from './layouts/navbar/active-menu.directive';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ApplicationConfigService } from '../app/core/config/application-config.service';
import './config/dayjs';
import { SharedModule } from '../app/shared/shared.module';
import { AppRoutingModule } from './app-routing.module';
import { HomeModule } from './home/home.module';
import { EntityRoutingModule } from './entities/entity-routing.module';
// jhipster-needle-angular-add-module-import JHipster will add new module here
import { NgbDateDayjsAdapter } from './config/datepicker-adapter';
import { fontAwesomeIcons } from './config/font-awesome-icons';
import { httpInterceptorProviders } from '../app/core/interceptor/index';
import { MainComponent } from './layouts/main/main.component';
import { SidebarComponent } from './layouts/sidebar/sidebar.component';
import { FooterComponent } from './layouts/footer/footer.component';
import { PageRibbonComponent } from './layouts/profiles/page-ribbon.component';
import { ErrorComponent } from './layouts/error/error.component';
import { NavbarComponent } from './layouts/navbar/navbar.component';
import { NgxSliderModule } from '@angular-slider/ngx-slider';

import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
//import { MatSortModule } from '@angular/material/sort';
import { MatMenuModule } from '@angular/material/menu';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSliderModule } from '@angular/material/slider';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatRadioModule } from '@angular/material/radio';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { HomePageComponent } from './layouts/home-page/home-page.component';
import { RegularPagesComponent } from './layouts/regular-pages/regular-pages.component';
import { AdminComponent } from './admin/admin.component';


import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';

import { HighlighterPipe } from './highlighter.pipe';
import { ImageSelectDirective } from './image-select.directive';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';

import { CommonModule } from '@angular/common';
import { AdminModule } from './admin/admin.module';
import { LoginModule } from './login/login.module';
import { LoginComponent } from './login/login.component';

import { NgxChartsModule } from '@swimlane/ngx-charts';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { LandingComponent } from './landing/landing.component';

// import saveAs from 'file-saver';
// import { saveAs } from 'file-saver';
// saveAs

// import { SecurityComponent } from './security/security.component';
import { environment } from '../environments/environment';
import { urlList } from './utils/urlList';
import { IPublicClientApplication, PublicClientApplication, InteractionType, BrowserCacheLocation, LogLevel } from '@azure/msal-browser';
import {
  MsalGuard,
  MsalInterceptor,
  MsalInterceptorConfiguration,
  MsalModule,
  MsalService,
  MSAL_GUARD_CONFIG,
  MSAL_INSTANCE,
  MSAL_INTERCEPTOR_CONFIG,
  MsalGuardConfiguration,
  MsalRedirectComponent,
  MsalBroadcastService,
} from '@azure/msal-angular';
import { BaseHrefService } from './base-href.service';
const isIE = window.navigator.userAgent.includes('MSIE ') || window.navigator.userAgent.includes('Trident/');

export function initializeBaseHref(appBaseHrefService: BaseHrefService) {
  return () => appBaseHrefService.getBaseHref();
}

const allModules = [
  BrowserModule,
  BrowserAnimationsModule,
  HomeModule,
  AdminModule,
  LoginModule,
  // jhipster-needle-angular-add-module JHipster will add new module here
  EntityRoutingModule,
  AppRoutingModule,
  MatIconModule,
  MatInputModule,
  MatProgressBarModule,
  MatToolbarModule,
  MatTableModule,
  MatPaginatorModule,
  NgxSliderModule,
  MatSliderModule,
  MatTabsModule,
  MatMenuModule,
  SharedModule,
  NgxExtendedPdfViewerModule,
  CommonModule,
  MatFormFieldModule,
  MatSelectModule,
  MatCardModule,
  MatRadioModule,
  MatButtonModule,
  FormsModule,
  ReactiveFormsModule,
  PopoverModule,
  NgbModule,
  RouterModule,
  // TranslationModule,
  TranslateModule.forRoot({
    defaultLanguage: 'en',
    loader: {
      provide: TranslateLoader,
      useFactory: HttpLoaderFactory,
      deps: [HttpClient],
    },
  }),
  MatCheckboxModule,
  MatSnackBarModule,
  MatSlideToggleModule,
  // NgxChartsModule,
  MatTooltipModule,
  // saveAs,
  // jhipster-needle-angular-add-module JHipster will add new module here
  EntityRoutingModule,
  AppRoutingModule,
  // Set this to true to enable service worker (PWA)
  ServiceWorkerModule.register('ngsw-worker.js', { enabled: false }),
  HttpClientModule,
  NgxWebstorageModule.forRoot({
    prefix: 'jhi',
    separator: '-',
    caseSensitive: true,
  }),
  MsalModule
];
const allProviders: any = [
  Title,
  BaseHrefService,
  { provide: LOCALE_ID, useValue: 'en' },
  { provide: NgbDateAdapter, useClass: NgbDateDayjsAdapter },
  httpInterceptorProviders,
  MsalBroadcastService,
  {
    provide: HTTP_INTERCEPTORS,
    useClass: MsalInterceptor,
    multi: true,
  },
  {
    provide: MSAL_INSTANCE,
    useFactory: MSALInstanceFactory,
  },
  {
    provide: MSAL_GUARD_CONFIG,
    useFactory: MSALGuardConfigFactory,
  },
  {
    provide: MSAL_INTERCEPTOR_CONFIG,
    useFactory: MSALInterceptorConfigFactory,
  },
  MsalService,
  MsalGuard

];
const allDeclarations: any = [
  MainComponent,
  SidebarComponent,
  ErrorComponent,
  NavbarComponent,
  PageRibbonComponent,
  FooterComponent,
  HomePageComponent,
  RegularPagesComponent,
  AdminComponent,
  ImageSelectDirective,
  HighlighterPipe,
  AppComponent,
  HomeComponent,
  LoginComponent,
  ActiveMenuDirective,
  LandingComponent,
];
const allBootstrap: any = [AppComponent, MsalRedirectComponent];
@NgModule({
  imports: allModules,
  providers: allProviders,
  declarations: allDeclarations,
  bootstrap: allBootstrap,
})
export class AppModule {


  constructor(
    applicationConfigService: ApplicationConfigService,
    iconLibrary: FaIconLibrary,
    dpConfig: NgbDatepickerConfig
  ) {
    // applicationConfigService.setEndpointPrefix("http://10.66.155.13:30019");
    registerLocaleData(locale);
    iconLibrary.addIcons(...fontAwesomeIcons);
    //const dayjs=require('dayjs');
    dpConfig.minDate = {
      year: dayjs().subtract(100, 'year').year(),
      month: 1,
      day: 1,
    };
    if (environment.isSSO) {
      initializeApp()
      // allModules.push(MsalModule)
      // allProviders.push( )
      //allBootstrap.push(MsalRedirectComponent)   
    }
  }


}
// AoT requires an exported function for factories
export function HttpLoaderFactory(http: HttpClient): TranslateHttpLoader {
  return new TranslateHttpLoader(http);
}

const msalConfig = {
  auth: {
    clientId: urlList.azure_clientid,
    redirectUri: urlList.azure_redirecturi,
    authority: urlList.azure_authority,
    navigateToLoginRequestUrl: true,
  },
};
export const msalInstance = await PublicClientApplication.createPublicClientApplication(msalConfig);

/**
 * Initializes the MSAL application.
 * This function is called to set up the MSAL instance and handle any errors during initialization.
 */
async function initializeApp() {
  try {
    await msalInstance.initialize();
    console.log('MSAL initialized successfully');
    // Call other MSAL APIs after successful initialization
  } catch (error) {
    console.log('MSAL initialization failed:', error);
  }
}

export function MSALInstanceFactory(): PublicClientApplication {
  return new PublicClientApplication(msalConfig);
}
export function MSALInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();
  protectedResourceMap.set('https://graph.microsoft.com/v1.0/me', ['user.read']);

  return {
    interactionType: InteractionType.Redirect,
    protectedResourceMap,
  };
}

export function MSALGuardConfigFactory(): MsalGuardConfiguration {
  return {
    interactionType: InteractionType.Redirect,
    authRequest: {
      scopes: ['user.read'],
    },
  };

}
