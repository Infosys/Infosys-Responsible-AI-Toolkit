/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ViewEncapsulation } from '@angular/core';
import { PagingConfig } from '../_models/paging-config.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { AddDataModelComponent } from '../add-data-model/add-data-model.component';

@Component({
  selector: 'app-data-form',
  templateUrl: './data-form.component.html',
  styleUrls: ['./data-form.component.css'],
  encapsulation: ViewEncapsulation.None

})
export class DataFormComponent implements PagingConfig{
  // FOR SHIMMER EFFECT
  isLoadingTable = true;
  ///
  pagingConfig: PagingConfig = {} as PagingConfig;
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  tableSize: number[] = [5, 10, 15, 20];

  dataSource_getBatches: any;
  user:any;
  deleteData:any;
  updateData:any;
  getData:any;
  showSpinner1 = false;
  constructor(private dialog: MatDialog,private https: HttpClient,public _snackBar: MatSnackBar) {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
  }

    // Initializes the component and sets up API endpoints
  ngOnInit(): void {
    let ip_port: any
    // user call should happen here
    this.user = localStorage.getItem('userid')?JSON.parse(localStorage.getItem('userid')!) : '';
    // getting list of api from  local storage
    ip_port = this.getLocalStoreApi()

    // seting up api list
    this.setApilist(ip_port);
    this.getBatches();
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
  // used to set the api list urls
  setApilist(ip_port: any) {
    this.deleteData=ip_port.result.Workbench + ip_port.result.Workbench_DeleteData;
    this.updateData = ip_port.result.Workbench + ip_port.result.Workbench_UpdateData;
    this.getData = ip_port.result.Workbench + ip_port.result.Workbench_Data;
  }

  // Fetches batches of data from the server
  getBatches() {
    const formData =new FormData;
    formData.append("userId",this.user)
    this.https.post(this.getData , formData).subscribe(
      (res: any) => {
        this.dataSource_getBatches = res;
        this.onTableDataChange(this.currentPage);
        this.showSpinner1 = false;
        this.isLoadingTable = false;
      }, error => {
          console.log(error)
          this.showSpinner1 = false;
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"      
        }
    )
  }

  // Deletes a record after confirmation
  deleteConfirmationModel(dataId: any){
    const params = new URLSearchParams();
    params.set('userId', this.user);
    params.set('dataid',dataId.toString())
    const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/x-www-form-urlencoded',
      }),
      body: params,
    };
    this.showSpinner1 = true;
    this.https.delete(this.deleteData, options).subscribe(
      (res: any) => {
        this.getBatches();
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
          const message = 'The Api has failed';
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

  // Opens a modal on the right side of the screen
  openRightSideModal(val:any) {
    const dialogRef = this.dialog.open(AddDataModelComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: {
        dataValue: val ,
        user :this.user
          }
    });

    dialogRef.afterClosed().subscribe(() => {
      this.getBatches()
    });
  }
  // ----------------Pagination-----------------
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.dataSource_getBatches.length;
  }
}
