/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Component, Inject, Input, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { MatOption } from '@angular/material/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NgbPopover } from '@ng-bootstrap/ng-bootstrap';
import { UserValidationService } from 'src/app/services/user-validation.service';

@Component({
  selector: 'app-accounts-configuration-modal-create-template-update',
  templateUrl: './admin-template-update.html',
  styleUrls: ['./admin-template-update.css'],
  encapsulation: ViewEncapsulation.Emulated // This is the default setting
})
export class AccountsConfigurationModalCreateTemplateUpdateComponent {
  constructor(public dialogRef: MatDialogRef<AccountsConfigurationModalCreateTemplateUpdateComponent>, public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog,private validationService:UserValidationService
    , @Inject(MAT_DIALOG_DATA) public data: { id: any, account: any, portfolio: any }) {
    this.fromCreation();
  }

  closeDialog() {
    this.dialogRef.close();
  }


  @ViewChild('select1') select1!: MatSelect;
  @ViewChild('select2') select2!: MatSelect;
  @ViewChild('select3') select3!: MatSelect;
  result: any;
  dataSource_getBatches: any;
  templateMappingGetUrl: any;
  isLoading: boolean = true; // Add isLoading property


// SCREEN TWO ADD DATA
//--------------VARIABLES-----------SECURITY

selectedReclist: any = [];
selectedReclist2: any = [];
allSelected1: any;
listShowlist1 = new Set();
allSelectedInput = false;
event1: any;
c1: boolean = false;
allSelected2: any;
listShowlist2 = new Set();
allSelectedInput2 = false;
event2: any;
c2: boolean = false;
userId =""
tab="Privacy"
dataSource: any = []
listReconList: any=[];
  customTemplateGetUrl: string="";
  responseArr:any=[]
  requestArr:any=[]
  tempalteArray:any=[]
  templateMappingPostUrl=""
  template_admin_update_addTempMap=""
  template_admin_get_selected_getTempMap=""
  template_admin_delete_selected_removeTempMap=""
  selectedReclist3: any = [];
  allSelected3: any;
listShowlist3 = new Set();
allSelectedInput3 = false;
event3: any;
c3: boolean = false;
masterTemplateArr :any = ["Prompt Injection Check","Jailbreak Check","TOXICITY","PIIDETCT","REFUSAL","PROFANITY","RESTRICTTOPIC","Fairness and Bias Check"]
comparsionDropDownArr:any=[]
requestResonseDropDownArr:any=[]

  // select 1- Toggles all selections for the first dropdown
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

// Updates the selection status for the first dropdown
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

  // select 2- Toggles all selections for the second dropdown
  toggleAllSelection2(event: any) {
    this.event2 = event;
    this.c2 = event.checked;
    this.allSelected2 = !this.allSelected2;
    if (this.allSelected2) {
      this.select2.options.forEach((item: MatOption) => {
        item.select();
        this.listShowlist2.add(item.value);
        const element = document.querySelector('[role="listbox"]');
        if (element instanceof HTMLElement) {
          element.style.display = 'none';
        }
        this.select2.close();
      });
    } else {
      this.select2.options.forEach((item: MatOption) => {
        item.deselect();

        this.listShowlist2.delete(item.value);
      });
    }
  }

  // Updates the selection status for the second dropdown
  selectRecognizertype2() {
    let newStatus = true;
    this.select2.options.forEach((item: MatOption) => {
      if (!item.selected) {
        newStatus = false;
        this.allSelected2 = false;
        this.listShowlist2.delete(item.value);
      } else {
        this.listShowlist2.add(item.value);
      }
    });
    this.allSelectedInput2 = newStatus;
  }


    // select 1- Toggles all selections for the third dropdown
toggleAllSelection3(event: any) {
  this.event3 = event;
  this.c3 = event.checked;
  this.allSelected3 = !this.allSelected3;
  if (this.allSelected3) {
    this.select3.options.forEach((item: MatOption) => {
      item.select();
      this.listShowlist3.add(item.value);
      const element = document.querySelector('[role="listbox"]');
      if (element instanceof HTMLElement) {
        element.style.display = 'none';
      }
      this.select3.close();
    });
  } else {
    this.select3.options.forEach((item: MatOption) => {
      item.deselect();

      this.listShowlist3.delete(item.value);
    });
  }
}

