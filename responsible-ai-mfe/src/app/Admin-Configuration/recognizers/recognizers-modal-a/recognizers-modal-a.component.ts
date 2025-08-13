/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { NonceService } from 'src/app/nonce.service';

@Component({
  selector: 'app-recognizers-modal-a',
  templateUrl: './recognizers-modal-a.component.html',
  styleUrls: ['./recognizers-modal-a.component.css'],
})
export class RecognizersModalAComponent {
  recognizerForm: FormGroup;
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<RecognizersModalAComponent>,
    public _snackBar: MatSnackBar,
    public https: HttpClient,public nonceService:NonceService,
    @Inject(MAT_DIALOG_DATA) public data: { id: any; api: any; api2: any; api3: any ; api4: any}
  ) {
    this.recognizerForm = this.fb.group({
      recognizerItems: this.fb.array([this.createRecognizerItem()])
    });

    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems,
    };
  }

  editIndex: number[] = [];

  pagingConfig: PagingConfig = {} as PagingConfig;
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;

  dataSource1: any = [];
  closeDialog() {
    this.dialogRef.close();
  }

  // Initializes the component and fetches the item list
  ngOnInit(): void {
    //console.log('this data is from parrent', this.data.id);
    this.getItemList(this.data.id, this.data.api);
  }

  isDataEmpty: boolean = false;
   // Fetches the list of items from the server
  getItemList(RecogGrpIdgg: any, api: any) {
    // this.copydataRecogGrpId = ""
    // this.copydataRecogGrpId = RecogGrpIdgg
    this.https.post(api, { RecogId: RecogGrpIdgg }).subscribe(
      (res: any) => {
        //console.log(res.DataEntities);
        this.dataSource1 = res.DataEntities;

        if (this.dataSource1.length === 0) {
          this.isDataEmpty = true;
          this._snackBar.open('Value is not set. Create a valid Reconizer.', 'Close', {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          this.isDataEmpty = false;
          this.onTableDataChange(this.currentPage);
        }
      },
      (error) => {
        // You can access status:
        //console.log(error.status);
        // //console.log(error.error.detail)
        //console.log(error);
        const message =
          (error.error && (error.error.detail || error.error.message)) ||
          'The Api has failed';
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

   // Deletes an item from the list
  deleteListEntity(id: any) {
    const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      }),
      body: {
        EntityId: id,
      },
    };
    // this.https.delete(this.admin_pattern_rec_delete_list, { headers }).subscribe
    this.https.delete(this.data.api2, options).subscribe(
      (res: any) => {
        //console.log('delete Resonce' + res.status);
        if (res.status === 'True') {
          const message = ' Item Deleted Successfully';
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 1000,
            panelClass: ['le-u-bg-black'],
          });
        } else if (res.status === 'False') {
          const message = 'Item Deletion was unsucessful';
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 1000,
            panelClass: ['le-u-bg-black'],
          });
        }

        this.getItemList(this.data.id, this.data.api);
      },
      (error) => {
        // You can access status:
        //console.log(error.status);
        if (error.status == 430) {
          //console.log(error.error.detail);
          //console.log(error);
          const message = error.error.detail;
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          // //console.log(error.error.detail)
          //console.log(error);
          const message =
            (error.error && (error.error.detail || error.error.message)) ||
            'The Api has failed';
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

  // Handles table pagination
  onTableDataChange(event: any) {
    this.currentPage = event;
    this.pagingConfig.currentPage = event;
    this.pagingConfig.totalItems = this.dataSource1.length;
  }
  // Updates an item in the list
  update(i: number, element: any) {
    this.editIndex = this.editIndex.filter(index => index !== i);
    const payload = {
      RecogId : this.data.id,
      EntityId: element.EntityId,
      EntityName: element.EntityName,
      // Add other fields as necessary
    };
    this.updateRecognizer(payload);
  }

  edit(i: number) {
    this.editIndex.push(i);
  }

  // Sends the updated recognizer data to the server
  updateRecognizer(payload: any) {
    // const url = 'https://rai-toolkit-rai.az.ad.idemo-ppc.com/api/v1/rai/admin/DataEntitesUpdate';
    const url = this.data.api3;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
  
    this.https.patch(url, payload, { headers }).subscribe(
      (res: any) => {
        //console.log("res", res);
        // this.getItemList(this.data.id, this.data.api);
        const message = "Data Group Updated Successfully";
        const action = "Close";
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      },
      (error) => {
        //console.log(error.status);
        //console.log(error);
        const message = (error.error && (error.error.detail || error.error.message)) || 'The Api has failed';
        const action = 'Close';
        this._snackBar.open(message, action, {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      }
    );
  }

  get recognizerItems(): FormArray {
    return this.recognizerForm.get('recognizerItems') as FormArray;
  }

  // Creates a new recognizer item form group
  createRecognizerItem(): FormGroup {
    return this.fb.group({
      newRecognizerItem: ['', Validators.required]
    });
  }

  addRecognizerItem(): void {
    this.recognizerItems.push(this.createRecognizerItem());
  }

  removeRecognizerItem(index: number): void {
    this.recognizerItems.removeAt(index);
  }

  // Handles form submission and adds new recognizer items
  onSubmit(): void {
    if (this.recognizerForm.valid) {
      const recognizerItemsArray = this.recognizerForm.value.recognizerItems.map((item: any) => item.newRecognizerItem);
      //console.log('Recognizer Items:', recognizerItemsArray);
      this.addItemList(recognizerItemsArray);
      // Handle the submission logic here
    }
    // call additemlistfunction 
  }

  // Sends the new recognizer items to the server
  addItemList(entityNames: string[]): void {
    const url = this.data.api4;
    const headers = new HttpHeaders({
      'accept': 'application/json',
      'Content-Type': 'application/json'
    });
    const body = {
      EntityNames: entityNames,
      RecogId: this.data.id
    };
  
    this.https.patch(url, body, { headers }).subscribe(
      (res: any) => {
        //console.log('API call successful', res);
        if (res.status === 'True') {
          this._snackBar.open('Items added successfully', 'Close', {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        } else {
          this._snackBar.open('Failed to add items', 'Close', {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        }
        this.getItemList(this.data.id, this.data.api);
      },
      (error: any) => {
        console.error('API call failed', error);
        this._snackBar.open('Failed to add items', 'Close', {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
        this.getItemList(this.data.id, this.data.api);
      }
    );
  }


}
