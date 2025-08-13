/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ViewChild } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { NgbPopover, NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { AccountsConfigurationModalPrivacyComponent } from './accounts-configuration-modal-privacy/accounts-configuration-modal-privacy.component';
import { AccountsConfigurationModalSafetyComponent } from './accounts-configuration-modal-safety/accounts-configuration-modal-safety.component';
import { AccountsConfigurationModalFmComponent } from './accounts-configuration-modal-fm/accounts-configuration-modal-fm.component';
import { AccountsConfigurationModalCreatePmComponent } from './accounts-configuration-modal-create-pm/accounts-configuration-modal-create-pm.component';
import { AccountsConfigurationModalCreateTemplateUpdateComponent } from './admin-template-update/admin-template-update';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-accounts-configuration',
  templateUrl: './accounts-configuration.component.html',
  styleUrls: ['./accounts-configuration.component.css']
})
export class AccountsConfigurationComponent {
  accountDetail: any;
  listReconList: any=[];
  csrfToken: string;
  constructor (public _snackBar: MatSnackBar, private https: HttpClient, public dialog: MatDialog,public nonceService:NonceService)
  {
    this.csrfToken = this.nonceService.getNonce();

    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
    this.AccountFormCall();
    this.CreateNewAccPortForm();
  }

  
  pagingConfig: PagingConfig = {} as PagingConfig;
  
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;

  Portfolio_options=[]
  Account_options=[]

  portfolioSelected=false
  Accountselected=false


  userId =""
  tab="Privacy"
  dataSource: any = []

  isSearchOpen: boolean = false;
  filteredDataSource:any;
  searchQuery: string = '';
  filteredItems: string[] = [];
  

    admin_list_getAccountDetails = ""
    admin_list_AccountMaping_AccMasterList = ""
    admin_pattern_rec_get_list = ""
    admin_list_rec_get_list = "" 
    admin_list_AccountMaping_AccMasterentry = "" 
    admin_list_rec_get_list_DataRecogGrpEntites = "" 
    admin_list_AccountMaping_AccMasterList_dataList = "" 
    admin_list_AccountMaping_AccMasterList_Delete = "" 
    admin_list_AccountMaping_AccMasterList_Delete_Data = "" 
    admin_list_AccountMaping_AccMasterList_Update_Data = "" 
    admin_list_AccountMaping_Acc_PrivacyEncrypt = "" 
    admin_list_AccountMaping_Acc_ThresholdUpdate = "" 
    Admin_SetPrivacyParameter = "" 
    Admin_SafetyUpdate = ""
    Admin_AccSafetyListAccountWise=""  
    fm_config_dataList = "" 
    
    fm_config_entry = "" 
    fm_config_entryList= "" 
    
    fm_config_dataUpdate ="" 
    fm_config_delete = ""
    fm_config_modCheck = ""
    fm_config_topicList = ""
    fm_config_outputModCheck = ""

    toggleTabs(tab: string){
    this.tab=tab;
  }

 // Submits the account form data
  submit() {
    console.log(this.AccountForm.value);
    const header = {
      portfolio: this.AccountForm.value.portfolio,
      account: this.AccountForm.value.account,
      // ptrnList: ptrnlist,
      dataGrpList: this.selectedReclist,
      
    }
    this.setPrivacyParameter(header)
  }

