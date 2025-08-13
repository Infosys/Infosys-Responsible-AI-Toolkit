/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ElementRef, ViewChild } from '@angular/core';
import { DICOMViewerComponent } from '../dicom-lib/dicom-viewer.component';
import * as cornerstoneWADOImageLoader from "cornerstone-wado-image-loader";
import * as cornerstone from "cornerstone-core";
import * as dicomParser from 'dicom-parser';
import { environment } from 'src/environments/environment';
import { ImageDicomService } from './image-dicom.service';
import { Subscription } from 'rxjs';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { FormControl, AbstractControl, ValidationErrors, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-image-dicom',
  templateUrl: './image-dicom.component.html',
  styleUrls: ['./image-dicom.component.css']
})
export class ImageDicomComponent {
  isLoadingUpload = true;
  isLoadingOutput = false; // Add this line
  isLoadingFile = false; // Add this line
  selectedImage: string = '';
  form: FormControl;
  @ViewChild(DICOMViewerComponent, { static: true }) viewPort: any = DICOMViewerComponent;

  dicom1 = environment.dicomPathUrl + '/assets/dicom/0_ORIGINAL.dcm';
  dicom2 = environment.dicomPathUrl + '/assets/dicom/1_ORIGINAL.dcm';
  dicom3 = environment.dicomPathUrl + '/assets/dicom/3_ORIGINAL.dcm';

  dicomThumb1 = environment.imagePathurl + '/assets/image/dicomThumb1.png';
  dicomThumb2 = environment.imagePathurl + '/assets/image/dicomThumb2.png';
  dicomThumb3 = environment.imagePathurl + '/assets/image/dicomThumb3.png';

  dicomFile: any[] = [];
  selectedDicomFile: File | any;
  arr: any[] = [];
  preview = false;

  files: any[] = [];
  demoFile: any[] = [];
  selectedFile: File | any;
  file: File | any;

  fileName: string = "TEST";
  progress: number = 0;
  uploadSubscription!: Subscription;

  dicomUrl = environment.dicomUrl;
  public ip_port: any;
  res1: any;
  res2: any;
  table: boolean = false;
  dicom: boolean = false;
  spinner = false;

  // Declare the loadedImagesMap property
  loadedImagesMap: Map<string, File> = new Map();

  constructor(private _snackBar: MatSnackBar, private dicomService: ImageDicomService, public dialog: MatDialog, public snackBar: MatSnackBar, private sanitizer: DomSanitizer) {
    this.form = new FormControl(null, this.fileSelectedValidator.bind(this));
  }

    // Validates if a file is selected
  fileSelectedValidator(control: AbstractControl): ValidationErrors | null {
    if ((control.value == null || control.value.length === 0) && !this.selectedImage) {
      return { 'noFileSelected': true };
    }
    return null;
  }

