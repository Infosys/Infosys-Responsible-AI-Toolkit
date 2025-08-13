/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, Input } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { UseCaseServiceService } from '../use-case-parent/use-case-service.service';
// import { Input } from 'hammerjs';

@Component({
  selector: 'app-use-case-report',
  templateUrl: './use-case-report.component.html',
  styleUrls: ['./use-case-report.component.css']
})
export class UseCaseReportComponent {
  userId: any;
  Ques_Risk_Dashboard: any;
  dataSource: any = [];
  table:any
  useCaseReport:any
  useCasePage=false

  @Input() useCaseName: any;

  constructor(private _snackBar: MatSnackBar,
    private _formBuilder: FormBuilder,
    private cdr: ChangeDetectorRef,
    public https: HttpClient, private router: Router,
    private useCaseService:UseCaseServiceService) {}

  getAllBatches(){

  }

   // Submits the request to fetch the risk dashboard data
  onSubmit() {
    console.log("the user id ", this.userId)
    // this.https.get(this.getRiskDash+this.userId).subscribe
    // this.useCaseService.getMessage.subscribe(msg => this.UseCaseName = msg)
    // this.https.get(this.Ques_Risk_Dashboard + '"' + this.userId + '"/'+this.UseCaseName).subscribe
    this.https.get(this.Ques_Risk_Dashboard + '"' + this.userId + '"/'+this.useCaseName).subscribe
      ((res: any) => {

        if (res == "No Record Found...") {
          this.dataSource = []
          this.table = false

          const message = "No record found ..."
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            panelClass: ['le-u-bg-black'],
          });



        } else {
          this.dataSource = res
          this.table = true;
        }

        // this.result = res
        // this.dataSource = res
        // this.table = true;

        // this.showSpinner1=false;
        // this.edited = true
        console.log("result====", res)
        // console.log("result1111====",res[0].DimensionName)
        this.cdr.detectChanges();



      }, error => {
  

        // this.showSpinner1 = false;

        // console.log(error.error.detail)
        console.log(error)
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          panelClass:['le-u-bg-black'],
        });

    }
      )
    this.cdr.detectChanges();
  }

  // Sets the API endpoints for the component
  setApilist(ip_port: any) {
    
 this.Ques_Risk_Dashboard = ip_port.result.Questionnaire + ip_port.result.Ques_Risk_Dashboard
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

  // Navigates to the next screen
  currentScreen:any;
  nextScreen() {
    if (this.currentScreen < 3 ) {
     
      this.currentScreen++;
      this.useCaseService.setMessage(this.currentScreen)

      console.log("this.cureentscrenn====",this.currentScreen)
      // console.log("this.aicanvas value====",this.raiCanvasForm.value)
    }
  }

  // Navigates to the previous screen
previousScreen() {
  if (this.currentScreen > 1) {
    this.currentScreen--;
    this.useCaseService.setMessage(this.currentScreen)
  }
}

// Navigates to the main use case page
useCaseMainPage(){
  this.useCasePage=true
  this.useCaseService.getGenerateReport.subscribe(msg => this.useCaseReport = msg)
  console.log("this.usecaseReport139=====",this.useCaseReport)
}

 // Initializes the component and sets up API endpoints
  ngOnInit(){
    // this.qutionnaireForm=this._formBuilder.group({})
    // console.log("cureent===",this.currentScreen)
    // this.useCaseService.getcurrentScreen.subscribe(msg => this.currentScreen = msg)
    // console.log("cureent===",this.currentScreen)
    let ip_port: any

  let user = this.getLogedInUser()
  console.log("useCaseName124=======",this.useCaseName)
  this.useCaseService.getGenerateReport.subscribe(msg => this.useCaseReport = msg)
  console.log("useCaseReport=======",this.useCaseReport)
  ip_port = this.getLocalStoreApi()
  this.setApilist(ip_port)
  // this.getDetails()
  this.onSubmit()
  }


}
