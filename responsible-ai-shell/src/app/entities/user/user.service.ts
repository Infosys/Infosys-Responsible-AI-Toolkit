/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApplicationConfigService } from '../../core/config/application-config.service';
import { createRequestOption } from '../../core/request/request-util';
import { isPresent } from '../../core/util/operators';
import { Pagination } from '../../core/request/request.model';
import { IUser, getUserIdentifier } from './user.model';
import { Account } from '../../core/auth/account.model';
import { environment } from 'src/environments/environment';
import { urlList } from 'src/app/utils/urlList';

@Injectable({ providedIn: 'root' })
export class UserService {
  private resourceUrl = this.applicationConfigService.getEndpointFor('api/users');

  constructor(private http: HttpClient, private applicationConfigService: ApplicationConfigService) {}

  /**
   * @param req - The request object containing pagination and sorting information
   * @returns An observable of HttpResponse containing an array of IUser objects
   * This method is used to query the user data from the server with pagination and sorting options.
   */
  query(req?: Pagination): Observable<HttpResponse<IUser[]>> {
    const options = createRequestOption(req);
    return this.http.get<IUser[]>(this.resourceUrl, { params: options, observe: 'response' });
  }

  /**
   * @description This method is used to add a user to the collection if it is not already present in the collection.
   * @param userCollection - The collection of users to check against
   * @param user - The user to check for existence in the collection
   * @param usersToCheck 
   * @returns 
   */
  addUserToCollectionIfMissing(userCollection: IUser[], ...usersToCheck: (IUser | null | undefined)[]): IUser[] {
    const users: IUser[] = usersToCheck.filter(isPresent);
    if (users.length > 0) {
      const userCollectionIdentifiers = userCollection.map(userItem => getUserIdentifier(userItem)!);
      const usersToAdd = users.filter(userItem => {
        const userIdentifier = getUserIdentifier(userItem);
        if (userIdentifier == null || userCollectionIdentifiers.includes(userIdentifier)) {
          return false;
        }
        userCollectionIdentifiers.push(userIdentifier);
        return true;
      });
      return [...usersToAdd, ...userCollection];
    }
    return userCollection;
  }

  /**
   * @description This method is used to get the user information from the server.
   * @returns An observable of Account object containing the user information
   */
  getUser(): Observable<Account> {
    return this.http.get<Account>(urlList.server_api_url+ '/api/account');
  }
}
