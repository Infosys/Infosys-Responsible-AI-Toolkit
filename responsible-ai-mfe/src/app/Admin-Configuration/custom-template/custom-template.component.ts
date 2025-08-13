/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormControlName, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
// import { PagingConfig } from '../_models/paging-config.model';
import { TemplateDataComponent } from '../template-data/template-data.component';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { SharedService } from '../configuration-parent/shared.service';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';
// PagingConfig

@Component({
  selector: 'app-custom-template',
  templateUrl: './custom-template.component.html',
  styleUrls: ['./custom-template.component.css']
})
export class CustomTemplateComponent implements OnInit, PagingConfig {
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  userId: any;
  result: any;
  dataSource_getBatches:any=[];
  dataSource_getBatches_filter:any=[];
  spinner=false
  modeArr: any = ["Private","Public"]
  templateSubTypeArr: any = ["evaluation_criteria","prompting_instructions","few_shot_examples"]
  Account_options=[]
  customTemplatePostUrl=""
  customTemplatePatchUrl_updateCustomeTemplate=""
  customTemplateGetUrl=""
  customTemplateDeleteUrl=""
  customTemplateUpdateUrl=""
  customTemplateTest =false
  selectedPrompt = '';
  templateMode:any
  templateType:any
  templateData:any
  templateNameValue:any
  pagingConfig: PagingConfig = {} as PagingConfig;
  tableSize: number[] = [5, 10, 15, 20];
  prevSubTemplate:any="evaluation_criteria"
  toggleButton = false
  templateSubmitFlag = false
  isLoadingSelectType = true;
  tenantarr: any = []
  selectedOptions: any = []
  isRoleAdmin:any
  templateNameArray:any=[]
  newTemplateName:any
  showSpinner: boolean = false;
  modeValidation = false
  categoryValidation = false
  category = false
  templateNameValidation = false
  templateDescValidation = false
  // For search bar
  searchQuery: string = '';
  filteredItems: string[] = [];
  isSearchOpen: boolean = false;
  filteredUsers:any;
  
  
  options:any = ["Prompt Injection Check","Jailbreak Check","TOXICITY","PIIDETCT","REFUSAL","PROFANITY","RESTRICTTOPIC","Fairness and Bias Check"]
  masterTemplateArr :any = ["Prompt Injection Check","Jailbreak Check","TOXICITY","PIIDETCT","REFUSAL","PROFANITY","RESTRICTTOPIC","Fairness and Bias Check"]
  // options: any = [ "PROMPT INJECTION CHECK", "Jailbreak Check CHECK","PROFANITY CHECK","PRIVACY CHECK","RESTRICTED TOPIC CHECK"]
  prompt_instToggle = true
  evaluation_criteriaToggle = false
  few_shot_exampleToggle=false
  map = new Map<String, String>();
  loadTemplate: any;

  constructor (public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog,private sharedService: SharedService,public nonceService:NonceService,private validationService:UserValidationService){
    this.formCreation()
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }

    console.log("pagingConfig===",this.pagingConfig)
  }

  // CustomTemplateForm!: FormGroup;

  
  CustomTemplateForm!: FormGroup;
// Creates the form for custom templates
  formCreation(){
      let role = localStorage.getItem('role');
      let v  = { value: '', disabled: false }
      if(role!== '"ROLE_ADMIN"'){
        this.isRoleAdmin=true
        v = {value:'General',disabled:true}
      }
     this.CustomTemplateForm= new FormGroup({
      mode: new FormControl({ value: v, disabled: this.formupdatedisbaled }, [Validators.required]),
      category: new FormControl({ value: v, disabled: this.formupdatedisbaled }, [Validators.required]),
      
      TemplateName : new FormControl({ value: '', disabled: this.formupdatedisbaled }, [Validators.required]),
      TemplateDesc:new FormControl('', [Validators.required]),
      // TemplateData : new FormControl('', [Validators.required]),
      
      promtInstruction : new FormControl('',[Validators.required]),
      evalutionCriteria : new FormControl('',[Validators.required]),
      fewShotExample : new FormControl('',[Validators.required]),

    })
  }


