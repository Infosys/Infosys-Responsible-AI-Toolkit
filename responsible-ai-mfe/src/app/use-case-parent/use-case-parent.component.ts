/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { AfterViewInit, ChangeDetectorRef, Component, ViewChild,Input, EventEmitter, Output  } from '@angular/core';
import { UseCaseServiceService } from './use-case-service.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { STEPPER_GLOBAL_OPTIONS } from '@angular/cdk/stepper';
import { MatStepper } from '@angular/material/stepper';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from 'src/environments/environment';
// import { Input } from 'hammerjs';
// import Stepper from 'bs-stepper';
// Replace 'your-package-name' with the actual package name that contains the 'Stepper' class.

@Component({
  selector: 'app-use-case-parent',
  templateUrl: './use-case-parent.component.html',
  styleUrls: ['./use-case-parent.component.css']
})
export class UseCaseParentComponent {
  @Output() closeEvent = new EventEmitter<void>();
  // Emits the close event
  onClose() {
    this.closeEvent.emit();
  }
  // private stepper: Stepper;

  // next() {
  //   this.stepper.next();
  // }
  // @ViewChild('stepper') stepper: any;
  @ViewChild('stepper') stepper!: MatStepper;
  @Input() editFun:any
  childFormGroup!: FormGroup<any>
  childData: any
  raiCanvasData: any
  aiCanvasData: any
  raiCanvasDatDetail: any
  useCaseName: any
  userId: any;
  createUseCase: any;
  aiCanvasSubmitResponse: any;
  raiCanvasSubmitResponse: any;
  useCaseMainPage: boolean = false;
  map: any
  questionPayload: any = []
  submit_Response: any;
  currentPage: any;
  showRaiCanas: any=false;
  // @ViewChild('stepper') stepper1: MatStepper | undefined;

  constructor(private useCaseService: UseCaseServiceService,
    private _formBuilder: FormBuilder,
    private cdr: ChangeDetectorRef,
    public https: HttpClient, private router: Router,
    private _snackBar: MatSnackBar,

  ) {
    this.childFormGroup = new FormGroup({})
    const d = this.useCaseService.getcurrentScreen.subscribe((msg) => (this.currentScreen = msg));
    console.log("data from constructor=======", d)
    console.log("current Screeen from constructor=======", this.currentScreen)
    this.currentScreen=1
  }

    // Updates the child data when it changes
    onChildDataChanged(data: any) {
    this.childData = data

  }

  // Opens a reference document in a new tab
  showNewTab(){
    // const newTabUrl = environment.imagePathurl + '/assets/image/sampleImage1.png';/// Replace with your content URL
    const newTabUrl=environment.imagePathurl + '/assets/Referrence_doc.pdf'
    // Open the content in a new tab using window.open()
    window.open(newTabUrl, '_blank');
  }

  // Retrieves data from the child component
  getDataFromChild() {
    this.useCaseService.getAiCanvas.subscribe(msg => this.aiCanvasData = msg)
    console.log("data from aiCanvasData 43child===", this.aiCanvasData)
    console.log("data from child===", this.childData)
  }

  // Updates the RAI canvas data when it changes
  onRaiCanvasChildDataChanged(data: any) {
    console.log("data from onRaiCanvasChildDataChanged 43child===", data)
    this.raiCanvasDatDetail = data

  }

  // Retrieves RAI canvas data from the child component
  getRaiCanvasDataFromChild() {
    this.useCaseService.getRaiCanvas.subscribe(msg => this.raiCanvasDatDetail = msg)
    console.log("data from raiCanvasDatDetail 43child===", this.raiCanvasDatDetail)

  }

  aiCnavasFormData: FormGroup<any> | undefined;

  firstFormGroup1 = this._formBuilder.group({
    firstCtrl: ['', Validators.required],
  });
  secondFormGroup = this._formBuilder.group({
    secondCtrl: ['', Validators.required],
  });

  thirdFormGroup = this._formBuilder.group({
    thirdCtrl: ['', Validators.required],
  });

  currentScreen: any=1;

   // Navigates to the next screen
  nextScreen() {
    this.showRaiCanas=true
    if (this.currentScreen < 3) {

      this.currentScreen++;
      // const a=this.useCaseService.getcurrentScreen.subscribe((msg) => (this.currentScreen = msg));
      this.useCaseService.setMessage(this.currentScreen)
    }
  }

  // Navigates to the previous screen
  previousScreen() {
    if (this.currentScreen > 1) {
      this.currentScreen--;
      this.useCaseService.setMessage(this.currentScreen)
    }
  }

  // Navigates to the previous step in the stepper
  goToPreviousStep() {
    if (this.stepper) {
      this.stepper.previous();
    }
  }

  // nextStep(){
  //   this.stepper.next();
  // }

  // prevStep(){
  //   this.stepper.previous();
  // }

  onFormDataChange(formData: FormGroup<any>) {
    this.aiCnavasFormData = formData;
    console.log("aiCnavasFormData===", formData);
  }

  saveUseCaseName() {
    this.useCaseService.setUseCaseName(this.useCaseName)
  }