 // Updates the selection status for the third dropdown
selectRecognizertype3() {
  let newStatus = true;
  this.select3.options.forEach((item: MatOption) => {
    if (!item.selected) {
      newStatus = false;
      this.allSelected3 = false;
      this.listShowlist3.delete(item.value);
    } else {
      this.listShowlist3.add(item.value);
    }
  });
  this.allSelectedInput3 = newStatus;
}

// Submits the template update form
  submit(){
    let payload ={
      "mapId":this.mapId,
      "userId": this.userId,
      "requestTemplate":this.templetUpdateFrom.get('requestTemplate')?.value,
      "responseTemplate":this.templetUpdateFrom.get('responseTemplate')?.value,
      "comparisonTemplate":this.templetUpdateFrom.get('comparisonTemplate')?.value
    }

    console.log("payload===",payload)
    this.patchtemplatet(payload)
  }

  // Sends a PATCH request to update the template
  patchtemplatet(payload: any){
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    // this.http.patch("https://rai-toolkit-dev.az.ad.idemo-ppc.com/api/v1/rai/admin/addTempMap", payload, { headers }).subscribe((res:any)=>{
    this.https.patch(this.template_admin_update_addTempMap, payload, { headers }).subscribe
    ((res:any)=>{
      console.log("res===",res)
      // this.dialogRef.close();
      const message = "Template Updated Successfully"
      this.getslectedDropdownvalues()
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });
    },(error)=>{
            // You can access status:
            console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass:['le-u-bg-black'],
            });})
  }

// Fetches template details
  getTemplateDetail(){
    // this.http.get(this.getUrl).subscribe
    // const getTemplateDetailLocalUrl="http://10.68.120.127:30016/api/v1/rai/admin/getCustomeTemplate/"
    this.https.get(this.customTemplateGetUrl+this.userId).subscribe
    ((res: any) => {

      this.result = res
      console.log("this.result===",this.result)
      this.dataSource_getBatches = res.templates;
      for(let i=0;i<this.dataSource_getBatches.length;i++){
        this.tempalteArray.push(this.dataSource_getBatches[i].templateName)

        // this.tempalteArray.push(this.)
      }
      this.comparsionDropDownArr = this.tempalteArray
      console.log("this.masterTemplateArr===",this.masterTemplateArr)
      this.tempalteArray = this.masterTemplateArr.concat(this.tempalteArray);
      console.log("this.tempalteArray===", this.tempalteArray);

    }  , error => {
      // You can access status:
      console.log(error)
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });

  })

}