viewoptions() {
  // console.log("Array===",this.selectedOptions)
  // [Privacy: true, Profanity: true, Explainability: true, FM-Moderation: true]
  const myObject = { ...this.selectedOptions };
  console.log("myObject===", myObject)
  const filteredKeys = this.filterKeysByBoolean(myObject);
  console.log("only keys",filteredKeys);
  this.tenantarr = filteredKeys
  console.log("tenantarr===",this.selectedOptions)
}

// Filters keys from an object based on boolean values
filterKeysByBoolean(obj: Record<string, boolean>): string[] {
  return Object.keys(obj).filter((key) => obj[key]);
}

// Resets the result data based on the selected template
resetResultData(template:any){
  console.log("template===",template)
  this.CustomTemplateForm.patchValue({
    TemplateData: ""
  });
  if(template == "evaluation_criteria"){
    this.CustomTemplateForm.patchValue({
      testTemplate2: false
    });
    // this.CustomTemplateForm.patchValue({this.CustomTemplateForm.value.TemplateData : ""})
    this.prompt_instToggle = false
    this.few_shot_exampleToggle=false
    this.evaluation_criteriaToggle = true
  }else if(template == "few_shot_examples"){
    // this.CustomTemplateForm.patchValue({
    //   testTemplate: template
    // });
    this.CustomTemplateForm.patchValue({
      testTemplate1: false
    });
    this.prompt_instToggle = false
    this.evaluation_criteriaToggle = false
    this.few_shot_exampleToggle=true
  }

}

// Handles changes in the textarea and updates the map
handleTextareaChange(event:any){
  const value = event.target.value;
  console.log("prompting_instructions===",this.prompt_instToggle)
  console.log("evaluation_criteriaToggle===",this.evaluation_criteriaToggle)
  console.log("few_shot_examples===",this.few_shot_exampleToggle)
  if(this.prompt_instToggle){
    this.map.set("prompting_instructions",value)
  }else if(this.evaluation_criteriaToggle){
    this.map.set("evaluation_criteria",value)
  }else if(this.few_shot_exampleToggle){
    this.map.set("few_shot_examples",value)
  
  }
  console.log("map===",this.map)
}

// Checks if a template name already exists
isTemplateNameExists(templateName: string): boolean {
  if(this.formupdatedisbaled)
  return false
else
  return this.templateNameArray.includes(templateName);
}


  Check(){
    console.log("this. tmeplateNmae Valeu=====",this.templateNameValue)
  }

