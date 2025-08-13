/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-accounts-configuration-modal-create-pm',
  templateUrl: './accounts-configuration-modal-create-pm.component.html',
  styleUrls: ['./accounts-configuration-modal-create-pm.component.css']
})
export class AccountsConfigurationModalCreatePmComponent{
  constructor(public dialogRef: MatDialogRef<AccountsConfigurationModalCreatePmComponent>,  public _snackBar: MatSnackBar, public https: HttpClient
    , @Inject(MAT_DIALOG_DATA) public data: { x: any }) { 
      // this.pagingConfig = {
      //   itemsPerPage: this.itemsPerPage,
      //   currentPage: this.currentPage,
      //   totalItems: this.totalItems
      // }
    }

    

    // pagingConfig: PagingConfig = {} as PagingConfig;
    // currentPage: number = 1;
    // itemsPerPage: number = 5;
    // totalItems: number = 0


  dataSource1: any = []
  closeDialog() {
    this.dialogRef.close();
  }

   ngOnInit(): void {

    console.log("data", this.data.x.portfolio)
    console.log("datax", this.data.x['portfolio'])
   }

   tab="acc"

  toggleTabs(tab: string){
    this.tab=tab;
  }
   

  

}
