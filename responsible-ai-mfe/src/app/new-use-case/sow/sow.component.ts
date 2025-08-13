/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-sow',
  templateUrl: './sow.component.html',
  styleUrls: ['./sow.component.css']
})
export class SowComponent {
  selectedOption: any;
  @ViewChild('sowFileInput') sowFileInput!: ElementRef;
  selectedSowFileName: any = '';
  sowFileProgress: number = 0;
  isSubmitting: boolean = false; // Add this property
  Placeholder:string = 'Enter Prompt';
  prompt: string ='';

  constructor(private https: HttpClient, private _snackBar: MatSnackBar) {}

  // Method to handle the dropdown change event
  onDropdownChange(event: any) {
    this.selectedOption = event.target.value;
    console.log('Selected option:', this.selectedOption);
    this.resetFileInputs();
  }

  // Resets file input fields
  resetFileInputs() {
    this.selectedSowFileName = '';
    // this.selectedRecFileName = '';
    if (this.sowFileInput && this.sowFileInput.nativeElement) {
      this.sowFileInput.nativeElement.value = '';
    }
    // if (this.recFileInput && this.recFileInput.nativeElement) {
    //   this.recFileInput.nativeElement.value = '';
    // }
    this.sowFileProgress = 0;
    // this.recFileProgress = 0;
  }

  // Opens the file input dialog for SOW file
  openSowFileInput() {
    this.sowFileInput.nativeElement.click();
  }

   // Handles file selection for SOW file
  sowFileBrowseHandler(event: any) {
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    console.log("fileBrowseHandler", event.target.files[0].type)
    if (!allowedTypes.includes(event.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      }); 
      // return;
    }else{
    const file = event.target.files[0];
    if (file) {
      this.selectedSowFileName = file.name;
      this.sowFileProgress = 0; // Reset progress
      // Simulate file upload progress
      const interval = setInterval(() => {
        this.sowFileProgress += 10;
        if (this.sowFileProgress >= 100) {
          clearInterval(interval);
        }
      }, 100);
    }
  }
  }

  // Removes the selected SOW file
  removeSowFile() {
    this.selectedSowFileName = '';
    this.sowFileInput.nativeElement.value = '';
    this.sowFileProgress = 0;
  } 

   // Handles form submission
  onSubmit() {
    this.isSubmitting = true;
    const sowFile = this.sowFileInput.nativeElement.files[0];
  
    if (!sowFile || (this.selectedOption === 'verification' && !this.prompt)) {
      console.error('Please select the required files.');
      this.isSubmitting = false;
      return;
    }
  
    const formData = new FormData();
    formData.append('SOW_File', sowFile, sowFile.name);
    formData.append('rec_text', this.prompt);
  
    if (this.selectedOption === 'verification') {
      this.submitForm(this.SOWagent, formData);
    } else if (this.selectedOption === 'recommendation') {
      this.submitForm(this.SOWagent_sow_recommendation, formData);
    }
  }
  
  // Submits the form data to the specified API
  submitForm(url: string, formData: FormData) {
    this.https.post(url, formData, {
      headers: {
        'accept': 'application/json'
      }
    }).subscribe((response: any) => {
      console.log('Upload successful', response);
      this.isSubmitting = false;
  
      if (response && response.filelink) {
        // Validate URL to ensure it's safe
     const isValidUrl = this.validateUrl(response.filelink);
     if (!isValidUrl) {
         console.error('Invalid or potentially unsafe URL:', response.filelink);
         return;
     }
        const a = document.createElement('a');
        a.href = response.filelink;
        a.target = '_blank'; // Open in a new tab
        a.click();
        //window.location.href = response.filelink;
  
        this._snackBar.open('File downloaded successfully', 'Close', {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }
    }, error => {
      console.error('Upload failed', error);
      this.isSubmitting = false;
    });
  }

  ip_port:any 
  SOWagent:any
  SOWagent_sow_recommendation:any
  user:any

// Initializes the component and sets up API calls
  ngOnInit(): void {
    let ip_port: any;
    this.user = localStorage.getItem('userid')?JSON.parse(localStorage.getItem('userid')!) : '';
    ip_port = this.getLocalStoreApi();
    // seting up api list
    this.setApiList(ip_port);
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
   // Sets the API endpoints
  setApiList(ip_port: any) {
    this.SOWagent = ip_port.result.legalAgent + ip_port.result.SOWagent ;
    this.SOWagent_sow_recommendation = ip_port.result.legalAgent + ip_port.result.SOWagent_sow_recommendation ;
  }

  // Refreshes the form inputs
  refresh(){
    this.selectedOption = '';
    this.selectedSowFileName = '';
    this.prompt = '';
    this.sowFileInput.nativeElement.value = '';
  }
//  function to validate URL
validateUrl(url: any) {
  console.log("url:::",url)
  const pattern = /^https:\/\/rai-toolkit-(dev|rai)\.az\.ad\.idemo-ppc\.com.*/;
  return pattern.test(url);
}
  

}