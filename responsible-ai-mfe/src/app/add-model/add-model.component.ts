/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from '../nonce.service';

@Component({
  selector: 'app-add-model',
  templateUrl: './add-model.component.html',
  styleUrls: ['./add-model.component.css']
})
export class AddModelComponent {
  user:any;
  addModels:any;
  updateModels:any;
  isCreateModel = false;
  isUpdateModel = false;
  spinner =false;
  spinner1 = false;
  SecurityFormModel!: FormGroup;
  modelEndPointInputValue = 'NA';
  apiRequestDataValue='NA';
  apipredictionDataValue='NA';
  demoFile: any[] = [];
  public browseFilesLenth = 0;
  files: any[] = [];
  checkedValue = '';
  textDesc: any;
  SecurityFormModelUpdate!: FormGroup;
  selectedModelFile:File | any;
  target_Data_Type = [
    { value: 'Tabular', viewValue: 'Tabular' },
    { value: 'Image', viewValue: 'Image' },
    { value: 'Text', viewValue: 'Text' },
  ];
  classifier_list = [
    { value: 'SklearnClassifier', viewValue: 'SklearnClassifier'},
    { value: 'ScikitlearnClassifier', viewValue: 'ScikitlearnClassifier'},
    { value: 'KerasClassifier', viewValue: 'KerasClassifier'},
    { value: 'PyTorchFasterRCNN', viewValue: 'PyTorchFasterRCNN'},
    { value: 'SklearnAPIClassifier', viewValue: 'SklearnAPIClassifier'}
  ];
  taskType_list =  [
    {
      "viewValue": "Classification",
      "value": "CLASSIFICATION"
    },
    {
      "viewValue": "Regression",
      "value": "REGRESSION"
    },
    {
      "viewValue": "Timeseries Forecast",
      "value": "TIMESERIESFORECAST"
    }
  ];
  @ViewChild("fileDropRef", { static: false }) fileDropEl: any = ElementRef;
  constructor(
    public dialogRef: MatDialogRef<AddModelComponent>,
    public https: HttpClient,
    private _snackBar: MatSnackBar,
    private fb: UntypedFormBuilder,
    @Inject(MAT_DIALOG_DATA) public data: any,public nonceService:NonceService
  ) {
    this.SecurityFormModel = this.fb.group({
      modelName: new FormControl('', [Validators.required]),
      targetDataType: new FormControl('', [Validators.required]),
      targetClassifier: new FormControl('', [Validators.required]),
      modelEndPointAvailable: new FormControl('', [Validators.required]),
      modelEndPoint: new FormControl('', [Validators.required]),
      requestData: new FormControl('', [Validators.required]),
      predictionData: new FormControl('', [Validators.required]),
      sampleDataID: new FormControl('', [Validators.required]),
      fileDropRef: new FormControl('', [Validators.required]),
      taskType:  new FormControl('', [Validators.required]),
    })
    this.SecurityFormModelUpdate = this.fb.group({
      userId: new FormControl(this.data.user, [Validators.required]),
      modelId: new FormControl(this.data.modelValue, [Validators.required]),
      targetDataType: new FormControl('', [Validators.required]),
      targetClassifier: new FormControl('', [Validators.required]),
      modelEndPointAvailable: new FormControl('', [Validators.required]),
      modelEndPoint: new FormControl('', [Validators.required]),
      requestData: new FormControl('', [Validators.required]),
      predictionData: new FormControl('', [Validators.required]),
      sampleDataID: new FormControl('', [Validators.required]),
      fileDropRef: new FormControl('', [Validators.required]),
      taskType:  new FormControl('', [Validators.required]),
    })
  }