    // Sends privacy parameters to the server
  setPrivacyParameter(header: any) {
    this.https.post(this.Admin_SetPrivacyParameter, header).subscribe
        ((res: any) => {
          console.log("data sent to database" + res.status)
          if (res.status === "True") {
        
            const message = "Recognizer Added Successfully"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass: ['le-u-bg-black'],
            });
            this.getAccountMasterEntryList()
            // this.getAllAccountData();
          } else if (res.status === "False") {
            const message = "Parameters have already been Mapped to this Account "
            const action = "Close"
            this.getAccountMasterEntryList()
            this._snackBar.open(message, action, {
              duration: 3000,
              panelClass: ['le-u-bg-black'],
            });
          }
          // this.AccountForm.reset(this.initialValues);
          this.getAccountMasterEntryList()

        }, error => {
          // You can access status:
          console.log(error.status);
            // console.log(error.error.detail)
            console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            this.getAccountMasterEntryList()
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black']
            });
        })
  }

 // Initializes the component and sets up API lists
  ngOnInit(): void {
    let ip_port: any

    let user = this.getLogedInUser()

    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    this.getAccountMasterEntryList()
    this.getAllAccountData()
    this.getadmin_list_rec_get_list()
    console.log("oninit");
  }

  // Retrieves the logged-in user from local storage
  getLogedInUser() {
    if (localStorage.getItem("userid") != null) {
      const x = localStorage.getItem("userid")
      if (x != null) {

        this.userId = JSON.parse(x)
        console.log(" userId", this.userId)
        return JSON.parse(x)
      }

      console.log("userId", this.userId)
    }
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

  // Sets the API list URLs
  setApilist(ip_port: any) {

    this.admin_list_getAccountDetails = ip_port.result.Admin + ip_port.result.getAccountDetail;
    this.admin_list_AccountMaping_AccMasterList = ip_port.result.Admin + ip_port.result.Admin_AccMasterList     // + environment.admin_list_AccountMaping_AccMasterList
    this.admin_pattern_rec_get_list = ip_port.result.Admin + ip_port.result.Admin_ptrnRecogniselist       //+ environment.admin_pattern_rec_get_list
    this.admin_list_rec_get_list = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrplist       //+ environment.admin_list_rec_get_list
    this.admin_list_AccountMaping_AccMasterentry = ip_port.result.Admin + ip_port.result.Admin_AccMasterEntry     // + environment.admin_list_AccountMaping_AccMasterentry
    this.admin_list_rec_get_list_DataRecogGrpEntites = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrpEntites      //+ environment.admin_list_rec_get_list_DataRecogGrpEntites
    this.admin_list_AccountMaping_AccMasterList_dataList = ip_port.result.Admin + ip_port.result.Admin_AccDataList      //+ environment.admin_list_AccountMaping_AccMasterList_dataList
    this.admin_list_AccountMaping_AccMasterList_Delete = ip_port.result.Admin + ip_port.result.Admin_AccMasterDelete     // + environment.admin_list_AccountMaping_AccMasterList_Delete
    this.admin_list_AccountMaping_AccMasterList_Delete_Data = ip_port.result.Admin + ip_port.result.Admin_AccDataDelete      //+ environment.admin_list_AccountMaping_AccMasterList_Delete_Data
    this.admin_list_AccountMaping_AccMasterList_Update_Data = ip_port.result.Admin + ip_port.result.Admin_AccEntityAdd      //+ environment.admin_list_AccountMaping_AccMasterList_Update_Data
    this.admin_list_AccountMaping_Acc_PrivacyEncrypt = ip_port.result.Admin + ip_port.result.Admin_PrivacyEncrypt     // + environment.admin_list_AccountMaping_Acc_PrivacyEncrypt
    this.admin_list_AccountMaping_Acc_ThresholdUpdate = ip_port.result.Admin + ip_port.result.Admin_ThresholdUpdate     // + environment.admin_list_AccountMaping_Acc_ThresholdUpdate
    this.Admin_AccSafetyListAccountWise = ip_port.result.Admin + ip_port.result.Admin_AccSafetyListAccountWise  
    this.Admin_SetPrivacyParameter = ip_port.result.Admin + ip_port.result.setPrivacyParameter    // setPriavy Parmenetre
    this.Admin_SafetyUpdate = ip_port.result.Admin + ip_port.result.Admin_SafetyUpdate 
    this.fm_config_dataList = ip_port.result.Admin + ip_port.result.Fm_Config_Data   
    this.admin_list_rec_get_list = ip_port.result.Admin + ip_port.result.Admin_DataRecogGrplist; 
    this.fm_config_entry = ip_port.result.Admin + ip_port.result.Fm_Config_Entry;
    this.fm_config_entryList= ip_port.result.Admin + ip_port.result.Fm_Config_EntryList
    this.fm_config_dataList = ip_port.result.Admin + ip_port.result.Fm_Config_Data
    this.fm_config_dataUpdate = ip_port.result.Admin + ip_port.result.Fm_Config_DataUpdate
    this.fm_config_delete = ip_port.result.Admin + ip_port.result.Fm_Config_Delete
    this.fm_config_modCheck = ip_port.result.Admin + ip_port.result.Fm_Config_ModCheck
   this.fm_config_topicList = ip_port.result.Admin + ip_port.result.Fm_Config_TopicList
   this.fm_config_outputModCheck = ip_port.result.Admin + ip_port.result.Fm_Config_OutputModCheck
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

   // Fetches account master entry list
  getAccountMasterEntryList(){
    console.log("getAccountMasterEntryList")
    this.https.get(this.admin_list_AccountMaping_AccMasterList).subscribe
      ((res: any) => {

        this.dataSource = res.accList
        this.filteredDataSource = this.dataSource;
        console.log("res", this.dataSource)
        this.pagingConfig.totalItems = this.dataSource.length;


      }
      , error => {
        // You can access status:
        console.log(error.status);
          // this.showSpinner1 = false;
          // this.edited = false;
          // console.log(error.error.detail)
          console.log(error)
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"
          // this._snackBar.open(message, action, {
          //   duration: 3000,
          //   horizontalPosition: 'left',
          //   panelClass: ['le-u-bg-black'],
          // });

        
      })
  }

  // portfolioSet: Set<any> = new Set();
  portfolioArr :any =[]
// Fetches all account data
  getAllAccountData(){
    this.https.get( this.admin_list_getAccountDetails).subscribe
        ((res: any) => {
          console.log("res=========>>>",res[0].AccountDetails)
          
          this.accountDetail=res[0].AccountDetails
          for(let i=0;i<res[0].AccountDetails.length;i++){
            console.log("portfolio",res)
            const portfolio = res[0].AccountDetails[i].portfolio
            console.log("portfolio11111",portfolio)
            // this.portfolioSet.add(portfolio)
            // this.accountArr.push(res[0].AccountDetails[i].account)
            this.portfolioArr.push(portfolio)
          }
          // Sort portfolioArr alphabetically and store it in Portfolio_options
          this.Portfolio_options = this.portfolioArr.sort((a: string, b: string) => a.localeCompare(b));
          console.log("portfolio",this.portfolioArr)
          // this.dataSource = res.fmList;
          
          
  
        }, error => {
          // You can access status:
          console.log(error.status);
            // console.log(error.error.detail)
            console.log(error)
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 3000,
              horizontalPosition: 'left',
              panelClass: ['le-u-bg-black'],
            });
  
          
        })
   }

   // Opens the privacy modal
  openRightSideModal1(a:any,b:any){
    const dialogRef = this.dialog.open(AccountsConfigurationModalPrivacyComponent, {
      data: {
        id: a,
        ThresholdScore: b,
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
      this.getAccountMasterEntryList()
      console.log("CLOSED")
    });
  }

  // Opens the safety modal
  openRightSideModal2(a:any){
    const dialogRef = this.dialog.open(AccountsConfigurationModalSafetyComponent, {
      data: {
        id: a,
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
      this.getAccountMasterEntryList()
      console.log("CLOSED")
    });
  }

  // Opens the FM configuration modal
  openRightSideModal3(a:any){
    const dialogRef = this.dialog.open(AccountsConfigurationModalFmComponent, {
      data: {
        id: a,
       
      },


      width: '77vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getAccountMasterEntryList()
      console.log("CLOSED")
    });
  } 

  // Opens the template update modal
  openRightSideModal5(a:any,account:any,portfolio:any){
    const dialogRef = this.dialog.open(AccountsConfigurationModalCreateTemplateUpdateComponent, {
      data: {
        id: a,
        account : account,
        portfolio: portfolio,
       
      },


      width: '77vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getAccountMasterEntryList()
      console.log("CLOSED")
    });
  } 

  // Opens the create PM modal
  openRightSideModal4(a:any){
    console.log("acccount from value",a)
    const dialogRef = this.dialog.open(AccountsConfigurationModalCreatePmComponent, {
      data: {
        x: a,
       
      },


      width: '77vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getAccountMasterEntryList()
      console.log("CLOSED")
    });
  } 

  // end of modal open call 


  AccountForm!: FormGroup;
  NewAccPort!: FormGroup;
   // Initializes the account form
  AccountFormCall(){

  this.AccountForm = new FormGroup({
    portfolio: new FormControl('Portfolio Name', [Validators.required]),
    account: new FormControl('Account Name', [Validators.required]),
    // patternRecognizerNames: new FormControl('', [Validators.required]),
    // listRecognizerNames: new FormControl('', [Validators.required]),
    // drawingsThreshold: new FormControl(0.5, [Validators.required]),
    // hentaiThreshold: new FormControl(0.25, [Validators.required]),
    // neutralThreshold: new FormControl(0.5, [Validators.required]),
    // pornThreshold: new FormControl(0.25, [Validators.required]),
    // sexyThreshold: new FormControl(0.25, [Validators.required]),
  });

}

// Initializes the new account/portfolio form
  CreateNewAccPortForm(){

  this.NewAccPort = new FormGroup({
    portfolio: new FormControl('', [Validators.required,Validators.minLength(3)]),
    account: new FormControl('', [Validators.required]),
  });

}
callCount: number = 0; 
 // Handles account dropdown selection
accountDropDown(){
  this.callCount++
  this.portfolioSelected=true
  const portfolio = this.AccountForm.controls['portfolio'].value
  console.log("inside accountDrop===",portfolio)
  const accountArr: any = [];
  for(let i=0;i<this.accountDetail.length;i++){
    if(this.accountDetail[i].portfolio == portfolio){
      accountArr.push(this.accountDetail[i].account )
    }
  }
  this.Account_options = accountArr
  if (this.callCount > 1) {
    this.AccountForm.get('account')?.setValue(this.Account_options[0]);
    // this.AccountForm.get('account')?.reset();
    this.Accountselected = true
  }

  this.isSearchOpen = true;
  this.searchQuery = this.AccountForm.controls['portfolio'].value;

  this.search();

}

 // Activates subcommands for account and portfolio
activateSubcommands(){

  this.Accountselected = true
  if(this.AccountForm.valid){
    this.openRightSideModal4(this.AccountForm.value)
  }else{
    this._snackBar.open("Please select an Account and Portfolio", "Close", {
      duration: 3000,
      horizontalPosition: 'left',
      panelClass: ['le-u-bg-black'],
    });
  }
}

save(){

}
@ViewChild('p') p!: NgbPopover;
test(p:any){
  if (this.p.isOpen()) {
    console.log('Popover is open');
    this.p.toggle();
  } else {
    this.p.toggle();
    console.log('Popover is closed');
  }

  
}

// Creates a new account/portfolio
createNewAccPot() {
  if (this.NewAccPort.valid) {
    const formData = this.NewAccPort.value;
    this.https.post(this.admin_list_AccountMaping_AccMasterentry, formData).subscribe(
      (response: any) => {
        // Handle success response
        console.log(response);
        this.getAllAccountData()
      },
      (error: any) => {
        // Handle error response
        console.error(error);
      }
    );
  }
}

// Fetches the list of recognizers
getadmin_list_rec_get_list(){
  this.https.get(this.admin_list_rec_get_list).subscribe
  ((res: any) => {
    console.log("res",res)
    this.listReconList = res.RecogList
  }, error => {
    // You can access status:
    console.log(error.status);
      // console.log(error.error.detail)
      console.log(error)
      const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
      const action = "Close"
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });

    
  })
}

