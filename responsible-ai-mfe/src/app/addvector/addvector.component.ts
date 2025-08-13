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
  selector: 'app-addvector',
  templateUrl: './addvector.component.html',
  styleUrls: ['./addvector.component.css']
})
export class AddvectorComponent {
  VectorForm!: FormGroup;
  VectorUpdateForm!: FormGroup;
  spinner = false;
  demoFile: any[] = [];
  public browseFilesLenth = 0;
  files: any[] = [];
  isCreateVector= false;
  isUpdateVector = false;
  user:any; 
  addVector:any;
  updateVector: any;
  textDesc: any;
  file: File | any;
  selectedVectorFile: File | any;
  @ViewChild("fileDropRef", { static: false }) fileDropEl: any = ElementRef;

  constructor(
    public dialogRef: MatDialogRef<AddvectorComponent>,
    public https: HttpClient,
    private _snackBar: MatSnackBar,
    private fb: UntypedFormBuilder,
    @Inject(MAT_DIALOG_DATA) public data: any,public nonceService:NonceService
  ){
    this.VectorForm = this.fb.group({
      vectorFileName : new FormControl('', [Validators.required]),
      dataFileDropRef: new FormControl('', [Validators.required]),
    })
    this.VectorUpdateForm =this.fb.group({
      userId: new FormControl(this.data.user, [Validators.required]),
      vectorFileId: new FormControl(this.data.vectorValue, [Validators.required]),
      vectorFileName : new FormControl(this.data.vectorName, [Validators.required]),
      dataFileDropRef: new FormControl('', [Validators.required]),
    })
  }

    // Initializes the component and sets up the API list
  ngOnInit(): void {
    if(this.data.vectorValue == 0){
      this.isCreateVector = true;
    }else{
     this.isUpdateVector = true;
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
  this.addVector = ip_port.result.Workbench + ip_port.result.Workbench_AddVector;
  this.updateVector = ip_port.result.Workbench + ip_port.result.Workbench_UpdateVector;
}
  
  // Closes the dialog
  closeDialog(){
    this.dialogRef.close();
  }

    // Handles file selection and validates the file type
  fileBrowseHandler(imgFile: any): void {
    // Prepare the files list
    this.prepareFilesList(imgFile.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
    console.log("File type:", this.file.type);
    // Validate file extension and type
    const allowedTypes = ['application/octet-stream', 'application/x-python-code']; // Add more if needed
    const allowedExtensions = ['.pkl'];
    // Check the file extension (for .pkl)
    const fileExtension = this.file.name.split('.').pop()?.toLowerCase();
    if (this.files.length > 0) {
      for (let i = 0; i < this.files.length; i++) {
        const currentFile = this.files[i];
        // Check MIME type and file extension
        if (!allowedTypes.includes(currentFile.type) && !allowedExtensions.includes(`.${fileExtension}`)) {
          alert('Please upload a valid .pkl file');
          this.files = [];
          this.demoFile = [];
          this.file = '';
          return;
        }
      }
      // If file is valid, patch the form
      this.VectorForm.patchValue({
        fileDropRef: this.files[0]
      });
    }
  }

    // Reads and uploads the selected document
  uploadDocument(file:any) {
    let fileReader = new FileReader();
    fileReader.onload = (e) => {
      this.textDesc = fileReader.result
    }
    fileReader.readAsText(file);
  }

    // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    this.files=[]
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
  // uploadFilesSimulator(index: number,files:any) {
  //   setTimeout(() => {
  //     // console.log(this.files[0].name)
  //     // console.log(files)
  //     // console.log(files[0].name)
  //     // console.log("START TIMEOUT")
  //     if (index === this.files.length) {
  //       console.log("RETURN")
  //       return;
  //     } else {
  //       this.files[index].progress = 0;
  //       const progressInterval = setInterval(() => {
  //         if (this.files[index].progress >= 100) {
  //           clearInterval(progressInterval);
  //         } else {
  //           // console.log("ELSE BLOCK")
  //           // console.log(this.files[index])
  //           // console.log(this.files[index].progress)
  //           this.files[index].progress += 10;
  //         }
  //       }, 200);
  //     }
  //   }, 1000);
  // }

    // Creates a new vector by submitting the form data to the server
  createNew(){
    if (this.VectorForm.invalid) {
      this._snackBar.open('Please fill all fields before submitting', '✖', {
        horizontalPosition: 'center', 
        verticalPosition: 'top', 
      });
      return;
    }
    this.spinner = true;
    const vectorFileName = this.VectorForm.value.vectorFileName;
    const fileData = new FormData();
    fileData.append('preprocessorName',vectorFileName);
    fileData.append('userId', this.user);
    for (let i = 0; i < this.demoFile.length; i++) {
      this.selectedVectorFile = this.demoFile[i];
      fileData.append('PreprocessorFile', this.selectedVectorFile);
    }
    this.https.post(this.addVector,fileData).subscribe((res: any)=>{
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

    // Updates an existing vector by submitting the updated form data to the server
  updateVectorFile(){
    if (this.VectorUpdateForm.invalid) {
      this._snackBar.open('Please fill all fields before submitting', '✖', {
        horizontalPosition: 'center', 
        verticalPosition: 'top', 
      });
      return;
    }
    this.spinner = true;
    const fileData = new FormData();
    fileData.append('userId', this.user);
    fileData.append('preprocessorId', this.data.vectorValue);
    fileData.append('preprocessorName', this.VectorUpdateForm.value.vectorFileName);
    for (let i = 0; i < this.demoFile.length; i++) {
      this.selectedVectorFile = this.demoFile[i];
      fileData.append('PreprocessorFile', this.selectedVectorFile);
    }
    this.https.patch(this.updateVector,fileData).subscribe((res:any)=>{
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
  resetForm(){
    this.VectorForm.reset();
  }

}
