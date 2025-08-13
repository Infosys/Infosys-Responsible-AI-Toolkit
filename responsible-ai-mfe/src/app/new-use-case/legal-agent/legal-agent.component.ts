/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpParams} from '@angular/common/http';
import { Component,OnInit ,Input} from '@angular/core';
import { AbstractControl, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';

@Component({
  selector: 'app-legal-agent',
  templateUrl: './legal-agent.component.html',
  styleUrls: ['./legal-agent.component.css']
})
export class LegalAgentComponent implements OnInit {
  @Input() useCaseNameDetail: any;
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
  legalUpload: any;
  // pagination
  pagingConfig: PagingConfig = {} as PagingConfig;
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  switch: boolean= false;
  selectedUseCase: string = '';
  legalReport: any;

  constructor (public _snackBar: MatSnackBar, private https: HttpClient, private snackBar: MatSnackBar,public nonceService:NonceService,private validationService:UserValidationService)
  {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
    this.useCase = new FormGroup({
      //useCaseName: new FormControl('', [Validators.required]),
      fileData: new FormControl('', [Validators.required]),
      option: new FormControl('', [Validators.required]),
    });
  }

  // Initializes the component and sets up API calls
  ngOnInit(): void {
    let ip_port: any;
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.user = x ;
      }    }    ip_port = this.getLocalStoreApi();
    // seting up api list
    this.setApiList(ip_port);
    this.getAllData();
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
    this.getData = ip_port.result.legalAgent + ip_port.result.legalAgentReports ;//"http://10.152.196.184:30080/v1/legalAgent/getAllReports";
    this.legalUpload = ip_port.result.legalAgent + ip_port.result.legalAgentUpload ;//"http://10.152.196.184:30080/v1/legalAgent/uploadFile";
    this.legalReport = ip_port.result.legalAgent + ip_port.result.legalReport;
    console.log("this.getData::",this.legalReport)
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

   // Handles file browsing and prepares the file list
  fileBrowseHandler(file: any){
    this.prepareFilesList(file.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
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

// Submits the form and triggers the API call
  submit(){
    this.showSpinner1 = true;
    if (this.switch==false){
      const { fileData, option } = this.useCase.value;
    if (!fileData) {
      this.showSpinner1 = false;
      this.snackBar.open('Please select a File', '✖', {
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
    this.https.post(this.legalUpload ,fileData1).subscribe((res: any)=>{
      this.showSpinner1 = false;
      this.getAllData();
      const message = res?.message;
      const action = "Close";
      this.snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
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
        this.showSpinner1 = false;
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

      this.https.get(this.legalReport, { params }).subscribe(
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
    //this.getData = this.getData + '?user_id='+ this.user;
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

  // Opens a file link in a new tab
  getfileContent(documentLink: string){
    console.log('Navigating to:', documentLink);
    const a = document.createElement('a');
    a.href = documentLink;
    a.target = '_blank'; // Open in a new tab
    a.click();
    //window.location.href = documentLink; 
  }
  
  // Toggles the switch state
  onToggleSwitch(event: Event): void {
    this.switch = (event.target as HTMLInputElement).checked;
  }
}