@ViewChild('select1') select1!: MatSelect;

// SCREEN TWO ADD DATA  
//--------------VARIABLES-----------SECURITY

selectedReclist: any = [];
allSelected1: any;
listShowlist1 = new Set();
allSelectedInput = false;
event1: any;
c1: boolean = false;

// select 1- Toggles all selections for the dropdown
toggleAllSelection1(event: any) {
  this.event1 = event;
  this.c1 = event.checked;
  this.allSelected1 = !this.allSelected1;
  if (this.allSelected1) {
    this.select1.options.forEach((item: MatOption) => {
      item.select();
      this.listShowlist1.add(item.value);
      const element = document.querySelector('[role="listbox"]');
      if (element instanceof HTMLElement) {
        element.style.display = 'none';
      }
      this.select1.close();
    });
  } else {
    this.select1.options.forEach((item: MatOption) => {
      item.deselect();

      this.listShowlist1.delete(item.value);
    });
  }
}

// Updates the status of the first select element based on selected options.
selectRecognizertype() {
  let newStatus = true;
  this.select1.options.forEach((item: MatOption) => {
    if (!item.selected) {
      newStatus = false;
      this.allSelected1 = false;
      this.listShowlist1.delete(item.value);
    } else {
      this.listShowlist1.add(item.value);
    }
  });
  this.allSelectedInput = newStatus;
}
 
