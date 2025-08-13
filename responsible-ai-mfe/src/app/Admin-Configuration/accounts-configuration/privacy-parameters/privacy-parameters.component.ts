/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Input, ViewChild } from '@angular/core';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { UserValidationService } from 'src/app/services/user-validation.service';

@Component({
  selector: 'app-privacy-parameters',
  templateUrl: './privacy-parameters.component.html',
  styleUrls: ['./privacy-parameters.component.css']
})
export class PrivacyParametersComponent {

  @Input() parPortfolio!: any;
  @Input() parAccount!: any;

  constructor (public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog, private validationService:UserValidationService){
    
  }


  listReconList: any=[];
  selectedReclist: any = [];

  Admin_SetPrivacyParameter = "" 
  admin_list_rec_get_list = ""



  @ViewChild('select1') select1!: MatSelect;

// SCREEN TWO ADD DATA  
//--------------VARIABLES-----------SECURITY

allSelected1: any;
listShowlist1 = new Set();
allSelectedInput = false;
event1: any;
c1: boolean = false;

// select 1- Toggles all selections for the dropdown
toggleAllSelection1(event: any) {
  this.event1 = event;
  this.c1 = event.checked;
  this.allSelected1 = !this.allSelected1;
  if (this.allSelected1) {
    this.select1.options.forEach((item: MatOption) => {
      item.select();
      this.listShowlist1.add(item.value);
      const element = document.querySelector('[role="listbox"]');
      if (element instanceof HTMLElement) {
        element.style.display = 'none';
      }
      this.select1.close();
    });
  } else {
    this.select1.options.forEach((item: MatOption) => {
      item.deselect();

      this.listShowlist1.delete(item.value);
    });
  }
}

// Updates the selection status for the dropdown
selectRecognizertype() {
  let newStatus = true;
  this.select1.options.forEach((item: MatOption) => {
    if (!item.selected) {
      newStatus = false;
      this.allSelected1 = false;
      this.listShowlist1.delete(item.value);
    } else {
      this.listShowlist1.add(item.value);
    }
  });
  this.allSelectedInput = newStatus;
}

// Submits the privacy parameters to the server
  submit() {
    // console.log(this.AccountForm.value);
    const header = {
      portfolio: this.parPortfolio,
      account: this.parAccount,
      // ptrnList: ptrnlist,
      dataGrpList: this.selectedReclist,
      
    }
    this.setPrivacyParameter(header)
  }

  // Sends the privacy parameters to the server
  setPrivacyParameter(header: any) {
    this.https.post(this.Admin_SetPrivacyParameter, header).subscribe
        ((res: any) => {
          console.log("data sent to database" + res.status)
          if (res.status === "True") {
        
            const message = "Recognizer Added Successfully"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass: ['le-u-bg-black'],
            });
            // this.getAccountMasterEntryList()
            // this.getAllAccountData();
          } else if (res.status === "False") {
            const message = "Mapping already exists for this account "

            const action = "Close"
            // this.getAccountMasterEntryList()
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass: ['le-u-bg-black'],
            });
          }
          // this.AccountForm.reset(this.initialValues);
          // this.getAccountMasterEntryList()

        }, error => {
          // You can access status:
          console.log(error.status);
            // console.log(error.error.detail)
            console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            // this.getAccountMasterEntryList()
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black']
            });
        })
  }

  // Fetches the list of recognizers from the server
  getadmin_list_rec_get_list(){
    this.https.get(this.admin_list_rec_get_list).subscribe
    ((res: any) => {
      console.log("res",res)
      this.listReconList = res.RecogList
    }, error => {
      // You can access status:
      console.log(error.status);
        // console.log(error.error.detail)
        console.log(error)
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
  
      
    })
  }

  // Initializes the component and sets up API lists
  ngOnInit(): void {
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    // this.getAccountMasterEntryList()
    // this.getAllAccountData()
    this.getadmin_list_rec_get_list()
    console.log("oninit");
  }
  userId: any
  // Retrieves the logged-in user from local storage
  getLogedInUser() {
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.userId = x ;
        console.log(" userId", this.userId)
      }
      return this.userId;
    }
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if(res != null){
        return ip_port = JSON.parse(res)
      }
    }
  }

  // Sets the API list URLs
  setApilist(ip_port: any) {
    this.admin_list_rec_get_list = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrplist       //+ environment.admin_list_rec_get_list
    
    this.Admin_SetPrivacyParameter = ip_port.result.Admin + ip_port.result.setPrivacyParameter    // setPriavy Parmenetre
    
  }

}
