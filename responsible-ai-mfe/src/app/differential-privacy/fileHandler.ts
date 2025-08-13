/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { MatSnackBar } from '@angular/material/snack-bar';
export class FileHandler {
    files: any[] = [];
    demoFile: any[] = [];
    file: File | any;
    fileUploadvalid=false
    validationMessage: string = '';

    constructor(public _snackBar: MatSnackBar ){}

    fileBrowseHandler(imgFile: any) {
        this.prepareFilesList(imgFile.target.files);
        this.demoFile = this.files;
        this.file = this.files[0];

        // Validate file type
        const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        if (!allowedTypes.includes(this.file.type)) {
           this._snackBar.open('Please select a valid file type', '✖', {
              horizontalPosition: 'center',
              verticalPosition: 'top',
              duration: 3000,
           }); 
            //  this.validationMessage = 'Only CSV files are allowed';  
            this.fileUploadvalid=false
            this.reset();
            return;
        }else{
            this.fileUploadvalid=true
            this.validationMessage = '';
        }

        // If the file is valid, clear the validation message and handle the file
        // this.validationMessage = '';
        // this.fileBrowseHandler(this.file);
    }

    // Prepare the file list for upload
    prepareFilesList(files: Array<any>) {
        this.files = []
        for (const item of files) {
            this.files.push(item);
        }
        this.uploadFilesSimulator(0, files)
    }

    removeFile() {
        this.demoFile = []
        this.files = []
    }
    // Simulate file upload progress
    uploadFilesSimulator(index: number, files: any) {
        setTimeout(() => {
            if (index === this.files.length) {
                return;
            } else {
                this.files[index].progress = 0;
                const progressInterval = setInterval(() => {
                    if (this.files[index].progress >= 100) {
                        clearInterval(progressInterval);
                    } else {
                        this.files[index].progress += 10;
                    }
                }, 200);
            }
        }, 1000);
    }

    // Validate if a file exists
    fileExitsValidator() {
        if(this.demoFile.length ==0){
            this.validationMessage = 'Please select a file';
            this.fileUploadvalid=false
            return false
        }else{
            this.validationMessage = '';
            this.fileUploadvalid=true
            return true
        }

    }

    reset() {
        // Reset properties
        this.files = [];
        this.demoFile = [];
        this.file = null;
        this.fileUploadvalid=false
        this.validationMessage = '';
    }
}
