/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { RecognizersModalAComponent } from './recognizers-modal-a/recognizers-modal-a.component';
import { FormControl, FormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { methods } from './recognizers-method';
import { RecognizersService } from './recognizers.service';
import { NonceService } from 'src/app/nonce.service';
import { UserValidationService } from 'src/app/services/user-validation.service';

@Component({
  selector: 'app-recognizers',
  templateUrl: './recognizers.component.html',
  styleUrls: ['./recognizers.component.css'],
  // encapsulation: ViewEncapsulation.None
})
export class RecognizersComponent implements OnInit {

  constructor(public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog, private _fb: UntypedFormBuilder, public recognizerService: RecognizersService,public nonceService:NonceService,private validationService:UserValidationService) {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
  }
  listForm!: FormGroup;
  pagingConfig: PagingConfig = {} as PagingConfig;

  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;

  files: any[] = [];
  demoFile: any[] = [];
  selectedFile: File | any;
  file: File | any;

  selectedFileName: File | undefined;
  userId: any

  dataSource: any = []
  isSearchOpen: boolean = false;
  filteredDataSource:any;
  searchQuery: string = '';
  filteredItems: string[] = [];

  options = []
  recognizerTypeOptions = ["Data", "Pattern"]
  recognizerValueTypeOptions = ["Single Value", "Multiple Value"]

  tempValue: number = 0;

  recognizer_type = ""
  recognizer_Name = ""
  recognizerValue_type = "Single Value"
  recognizer_Value = ""
  supported_Entity = ""
  context_value = ""

  admin_list_rec = ""
  admin_list_rec_get_list = ""
  admin_list_rec_get_list_DataRecogGrpEntites = ""
  admin_list_rec_get_list_Delete_DataRecogGrp = ""
  admin_list_rec_get_list_Update_DataRecogGrpEntity = ""
  admin_list_rec_get_list_Update_DataRecogGrp = ""
  admin_list_rec_get_list_Update_AddnewlistItem = ""
  admin_list_rec_get_list_Delete_DataRecogGrpEntites = ""

  selectedTab = 0;
  recoGnizers = true;
  accountMaping = false;

  toggleTab(){
    this.recoGnizers = !this.recoGnizers;
    this.accountMaping = !this.accountMaping;
  }

  // Sets the selected recognizer type
  selectRecognizerType(e: any) {
    //console.log("Selected option ID:", e.value);
    this.recognizer_type = e.value
  }

  // Sets the selected recognizer value type
  selectRecognizerValueType(e: any) {
    //console.log("Selected option ID:", e.value);
    this.recognizerValue_type = e.value
  }

  // Initializes the component and loads data
  ngOnInit(): void {

    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    this.getRecognizerList()
    this.fromCreation()
  }

  // Retrieves the logged-in user from local storage
  getLogedInUser() {
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.userId = x ;
        console.log(" userId", this.userId)
      }
      return this.userId;
    }
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if(res != null){
        return ip_port = JSON.parse(res)
      }
    }
  }

  // Sets the API list URLs
  setApilist(ip_port: any) {
  
    this.admin_list_rec = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrp   //+ environment.admin_list_rec
    this.admin_list_rec_get_list = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrplist // environment.admin_list_rec_get_list
    this.admin_list_rec_get_list_DataRecogGrpEntites = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrpEntites   //environment.admin_list_rec_get_list_DataRecogGrpEntites
    this.admin_list_rec_get_list_Delete_DataRecogGrp = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrpDelete  //environment.admin_list_rec_get_list_Delete_DataRecogGrp
    this.admin_list_rec_get_list_Update_DataRecogGrpEntity = ip_port.result.Admin + ip_port.result.Admin_DataEntitesUpdate  //environment.admin_list_rec_get_list_Update_DataRecogGrpEntity
    this.admin_list_rec_get_list_Update_DataRecogGrp = ip_port.result.Admin + ip_port.result.Admin_DataGrpUpdate    //environment.admin_list_rec_get_list_Update_DataRecogGrp
    this.admin_list_rec_get_list_Update_AddnewlistItem = ip_port.result.Admin + ip_port.result.Admin_DataEntityAdd  //environment.admin_list_rec_get_list_Update_AddnewlistItem
    this.admin_list_rec_get_list_Delete_DataRecogGrpEntites = ip_port.result.Admin + ip_port.result.Admin_DataRecogEntityDelete    //environment.admin_list_rec_get_list_Delete_DataRecogGrpEntites
  }

  // Fetches the list of recognizers
  getRecognizerList() {
    this.https.get(this.admin_list_rec_get_list).subscribe
      ((res: any) => {
        this.dataSource = []

        res.RecogList.forEach((i: any) => {
          //console.log(i.isPreDefined + "i print")
          if (i.isPreDefined == "No") {
            this.dataSource.push(i)
          }
          this.filteredDataSource = this.dataSource;
        });


        // this.pagingConfig.totalItems = this.dataSource.length
        this.onTableDataChange(this.currentPage)
      }, error => {
        // You can access status:
        //console.log(error.status);


        // //console.log(error.error.detail)
        //console.log(error)
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });


      })
  }

  // Handles table pagination
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.filteredDataSource.length;

  }
  // Handles table size changes
  onTableSizeChange(event: any): void {
    this.pagingConfig.itemsPerPage = event.result.value;
    this.pagingConfig.currentPage = 1;
    this.pagingConfig.totalItems = this.filteredDataSource.length;
  }

  // Opens the right-side modal for recognizers
  openRightSideModal(value: any) {
    const dialogRef = this.dialog.open(RecognizersModalAComponent, {
      data: {
        id: value,
        api: this.admin_list_rec_get_list_DataRecogGrpEntites,
        api2: this.admin_list_rec_get_list_Delete_DataRecogGrpEntites,
        api3:this.admin_list_rec_get_list_Update_DataRecogGrpEntity,
        api4:this.admin_list_rec_get_list_Update_AddnewlistItem
      },


      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getRecognizerList()
      //console.log("CLOSED")
    });
  }

  @ViewChild('fileInput') fileInput!: ElementRef;

  // Opens the file input dialog
  openFileInput() {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: any) {
    //console.log(event)
  }
  fileName!: string;

