/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from '../_models/paging-config.model';
import { NonceService } from '../nonce.service';
import { Router } from '@angular/router';
import * as saveAs from 'file-saver';

@Component({
  selector: 'app-bulk-processing',
  templateUrl: './bulk-processing.component.html',
  styleUrls: ['./bulk-processing.component.css']
})

export class BulkProcessingComponent {

  file: File | any;
  files: any[] = [];
  demoFile: any[] = [];
  filePreview: any = '';
  explainabilityForm: FormGroup;
  anotherOptionControl: FormControl;
  anotherOptions: any[] =['all', 'privacy-fake', 'privacy-anonymize', 'safety'];
  dataReceived: boolean = false;
  triggerPrompt: boolean = false;
  promptResponse: boolean = false;
  spinner: boolean = false;
  showTable: boolean = false;
  spinnerTrigger: boolean = false;
  promptText: any = '';
  tableData: any = [];
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  pagingConfig: PagingConfig = {} as PagingConfig;
  ragId: string = '';
  private THOTUrl: any;
  private COTUrl: any;
  private DOCUrl: any;
  private getTableDataUrl: any;
  private submitFilesUrl: any;
  private ragTriggerUrl: any;
  thotResponse: string = '';
  thotTime: any
  thotResult: any = '';
  thotSource: any;
  thotExplanation:any ='';
  cotResponse: string = '';
  cotTime: any
  cotResult: any = '';
  cotSource: any;
  cotExplanation:any ='';
  clickedDocDetId: number | null = null;

  constructor(
    private fb: FormBuilder,
    public dialog: MatDialog,
    public _snackBar: MatSnackBar,
    private https: HttpClient,
    public nonceService:NonceService,
    private router: Router) {
    this.explainabilityForm = new FormGroup({})
    this.anotherOptionControl = new FormControl();
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
  }

