/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { FormBuilder, FormControl, FormGroup ,ReactiveFormsModule} from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { UseCaseServiceService } from '../use-case-parent/use-case-service.service';
import { MatStepper } from '@angular/material/stepper';
import { NonceService } from '../nonce.service';

@Component({
  selector: 'app-rai-canvas-usecase',
  templateUrl: './rai-canvas-usecase.component.html',
  styleUrls: ['./rai-canvas-usecase.component.css']
})
export class RaiCanvasUsecaseComponent implements OnChanges{

  @Input() step: any;
  @Input() stepper!: MatStepper;
  @Input() editValue :any;
  @Output() next:EventEmitter<any> = new EventEmitter<any>();
  @Output() prev:EventEmitter<any> = new EventEmitter<any>();
  @Output() previousClicked: EventEmitter<any> = new EventEmitter();
  @Output() formRaiCanvasDataChanged = new EventEmitter<any>();
  userId:any;
  apiURL:any;
  getAICanvasEndPoint:any;
  postAICanvasEndPoint:any;
  reload= false;
  UseCaseName=""
  AiUseCaseName=""
  RaiUseCaseName=""
  wordLength :any[]=[]
  resetFeatureWordLength:any[]=[]
  raicanvasEditData: any
  editParameter:any

  // aiCanvasForm = new FormGroup({
  //   BusinessProblem: new FormControl(''),
  //   BusinessValue: new FormControl(''),
  //   EndUserValue: new FormControl(''),
  //   DataStrategy: new FormControl(''),
  //   ModellingApproach: new FormControl(''),
  //   ModelTraining: new FormControl(''),
  //   ObjectiveFunction: new FormControl(''),
  //   AICloudEngineeringServices: new FormControl(''),
  //   ResponsibleAIApproach: new FormControl('')
  // })

  raiCanvasForm = new FormGroup({
    Accountability: new FormControl(''),
    SecurityVulnerabilities: new FormControl(''),
    Explainability: new FormControl(''),
    StandardMLopsPractices: new FormControl(''),
    Fairness: new FormControl(''),
    Drift: new FormControl(''),
    HumanTouchPoints: new FormControl(''),
    RobustnessAndRisks: new FormControl(''),
    Privacy: new FormControl(''),
    IPProtectionandIPInfringement : new FormControl('')
  })
 


  constructor(private _snackBar: MatSnackBar,
    private _formBuilder: FormBuilder,
    private cdr: ChangeDetectorRef,
    public https: HttpClient, private router: Router,
    private useCaseService:UseCaseServiceService,
    public nonceService:NonceService
  ) {

    console.log("Hi From Constructor===============")
  }
  // private stepper:MatStepper

// Counts the number of words in the input text
    countWords(event:any,index:any){
      const text = event.target.value
      const words = text.trim().split(/\s+/);
      this.wordLength[index] = words.length;
      // this.wordLength=words.length // Split the text into words
      console.log("words", text)
      console.log("words.length", words.length)
      this.cdr.detectChanges();
  
    }

    // Resets the word count for a specific feature
    resetFeatureCountWords(event:any,index:any){
      const text = event.target.value
      const words = text.trim().split(/\s+/);
      this.resetFeatureWordLength[index] = words.length;
      // this.wordLength=words.length // Split the text into words
      console.log("words", text)
      console.log("words.length", words.length)
      this.cdr.detectChanges();
  
    }
  

    // emitDataToParent(){
    //   this.useCaseService.setRaiCanvas(this.raiCanvasForm)
    // }

    // ngAfterViewInit() {
    //   // Set the initial step based on the currentScreen value
    //   this.stepper.selectedIndex = this.currentScreen-1;
    // }

    // Emits the RAI Canvas form data to the parent component
    emitRaiCanvasDataToParent(){
      this.formRaiCanvasDataChanged.emit(this.raiCanvasForm.value)
      this.useCaseService.setRaiCanvas(this.raiCanvasForm.value)
    }

