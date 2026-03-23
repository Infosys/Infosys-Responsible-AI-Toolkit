/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { PagingConfig } from '../_models/paging-config.model';
import { environment } from 'src/environments/environment';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RoleManagerService } from '../services/role-maganer.service';
import { UserValidationService } from '../services/user-validation.service';
import { UnstructuredTextService } from './unstructured-text.service';
import { Subject, takeUntil } from 'rxjs';


@Component({
  selector: 'app-unstructured-text',
  templateUrl: './unstructured-text.component.html',
  styleUrls: ['./unstructured-text.component.css']
})
export class UnstructuredTextComponent implements OnInit, PagingConfig, OnDestroy {
  private destroy$ = new Subject<void>();

  // Pagination Configuration
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  pagingConfig: PagingConfig = {} as PagingConfig;
  tableSize: number[] = [5, 10, 15, 20];
  p: number = 1;

  // Loading States for Shimmer Effect
  isLoadingUpload = true;
  isLoadingSelectType = true;
  isLoadingTable = true;

  // UI Mode States
  uploadMode = false;
  promptMode = true;

  // Form and Data
  form: FormGroup;
  dataSource: any = [];

  // File Management
  files: any[] = [];
  demoFile: any[] = [];
  selectedFile: File | any;
  file: File | any;
  favoriteSeason: any;

  // User and Options
  user = "admin";
  showSpinner1 = false;
  tenantarr: any = [];
  selectedOptions: any = [];
  options: any = ["Privacy", "Profanity", "FM-Moderation", "Explainability"];

  // Asset Paths
  imageEnv = environment.imagePathurl + '/assets/image/';
  imgType = ".png";
  sampleSrc1 = environment.imagePathurl + '/assets/image/csvIcon2.png';
  sampleFile1 = environment.imagePathurl + '/assets/samplefiles/Sample_File1.csv';
  sampleFile2 = environment.imagePathurl + '/assets/samplefiles/Sample_File2.csv';

  // API Endpoints (only the ones actually used)
  lot_details: any;
  Workbench_UploadFile: any;

