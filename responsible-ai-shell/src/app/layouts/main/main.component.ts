/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { Router, ActivatedRouteSnapshot, NavigationEnd, NavigationError, NavigationStart } from '@angular/router';
import { AccountService } from '../../../app/core/auth/account.service';
// Generated Import Start
// Generated Import End
// Custom Code Start
// Custom Code End

@Component({
  selector: 'jhi-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.scss'],
})
export class MainComponent implements OnInit {
  public currentRoutePath = '/';
  public layoutRegExpList: any = ['^\\/$'];
  public layoutNumber = 0;
  // Generated Data Start
  // Generated Data End
  // Custom Code Start
  // Custom Code End

  constructor(
    private accountService: AccountService,
    private titleService: Title,
    private router: Router
  ) // Generated Required Services Start
  // Generated Required Services End
  // Custom Code Start
  // Custom Code End
  {}

  ngOnInit(): void {
    this.accountService.identity().subscribe();
    this.router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        this.currentRoutePath = event.url;
        for (let index = 0; index < this.layoutRegExpList.length; index++) {
          if (this.currentRoutePath.search(this.layoutRegExpList[index]) >= 0) {
            this.layoutNumber = index;
            break;
          }
        }
      }
      if (event instanceof NavigationEnd) {
        this.updateTitle();
      }
      if (event instanceof NavigationError && event.error.status === 404) {
        this.router.navigate(['/404']);
      }
    });

    // Generated Load Data Function Calls Start
    // Generated Load Data Function Calls End
    // Custom Code Start
    // Custom Code End
  }

  /**
   * @description This function is used to get the page title from the route snapshot.
   * @param routeSnapshot The route snapshot to get the page title from.
   * @returns The page title.
   */
  private getPageTitle(routeSnapshot: ActivatedRouteSnapshot): string {
    const title: string = routeSnapshot.data['pageTitle'] ?? '';
    if (routeSnapshot.firstChild) {
      return this.getPageTitle(routeSnapshot.firstChild) || title;
    }
    return title;
  }

  /**
   * @description This function is used to update the page title.
   */
  private updateTitle(): void {
    let pageTitle = this.getPageTitle(this.router.routerState.snapshot.root);
    if (!pageTitle) {
      pageTitle = 'RAI';
    }
    this.titleService.setTitle(pageTitle);
  }
  // Generated Load Data Functions Start
  // Generated Load Data Functions End
  // Custom Code Start
  // Custom Code End
}