// Retrieves the logged-in user from local storage
  getLogedInUser():any {
    let role = localStorage.getItem('role');
    console.log("role267===",role)  
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.userId = x ;
        return this.userId
      }
      console.log("userId", this.userId)
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
      this.templateMappingPostUrl=ip_port.result.Admin + ip_port.result.ACCTEMPMAP
    this.customTemplateGetUrl=ip_port.result.Admin + ip_port.result.TemplateGet
    this.templateMappingGetUrl=ip_port.result.Admin + ip_port.result.GETACCTEMPMAP
    this.template_admin_update_addTempMap = ip_port.result.Admin + ip_port.result.Template_admin_update_addTempMap
    this.template_admin_get_selected_getTempMap = ip_port.result.Admin + ip_port.result.Template_admin_get_selected_getTempMap
    this.template_admin_delete_selected_removeTempMap = ip_port.result.Admin + ip_port.result.Template_admin_delete_selected_removeTempMap

  }

  reset(){

  }

 // Initializes the component and sets up API lists
  ngOnInit(): void {
    this.isLoading = true
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()

    this.setApilist(ip_port)
    // this.getTemplateDetail()
    this.getslectedDropdownvalues()
    this.getTemplateDetailMultiple()
    this.getTemplateDetailSingle()
  }

  // Initializes the template update form
  templetUpdateFrom!: FormGroup;
  fromCreation() {


    this.templetUpdateFrom = new FormGroup({
      requestTemplate: new FormControl([], [Validators.required]),
      responseTemplate: new FormControl([], [Validators.required]),
      comparisonTemplate: new FormControl([], [Validators.required]),

    });
  }
  displayedColumns: string[] = [
     'subcategory',
    'requestTemplate', 'responseTemplate',
  ];
  mapId:any
  singleModelArray: any[] = [];
  multiModelArray: any[] = [];
  singleModelCategories: string[] = [];
  multiModelCategories: string[] = [];
  SinglemodelSubCetegories: any[] = [];
  SingletemplateSubCategories: any[] = [];

  TextTemplateCategories: any[] = [];
  TextModelCategories: any[] = [];
  imageCategories: any[] = [];
  ImageTemplateCategories: any[] = [];
  ImageModelCategories: any[] = [];

  account :any
  portfolio :any
  isDataEmpty: boolean = false;
 // Fetches selected dropdown values
  getslectedDropdownvalues(){
    const body = new URLSearchParams();
    body.set('accMasterId', this.data.id);


    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });
    // this.http.post("https://rai-toolkit-dev.az.ad.idemo-ppc.com/api/v1/rai/admin/getTempMap", body.toString(), { headers }).subscribe
    this.https.post(this.template_admin_get_selected_getTempMap, body.toString(), { headers }).subscribe
    ((res:any)=>{
      this.isLoading = false
      if (!res || res.length === 0) {
        this.isDataEmpty = true;
        this._snackBar.open('Value is not set. Create a mapping first.', 'Close', {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      } else {
        this.isDataEmpty = false;

      // this.responseArr=res
      // this.mapId=res[0].mapId
      // this.account=res[0].account
      // this.portfolio=res[0].portfolio

            this.singleModelArray = res.filter((item: { category: string; })  => item.category === 'SingleModel');
            this.multiModelArray = res.filter((item: { category: string; }) => item.category === 'MultiModel');
            this.singleModelCategories = [...new Set(this.singleModelArray.map(item => item.subcategory))];
            this.multiModelCategories = [...new Set(this.multiModelArray.map(item => item.subcategory))];
            console.log("this.singleModelArray===",this.singleModelArray)
            console.log("this.multiModelArray===",this.multiModelArray)

            // Segregate singleModelCategories into SinglemodelSubCetegories and SingletemplateSubCategories
            this.SinglemodelSubCetegories = this.singleModelArray.filter(item => item.subcategory === 'Model');
            this.SingletemplateSubCategories = this.singleModelArray.filter(item => item.subcategory === 'Template');
            console.log("this.SinglemodelSubCetegories===",this.SinglemodelSubCetegories)
            console.log("this.SingletemplateSubCategories===",this.SingletemplateSubCategories)

                    // Segregate multiModelCategories into TextTemplateCategories and imageCategories
        this.TextTemplateCategories = this.multiModelArray.filter(item => item.subcategory === 'TextTemplate');
        this.TextModelCategories = this.multiModelArray.filter(item => item.subcategory === 'TextModel');
        this.ImageTemplateCategories = this.multiModelArray.filter(item => item.subcategory === 'ImageTemplate');
        this.ImageModelCategories = this.multiModelArray.filter(item => item.subcategory === 'ImageModel');

        console.log("this.TextTemplateCategories===",this.TextTemplateCategories)
        console.log("this.TextModelCategories===",this.TextModelCategories)
        console.log("this.ImageTemplateCategories===",this.ImageTemplateCategories)
        console.log("this.ImageModelCategories===",this.ImageModelCategories)
      // this.templetUpdateFrom.get('requestTemplate')?.setValue(res[0].requestTemplate)
      // this.templetUpdateFrom.get('responseTemplate')?.setValue(res[0].responseTemplate)
      // this.templetUpdateFrom.get('comparisonTemplate')?.setValue(res[0].comparisonTemplate)
      this.templetUpdateFrom.patchValue({
        requestTemplate: res[0].requestTemplate,
        responseTemplate: res[0].responseTemplate,
        comparisonTemplate: res[0].comparisonTemplate
      });

      this.isLoading = false
    }

    },(error)=>{
            // You can access status:
            console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass:['le-u-bg-black'],
            });})

  }
  // new code

  RequestTextDropDownArr:any=["PromptInjection", "JailBreak", "Toxicity", "Piidetct", "Refusal", "Profanity", "RestrictTopic", "TextQuality", "CustomizedTheme"]
  ResponseTextDropDownArr:any=["Toxicity", "Piidetct", "Refusal", "Profanity", "RestrictTopic", "TextQuality", "TextRelevance"]

  RequestSingleModelDropDownArr:any=["PromptInjection", "JailBreak", "Toxicity", "Piidetct", "Refusal", "Profanity", "RestrictTopic", "TextQuality", "CustomizedTheme"]
