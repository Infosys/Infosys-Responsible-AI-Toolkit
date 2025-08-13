/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { PagingConfig } from '../_models/paging-config.model';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { MatSelect } from '@angular/material/select';
import { MatDialog } from '@angular/material/dialog';
import { StructuredTextService } from './structured-text.service';
import { saveAs } from 'file-saver';
import { MatSnackBar } from '@angular/material/snack-bar';
import { StructuredTextModalComponent } from '../structured-text-modal/structured-text-modal.component';
import { delay } from 'rxjs';
// export interface Payload {
//   userId: string;
//   modelId: number;
//   dataId: number;
//   tenetName: string[];
//   appAttacks?: string[];
//   appExplanationMethods?: string[];
//   biasType?: string;
//   methodType?: string;
//   taskType?: string;
//   label?: string;
//   favorableOutcome?: string;
//   protectedAttribute?: any;
//   privilegedGroup?: any;
// }
@Component({
  selector: 'app-structured-text',
  templateUrl: './structured-text.component.html',
  styleUrls: ['./structured-text.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class StructuredTextComponent implements OnInit {
  @ViewChild('addModal') popupview3 !: ElementRef
  @ViewChild('content1') popupview1 !: ElementRef
  @ViewChild('select3') select3!: MatSelect;
  @ViewChild('select2') select2!: MatSelect;
  // FOR SHIMMER LOADING
  isLoadingTable = true;
  ////
  // --------PAGINATION CONFIGURATION----------------
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  pagingConfig: PagingConfig = {} as PagingConfig;

  allModels: any;
  allDataFiles: any;
  selectedDataFileId: number = 0;
  selectedTargetClassifier: any;
  selectedModelDataTypeValue: any;
  securityBatchId: any;
  applicableAttack: any = [];
  tenantarr: any = [];
  allSelected1: any;
  demoFile: any = [];
  fairSampleId: any;
  selectoption1: any;
  result: any;
  resultDummy: any;
  resultLabel: any;
  featureDrop: boolean = false;
  labelDrop: boolean = false;
  labelValue: any;
  nextFOButton: boolean = false;
  labelResult: any;
  FODrop: boolean = false;
  pAdrop: boolean = false;
  /** Label Drop  */
  resultFO: any;
  protectedResult: any;
  listShowlistForLabel = new Set();
  selectedLabel: any;
  fAValue: any;
  protAttDrop: boolean = false;
  selectedFO: any;
  Protected: boolean = false;
  padata: boolean = false;
  temp: any;
  ladata: any;
  labeltemp: any;
  pAResult: any;
  ldata: any;
  protAttResult: any;
  protectedAttValue: any;
  selectedPAArray: any[] = [];
  priviDrop: boolean = false;
  protAttrArray: any = [];
  public pa: string[] = [];
  palabeldata: any;
  selectedProtAtt: any;
  i: number = 1;
  listShowlistForPA = new Set();
  privDrop: boolean = false;
  priviRes: any;
  public pri: string[] = []
  privValue: any;
  selectedPriv: any;
  selectedPrivArray: any[] = [];
  public privAttArray: string[] = [];
  nextprivButton: boolean = false;
  nextprivButton1: boolean = false;
  finalSubmit: boolean = false;
  event2: any;
  c2: boolean = false;
  allSelectedMethod: boolean = false;
  selectedModelFileId: any;
  applicableMethod: any;
  allTenants: any;
  securityReport: any;
  deleteBatch: any;
  explanation_visualization:any;
  constructor(private dialog: MatDialog, public _snackBar: MatSnackBar, public https: HttpClient) {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
  }
  selectedOptions: any = []
  options: any = ["Fairness", "Explainability", "Security"]
  dataSource: any = [];

  loggedin_userId: any;

  security_applicableAttacks: any;
  getAllData: any;
  getAllModels: any;
  fairnessSubmit: any;
  fairnessReport: any;
  ExplainMethods: any;
  ExplainReport: any;
  batchGeneration: any;
  batchTable: any;
  allTenantsApi: any;
  ReportDownload: any;
  FairnessWrapDownload: any;
  //Expand Panel Model
  panelSecurity = false;
  panelExplain = false;
  panelFairness = false;
  selectedApplicableMethod: any;
  allSelected2 = false;
  listShowlist2 = new Set();
  // // // // // // // //
  selectedApplicableAttack: any;
  selectedOption: any;

  // SECURITY VARIABLES
  listShowlist1 = new Set();
  event1: any;
  c1: boolean = false;
  allSelectedInput = false;
  target_Data_Type = [
    { value: 'Tabular', viewValue: 'Tabular' },
    { value: 'Image', viewValue: 'Image' },
    { value: 'Text', viewValue: 'Text' },
  ];
  classifier_list = [
    { value: 'SklearnClassifier', viewValue: 'SklearnClassifier' },
    { value: 'ScikitlearnClassifier', viewValue: 'ScikitlearnClassifier' },
    { value: 'KerasClassifier', viewValue: 'KerasClassifier' },
    { value: 'PyTorchFasterRCNN', viewValue: 'PyTorchFasterRCNN' },
    { value: 'SklearnAPIClassifier', viewValue: 'SklearnAPIClassifier' }
  ];

  openRightSideModal() {
    const dialogRef = this.dialog.open(StructuredTextModalComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getAllBatches()
    });
  }

  //Fairness MODAL Variables
  public selectedBiasTypeOption: any;
  public selectedTaskTypeOption: any;
  public BiasTypeOptions: any[] = [
    { value: 'PRETRAIN', viewValue: 'PRETRAIN' },
    { value: 'POSTTRAIN', viewValue: 'POSTTRAIN' },
  ];

  public taskTypeOptions: any[] = [
    { value: 'CLASSIFICATION', viewValue: 'CLASSIFICATION' },
  ];
  public posttrain: any[] = [
    { value: 'STATISTICAL-PARITY-DIFFERENCE', viewValue: 'STATISTICAL-PARITY-DIFFERENCE' },
    { value: 'COHEN_D', viewValue: 'COHEN_D' },
    { value: 'DISPARATE_IMPACT', viewValue: 'DISPARATE_IMPACT' },
    { value: 'FOUR_FIFTHS_RULE', viewValue: 'FOUR_FIFTHS_RULE' },
    { value: 'STATISTICAL_PARITY', viewValue: 'STATISTICAL_PARITY' },
    { value: 'Z_TEST_DIFFERENCE', viewValue: 'Z_TEST_DIFFERENCE' },
    { value: 'ALL', viewValue: 'ALL' }

  ];
  public pretrain: any[] = [
    { value: 'STATISTICAL-PARITY-DIFFERENCE', viewValue: 'STATISTICAL-PARITY-DIFFERENCE' },
    { value: 'DISPARATE-IMPACT', viewValue: 'DISPARATE-IMPACT' },
    { value: 'SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS', viewValue: 'SMOOTHED_EMPIRICAL_DIFFERENTIAL_FAIRNESS' },
    { value: 'CONSISTENCY', viewValue: 'CONSISTENCY' },
    { value: 'BASE_RATE', viewValue: 'BASE_RATE' },
    { value: 'ALL', viewValue: 'ALL' }
  ]
  labelOption: [] = []
  listShowlistForLabelDummy = new Set();
  listShowlistForFO = new Set();

// Initializes the component and fetches initial data
  ngOnInit(): void {
    // make is loading false after 3 seconds
    // setTimeout(() => {
    //   this.isLoadingTable = false;
    // }, 3000);
    console.log("STRUCTURED TEXT")
    if (localStorage.getItem("userid") != null) {
      const userid = localStorage.getItem("userid");
      if (userid != null) {
        this.loggedin_userId = JSON.parse(userid);
      }
    }
    let ip_port: any
    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)

    // this.getModels();
    // this.getDataFiles();
    // this.getAllTenants();
    this.getAllBatches();
  }

  //-------------- used to set the api list urls ----------------
  setApilist(ip_port: any) {
    this.security_applicableAttacks = ip_port.result.SecurityWrapper + ip_port.result.security_applicableAttack;
    this.getAllData = ip_port.result.Workbench + ip_port.result.Workbench_Data;
    this.getAllModels = ip_port.result.Workbench + ip_port.result.Workbench_Model;

    this.fairnessSubmit = ip_port.result.Fairness + ip_port.result.FairSubmit;
    this.fairnessReport = ip_port.result.Fairness + ip_port.result.FairGenReport;
    this.ExplainMethods = ip_port.result.Explainability_Demo + ip_port.result.ExplainWorkMethods;
    this.ExplainReport = ip_port.result.Explainability_Demo + ip_port.result.ExplainGenReport;
    this.batchGeneration = ip_port.result.Workbench + ip_port.result.BatchGeneration;
    this.batchTable = ip_port.result.Workbench + ip_port.result.BatchTable;
    this.allTenantsApi = ip_port.result.Workbench + ip_port.result.AllTenant;
    this.ReportDownload = ip_port.result.WorkbenchReport + ip_port.result.DownloadWorkReport;
    this.FairnessWrapDownload = ip_port.result.Fairness + ip_port.result.FairnessWrapDownload;
    this.securityReport = ip_port.result.SecurityWorkbench + ip_port.result.SecurityReport;
    this.deleteBatch = ip_port.result.Workbench + ip_port.result.Workbench_deleteBatch;
    this.explanation_visualization = ip_port.result.explanation_visualization;
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

  // Checks if the given data indicates a completed status
  isCompleted(data: any): boolean {
    return true ? data == "Completed" : false
  }

  // ---------------------------GET INITIAL DATA Functions--------------------------
  getAllBatches() {
    console.log("GET ALL BATCHES CALLED")
    const formData = new FormData();
    formData.append("userId", this.loggedin_userId)
    this.https.post(this.batchTable, formData).subscribe((data: any) => {
      this.dataSource = data;
      this.onTableDataChange(this.currentPage)
      this.isLoadingTable = false;
    }, error => {
      console.log(error)
      const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'center',
        panelClass: ['le-u-bg-black'],
      });
    })
    // this.cdr.detectChanges();
  }
  // getModels() {
  //   // this.showSpinner1 = true;
  //   const formData = new FormData;
  //   formData.append("userId", this.loggedin_userId)
  //   this.https.post(this.getAllModels, formData).subscribe((res: any) => {
  //     this.allModels = res;
  //     // this.showSpinner1 = false;
  //     console.log("ALL MODELS", this.allModels)

  //   }, error => {
  //     console.log(error)
  //     const message = error.error.detail
  //     const action = "Close"
  //     // this._snackBar.open(message, action, {
  //     //   duration: 3000,
  //     //   horizontalPosition: 'center',
  //     //   panelClass: ['le-u-bg-black'],
  //     // });
  //   })
  // }
  // getDataFiles() {
  //   const formData = new FormData;
  //   formData.append("userId", this.loggedin_userId)
  //   this.https.post(this.getAllData, formData).subscribe((res: any) => {
  //     this.allDataFiles = res;
  //     console.log(this.allDataFiles)
  //   }, error => {
  //     console.log(error)
  //     const message = error.error.detail
  //     const action = "Close"
  //     // this._snackBar.open(message, action, {
  //     //   duration: 3000,
  //     //   horizontalPosition: 'center',
  //     //   panelClass: ['le-u-bg-black'],
  //     // });
  //   })
  // }
  // getAllTenants() {
  //   this.https.get(this.allTenantsApi).subscribe((res: any) => {
  //     this.allTenants = res;
  //   })
  // }

  //-----------------HANDLE REPORT FILE------------------------
  downloadReport1(batch: any) {
    const id = batch.BatchId;
    //const form = new FormData();
    //form.append('batchId', id);
    const body = new URLSearchParams();
    
    if (batch.TenetId == 2.2) {
    const payload = {'Batch_id': id}
      this.https.post(this.FairnessWrapDownload, payload ,{ responseType: 'blob',observe: 'response' }).subscribe(
        (res: any) => {
          let filename = this.genFile();
      //   const contentType = res.type;
      //   const urlCreator = window.URL || window.webkitURL;
      //   const a = document.createElement('a');
      //   let downloadUrl!: any;
      // if (contentType == 'application/pdf') {
      //  downloadUrl = urlCreator.createObjectURL(res);

      // } else if (contentType == 'application/octet-stream') {
      //     const blob = new Blob([res], { type: 'text/csv;charset=utf-8' });
      //      downloadUrl = urlCreator.createObjectURL(blob);
      // }
      // a.href = downloadUrl;
      // a.download = filename;
      // document.body.appendChild(a);
      // a.click();
      // a.remove();
      // urlCreator.revokeObjectURL(downloadUrl);

      const contentDisposition = res.headers.get('Content-Disposition');
      if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
        filename = contentDisposition.split('filename=')[1].trim().replace(/"/g, '');
      }
      this.downloadFile(res.body, filename);
        }, error => { 
          console.log(error)
          const message = error.error.detail
          const action = "Close"
        })
    } else {
      body.set('batchId', id.toString());
      this.https.post(this.ReportDownload, body, { responseType: 'blob', headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded') }).subscribe(
        (res: Blob) => {
          const filename = this.genFile();
          saveAs(res, filename);
        }, error => {
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          // this._snackBar.open(message, action, {
          //   duration: 3000,
          //   horizontalPosition: 'center',
          //   panelClass: ['le-u-bg-black'],
          // });
        })
    }

  }

  // Downloads a file with the given data and filename
  downloadFile1(data: Blob, filename: string) {
    const blob = new Blob([data], { type: data.type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
  
// Generates a unique filename with a timestamp
  genFile(): string {
    const timestamp = new Date().getTime();
    return `file_${timestamp}`;
  }

  // ------------------------Handle Model and Data File Selection Change--------------------------
  // selectDataMethod(data: any) {
  //   let selectedOptionIndex = data.options['selectedIndex']
  //   this.selectedDataFileId = data.options[selectedOptionIndex].id;
  //   this.fairSampleId = data.options[selectedOptionIndex].value;
  //   console.log("selectedDataFileId::", this.selectedDataFileId)
  //   console.log("selectedSampleFilesID::", this.fairSampleId)
  //   //const element = document.querySelector('[role="listbox"]');
  //   //if (element instanceof HTMLElement) {
  //   //  element.style.display = 'none';
  //   //}
  // }
  // async selectModelMethod(optionValue: any) {
  //   console.log(optionValue.value)
  //   let filteredModels = this.allModels.filter((r: any) => r.modelId == optionValue.value);
  //   console.log(filteredModels)
  //   optionValue = filteredModels[0]
  //   this.selectedTargetClassifier = optionValue.targetClassifier;
  //   this.selectedModelDataTypeValue = optionValue.targetDataType;
  //   this.selectedModelFileId = optionValue.modelId;
  //   const element = document.querySelector('[role="listbox"]');
  //   if (element instanceof HTMLElement) {
  //     element.style.display = 'none';
  //   }
  // }
  // applicableAttacksMethod() {
  //   const fdata = new FormData();
  //   //const fdata1 = new FormData();
  //   fdata.append('TargetClassifier', this.selectedTargetClassifier)
  //   fdata.append('TargetDataType', this.selectedModelDataTypeValue)
  //   const payload = {
  //     "datasetId": this.selectedDataFileId,
  //     "modelId": this.selectedModelFileId,
  //     "scope": null
  //   }

  //   this.https.post(this.security_applicableAttacks, fdata).subscribe(
  //     (res: any) => {
  //       this.applicableAttack = res
  //       console.log(this.applicableAttack)
  //       this.cdr.detectChanges();
  //     }, error => {
  //       // You can access status:
  //       console.log(error.status);
  //       console.log(error)
  //     }
  //   )
  //   this.https.post(this.ExplainMethods, payload).subscribe(
  //     (data: any) => {
  //       this.applicableMethod = data.methods;
  //       this.cdr.detectChanges();
  //     }
  //   )
  // }

  // // --------------Handle Checkbox Selections------------------
  // viewoptions() {
  //   console.log("Array===", this.selectedOptions)
  //   // [Privacy: true, Profanity: true, Explainability: true, FM-Moderation: true]
  //   const myObject = { ...this.selectedOptions };
  //   console.log("myObject===", myObject)
  //   const filteredKeys = this.filterKeysByBoolean(myObject);
  //   console.log("only keys", filteredKeys);
  //   this.tenantarr = filteredKeys
  // }
  // filterKeysByBoolean(obj: Record<string, boolean>): string[] {
  //   return Object.keys(obj).filter((key) => obj[key]);
  // }

  // ----------------Pagination-----------------
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.dataSource.length;
  }

  // -----------Generate Report----------------
  generateReport(batch: any, index: number) {
    this.dataSource[index].Status = "In-progress"
    if (batch.TenetId == 1.1) {
      this.https.post(this.ExplainReport, { "batchId": batch.BatchId }).subscribe((res1: any) => {
        this.getAllBatches();
        if (res1.status == 'FAILURE') {
          this._snackBar.open(res1.message, "Close", {
            duration: 3000,
            panelClass: ['le-u-bg-black'],
          });
        } else {
          this._snackBar.open("Report Generated Successfully", "Close", {
            duration: 3000,
            panelClass: ['le-u-bg-black'],
          });
        }
      }, error => {
        this.getAllBatches();
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      })
    } else if (batch.TenetId == 2.2) {
      this.https.post(this.fairnessReport, { "Batch_id": batch.BatchId }).subscribe((res1: any) => {
        this.getAllBatches();
        this._snackBar.open("Report Generated Successfully", "Close", {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }, error => {
        this.getAllBatches();
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });

      })
    } else if (batch.TenetId == 3.3) {
      const formData = new FormData();
      formData.append('batchId', batch.BatchId);
      this.https.post(this.securityReport, formData).subscribe((res1: any) => {
        this.getAllBatches();
        this._snackBar.open("Report Generated Successfully", "Close", {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });
      }, error => {
        this.getAllBatches();
        const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          panelClass: ['le-u-bg-black'],
        });

      })
    }
  }

  // ---------------Delete Batch-------------------
  deleteConfirmationBatch(batchId: any, tenetName: any) {
    const params = new URLSearchParams();
    params.set('userId', this.loggedin_userId)
    params.set('batchId', batchId.toString())
    // this.logger.log('batchId',batchId.toString());
    const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/x-www-form-urlencoded',
      }),
      body: params,
    };
    this.https.delete(this.deleteBatch, options).subscribe(
      (res: any) => {
        this.getAllBatches();
        const message = 'Record Deleted Successfully';
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 5000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      error => {
        if (error.status == 430) {
          const message = error.error.detail;
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          const message = (error && error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        }
      }
    );
  }
  //--------------------------------------------

  //--------------------MODAL---------------
  // openPopup() {
  //   if (this.tenantarr.length > 0)
  //     this.modalService.open(this.popupview3, { size: 'lg' });
  //   this.applicableAttacksMethod();
  // }
  //---------Security Collapse------------
  // toggleAllSelection1(event: any) {
  //   this.event1 = event;
  //   this.c1 = event.checked;
  //   this.allSelected1 = !this.allSelected1;
  //   if (this.allSelected1) {
  //     this.select2.options.forEach((item: MatOption) => {
  //       item.select();
  //       this.listShowlist1.add(item.value);
  //       const element = document.querySelector('[role="listbox"]');
  //       if (element instanceof HTMLElement) {
  //         element.style.display = 'none';
  //       }
  //       this.select2.close();
  //     });
  //   } else {
  //     this.select2.options.forEach((item: MatOption) => {
  //       item.deselect();

  //       this.listShowlist1.delete(item.value);
  //     });
  //   }
  // }
  // optionClick1() {
  //   let newStatus = true;
  //   this.select2.options.forEach((item: MatOption) => {
  //     if (!item.selected) {
  //       newStatus = false;
  //       this.allSelected1 = false;
  //       this.listShowlist1.delete(item.value);
  //     } else {
  //       this.listShowlist1.add(item.value);
  //     }
  //   });
  //   this.allSelectedInput = newStatus;
  // }


  // -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  //-------------Explainability Collapse---------------------
  // toggleAllSelection2(event: any) {
  //   this.event2 = event;
  //   this.c2 = event.checked;
  //   this.allSelected2 = !this.allSelected2;
  //   if (this.allSelected2) {
  //     this.select3.options.forEach((item: MatOption) => {
  //       item.select();
  //       this.listShowlist2.add(item.value);
  //       const element = document.querySelector('[role="listbox"]');
  //       if (element instanceof HTMLElement) {
  //         element.style.display = 'none';
  //       }
  //       this.select3.close();
  //     });
  //   } else {
  //     this.select3.options.forEach((item: MatOption) => {
  //       item.deselect();
  //       this.listShowlist2.delete(item.value);
  //     });
  //   }
  // }
  // optionClick2() {
  //   let newStatus = true;
  //   this.select3.options.forEach((item: MatOption) => {
  //     if (!item.selected) {
  //       newStatus = false;
  //       this.allSelected2 = false;
  //       this.listShowlist2.delete(item.value);
  //     } else {
  //       this.listShowlist2.add(item.value);
  //     }
  //   });
  //   this.allSelectedMethod = newStatus;

  // }
  // -----------------Fairness Collapse---------------------
  // onSelectBiasType(e: any) {
  //   this.selectedBiasTypeOption = e.value;
  // }
  // onSelectTaskType(e: any) {
  //   this.selectedTaskTypeOption = e.value;
  // }
  // onSelectMethodType(e: any) {
  //   this.selectoption1 = e.value;
  // }
  // fairSubmit() {
  //   const fileData = new FormData();
  //   fileData.append('biasType', this.selectedBiasTypeOption);
  //   fileData.append('methodType', this.selectoption1);
  //   fileData.append('fileId', this.fairSampleId);
  //   fileData.append('taskType', this.selectedTaskTypeOption);

  //   this.structuredTextService.api(this.fairnessSubmit, fileData).subscribe({
  //     next: (data: { AttributesInTheDataset: { CategoricalAttributesList: any; }; }) => {
  //       console.log(data)
  //       this.result = data;
  //       this.resultDummy = data.AttributesInTheDataset.CategoricalAttributesList
  //       this.resultLabel = data.AttributesInTheDataset.CategoricalAttributesList;
  //       this.labelOption = this.resultLabel
  //       this.listShowlistForLabelDummy = this.resultLabel
  //       this.featureDrop = true;
  //       this.labelDrop = true;
  //     }, error: error => {
  //       console.log(error.status);
  //       if (error.status == 430) {
  //         console.log(error.error.detail)
  //         console.log(error)
  //         const message = error.error.detail
  //         const action = "Close"
  //         /**
  //         this._snackBar.open(message, action, {
  //           duration: 3000,
  //           horizontalPosition: 'left',
  //           panelClass: ['le-u-bg-black'],
  //         });
  //          */
  //       } else {
  //         console.log(error)
  //         const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
  //         const action = "Close"
  //         //this._snackBar.open(message, action, {
  //         //  duration: 3000,
  //         //  horizontalPosition: 'left',
  //         //  panelClass: ['le-u-bg-black'],
  //         //});
  //       }
  //     }
  //   })
  // }

  // LABEL DROP
  // optionClickFromLabel() {
  //   this.labelValue = this.listShowlistForLabel.values().next().value
  //   console.log(this.labelValue)
  //   this.nextFOButton = true;
  //   this.labelResult = this.listShowlistForLabel
  //   this.FODrop = true
  //   console.log(this.labelResult)
  //   this.getLabel();
  //   // Get the DOM element by role
  //   const element = document.querySelector('[role="listbox"]');
  //   // Add a style to the div
  //   if (element instanceof HTMLElement) {
  //     element.style.display = 'none';
  //   }
  // }
  // getLabel() {
  //   this.pAdrop = true;
  //   const fo = this.selectedLabel
  //   console.log(fo)
  //   this.resultFO = this.result.CategoricalAttributesUniqueValues[fo]
  //   this.protectedResult = this.resultFO
  // }
  // optionClickFromFO() {
  //   this.fAValue = this.listShowlistForFO.values().next().value
  //   this.fAValue = this.selectedFO
  //   // console.log("fAValue=====",this.fAValue);
  //   this.protAttDrop = true
  //   // this.allSelectedFromPA = newStatus;
  //   this.getProtectedAttribute();
  //   // Get the DOM element by role
  //   const element = document.querySelector('[role="listbox"]');
  //   // Add a style to the div
  //   if (element instanceof HTMLElement) {
  //     element.style.display = 'none';
  //   }
  // }
  // getProtectedAttribute() {
  //   this.Protected = true;
  //   this.padata = true
  //   const resp = this.listShowlistForLabelDummy
  //   const fo = this.selectedLabel
  //   this.temp = this.result.AttributesInTheDataset.CategoricalAttributesList;
  //   this.ladata = fo
  //   this.temp.splice(this.temp.indexOf(fo), 1);
  //   this.labeltemp = fo
  //   this.pAResult = this.temp
  //   this.ldata = this.labelValue
  //   this.resultDummy = this.resultLabel
  // }
  // optionClickFromPA() {
  //   this.protAttResult = this.listShowlistForPA
  //   this.protectedAttValue = this.selectedProtAtt
  //   this.selectedPAArray.push(this.selectedProtAtt)
  //   this.priviDrop = true
  //   this.protAttrArray[this.i - 1] = this.protectedAttValue
  //   this.pa.push(this.protectedAttValue)
  //   const fo = this.selectedProtAtt
  //   this.palabeldata = fo
  //   this.protectedAttValue = ""
  //   this.temp = this.result.AttributesInTheDataset.CategoricalAttributesList;
  //   this.getPriviledged()
  // }

  // getPriviledged() {
  //   this.privDrop = true
  //   const fo = this.selectedProtAtt
  //   const temp = this.result.CategoricalAttributesUniqueValues[fo]
  //   this.temp.splice(this.temp.indexOf(fo), 1);
  //   this.priviRes = temp
  //   this.selectedProtAtt = ""
  // }
  // optionClickFromPriv() {
  //   this.pri = []
  //   this.privValue = this.selectedPriv
  //   this.selectedPrivArray.push(this.selectedPriv)
  //   this.privAttArray[this.i - 1] = this.privValue
  //   this.pri.push(this.privValue)
  //   this.priviRes = []
  //   this.nextprivButton = false
  //   this.nextprivButton1 = true
  //   this.finalSubmit = true
  //   this.selectedPriv = ""
  // }

  // -----------RESET FUNCTION-----------------
  // reset(){
  //   this.selectedDataFileId =
  //   this.fairSampleId =
  // }

  //--------------HANDLE FINAL SUBMIT----------------
  // onUpload() {
  //   console.log("selectedApplicableAttack::", this.selectedApplicableAttack)
  //   console.log("selectedApplicableMethod:", new Array(this.selectedApplicableMethod))
  //   const payload: Payload = {
  //     "userId": this.loggedin_userId,
  //     "modelId": this.selectedModelFileId,
  //     "dataId": this.selectedDataFileId,
  //     "tenetName": this.tenantarr,
  //   }
  //   if (payload.tenetName.includes('Security')) {
  //     payload.appAttacks = this.selectedApplicableAttack;
  //   }
  //   if (payload.tenetName.includes('Explainability')) {
  //     payload.appExplanationMethods = this.selectedApplicableMethod;
  //   }
  //   if (payload.tenetName.includes('Fairness')) {
  //     payload.biasType = this.selectedBiasTypeOption;
  //     payload.methodType = this.selectoption1;
  //     payload.taskType = this.selectedTaskTypeOption;
  //     payload.label = this.selectedLabel;
  //     payload.favorableOutcome = this.selectedFO;
  //     payload.protectedAttribute = JSON.stringify(this.protAttrArray)
  //     payload.privilegedGroup = JSON.stringify(this.privAttArray);

  //   }
  //   console.log("PAYLOADS::", payload)
  //   this.https.post(this.batchGeneration, payload).subscribe((res: any) => {
  //     const BatchResponse = res;
  //     BatchResponse.forEach((batch: any) => {
  //       if (batch.TenetId == 1.1) {
  //         this.https.post(this.ExplainReport, { "batchId": batch.BatchId }).subscribe((res1: any) => {
  //           this.getAllBatches();
  //         })
  //       } else if (batch.TenetId == 2.2) {
  //         this.https.post(this.fairnessReport, { "Batch_id": batch.BatchId }).subscribe((res1: any) => {
  //           this.getAllBatches();
  //         })
  //       }
  //     })
  //     this.cdr.detectChanges()
  //   }, error => {
  //     console.log(error)
  //     const message = error.error.detail
  //     const action = "Close"
  //     /**
  //     this._snackBar.open(message, action, {
  //       duration: 3000,
  //       horizontalPosition: 'center',
  //       panelClass: ['le-u-bg-black'],
  //     });
  //      */
  //   })
  //   this.modalService.dismissAll();

  // }

   // Opens the explanation visualization in a new tab
  visualization(){
    window.open(this.explanation_visualization, "_blank");
  }
  downloadReport(batch: any) {
    const id = batch.BatchId;
    //const form = new FormData();
    //form.append('batchId', id);
    const body = new URLSearchParams();
   
    if (batch.TenetId == 2.2) {
    const payload = {'Batch_id': id}
      this.https.post(this.FairnessWrapDownload, payload ,{ responseType: 'blob',observe: 'response' }).subscribe(
        (res: any) => {
          let filename = this.genFile();
      const contentDisposition = res.headers.get('Content-Disposition');
      if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
        filename = contentDisposition.split('filename=')[1].trim().replace(/"/g, '');
      }
      this.downloadFile(res.body, filename);
        }, error => {
          console.log(error)
          const message = error.error.detail
          const action = "Close"
        })
    } else {
      body.set('batchId', id.toString());
      this.https.post(this.ReportDownload, body, { responseType: 'blob', headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded') }).subscribe(
        (res: Blob) => {
          const filename = this.genFile();
          saveAs(res, filename);
        }, error => {
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          // this._snackBar.open(message, action, {
          //   duration: 3000,
          //   horizontalPosition: 'center',
          //   panelClass: ['le-u-bg-black'],
          // });
        })
    }
 
  }
    // Downloads a file with the given data and filename
  downloadFile(data: Blob, filename: string) {
    const blob = new Blob([data], { type: data.type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}
