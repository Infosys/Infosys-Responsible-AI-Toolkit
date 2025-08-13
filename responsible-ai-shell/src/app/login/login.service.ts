/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of, forkJoin } from 'rxjs';
import { catchError, map, mergeMap, tap } from 'rxjs/operators';

import { Account } from '../../app/core/auth/account.model';
import { AccountService } from '../../app/core/auth/account.service';
import { AuthServerProvider } from '../../app/core/auth/auth-jwt.service';
import { Login } from './login.model';
import { urlList } from '../utils/urlList';

@Injectable({ providedIn: 'root' })
export class LoginService {
  public authorityAPI = urlList.server_api_url + '/pageauthoritynew';
  public logOut = urlList.server_api_url + '/logout';
  pages: any;

  constructor(
    public http: HttpClient,
    private accountService: AccountService,
    private authServerProvider: AuthServerProvider
  ) {}

  public url: any;

  /**
   * @method loginUrls
   * @returns {string}
   * @description This method is used to get the login URL from the urlList object.
   */
  loginUrls() {
    console.log('hi india', this.url);
    return this.url;
  }

  /**
   * @method setLoginUrl
   * @param {string} url
   * @description This method is used to set the login URL in the urlList object.
   */
  getConfigApiList(url: any): Observable<any> {
    return this.http.get<any>(url);
  }

  /**
   * @param credentials - The credentials object containing the username and pswrd.
   * @description This method is used to login the user. It calls the authServerProvider's login method and then retrieves the user's identity.
   * @returns 
   */
  login(credentials: Login): Observable<Account | null> {
    return this.authServerProvider.login(credentials).pipe(
      mergeMap(() => this.accountService.identity(true))
    );
  }

  /**
   * @param {string} username - The username of the user to be logged out.
   * @returns {Observable<void>}
   * @description This method is used to logout the user. It calls the authServerProvider's logout method and then retrieves the user's identity.
   */
  logout(): Observable<void> {
    const userName = this.getUserName();
    console.log('userName', userName);
    return this.authServerProvider.logout().pipe(
      tap(() => this.accountService.authenticate(null)),
      mergeMap(() => this.http.get<any>(`${this.logOut}?username=${userName}`)),
      tap({
        next: response => {
          console.log('Logout successful:', response);
        },
        error: error => {
          console.error('Logout error:', error);
        }
      })
    );
  }

  /**
   * @method getUserName
   * @returns {string | null}
   * @description This method retrieves the username from local storage.
   */
  getUserName(): string | null {
    return localStorage.getItem('userid');
  }

  /**
   * @method getPages
   * @param {string[]} roles - The roles of the user.
   * @returns {Observable<string[]>}
   * @description This method retrieves the pages for the given roles. It makes multiple HTTP requests and combines the results.
   */
  getPages(roles: string[]): Observable<string[]> {
    const requests = roles.map(role =>
      this.http.get<any>(`${this.authorityAPI}?role=${role}`).pipe(
        map(response => {
          localStorage.setItem('pages', JSON.stringify(response.pages));
          return Object.keys(response.pages);
        }),
        catchError(error => {
          console.error(`Error retrieving pages for role ${role}:`, error);
          return of([]);
        })
      )
    );

    return forkJoin(requests).pipe(
      map(pagesArray => {
        const combinedPages = pagesArray.reduce<string[]>((accumulator, pages) => accumulator.concat(pages), []);
        return combinedPages;
      }),
      catchError(error => {
        console.error('Error combining pages:', error);
        return of([]);
      })
    );
  }
}