// Handles file browsing and validates file type
  fileBrowseHandler(imgFile: any) {
    const allowedTypes = ['text/plain'];
    console.log("fileBrowseHandler", imgFile.target.files[0].type)
    if (!allowedTypes.includes(imgFile.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      }); 
      // return;
    }else{
    //console.log(imgFile)
    this.files = [];
    this.demoFile = [];
    this.prepareFilesList(imgFile.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
    // //console.log("file name",this.selectedFile.fileName)

    // 
    const target = imgFile.target as HTMLInputElement;
    const filez: File = (target.files as FileList)[0];
    this.fileName = filez.name;
    //console.log("file name", this.fileName)
  }
}

// Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    for (const item of files) {
      // item.progress = 0;
      this.files.push(item);
    }
  }

   // Creates the form for recognizers
  fromCreation() {
    this.listForm = this._fb.group({
      recognizer_type: ['DATA', Validators.required],
      recognizer_Name: ['',
        [
          Validators.required,
          Validators.pattern('^[a-zA-Z0-9]*$'),
          Validators.minLength(1),
          Validators.maxLength(50),
        ],],  
     // recognizerValue_type: ['', Validators.required],
      recognizer_Value: ['', Validators.required],
      supported_Entity: ['',
        [
          Validators.required,
          Validators.pattern('^[a-zA-Z0-9]*$'),
          Validators.minLength(1),
          Validators.maxLength(50),
        ],],
      tempValue: [0, Validators.required]
    });
  }

  // Getter for recognizer name form control
  get recognizerName() {
    return this.listForm.get('recognizer_Name');
  }
  get supportedEntity() {
    return this.listForm.get('supported_Entity');
  }

   // Handles the Apply button click
  onClickApply() {
    //console.log("Apply")
    //console.log(this.listForm.value)
    // //console.log(this.tempValue)

    if (this.listForm.valid) {
      console.log('Form Submitted', this.listForm.value);
      this.payloadonSubmit();
    } else {
      console.log('Form is invalid');
    }  
    }

  // Prepares the payload and submits the recognizer data
  payloadonSubmit(): void {
    let score = this.listForm.value.tempValue / 10
    //console.log("score", score)
    const fileData = new FormData();
    this.selectedFile = this.demoFile[0];
    fileData.append('name', this.listForm.value.recognizer_Name);
    fileData.append('rtype', this.listForm.value.recognizer_type);
    fileData.append('ptrn', this.listForm.value.recognizer_Value);
    fileData.append('entity', this.listForm.value.supported_Entity);
    fileData.append('score', score.toString());
    fileData.append('context', this.listForm.value.context_value);
    if (this.selectedFile) {
      fileData.append('filecpy', this.selectedFile);
    }


    this.postDataRecogGroupApi(fileData)
  }

  // Sends the recognizer data to the server
  postDataRecogGroupApi(fileData: FormData) {
    this.https.post(this.admin_list_rec, fileData).subscribe
      ((res: any) => {
        //console.log("res", res)
        this.getRecognizerList()
        const message = "The Api has been successfully called"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });

      })
      , (error: { status: any; }) => {
        // You can access status:
        //console.log(error.status);
      }

  }

