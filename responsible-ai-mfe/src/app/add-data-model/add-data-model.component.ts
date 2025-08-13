/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, Input, ViewChild } from '@angular/core';
import { FormControl, FormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from '../nonce.service';


@Component({
  selector: 'app-add-data-model',
  templateUrl: './add-data-model.component.html',
  styleUrls: ['./add-data-model.component.css']
})
export class AddDataModelComponent {
  SecurityForm!: FormGroup;
  numberArray2: any[] = [];
  target_Data_Type = [
    { value: 'Tabular', viewValue: 'Tabular' },
    { value: 'Image', viewValue: 'Image' },
    { value: 'Text', viewValue: 'Text' },
  ];
  spinner = false;
  spinner1 = false;
  demoFile: any[] = [];
  public browseFilesLenth = 0;
  files: any[] = [];
  textDesc: any;
  user:any; 
  addData:any;
  updateData:any;
  selectedDataFile: File | any;
  isCreateData= false;
  isUpdateData = false;
  SecurityUpdateForm!: FormGroup;
  
  classifier_list = [
    { value: 'SklearnClassifier', viewValue: 'SklearnClassifier'},
    { value: 'ScikitlearnClassifier', viewValue: 'ScikitlearnClassifier'},
    { value: 'KerasClassifier', viewValue: 'KerasClassifier'},
    { value: 'PyTorchFasterRCNN', viewValue: 'PyTorchFasterRCNN'},
    { value: 'SklearnAPIClassifier', viewValue: 'SklearnAPIClassifier'}
  ];
  @ViewChild("fileDropRef", { static: false }) fileDropEl: any = ElementRef;
  
  constructor(
    public dialogRef: MatDialogRef<AddDataModelComponent>,
    public https: HttpClient,
    private _snackBar: MatSnackBar,
    private fb: UntypedFormBuilder,
    @Inject(MAT_DIALOG_DATA) public data: any,public nonceService:NonceService
  ) {
    this.SecurityForm = this.fb.group({
      dataFileName: new FormControl('', [Validators.required]),
      targetDataType: new FormControl('', [Validators.required]),
      targetColumnName: new FormControl('', [Validators.required]),
      targetOutputClass: new FormControl('', [Validators.required]),
      dataFileDropRef: new FormControl('', [Validators.required]),
    })
    this.SecurityUpdateForm = this.fb.group({
      userId: new FormControl(this.data.user, [Validators.required]),
      datafileid: new FormControl(this.data.dataValue, [Validators.required]),
      targetDataType:new FormControl('', [Validators.required]),
      targetColumnName: new FormControl('', [Validators.required]),
      targetOutputClass: new FormControl('', [Validators.required]),
      dataFileDropRef: new FormControl('', [Validators.required]),
    })
  }
  
  ngOnInit(): void {
      if(this.data.dataValue == 0){
        this.isCreateData = true;
      }else{
       this.isUpdateData = true;
      } 
    let ip_port: any;
    // user call should happen here 
    this.user = this.data.user;
    // getting list of api from  local storage 
    ip_port = this.getLocalStoreApi()
    // seting up api list 
    this.setApilist(ip_port);
  }
  getLocalStoreApi() {
    let ip_port
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        return ip_port = JSON.parse(x)
      }
    }
  }
  // used to set the api list urls 
  setApilist(ip_port: any) {
    this.addData = ip_port.result.Workbench + ip_port.result.Workbench_AddData;
    this.updateData = ip_port.result.Workbench + ip_port.result.Workbench_UpdateData;
  }

  closeDialog(){
    this.dialogRef.close();
  }

    //  This method converts the targetOutputClass field value from the SecurityForm to an array of numbers or strings.
  convertToArrayForTargetOutputClass() {
    // this.numberArray2 = this.SecurityForm.value['targetOutputClass'].split(',').map(Number);
    const a= this.SecurityForm.value['targetOutputClass']
    if (/^\d+(,\d+)*$/.test(a)) {
      this.numberArray2 = a.split(',').map(Number);
    }
    else{
      this.numberArray2 = a.split(',');
    }
  }

  // This method will converts the targetOutputClass field value from the SecurityUpdateForm to an array of numbers or strings.
  convertToArrayForTargetOutputClass2() {
    // this.numberArray2 = this.SecurityForm.value['targetOutputClass'].split(',').map(Number);
    const a= this.SecurityUpdateForm.value['targetOutputClass']
    if (/^\d+(,\d+)*$/.test(a)) {
      this.numberArray2 = a.split(',').map(Number);
    }
    else{
      this.numberArray2 = a.split(',');
    }
  }

    // This method will handles file selection, validates the file type, and initiates the file upload process.
  fileBrowseHandler(imgFile: any) {
    const allowedTypes = ['text/csv'];
    console.log("fileBrowseHandler", imgFile.target.files[0].type)
    if (!allowedTypes.includes(imgFile.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      }); 
      // return;
    }else{
    console.log("Called")
    this.files = []
    this.demoFile = this.files;
    this.browseFilesLenth = imgFile.target.files.length;
    this.prepareFilesList(imgFile.target.files);
    this.spinner1 = true
    this.uploadDocument(this.demoFile[0])
  }
}

  // Reads and uploads the selected document
  uploadDocument(file:any) {
    let fileReader = new FileReader();
    fileReader.onload = (e) => {
      // console.log(fileReader.result);
      this.textDesc = fileReader.result
      this.spinner1 = false
    }
    fileReader.readAsText(file);
  }

  // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    for (const item of files) {
      this.files.push(item);
    }
    this.uploadFilesSimulator(0);
  }

  // Simulates file upload progress
  uploadFilesSimulator(index: number) {
    setTimeout(() => {
      if (index === this.files.length) {
        return;
      } else {
        this.files[index].progress = 0;
        const progressInterval = setInterval(() => {
          if (this.files[index].progress === 100) {
            clearInterval(progressInterval);
            this.uploadFilesSimulator(index + 1);
          } else {
            this.files[index].progress += 20;
          }
        }, 200);
      }
    }, 1000);
  }

  // Deletes a file from the list
  deleteFile(index: number) {
    if (this.files[index].progress < 100) {
      console.log("if of deltefile 1.");
      return;
    }
    this.files.splice(index, 1);
  }