ResponseSingleModelDropDownArr:any=["Toxicity", "Piidetct", "Refusal", "Profanity", "RestrictTopic", "TextQuality", "TextRelevance"]

RequestSingleTemplateDropDownArr:any=[]
ResponseSingleTemplateDropDownArr:any=[]
RequestMultipleTemplateDropDownArr:any=[]
ResponseMultipleTemplateDropDownArr:any=[]
RequestMultipleImageModelDropDownArr:any= [ "Privacy","Profanity"]

  options :any = ["Model","Template",]
  options3 :any =["TextTemplate","TextModel","ImageTemplate","ImageModel"]
  disabledsubcategoryList :any = []

  selectedOptions: { [key: string]: boolean } = {};
  selectedOptions3: { [key: string]: boolean } = {};

  onCheckboxChange(option: string, event: any) {
    if (event.checked) {
      this.selectedOptions[option] = true;
    } else {
      delete this.selectedOptions[option];
    }
    this.resetAll();
    this.handleSelectTypeChange();
  }

  resetAll() {
    // Your logic here
  }

  handleSelectTypeChange() {
    // Your logic here
  }

  selectedCategories2: { [key: string]: boolean } = {};

  onCheckboxChange2(option: string, event: any) {
    if (event.checked) {
      this.selectedCategories2[option] = true;
    } else {
      delete this.selectedCategories2[option];
    }
  }
  // for multimodel
  selectedCategories3: { [key: string]: boolean } = {};

  onCheckboxChange3(option: string, event: any) {
    if (event.checked) {
      this.selectedCategories3[option] = true;
    } else {
      delete this.selectedCategories3[option];
    }
  }

  oncheckboxChangeCategory(){
    const selectedValues = Object.keys(this.selectedCategories2).filter(key => this.selectedCategories2[key]);
    console.log("Selected options:", selectedValues);
  }
  isDisabled(option: string): boolean {
    const selectedValues = Object.keys(this.selectedCategories2).filter(key => this.selectedCategories2[key]);
    return !selectedValues.includes(option);
  }

  //
  selectedModelRequest: any[] = [];
  selectedModelResponse: any[] = [];
  selectedTemplateRequest: any[] = [];
  selectedTemplateResponse: any[] = [];
  selectedTextTemplateRequest: any[] = [];
  selectedTextTemplateResponse: any[] = [];
  selectedTextModelRequest: any[] = [];
  selectedTextModelResponse: any[] = [];
  selectedImageTemplateRequest: any[] = [];
  selectedImageModelRequest: any[] = [];

  @ViewChild('selectModelRequest1') selectModelRequest1!: MatSelect;
@ViewChild('selectModelResponse1') selectModelResponse1!: MatSelect;
@ViewChild('selectTemplateRequest1') selectTemplateRequest1!: MatSelect;
@ViewChild('selectTemplateResponse1') selectTemplateResponse1!: MatSelect;
@ViewChild('selectTextTemplateRequest1') selectTextTemplateRequest1!: MatSelect;
@ViewChild('selectTextTemplateResponse1') selectTextTemplateResponse1!: MatSelect;
@ViewChild('selectTextModelRequest1') selectTextModelRequest1!: MatSelect;
@ViewChild('selectTextModelResponse1') selectTextModelResponse1!: MatSelect;
@ViewChild('selectImageTemplateRequest1') selectImageTemplateRequest1!: MatSelect;
@ViewChild('selectImageModelRequest1') selectImageModelRequest1!: MatSelect;

allSelectedModelRequest1: any;
allSelectedModelResponse1: any;
allSelectedTemplateRequest1: any;
allSelectedTemplateResponse1: any;
allSelectedTextTemplateRequest1: any;
allSelectedTextTemplateResponse1: any;
allSelectedTextModelRequest1: any;
allSelectedTextModelResponse1: any;
allSelectedImageTemplateRequest1: any;
allSelectedImageModelRequest1: any;

