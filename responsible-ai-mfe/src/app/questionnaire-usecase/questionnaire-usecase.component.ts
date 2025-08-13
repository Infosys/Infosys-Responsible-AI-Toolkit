/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, EventEmitter, Input, Output } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup ,ReactiveFormsModule, Validators} from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { UseCaseServiceService } from '../use-case-parent/use-case-service.service';
import { MatStepper } from '@angular/material/stepper';
import { NonceService } from '../nonce.service';
import { UserValidationService } from '../services/user-validation.service';

@Component({
  selector: 'app-questionnaire-usecase',
  templateUrl: './questionnaire-usecase.component.html',
  styleUrls: ['./questionnaire-usecase.component.css']
})
export class QuestionnaireUsecaseComponent {
  result: any;
  cnt: any;
  map = new Map<string, any[]>()
  @Input() stepper!: MatStepper ;
  @Input() stepper2: MatStepper | undefined;
  @Output() pageValueChange = new EventEmitter<any>();
  next: any;
  UseCaseName:any
  formControlNames: string[] = []; 
  editValue: any;
  questionnaireForm!: FormGroup;
  raiCanvasData: any
  aiCanvasData: any
  raiCanvasDatDetail: any
  useCaseName: any
  userId: any;
  createUseCase: any;
  aiCanvasSubmitResponse: any;
  raiCanvasSubmitResponse: any;
  useCaseMainPage: boolean = false;
  map1: any
  questionPayload: any = []
  // map: any
  // firstFormGroup!: FormGroup;
  // firstFormGroup!:FormGroup
  firstFormGroup = this._formBuilder.group({
    
    firstCtrl: ['', Validators.required],
    
  });
  firstFormGroup1 = this._formBuilder.group({
    firstCtrl1: ['', Validators.required],
  });
  firstFormGroup2 = this._formBuilder.group({
    firstCtrl2: ['', Validators.required],
  });
  firstFormGroup3 = this._formBuilder.group({
    firstCtrl3: ['', Validators.required],
  });
  firstFormGroup4 = this._formBuilder.group({
    firstCtrl4: ['', Validators.required],
  });
  secondFormGroup = this._formBuilder.group({
    secondCtrl: ['', Validators.required],
  });

  thirdFormGroup = this._formBuilder.group({
    thirdCtrl: ['', Validators.required],
  });
  fourthFormGroup = this._formBuilder.group({
    fourthCtrl: ['', Validators.required],
  });
  fifthFormGroup = this._formBuilder.group({
    fifthCtrl: ['', Validators.required],
  });
  subdata: any;
  // createUseCase: any;
  // aiCanvasSubmitResponse: any;
  // raiCanvasSubmitResponse: any;

  // dynamicallycreateFormControl(id: string) {  
    
    // const formControlName = `firstCtrl-${id}`; 
    //  this.firstFormGroup.addControl(formControlName, this._formBuilder.control(''));}

  constructor(private _snackBar: MatSnackBar,
    private _formBuilder: FormBuilder,
    private cdr: ChangeDetectorRef,
    public https: HttpClient, private router: Router,
    private useCaseService:UseCaseServiceService,
    public nonceService:NonceService,
    private validationService:UserValidationService
  ) {}
  // private stepper:MatStepper

    qutionnaireForm : FormGroup | undefined
    question:any[]=[]
    selectedOptionMap:Map<string,string>=new Map()
    myForm = new FormGroup({
      questionGroups: new FormArray([])
    });

    selectedTab: any=1;
    parameterTab=true
    // userId :any
    submit_Response=""
    ques_Details=""
    Ques_Risk_Dashboard=""
    Ques_selectedResponse=""
    
    // Emits the current screen page value to the parent component
    onChildValueChange() {
      this.pageValueChange.emit(this.currentScreenPage);
      console.log("this.currentScreenPage90===",this.currentScreenPage)
    }
    
    // Selects the specified tab and updates the UI
  selectTab(tab: any) {

    console.log("FirstFormGroup====",this.firstFormGroup.value)
    this.selectedTab = tab;
    console.log("seectedTab====",this.selectedTab)
    this.cdr.detectChanges();
  }

  // Navigates to the next screen in the questionnaire
  currentScreenPage:any=1;
      nextScreen() {
        console.log("inside nexscreen()========")
        if (this.currentScreenPage < 5 ) {
         
          this.currentScreenPage++;
          this.selectTab(this.currentScreenPage)
          this.useCaseService.setCurrentPage(this.currentScreenPage)
  
          console.log("this.cureentscrenn====",this.currentScreenPage)
          // console.log("this.aicanvas value====",this.raiCanvasForm.value)
        }
      }
  
