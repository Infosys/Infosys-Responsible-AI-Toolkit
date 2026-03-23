/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable, isDevMode } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { AccountService } from '../../../app/core/auth/account.service';
import { StateStorageService } from './state-storage.service';
import { LoginService } from '../../../app/login/login.service';

@Injectable({ providedIn: 'root' })
export class UserRouteAccessService implements CanActivate {
  user: any;
  
  authenticationError = false;


  constructor(private router: Router, 
    private accountService: AccountService, 
    private stateStorageService: StateStorageService,
    private loginService: LoginService) {}

  /**
   * @description This method is used to check if the user has access to the route or not.
   * @param route
   * @param state 
   * @returns 
   */
  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
    if (route.queryParams) {
      console.log("YESS:",route);
      this.user = route.queryParams['user'];
    }
    if(this.user){
      sessionStorage.setItem('user',this.user);
    }



    return this.accountService.identity().pipe(
      map(account => {
        if (account) {
          const authorities = route.data['authorities'];

          if (!authorities || authorities.length === 0 || this.accountService.hasAnyAuthority(authorities)) {
            return true;
          }

          if (isDevMode()) {
            console.error('User has not any of required authorities: ', authorities);
          }
          this.router.navigate(['accessdenied']);
          return false;
        }

        this.stateStorageService.storeUrl(state.url);
        return false;
      })
    );
  }
}