  // Utility
  intervalId: any;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    public roleService: RoleManagerService,
    private validationService: UserValidationService,
    private unstructuredTextService: UnstructuredTextService) {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
    this.form = this.fb.group({
      file: [null, Validators.required],
      options: [null, Validators.required]
    });
  }

  // ===== LIFECYCLE METHODS =====
  
  // Initializes the component and fetches initial data
  ngOnInit(): void {
    this.options = this.roleService.getSelectedTypeOptions("Workbench", "Unstructured-Text", "Traditional-AI")
    if (!this.roleService.checkActiveTabExists('Workbench', 'Unstructured-Text', 'Traditional-AI')) {
      this.uploadMode = false;
      this.promptMode = true;
    }

    let ip_port: any
    // user call should happen here
    this.user = this.validationService.getLogedInUser()
    // geting list of api from  local sotragge
    ip_port = this.validationService.getLocalStoreApi()

    // seting up api list
    this.setApilist(ip_port)
    this.getLotDetails(this.user)
  }

  // ===== INITIALIZATION & CONFIGURATION METHODS =====




  // Used to set the API list URLs (only the ones actually used)
  setApilist(ip_port: any) {
    // Only setting the API endpoints that are actually used in the component
    this.lot_details = ip_port.result.Questionnaire + ip_port.result.AllLotDetails;
    this.Workbench_UploadFile = ip_port.result.Questionnaire + ip_port.result.Workbench_UploadFile;
  }

  // ===== DATA MANAGEMENT METHODS =====

  // Fetches the details of the lots for the given user
  getLotDetails(user: any) {
    this.dataSource = [];
    const getUrl = this.lot_details + user;
    this.unstructuredTextService.getAllLotDetails(getUrl).pipe(takeUntil(this.destroy$)).subscribe(
      (res: any) => {
        if (!Array.isArray(res)) {
          this.isLoadingUpload = false;
          this.isLoadingSelectType = false;
          this.isLoadingTable = false;
          return
        }
        else {
          this.dataSource = res;
          this.pagingConfig.totalItems = this.dataSource.length;
        }
        this.isLoadingUpload = false;
        this.isLoadingSelectType = false;
        this.isLoadingTable = false;;
      });
  }

  // ===== UI EVENT HANDLERS =====

  // Toggles between upload mode and prompt mode
  ontoglechange(event: any) {
    if (event.checked == true) {
      this.uploadMode = false;
      this.promptMode = true;
    } else {
      this.uploadMode = true;
      this.promptMode = false;
    }
  }

  // Handles changes in the selected view
  viewchange() {
    console.log('view change', this.favoriteSeason);
  }

  // Updates the selected options for tenants
  viewoptions() {
    const myObject = { ...this.selectedOptions };
    const filteredKeys = this.filterKeysByBoolean(myObject);
    this.tenantarr = filteredKeys
    this.form.patchValue({
      options: this.tenantarr
    });
  }

  // ===== PAGINATION METHODS =====

  // Handles pagination changes
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.dataSource.length;
  }

  // Handles changes in the table size
  onTableSizeChange(event: any): void {
    this.pagingConfig.itemsPerPage = event.target.value;
    this.pagingConfig.currentPage = 1;
    this.pagingConfig.totalItems = this.dataSource.length;
  }

  // ===== FILE MANAGEMENT METHODS =====

  // Handles file changes (reading file content)
  onFileChange(event: any) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
      console.log(text);
    };
    reader.readAsText(event.target.files[0]);
  }

  // Handles file selection for upload
  fileBrowseHandler(imgFile: any) {
    const allowedTypes = ['text/csv'];
    if (!allowedTypes.includes(imgFile.target.files[0].type)) {
      let message = 'Please select a valid file type';
      this.openSnackBar(message, '✖');
    } else {
      this.prepareFilesList(imgFile.target.files);
      this.demoFile = this.files;
      this.file = this.files[0];
      this.form.patchValue({
        file: this.files[0]
      });
    }
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

  // Removes the selected file
  removeFile() {
    this.demoFile = []
    this.files = []
    this.resetRadioButtons()
  }

  // Simulates the file upload process
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

  // Handles the click event for downloading a sample file
  onClick(s: any) {
    fetch(s)
      .then((response) => response.blob())
      .then((blob) => {
        const file = new File(
          [blob],
          s.replace(/^.*[\\\/]/, { type: 'csv' })
        );
        const abc: any = [];
        abc.push(file);
        this.selectedFile = file;
        this.prepareFilesList(abc);
        this.demoFile.push(file);
        this.form.get('file')?.setValue('validFileValue');
      })
      .catch((error) => {
        console.error('error converting imgageurl to file: ');
      });
  }

  // Downloads the specified file
  downloadFile(file: string, event: MouseEvent) {
    event.preventDefault(); // Prevent the default context menu from appearing
    const link = document.createElement('a');
    link.href = file; // Assuming `file` is the URL to the file
    link.download = file.split('/').pop() || 'downloaded-file'; // Provide a default file name if undefined
    link.click();
  }

  // ===== FORM SUBMISSION & API METHODS =====

  // Submit call for the API
  submit() {
    if (this.form.invalid) {
      let message = 'Please select a File along with at least one of the Select type ';
      this.openSnackBar(message, '✖');
      return;
    }
    this.uploadFileData()
  }

  // Uploads the selected file data
  uploadFileData() {
    this.showSpinner1 = true;
    this.getLotDetails(this.user);
    const fileData = new FormData();
    this.selectedFile = this.files[0];
    fileData.append('file', this.selectedFile);
    fileData.append('userId', this.user)
    fileData.append('tenant', this.tenantarr)
    this.workBenchPostApiCall(fileData)
  }

  // Makes the API call to upload the file to the workbench
  workBenchPostApiCall(fileData: any) {
    this.unstructuredTextService.uploadFileToWorkbench(this.Workbench_UploadFile, fileData).pipe(takeUntil(this.destroy$)).subscribe((res) => {
      this.showSpinner1 = false
      clearInterval(this.intervalId);
      this.getLotDetails(this.user);
    },
      error => {
        this.showSpinner1 = false;
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        this.openSnackBar(message, '✖');
      });
  }

  // ===== UTILITY METHODS =====

  // Filters keys with boolean values from an object
  filterKeysByBoolean(obj: Record<string, boolean>): string[] {
    return Object.keys(obj).filter((key) => obj[key]);
  }

  // Checks if the given data indicates a completed status
  isCompleted(data: any): boolean {
    if (data == "Completed") {
      return true
    }
    else {
      return false
    }
  }

  // Resets the selected radio buttons
  resetRadioButtons() {
    this.favoriteSeason = null; // or any default value that doesn't match the radio button values
  }

  // Opens a snackbar with the specified message and action
  openSnackBar(message: string, action: string) {
    this.snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // Cleanup on component destruction
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}