listShowlistModelRequest1 = new Set();
listShowlistModelResponse1 = new Set();
listShowlistTemplateRequest1 = new Set();
listShowlistTemplateResponse1 = new Set();
listShowlistTextTemplateRequest1 = new Set();
listShowlistTextTemplateResponse1 = new Set();
listShowlistTextModelRequest1 = new Set();
listShowlistTextModelResponse1 = new Set();
listShowlistImageTemplateRequest1 = new Set();
listShowlistImageModelRequest1 = new Set();

  toggleAllSelectionModelRequest1(event: any) {
    this.toggleAllSelection(event, this.selectModelRequest1, this.listShowlistModelRequest1, 'allSelectedModelRequest1');
  }

  toggleAllSelectionModelResponse1(event: any) {
    this.toggleAllSelection(event, this.selectModelResponse1, this.listShowlistModelResponse1, 'allSelectedModelResponse1');
  }

  toggleAllSelectionTemplateRequest1(event: any) {
    this.toggleAllSelection(event, this.selectTemplateRequest1, this.listShowlistTemplateRequest1, 'allSelectedTemplateRequest1');
  }

  toggleAllSelectionTemplateResponse1(event: any) {
    this.toggleAllSelection(event, this.selectTemplateResponse1, this.listShowlistTemplateResponse1, 'allSelectedTemplateResponse1');
  }

  toggleAllSelectionTextTemplateRequest1(event: any) {
    this.toggleAllSelection(event, this.selectTextTemplateRequest1, this.listShowlistTextTemplateRequest1, 'allSelectedTextTemplateRequest1');
  }

  toggleAllSelectionTextTemplateResponse1(event: any) {
    this.toggleAllSelection(event, this.selectTextTemplateResponse1, this.listShowlistTextTemplateResponse1, 'allSelectedTextTemplateResponse1');
  }

  toggleAllSelectionTextModelRequest1(event: any) {
    this.toggleAllSelection(event, this.selectTextModelRequest1, this.listShowlistTextModelRequest1, 'allSelectedTextModelRequest1');
  }

  toggleAllSelectionTextModelResponse1(event: any) {
    this.toggleAllSelection(event, this.selectTextModelResponse1, this.listShowlistTextModelResponse1, 'allSelectedTextModelResponse1');
  }

  toggleAllSelectionImageTemplateRequest1(event: any) {
    this.toggleAllSelection(event, this.selectImageTemplateRequest1, this.listShowlistImageTemplateRequest1, 'allSelectedImageTemplateRequest1');
  }

  toggleAllSelectionImageModelRequest1(event: any) {
    this.toggleAllSelection(event, this.selectImageModelRequest1, this.listShowlistImageModelRequest1, 'allSelectedImageModelRequest1');
  }

  // Toggles all selections for a specific dropdown
  toggleAllSelection(event: any, select: MatSelect, listShowlist: Set<any>, allSelectedKey: keyof AccountsConfigurationModalCreateTemplateUpdateComponent & string) {
    (this as any)[allSelectedKey] = !(this as any)[allSelectedKey];
    if ((this as any)[allSelectedKey]) {
      select.options?.forEach((item: MatOption) => {
        item.select();
        listShowlist.add(item.value);
        const element = document.querySelector('[role="listbox"]');
        if (element instanceof HTMLElement) {
          element.style.display = 'none';
        }
        select.close();
      });
    } else {
      select.options?.forEach((item: MatOption) => {
        item.deselect();
        listShowlist.delete(item.value);
      });
    }
  }

  updateSelectionStatusModelRequest1() {
    this.updateSelectionStatus(this.selectModelRequest1, this.listShowlistModelRequest1, 'allSelectedModelRequest1');
  }

  updateSelectionStatusModelResponse1() {
    this.updateSelectionStatus(this.selectModelResponse1, this.listShowlistModelResponse1, 'allSelectedModelResponse1');
  }

  updateSelectionStatusTemplateRequest1() {
    this.updateSelectionStatus(this.selectTemplateRequest1, this.listShowlistTemplateRequest1, 'allSelectedTemplateRequest1');
  }

  updateSelectionStatusTemplateResponse1() {
    this.updateSelectionStatus(this.selectTemplateResponse1, this.listShowlistTemplateResponse1, 'allSelectedTemplateResponse1');
  }

  updateSelectionStatusTextTemplateRequest1() {
    this.updateSelectionStatus(this.selectTextTemplateRequest1, this.listShowlistTextTemplateRequest1, 'allSelectedTextTemplateRequest1');
  }

  updateSelectionStatusTextTemplateResponse1() {
    this.updateSelectionStatus(this.selectTextTemplateResponse1, this.listShowlistTextTemplateResponse1, 'allSelectedTextTemplateResponse1');
  }

  updateSelectionStatusTextModelRequest1() {
    this.updateSelectionStatus(this.selectTextModelRequest1, this.listShowlistTextModelRequest1, 'allSelectedTextModelRequest1');
  }

  updateSelectionStatusTextModelResponse1() {
    this.updateSelectionStatus(this.selectTextModelResponse1, this.listShowlistTextModelResponse1, 'allSelectedTextModelResponse1');
  }

  updateSelectionStatusImageTemplateRequest1() {
    this.updateSelectionStatus(this.selectImageTemplateRequest1, this.listShowlistImageTemplateRequest1, 'allSelectedImageTemplateRequest1');
  }

  updateSelectionStatusImageModelRequest1() {
    this.updateSelectionStatus(this.selectImageModelRequest1, this.listShowlistImageModelRequest1, 'allSelectedImageModelRequest1');
  }

   // Updates the selection status for a specific dropdown
  updateSelectionStatus(select: MatSelect, listShowlist: Set<any>, allSelectedKey: keyof AccountsConfigurationModalCreateTemplateUpdateComponent & string) {
    let newStatus = true;
    select.options?.forEach((item: MatOption) => {
      if (!item.selected) {
        newStatus = false;
        (this as any)[allSelectedKey] = false;
        listShowlist.delete(item.value);
      } else {
        listShowlist.add(item.value);
      }
    });
    (this as any)[allSelectedKey] = newStatus;
  }

   // Submits the single model template
  submitSingleModel() {
    const selectedModelRequest = this.selectedModelRequest;
    const selectedModelResponse = this.selectedModelResponse;
    const selectedTemplateRequest = this.selectedTemplateRequest;
    const selectedTemplateResponse = this.selectedTemplateResponse;

    // Process or log the selected values
    console.log('Selected Model Request:', selectedModelRequest);
    console.log('Selected Model Response:', selectedModelResponse);
    console.log('Selected Template Request:', selectedTemplateRequest);
    console.log('Selected Template Response:', selectedTemplateResponse);

    // Add further processing logic as needed
    let payload = {
      "userId": this.userId,
      "portfolio": "Infosys",
      "account": "IMPACT",
      "category": "SingleModel",
      "subcategory": "Template",
      "requestTemplate": [
        "string"
      ],
      "responseTemplate": [
        "string"
      ],
      "comparisonTemplate": [
        "string"
      ]
    }
  }

    // Submits the single model template based on subcategory
  submitSingleModelx(subcategory:any) {

    const selectedModelRequest = this.selectedModelRequest;
    const selectedModelResponse = this.selectedModelResponse;
    const selectedTemplateRequest = this.selectedTemplateRequest;
    const selectedTemplateResponse = this.selectedTemplateResponse;

    // Process or log the selected values
    console.log('Selected Model Request:', selectedModelRequest);
    console.log('Selected Model Response:', selectedModelResponse);
    console.log('Selected Template Request:', selectedTemplateRequest);
    console.log('Selected Template Response:', selectedTemplateResponse);

    // Add further processing logic as needed

    if (subcategory === 'Model') {
      console.log('Submitting for Model');
      // Add your logic for Model here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "SingleModel",
        "subcategory": "Model",
        "requestTemplate":selectedModelRequest,
        "responseTemplate": selectedModelResponse,
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else if (subcategory === 'Template') {
      console.log('Submitting for Template');
      // Add your logic for Template here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "SingleModel",
        "subcategory": "Template",
        "requestTemplate":selectedTemplateRequest,
        "responseTemplate": selectedTemplateResponse,
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else {
      console.log('Unknown value');
    }
  }

// Submits the multi-model template
  submitMultiModel() {
    const selectedTextTemplateRequest = this.selectedTextTemplateRequest;
    const selectedTextTemplateResponse = this.selectedTextTemplateResponse;
    const selectedTextModelRequest = this.selectedTextModelRequest;
    const selectedTextModelResponse = this.selectedTextModelResponse;
    const selectedImageTemplateRequest = this.selectedImageTemplateRequest;
    const selectedImageModelRequest = this.selectedImageModelRequest;

    // Process or log the selected values
    console.log('Selected Text Template Request:', selectedTextTemplateRequest);
    console.log('Selected Text Template Response:', selectedTextTemplateResponse);
    console.log('Selected Text Model Request:', selectedTextModelRequest);
    console.log('Selected Text Model Response:', selectedTextModelResponse);
    console.log('Selected Image Template Request:', selectedImageTemplateRequest);
    console.log('Selected Image Model Request:', selectedImageModelRequest);

    // Add further processing logic as needed
  }

  // Submits the multi-model template based on subcategory
  submitMultiModelx(subcategory:any) {
    const selectedTextTemplateRequest = this.selectedTextTemplateRequest;
    const selectedTextTemplateResponse = this.selectedTextTemplateResponse;
    const selectedTextModelRequest = this.selectedTextModelRequest;
    const selectedTextModelResponse = this.selectedTextModelResponse;
    const selectedImageTemplateRequest = this.selectedImageTemplateRequest;
    const selectedImageModelRequest = this.selectedImageModelRequest;

    // Process or log the selected values
    console.log('Selected Text Template Request:', selectedTextTemplateRequest);
    console.log('Selected Text Template Response:', selectedTextTemplateResponse);
    console.log('Selected Text Model Request:', selectedTextModelRequest);
    console.log('Selected Text Model Response:', selectedTextModelResponse);
    console.log('Selected Image Template Request:', selectedImageTemplateRequest);
    console.log('Selected Image Model Request:', selectedImageModelRequest);

    // Add further processing logic as needed
    if (subcategory === 'TextTemplate') {
      console.log('Submitting for TextTemplate');
      // Add your logic for TextTemplate here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "MultiModel",
        "subcategory": "TextTemplate",
        "requestTemplate":selectedTextTemplateRequest,
        "responseTemplate": selectedTextTemplateResponse,
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else if (subcategory === 'TextModel') {
      console.log('Submitting for TextModel');
      // Add your logic for TextModel here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "MultiModel",
        "subcategory": "TextTemplate",
        "requestTemplate":selectedTextModelRequest,
        "responseTemplate": selectedTextModelResponse,
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else if (subcategory === 'ImageTemplate') {
      console.log('Submitting for ImageTemplate');
      // Add your logic for ImageTemplate here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "MultiModel",
        "subcategory": "ImageTemplate",
        "requestTemplate":selectedImageModelRequest,
        "responseTemplate": [],
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else if (subcategory === 'ImageModel') {
      console.log('Submitting for ImageModel');
      // Add your logic for ImageModel here
      let payload = {
        "userId": this.userId,
        "portfolio": this.data.portfolio,
        "account": this.data.account,
        "category": "MultiModel",
        "subcategory": "ImageModel",
        "requestTemplate":selectedImageTemplateRequest,
        "responseTemplate": [],
        "comparisonTemplate": [
        ]
      }
      this.patchtemplatet(payload)
    } else {
      console.log('Unknown value');
    }
  }

  // Fetches multiple template details
  getTemplateDetailMultiple(){
    console.log("inside getTemplateDetailMultiple")
    let temptempalteArray:any= []
    // const url = 'http://localhost:30016/api/v1/rai/admin/getCustomeTemplate/';
    const url = this.customTemplateGetUrl;
    const params = new HttpParams()

      .set('category',"MultiModel");
    // let urlx = `${url}${this.userId}`
    let urlx = `${this.customTemplateGetUrl}${this.userId}`

    this.https.get(urlx, { params, headers: { 'accept': 'application/json' } })
      .subscribe
    // this.http.get(this.customTemplateGetUrl+this.userId+this.category).subscribe
    ((res: any) => {

      this.result = res
      console.log("this.result===",this.result)
      this.dataSource_getBatches = res.templates;
      for(let i=0;i<this.dataSource_getBatches.length;i++){
        temptempalteArray.push(this.dataSource_getBatches[i].templateName)
        // this.tempalteArray2.push(this.dataSource_getBatches[i].templateName)

        // this.tempalteArray.push(this.)
      }
      // this.requestDropDownArr = temptempalteArray
      this.RequestMultipleTemplateDropDownArr = temptempalteArray // for image template
      this.ResponseMultipleTemplateDropDownArr= temptempalteArray // for image template
      // this.resonseDropDownArr = temptempalteArray
      // this.comparsionDropDownArr = this.tempalteArray // made changes on 8/28/2024
      // this.comparsionDropDownArr = []
      console.log("this.masterTemplateArr===",this.masterTemplateArr)
      // this.tempalteArray = this.masterTemplateArr.concat(this.tempalteArray);  // made changes on 8/28/2024
      // console.log("this.tempalteArray===", this.tempalteArray);

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

}

// Fetches single template details
  getTemplateDetailSingle(){
    console.log("inside getTemplateDetail single")
    let temptempalteArray:any= []
    // const url = 'http://localhost:30016/api/v1/rai/admin/getCustomeTemplate/';
    const url = this.customTemplateGetUrl;
    const params = new HttpParams()

      .set('category',"SingleModel");
    // let urlx = `${url}${this.userId}`
    let urlx = `${this.customTemplateGetUrl}${this.userId}`

    this.https.get(urlx, { params, headers: { 'accept': 'application/json' } })
      .subscribe
    // this.http.get(this.customTemplateGetUrl+this.userId+this.category).subscribe
    ((res: any) => {

      this.result = res
      console.log("this.result===",this.result)
      this.dataSource_getBatches = res.templates;
      for(let i=0;i<this.dataSource_getBatches.length;i++){
        temptempalteArray.push(this.dataSource_getBatches[i].templateName)
        // this.tempalteArray2.push(this.dataSource_getBatches[i].templateName)

        // this.tempalteArray.push(this.)
      }
      // this.requestDropDownArr = temptempalteArray
      this.RequestSingleTemplateDropDownArr = temptempalteArray
      this.ResponseSingleTemplateDropDownArr= temptempalteArray

      // this.resonseDropDownArr = temptempalteArray
      // this.comparsionDropDownArr = this.tempalteArray // made changes on 8/28/2024
      // this.comparsionDropDownArr = []
      // console.log("this.masterTemplateArr===",this.masterTemplateArr)
      // this.tempalteArray = this.masterTemplateArr.concat(this.tempalteArray);  // made changes on 8/28/2024
      // console.log("this.tempalteArray===", this.tempalteArray);

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

}

// Deletes a specific template mapping
clickDeleteValue(category:any,subcategory:any,type:any,value:any){
  const url = this.template_admin_delete_selected_removeTempMap;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'accept': 'application/json'
    });
    const body = {
      userId: this.userId,
      portfolio: this.data.portfolio,
      account: this.data.account,
      category: category,
      subcategory: subcategory,
      tempType: type,
      templateName: value
    };

    this.https.delete(url, { headers: headers, body: body }).subscribe(
      response => {
        console.log('Delete successful', response);
        const message = "Data Deleted Successfully"
      this.getslectedDropdownvalues()
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });
    },(error)=>{
      // You can access status:
      console.log(error)
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass:['le-u-bg-black'],
      });});


}

@ViewChild('p') p!: NgbPopover;
@ViewChild('p2') p2!: NgbPopover;
@ViewChild('p3') p3!: NgbPopover;
@ViewChild('p4') p4!: NgbPopover;
@ViewChild('p5') p5!: NgbPopover;
@ViewChild('p6') p6!: NgbPopover;
// Toggles the popover for a specific subcategory
test(subcategory: string) {
  console.log('Subcategory:', subcategory);
  switch (subcategory) {
    case 'Model':
      this.togglePopover(this.p);
      break;
    case 'Template':
      this.togglePopover(this.p2);
      break;
    case 'TextTemplate':
      this.togglePopover(this.p3);
      break;
    case 'TextModel':
      this.togglePopover(this.p4);
      break;
      case 'ImageTemplate':
        this.togglePopover(this.p5);
        break;
      case 'ImageModel':
        this.togglePopover(this.p6);
        break;
      default:
        console.log('Unknown subcategory');
    }
  }

  private togglePopover(popover:any) {
    console.log('Popover:', popover);
    if (popover.isOpen()) {
      console.log('Popover is open');
      popover.toggle();
    } else {
      popover.toggle();
      console.log('Popover is closed');
    }
  }


}
