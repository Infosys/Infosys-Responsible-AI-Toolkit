/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, ViewChild,ElementRef  } from '@angular/core';
import { MatOption } from '@angular/material/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSelect, MatSelectChange } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { StructuredTextService } from '../structured-text/structured-text.service';
import { ConstantPool } from '@angular/compiler';
import * as saveAs from 'file-saver';
import { UserValidationService } from '../services/user-validation.service';
export interface Payload {
  title: string;
  userId: string;
  modelId: number;
  dataId: number;
  tenetName: string[];
  appAttacks?: string[];
  appExplanationMethods?: string[];
  biasType?: string;
  methodType?: string;
  taskType?: string;
  label?: string;
  favorableOutcome?: string;
  protectedAttribute?: any;
  privilegedGroup?: any;
  preProcessorId?: any;
  mitigationTechnique?: string;
  mitigationType?: string;
  knn?: any;
  predLabel?: string;
  favourableLabel?: string;
  sensitiveFeatures?:string[];
  categorical_attributes?:string[]

}
@Component({
  selector: 'app-structured-text-modal',
  templateUrl: './structured-text-modal.component.html',
  styleUrls: ['./structured-text-modal.component.css', './structured-text-modal.component.scss']
})
export class StructuredTextModalComponent {
  @ViewChild('select3') select3!: MatSelect;
  @ViewChild('select2') select2!: MatSelect;
  @ViewChild('selectRef') selectRef!: ElementRef;
  //-----------INITIAL VARIABLES----------------
  loggedin_userId: any;
  allTenants: any;
  apiEndpoints = {
    getAllData: '',
    getAllModels: '',
    getVector: '',
    allTenantsApi: '',
    security_applicableAttacks: '',
    fairnessSubmit: '',
    fairnessReport: '',
    ExplainMethods: '',
    batchGeneration: '',
    ExplainReport: '',
    PreAnalyze:'',
    PreMitigate:'',
    PostMitigate:'',
    PostAnalyze:'',
    GenAnalyze:'',
    GenMitigate:'',
    MitigateDownload:'',
    inProcessGenerate:'',
    inProcessDwnld:'',
    inProcessUpload:'',
    decisiveAuditApi:'',
    GenericAuditApi:''
  }
  givenTitle = '';
  KValue = 5;
  favorableLabel ='';
  predLabel = '';
  selectedPrivList:any =[];
  senValues:any;
  constructor(public dialogRef: MatDialogRef<StructuredTextModalComponent>, public structuredTextService: StructuredTextService, public _snackBar: MatSnackBar, public https: HttpClient,private validationService:UserValidationService) { }
  // INITIAL DATA FETCHING
  ngOnInit(): void {
    console.log("STRUCTURED TEXT")
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.loggedin_userId = x
        console.log(" userId", this.loggedin_userId)
      }
    }
    let ip_port: any
    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)

    this.getModels();
    this.getDataFiles();
    this.getAllTenants();
    this.getAllPreprocessor();
  }

  // Sets the API endpoints for the modal
  setApilist(ip_port: any) {
    this.apiEndpoints.security_applicableAttacks = ip_port.result.SecurityWrapper + ip_port.result.security_applicableAttack;
    this.apiEndpoints.getAllData = ip_port.result.Workbench + ip_port.result.Workbench_Data;
    this.apiEndpoints.getAllModels = ip_port.result.Workbench + ip_port.result.Workbench_Model;
    this.apiEndpoints.getVector = ip_port.result.Workbench + ip_port.result.Workbench_Vector;

    this.apiEndpoints.fairnessSubmit = ip_port.result.Fairness + ip_port.result.FairSubmit;
    this.apiEndpoints.fairnessReport = ip_port.result.Fairness + ip_port.result.FairGenReport;
    this.apiEndpoints.ExplainMethods = ip_port.result.Explainability_Demo + ip_port.result.ExplainWorkMethods;
    this.apiEndpoints.ExplainReport = ip_port.result.Explainability_Demo + ip_port.result.ExplainGenReport;
    this.apiEndpoints.allTenantsApi = ip_port.result.Workbench + ip_port.result.AllTenant;
    this.apiEndpoints.batchGeneration = ip_port.result.Workbench + ip_port.result.BatchGeneration;
    this.apiEndpoints.PreAnalyze = ip_port.result.Fairness + ip_port.result.PreAnalyze;
    this.apiEndpoints.PreMitigate = ip_port.result.Fairness + ip_port.result.PreMitigate;
    this.apiEndpoints.PostMitigate = ip_port.result.Fairness + ip_port.result.PostMitigate;
    this.apiEndpoints.PostAnalyze = ip_port.result.Fairness + ip_port.result.PostAnalyze;
    this.apiEndpoints.GenAnalyze = ip_port.result.Fairness + ip_port.result.GenAnalyze;
    this.apiEndpoints.GenMitigate = ip_port.result.Fairness + ip_port.result.GenMitigate;
    this.apiEndpoints.MitigateDownload = ip_port.result.Fairness + ip_port.result.MitigateDownload;
    this.apiEndpoints.inProcessGenerate =  ip_port.result.Fairness + ip_port.result.inProcessGenerate;
    this.apiEndpoints.inProcessDwnld = ip_port.result.Fairness + ip_port.result.inProcessDwnld;
    this.apiEndpoints.inProcessUpload = ip_port.result.Fairness + ip_port.result.InProcessUpload;
    this.apiEndpoints.decisiveAuditApi = ip_port.result.Fairness + ip_port.result.DecisiveAudit;
    this.apiEndpoints.GenericAuditApi = ip_port.result.Fairness + ip_port.result.GenericAudit;
    
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

  // Fetches all available models
  getModels() {
    // this.showSpinner1 = true;
    const formData = new FormData;
    formData.append("userId", this.loggedin_userId)
    this.https.post(this.apiEndpoints.getAllModels, formData).subscribe((res: any) => {
      this.allModels = (Array.isArray(res)) ? res : [];
      // this.showSpinner1 = false;
      console.log("ALL MODELS", this.allModels)

    }, error => {
      this.handleError(error)
    })
  }

  // Fetches all available data files
  getDataFiles() {
    const formData = new FormData;
    formData.append("userId", this.loggedin_userId)
    this.https.post(this.apiEndpoints.getAllData, formData).subscribe((res: any) => {
      this.allDataFiles = res;
      console.log(this.allDataFiles)
    }, error => {
      this.handleError(error)
    })
  }

  // Fetches all available preprocessors
  getAllPreprocessor() {
    const formData = new FormData;
    formData.append("userId", this.loggedin_userId)
    this.https.post(this.apiEndpoints.getVector, formData).subscribe(
      (res: any) => {
        this.allVectors = res;
      }, (error: any) => {
        this.handleError(error)
      }
    )
  }

  // Fetches all tenants
  getAllTenants() {
    this.https.get(this.apiEndpoints.allTenantsApi).subscribe((res: any) => {
      this.allTenants = res;
    })
  }

  // Fetches applicable attacks and methods based on the selected options
  applicableAttacksMethod() {
    const fdata = new FormData();
    fdata.append('TargetClassifier', this.selectedTargetClassifier)
    fdata.append('TargetDataType', this.selectedModelDataTypeValue)
    const payload = {
      "datasetId": this.selectedDataFileId,
      "modelId": this.selectedModelFileId,
      "scope": null
    }
    if (this.tenantarr.includes('Security')) {
      this.https.post(this.apiEndpoints.security_applicableAttacks, fdata).subscribe(
        (res: any) => {
          this.applicableAttack = res
          console.log(this.applicableAttack)
          // this.cdr.detectChanges();
        }, error => {
          this.handleError(error)
        }
      )
    }
    if (this.tenantarr.includes('Explainability')) {
      this.https.post(this.apiEndpoints.ExplainMethods, payload).subscribe(
        (data: any) => {
          this.applicableMethod = data.methods;
          // this.cdr.detectChanges();
        }
      )
    }
  }

  // Toggle Screens 
  currentScreen = 1;
  nextScreen() {
    if (this.currentScreen < 3 && this.tenantarr.length > 0) {
      if (this.currentScreen == 1) {
        this.applicableAttacksMethod();
      } else if (this.currentScreen == 2 && this.tenantarr.includes("Fairness") && this.fairnessType != 'audit') {
        console.log("FAIRNESS INCLUDES")
        this.fairSubmit();
      } else if (this.currentScreen == 2 && (this.tenantarr.includes("Fairness") && this.fairnessType == 'audit')) {
        this.onChange("audit");
      }
      this.currentScreen++;
    }
  }

  previousScreen() {
    if (this.currentScreen > 1) {
      this.currentScreen--;
    }
  }


  // INITIAL SELECT MODAL AND DATA FILE AND PREPROCESSOR Variables
  allModels: any = [];
  allDataFiles: any;
  allVectors: any;
  selectedDataFileId: number = 0;
  fairSampleId: any;
  selectedTargetClassifier: any;
  selectedModelDataTypeValue: any;
  selectedModelFileId: any;
  selectedVectorId: any = 0;
  options: any = ["Fairness", "Explainability", "Security"]
  selectedOptions: any = []
  tenantarr: any = [];


  // SCREEN TWO ADD DATA  
  //--------------VARIABLES-----------SECURITY
  selectedApplicableAttack: any;
  applicableAttack: any = [];
  allSelected1: any;
  listShowlist1 = new Set();
  allSelectedInput = false;
  event1: any;
  c1: boolean = false;
  // --------------VARIABLES------------EXPAINABILITY
  applicableMethod: any = [];
  selectedApplicableMethod: any;
  allSelected2 = false;
  event2: any;
  c2: boolean = false;
  listShowlist2 = new Set();
  allSelectedMethod: boolean = false;
  // --------------VARIABLES------------FAIRNESS
  public selectedBiasTypeOption: any;
  public selectTypeFairness: any = '';
  public selectedTaskTypeOption: any;
  public fairnessType: any;
  selectoption1: any;
  public selectTypeFairnessOptions: any[] = [
    { value: 'ANALYZE', viewValue: 'ANALYZE' },
    { value: 'MITIGATE', viewValue: 'MITIGATE' },
  ];

  public taskTypeOptions: any[] = [
    { value: 'CLASSIFICATION', viewValue: 'CLASSIFICATION' },
  ];
  public posttrain: any[] = [
    { value: 'STATISTICAL_PARITY', viewValue: 'STATISTICAL_ARITY' },
    { value: 'DISPARATE_IMPACT', viewValue: 'DISPARATE_IMPACT' },
    { value: 'FOUR_FIFTHS_RULE', viewValue: 'FOUR_FIFTHS_RULE' },
    { value: 'COHEN_D', viewValue: 'COHEN_D' },
    { value: 'EQUAL_OPPORTUNITY_DIFFERENCE', viewValue: 'EQUAL_OPPORTUNITY_DIFFERENCE' },
    { value: 'FALSE_POSITIVE_RATE_DIFFERENCE', viewValue: 'FALSE_POSITIVE_RATE_DIFFERENCE' },
    { value: 'FALSE_NEGATIVE_RATE_DIFFERENCE', viewValue: 'FALSE_NEGATIVE_RATE_DIFFERENCE' },
    { value: 'TRUE_NEGATIVE_RATE_DIFFERENCE', viewValue: 'TRUE_NEGATIVE_RATE_DIFFERENCE' },
    { value: 'AVERAGE_ODDS_DIFFERENCE', viewValue: 'AVERAGE_ODDS_DIFFERENCE' },
    { value: 'ACCURACY_DIFFERENCE', viewValue: 'ACCURACY_DIFFERENCE' },
    { value: 'Z_TEST_DIFFERENCE', viewValue: 'Z_TEST_DIFFERENCE' },
    { value: 'ABROCA', viewValue: 'ABROCA' },
    { value: 'ALL', viewValue: 'ALL' }

  ];
  public pretrain: any[] = [
    { value: 'STATISTICAL-PARITY-DIFFERENCE', viewValue: 'STATISTICAL-PARITY-DIFFERENCE' },
    { value: 'DISPARATE-IMPACT', viewValue: 'DISPARATE-IMPACT' },
    { value: 'SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS', viewValue: 'SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS' },
    { value: 'CONSISTENCY', viewValue: 'CONSISTENCY' },
    { value: 'BASE_RATE', viewValue: 'BASE_RATE' },
    { value: 'ALL', viewValue: 'ALL' }
  ]

  public mitigationTechOptions: any[] = [
    { value: 'REWEIGHING', viewValue: 'REWEIGHING' },
    // { value: 'DISPARATE IMPACT REMOVER', viewValue: 'DISPARATE IMPACT REMOVER' },
    // { value: 'CORRELATION REMOVER', viewValue: 'CORRELATION REMOVER' },
    // { value: 'LEARNING FAIR REPRESENTATION', viewValue: 'LEARNING FAIR REPRESENTATION' }
  ]
  selectedMitigationTechnique: any = '';
  public selectTypeAudit: any = '';


  handleError(error: any, customErrorMessage?: any) {
    console.log(error)
    console.log(error.status);
    console.log(error.error.detail);
    let message
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error.detail || error.error.message || "API has failed";
    }
    const action = 'Close';
    this.openSnackBar(message, action);
  }
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }



  // Toggles the selection of all security options
  toggleAllSelection1(event: any) {
    this.event1 = event;
    this.c1 = event.checked;
    this.allSelected1 = !this.allSelected1;
    if (this.allSelected1) {
      this.select2.options.forEach((item: MatOption) => {
        item.select();
        this.listShowlist1.add(item.value);
        const element = document.querySelector('[role="listbox"]');
        if (element instanceof HTMLElement) {
          element.style.display = 'none';
        }
        this.select2.close();
      });
    } else {
      this.select2.options.forEach((item: MatOption) => {
        item.deselect();

        this.listShowlist1.delete(item.value);
      });
    }
  }
  // Handles the selection of applicable security attacks
  selectApplicableAttackSecurity() {
    let newStatus = true;
    this.select2.options.forEach((item: MatOption) => {
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
   
  // Toggles the selection of all explainability options
  toggleAllSelection2(event: any) {
    this.event2 = event;
    this.c2 = event.checked;
    this.allSelected2 = !this.allSelected2;
    if (this.allSelected2) {
      this.select3.options.forEach((item: MatOption) => {
        item.select();
        this.listShowlist2.add(item.value);
        const element = document.querySelector('[role="listbox"]');
        if (element instanceof HTMLElement) {
          element.style.display = 'none';
        }
        this.select3.close();
      });
    } else {
      this.select3.options.forEach((item: MatOption) => {
        item.deselect();
        this.listShowlist2.delete(item.value);
      });
    }
  }

  // Handles the selection of applicable explainability methods
  selectApplicableMethod() {
    let newStatus = true;
    this.select3.options.forEach((item: MatOption) => {
      if (!item.selected) {
        newStatus = false;
        this.allSelected2 = false;
        this.listShowlist2.delete(item.value);
      } else {
        this.listShowlist2.add(item.value);
      }
    });
    this.allSelectedMethod = newStatus;
  }

  // --------------FUNCTIONS------------FAIRNESS
  // Handles the selection of bias type
  onSelectBiasType(e: any) {
    this.selectedBiasTypeOption = e.value;
  }
  // Handles the selection of task type
  onSelectTaskType(e: any) {
    this.selectedTaskTypeOption = e.value;
  }
  // Handles the selection of method type
  onSelectMethodType(e: any) {
    this.selectoption1 = e.value;
  }

  // Submits the fairness-related data for analysis or mitigation
  fairSubmit() {
    console.log(this.fairnessType, this.selectedTaskTypeOption, this.selectoption1)
    let fileData;
    let endpointUrl;
    if (this.fairnessType == 'preprocessing') {
      if (this.selectTypeFairness == 'MITIGATE') {
        endpointUrl = this.apiEndpoints.PreMitigate;
        fileData = new FormData();
        fileData.append('MitigationType', this.fairnessType);
        fileData.append('MitigationTechnique', this.selectedMitigationTechnique);
        fileData.append('fileId', this.fairSampleId);
        fileData.append('taskType', this.selectedTaskTypeOption);
      } else {
        endpointUrl = this.apiEndpoints.PreAnalyze;
        fileData = new FormData();
        fileData.append('biasType', "pretrain");
        fileData.append('methodType', this.selectoption1);
        fileData.append('fileId', this.fairSampleId);
        fileData.append('taskType', this.selectedTaskTypeOption);
      }
    } else if(this.fairnessType == 'postprocessing') {
      // if (this.selectTypeFairness == 'MITIGATE') {
      //   endpointUrl = this.apiEndpoints.PostMitigate;
      //   fileData = new FormData();
      // } 
        endpointUrl = this.apiEndpoints.PostAnalyze;
        fileData = new FormData();
        fileData.append('biasType', "posttrain");
        fileData.append('methodType', this.selectoption1);
        fileData.append('fileId', this.fairSampleId);
        fileData.append('taskType', this.selectedTaskTypeOption);   
    }
    // return
    this.structuredTextService.api(endpointUrl, fileData).subscribe({
     // next: (data: { AttributesInTheDataset: { CategoricalAttributesList: any;FeatureList :any; }; }) => {
        next: (data:any) => {
        console.log(data)      
        this.result = data;
        this.resultDummy = data.AttributesInTheDataset.CategoricalAttributesList
        this.resultLabel = data.AttributesInTheDataset.CategoricalAttributesList;
        this.predLabelList = data.AttributesInTheDataset["FeatureList "];
        this.labelOption = this.resultLabel
        this.listShowlistForLabelDummy = this.resultLabel
        this.featureDrop = true;
        this.labelDrop = true;
      }, error: error => {
        this.handleError(error)
      }
    })
  }


  // ----------------------SCREEN THREE---------------------------------------
  //-----------------VARIABLES----------------
  result: any;
  resultDummy: any;
  resultLabel: any;
  predLabelList: any;
  featureDrop: boolean = false;
  labelDrop: boolean = false;
  labelOption: [] = []
  listShowlistForLabelDummy = new Set();
  selectedLabel: any;

  resultFO: any;
  protectedResult: any;
  labelValue: any;
  nextFOButton: boolean = false;
  labelResult: any;
  listShowlistForLabel = new Set();

  fAValue: any;
  selectedFO: any;
  Protected: boolean = false;
  padata: boolean = false;
  temp: any;
  ladata: any;
  labeltemp: any;
  pAResult: any;
  ldata: any;
  listShowlistForFO = new Set();
  categoricalAttribute:any;
  categoricalAttrArray:any;
  protAttResult: any;
  protectedAttValue: any;
  selectedPAArray: any[] = [];
  priviDrop: boolean = false;
  protAttrArray: any = [];
  public pa: string[] = [];
  selectedProtAtt: any;
  i: number = 1;
  listShowlistForPA = new Set();
  palabeldata: any;
  priviRes: any;

  public pri: string[] = []
  privValue: any;
  selectedPriv: any;
  selectedPrivArray: any[] = [];
  public privAttArray: string[] = [];
  nextprivButton: boolean = false;
  nextprivButton1: boolean = false;
  finalSubmit: boolean = false;

  rows: any = [{ pa: '', priv: '', priviRes: [] }];

  // Handles the selection of a label
  optionClickFromLabel(e: any) {
    this.selectedLabel = e.value
    console.log(this.selectedLabel);
    console.log(this.resultLabel);
    if (this.fairnessType == 'preprocessing' || this.fairnessType == 'postprocessing'){
      this.getLabel(this.selectedLabel);
    }
  }

   // Retrieves the unique values for the selected label
  getLabel(selectedLbl: any) {
    this.resultFO = this.result.CategoricalAttributesUniqueValues[selectedLbl]
    this.protectedResult = this.resultFO
  }

  // Handles the selection of a predicted label
  optionClickPredLabel(e: any) {
    this.predLabel = e.value
    console.log("predLabel::",this.predLabel);
  }

  // Handles the selection of a favorable outcome
  optionClickFromFO(e: any) {
    console.log("______________ SECOND")
    console.log(e.value)
    this.selectedFO = e.value
    console.log(this.selectedLabel)
    console.log(this.selectedFO)
    console.log(this.resultLabel)
    // this.fAValue = this.listShowlistForFO.values().next().value
    // this.fAValue = this.selectedFO
    // console.log("fAValue=====",this.fAValue);
    // this.protAttDrop = true
    // this.allSelectedFromPA = newStatus;
    this.getProtectedAttribute();
    // Get the DOM element by role
    // const element = document.querySelector('[role="listbox"]');
    // // Add a style to the div
    // if (element instanceof HTMLElement) {
    //   element.style.display = 'none';
    // }
  }

  // Retrieves the protected attributes for the selected label
  getProtectedAttribute() {
    const fo = this.selectedLabel
    let temp = this.result.AttributesInTheDataset.CategoricalAttributesList;
    // this.ladata = fo
    let tempCopy = [...temp];
    tempCopy.splice(tempCopy.indexOf(fo), 1);
    this.labeltemp = fo
    this.pAResult = tempCopy
    console.log(this.pAResult)
    // this.ldata = this.labelValue
    // this.resultDummy = this.resultLabel
  }

  // Handles the selection of a protected attribute
  optionClickFromPA(e: any, index: any) {
    // console.log(r,"_______________________________")
    this.selectedProtAtt = e.value
    this.rows[index].pa = e.value;
    console.log(e.value)
    console.log(this.selectedProtAtt)
    let r = this.getPriviledged();
    this.rows[index].priviRes = r; // Fix: Added 'priviRes' property to 'rows' array
    this.protAttResult = this.listShowlistForPA
    this.protectedAttValue = this.selectedProtAtt
    this.selectedPAArray.push(this.selectedProtAtt)
    this.priviDrop = true
    this.protAttrArray[this.i - 1] = this.protectedAttValue
    this.pa.push(this.protectedAttValue)
    const fo = this.selectedProtAtt
    this.palabeldata = fo
    this.protectedAttValue = ""
    this.temp = this.result.AttributesInTheDataset.CategoricalAttributesList;
    this.getPriviledged()
  }

  // Retrieves the privileged groups for the selected protected attribute
  getPriviledged() {
    // this.privDrop = true
    const fo = this.selectedProtAtt
    const temp = this.result.CategoricalAttributesUniqueValues[fo]
    console.log(fo, temp)
    let tempCopy = [...temp];
    tempCopy.splice(tempCopy.indexOf(fo), 1);
    // this.priviRes = tempCopy
    return tempCopy
    // this.selectedProtAtt = ""
  }

  // optionClickFromPriv(e: any, index: any) {
  //   this.selectedPriv = e.value
  //   this.rows[index].priv = e.value;
  //   this.pri = []
  //   this.privValue = this.selectedPriv
  //   this.selectedPrivArray.push(this.selectedPriv)
  //   this.privAttArray[this.i - 1] = this.privValue
  //   this.pri.push(this.privValue)
  //   // this.priviRes = []
  //   // this.nextprivButton = false
  //   // this.nextprivButton1 = true
  //   // this.finalSubmit = true
  //   // this.selectedPriv = ""
  // }

  // Handles the selection of privileged groups
  optionClickFromPriv(event: MatSelectChange,index: any) {
    const selectedValues = event.value;
    console.log("PRIV LIST::", selectedValues);
    this.rows[index].priv = selectedValues;
    }

// Adds a new row for protected attributes and privileged groups
  addRow() {
    this.rows.push({ pa: '', priv: '', priviRes: [] });
    console.log(this.rows)
  }

  // FUNCTION TO HANDLE SELECT MODAL AND DATA FILE CHANGE 
  selectDataMethod(data: any) {
    let selectedOptionIndex = data.options['selectedIndex']
    this.selectedDataFileId = data.options[selectedOptionIndex].id;
    this.fairSampleId = data.options[selectedOptionIndex].value;
    console.log("selectedDataFileId::", this.selectedDataFileId)
    console.log("selectedSampleFilesID::", this.fairSampleId)
    //const element = document.querySelector('[role="listbox"]');
    //if (element instanceof HTMLElement) {
    //  element.style.display = 'none';
    //}
  }

  // Handles the selection of a model
  async selectModelMethod(optionValue: any) {
    console.log(optionValue.value)
    let filteredModels = this.allModels.filter((r: any) => r.modelId == optionValue.value);
    console.log(filteredModels)
    optionValue = filteredModels[0]
    this.selectedTargetClassifier = optionValue.targetClassifier;
    this.selectedModelDataTypeValue = optionValue.targetDataType;
    this.selectedModelFileId = optionValue.modelId;
  }

  // Handles the selection of a vector
  selectVectorMethod(vectorValue: any) {
    console.log("vectorValue", vectorValue.value)
    this.selectedVectorId = vectorValue.value;
  }

  // CLOSE MODAL
  closeDialog() {
    this.dialogRef.close();
  }
  // --------------Handle Checkbox Selections------------------
  viewoptions() {
    console.log("Array===", this.selectedOptions)
    // [Privacy: true, Profanity: true, Explainability: true, FM-Moderation: true]
    const myObject = { ...this.selectedOptions };
    console.log("myObject===", myObject)
    const filteredKeys = this.filterKeysByBoolean(myObject);
    console.log("only keys", filteredKeys);
    this.tenantarr = filteredKeys
  }
  filterKeysByBoolean(obj: Record<string, boolean>): string[] {
    return Object.keys(obj).filter((key) => obj[key]);
  }

  //--------------HANDLE FINAL SUBMIT----------------
  onUpload() {
    console.log("selectedApplicableAttack::", this.selectedApplicableAttack)
    console.log("selectedApplicableMethod:", new Array(this.selectedApplicableMethod))
    console.log("rows::",this.rows);
    let protectedAttributesArr: any = [];
    let privilegedGroupArr: any = [];
    this.rows.forEach((row: any) => {
      protectedAttributesArr.push(row.pa);
      privilegedGroupArr.push(row.priv);
    });
    const payload: Payload = {
      "title": this.givenTitle,
      "userId": this.loggedin_userId,
      "modelId": this.selectedModelFileId,
      "dataId": this.selectedDataFileId,
      "tenetName": this.tenantarr,
    }
    if (payload.tenetName.includes('Security')) {
      payload.appAttacks = this.selectedApplicableAttack;
    }
    if (payload.tenetName.includes('Explainability')) {
      payload.appExplanationMethods = this.selectedApplicableMethod;
    }
    if (payload.tenetName.includes('Fairness')) {
      payload.biasType = this.fairnessType == 'preprocessing' ? 'PRETRAIN' : 'POSTTRAIN';
      payload.methodType = this.selectoption1 ? this.selectoption1 : 'ALL';
      payload.taskType = this.selectedTaskTypeOption ? this.selectedTaskTypeOption : "" ;
      payload.label = this.selectedLabel;
      payload.favorableOutcome = this.selectedFO ? this.selectedFO : "";
      // payload.protectedAttribute = JSON.stringify(protectedAttributesArr)
      // payload.privilegedGroup = JSON.stringify(privilegedGroupArr);
       payload.protectedAttribute =  this.fairnessType =='audit'? this.categoricalAttribute : protectedAttributesArr;
      payload.privilegedGroup = ( this.fairnessType == 'inprocessing' || this.fairnessType == 'audit') ? [[""]]: privilegedGroupArr;
      payload.mitigationType = this.fairnessType.toUpperCase();
      payload.mitigationTechnique = this.selectedMitigationTechnique;
      payload.knn = this.KValue;
      payload.predLabel = this.predLabel?this.predLabel : 'NA';
      payload.favourableLabel = this.favorableLabel;
      payload.sensitiveFeatures = this.senValues;
      // payload.methodType = ALL,
      if(this.fairnessType =='audit'){
        payload.methodType = this.selectTypeAudit;
      }
    }
    if (this.selectedVectorId != 0) {
      payload.preProcessorId = this.selectedVectorId;
    }
    console.log("PAYLOADS::", payload)
    this.https.post(this.apiEndpoints.batchGeneration, payload).subscribe((res: any) => {
      console.log
      this._snackBar.open("Batch Added Successful", "Close", {
        duration: 3000,
        horizontalPosition: 'center',
        panelClass: ['le-u-bg-black'],
      });

     
      this.closeDialog()
    }, error => {
      this.handleError(error)
    })

  }

  // Calls the batch generation API for fairness
  callBatchGenerationFairness(batchId: any) {
    this.structuredTextService.api(this.apiEndpoints.inProcessGenerate,{Batch_id:batchId}).subscribe({
          next: (data: any) => {
            console.log(data);
            const fileName = data?.modelfileId;
            console.log("data::",fileName);
            this._snackBar.open("InProcess Report Generated", "Close", {
              duration: 3000,
              horizontalPosition: 'center',
              panelClass: ['le-u-bg-black'],
            });
            this.https.get(this.apiEndpoints.inProcessDwnld + fileName, { responseType: 'blob' }).subscribe
            ((response: Blob)=>{
            //const blob = new Blob([response], { type: 'text/csv' });
             saveAs(response, fileName);
           })
        }, error: error => {
          this.handleError(error)
        }
      })
           // this.http.get(this.apiEndpoints.inProcessDwnld).subscribe(())
    // if (this.selectTypeFairness == 'ANALYZE') {
    //   this.structuredTextService.api(this.apiEndpoints.GenAnalyze,{Batch_id:batchId}).subscribe({
    //     next: (data: any) => {
    //       console.log(data)
    //     }, error: error => {
    //       this.handleError(error)
    //     }
    //   })
    // } else if (this.selectTypeFairness == 'MITIGATE') { 
    //   this.structuredTextService.api(this.apiEndpoints.GenMitigate, { Batch_id: batchId }).subscribe({
    //     next: (data: any) => {
    //       console.log(data);
    //      const mitigatedFile = data[1]!;
    //      this.http.get(this.apiEndpoints.MitigateDownload + mitigatedFile, { responseType: 'text' }).subscribe
    //         ((response: any)=>{
    //         const blob = new Blob([response], { type: 'text/csv' });
    //          saveAs(blob, mitigatedFile);
    //        })
    //     }, error: error => {
    //       this.handleError(error)
    //     }
    //   })
    // }
  }

  // Calls the batch audit API
  callBatchAudit(url:any,batchId: any){
    this.https.post(url,{Batch_id:batchId}).subscribe((data:any)=>{
      this._snackBar.open("Report Generated Successfully", "Close", {
        duration: 3000,
        horizontalPosition: 'center',
        panelClass: ['le-u-bg-black'],
      });
    }, error => {
      this.handleError(error)
    })
  }
  // --------------VALIDATION-------------------------
  isScreen1Valid() {
    console.log(this.tenantarr)
    console.log("selectedDataFileId", this.selectedDataFileId, this.tenantarr.length, this.tenantarr.includes("Fairness"))
    if (!(this.tenantarr.length == 1 && this.tenantarr.includes("Fairness"))) {
      console.log("INSIDE")
      console.log(this.selectedModelFileId)
      if (!this.selectedModelFileId) {
        return false;
      }
    }
    if (this.selectedDataFileId == 0) {
      return false;
    }
    // if (this.selectedDataFileId == 0) {
    //   return false;
    // }

    // Check if at least one type is selected
    if (this.tenantarr.length == 0) {
      return false;
    }
    if (this.givenTitle.length == 0) return false;
    return true;
  }
  isScreen2Valid() {
    // Check if all the required details are provided in the Security section
    if (this.tenantarr.includes('Security') && (!this.selectedApplicableAttack || this.selectedApplicableAttack.length === 0)) {
      this.getSecuityOptionsSelected();
      return false;
    }
    // Check if all the required details are provided in the Explainability section
    if (this.tenantarr.includes('Explainability') && (!this.selectedApplicableMethod || this.selectedApplicableMethod.length === 0)) {
      return false;
    }
    // Check if all the required details are provided in the Fairness section
    // if (this.tenantarr.includes('Fairness') && (!this.selectedBiasTypeOption || !this.selectedTaskTypeOption || !this.selectoption1)) {
    //   return false;
    // }
    // if (this.tenantarr.includes('Fairness') && (this.fairnessType == 'audit' &&  this.selectTypeAudit == '')) {
    //   return false;
    // }
    return true;
  }
  isScreen3Valid(): boolean {
    if(this.fairnessType == 'audit'){
      return true
    }
    if (!this.selectedLabel) {
      return false;
    }
    if (!this.selectedFO) {
      return false;
    }
    // Check if data in the Protected Attribute and Privileged selects for each row is selected
    if(this.fairnessType != 'audit'){
    for (let row of this.rows) {
      if (!row.pa || !row.priv) {
        return false;
      }
    }
  }
    return true;
  }

  // Logs the selected label and favorable outcome
  onUpload1(){
  console.log("selectedLabel::",this.selectedLabel);
  console.log("selectedFO::",this.selectedFO);
 // console.log("categoricalAttribute::",this.categoricalAttrArray);
  }

  // Converts the categorical attribute input to an array
  convertToArrayForCategory() {
    const a= this.categoricalAttribute;
    if (/^\d+(,\d+)*$/.test(a)) {
      this.categoricalAttrArray = a.split(',').map(Number);
    }
    else{
      this.categoricalAttrArray = a.split(',');
    }
  }

// Handles changes for fairness type
onChange(type: string){
   console.log("Type:",type)
  const endpointUrl =  this.apiEndpoints.inProcessUpload;
 const fileData = new FormData();
  fileData.append('fileId',this.fairSampleId);
  this.structuredTextService.api(endpointUrl, fileData).subscribe({
       next: (data:any) => {
       console.log(data)
         this.resultLabel = data['feature_list'];      
     }, error: error => {
       this.handleError(error)
     }
   })
  }

  // Selects all security options
  getSecuityOptionsSelected() {
    this.allSelected1 = true;
    this.select2?.options?.forEach((item: MatOption) => {
      item.select();
      this.listShowlist1.add(item.value);
    });
  }
}