// Deletes an account group by sending a DELETE request.
deleteAccounttGroup(id: any) {
  const options = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
    }),
    body: {
      accMasterId: id
    },
  };
  this.https.delete(this.admin_list_AccountMaping_AccMasterList_Delete, options).subscribe
    ((res: any) => {
      if (res.status === "True") {

        const message = "Account Deleted Successfully"
        const action = "Close"
        this.getAccountMasterEntryList();
        this._snackBar.open(message, action, {
          duration: 1000,
          panelClass: ['le-u-bg-black'],
        });
      } else if (res.status === "False") {
        const message = "Account Deletion was unsucessful"
        this.getAccountMasterEntryList()
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 1000,
          panelClass: ['le-u-bg-black'],
        });

      }

      this.getAccountMasterEntryList()

    }, error => {
      // You can access status:
      console.log(error.status);
      if (error.status == 430) {
        console.log(error.error.detail)
        console.log(error)
        const message = error.error.detail
        this.getAccountMasterEntryList()
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      } else {
        // console.log(error.error.detail)
        console.log(error)
        const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
        this.getAccountMasterEntryList()
        const action = "Close"
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });

      }
    })
}

search() {
  if (this.searchQuery) {
    this.filteredDataSource = this.dataSource.filter((item :any) =>
      item.portfolio.toLowerCase().includes(this.searchQuery.toLowerCase())
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



toggleSearch() {
this.isSearchOpen = !this.isSearchOpen;
this.searchQuery = '';
this.filteredItems = [];
}




closeSearch() {
  this.isSearchOpen = false;
  this.searchQuery = '';
  this.filteredDataSource = this.dataSource;
  this.currentPage = 1;
  this.pagingConfig.currentPage = 1;
  this.pagingConfig.totalItems = this.filteredDataSource.length;
}
}