  // Submits the use case data
  submit() {


    this.useCaseService.getQuestionnaireResponse.subscribe((msg) => this.map = msg)
    console.log("map==========", this.map)
    this.useCaseService.getUsecaseName.subscribe((msg) => (this.useCaseName = msg));
    const payload = {
      "UserId": '"' + this.userId + '"',
      "UseCaseName": this.useCaseName
    }
    console.log("length of useCadse Name===", this.useCaseName.length)
    if (this.useCaseName.length == 0) {
      this._snackBar.open("Please enter usecase name", "close", {
        duration: 2000,
        panelClass: ['le-u-bg-black'],
      });
      return
    }
    this.useCaseService.getAiCanvas.subscribe(msg => this.aiCanvasData = msg)

    console.log("This.aiCanvasData147========", this.aiCanvasData)

    console.log("this.aiCanvasData.value===", this.aiCanvasData["AICloudEngineeringServices"])
    const aiCanvaspayload = {
      "UserId": '"' + this.userId + '"',
      "UseCaseName": this.useCaseName,
      "AICanvasResponse": {
        "BusinessProblem": this.aiCanvasData["BusinessProblem"],
        "BusinessValue": this.aiCanvasData["BusinessValue"],
        "EndUserValue": this.aiCanvasData["EndUserValue"],
        "DataStrategy": this.aiCanvasData["DataStrategy"],
        "ModellingApproach": this.aiCanvasData["ModellingApproach"],
        "ModelTraining": this.aiCanvasData["ModelTraining"],
        "ObjectiveFunction": this.aiCanvasData["ObjectiveFunction"],
        "AICloudEngineeringServices": this.aiCanvasData["AICloudEngineeringServices"],
        "ResponsibleAIApproach": this.aiCanvasData["ResponsibleAIApproach"],
      }
    }

    this.useCaseService.getRaiCanvas.subscribe(msg => this.raiCanvasDatDetail = msg)

    console.log("aiCanvaspayload========", aiCanvaspayload)
    // raiCanvasDatDetail
    const raiCanvasPayload = {
      "UserId": '"' + this.userId + '"',
      "UseCaseName": this.useCaseName,
      "CanvasResponse": {
        "Accountability": this.raiCanvasDatDetail["Accountability"],
        "SecurityVulnerabilities": this.raiCanvasDatDetail["SecurityVulnerabilities"],
        "Explainability": this.raiCanvasDatDetail["Explainability"],
        "StandardMLopsPractices": this.raiCanvasDatDetail["StandardMLopsPractices"],
        "Fairness": this.raiCanvasDatDetail["Fairness"],
        "Drift": this.raiCanvasDatDetail["Drift"],
        "HumanTouchPoints": this.raiCanvasDatDetail["HumanTouchPoints"],
        "RobustnessAndRisks": this.raiCanvasDatDetail["RobustnessAndRisks"],
        "Privacy": this.raiCanvasDatDetail["Privacy"],
        "IPProtectionandIPInfringement": this.raiCanvasDatDetail["IPProtectionandIPInfringement"]
      }
    }

    for (let [key, value] of this.map) {
      // console.log(key + " is " + value);
      const payload = {
        "QuestionId": value[1],
        "UserId": '"' + value[3] + '"',
        "UseCaseName": value[4],
        "QuestionOptionId": value[0],
        "ResponseDesc": value[2]
        // "Q_Weightage":value[5],
        // "RAI_Risk_Index":value[6]
      }

      const jsonPayload = JSON.stringify(payload);
      console.log(jsonPayload);
      this.questionPayload.push(jsonPayload)

      // 
      // c++;

      console.log("payload=====", payload["UserId"])

    }
    console.log("RaiCanvaspayload182===========", this.raiCanvasDatDetail)

    this.creatUsecsse(payload, aiCanvaspayload, raiCanvasPayload, this.questionPayload)

    // this.https.post(this.createUseCase, {

  }