    // Handles changes to the input properties and updates the form
    ngOnChanges() {
    
      // this.editDataSet(this.aicanvasEditData)
    console.log("editValue===",this.editValue)
    if (this.editValue === true) {
      this.useCaseService.geteditParameter.subscribe(msg => this.editParameter = msg)

      console.log("editParameter Rai Canvas===",this.editParameter)

      if(this.editParameter == true){
        this.useCaseService.getRaiCanvas.subscribe(msg => this.raicanvasEditData = msg)
        console.log("this.raicanvasEditData===",this.raicanvasEditData)
        this.editDataSet(this.raicanvasEditData)
      }
      // this.useCaseService.getAiCanvas.subscribe(msg => this.raicanvasEditData = msg)
      // this.editDataSet(this.raicanvasEditData)
    }
    // this.editValue = false
    // this.useCaseService.setRaiCanvas("")
  }

// Populates the form with existing data for editing
  editDataSet(res:any){
    console.log("res181editDataaRaiCanvas========",res)
    this.raiCanvasForm.patchValue({
            Accountability: res.Accountability,
            SecurityVulnerabilities: res.SecurityVulnerabilities,
            Explainability: res.Explainability,
            StandardMLopsPractices: res.StandardMLopsPractices,
            Fairness: res.Fairness,
            Drift: res.Drift,
            HumanTouchPoints: res.HumanTouchPoints,
            RobustnessAndRisks: res.RobustnessAndRisks,
            Privacy: res.Privacy,
            IPProtectionandIPInfringement: res.IPProtectionandIPInfringement
    })

    console.log("this.raicavasForm===",this.raiCanvasForm.value)
    
    // this.useCaseService.setAiCanvas("")
  }

      handleAiCanvasSubmit(){

      }

       // Navigates to the next step in the stepper
      goToNextStep() {
        console.log("inside Rai next===")
        if (this.stepper) {
          this.stepper.next();
          console.log("this.stepper.previous()",this.stepper.previous())
          console.log("value of stepper===",this.stepper)
          this.cdr.detectChanges();
        }
        console.log("value of outside   stepper===",this.stepper)

      }
    
      // Navigates to the previous step in the stepper
      goToPreviousStep() {
        console.log("inside Rai Prvious===")
        console.log("curentscreen value95=====",this.currentScreen)
        this.previousClicked.emit();
        if (this.stepper) {
          this.stepper.previous();
          console.log("this.stepper.previous()",this.stepper.previous())
          console.log("value of stepper===",this.stepper)
          this.cdr.detectChanges();
        }
      }
      // goToPreviousStep() {
        
      // }

      // Validates the form for the second screen
      isScreen2Valid(){
        return this.raiCanvasForm.valid
        // return this.aiCanvasForm.get('BusinessProblem')?.valid && this.aiCanvasForm.get('BusinessValue')?.valid && this.aiCanvasForm.get('EndUserValue')?.valid
      }

      // Navigates to the next screen in the RAI Canvas workflow
      currentScreen:any=1;
      nextScreen() {
        // if (this.raiCanvasForm.invalid) {
        //   return;
        // }

        
        if (this.currentScreen < 3 ) {
         
          this.currentScreen++;
          this.useCaseService.setMessage(this.currentScreen)
          this.stepper?.next()
  
          console.log("this.cureentscrenn====",this.currentScreen)
          console.log("this.aicanvas value====",this.raiCanvasForm.value)
        }
      }
  
      // Navigates to the previous screen in the RAI Canvas workflow
    previousScreen() {
      
      console.log("Inside previos==========113")
      if (this.currentScreen > 1) {
        this.currentScreen--;
        this.useCaseService.setMessage(this.currentScreen)
        this.stepper.previous()
        console.log("curenent scrennn117========",this.currentScreen)
      }
    }

     // Submits the RAI Canvas form data
    onSubmit(){
      console.log("this.raiCanvasForm.value",this.raiCanvasForm.value)
      this.useCaseService.setRaiCanvas(this.raiCanvasForm.value)
     
    }
  
  // Initializes the component and sets up API calls
    ngOnInit(){
      console.log("cureent===",this.currentScreen)
      this.useCaseService.getcurrentScreen.subscribe(msg => this.currentScreen = msg)
      console.log("cureent===",this.currentScreen)
     
      this.useCaseService.geteditParameter.subscribe(msg => this.editParameter = msg)

      console.log("editParameter===",this.editParameter)

      // if(this.editParameter == true){
      //   this.useCaseService.getRaiCanvas.subscribe(msg => this.raicanvasEditData = msg)
      //   console.log("this.raicanvasEditData===",this.raicanvasEditData)
      //   this.editDataSet(this.raicanvasEditData)
      // }
    }
  

  

}