// Saves the custom template data
  save(){
    console.log("this.CustomTemplateForm.value===",this.CustomTemplateForm.value)
    if(this.CustomTemplateForm.get('category')?.invalid){
      this.categoryValidation = true
    }
    if(this.CustomTemplateForm.get('mode')?.invalid){
      this.modeValidation = true
    }
    if(this.CustomTemplateForm.get('TemplateName')?.invalid){
      this.templateNameValidation = true
    }
    if(this.CustomTemplateForm.get('TemplateDesc')?.invalid){
      this.templateDescValidation = true
    }

    if(this.categoryValidation||this.modeValidation || this.templateNameValidation || this.templateDescValidation){
      return ;
    }

  //  if(this.CustomTemplateForm.get('mode')?.invalid || this.CustomTemplateForm.get('TemplateName')?.invalid || this.CustomTemplateForm.get('TemplateDesc')?.invalid ){
  //   this._snackBar.open("Please fill all the field", "Close", {
  //     duration: 2000,
  //   });

  //   return;
  //  }
   

    this.templateSubmitFlag=false
    this.showSpinner = true
    console.log("this.CustomTemplateForm.value===",this.CustomTemplateForm.valid)

   

    const subTemp = []
    const subTemplateData = []

    const obj = {
            "prompting_instructions": this.CustomTemplateForm.value.promtInstruction,
            "evaluation_criteria":this.CustomTemplateForm.value.evalutionCriteria,
            "few_shot_examples":this.CustomTemplateForm.value.fewShotExample
    }

    for (let [key, value] of Object.entries(obj)) {
      subTemplateData.push({"subtemplate":key,"templateData":value})
      console.log("Key:", key);
      console.log("Value:", value);
    }
    for(let i of this.map){
      // console.log("i===",i)
      subTemp.push({"subtemplate":i[0],"templateData":i[1]})
    }
    console.log("subTemp===",subTemp)
    console.log("subTemplateData===",subTemplateData) 
    console.log("mode value==========",this.CustomTemplateForm.get('mode')?.value)
    console.log("customeTemplate value==========",this.CustomTemplateForm.value)
    const payload1 = {
      "userId": this.userId,
      "category": this.CustomTemplateForm.get('category')?.value,
      "mode": this.CustomTemplateForm.get('mode')?.value,
      "description":this.CustomTemplateForm.value.TemplateDesc,
      // "templateType": this.CustomTemplateForm.value.template_type,
      "templateName": this.CustomTemplateForm.get('TemplateName')?.value,
      "subTemplates" :subTemplateData,
      // "masterTemplateList": this.tenantarr
      
      // "templateData": this.CustomTemplateForm.value.TemplateData
    }

    console.log("payload1=======" ,payload1)
    console.log("payload1======= template name" ,this.CustomTemplateForm.get('TemplateName')?.value)

    if(this.updatecall){
      this.https.patch(this.customTemplatePatchUrl_updateCustomeTemplate,payload1).subscribe((res)=>{
        console.log("res=================",res)
        // this.CustomTemplateForm.reset()
        this.showSpinner = false
        this.resetData();
        this.getTemplateDetail()
        this.LoadTemplateData()
        this._snackBar.open("Template Saved Successfully", "Close", {
          duration: 2000,
        });
      }, error => {
        // You can access status:
        console.log(error.status);
  
  
        // console.log(error.error.detail)
        console.log(error)
        this.showSpinner = false
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
  
  
      })
    }else{
    this.https.post(this.customTemplatePostUrl,payload1).subscribe((res)=>{
      console.log("res=================",res)
      // this.CustomTemplateForm.reset()
      this.showSpinner = false
      this. resetData();
      this.getTemplateDetail()
      this.LoadTemplateData()
      this._snackBar.open("Template Saved Successfully", "Close", {
        duration: 2000,
      });
    }, error => {
      // You can access status:
      console.log(error.status);


      // console.log(error.error.detail)
      console.log(error)
      this.showSpinner = false
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });


    })}
  }


  saveSubTemplateData(){
    const newSubTemplate = this.CustomTemplateForm.value.templateSubtype
    this.map.set(newSubTemplate,this.CustomTemplateForm.value.TemplateData)
    this.prevSubTemplate = newSubTemplate
    // this.CustomTemplateForm.value.TemplateData.setValue("")
    console.log("this.map===================",this.map)
    if(this.map.size >= 3){
      this.toggleButton = true
    }
  }
  saveTemplateData(option:any){
    // this.prevSubTemplate  =option
    const newSubTemplate = option
    this.map.set(this.prevSubTemplate,this.CustomTemplateForm.value.TemplateData)
    this.prevSubTemplate = newSubTemplate
    // this.CustomTemplateForm.value.TemplateData.setValue("")
    console.log("this.map===================",this.map)
    this.CustomTemplateForm.patchValue({
      TemplateData: ''
    });

  }

   // Retrieves the logged-in user from local storage
  getLogedInUser() {
    let role = localStorage.getItem('role');
    if(role== '"ROLE_ADMIN"'){
      this.isRoleAdmin = true
    }

    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.userId = x ;
      }
      console.log("userId", this.userId)
      return this.userId;
    }
  }

   // Loads template data from the server
  LoadTemplateData(){
    console.log("fd:",this.loadTemplate+this.userId)
    this.https.get(this.loadTemplate+this.userId).subscribe((res:any)=>{
      console.log("res=================",res) 
    }, error => {
      // You can access status:
      console.log(error.status);
      let message;
      if(error.status == 200){
        message = 'Templates Retrieved';
      }else{
      console.log(error)
       message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      }
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });


    })
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
      this.customTemplatePostUrl=ip_port.result.Admin + ip_port.result.TemplateCreation 
      this.customTemplatePatchUrl_updateCustomeTemplate=ip_port.result.Admin + ip_port.result.customTemplatePatchUrl_updateCustomeTemplate 
    this.customTemplateGetUrl=ip_port.result.Admin + ip_port.result.TemplateGet 
    this.customTemplateDeleteUrl=ip_port.result.Admin + ip_port.result.TemplateDelete 
    this.customTemplateUpdateUrl=ip_port.result.Admin + ip_port.result.TemplateUpdate 
    this.loadTemplate=ip_port.result.FM_Moderation + ip_port.result.loadTemplate 

    // this.Admin_uploadFile = ip_port.result.Admin_Rag + ip_port.result.Admin_uploadFile;
    // this.Admin_getFiles = ip_port.result.Admin_Rag + ip_port.result.Admin_getFiles;
    // this.Admin_setCache = ip_port.result.Admin_Rag + ip_port.result.Admin_setCache;
    // this.Admin_getEmbedings = ip_port.result.Admin_Rag + ip_port.result.Admin_getEmbedings;
    // this.Admin_LLmExplain_deleteFile = ip_port.result.Admin_Rag + ip_port.result.Admin_LLmExplain_deleteFile;
  }

  // Deletes a template by ID
  deleteConfirmationModel(templateId: any){
    // const params = new URLSearchParams();
    // params.set('userId', this.user);
    // params.set('dataid',dataId.toString())
    // const options = {
    //   headers: new HttpHeaders({
    //     'Content-Type': 'application/x-www-form-urlencoded',
    //   }),
    //   body: params,
    // };
    const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/x-www-form-urlencoded',
      }),
      body: `templateId=${templateId}`
    }
  
    // const payload = {
    //   "templateName": templateName
    // }

    this.https.delete(this.customTemplateDeleteUrl,options ).subscribe(
      (res: any) => {
        // this.getBatches();
        
        const message = 'Record Deleted Successfully';
        const action = 'Close';
        this.getTemplateDetail()
        this._snackBar.open(message, action, {
          duration: 5000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        if (error.status == 430) {
          const message = error.error.detail;
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          const message = 'The Api has failed';
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        }
      }
    );
  }

  // Opens the right-side modal for template data
  openRightSideModal(templateData:any,templateName:any,mode:any,template_type:any,userId:any){
    console.log("templateData===",templateData)
    const dialogRef = this.dialog.open(TemplateDataComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: {
        dataValue: templateData,
        templateName: templateName,
        userid: userId,
        mode:mode ,
        template_type:template_type,
        templateTest:false
          }
    });

    dialogRef.afterClosed().subscribe(() => {
      // this.getBatches()
      this.getTemplateDetail()
    });
    // TemplateDataComponent

  }
  formupdatedisbaled:boolean=false
  updatecall:boolean=false
  populateCustomtemFrom(templateData:any,templateName:any,mode:any,template_type:any,userId:any,description:any,category:any){
    this.formupdatedisbaled=true
    this.updatecall=true
    this.CustomTemplateForm.get('TemplateName')?.disable();
    this.CustomTemplateForm.get('mode')?.disable();
    console.log("templateData===",templateData)
    this.CustomTemplateForm.patchValue({
      mode:mode,
      category:category,
      TemplateName:templateName,
      TemplateDesc:description,
      promtInstruction:templateData[0].templateData,
      evalutionCriteria:templateData[1].templateData,
      fewShotExample:templateData[2].templateData
    })
    // this.getTemplateDetail()

  }

  
  openRightSidePromptTestModal(templateData:any,templateName:any,mode:any,template_type:any,userId:any){
    console.log("templateData===",templateData)
    const dialogRef = this.dialog.open(TemplateDataComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: {
        dataValue: templateData,
        templateName: templateName,
        userid: userId,
        mode:mode ,
        template_type:template_type,
        templateTest:true
          }
    });

    dialogRef.afterClosed().subscribe(() => {
      // this.getBatches()
      this.getTemplateDetail()
    });
    // TemplateDataComponent

  }
