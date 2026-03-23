/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, EventEmitter, Input, Output,OnChanges } from '@angular/core';
import { FormBuilder, FormControl, FormGroup ,ReactiveFormsModule} from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { UseCaseServiceService } from '../use-case-parent/use-case-service.service';
import { MatStepper } from '@angular/material/stepper';
import { NonceService } from '../nonce.service';

@Component({
  selector: 'app-ai-canvas-usecase',
  templateUrl: './ai-canvas-usecase.component.html',
  styleUrls: ['./ai-canvas-usecase.component.css']
})
export class AiCanvasUsecaseComponent implements OnChanges {

  @Output() aiCanvasFormData = new EventEmitter<FormGroup<any>>();
  @Output() formData: EventEmitter<any> = new EventEmitter<any>();
  @Output() formDataChanged = new EventEmitter<any>();
  // @Input() aiCanvasForm!:FormGroup ;

  @Input() stepper!: MatStepper;
  @Input() editValue :any;
  // @Input() data: number ;

  @Input() step: any;
  @Output() next:EventEmitter<any> = new EventEmitter<any>();
  @Output() prev:EventEmitter<any> = new EventEmitter<any>();
  userId:any;
  apiURL:any;
  getAICanvasEndPoint:any;
  postAICanvasEndPoint:any;
  editParameter: any;
  reload= false;
  localPostUrl = "http://localhost:30080/v1/questionnaire/aicanvas/submitResponse"
  localgetUrl = "http://localhost:30080/v1/questionnaire/aicanvas/getResponse/"
  UseCaseName=""
  AiUseCaseName=""
  RaiUseCaseName=""
  wordLength :any[]=[]
  resetFeatureWordLength:any[]=[]
  aicanvasEditData :any

  aiCanvasForm = new FormGroup({
    BusinessProblem: new FormControl(''),
    BusinessValue: new FormControl(''),
    EndUserValue: new FormControl(''),
    DataStrategy: new FormControl(''),
    ModellingApproach: new FormControl(''),
    ModelTraining: new FormControl(''),
    ObjectiveFunction: new FormControl(''),
    AICloudEngineeringServices: new FormControl(''),
    ResponsibleAIApproach: new FormControl('')
  })
  


  constructor(private _snackBar: MatSnackBar,
    private _formBuilder: FormBuilder,
    private cdr: ChangeDetectorRef,
    public https: HttpClient, private router: Router,
    private useCaseService:UseCaseServiceService,public nonceService:NonceService
    ) {
      // this.useCaseService.getAiCanvas.subscribe(msg => this.aicanvasEditData = msg)
      // this.editDataSet(this.aicanvasEditData)
    }
    // private stepper:MatStepper

    // Emits form data to the parent component
    emitDataToParent(){
      this.formDataChanged.emit(this.aiCanvasForm.value)
      this.useCaseService.setAiCanvas(this.aiCanvasForm.value)
    }

    // Counts the number of words in a text field
    countWords(event:any,index:any){
      const text = event.target.value
      const words = text.trim().split(/\s+/);
      this.wordLength[index] = words.length;
      console.log("aicanvas from valid====",this.aiCanvasForm.valid)
      // this.wordLength=words.length // Split the text into words
      console.log("words", text)
      console.log("words.length", words.length)
      this.cdr.detectChanges();
  
    }

    submitForm() {
      // Emit the form data to the parent component
      this.formData.emit(this.aiCanvasForm.value);
    }

    // ngAfterViewInit() {
    //   // Set the initial step based on the currentScreen value
    //   this.stepper.selectedIndex = this.currentScreen-1;
    // }

      handleAiCanvasSubmit(){

      }

      // Checks if the form is valid for screen 2
      isScreen2Valid(){
        return this.aiCanvasForm.valid
        // return this.aiCanvasForm.get('BusinessProblem')?.valid && this.aiCanvasForm.get('BusinessValue')?.valid && this.aiCanvasForm.get('EndUserValue')?.valid
      }