  // Initializes the component and sets up the API list
  ngOnInit(): void {
    if(this.data.modelValue == 0){
      this.isCreateModel = true;
    }else{
     this.isUpdateModel = true;
    } 
  let ip_port: any;
  // user call should happen here 
  this.user = this.data.user;
  // getting list of api from  local storage 
  ip_port = this.getLocalStoreApi()
  // seting up api list 
  this.setApilist(ip_port);
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
// used to set the api list urls 
setApilist(ip_port: any) {
  this.addModels =ip_port.result.Workbench + ip_port.result.Workbench_AddModel
    this.updateModels =ip_port.result.Workbench + ip_port.result.Workbench_UpdateModel
}

// This method will handles file selection, validates the file type, and initiates the file upload process.
fileBrowseHandler(imgFile: any): void {
  console.log("Called");
  // Reset files list before adding new files
  this.files = [];
  this.demoFile = this.files;
  this.browseFilesLenth = imgFile.target.files.length;
  this.prepareFilesList(imgFile.target.files);
  this.spinner1 = true;
  const allowedTypes = ['application/octet-stream', 'application/x-python-code']; // Allowed MIME types
  const allowedExtensions = ['.pkl'];
    // Check the file extension (for .pkl)
    const fileExtension = this.demoFile[0].name.split('.').pop()?.toLowerCase();

    if (this.files.length > 0) {
      for (let i = 0; i < this.files.length; i++) {
        const currentFile = this.files[i];
        // Check the MIME type
        if (!allowedTypes.includes(currentFile.type) && !allowedExtensions.includes(`.${fileExtension}`)) {
          alert('Please upload a valid .pkl file');
            this.files = [];
            this.demoFile = [];
            return;
        }
    }
      // If files are valid, upload the first file (or process as needed)
  if (this.files.length > 0) {
    this.uploadDocument(this.demoFile[0]);
}
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
  this.uploadFilesSimulator(0)
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

// Closes the dialog
closeDialog(){
  this.dialogRef.close();
}

// This method will creates a new model by submitting the form data to the server.
createNew(){
  this.spinner = true;
    const mName = this.SecurityFormModel.value.modelName;
    const tdType = this.SecurityFormModel.value.targetDataType;
    const mEndPointA = this.SecurityFormModel.value.modelEndPointAvailable;
    const mEndPoint = this.modelEndPointInputValue;
    const requestD = this.apiRequestDataValue;
    const predictionD = this.apipredictionDataValue;
    const typeOfTask = this.SecurityFormModel.value.taskType ;
    const classifier = this.SecurityFormModel.value.targetClassifier;
    const payload = {
      "modelName": mName,
  "targetDataType": tdType,
  "taskType": typeOfTask,
  "targetClassifier": classifier,
  "useModelApi": mEndPointA,
  "modelEndPoint": mEndPoint,
  "data": requestD,
  "prediction": predictionD,
  "imageClassificationTypes":"binary classification"
}
const fileData = new FormData();
fileData.append('userId', this.user);
fileData.append('Payload', JSON.stringify(payload));
if(this.demoFile.length==1){
  for (let i = 0; i < this.demoFile.length; i++) {
    this.selectedModelFile = this.demoFile[i];
    fileData.append('ModelFile', this.selectedModelFile);
  }
  }

this.https.post(this.addModels,fileData).subscribe((res: any)=>{
  this.spinner = false;
    this.resetForm();
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

// This method will updates an existing model by submitting the updated form data to the server.
updateModel(){
  this.spinner = true;
  const tdType = this.SecurityFormModelUpdate.value.targetDataType;
  const mEndPointA = this.SecurityFormModelUpdate.value.modelEndPointAvailable;
  const mEndPoint = this.modelEndPointInputValue;
  const requestD = this.apiRequestDataValue;
  const predictionD = this.apipredictionDataValue;
  const typeOfTask = this.SecurityFormModelUpdate.value.taskType ;
  const classifier = this.SecurityFormModelUpdate.value.targetClassifier;
  const payload = {
"targetDataType": tdType,
"taskType": typeOfTask,
"targetClassifier": classifier,
"useModelApi": mEndPointA,
"modelEndPoint": mEndPoint,
"data": requestD,
"prediction": predictionD
}
const fileData = new FormData();
fileData.append('userId', this.user);
fileData.append('modelId', this.data.modelValue);
fileData.append('Payload', JSON.stringify(payload));
if(this.demoFile.length==1){
for (let i = 0; i < this.demoFile.length; i++) {
  this.selectedModelFile = this.demoFile[i];
  fileData.append('ModelFile', this.selectedModelFile);
}
}
this.https.patch(this.updateModels,fileData).subscribe((res:any)=>{
  this.spinner = false;
    this.resetForm();
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

// Resets the form and clears file uploads
resetForm(){
  this.SecurityFormModel.reset();
  this.SecurityFormModelUpdate.reset();  
  this.spinner1= false;
  if (this.files.length==1) {
    this.files.splice(0, 1);
    this.demoFile.splice(0, 1);
  }
}

// Handles changes in the model endpoint availability
changeModelEndPointAvailable(event: any) {
  //this.selectedRadioBoxVariable.emit(this.selectedRadioBox);
  // this.checkedValue = event.target.value;
  this.checkedValue = event.value;
}
}