      // Navigates to the previous screen in the questionnaire
    previousScreen() {
      // this.stepper.previous()
      if (this.currentScreenPage > 1) {
        this.currentScreenPage--;
        this.selectTab(this.currentScreenPage)
        this.useCaseService.setCurrentPage(this.currentScreenPage)
      }
    }

    // Sets the API endpoints for the component
    setApilist(ip_port: any) {
      this.createUseCase = ip_port.result.Questionnaire + ip_port.result.Questionnaire_createUsecase
    this.aiCanvasSubmitResponse = ip_port.result.Questionnaire + ip_port.result.Ai_Canvas_Submit
    this.raiCanvasSubmitResponse = ip_port.result.Questionnaire + ip_port.result.Canvas_Submit
    // this.submit_Response = ip_port.result.Questionnaire + ip_port.result.submitResponse
      this.submit_Response =ip_port.result.Questionnaire +ip_port.result.submitResponse  // +environment.fairnesApi;
   this.ques_Details = ip_port.result.Questionnaire + ip_port.result.questionnariesDetails // + environment.admin_list_rec
   this.Ques_Risk_Dashboard = ip_port.result.Questionnaire + ip_port.result.Ques_Risk_Dashboard
   this.Ques_selectedResponse = ip_port.result.Questionnaire + ip_port.result.Ques_selectedResponse
    }

     // Retrieves the logged-in user ID from local storage
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

    // Moves to the next step in the stepper
    goToNextStep() {
      console.log("inside Rai next===")
      if (this.stepper2) {
        this.stepper2.next();
        console.log("this.stepper.previous()",this.stepper2.previous())
        console.log("value of stepper===",this.stepper2)
        this.cdr.detectChanges();
      }
      console.log("value of outside   stepper===",this.stepper2)

    }
  
    // Moves to the previous step in the stepper
    goToPreviousStep() {
      console.log("inside Rai Prvious===")
      if (this.stepper2) {
        this.stepper2.previous();
        console.log("this.stepper.previous()",this.stepper2.previous())
        console.log("value of stepper===",this.stepper2)
        this.cdr.detectChanges();
      }
    }

    
  // getDetails() is used to get all the questions and option from database using this.ques_Details api.....
  getDetails(){
    
    // this.https.get(this.getUrl).subscribe
    this.https.get(this.ques_Details).subscribe
    ((res: any) => {
      // this.OpenAitoogleValue = res.isOpenAI
      // this.dataSource = res.result
      this.result = res
      console.log("res===",res)
      // this.initializeFormControls();
      // this.dataSource = []
      // this.showSpinner1=false;
      // this.edited = true
      // console.log("result====",res)
      console.log("result1111====",res[0].SubDimesnion)
      this.cdr.detectChanges();

      

    }  , error => {
 
 
      // this.showSpinner1 = false;

      // console.log(error.error.detail)
      console.log(error)
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });

  })
    this.cdr.detectChanges();
  }
// getDetails()  closed ///

 // Saves the user's responses to the questionnaire
saveResponse(result:any){
    
  for(let i=0;i<result.length;i++){
    this.cnt=this.cnt+result[i].QuestionDetails.length
  }

  console.log("Inside Save Response=====")
  // console.log("REsult=====",result)
  for (let [key, value] of this.map) {
    console.log(key + " is " + value);
  }

  console.log("total number of questions=====",this.cnt)
  if(this.cnt == this.map.size){
    this.next = true
  }else{
    this.next=false
  }
  
}

 // Stores the response data for a specific question
