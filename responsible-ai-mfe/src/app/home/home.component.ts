/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Renderer2 } from '@angular/core';
import { HomeService } from './home.service';
import { RoleManagerService } from '../services/role-maganer.service';
import { urlList } from '../urlList';
import { MatDialog } from '@angular/material/dialog';
import { TermsAndConditionsComponent } from '../terms-and-conditions/terms-and-conditions.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent {
  master_url = urlList.masterurl;
  authorityAPI = urlList.authorityAPI;
  pages: any;
  showSidebar = false;
  showComponent!: string;
  userId = "";
  apiList: any;
  localUrlList: any;

  constructor(
    private elementRef: ElementRef,
    private renderer: Renderer2,
    public https: HttpClient,
    private homeService: HomeService,
    public roleService: RoleManagerService,
    public dialog: MatDialog,
    public routes: Router
  ) {}

  // Toggles the visibility of components based on the selected tab
  toggleComponents(tabValue: any) {
    this.showComponent = tabValue;
    if (this.showSidebar) {
      this.renderer.removeClass(document.body, 'overflow-hidden');
    }
    this.showSidebar = false;
  }

    // Opens the terms and conditions dialog
  openTermsAndConditions(event: Event): void {
    event.preventDefault();
    let userId = this.getLogedInUser();
    this.dialog.open(TermsAndConditionsComponent, {
      data: { userId: userId,
              setUserConsentUrl: this.localUrlList.setUserConsent,
              getUserConsentUrl: this.localUrlList.getUserConsent
       },
      disableClose: true
    });
  }

  // Toggles the visibility of the sidebar
  toggleSidebar() {
    if (this.showSidebar) {
      this.renderer.removeClass(document.body, 'overflow-hidden');
    } else {
      this.renderer.addClass(document.body, 'overflow-hidden');
    }
    this.showSidebar = !this.showSidebar;
  }

  // Closes the sidebar if it is open
  closeSidebar() {
    if (this.showSidebar) {
      this.renderer.removeClass(document.body, 'overflow-hidden');
    }
    this.showSidebar = false;
  }

  // async ngOnInit() {
  //   await this.loadConfig();
  //   this.initializeComponent();
  //   let loggedInUser = this.getLogedInUser();
  //   this.setUrlList(this.apiList);
  //   this.getUserConsent(loggedInUser);
  // }

  // Initializes the component and sets up API configurations
  ngOnInit() {
    if (this.roleService.getLocalStoreUserRole() === 'ROLE_ML') {
      this.showComponent = "workbench";
    }
    else if (this.roleService.getLocalStoreUserRole() == "ROLE_EMPTY") {
      this.showComponent = "newUser";
    }
    else {
      this.showComponent = "workbench";
    }
    console.log(this.showComponent, "showComponent")
    this.homeService.getConfigApiList(this.master_url).subscribe
      ((res: any) => {
        localStorage.setItem("res", JSON.stringify(res))
      })

    // let loggedInUser = this.getLogedInUser();
    // this.setUrlList(this.apiList);
    // this.getUserConsent(loggedInUser);
  }

  // Fetches user consent status from the server
  getUserConsent(userId: string) {
    // console.log("the local url", this.localUrlList.getUserConsent);
    const url = `${this.localUrlList.getUserConsent}${userId}`;
    this.https.get(url, { headers: { 'accept': 'application/json' } }).subscribe(
      (response: any) => {
        console.log('User consent:', response);
        if (response.userConsentStatus == true) {
          console.log('User has given consent');
        } else {
          console.log('User has not given consent');
          this.openTermsAndConditions(new Event('click'));
        }
      },
      (error) => {
        console.error('Error fetching user consent:', error);
      }
    );
  }

  // Loads the configuration from the server
  async loadConfig() {
    return new Promise<void>((resolve, reject) => {
      this.homeService.getConfigApiList(this.master_url).subscribe(
        (res: any) => {
          this.apiList = res;
          localStorage.setItem('res', JSON.stringify(res));
          resolve();
        },
        (error) => {
          console.error('Error loading config:', error);
          reject(error);
        }
      );
    });
  }

   // Initializes the component based on the user role
  initializeComponent() {
    if (this.roleService.getLocalStoreUserRole() === 'ROLE_ML') {
      this.showComponent = 'workbench';
    } else if (this.roleService.getLocalStoreUserRole() == 'ROLE_EMPTY') {
      this.showComponent = 'newUser';
    } else {
      this.showComponent = 'workbench';
    }
    console.log(this.showComponent, 'showComponent');
  }

   // Retrieves the logged-in user's ID from local storage
  getLogedInUser() {
    let role = localStorage.getItem('role');
    console.log("role267===", role);

    if (localStorage.getItem("userid") != null) {
      const x = localStorage.getItem("userid");
      if (x != null) {
        this.userId = JSON.parse(x);
        console.log(" userId", this.userId);
        return JSON.parse(x);
      }

      console.log("userId", this.userId);
    }
  }

  // Sets the local URL list for API endpoints
  setUrlList(apiList: any) {
    console.log("apiList", apiList);
    this.localUrlList = {
      getUserConsent: apiList.result.RAI_Backend_URL + apiList.result.RAI_Backend_getUserConsent,
      setUserConsent: apiList.result.RAI_Backend_URL + apiList.result.RAI_Backend_setUserConsent
    };

    console.log("localUrlList initialized", this.localUrlList);
  }
}