  // Initializes the component and sets up API lists and form controls
  ngOnInit() {
    let ip_port: any;
    ip_port = this.getLocalStoreApi();
    this.setApilist(ip_port);
    this.explainabilityForm = this.fb.group({
      anotherOptionControl: this.anotherOptionControl
    });
    this.getTableData();
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if (res != null) {
        return ip_port = JSON.parse(res)
      }
    }
  }

  // Sets the API list URLs
  setApilist(ip_port: any) {
    this.THOTUrl = ip_port.result.Rag + ip_port.result.RagTHOT;
    this.COTUrl = ip_port.result.Rag + ip_port.result.RagCOT;
    this.DOCUrl = ip_port.result.Rag + ip_port.result.docDetail;
    this.getTableDataUrl = ip_port.result.BulkProcess + ip_port.result.getBulkTable;
    this.submitFilesUrl = ip_port.result.BulkProcess + ip_port.result.bulkSubmit;
    this.ragTriggerUrl = ip_port.result.BulkProcess + ip_port.result.bulkRagLoad;
  }

  // Get api fetches for table data
  getTableData() {
    this.dataReceived = false;
    this.showTable = true;
    this.https.get(this.getTableDataUrl).subscribe((res: any) => {
      this.tableData = res?.res?.map((rowData: any) => {
        rowData.isExpand = false; // Add isExpand property
        rowData.subTable = []; // Add subTable property
        return rowData;
      });
      this.onTableDataChange(this.currentPage)
      this.dataReceived = true;
    },
    (error) => {
      console.log(error);
    });
  }

  // File upload
  onFileChange(event: any) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
      // console.log(text);
    };
    reader.readAsText(event.target.files[0]);
    this.fileBrowseHandler(event);
  }

  // File upload handler
  fileBrowseHandler(File: any) {
    this.prepareFilesList(File.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
    const reader = new FileReader();
    reader.readAsDataURL(this.files[0]);
    reader.onload = (_event) => {
      const base64String = reader.result as string;
      this.filePreview = base64String;
    };
  }

  // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    for (let index = 0; index < files.length; index++) {
      const item = files[index];
      const cleanedName = item.name.replace(/\[object Object\]/g, '');
      const newFile = new File([item], cleanedName, { type: item.type });
      this.files.push(newFile);
    }
    this.files.forEach((file: any, index) => {
      this.uploadFilesSimulator(index, files);
    });
  }

  // Simulates file upload progress
  uploadFilesSimulator(index: number, files: any) {
    this.files[index].progress = 0;
    const progressInterval = setInterval(() => {
      if (this.files[index].progress >= 100) {
        clearInterval(progressInterval);
      } else {
        this.files[index].progress += 10;
      }
    }, 200);
  }

  // Removes a file from the list
  removeFile(index: any) {
    if(index === 'all') {
      this.demoFile = [];
      this.files = [];
      this.file = null;
    }
    else {
      this.demoFile.splice(index, 1);
      // this.files.splice(index, 1);
    }
  }

  // Selected options of multi-select
  onSelectionChange(event: any): void {
    const selectedValues = event.value;    
    if (selectedValues.includes('all')) {
      this.anotherOptionControl.setValue(['privacy-fake','privacy-anonymize', 'safety']);
    }
  }

  // Reset all values
  resetAll() {
    this.anotherOptionControl.setValue([]);
    this.removeFile('all');
    this.getTableData();
    this.dataReceived = false;
    this.triggerPrompt = false;
    this.promptResponse = false;
  }

  // Submit button call api and sends uploaded files and selected options
  submit() {
    if(this.files.length > 0 && this.anotherOptionControl.value !== null) {
      this.showTable = true;
      this.spinner = true;
      const formData = new FormData();
      this.demoFile.forEach((file: any) => {
        formData.append('files', file);
      });
      formData.append('checks', this.anotherOptionControl.value.join(','));
      
      this.https.post(this.submitFilesUrl, formData).subscribe((res: any) => {
        this.dataReceived = true;
        this.getTableData();
        this._snackBar.open('File Submitted Successfully!', '✖', {
          horizontalPosition: 'end',
          verticalPosition: 'top',
          duration: 3000,
        });
        this.removeFile('all');
        this.spinner = false;
      },
      (error) => {
        console.log(error);
        this._snackBar.open('Failed to Submit. Please Try again.', '✖', {
          horizontalPosition: 'end',
          verticalPosition: 'top',
          duration: 3000,
        });
        this.spinner = false;
      });
    }
    else {
      let msg = '';
      this.files.length === 0 ? msg = 'Please upload a file' : msg = 'Please select an option';
      this._snackBar.open(msg, '✖', {
        horizontalPosition: 'end',
        verticalPosition: 'top',
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
    }
  }

  // Pagination
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.tableData.length;
  }

  // Trigger RAG
  triggerRAG(id: number, totalFiles: any) {
    this.clickedDocDetId = id;
    this.spinnerTrigger = true;
    this.triggerPrompt = false;
    let btnId = id.toString();
    const formData = new FormData();
    formData.append('docId', btnId);
    
    this.https.post(this.ragTriggerUrl, formData).subscribe((res: any) => {
      this.ragId = res?.id;
      if(this.ragId !== '' && this.ragId !== null && this.ragId !== undefined && res !== null) {
        this.triggerPrompt = true;
        this.router.navigate(['responsible-ui/workbench']);
        sessionStorage.setItem('vectorId', this.ragId);
        sessionStorage.setItem('totalRagFiles', totalFiles);
        this.spinnerTrigger = false;
      }
      else {
        this._snackBar.open(`${res?.detail}. Please try again later!`, '✖', {
          horizontalPosition: 'end',
          verticalPosition: 'top',
          duration: 3000,
        });
        this.spinnerTrigger = false;
      }
    },
    (error) => {
      console.log(error);
      this._snackBar.open('Failed to Trigger RAG. Please Try again.', '✖', {
        horizontalPosition: 'end',
        verticalPosition: 'top',
        duration: 3000,
      });
      this.spinnerTrigger = false;
    });
  }

  // api for prompt
  sendPrompt() {
    if(this.promptText != '') {
      const payload = {
        fileupload: 'true',
        text: this.promptText,
        vectorestoreid: this.ragId,
      };

      this.callForThot(payload);
      this.callForCot(payload);
        this.promptResponse = true;
    }
  }
    
  // API call for THOT 
  callForThot(payload: any) {
    this.thotResponse = '';
    this.https.post(this.THOTUrl, payload).subscribe((response: any) => {
      this.thotResponse = response.thot_response;
      this.thotTime = response.timetaken
      this.thotSource = response['source-name'];
      this.splitFunction(this.thotResponse, 'thot');
    }, 
    error => {
      console.error(error);
    });
  };

  // API call for COT
  callForCot(payload: any) {
    this.cotResponse = '';
    this.https.post(this.COTUrl, payload).subscribe((response: any) => {
      this.cotResponse = response.cot_response;
      this.cotTime = response.timetaken
      this.cotSource = response['source-name'];
      this.splitFunction(this.cotResponse, 'cot');
    },
    error => {
      console.error(error);
    });
  };

  // Splits the response string into explanation and result
  splitFunction(res: string, type: string) {
    const lines = res.split('\n');
    let explanationValue = '';
    let isExplanation = false;
    const resultLine = lines.find(line => line.startsWith('Result:'));
    const resultAnswer = lines.find(line => line.startsWith('Answer:'));
    let resultValue;
    if (resultLine) {
      resultValue = resultLine.split('Result:')[1];
    } else if (resultAnswer) {
      resultValue = resultAnswer.split('Answer:')[1];
    }
    if (type === 'cot') {
      this.cotResult = resultValue?.replace(/"/g, ''); // Remove the surrounding quotes
    } else if (type === 'thot') {
      this.thotResult = resultValue?.replace(/"/g, ''); // Remove the surrounding quotes
    }

    for (const line of lines) {
      if (line.startsWith('Explanation:')) {
        isExplanation = true;
        explanationValue += '' + line.split('Explanation:')[1]?.trim() + '\n';
      } else if (line.startsWith('Source:')) {
        isExplanation = false;
        break;
      } else if (isExplanation) {
        explanationValue += line.trim() + '\n';
      }
    }
    if (type === 'cot') {
      this.cotExplanation = explanationValue.replace(/"/g, '').replace(/\n/g, '');
    } else if (type === 'thot') {
      this.thotExplanation = explanationValue.replace(/"/g, '').replace(/\n/g, '');
    }
  }

  // Toggles the row expansion
  toggleRow(row: any) {
    row.isExpand = !row.isExpand;
    if (row.isExpand && row.subTable.length === 0) {
      this.getTableSubData(row);
    }
  }

  // Fetches sub-table data for the specific row
  getTableSubData(row: any) {
    const payload = { docDtlId: row.DocDetId };
    this.https.post(this.DOCUrl, payload).subscribe((res: any) => {
      if(res.result.length > 0) {
        row.subTable = res.result;
      }
      else {
        row.subTable = [];
        row.isExpand = false;
      }
    },
    (error) => {
      console.log(error);
    });
  }

  // Downloads the file from server
  dowloadFile(row: any) {
    const params = new HttpParams()
    .set('blob_name', row.ProcDocPath)
    .set('container_name', 'bulk-data');
    
    const url = 'https://rai-toolkit-dev.az.ad.idemo-ppc.com/api/v1/azureBlob/getBlob';

    this.https.get(url, { params, responseType: 'blob' }).subscribe((res: Blob) => {
      const blob = new Blob([res], { type: 'text/csv' });
      saveAs(blob, row.ProcDocPath);
    },
    (error) => {
      console.error('Download failed', error);
    });
  }

}
