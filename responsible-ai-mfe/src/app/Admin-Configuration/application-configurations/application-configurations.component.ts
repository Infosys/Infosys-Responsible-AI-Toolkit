/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-application-configurations',
  templateUrl: './application-configurations.component.html',
  styleUrls: ['./application-configurations.component.css']
})
export class ApplicationConfigurationsComponent implements OnInit {

  constructor(private _snackBar: MatSnackBar, public https: HttpClient, private modalservice: NgbModal,private cdr: ChangeDetectorRef) { }

  public ip_port : any

  public admin_fm_admin_get_OpenAiStatusandRoll = environment.admin_fm_admin_get_OpenAiStatusandRoll
  public admin_fm_admin_Update_OpenAiStatus = environment.admin_fm_admin_Update_OpenAiStatus
  public admin_fm_admin_UserRole = environment.admin_fm_admin_UserRole
  public admin_fm_admin_Update_OpenSelfReminderStatus = ""
  public admin_fm_admin_Update_OpenNemoStatus = ""
  
  OpenAitoogleValue:any;
  OpenAitoogleNewValue:any;
  openAiStatusasperUserRole:any;
  Account_Role:any;

  displayedColumns: string[] = ['role','isOpenAI','selfReminder'];
  dataSource: any;

  // Toggles the OpenAI status for a specific role
  ontoggleOpen(e:any,roleV:any){
    this.OpenAitoogleNewValue = !e.target.checked;
    console.log(e.target.checked);
    console.log(roleV);

    this.https.patch(this.admin_fm_admin_Update_OpenAiStatus,{isOpenAI: e.target.checked,role: roleV}).subscribe
      ((res: any) => {
        
          if (res.isOpenAI == true) {
            const message = "Open Ai Turned On Succesfully " + res.role
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });
          } else if (res.isOpenAI == false) {
            const message = "Open Ai Turned of Succesfully for "+ res.role
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });
  
          }
          this.cdr.detectChanges();

          this.https.get(this.admin_fm_admin_get_OpenAiStatusandRoll).subscribe
      ((res: any) => {
        this.OpenAitoogleValue = res.isOpenAI
        this.dataSource = res.result

      }, error => {
        console.log(error.status);
        if (error.status == 430) {
          console.log(error.error.detail)
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });
        } else {
          console.log(error)
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });

        }
      })
        

      }, error => {
        console.log(error.status);
        if (error.status == 430) {
          console.log(error.error.detail)
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });
        } else {
          console.log(error)
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });

        }
      })
      this.cdr.detectChanges();

  }

  // Toggles the self-reminder status for a specific role
  ontoggleReminder(e:any,roleV:any){
    this.OpenAitoogleNewValue = !e.target.checked;
    console.log(e.target.checked);
    console.log(roleV);
    this.https.patch(this.admin_fm_admin_Update_OpenSelfReminderStatus,{selfReminder: e.target.checked,role: roleV}).subscribe // 
     ((res: any) => {
        
          if (res.isOpenAI == true) {
            const message = "Self Reminder Turned On Succesfully" + res.role
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });
          } else if (res.isOpenAI == false) {
            const message = "Self Reminder Turned of Succesfully for "+ res.role
            const action = "Close"
            this._snackBar.open(message, action, {
              duration: 1000,
              panelClass: ['le-u-bg-black'],
            });
  
          }

        

      }, error => {
        // You can access status:
        console.log(error.status);
        if (error.status == 430) {
          console.log(error.error.detail)
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });
        } else {
          console.log(error)
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });

        }
      })

  }

  // Initializes the component and sets up API configurations
  ngOnInit(): void {
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if(res != null){
        this.ip_port = JSON.parse(res);
        console.log("inside parse",this.ip_port.result)
      }
    }
    this.admin_fm_admin_get_OpenAiStatusandRoll =this.ip_port.result.Admin + this.ip_port.result.Admin_getOpenAI      // + environment.admin_fm_admin_get_OpenAiStatusandRoll
    this.admin_fm_admin_Update_OpenAiStatus =this.ip_port.result.Admin + this.ip_port.result.Admin_UpdateOpenAI       // + environment.admin_fm_admin_Update_OpenAiStatus
    this.admin_fm_admin_UserRole =this.ip_port.result.Admin + this.ip_port.result.Admin_userRole     //+ environment.admin_fm_admin_UserRole
    this.admin_fm_admin_Update_OpenSelfReminderStatus =this.ip_port.result.Admin + this.ip_port.result.Admin_UpdateReminder     // + "/api/v1/rai/admin/UpdateReminder"
    this.admin_fm_admin_Update_OpenNemoStatus =this.ip_port.result.Admin + this.ip_port.result.Admin_UpdateReminder      //+ "/api/v1/rai/admin/UpdateNemo"

    this.https.get(this.admin_fm_admin_get_OpenAiStatusandRoll).subscribe
      ((res: any) => {
        this.OpenAitoogleValue = res.isOpenAI
        this.dataSource = res.result

        

      }, error => {
        console.log(error.status);
        if (error.status == 430) {
          console.log(error.error.detail)
          console.log(error)
          const message = error.error.detail
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });
        } else {
          console.log(error)
          const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
          const action = "Close"
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
          });

        }
      })
      
  }
}