  // Initializes the component and loads DICOM files
  ngOnInit(): void {
    console.log(this.dicomThumb1);
  
    // Fetch files in parallel
    const fetchFile = (url: string) => {
      return fetch(url)
        .then(response => response.blob())
        .then(blob => {
          const fileName = url.replace(/^.*[\\\/]/, '').replace(/\[object Object\]/g, '');
          return new File([blob], fileName, { type: 'dicom/dcm' });
        });
    };
  
    const promises = [this.dicom1, this.dicom2, this.dicom3].map(fetchFile);
  
    Promise.all(promises)
      .then(files => {
        this.dicomFile = files;
        this.arr = [files];
        this.loadedImagesMap = new Map(files.map(file => [file.name, file])); // Store loaded images in a map
        console.log("Files loaded:", files);
        this.isLoadingUpload = false;
      })
      .catch(error => {
        console.error('Error fetching files:');
        this.isLoadingUpload = false;
      });
  
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone; // Initialize WADO Image loader
    cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
    // Configure codecs and web workers
    cornerstoneWADOImageLoader.webWorkerManager.initialize({
      webWorkerPath: './assets/cornerstone/webworkers/cornerstoneWADOImageLoaderWebWorker.js',
      taskConfiguration: {
        'decodeTask': {
          codecsPath: '../codecs/cornerstoneWADOImageLoaderCodecs.js'
        }
      }
    });
  
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res");
      if (x != null) {
        this.ip_port = JSON.parse(x);
        console.log("inside parse", this.ip_port.result);
      }
      console.log("ip_port arr v", this.ip_port.result.DICOM);
      console.log("ip_port", this.ip_port);
    }
    this.dicomUrl = this.ip_port.result.DICOM + this.ip_port.result.Privacy_dicom_anonymize; // + environment.dicomUrl
  }

  // Handles API errors and displays a snackbar message
  handleError(error: any, customErrorMessage?: any) {
    console.log(error);
    console.log(error.status);
    console.log(error.error.detail);
    let message;
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error.detail || error.error.message || "API has failed";
    }
    const action = 'Close';
    this.openSnackBar(message, action);
  }

  // Opens a snackbar with a custom message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // -------------HANDLE DICOM IMAGE VIEWER----------------
  loadDICOMImages(files: any, x: any, y: any) {
    console.log("LOAD DICOM IMAGE FUN");
    this.dicom = true;
    this.preview = true;
    if (y == 1) {
      files = this.dicomFile[0];
    } else if (y == 2) {
      files = this.dicomFile[1];
    } else if (y == 3) {
      files = this.dicomFile[2];
    }
    if (files) {
      let imageList: any[] = [];
      const fileList: Array<File> = [files];
      fileList.sort((a, b) => a.name.localeCompare(b.name));
      cornerstoneWADOImageLoader.wadouri.dataSetCacheManager.purge();

      for (let i = 0; i < fileList.length; i++) {
        const dicomFile: File = fileList[i];
        const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(dicomFile);
        imageList.push(imageId);
      }
      this.viewPort.resetAllTools();
      this.viewPort.loadStudyImages(imageList);
    }
  }

  // Handles DICOM file selection from a URL
  onclick(s: any) {
    console.log("dicom1===", s)
    fetch(s)
      .then(response => response.blob())
      .then(blob => {
        const file = new File([blob], s.replace(/^.*[\\\/]/, { type: 'dicom/dcm' }))
        console.log("conver6ec file ", file);
        this.selectedDicomFile = file;
        this.dicomFile.push(file)
        this.arr.push(this.dicomFile)
      })
      .catch(error => {
        console.error('error converting imgageurl to file: ');
      })
  }

    // Handles DICOM file selection and loading
  onClick(s: any) {
    this.isLoadingFile = true; // Set loading state to true
    this.table = false;
    this.selectedImage = s;
    this.form.updateValueAndValidity();
    this.demoFile = [];
    this.files = [];
    this.preview = false;
  
    const fileName = s.replace(/^.*[\\\/]/, '').replace(/\[object Object\]/g, '');
    const loadedFile = this.loadedImagesMap.get(fileName); // Check if the image is already loaded
  
    if (loadedFile) {
      // Use the already loaded file
      this.selectedFile = loadedFile;
      this.demoFile.push(loadedFile);
      this.files.push(loadedFile);
      this.isLoadingFile = false; // Set loading state to false
      this.uploadFilesSimulator(0, this.files);
    } else {
      // Fetch the image if not already loaded
      fetch(s)
        .then(response => response.blob())
        .then(blob => {
          const file = new File([blob], fileName, { type: 'dicom/dcm' });
          this.selectedFile = file;
          this.demoFile.push(file);
          this.files.push(file);
          this.isLoadingFile = false; // Set loading state to false
          this.uploadFilesSimulator(0, this.files);
        })
        .catch(error => {
          console.error('error converting image URL to file: ');
          this.isLoadingFile = false; // Set loading state to false on error
        });
    }
  }

  // -----------IMAGE FULLSCREEN---------------------
  openDialog(data: any) {
    console.log("data===", data);
    let imageData = data;
    if (!data.startsWith('data:image/')) {
      imageData = `data:image/png;base64,${data}`;
    }
    console.log("imageData", imageData);
    this.dialog.open(ImageDialogComponent, {
      data: { image: imageData, flag: true },
      backdropClass: 'custom-backdrop'
    });
  }

  // -----------HANDLE FILE UPLOAD----------------
  onFileChange(event: any) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
      console.log(text);
    };
    reader.readAsText(event.target.files[0]);
  }

  // Handles file browsing for DICOM files
  fileBrowseHandler(imgFile: any) {
    const allowedTypes = ['application/dicom', 'application/dicom+json', 'application/dicom+xml', 'application/dicom+zip'];
    const allowedExtensions = ['dcm'];
    const file = imgFile.target.files[0];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    console.log("fileBrowseHandler", file.type, fileExtension);

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      this._snackBar.open('Please select a valid DICOM file (.dcm)', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return;
    } else {
      this.selectedImage = '';
      this.files = [];
      this.prepareFilesList(imgFile.target.files);
      this.demoFile = this.files;
      this.file = this.files[0];
      console.log(this.demoFile);
      this.preview = false;
      this.form.setValue(this.files);
    }
  }

  // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    for (const item of files) {
      const cleanedName = item.name.replace(/\[object Object\]/g, '');
      const newFile = new File([item], cleanedName, { type: item.type });
      this.files.push(newFile);
    }
    console.log("PREPARE", this.files);
    this.uploadFilesSimulator(0, files);
  }

  // Simulates file upload progress
  uploadFilesSimulator(index: number, files: any) {
    setTimeout(() => {
      if (index === this.files.length) {
        return;
      } else {
        this.files[index].progress = 0;
        const progressInterval = setInterval(() => {
          if (this.files[index].progress >= 100) {
            clearInterval(progressInterval);
            this.loadDICOMImages(this.files[0], 1, 4);
          } else {
            this.files[index].progress += 10;
          }
        }, 200);
      }
    }, 1000);
  }

  cancelUpload() {
    this.files = [];
    this.Reset();
  }

  // -----------HANDLE ON SUBMIT---------------------
  Submit() {
    if (this.form.invalid) {
      this.snackBar.open('Please select a File before Submitting', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      return;
    }
    this.spinner = true;
    this.isLoadingOutput = true; // Set loading state to true
    const regex = /^(.*\.dcm$).*/;
    if (this.demoFile.length == 0) {
      console.log("EMPTY");
    } else {
      for (let i = 0; i < this.demoFile.length; i++) {
        const fileData = new FormData();
        this.selectedFile = this.demoFile[i];
        const isMatch = regex.test(this.selectedFile.name);
        if (!isMatch) {
          console.log("HEY");
        } else {
          console.log(this.selectedFile.name);
          fileData.append('payload', this.selectedFile);
          this.dicomService.api(this.dicomUrl, fileData).subscribe((res) => {
            console.log(res);
            this.res1 = this.sanitizeImage(res.original);
            this.res2 = this.sanitizeImage(res.anonymize);
            this.table = true;
            this.spinner = false;
            this.isLoadingOutput = false; // Reset loading state
          }, error => {
            this.handleError(error);
            this.isLoadingOutput = false; // Reset loading state on error
          });
        }
      }
    }
  }

  // -----------HANDLE ON RESET---------------------
  Reset() {
    console.log("RESET CALLED");
    this.preview = false;
    this.files = [];
    this.demoFile = [];
    this.selectedFile = "";
    this.selectedImage = "";
    this.table = false;
    this.spinner = false;
    this.isLoadingOutput = false;
    this.isLoadingFile = false; // Set loading state to false
    this.dicom = false
    this.dicomFile = []
    this.onclick(this.dicom1);
    this.onclick(this.dicom2);
    this.onclick(this.dicom3);
  }

  // Sanitizes image data for safe rendering
  sanitizeImage(imageData: string): SafeUrl {
    return this.sanitizer.bypassSecurityTrustUrl('data:image/jpg;base64,' + imageData);
  }
}