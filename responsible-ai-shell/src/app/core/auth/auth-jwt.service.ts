/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { LocalStorageService, SessionStorageService } from 'ngx-webstorage';

import { ApplicationConfigService } from '../config/application-config.service';
import { Login } from '../../../app/login/login.model';
import { urlList } from '../../utils/urlList';

type JwtToken = {
  id_token: string;
};

@Injectable({ providedIn: 'root' })
export class AuthServerProvider {
  public logOut =  urlList.server_api_url + '/logout';
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private sessionStorageService: SessionStorageService,
    private applicationConfigService: ApplicationConfigService
  ) {}

  /**
   * @description This method is used to check if the user is logged in or not.
   * @returns boolean
   */
  getToken(): string {
    const tokenInLocalStorage: string | null = this.localStorageService.retrieve('authenticationToken');
    const tokenInSessionStorage: string | null = this.sessionStorageService.retrieve('authenticationToken');
    return tokenInLocalStorage ?? tokenInSessionStorage ?? '';
  }

  /**
   * 
   * @description This method is used to login the user.
   * @param credentials This is the credentials object which contains the username and pswrd.
   * @returns Observable<void>
   */
  login(credentials: Login): Observable<void> {
    console.log("URL::",urlList.server_api_url)
    return this.http
    .post<JwtToken>(urlList.server_api_url + '/authenticate', credentials)
      .pipe(map(response => this.authenticateSuccess(response, credentials.rememberMe)));
  }

  /**
   * @description This method is used to logout the user.
   * @returns Observable<void>
   */
  logout(): Observable<void> {
    let userName = this.getUserName();
    this.localStorageService.clear('authenticationToken');
    this.sessionStorageService.clear('authenticationToken');
    return this.http.get<any>(`${this.logOut}?username=${userName}`)
    // return new Observable(observer => {
    //   this.localStorageService.clear('authenticationToken');
    //   this.sessionStorageService.clear('authenticationToken');
    //   observer.complete();
    // });
  }

  /**
   * @description This method is used to check if the user is logged in or not.
   * @returns boolean
   */
  getUserName(){
    let userName = localStorage.getItem('userid')
    return userName
  }

  /**
   * @description This method is used to check if the user is logged in or not.
   * @returns boolean
   */
  private authenticateSuccess(response: JwtToken, rememberMe: boolean): void {
    const jwt = response.id_token;
    if (rememberMe) {
      this.localStorageService.store('authenticationToken', jwt);
      this.sessionStorageService.clear('authenticationToken');
    } else {
      this.sessionStorageService.store('authenticationToken', jwt);
      this.localStorageService.clear('authenticationToken');
    }
  }
}