      currentScreen:any;
    // Navigates to the next screen
    nextScreen() {
      
      if (this.currentScreen < 3 ) {
       
        this.currentScreen++;
        this.useCaseService.setMessage(this.currentScreen)
        this.stepper?.next()

        console.log("this.cureentscrenn====",this.currentScreen)
        console.log("this.aicanvas value====",this.aiCanvasForm.value)
      }
    }

    // currentScreen:any;
      // nextScreen() {
      //   if (this.currentScreen < 3 ) {
         
      //     this.currentScreen++;
      //     this.useCaseService.setMessage(this.currentScreen)
  
      //     console.log("this.cureentscrenn====",this.currentScreen)
      //     console.log("this.aicanvas value====",this.raiCanvasForm.value)
      //   }
      // }
  
    previousScreen() {
      if (this.currentScreen > 1) {
        this.currentScreen--;
        this.useCaseService.setMessage(this.currentScreen)
      }
    }

  // Moves to the next step in the stepper
  goToNextStep() {
    if (this.stepper) {
      this.stepper.next();
      console.log("value of AI stepper===",this.stepper)
    }
  }

  goToPreviousStep() {
    console.log("inside Rai Prvious===")
    if (this.stepper) {
      this.stepper.previous();
      console.log("Value 0f iside ===stepper in Ai =====",this.stepper)
    }
    console.log("Value 0f stepper in Ai =====",this.stepper)
  }

  // Submits the form and emits data to the parent component
  onSubmit(){
    console.log("this.aiCanvasForm.value",this.aiCanvasForm.value)
    const formData: FormGroup<any> = this.aiCanvasForm;
    this.aiCanvasFormData.emit(formData)
    this.useCaseService.setAiCanvas(this.aiCanvasForm.value)
    // this.formDataChange.emit(formData);
    // if(this.aiCanvasForm.valid){
    //   console.log("89====this.aiCanvasForm.value",this.aiCanvasForm.value)
    //   this.aiCanvasFormData.emit(this.aiCanvasForm)
    // }
  }

  // Handles changes in input properties
  ngOnChanges() {
    
      // this.editDataSet(this.aicanvasEditData)
    console.log("editValue===",this.editValue)
    if (this.editValue === true) {
      this.useCaseService.getAiCanvas.subscribe(msg => this.aicanvasEditData = msg)
      // this.editDataSet(this.aicanvasEditData)
    }
    // this.editValue = false
    this.useCaseService.setAiCanvas("")
  }

  // if(editValue:any){
  //   console.log("editValue===",editValue)
  //   if(editValue==true){
  //     this.editDataSet(this.aicanvasEditData)
  //   }
  //   console.log("editValue===",editValue)
  // }

  // if(editValue:any==true){
  //   console.log("editValue===",editValue)
  // }

  // Edits the form data with the provided response
  editDataSet(res:any){
    console.log("res181editDataa========",res)
    this.aiCanvasForm.patchValue({
      BusinessProblem: res.BusinessProblem,
      BusinessValue: res.BusinessValue,
      EndUserValue: res.EndUserValue,
      DataStrategy: res.DataStrategy,
      ModellingApproach: res.ModellingApproach,
      ModelTraining: res.ModelTraining,
      ObjectiveFunction: res.ObjectiveFunction,
      AICloudEngineeringServices: res.AICloudEngineeringServices,
      ResponsibleAIApproach: res.ResponsibleAIApproach,
    })

    console.log("this.aicavasForm===",this.aiCanvasForm.value)
    
    // this.useCaseService.setAiCanvas("")
  }

   // Initializes the component and sets up data
  ngOnInit(){
    console.log("cureent===",this.currentScreen)
    this.useCaseService.getAiCanvas.subscribe(msg => this.aicanvasEditData = msg)
    this.useCaseService.getcurrentScreen.subscribe(msg => this.currentScreen = msg)
    console.log("aicanvasEditData===",this.aicanvasEditData)
    this.useCaseService.geteditParameter.subscribe(msg => this.editParameter = msg)

    if(this.editParameter == true){
      this.useCaseService.getAiCanvas.subscribe(msg => this.aicanvasEditData = msg)
      console.log("this.raicanvasEditData===",this.aicanvasEditData)
      this.editDataSet(this.aicanvasEditData)
    }
    // this.editDataSet(this.aicanvasEditData)
  }

  



}
