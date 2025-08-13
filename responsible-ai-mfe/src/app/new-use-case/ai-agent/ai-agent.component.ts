/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpParams} from '@angular/common/http';
import { Component,OnInit ,Input, ViewChild, TemplateRef, ChangeDetectorRef } from '@angular/core';
import { AbstractControl, FormControl,FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { MatStepper } from '@angular/material/stepper';
import { MatDialog } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';
import { MatOption } from '@angular/material/core';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';

@Component({
  selector: 'app-ai-agent',
  templateUrl: './ai-agent.component.html',
  styleUrls: ['./ai-agent.component.css']
})

export class AiAgentComponent implements OnInit {
  @ViewChild('businessJustificationDialog') businessJustificationDialog!: TemplateRef<any>;
  @ViewChild('select2') select2!: MatSelect;
  @Input() useCaseNameDetail: any;
  usecasesList: any[] = [];
  files: any[] = [];
  demoFile: any[] = [];
  file: File | any;
  selectedFile: File | any;
  showSpinner1 = false;
  useCase!: FormGroup;
  dataSource: any = [];
  user:any;
   // FOR SHIMMER LOADING
   isLoadingTable = true;
  // API
  getData: any;
  aiUpload: any;
  createUsecase: any;
  getUsecases: any;
  generateCompReport: any;
  generateImpactRep: any;
  recommendationRep: any;
  complianceRecommendations: any;
  createPredictRisk: any;
  // pagination
  pagingConfig: PagingConfig = {} as PagingConfig;
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  switch: boolean= false;
  selectedUseCase: string = '';
  PredictRiskUseCase: any;
  deleteRisk: any;
  UcSwitch: boolean = false;
  // useCaseName: string = '';
  UsecaseType: string = '';
  selectedModel: number = 1;
  displayedModels: number[] = [1];
  Jurisdiction: any = [];
  options = [
    { viewValue: 'Internal',
      value: 'Internal',    },
    { viewValue: 'Tools & Procurement',
      value: 'Tools & Procurement',    }
  ];
  jurisdictionOptions = [
    { value: 'United States', viewValue: 'United States' },
    { value: 'Japan', viewValue: 'Japan' },
    { value: 'United Kingdom', viewValue: 'United Kingdom' },
    { value: 'Germany', viewValue: 'Germany' },
    { value: 'France', viewValue: 'France' },
    { value: 'Italy', viewValue: 'Italy' },
    { value: 'Singapore', viewValue: 'Singapore' },
    { value: 'Australia', viewValue: 'Australia' },
    { value: 'India', viewValue: 'India' }
  ];
  aiCanvasForm = new FormGroup({
    BusinessProblem: new FormControl('',[Validators.required]),
    BusinessValue: new FormControl('',[Validators.required]),
    EndUserValue: new FormControl('',[Validators.required]),
    DataStrategy: new FormControl('',[Validators.required]),
    ModellingApproach: new FormControl('',[Validators.required]),
    ModelTraining: new FormControl('',[Validators.required]),
    ObjectiveFunction: new FormControl('',[Validators.required]),
    AICloudEngineeringServices: new FormControl('',[Validators.required]),
    ResponsibleAIApproach: new FormControl('',[Validators.required])
  })
  raiCanvasForm = new FormGroup({
    Accountability: new FormControl('',[Validators.required]),
    Drift: new FormControl('',[Validators.required]),
    SecurityVulnerabilities: new FormControl('',[Validators.required]),
    HumanTouchPoints: new FormControl('',[Validators.required]),
    Explainability: new FormControl('',[Validators.required]),
    RobustnessAndRisks: new FormControl('',[Validators.required]),
    StandardMLopsPractices: new FormControl('',[Validators.required]),
    Privacy: new FormControl('',[Validators.required]),
    Fairness: new FormControl('',[Validators.required]),
    IPProtectionandIPInfringement: new FormControl('',[Validators.required]),
   // SolutionImpact: new FormControl('', [Validators.required]),
   // DataQuality: new FormControl('', [Validators.required]),
   // Audit: new FormControl('', [Validators.required]),
   // Validation: new FormControl('', [Validators.required]),
    VulnerableGroups: new FormControl('', [Validators.required])
  });
  modelDetailForm: { [key: number]: FormGroup } = {};

  // modelDetailForm= new FormGroup({
  //   TypeOfAIModel: new FormControl('',[Validators.required]),
  //   ModelInput: new FormControl('',[Validators.required]),
  //   ModelOutput: new FormControl('',[Validators.required]),
  //   OtherModelInput: new FormControl('',[Validators.required]),
  //   OtherModelOutput: new FormControl('',[Validators.required]),
  //   ModelDescription: new FormControl('',[Validators.required])
  // });
  BusinessJustificationForm = new FormGroup({
    Objective: new FormControl('',[Validators.required]),
    AlignmentWithBusinessGoals: new FormControl('',[Validators.required]),
    CurrentChallenges: new FormControl('',[Validators.required]),
    ImpactOfTheProblem: new FormControl('',[Validators.required]),
    ProposedSolution: new FormControl('',[Validators.required]),
    HowItWorks: new FormControl('',[Validators.required]),
    QuantifiableBenefits: new FormControl('',[Validators.required]),
    IntangibleBenefits: new FormControl('',[Validators.required]),
    CompetitiveAdvantage: new FormControl('',[Validators.required]),
    InitialCosts: new FormControl('',[Validators.required]),
    OngoingCosts: new FormControl('',[Validators.required]),
    ReturnOnInvestment: new FormControl('',[Validators.required]),
    StakeholdersInvolved: new FormControl('',[Validators.required]),
    ChangeManagement: new FormControl('',[Validators.required]),
    KPIs: new FormControl('',[Validators.required]),
    MonitoringAndEvaluation: new FormControl('',[Validators.required]),
    EndOfLife: new FormControl('',[Validators.required])
  })
  predictedRisk: any;
  predictedRiskId: any;
  busninessJustification: string = '';
  businessJustificationUrl: any;
  businessJustUrl : any;

  
  constructor (public _snackBar: MatSnackBar, private https: HttpClient, private snackBar: MatSnackBar, private dialog: MatDialog,public nonceService:NonceService,private validationService:UserValidationService,private fb: FormBuilder,private cdRef: ChangeDetectorRef)
  {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
    this.useCase = new FormGroup({
      useCaseName: new FormControl('', [Validators.required]),
      fileData: new FormControl('', [Validators.required]),
      option: new FormControl('', [Validators.required]),
      usecaseDescription: new FormControl('',[Validators.required]),
      datasetAnalyze: new FormControl('',[Validators.required])
    });
    this.initializeForms();
  }

  // Initializes the component and sets up API calls
  ngOnInit(): void {
    let ip_port: any;
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.user = x ;
      }    }
    ip_port = this.getLocalStoreApi();
    // seting up api list
    this.setApiList(ip_port);
    this.getAllData();
    this.getUsecasesList();
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

  // Sets the API endpoints
  setApiList(ip_port: any) {
    this.getData =  ip_port.result.legalAgent + ip_port.result.PredictRisk ;
    this.aiUpload = ip_port.result.legalAgent + ip_port.result.PredictUpload ;
    this.deleteRisk = ip_port.result.legalAgent + ip_port.result.DeleteRisk ;
    this.PredictRiskUseCase = ip_port.result.legalAgent + ip_port.result.PredictRiskUseCase;
    this.createUsecase = ip_port.result.legalAgent + ip_port.result.createUsecase ;
    this.getUsecases = ip_port.result.legalAgent + ip_port.result.getUsecases ;
    this.generateCompReport = ip_port.result.legalAgent + ip_port.result.generateCompReport ;
    this.businessJustificationUrl = ip_port.result.legalAgent + ip_port.result.businessJustificationUrl;
    this.businessJustUrl= ip_port.result.legalAgent + ip_port.result.businessJustUrl;
    this.generateImpactRep = ip_port.result.legalAgent + ip_port.result.generateImpactRep ;
    this.recommendationRep = ip_port.result.legalAgent + ip_port.result.recommendationRep ;
    this.complianceRecommendations = ip_port.result.legalAgent + ip_port.result.complianceReportRecommendations;
    this.createPredictRisk = ip_port.result.legalAgent + ip_port.result.createPredictRisk;
  }
// ----------------Pagination-----------------
onTableDataChange(event: any) {
  this.currentPage = event;
  this.pagingConfig.currentPage = event;
  this.pagingConfig.totalItems = this.dataSource.length;
}

// Handles file change event
  onFileChange(event: any) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
    //  console.log(text);
    };
    reader.readAsText(event.target.files[0]);
  }

  // Handles file browsing and validation
  fileBrowseHandler(file: any){
    const allowedTypes = ['application/pdf', 'text/plain'];
    console.log("fileBrowseHandler", file.target.files[0].type)
    if (!allowedTypes.includes(file.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      }); 
      // return;
    }else{
    this.prepareFilesList(file.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
    }
  }

  // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    this.files = []
    for (const item of files) {
      const cleanedName = item.name.replace(/\[object Object\]/g, '');
      const newFile = new File([item], cleanedName, { type: item.type });
      this.files.push(newFile);
    }
    this.uploadFilesSimulator(0, files)
  }

   // Simulates file upload progress
  uploadFilesSimulator(index: number, files: any) {
    setTimeout(() => {
      if (index === this.files.length) {
        console.log("RETURN")
        return;
      } else {
        this.files[index].progress = 0;
        const progressInterval = setInterval(() => {
          if (this.files[index].progress >= 100) {
            clearInterval(progressInterval);
          } else {
            console.log("ELSE BLOCK")
            this.files[index].progress += 10;
          }
        }, 200);
      }
    }, 1000);
  }

   // Deletes the uploaded file
  deleteFile(){
    this.files = [];
    this.demoFile = [];
    this.file = null;
  }

  // Initializes the forms for model details
  initializeForms() {
    for (let i = 1; i <= 3; i++) {
      this.modelDetailForm[i] = this.fb.group({
        TypeOfAIModel: [''],
        ModelInput: [''],
        ModelOutput: [''],
        OtherModelInput: [''],
        OtherModelOutput: [''],
        ModelDescription: ['']
      });
    }
  }

   // Updates the model forms based on the selected number of models
  updateModelForms() {
    this.displayedModels = Array.from({ length: Number(this.selectedModel) }, (_, i) => i + 1);
  }
  
  // Submits the use case form
  submit(){
    this.showSpinner1 = true;
    console.log(this.useCase.value);
    console.log(this.UsecaseType, this.Jurisdiction)
    if (this.switch==false){
      const { fileData, option } = this.useCase.value;
      if (this.useCase.value.useCaseName == '' || this.useCase.value.useCaseName == null) {
        this.showSpinner1 =  false;
        this.snackBar.open('Please enter a Use Case Name', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000,
        });
        return;
      }
      if (this.UsecaseType == '' || this.UsecaseType == null) {
        this.showSpinner1 =  false;
        this.snackBar.open('Please select a Usecase Type', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000,
        });
        return;
      }
      if (this.UsecaseType == 'Internal' && (this.Jurisdiction.length == 0)) {
        this.showSpinner1 =  false;
        this.snackBar.open('Please select a Jurisdiction', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000,
        });
        return;
      }
      if (!fileData) {
        this.showSpinner1 = false;
        this.snackBar.open('Please upload a File', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000,
        });
        return;
      }

    const fileData1 = new FormData();
    this.selectedFile = this.files[0];
    fileData1.append('file', this.selectedFile);
    fileData1.append('user_id', this.user);
    fileData1.append('usecaseName', this.useCase.value.useCaseName);
    fileData1.append('usecaseType', this.UsecaseType);
    
    const jurisdictionQuery = this.Jurisdiction.map((j:any) => `jurisdiction=${encodeURIComponent(j)}`).join('&');

    this.https.post(this.aiUpload + `?${jurisdictionQuery}` ,fileData1).subscribe((res: any)=>{
      // this.predictedRisk= res.data.risk;
      // this.predictedRiskId= res.id;
      // if (this.predictedRisk == 'High-Risk') {
      //   this.busninessJustification = '';
      //   const dialogRef = this.dialog.open(this.businessJustificationDialog);

      //   dialogRef.afterClosed().subscribe(result => {
      //     if (result) {
      //       this.busninessJustification = result;
      //       console.log('Business Justification:', this.busninessJustification);
            
      //       const params = new URLSearchParams({
      //         id: this.predictedRiskId,
      //         businessJustification: this.busninessJustification
      //       }).toString();

      //       this.http.post(`${this.businessJustificationUrl}?${params}`, {}).subscribe(
      //         (response: any) => {
      //           console.log('Business Justification Response:', response);                
      //         },
      //         (error: any) => {
      //           console.error('Error submitting business justification:', error);                
      //         }
      //       );

      //       this.getAllData();
      //       this.showSpinner1 = false;
      //       const message = "Submitted Successfully";
      //       const action = "Close";
      //       this.snackBar.open(message, action, {
      //         duration: 3000,
      //         panelClass: ['le-u-bg-black'],
      //       });
      //     } else {
      //       this.showSpinner1 = false;
      //       this.snackBar.open('Business justification is required for high risk usecases', '✖', {
      //         horizontalPosition: 'center',
      //         verticalPosition: 'top',
      //         duration: 5000,
      //       });
      //       return;
      //     }
      //   });
      // } else {
      //   this.getAllData();
      //   this.showSpinner1 = false;
      //   const message = "Submitted Successfully";
      //   const action = "Close";
      //   this.snackBar.open(message, action, {
      //     duration: 3000,
      //     panelClass: ['le-u-bg-black'],
      //   });
      // }
      // if (this.predictedRisk === 'High-Risk') {
      //   const dialogRef = this.dialog.open(this.businessJustificationDialog);
  
      //   dialogRef.afterClosed().subscribe(result => {
      //     if (this.BusinessJustificationForm.valid) {
      //       const payload = {
      //         id: this.predictedRiskId,
      //         objective: this.BusinessJustificationForm.value.Objective,
      //         AlignmentWithBusinessGoals: this.BusinessJustificationForm.value.AlignmentWithBusinessGoals,
      //         CurrentChallenges: this.BusinessJustificationForm.value.CurrentChallenges,
      //         ImpactOfTheProblem: this.BusinessJustificationForm.value.ImpactOfTheProblem,
      //         ProposedSolution: this.BusinessJustificationForm.value.ProposedSolution,
      //         HowItWorks: this.BusinessJustificationForm.value.HowItWorks,
      //         QuantifiableBenefits: this.BusinessJustificationForm.value.QuantifiableBenefits,
      //         IntangibleBenefits: this.BusinessJustificationForm.value.IntangibleBenefits,
      //         CompetitiveAdvantage: this.BusinessJustificationForm.value.CompetitiveAdvantage,
      //         InitialCosts: this.BusinessJustificationForm.value.InitialCosts,
      //         OngoingCosts: this.BusinessJustificationForm.value.OngoingCosts,
      //         ReturnOnInvestment: this.BusinessJustificationForm.value.ReturnOnInvestment,
      //         StakeholdersInvolved: this.BusinessJustificationForm.value.StakeholdersInvolved,
      //         ChangeManagement: this.BusinessJustificationForm.value.ChangeManagement,
      //         KPIs: this.BusinessJustificationForm.value.KPIs,
      //         MonitoringAndEvaluation: this.BusinessJustificationForm.value.MonitoringAndEvaluation,
      //         EndOfLife: this.BusinessJustificationForm.value.EndOfLife
      //       };
  
      //       this.http.post(this.businessJustUrl, payload)
      //         .subscribe(response => {
      //           console.log('Response:', response);
      //         }, error => {
      //           console.error('Error:', error);
      //         });
      //       this.getAllData();
      //       this.showSpinner1 = false;
      //       const message = "Submitted Successfully";
      //       const action = "Close";
      //       this.snackBar.open(message, action, {
      //         duration: 3000,
      //         panelClass: ['le-u-bg-black'],
      //       });
      //     } else {
      //       this.showSpinner1 = false;
      //       this.snackBar.open('All the Busniness Justification fields are required for High Risk Usecases', '✖', {
      //         horizontalPosition: 'center',
      //         verticalPosition: 'top',
      //         duration: 5000,
      //       });
      //       return;
      //     }
      //   });
      // } else {
      this.getAllData();
      this.showSpinner1 = false;
      const message = "Submitted Successfully";
      const action = "Close";
      this.snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      // }
    }, error => {
      this.showSpinner1 = false;
      const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this.snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
    })
  }
    if(this.switch){
      if (this.selectedUseCase=='') {
        this.showSpinner1 =  false;
        this.snackBar.open('Please select a Use Case', '✖', {
          horizontalPosition: 'center',
          verticalPosition: 'top',
          duration: 3000,
        });
        return;
      }

      const params = new HttpParams()
        .set('userId', this.user)
        .set('useCaseName', this.selectedUseCase);

      this.https.get(this.PredictRiskUseCase, { params }).subscribe(
        (response) => {
          this.getAllData();
           this.showSpinner1 = false;
          console.log('Response:', response);
          this.snackBar.open('Processing started', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
          });
        },
        (error) => {
          this.showSpinner1 = false;
          console.error('API error:', error);
          this.snackBar.open('API Failed', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
          });
        }
      );
    }
  }


  onDialogSubmit(dialogRef: any) {
    // if (!this.busninessJustification || this.busninessJustification.trim() === '') {
      if (!this.BusinessJustificationForm.valid) {
      this.snackBar.open('Please fill all the Busniness Justification fields', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 5000,
      });
    } else {
      dialogRef.close(this.busninessJustification);
    }
  }

  // Handles the creation of a new use case
  handleCreateUsecase(){
    if (this.useCase.value.useCaseName == '' || this.useCase.value.useCaseName == null) {
      this.showSpinner1 =  false;
      this.snackBar.open('Please enter a Use Case Name', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return;
    }
    if (this.UsecaseType == '' || this.UsecaseType == null) {
      this.showSpinner1 =  false;
      this.snackBar.open('Please select a Usecase Type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return;
    }
    if (this.UsecaseType == 'Internal' && (this.Jurisdiction == '' || this.Jurisdiction == null)) {
      this.showSpinner1 =  false;
      this.snackBar.open('Please select a Jurisdiction', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return;
    };
    if (this.raiCanvasForm.invalid || this.aiCanvasForm.invalid) {
      this.snackBar.open('Please fill all the fields', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return
    }
     let apiModelPayload: any = {};

  // Loop through the number of models to dynamically build the payload
  for (let i = 1; i <= this.selectedModel; i++) {
    const formGroup = this.modelDetailForm[i];

    // Extract values from the form controls
    apiModelPayload[`ModelResponse${i}`] = {
      TypeOfAi: formGroup.get('TypeOfAIModel')?.value || 'None',
      ModelDescription: formGroup.get('ModelDescription')?.value || 'None',
      ModelInput: formGroup.get('ModelInput')?.value || 'None',
      OtherModelInput: formGroup.get('OtherModelInput')?.value || 'None',
      ModelOutput: formGroup.get('ModelOutput')?.value || 'None',
      OtherModelOutput: formGroup.get('OtherModelOutput')?.value || 'None',
    };
  }
    const payload = {
      UserId: this.user,
      usecaseName: this.useCase.value.useCaseName,
      usecaseType: this.UsecaseType,
      usecaseDescription: this.useCase.value.usecaseDescription,
      jurisdiction: this.Jurisdiction,
      datasetAnalyze: this.useCase.value.datasetAnalyze,
      AiCanvasResponse: this.aiCanvasForm.value,
      RaiCanvasResponse: this.raiCanvasForm.value
    };
    const finalPayload = {
      ...payload, // Spread the existing payload
      ...apiModelPayload // Add the dynamic model responses
    };    

    console.log(finalPayload)

    this.https.post(this.createPredictRisk, finalPayload).subscribe(
      (res: any) => {
        this.getUsecasesList();
        this.showSpinner1 = false;
        const message = "Usecase Added Successfully";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // Generates a compliance report
  generateComplianceReport(id: any){
    this.https.get(this.generateCompReport + '?batch_id=' + id).subscribe(
      (res: any) => {
        this.getAllData();
        const message = "Report Generation Started";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // Generates an impact report
  generateImpactReport(id: any){
    this.https.get(this.generateImpactRep + '?batch_id=' + id).subscribe(
      (res: any) => {
        this.getAllData();
        const message = "Report Generation Started";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // Downloads the risk mitigation report
  downloadRiskMitigation(id: any,data:any){
    if (data?.impact_assessment_data && data.impact_assessment_data.recommendation_report_url && data.impact_assessment_data.recommendation_report_url != null){
      this.getfileContent(data.impact_assessment_data.recommendation_report_url)
      return;
    }
    this.snackBar.open('Downloading started', '✖', {
      horizontalPosition: 'center',
      verticalPosition: 'top',
      duration: 3000,
    });
    this.https.get(this.recommendationRep + '?batch_id=' + id ).subscribe(
      (res: any) => {
        if (res.reportLink && res.reportLink != ''){
          this.getfileContent(res.reportLink)
        }else{
          this.snackBar.open('Try Again later', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
          });
        }
      },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  // Fetches compliance report recommendations
  complianceReportRecommnedation(id: any,data:any){
    console.log("COMPLIANCE REPORT RECOMMENDSTION")
    if (data && data.compliance_data.recommendations_url && data.compliance_data.recommendations_url != null){
      this.getfileContent(data.compliance_data.recommendations_url)
      return;
    }
    this.https.get(this.complianceRecommendations + '?batch_id=' + id).subscribe(
      (res: any) => {
        if (res.data && res.data != ''){
          this.getfileContent(res.data)
        }else{
          this.snackBar.open('Try Again later', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
          });
        }
      },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed";
        const action = "Close";
        this.snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      })
  }
    
  // Downloads the recommendation report 
  downloadRecomedationReport(id: any,data:any){
    if (data && data.compliance_data.status == 'Completed'){
      this.complianceReportRecommnedation(id,data)
    }
    if (data && data.impact_assessment_data.status == 'Completed'){
      this.downloadRiskMitigation(id,data)
    }
  }

// Handles the selection of an option
  selectOption(e: any) {
    console.log('Selected option ID:', e.value);
    this.selectedUseCase = e.value;
  }

  // Resets the file inputs
  reset(){
    this.files = [];
    this.demoFile = [];
    this.file = null;
  }

  // Returns the error message for a form control
  getErrorMessage(control: AbstractControl): string {
    if (control.hasError('required')) {
      return 'File is required.';
    } else {
      return 'Please enter a valid file.';
    }
  }

  // Fetches all data for the table
  getAllData(){
    this.https.get(this.getData + '?user_id='+ this.user).subscribe
    ((res: any)=>{
      this.dataSource = res;
      this.onTableDataChange(this.currentPage);
      this.isLoadingTable = false;
    }, error => {
      const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this.snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
    })
  }

  // Fetches the list of use cases
  getUsecasesList(){
    this.https.get(this.getUsecases + '?UserId='+ this.user).subscribe
    ((res: any)=>{
      this.usecasesList = res.data;
    }, error => {
      const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this.snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
    })
  }

  // Opens a file link in a new tab
  getfileContent(documentLink: string){
    console.log('Navigating to:', documentLink);
     // Validate URL to ensure it's safe
     const isValidUrl = this.validateUrl(documentLink);
     if (!isValidUrl) {
         console.error('Invalid or potentially unsafe URL:', documentLink);
         return;
     }
    const a = document.createElement('a');
    a.href = documentLink;
    a.target = '_blank'; // Open in a new tab
    a.click();
    //window.location.href = documentLink; 
  }
  
  // Toggles the switch state
  onToggleSwitch(event: Event): void {
    this.switch = (event.target as HTMLInputElement).checked;
    this.UcSwitch = false;
  }

  // Deletes a use case by ID
  delete(id: any){
   this.https.delete(this.deleteRisk + '?batch_id='+ id).subscribe((res:any)=>{
    this.getAllData();
   } , error => {
    const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
    const action = "Close"
    this.snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  })
  }
  isStartCompleted = false;
  isInProgressCompleted = false;

  // Marks the start step as completed
  completeStart() {
    this.isInProgressCompleted = true;
  }

  // Marks the in-progress step as completed
  completeInProgress() {
    this.isInProgressCompleted = true;
  }

  // Toggles the UC switch
  toggleUcSwitch() {
    this.UcSwitch = !this.UcSwitch;
  }

  // Handles the selection change for use case type
  onSelectChange(event: any) {
    this.UsecaseType = event.target.value;
  }

  // Handles the jurisdiction selection change
  onJurisdictionChange(event: any) {
    console.log(event)
    console.log("-----------------------")
    let ls:any[] = []
    this.select2.options.forEach((item: MatOption) => {
      if (item.selected){
        ls.push(item.value)
      }
    });
    console.log(ls)
    console.log("-------------------------------------------")
    this.Jurisdiction = ls;
  }

  // Checks if the AI Canvas step is active
  isAICanvasActive(stepper: MatStepper): boolean {
    return stepper.selectedIndex === 0;
  }

  // Checks if the RAI Canvas step is active
  isRAICanvasActive(stepper: MatStepper): boolean {
    return stepper.selectedIndex === 1; // RAI Canvas is the second step
}

 // Checks if the Model Detail step is active
isModelDetailActive(stepper: MatStepper): boolean {
    return stepper.selectedIndex === 2; // Model Detail is the third step
}

// Returns the icon margin based on use case type
  getIconMargin(): string {
    return this.UsecaseType === 'Internal' ? '40px' : '140px';
  }
  isEuropeanRegion(jurisdiction: string): boolean {
    jurisdiction = jurisdiction.toLowerCase();
    return jurisdiction === 'germany' || jurisdiction === 'france' || jurisdiction === 'italy';
  }

//  function to validate URL
validateUrl(url: any) {
  console.log("url:::",url)
  const pattern = /^https:\/\/rai-toolkit-(dev|rai)\.az\.ad\.idemo-ppc\.com.*/;
  return pattern.test(url);
}

}
