/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ViewChild, OnInit, AfterViewInit, ElementRef } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { LoginService } from '../../app/login/login.service';
import { AccountService } from '../../app/core/auth/account.service';
import { environment } from 'src/environments/environment';
// for azure login
import { MsalService, MsalBroadcastService } from '@azure/msal-angular';
import { EventMessage, EventType, AuthenticationResult } from '@azure/msal-browser';
import { filter } from 'rxjs/operators';
// for register
import { RegisterService } from 'src/app/account/register/register.service';
import { EMAIL_ALREADY_USED_TYPE, LOGIN_ALREADY_USED_TYPE } from '../../app/config/error.constants';
import { HttpErrorResponse } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import { NonceService } from '../nonce.service';
import { UserValidationService } from '../user-validation.service';
import { urlList } from '../utils/urlList';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit, AfterViewInit {
  @ViewChild('username', { static: false })
  username!: ElementRef;
  formBased = true;
  masterUrl = environment.master_url;
  authenticationError = false;
  roles: any;
  pages: any;
  loginForm = this.fb.group({
    username: [null, [Validators.required]],
    cred: [null, [Validators.required]],
    rememberMe: [false],
  });
  // variables for register
  loggedIn = false;
  doNotMatch = false;
  error = false;
  errorEmailExists = false;
  errorUserExists = false;
  success = false;
  csrfToken: string;
  constructor(
    private authService: MsalService,
    private accountService: AccountService,
    private loginService: LoginService,
    private router: Router,
    private fb: FormBuilder,
    private msalBroadcastService: MsalBroadcastService,
    private registerService: RegisterService,
    public nonceService:NonceService,
    public validationService: UserValidationService
  ) {
    this.csrfToken = this.nonceService.getNonce();
  }

  ngOnInit(): void {
    this.loginService.getConfigApiList(this.masterUrl).subscribe((res: any) => {
      localStorage.setItem('res', JSON.stringify(res));
    });

    if (environment.isSSO) {
      this.formBased = false;
      const accounts = this.authService.instance.getAllAccounts();
      if (accounts.length > 0) {
        console.log('inside if contn. of login cpmt');
        this.loginBySSO();
      } else {
        console.log('Msal redirect happening from login oninit');
        this.authService.loginRedirect();
      }
      const mail = localStorage.getItem('mail');
      if (mail) {
        console.log('executing in login component based on local strg,just checking');
        this.register();
      }
    } else {
      // if already authenticated then navigate to home page
      this.accountService.identity().subscribe(() => {
        if (this.accountService.isAuthenticated()) {
          this.router.navigate(['']);
        }
      });
    }
  }

  /**
   * @description This method is called after the view has been initialized. It focuses on the username input field if it exists.
   */
  ngAfterViewInit(): void {
    if (this.username) {
      this.username.nativeElement.focus();
    }
  }

  /**
   * @description This method is called when the login button is clicked. It retrieves the values from the form and calls the login service to authenticate the user.
   */
  login(): void {
    const credentials = {
      username: this.loginForm.get('username')!.value,
      cred: this.loginForm.get('cred')!.value,
      rememberMe: this.loginForm.get('rememberMe')!.value,
    };

    this.loginService.login(credentials).subscribe(
      (res: any) => {
        this.authenticationError = false;
        if (!this.router.getCurrentNavigation()) {
          // There were no routing during login (eg from navigationToStoredUrl)
          this.router.navigate(['responsible-ui']);
        }
        console.log('login response', res.login);
        console.log('login response', res.authorities);

        localStorage.setItem('role', JSON.stringify(res.authorities[0]));
        localStorage.setItem('userid', JSON.stringify(res.login));

        this.roles = res.authorities;
        console.log('ROLES FROM LOCAL STORAGE' + this.roles);

        this.loginService.getPages(this.roles).subscribe((pages: any) => {
          this.pages = pages;
          console.log(this.pages);
        });
      },
      () => (this.authenticationError = true)
    );
  }

  /**
   * @description This method is called when the register button is clicked. It retrieves the email from local storage and calls the register service to save the user.
   */
  register(): void {
    console.log('register from login');
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
       ()=> this.loginBySSO()

      );
    }
  }

  /**
   * @description This method processes the error response from the register service. It checks the status code and sets the appropriate error flags.
   * @param {HttpErrorResponse} response - The error response from the register service.
   */
  private processError(response: HttpErrorResponse): void {
    if (response.status === 400 && response.error.type === LOGIN_ALREADY_USED_TYPE) {
      this.errorUserExists = true;
    } else if (response.status === 400 && response.error.type === EMAIL_ALREADY_USED_TYPE) {
      this.errorEmailExists = true;
    } else {
      this.error = true;
    }
  }

  /**
 * @description This method handles the Single Sign-On (SSO) login process.
 * It retrieves the user's email from local storage, sets it as the username, 
 * and sends the credentials to the login service for authentication.
 * On successful login, it stores the user's role and ID in local storage, 
 * retrieves the user's accessible pages, and sets the active account for MSAL.
 */
  loginBySSO(): void {
    console.log('in login of logincomponent');
    const mail = localStorage.getItem('mail') || '{}';
    localStorage.setItem('userName', mail);

    const credentials = {
      username: mail,
      cred: urlList.user_cred,
      rememberMe: true,
    };

    this.loginService.login(credentials).subscribe(
      (res: any) => {
        this.authenticationError = false;
        if (!this.router.getCurrentNavigation()) {
          this.router.navigate(['responsible-ui']);
        }
        console.log('login response', res.login);
        console.log('login response', res.authorities[0]);

        localStorage.setItem('role', JSON.stringify(res.authorities[0]));
        localStorage.setItem('userid', JSON.stringify(res.login));
        this.roles = res.authorities;
        console.log('ROLES FROM LOCAL STORAGE' + this.roles);

        this.loginService.getPages(this.roles).subscribe((pages: any) => {
          this.pages = pages;
             console.log(this.pages)
      },
      () => (this.authenticationError = true)
    );
  })
}
}