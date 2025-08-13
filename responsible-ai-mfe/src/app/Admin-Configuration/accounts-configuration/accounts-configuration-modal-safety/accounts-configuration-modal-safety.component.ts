/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Inject } from '@angular/core';
import { FormGroup, Validators, FormControl, UntypedFormBuilder } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-accounts-configuration-modal-safety',
  templateUrl: './accounts-configuration-modal-safety.component.html',
  styleUrls: ['./accounts-configuration-modal-safety.component.css']
})
export class AccountsConfigurationModalSafetyComponent  {
  constructor(public dialogRef: MatDialogRef<AccountsConfigurationModalSafetyComponent>,  public _snackBar: MatSnackBar,private _fb: UntypedFormBuilder, public https: HttpClient,public nonceService:NonceService
    , @Inject(MAT_DIALOG_DATA) public data: { id: any }) { 
      // this.fromCreation();
      this.fromCreation2();
      // this.pagingConfig = {
      //   itemsPerPage: this.itemsPerPage,
      //   currentPage: this.currentPage,
      //   totalItems: this.totalItems
      // }
    }


    edited: any = false;
  autoTicks = false;
  disabled = false;
  // invert = false;
  max = 1;
  min = 0;
  showTicks = true;
  step = 0.01;
  thumbLabel = true;

    

    // pagingConfig: PagingConfig = {} as PagingConfig;
    // currentPage: number = 1;
    // itemsPerPage: number = 5;
    // totalItems: number = 0


  dataSource1: any = []
  closeDialog() {
    this.dialogRef.close();
  }

  // Initializes the component and sets up API lists
  ngOnInit(): void {
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    console.log("oninit");
    // console.log(this.data);
    this.getSafetyFormEntity();

   }

   // Retrieves the logged-in user from local storage
  userId: any
  getLogedInUser() {
    if (localStorage.getItem("userid") != null) {
      const x = localStorage.getItem("userid")
      if (x != null) {

        this.userId = JSON.parse(x)
        console.log(" userId", this.userId)
        return JSON.parse(x)
      }

      console.log("userId", this.userId)
    }
  }

   // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        return ip_port = JSON.parse(x)
      }
    }
  }
  Admin_SetSafetyParamter=""
  Admin_SafetyUpdate=""
  Admin_AccSafetyListAccountWise=""
  // Sets the API list URLs
  setApilist(ip_port: any) {
    this.Admin_SetSafetyParamter = ip_port.result.Admin + ip_port.result.setSafetyParameter
    this.Admin_SafetyUpdate = ip_port.result.Admin + ip_port.result.Admin_SafetyUpdate 
    this.Admin_AccSafetyListAccountWise = ip_port.result.Admin + ip_port.result.Admin_AccSafetyListAccountWise  
  }

   submit() {

   }

   safetyForm!: FormGroup;
   SafetyFormUpdateEntity!: FormGroup;
   // Initializes the safety form
   fromCreation() {
    this.safetyForm = this._fb.group({
      xv: [5, Validators.required],
      drawingsThreshold: new FormControl(50, [Validators.required]),
      hentaiThreshold: new FormControl(25, [Validators.required]),
      neutralThreshold: new FormControl(50, [Validators.required]),
      pornThreshold: new FormControl(25, [Validators.required]),
      sexyThreshold: new FormControl(25, [Validators.required]),
    });
  }

  // Initializes the safety update form
  fromCreation2(){
    this.SafetyFormUpdateEntity = new FormGroup({
      drawingsThreshold: new FormControl(0.5, [Validators.required]),
      hentaiThreshold: new FormControl(0.25, [Validators.required]),
      neutralThreshold: new FormControl(0.5, [Validators.required]),
      pornThreshold: new FormControl(0.25, [Validators.required]),
      sexyThreshold: new FormControl(0.25, [Validators.required]),
    });
  }

  // Updates safety parameters
  UpdateSafePars(v: any, par: any) {
    // this.showSpinner1 = true

    console.log("value of e", v, "valueof x", par)
    let headers = {
      "accMasterId": this.data.id,
      "parameters": par,
      "value": v
    }
    this.https.patch(this.Admin_SafetyUpdate, headers).subscribe
      ((res: any) => {
        // this.showSpinner1 = false
        console.log("value of res", res)

        const message = par + " value Updated Successfully"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }


        , error => {
          // You can access status:
          console.log(error.status);
          if (error.status == 430) {
            // this.showSpinner1 = false;
            // this.edited = false;
            console.log(error.error.detail)
            console.log(error)
            const message = error.error.detail
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
          } else {
            // this.showSpinner1 = false;
            // this.edited = false;
            // console.log(error.error.detail)
            console.log(error)
            const message = "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });

          }
        })
  }

  // Updates the safety form entity
  updateSafetyFormEntity(){
    console.log(this.SafetyFormUpdateEntity.value);
    // this.UpdateSafePars(this.SafetyFormUpdateEntity.value,this.data.id);
  }
   xv:any;
   isLoading: boolean = true;
   isDataEmpty: boolean = false;
    // Fetches safety form entity data
   getSafetyFormEntity() {
    let payload = {
      accMasterId: this.data.id
    };
    this.https.post(this.Admin_AccSafetyListAccountWise, payload).subscribe(
      (response: any) => {
        console.log(response);
        this.isLoading = false;

        if (!response || Object.keys(response).length === 0 || response.dataList.length === 0) {
          this.isDataEmpty = true;
          this._snackBar.open('Value is not set. Create a mapping first.', 'Close', {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          this.isDataEmpty = false;
          // this.safetyValues = response;
          let safetygetvalues = response;
      this.xv = response;
      this.SafetyFormUpdateEntity.setValue({
        drawingsThreshold: safetygetvalues.drawings,
        hentaiThreshold: safetygetvalues.hentai,
        neutralThreshold: safetygetvalues.neutral,
        pornThreshold: safetygetvalues.porn,
        sexyThreshold: safetygetvalues.sexy,
      })
      this.SafetyFormUpdateEntity.patchValue(response);
        }
      },
      (error) => {
        console.log(error.status);
        this.isLoading = false;
        const message = (error.error && (error.error.detail || error.error.message)) || 'The Api has failed';
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }
}