// This method will creates a new data model by submitting the form data to the server.
  createNew(){
    if (this.SecurityForm.invalid) {
      this._snackBar.open('Please fill all fields before submitting', '✖', {
        horizontalPosition: 'center', 
        verticalPosition: 'top', 
      });
      return;
    }
    this.spinner = true;
    const dataname = this.SecurityForm.value.dataFileName;
    const tdType = this.SecurityForm.value.targetDataType;
    const tClasses = this.numberArray2;
    const tClassifier = this.SecurityForm.value.targetColumnName;

    const payload = {
      "dataFileName": dataname,
      "dataType": tdType,
      "groundTruthClassNames": tClasses,
      "groundTruthClassLabel": tClassifier
    }
    const fileData = new FormData();
    fileData.append('userId', this.user);
    fileData.append('Payload', JSON.stringify(payload));
    for (let i = 0; i < this.demoFile.length; i++) {
      this.selectedDataFile = this.demoFile[i];
      fileData.append('DataFile', this.selectedDataFile);
    }
    this.https.post(this.addData,fileData).subscribe((res: any)=>{
      this.resetForm();
      this.spinner = false;
      this._snackBar.open(res, "Close", {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      this.closeDialog();
      }, error => {      
        console.log(error)
        this.spinner = false;
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
        this.closeDialog();
      })
  }

  // This method will updates an existing data model by submitting the updated form data to the server.
  updateDataFile(){
    if (this.SecurityUpdateForm.invalid) {
      this._snackBar.open('Please fill all fields before submitting', '✖', {
        horizontalPosition: 'center', 
        verticalPosition: 'top', 
      });
      return;
    }
    this.spinner = true;
    const tdType = this.SecurityUpdateForm.value.targetDataType;
    const tClasses = this.numberArray2;
    const tClassifier = this.SecurityUpdateForm.value.targetColumnName;

    const payload = {
      "dataType": tdType,
      "groundTruthClassNames": tClasses,
      "groundTruthClassLabel": tClassifier
    }
    console.log("pay:;",payload)
    const fileData = new FormData();
    fileData.append('userId', this.user);
    fileData.append('dataid', this.data.dataValue);
    fileData.append('Payload', JSON.stringify(payload));
    for (let i = 0; i < this.demoFile.length; i++) {
      this.selectedDataFile = this.demoFile[i];
      fileData.append('DataFile', this.selectedDataFile);
    }
    this.https.patch(this.updateData,fileData).subscribe((res:any)=>{
      this.spinner = false;
      this.resetForm();
      this._snackBar.open("Data Updated", "Close", {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      this.closeDialog();
    }, error => {      
      console.log(error)
      this.spinner = false;
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      this.closeDialog();
    })
  }

   // Resets the form and clears file uploads
  resetForm() {
    this.SecurityForm.reset();
    this.spinner1= false;
    if (this.files.length==1) {
      this.files.splice(0, 1);
      this.demoFile.splice(0, 1);
    }
  }

}
