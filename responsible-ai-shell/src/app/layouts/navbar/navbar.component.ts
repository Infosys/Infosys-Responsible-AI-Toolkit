/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Inject, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { SessionStorageService } from 'ngx-webstorage';

import { Account } from '../../../app/core/auth/account.model';
import { AccountService } from '../../../app/core/auth/account.service';
import { LoginService } from '../../../app/login/login.service';
import { ProfileService } from '../../../app/layouts/profiles/profile.service';
import { EntityNavbarItems } from '../../../app/entities/entity-navbar-items';

import { MsalBroadcastService, MsalService } from '@azure/msal-angular';
import { InteractionStatus } from '@azure/msal-browser';
import { filter, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { RegisterService } from 'src/app/account/register/register.service';
import { EMAIL_ALREADY_USED_TYPE, LOGIN_ALREADY_USED_TYPE } from '../../../app/config/error.constants';
import { EventMessage, EventType, AuthenticationResult } from '@azure/msal-browser';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { urlList } from 'src/app/utils/urlList';
import { colorSets } from '@swimlane/ngx-charts';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/user-validation.service';
@Component({
  selector: 'jhi-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent implements OnInit {
  private readonly _destroying$ = new Subject<void>();
  ip_port: any;
  raiKabanUrl: any;

  inProduction?: boolean;
  isNavbarCollapsed = true;
  openAPIEnabled?: boolean;
  version = '';
  account: Account | null = null;
  entitiesNavbarItems: any[] = [];
  loggedIn = false;
  doNotMatch = false;
  error = false;
  errorEmailExists = false;
  errorUserExists = false;
  success = false;
  authenticationError = false;
  roles: any;
  pages: any;

  callCount: number = 0;
  portfolioSelected = false;
  Accountselected = false;
  Portfolio_options = [];
  Account_options = [];
  accountDetail: any;
  portfolioArr: any = [];
  AccountForm!: FormGroup;
  portfolioUrl : any;
  dashboardLink : any;
  csrfToken: string;
  constructor(
    private loginService: LoginService,
    private translateService: TranslateService,
    private sessionStorageService: SessionStorageService,
    private accountService: AccountService,
    private profileService: ProfileService,
    private router: Router,
    private msalBroadcastService: MsalBroadcastService,
    private authService: MsalService,
    private registerService: RegisterService,
    public _snackBar: MatSnackBar,
    private http: HttpClient,
    public nonceService:NonceService,
    public validationService: UserValidationService
  ) //private loginModalService: LoginModalService
  {
    this.AccountFormCall();
   this.dashboardLink =  urlList.telemetry_dashboard;
   this.csrfToken = this.nonceService.getNonce();
  }

  // This method is used to get the URL for the portfolio API
  // It retrieves the IP and port from local storage and constructs the URL
goToUrl(){
  if(localStorage.getItem("res") != null){
    const x = localStorage.getItem("res")
    if(x != null){
      this.ip_port = JSON.parse(x);
    }
    this.portfolioUrl = this.ip_port.result.Admin + this.ip_port.result.getAccountDetail;
  }
}

  ngOnInit(): void {
    this.clearLocalStorage();
    if (environment.isSSO) {
      console.log("MSAL SERVICE INIT");
      this.msalBroadcastService.inProgress$
        .pipe(
          filter((status: InteractionStatus) => status === InteractionStatus.None),
          takeUntil(this._destroying$)
        )
        .subscribe(() => {
          this.setLoginDisplay();
          console.log("SET LOGIN DISPLAY METHOD ACTIVATED");
        });

      window.onscroll = () => {
        this.scrollFunction();
      };
      if (localStorage.getItem('mail') != null) {
        const mail = localStorage.getItem('mail');
        if (mail) {
          console.log("executing based on local storage");
          this.register();
        }
      }
    }

    this.entitiesNavbarItems = EntityNavbarItems;

    this.accountService.getAuthenticationState().subscribe(account => {
      this.account = account;
    });
    this.getInitials();
  }

  // This method is used to change the language of the application
  // It stores the selected language in session storage and updates the translation service
  changeLanguage(languageKey: string): void {
    this.sessionStorageService.store('locale', languageKey);
    this.translateService.use(languageKey);
  }

  // This method is used to collapse the navbar and reload the shell
  // It sets the isNavbarCollapsed property to true and calls the reloadShell method
  collapseNavbar(): void {
    this.isNavbarCollapsed = true;
    this.reloadShell();
  }

  // This method is used to reload the shell of the application
  // It subscribes to the router events and reloads the page when a NavigationEnd event occurs
  reloadShell(): void {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        location.reload();
      }
    });
  }

  // This method is used to check if the user is authenticated
  // It checks if the authentication token is present in session storage or local storage
  isAuthenticated(): boolean {
    return !!(sessionStorage.getItem('jhi-authenticationToken') || localStorage.getItem('jhi-authenticationToken'));
  }

  /**
   * This method is used to navigate to the login page
   * It sets the isNavbarCollapsed property to true and navigates to the login route
   */
  loginNavbar(): void {
    this.router.navigate(['/login']);
    console.log('1');
  }

  // This method is used to logout the user
  // It collapses the navbar, calls the logout method of the login service, and navigates to the login route
  logout(): void {
    this.collapseNavbar();
    this.loginService.logout();
    this.router.navigate(['/login']);
    localStorage.clear();
  }

  // This method is used to toggle the navbar collapse state
  // It sets the isNavbarCollapsed property to the opposite of its current value
  toggleNavbar(): void {
    this.isNavbarCollapsed = !this.isNavbarCollapsed;
  }

  // This method is used to get the image URL of the user
  // It checks if the user is authenticated and calls the getImageUrl method of the account service
  getImageUrl(): string {
    return this.isAuthenticated() ? this.accountService.getImageUrl() : '';
  }

  /**
   * This method is used to scroll the page to the top when the user clicks on the "Back to Top" button
   * It checks if the user has scrolled down 20 pixels from the top of the document and displays the button accordingly
   */
  scrollFunction(): void {
    const backToTop = document.getElementById('back_to_top') as HTMLElement;
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      backToTop.style.display = 'block';
    } else {
      backToTop.style.display = 'none';
    }
  }

  // This method is used to set the login display state
  // It checks if the user is logged in by checking the accounts in the authService instance
  setLoginDisplay(): void {
    console.log("in set login display");
    this.loggedIn = this.authService.instance.getAllAccounts().length > 0;
    if (this.loggedIn) {
      console.log('inside if logged In: ', new Date());
      const id = this.authService.instance.getAllAccounts()[0].username;
      const index = id.indexOf('@');
      localStorage.setItem('mail', id.substring(0, index) + '@infosys.com');
      this.register();
    }
  }

  // This method is used to register the user
  // It checks if the user is already registered and if not, it calls the save method of the register service
  register(): void {
    console.log("register from navbar");
    this.doNotMatch = false;
    this.error = false;
    this.errorEmailExists = false;
    this.errorUserExists = false;
    const userName = (window && window.localStorage && typeof localStorage !== 'undefined') ? localStorage.getItem('mail')! :'{}'
    const valid = this.validationService.isValidEmail(userName) || this.validationService.isValidName(userName)

    const cred = urlList.user_cred;
    if (cred !== urlList.user_cred && !valid) {
      this.doNotMatch = true;
    } else {
      const login = userName;
      const email = userName;
      this.registerService.save({ login, email, cred, langKey: 'en' }).subscribe(
       () => (this.success = true),
       response => this.processError(response),// modified backend to make this work
       ()=> this.login()

      );
    }
  }

  // This method is used to process the error response from the server
  // It checks the status code and sets the appropriate error flags
  private processError(response: HttpErrorResponse): void {
    if (response.status === 400 && response.error.type === LOGIN_ALREADY_USED_TYPE) {
      this.errorUserExists = true;
    } else if (response.status === 400 && response.error.type === EMAIL_ALREADY_USED_TYPE) {
      this.errorEmailExists = true;
    } else {
      this.error = true;
    }
  }

  // This method is used to check if the user is logged in
  // It checks if the user is authenticated and if the authentication token is present in session storage or local storage
  login(): void {
    console.log("IN LOGIN of navbar");
    localStorage.setItem('userName', localStorage.getItem('mail') || '{}');
    this.loginService
      .login({
        username: localStorage.getItem('mail') || '{}',
        cred: urlList.user_cred,
        rememberMe: true,
      })
      .subscribe(
        (res: any) => {
          this.authenticationError = false;
          if (!this.router.getCurrentNavigation()) {
            this.router.navigate(['responsible-ui']);
          }
          console.log("login response", res.login);
          console.log("login response", res.authorities[0]);

          localStorage.setItem("role", JSON.stringify(res.authorities[0]));
          localStorage.setItem("userid", JSON.stringify(res.login));

          this.roles = res.authorities;
          console.log("ROLES FROM LOCAL STORAGE" + this.roles);

          this.loginService.getPages(this.roles).subscribe((pages: any) => {
            this.pages = pages;
            console.log(this.pages);
          });

          this.msalBroadcastService.msalSubject$
            .pipe(
              filter((msg: EventMessage) => msg.eventType === EventType.LOGIN_SUCCESS)
            )
            .subscribe((result: EventMessage) => {
              const payload = result.payload as AuthenticationResult;
              this.authService.instance.setActiveAccount(payload.account);
            });
        },
        () => (this.authenticationError = true)
      );
  }

  // This method is used to get the initials of the user
  // It checks if the user is authenticated and calls the getUserNames method of the account service
  getInitials(): string {
    return this.isAuthenticated() ? this.accountService.getUserNames() : 'U';
  }

  // This method is used to create the form group for the account form
  // It initializes the form controls with default values and validators
  AccountFormCall() {
    this.AccountForm = new FormGroup({
      portfolio: new FormControl('Portfolio Name', [Validators.required]),
      account: new FormControl('Account Name', [Validators.required]),
    });
  }

  // This method is used to get the account data from the server
  // It calls the goToUrl method to get the URL and then makes an HTTP GET request to fetch the account details
  getAllAccountData() {
    this.goToUrl();
    this.http.get(this.portfolioUrl).subscribe(
      (res: any) => {
        console.log("res=========>>>", res[0].AccountDetails);

        this.accountDetail = res[0].AccountDetails;
        for (let i = 0; i < res[0].AccountDetails.length; i++) {
          console.log("portfolio", res);
          const portfolio = res[0].AccountDetails[i].portfolio;
          console.log("portfolio11111", portfolio);
          this.portfolioArr.push(portfolio);
        }
        this.Portfolio_options = this.portfolioArr.sort((a: string, b: string) => a.localeCompare(b));
        console.log("portfolio", this.portfolioArr);
      },
      error => {
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // This method is used to handle the change event of the portfolio dropdown
  // It updates the selected portfolio in local storage and filters the account options based on the selected portfolio
  accountDropDown() {
    this.callCount++;
    this.portfolioSelected = true;
    const portfolio = this.AccountForm.controls['portfolio'].value;
    if (portfolio === 'Portfolio Name') {
      localStorage.removeItem('selectedPortfolio');
      return;
    }
    localStorage.setItem('selectedPortfolio', portfolio);
    console.log("inside accountDrop===", portfolio);
    const accountArr: any = [];
    for (let i = 0; i < this.accountDetail.length; i++) {
      if (this.accountDetail[i].portfolio == portfolio) {
        accountArr.push(this.accountDetail[i].account);
      }
    }
    this.Account_options = accountArr;
    if (this.callCount > 1) {
      this.AccountForm.get('account')?.setValue(this.Account_options[0]);
      this.Accountselected = true;
    }
  }

  // This method is used to handle the change event of the account dropdown
  // It updates the selected account in local storage and checks if the form is valid before proceeding
  activateSubcommands() {
    this.Accountselected = true;
    const account = this.AccountForm.controls['account'].value;
    if (account === 'Account Name') {
      localStorage.removeItem('selectedAccount');
      return;
    }
    localStorage.setItem('selectedAccount', account);
    if (this.AccountForm.valid) {
      //this.openRightSideModal4(this.AccountForm.value)
    } else {
      this._snackBar.open("Please select an Account and Portfolio", "Close", {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
    }
  }

  // This method is used to clear the local storage items for selected portfolio and account
  // It removes the items from local storage to reset the selections
  clearLocalStorage(): void {
    localStorage.removeItem('selectedPortfolio');
    localStorage.removeItem('selectedAccount');
  }
}