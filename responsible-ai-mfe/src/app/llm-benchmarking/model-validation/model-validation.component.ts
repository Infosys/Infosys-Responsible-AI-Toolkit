/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Component, ViewChild, ViewEncapsulation } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NgbPopover } from '@ng-bootstrap/ng-bootstrap';
import { PreviewModalComponent } from './preview-modal/preview-modal.component';
import { MatDialog } from '@angular/material/dialog';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-model-validation',
  templateUrl: './model-validation.component.html',
  styleUrls: ['./model-validation.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class ModelValidationComponent {
  // FOR SHIMMER
  isLoadingSelectType = true;
  isLoadingPrompt = true;
  isLoadingAvailableModel = true;
  isLoadingAvailableDataset = true;
  ////
  apiUrlEndpoints: any = {};
  listOfavailableModels: any = [];
  listOfaviablableDataSets: any = [];
  demoFile: any;
  file: any;
  files: any = [];

  availableModels: any;
  availableDataSets: any;
  showSpinner1: boolean = false;
  files2: any = [];

  selectedPrompt = '';
  placeholder = 'Number of Samples';
  datasetLength: any;
  prompts: any;
  modelValidateDataSource: any;
  labels: any;
  showResultTab: boolean = false;
  showResultLoader: boolean = false;

  constructor(public https: HttpClient,
    private _snackBar: MatSnackBar,
    private dialog: MatDialog,
    public nonceService:NonceService
  ) { }

  // Initializes the component and sets up API endpoints
  ngOnInit(): void {
    let ip_port
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if(res != null){
       ip_port = JSON.parse(res)
      }
    }
    this.apiUrlEndpoints.securityLLM_availableDatasets = ip_port.result.Security_llm + ip_port.result.SecurityLLM_availableDataSets;
    this.apiUrlEndpoints.securityLLM_previewDataSet = ip_port.result.Security_llm + ip_port.result.SecurityLLM_previewDataSets;
    this.apiUrlEndpoints.securityLLM_availableModels = ip_port.result.Security_llm + ip_port.result.SecurityLLM_availableModels;
    this.apiUrlEndpoints.securityLLM_addDataSet = ip_port.result.Security_llm + ip_port.result.SecurityLLM_addDataSet;
    this.apiUrlEndpoints.securityLLM_addModel = ip_port.result.Security_llm + ip_port.result.SecurityLLM_addModel;
    this.apiUrlEndpoints.securityLLM_deleteDataSet = ip_port.result.Security_llm + ip_port.result.SecurityLLM_deleteDataSet;
    this.apiUrlEndpoints.securityLLM_deleteModel = ip_port.result.Security_llm + ip_port.result.SecurityLLM_deleteModel;
    this.apiUrlEndpoints.securityLLM_validateModel = ip_port.result.Security_llm + ip_port.result.SecurityLLM_validateModel;

    // set timeout for isloading

    this.isLoadingSelectType = false;
    this.isLoadingPrompt = false;

    this.getAvailableDataSets();
    this.getAvailableModels();
  }

  // Handles dataset selection and updates the prompt
  onDataSetSelect(event: any) {
    const selectedOption = event.target.value;
    this.getLengthofDataSet(selectedOption);
    if (selectedOption == 'qqp') {
      this.selectedPrompt = 'Can these two statements be considered equal in meaning?: {content}';
    }
    else if (selectedOption == 'sst2') {
      this.selectedPrompt = 'Determine the emotion of the following sentence as positive or negative: {content}';
    }
    else if (selectedOption == 'cola') {
      this.selectedPrompt = 'Assess the following sentence and determine if it is grammatically correct: {content}';
    }
    else {
      this.selectedPrompt = '';
    }
  }

  // Fetches the length of the selected dataset
  getLengthofDataSet(selectedDataSetValue: any) {
    const fData = new FormData();
    const a2 = '1';
    fData.append('datasetName', selectedDataSetValue);
    fData.append('numberOfEntries', a2);
    this.https.post(this.apiUrlEndpoints.securityLLM_previewDataSet + '?datasetName=' + selectedDataSetValue + '&numberOfEntries=' + a2, fData).subscribe(
      (res: any) => {
        this.datasetLength = res['length'];
        this.placeholder = 'MaxLimit - ' + this.datasetLength;
      },
      error => {
        this.handleError(error)
      }
    );
  }


  // ---------------HANDLE SUBMIT---------------------
  submitValidateModelForm(formValue:any) {
    let { dataSetName , model , noOfSamples} = formValue
    console.log(noOfSamples,this.datasetLength)
    if (noOfSamples != '' && noOfSamples <= this.datasetLength) {
      // this.modelValidateFlag = false;
      this.prompts = [];
      this.labels = [];
      this.showResultTab = true;
      this.showResultLoader = true;
      const params = new HttpParams();
      params.set('modelName', model);
      params.set('dataset', dataSetName);
      params.set('numberOfSamples', noOfSamples);
      const s = noOfSamples;
      const a: string[] = this.selectedPrompt.split(',').map(item => item.trim());
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
      });
      const options = { headers: headers, params: params };
      const modelName = model;
      const dataSet = dataSetName;
      this.https.post(this.apiUrlEndpoints.securityLLM_validateModel + '?modelName=' + modelName + '&dataset=' + dataSet + '&numberOfSamples=' + s, JSON.stringify(a), options).subscribe(
        (res: any) => {
          console.log("API CALL HAS BEEN SUCCESSFULL",res)
          this.modelValidateDataSource = res;
          this.showResultLoader = false
          this.validateModelData();
        },
        error => {
          this.showResultTab = false
          this.handleError(error)
        }
      );
    } else {
      console.log("Number of samples should be less than or equal to the dataset length")
      this._snackBar.open("Number of samples should be less than or equal to the dataset length", "Close", {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
    }
  }

  // Validates the model data
  validateModelData(){
    try{
    const a = this.modelValidateDataSource.prompts.length;
    for(let i=0;i<a;i++){
      this.prompts.push(this.modelValidateDataSource.prompts[i]);
      this.labels.push(this.modelValidateDataSource[this.modelValidateDataSource.prompts[i]])
    }
    console.log("List of prompts",this.prompts);
    console.log("List of labels",this.labels);
  }catch(error){
    console.log("method failed",error);
  }
  }

  // ---------------RESET FORM---------------------
  resetForm(form: any) {
    form.resetForm();
    form.controls['model'].setValue('');
    form.controls['dataSetName'].setValue('');
    this.placeholder = 'Number of Samples';
    this.showResultTab = false;
  }

  // OPEN MODAL
  openPrevModal(dataSetName: any, noOfEntries: any, popOver: any) {
    if (noOfEntries == undefined || noOfEntries == null || noOfEntries == '') {
      const message = 'Please enter the number of entries';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    this.showSpinner1 = true;
    const fData = new FormData();
    fData.append('datasetName', dataSetName);
    fData.append('numberOfEntries', noOfEntries);
    this.https.post(this.apiUrlEndpoints.securityLLM_previewDataSet + '?datasetName=' + dataSetName + '&numberOfEntries=' + noOfEntries, fData).subscribe(
      (res: any) => {
        this.showSpinner1 = false;
        popOver.toggle()
        this.dialog.open(PreviewModalComponent, {
          width: '52vw',
          data: res[dataSetName],
          backdropClass: 'custom-backdrop'
        });
      },
      error => {
        this.showSpinner1 = false
        this.handleError(error)
      }
    );
  }

  // Add MODEL
  addModelFile(modelFileName: any, popOver: any) {
    if (modelFileName == undefined || modelFileName == null || modelFileName == '') {
      const message = 'Please enter the model name';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    if (this.files.length == 0) {
      const message = 'Please upload the model file';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    this.showSpinner1 = true;
    const fData = new FormData();
    fData.append('modelName', modelFileName);
    fData.append('modelFile', this.files[0]);
    //this.logger.log("User has added modelFile",this.selectedModelFile);
    this.https.post(this.apiUrlEndpoints.securityLLM_addModel + '?modelName=' + modelFileName, fData).subscribe(
      (res: any) => {
        this.getAvailableModels();
        this.showSpinner1 = false;
        popOver.toggle()
        const message = "Model Added Successfully";
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 10000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.showSpinner1 = false;
        this.handleError(error)
      }
    );
  }

  // Add Data Set
  addDataSet(dataSetName: any, popOver: any) {
    if (dataSetName == undefined || dataSetName == null || dataSetName == '') {
      const message = 'Please enter the data set name';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    if (this.files2.length == 0) {
      const message = 'Please upload the data file';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    this.showSpinner1 = true;
    const fData = new FormData();
    fData.append('datasetName', dataSetName);
    fData.append('datasetFile', this.files2[0]);
    //this.logger.log("User added datafile",this.selectedDataFile);
    this.https.post(this.apiUrlEndpoints.securityLLM_addDataSet + '?datasetName=' + dataSetName, fData).subscribe(
      (res: any) => {
        this.getAvailableDataSets();
        this.showSpinner1 = false;
        const message = "DataSet Added Successfully";
        const action = 'Close';
        popOver.toggle()
        this._snackBar.open(message, action, {
          duration: 10000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.showSpinner1 = false;
        this.handleError(error)
      }
    );
  }

  // POPOver
  openPopOver(p: any) {
    console.log(p)
    if (p.isOpen()) {
      console.log('Popover is open');
      p.toggle();
    } else {
      p.toggle();
      console.log('Popover is closed');
    }
  }

  // ----------Handle File Upload--------------------
  fileBrowseHandler(file: any) {
    this.prepareFilesList(file.target.files);
  }

  // Prepares the list of model files
  prepareFilesList(files: Array<any>) {
    this.files = [];
    for (const item of files) {
      this.files.push(item);
    }
    this.uploadFilesSimulator(0, "modelFile")
  }

  // Handles file upload for dataset files
  fileBrowseHandler2(file: any) {
    this.prepareFilesList2(file.target.files);
  }

   // Prepares the list of dataset files
  prepareFilesList2(files: Array<any>) {
    this.files2 = [];
    for (const item of files) {
      this.files2.push(item);
    }
    this.uploadFilesSimulator(0, "dataFile")
  }

   // Simulates file upload progress
  uploadFilesSimulator(index: number, files: any) {
    if (files == 'modelFile') {
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
              this.files[index].progress += 10;
            }
          }, 200);
        }
      }, 1000);
    }
    else {
      setTimeout(() => {
        if (index === this.files2.length) {
          console.log("RETURN")
          return;
        } else {
          this.files2[index].progress = 0;
          const progressInterval = setInterval(() => {
            if (this.files2[index].progress >= 100) {
              clearInterval(progressInterval);
            } else {
              this.files2[index].progress += 10;
            }
          }, 200);
        }
      }, 1000);
    }
  }

  removeFile() {
    this.files = [];
    this.files2 = [];
  }
  
  // Handles API errors and displays a snackbar message
  handleError(error: any) {
    console.log(error.status);
    console.log(error.error.detail);
    console.log(error);
    let message
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error.detail || error.error.message || "API has failed";
    }
    const action = 'Close';
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // Fetches the list of available datasets
  getAvailableDataSets() {
    this.https.get(this.apiUrlEndpoints.securityLLM_availableDatasets).subscribe(
      (res: any) => {
        this.availableDataSets = res;
        this.getListOfDataSets(res);
        this.isLoadingAvailableDataset = false;
      }, error => {
        this.handleError(error)
      }
    )
  }

  // Extracts dataset names from the API response
  getListOfDataSets(avaiableDataSetsVariable: any) {
    try {
      for (let i = 0; i < avaiableDataSetsVariable.length; i++) {
        this.listOfaviablableDataSets.push(avaiableDataSetsVariable[i].DatasetName);
      }
    } catch (error) {
      console.log(error)
    }
  }

  // Fetches the list of available models
  getAvailableModels() {
    this.https.get(this.apiUrlEndpoints.securityLLM_availableModels).subscribe(
      (res: any) => {
        this.availableModels = res
        this.getListOfModels();
        this.isLoadingAvailableModel = false;
      }, error => {
        this.handleError(error)
      }
    )
  }
  // Extracts model names from the API response
  getListOfModels() {
    try {
      for (let i = 0; i < this.availableModels.length; i++) {
        this.listOfavailableModels.push(this.availableModels[i].modelName);
      }
    } catch (error) {
      console.log(error)
    }
    console.log(this.listOfavailableModels)
  }

  // DELETE
  deleteModel(model: string) {
    const fData = new FormData();
    fData.append('modelName', model);
    this.https.post(this.apiUrlEndpoints.securityLLM_deleteModel + '?modelName=' + model, fData).subscribe(
      (res: any) => {
        this.getAvailableModels();
        const message = "Model Deleted Successfully";
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 10000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.handleError(error)
      }
    );
  }

  // Deletes a dataset
  deleteDataSet(dataSet: string) {
    const fData = new FormData();
    fData.append('datasetName', dataSet);
    this.https.post(this.apiUrlEndpoints.securityLLM_deleteDataSet + '?datasetName=' + dataSet, fData).subscribe(
      (res: any) => {
        this.getAvailableDataSets();
        const message = "DataSet Deleted Successfully";
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 10000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        this.handleError(error)
      }
    );
  }
}
