/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FileHandler } from './fileHandler'
import { Helper } from './helper';
import { DifferentialPrivacyService } from './differential-privacy.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { environment } from 'src/environments/environment'; `  `
import { NonceService } from '../nonce.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-differential-privacy',
  templateUrl: './differential-privacy.component.html',
  styleUrls: ['./differential-privacy.component.css'],
})

export class DifferentialPrivacyComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  supressionList: any;
  noiseList = [];
  rangeList = [];
  binaryList = [];
  form!: FormGroup;
  showSpinner1: boolean = false;
  showSpinner2: boolean = false;
  fileHandler = new FileHandler(this._snackBar);
  helper = new Helper();
  intialFromstatus = false;
  isLoading = false;
  favoriteSeason: any;
  sampleSrc1 = environment.imagePathurl + '/assets/image/csvIcon2.png';
  sampleFile1 = environment.imagePathurl + '/assets/samplefiles/DifferentialTest.csv';

  constructor(private differentialPrivacyService: DifferentialPrivacyService,
    public _snackBar: MatSnackBar,
    private fb: FormBuilder,
    public nonceService: NonceService) {
      this.fromCreation();
      this.fileHandler = new FileHandler(this._snackBar);
  }

  // Initializes the component and sets up API endpoints
  ngOnInit(): void {
    let ip_port: any

    ip_port = this.helper.getLocalStoreApi()
    this.helper.setApilist(ip_port)
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  submit() {
    if (this.fileHandler.fileExitsValidator() == true) {
      this.postFile();
    }
  }

  // Uploads the file to the server
  postFile() {
    this.showSpinner1 = true;
    let formData = new FormData();
    formData.append('dataset', this.fileHandler.file);

    this.differentialPrivacyService.postData(this.helper.diff_priv_file, formData).pipe(takeUntil(this.destroy$)).subscribe((res: any) => {
      this.setSelectOptionsList(res);
      this.showSpinner1 = false;
      this.intialFromstatus = true;
      this._snackBar.open('File uploaded successfully', 'Close', {
        duration: 2000,
      });
    },
    error => {
      this.errorMessageCall(error)
    });
  }

  // Sets the dropdown options based on the server response
  setSelectOptionsList(res: any) {
    this.supressionList = res.allHeadders
    this.noiseList = res.numaricHeadder
    this.rangeList = res.numaricHeadder
    this.binaryList = res.binaryHeadder
  }

  // Creates the form with required controls
  fromCreation() {
    this.form = new FormGroup({
      supressionList: new FormControl([], Validators.required),
      noiseList: new FormControl([], Validators.required),
      rangeList: new FormControl([], Validators.required),
      binaryList: new FormControl([], Validators.required),
    });
  }

  // Submits the form data to the server
  submitFrom() {
    if (this.form.valid) {
      this.showSpinner2 = true;
      const fileData = new FormData();
      fileData.append('suppression', this.form.value.supressionList);
      fileData.append('noiselist', this.form.value.noiseList);
      fileData.append('rangeList', this.form.value.rangeList);
      fileData.append('binarylist', this.form.value.binaryList);
      this.differentialPrivacyService.postform(this.helper.diff_priv_anonymize, fileData).pipe(takeUntil(this.destroy$)).subscribe((data: any) => {
        this.showSpinner2 = false;
        const blob = new Blob([data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'data.csv';
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error => {
        this.errorMessageCall(error)
      });
    }
    else {
      this._snackBar.open('Please select all the options', 'Close', {
        duration: 2000,
      });
    }
  }

  // Resets the form and its controls
  reset() {
    this.form.reset({
      supressionList: [],
      noiseList: [],
      rangeList: [],
      binaryList: [],
    });

    // Reset variables
    this.showSpinner1 = false;
    this.showSpinner2 = false;
    this.intialFromstatus = false;
    this.fileHandler.reset();

    // Reset lists
    this.supressionList = null;
    this.noiseList = [];
    this.rangeList = [];
    this.binaryList = [];

    // Close any open snack bars
    this._snackBar.dismiss();
    this.resetRadioButtons()
  }

  // Displays an error message in a snackbar
  errorMessageCall(error: any) {
    const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
    const action = "Close"
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // Handles the click event for downloading a sample file
  onClick(s: any) {
    fetch(s)
      .then((response) => response.blob())
      .then((blob) => {
        const file = new File(
          [blob],
          s.replace(/^.*[\\\/]/, ''),
          { type: 'text/csv' }
        );
        const abc: any = [];
        abc.push(file);
        this.fileHandler.fileBrowseHandler({ target: { files: abc } });
        this.fileHandler.prepareFilesList(abc);

        this.fileHandler.demoFile.push(file);
        this.form.get('file')?.setValue('validFileValue');
      })
      .catch((error) => {
        console.warn('error converting imgageurl to file: ');
      });
  }

  viewchange() {
    console.log('view change', this.favoriteSeason);
  }

  // Downloads a file from a given URL
  downloadFile(file: string, event: MouseEvent) {
    event.preventDefault(); // Prevent the default context menu from appearing
    const link = document.createElement('a');
    link.href = file; // Assuming `file` is the URL to the file
    link.download = file.split('/').pop() || 'downloaded-file'; // Extract the file name from the URL
    link.click();
  }

  resetRadioButtons() {
    this.favoriteSeason = null; // or any default value that doesn't match the radio button values
  }

}