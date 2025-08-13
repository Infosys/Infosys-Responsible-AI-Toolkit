/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PageRoleAccessService {
  accessiblePages : any ;
  constructor(private https: HttpClient) { }

  // getAccessiblePages(url:any, selectedRole:any): Observable<any> {
  //   console.log("URL", url)
  //   console.log("Selected Role", selectedRole)
  //   let xyz = this.http.get<any>(url, selectedRole);
  //   console.log("xyz", xyz)
  //   return xyz;
  // }
  getAccessiblePages(url: string, selectedRole: any): Observable<any> {
    // Add the selectedRole as a query parameter
    // url = "http://localhost:30019/v1/rai/backend/pageauthoritynew"
    const params = new HttpParams().set('role', selectedRole);
    return this.https.get<any>(url, { params });
  }

  // updateRoleAccess(role: string, pages: any): void {
  //   const url = "http://localhost:30019/v1/rai/backend/pageauthoritynewupdate";
  //   const data = {
  //     role: role,
  //     pages: pages
  //   };

  //   this.http.patch(url, data, {
  //     headers: {
  //       'Content-Type': 'application/json'
  //     }
  //   }).subscribe(
  //     response => {
  //       console.log('Data sent successfully', response);
  //     },
  //     error => {
  //       console.error('Error sending data', error);
  //     }
  //   );
  // }

  updateRoleAccess(role: string, pages: any, url:any): Observable<any> {
    //  url = "http://localhost:30019/v1/rai/backend/pageauthoritynewupdate";
    const data = {
      role: role,
      pages: pages
    };

    return this.https.patch(url, data, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
}