//  for search bar
toggleSearch() {
  this.isSearchOpen = !this.isSearchOpen;
  this.searchQuery = '';
  this.filteredItems = [];
}

// Filters templates based on the search query
search() {
  if (this.searchQuery) {
    console.log("serach query===",this.searchQuery)
    console.log("this.dataSource_getBatches571===",this.dataSource_getBatches_filter.templates)
    this.dataSource_getBatches = this.dataSource_getBatches_filter.templates.filter((temp: { templateName: string; }) =>
      temp.templateName.toLowerCase().includes(this.searchQuery.toLowerCase())
    );
    console.log(this.dataSource_getBatches, "Users Filtered")
  } else {
    this.dataSource_getBatches = this.dataSource_getBatches_filter.templates;
  }
  console.log(this.dataSource_getBatches_filter, "Users from backend")
}

 // Closes the search bar and resets the template list
closeSearch() {
  this.isSearchOpen = false;
  this.searchQuery = '';
  this.dataSource_getBatches = this.dataSource_getBatches_filter.templates;
}

 // Retrieves template details from the server
  getTemplateDetail(){
    // AllModel
    const params = new HttpParams()

      .set('category',"AllModel");
    let urlx = `${this.customTemplateGetUrl}${this.userId}`
    // let urlx = `${this.customTemplateGetUrl}${this.userId}`

    this.https.get(urlx, { params, headers: { 'accept': 'application/json' } })
      .subscribe
      // this.https.get(this.customTemplateGetUrl+this.userId).subscribe
      ((res: any) => {
       
        this.result = res
        this.dataSource_getBatches = res.templates;
        this.dataSource_getBatches_filter=res;
        console.log("this.datasource===",this.dataSource_getBatches)
        this.templateNameArray=[]
        for(let i=0;i<this.dataSource_getBatches.length;i++){
          this.templateNameArray.push(this.dataSource_getBatches[i].templateName)
        }
        console.log("this.templateNameArray===",this.templateNameArray)
        this.pagingConfig.totalItems = this.dataSource_getBatches.length;
        console.log("res===",this.pagingConfig)
        
  
        
  
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

  accountDropDown(){
    
    const accountArr: any = [];
   
    this.Account_options = this.modeArr
  
  }

  templatetype(){
    // const mode = this.CustomTemplateForm.controls['template_type'].value
    // console.log("inside accountDrop===",mode)
    const accountArr: any = [];
    // for(let i=0;i<this.accountDetail.length;i++){
    //   if(this.accountDetail[i].portfolio == portfolio){
    //     accountArr.push(this.accountDetail[i].account )
    //   }
    // }
    // this.Account_options = this.modeArr
  }

  templateTest(templateData:any,templateName:any,mode:any,template_type:any,userId:any){
    this.customTemplateTest=true
  }


  pormptTest(){

  }

  onTableDataChange(event: any) {
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.dataSource_getBatches.length;
  }

  onTableSizeChange(event: any): void {
    this.pagingConfig.itemsPerPage = event.target.value;
    this.pagingConfig.currentPage = 1;
    this.pagingConfig.totalItems = this.dataSource_getBatches.length;
  }

  submit(){
    console.log("selectedPrompt===",this.selectedPrompt)
  }

  // Resets the form and related data
  resetData(){
    
    this.showSpinner = false
    this.newTemplateName=""
    this.selectedOptions = [];
      this.tenantarr = [];
    this.CustomTemplateForm.patchValue({
      masterTemplate:[]
    })
    this.categoryValidation=false
    this.modeValidation=false
    this.templateNameValidation =false
    this.templateDescValidation = false
    this.tenantarr=[]
    console.log("masterTemplate====",this.CustomTemplateForm.value.masterTemplate)
    console.log("this.selectedoption===",this.selectedOptions) 
    console.log("this.tenantarr===",this.tenantarr) 
    this.templateSubmitFlag=false
    this.prompt_instToggle = true
  this.evaluation_criteriaToggle = false
  this.few_shot_exampleToggle=false
  this.updatecall=false
  this.formupdatedisbaled=false
  this.formCreation()
    // this.CustomTemplateForm.reset()
  }

  resetForm(){
    this.selectedPrompt = '';
    this.newTemplateName=""
  }

  // Initializes the component and loads data
  ngOnInit(): void {
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.prevSubTemplate = this.CustomTemplateForm.value.template_type
    this.setApilist(ip_port)
    this.getTemplateDetail()
    this.prompt_instToggle = true
    
    
  }
  triggerParentClick() {
    this.sharedService.triggerClick();
  }

}