  // Sets the API endpoints for the component
  setApilist(ip_port: any) {
    // this.getFile = ip_port.result.DocProcess + ip_port.result.DocProcess_getFiles  // + environment.getFile
    // this.uploadFile = ip_port.result.DocProcess + ip_port.result.DocProcess_uploadFile   //+ environment.uploadFile
    // this.DocProcessing_getFileContent = ip_port.result.DocProcess + ip_port.result.DocProcessing_getFileContent   //+ environment.uploadFile

    this.createUseCase = ip_port.result.Questionnaire + ip_port.result.Questionnaire_createUsecase
    this.aiCanvasSubmitResponse = ip_port.result.Questionnaire + ip_port.result.Ai_Canvas_Submit
    this.raiCanvasSubmitResponse = ip_port.result.Questionnaire + ip_port.result.Canvas_Submit
    this.submit_Response = ip_port.result.Questionnaire + ip_port.result.submitResponse
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

  parentPageValue: any;
// Updates the parent page value when the child value changes
  onChildValueChange(newValue: any) {
    console.log("Inside value changes======")
    this.parentPageValue = newValue;

    console.log("parentPageValue===", this.parentPageValue)
  }

   // Initializes the component and sets up API endpoints
  ngOnInit() {
    console.log("cureent===", this.currentScreen);
    
    this.useCaseService.getcurrentScreen.subscribe((msg) => (this.currentScreen = msg));
    console.log("cureent===", this.currentScreen);

    this.useCaseService.getUsecaseName.subscribe((msg) => (this.useCaseName = msg));

    this.useCaseService.getcurrentPage.subscribe((msg) => (this.currentPage = msg));

    console.log("cureentPageNumber275=====", this.currentPage);
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    console.log("ipport===", ip_port)
    this.setApilist(ip_port)

  }

  // Creates a new use case
  creatUsecsse(payload: any, aiCanvaspayload: any, raiCanvasPayload: any, quesPayload: any) {
    this.https.post(this.createUseCase, payload).subscribe(

      (res: any) => {
        // console.log("Payload===",payload)
        console.log("res========76", res)
        if (res) {
          this.aiCanvasSubmit(aiCanvaspayload, raiCanvasPayload, quesPayload)
          console.log("Successfully usecasename created")

        }

        const element = document.getElementById('aicanvasTab');
        if (element) {
          console.log("Inside element click")
          element.click();
        }

      }, error => {
        console.log(error.status);
        console.log(error)
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        // this.processing = "Failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    )
  }

   // Submits the AI canvas data
  aiCanvasSubmit(aiCanvaspayload: any, raiCanvasPayload: any, quesPayload: any) {
    this.https.post(this.aiCanvasSubmitResponse, aiCanvaspayload).subscribe(
      (res: any) => {
        console.log("Successfully Added AI canvas====", res);

        if (res == "Added Successfully" || res == " Updated Successfully...") {
          this.raiCanvasSubmit(raiCanvasPayload, quesPayload)
          if (res == " Updated Successfully...") {
            this._snackBar.open(res, "close", {
              duration: 2000,
              panelClass: ['le-u-bg-black'],
            });
          } else {
            this._snackBar.open(res, "close", {
              duration: 2000,
              panelClass: ['le-u-bg-black'],
            });

            const element = document.getElementById('raicanvasTab');
            if (element) {
              console.log("Inside element click")
              element.click();
            }
          }
          // this.aiCanvasEdit = false;
          this.cdr.detectChanges();
        } else {
          this._snackBar.open("Something went wrong...", "close", {
            duration: 2000,
            panelClass: ['mat-toolbar', 'mat-primary']
          });
        }
        // update db with role user,local storage ,call page authority 
        const userRole = localStorage.getItem('role');
        console.log("USerROLE=====", userRole)
        // if(userRole?.length == 0)
        // this.homeService.updateNewUserRole(userPayload);

        // Trigger a shell refresh


      },
      error => {
        console.log(error);
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        this._snackBar.open(message, "close", {
          duration: 2000,
          panelClass: ['le-u-bg-black'],
        });
      }
    )
  }

  // Submits the RAI canvas data
  raiCanvasSubmit(raiCanvasPayload: any, quesPayload: any) {
    this.https.post(this.raiCanvasSubmitResponse, raiCanvasPayload).subscribe(
      (res: any) => {
        console.log(res);
        if (res == "Added Successfully" || res == " Updated Successfully...") {
          console.log("Successfully Added RAI canvas====", res);
          // this.useCaseMainPage=true
          this.questionnaireSubmit(quesPayload)
          if (res == " Updated Successfully...") {
            this._snackBar.open(res, "close", {
              duration: 2000,
              panelClass: ['le-u-bg-black'],
            });
          } else {
            this._snackBar.open(res, "close", {
              duration: 2000,
              panelClass: ['le-u-bg-black'],
            });

            const element = document.getElementById('question');
            if (element) {
              console.log("Inside element click")
              element.click();
            }
          }
          // this.raiCanvasEdit = false;
          this.cdr.detectChanges();
        } else {
          this._snackBar.open("Something went wrong...", "close", {
            duration: 2000,
            panelClass: ['mat-toolbar', 'mat-primary']
          });
        }
        // // update db with role user,local storage ,call page authority 
        // this.homeService.updateNewUserRole(userPayload);
        // // Trigger a shell refresh


      },
      error => {
        console.log(error);
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        this._snackBar.open(message, "close", {
          duration: 2000,
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // Submits the questionnaire data
  questionnaireSubmit(payload: any) {
    const payload1 = {
      // "data":this.questionPayload
      "data": payload
    }
    this.https.post(this.submit_Response, payload1).subscribe(

      (res: any) => {
        // console.log("Payload===",payload)
        if (res == "Response Updated Successfully..." || res == "Response Added Successfully...") {
          // this.getRisk(this.userId,this.UseCaseName)
          this.useCaseMainPage = true
          this.useCaseService.setUseCaseName("")
          this.useCaseService.setAiCanvas("")
          this.useCaseService.setRaiCanvas("")

        }

        console.log("res========76", res)

      }, error => {
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        // this.processing = "Failed"
        this.useCaseService.setUseCaseName("")
          this.useCaseService.setAiCanvas("")
          this.useCaseService.setRaiCanvas("")
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    )
  }


}