// Deletes a recognizer by ID
  clickDeleteRecognizer(id: any, preDefined: any) {
    // //console.log("Delete clicked")
    // const formattedDate = methods.hi();
    // //console.log("on click delete",formattedDate);


    if (preDefined == 'Yes') {
      const message = "You Can't delete a Pre-Defined List"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 1000,
        panelClass: ['le-u-bg-black'],
      });
    }
    else if (preDefined = "No") {



      const options = {
        headers: new HttpHeaders({
          'Content-Type': 'application/json',
        }),
        body: {
          RecogId: id
        },
      };
      // const methodsInstance = new methods(this.http, this._snackBar, this.recognizerService);
      // this.dataSource = methodsInstance.delete(this.admin_list_rec_get_list_Delete_DataRecogGrp, options,this.admin_list_rec_get_list);
      // this.https.delete(this.admin_pattern_rec_delete_list, { headers }).subscribe
      this.https.delete(this.admin_list_rec_get_list_Delete_DataRecogGrp, options).subscribe
        ((res: any) => {
          //console.log("delete Resonce" + res.status)
          if (res.status === "True") {


            this.getRecognizerList()

            // this.https.get(this.admin_list_rec_get_list).subscribe
            //   ((res: any) => {
            //     this.dataSource = []
            //     // this.showSpinner1=false;

            //     // //console.log("data sent to database" + res.PtrnList)
            //     // this.dataSource = res.RecogList
            //     res.RecogList.forEach((i: any) => {
            //       //console.log(i.isPreDefined + "i print")
            //       if (i.isPreDefined == "No") {
            //         this.dataSource.push(i)
            //       }

            //     });

            //   })

            //

            const message = "Data Group Deleted Successfully"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });
          } else if (res.status === "False") {
            const message = "Data Group Deletion was unsucessful"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });

          }



        }, error => {
          // You can access status:
          //console.log(error.status);
          if (error.status == 430) {
            //console.log(error.error.detail)
            //console.log(error)
            const message = error.error.detail
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
          } else {

            // //console.log(error.error.detail)
            //console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });

          }
        })

    }
  }

  clickgetRecognizers() {
    const methodsInstance = new methods(this.https, this._snackBar, this.recognizerService);
    // this.dataSource = methodsInstance.getRecognizers(this.admin_list_rec_get_list);
    // methodsInstance.getDataSource(this.admin_list_rec_get_list).then((res: any) => {//console.log("getRecognizers functionzzz",res)});
    //console.log("getRecognizers function", this.dataSource);
  }

  // clickDeleteRecognizerx(id: any, preDefined: any) {
  //   // Call the delete function from the method class here
  //   let a,b,c
  //   const methodsInstance = new methods(this.https, this._snackBar, this.recognizerService);
  //   methodsInstance.delete(a,b,c);
  // }

  editIndex: number[] = [];

  edit(i: any) {
    this.editIndex.push(i);

  }

  // Updates a recognizer with new data
  update(i: any,RecogId: any,RecogName:any,supported_entity:any,RecogType: any) {
    this.editIndex = this.editIndex.filter(index => index !== i);
    let payload ={
      RecogId:RecogId,
      RecogName:RecogName,
      supported_entity:supported_entity,
      RecogType:RecogType
    }
    this.updateRecognizer(payload)
  }
  // Sends the updated recognizer data to the server
  updateRecognizer(payload:any){
    this.https.patch(this.admin_list_rec_get_list_Update_DataRecogGrp, payload).subscribe 
    ((res: any) => 
      {
        //console.log("res",res)
        this.getRecognizerList()
        const message = "Data Group Updated Successfully"
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      })
  }

  // Filters the recognizer list based on the search query
  search() {
    if (this.searchQuery) {
      this.filteredDataSource = this.dataSource.filter((item :any) =>
        item.RecogName.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
  
      this.currentPage = 1;
      this.pagingConfig.currentPage = 1;
      this.pagingConfig.totalItems = this.filteredDataSource.length;
    } else {
      this.filteredDataSource = this.dataSource;
      this.currentPage = 1;
      this.pagingConfig.currentPage = 1;
      this.pagingConfig.totalItems = this.filteredDataSource.length;
  
    }
  }
  
  // Toggles the search bar visibility
  toggleSearch() {
  this.isSearchOpen = !this.isSearchOpen;
  this.searchQuery = '';
  this.filteredItems = [];
  }
  
  // Closes the search bar and resets the recognizer list
  closeSearch() {
    this.isSearchOpen = false;
    this.searchQuery = '';
    this.filteredDataSource = this.dataSource;
    this.currentPage = 1;
    this.pagingConfig.currentPage = 1;
    this.pagingConfig.totalItems = this.filteredDataSource.length;
  }

}