responseData(Id:any,QuestionId:any,OptionsValue:any,Question_Weightage:any,RAI_secore:any){
  this.userId = this.getLogedInUser()
  // console.log("Id====",Id,QuestionId,OptionsValue,this.userId,this.quesUseCaseName,Question_Weightage,RAI_secore)
  // this.useCaseService.questionGetMessage.subscribe(msg => this.quesUseCaseName = msg)
  console.log("this.quesUseCaseName=====",this.UseCaseName)
  this.useCaseService.getUsecaseName.subscribe(msg => this.UseCaseName = msg)
  console.log("Id====",Id,QuestionId,OptionsValue,this.userId,this.UseCaseName,Question_Weightage,RAI_secore)
  // this.map.set("")
  this.map.set(QuestionId,[Id,QuestionId,OptionsValue,this.userId,this.UseCaseName,Question_Weightage,RAI_secore])
  console.log("map===========",this.map)

  this.useCaseService.setQuestionnaireResponse(this.map)
  


 
}
  // UseCaseName(arg0: string, UseCaseName: any) {
  //   throw new Error('Method not implemented.');
  // }

   // Submits the questionnaire responses and related data
  submit() {
    this.useCaseService.getQuestionnaireResponse.subscribe((msg) => this.map1 = msg)
    console.log("map==========", this.map1)
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

    for (let [key, value] of this.map1) {
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

  // Creates a new use case with the provided payloads
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

  // Submits the AI Canvas data to the API
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

  // Submits the RAI Canvas data to the API
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

   // Submits the questionnaire responses to the API
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

 // Fetches details for resubmitting the questionnaire
  getResubmitDetails(){
    
    // this.https.get(this.getUrl).subscribe
    // this.userId = localStorage.getItem("userid")
    // this.https.get(this.getResetData+this.userId+"/"+this.UseCaseName).subscribe
    console.log("====this.Ques_selectedResponse",this.Ques_selectedResponse)
    this.https.get(this.Ques_selectedResponse+'"'+this.userId+'"'+"/"+this.UseCaseName).subscribe
    ((res: any) => {
      // this.OpenAitoogleValue = res.isOpenAI
      // this.dataSource = res.result
      this.result = res
      // this.dataSource = []
      // this.showSpinner1=false;
      // this.edited = true
      // console.log("result====",res)
      console.log("result1111====116====",res)
      this.cdr.detectChanges();
  
    }  , error => {
  
  
      // this.showSpinner1 = false;
  
      // console.log(error.error.detail)
      console.log(error)
      const message = "api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });
  
  })
    this.cdr.detectChanges();
  }
  
  // Initializes the component and sets up API calls
    ngOnInit(){
      this.qutionnaireForm=this._formBuilder.group({})
      console.log("cureent===",this.currentScreenPage)
      // this.useCaseService.getcurrentScreen.subscribe(msg => this.currentScreen = msg)
      // console.log("cureent===",this.currentScreen)
      let ip_port: any


    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)

    this.useCaseService.geteditParameter.subscribe(msg => this.editValue = msg) 
    this.useCaseService.getUsecaseName.subscribe(msg => this.UseCaseName = msg)

    if(this.editValue == true){
      this.getResubmitDetails()
    }else{
      this.getDetails()
    }
    

    console.log("firstFormGroup2====",this.firstFormGroup2)
   
    
    // Initialize the form controls for each question
    // this.initializeFormControls();
    }

  //   const questionGroups = this.subdata.OptionsDetail.map(question => {
  //     return new FormGroup({
  //       // Add a form control for each question's selected option
  //       selectedOption: new FormControl(null, required)
  //     });
  //   });
  //   this.myForm.setControl('questionGroups', new FormArray(questionGroups));
  // }


    // responseData1(optionId: number, questionId: number, optionValue: string, weightage: number, minScore: number) {
    //   // Access selected option value from the form
    //   const selectedOption = this.myForm.get('questionGroups').value[questionId];
      
    //   // Process data based on selectedOption
    //   // ...
    // }

      
    // initializeFormControls() {
    //   this.firstFormGroup = this._formBuilder.group({});
    //   // const questionsArray = this.questionnaireForm.get('questions') as FormArray;
  
    //   // Loop through your questions data and create form controls
    //   for (let i = 0; i < this.result[0].SubDimesnion.length; i++) {
    //     const subDimension = this.result[0].SubDimesnion[i];
    //     const questionDetails = subDimension.QuestionDetails;
    //     const formControls: { [key: string]: FormControl } = {}; // Define formControls as an object with string keys and FormControl values

    //     for (let j = 0; j < questionDetails.length; j++) {
    //       const questionId = questionDetails[j].QuestionId;
    //       formControls[questionId] = new FormControl('', Validators.required); // Assign a new FormControl to the corresponding key in formControls
    //     }
    //     console.log("formControls====",formControls)
    //     // this.firstFormGroup = this._formBuilder.group(formControls); 
    //     const subFormGroup = this._formBuilder.group(formControls);
    //      this.firstFormGroup.addControl('subFormGroup', subFormGroup);
    //     console.log("firstFormGroup2====",this.firstFormGroup2)
    //     // console.log("firstFormGroup====",this.firstFormGroup)
    //     // Use formControls object to create the FormGroup
    //   }
    //   console.log("firstFormGrouplast====",this.firstFormGroup)
      
    // }
    

    // ontoglechange(event:any){
    // }
}
