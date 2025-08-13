/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Input } from '@angular/core';
import { FormControl, FormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-safety-parameters',
  templateUrl: './safety-parameters.component.html',
  styleUrls: ['./safety-parameters.component.css']
})
export class SafetyParametersComponent {
  constructor(private _fb: UntypedFormBuilder, public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog,public nonceService:NonceService) {
    this.fromCreation();
  }

  @Input() parPortfolio!: any;
  @Input() parAccount!: any;

  userId:any
  safetyForm!: FormGroup;
  // xv: number = 10;
  tempValue: number = 10;

  // Submits the safety parameters
  submit() {
    console.log("submit");
    console.log("submit", this.safetyForm.value);
    const safetyParameterPayload = {
      "portfolio": this.parPortfolio,
      "account": this.parAccount,
      "drawings": this.safetyForm.value.drawingsThreshold / 100,
      "hentai": this.safetyForm.value.hentaiThreshold / 100,
      "neutral": this.safetyForm.value.neutralThreshold / 100,
      "porn": this.safetyForm.value.pornThreshold / 100,
      "sexy": this.safetyForm.value.sexyThreshold / 100
    }

    this.safetySubmit(safetyParameterPayload)

  }

// Creates the safety form
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

  // Sends the safety parameters to the server
  safetySubmit(payload: any) {
    this.https.post(this.Admin_SetSafetyParamter, payload).subscribe
      ((res: any) => {
        if (res.status === "Success") {
          const message = "Safety Parameter Set Successfully"
          const action = "Close"
          // this.getAccountMasterEntryList();
          this._snackBar.open(message, action, {
            duration: 3000,
            panelClass: ['le-u-bg-black'],
          });
        } else if (res.status === "False") {
          const message = "Mapping already exists for the account "
          // this.getAccountMasterEntryList();
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            panelClass: ['le-u-bg-black'],
          });
        }


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
          panelClass: ['le-u-bg-black']
        });
      })
  }

  // Initializes the component and sets up API configurations
  ngOnInit(): void {
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    console.log("oninit");
  }

  // Retrieves the logged-in user from local storage
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
  setApilist(ip_port: any) {
    this.Admin_SetSafetyParamter = ip_port.result.Admin + ip_port.result.setSafetyParameter
  }

}
