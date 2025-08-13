import { HttpClient } from '@angular/common/http';
import { Component,OnInit,ViewChild } from '@angular/core';
import { FormBuilder, FormGroup,Validators } from '@angular/forms';
import { NgbPopover, NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { PagingConfig } from 'src/app/_models/paging-config.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from 'src/app/nonce.service';
 
interface ApiResponse {
  [key: string]: {
    ip: string;
    port: string;
  };
}
@Component({
  selector: 'app-api-configuration',
  templateUrl: './api-configuration.component.html',
  styleUrls: ['./api-configuration.component.css']
})
export class ApiConfigurationComponent implements OnInit{
  @ViewChild('p') popover!: NgbPopover;

  apis: any[] = [];
  apiForm: FormGroup; 
  editingApi: any = null;
  editingApiCopy: any = {};  // To hold the editable copy of the API object
  getConfigs: any;
  updateApi: any;
  deleteApi: any;
  createNewApi: any;
constructor(private fb: FormBuilder, private https: HttpClient,public _snackBar: MatSnackBar,public nonceService:NonceService) {
  this.apiForm = this.fb.group({
    name: ['', Validators.required],
      ip: ['', Validators.required],
      port: ['', Validators.required]
  });
  this.pagingConfig = {
    itemsPerPage: this.itemsPerPage,
    currentPage: this.currentPage,
    totalItems: this.totalItems
  }

}
pagingConfig: PagingConfig = {} as PagingConfig;
  
  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;

  dataSource: any = []
  isSearchOpen: boolean = false;
  searchName: string = '';
  filteredItems: string[] = []; 

ngOnInit(): void {
  let ip_port: any
  ip_port = this.getLocalStoreApi()
  this.setApiList(ip_port)
  this.getApis();
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
//-------------- used to set the api list urls ----------------
setApiList(ip_port: any) {
  this.getConfigs = ip_port.result.Admin + ip_port.result.Admin_getConfig ;
  this.updateApi = ip_port.result.Admin + ip_port.result.Admin_updateConfig;
  this.deleteApi = ip_port.result.Admin + ip_port.result.Admin_deleteConfig;
  this.createNewApi = ip_port.result.Admin + ip_port.result.Admin_newConfig;
}

// Fetches the list of APIs from the server
getApis(): void {
  this.https.get(this.getConfigs)
    .subscribe((data: any) => {
      console.log("res2", data)
      const result: ApiResponse = data.result; 
      this.apis = Object.entries(result).map(([key, value]) => {
        return { name: key, ip:value };
      });
      this.dataSource = this.apis; 
      this.pagingConfig.totalItems = this.apis.length;
      this.onTableDataChange(this.currentPage)

    });
}

// Creates a new API configuration
createApi(): void {
  const apiData = {
    ApiName: this.apiForm.value.name,
    ApiIp: this.apiForm.value.ip,
    ApiPort: null
  };
  this.https.post(this.createNewApi, apiData)
    .subscribe(() => {
      const newApi = { name: apiData.ApiName, ip: `${apiData.ApiIp}:${apiData.ApiPort}`, port: apiData.ApiPort, isNew: true };
      this.apis.push(newApi);    
      this.pagingConfig.totalItems = this.apis.length;
       this.getApis();
      this.resetFormAndClosePopover();
    });
}

// Deletes an API configuration
deleteConfig(name: string): void {
  const apiIndex = this.apis.findIndex(api => api.name === name);
  if (apiIndex !== -1) {
    const apiData = {
      ApiName: name
    };
  this.https.delete(this.deleteApi, { body: apiData })
  .subscribe((res: any) => {
        this.apis.splice(apiIndex, 1);
          this.pagingConfig.totalItems = this.apis.length;
          const message = "API Deleted Successfully";
          const action = "Close";
          this._snackBar.open(message, action, {
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
        });
    }
    else {
      this._snackBar.open('Cannot delete existing API', 'Close', {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
    }
  }
  // removeNewApiFromLocalStorage(name: string): void {
  //   const storedNewApis = JSON.parse(localStorage.getItem('newApis') || '[]');
  //   const updatedNewApis = storedNewApis.filter((api: any) => api.name !== name);
  //   localStorage.setItem('newApis', JSON.stringify(updatedNewApis));
  // }
onTableDataChange(event: any) {
  this.currentPage = event;
  this.pagingConfig.currentPage = event;
  this.pagingConfig.totalItems = this.apis.length;
}

 // Resets the form and closes the popover
resetFormAndClosePopover(): void {
  this.apiForm.reset();
  this.popover.close();
}

// Toggles the edit mode for an API
toggleEdit(api: any): void {
  if (this.editingApi === api) {
    // If already editing, save the updated data
    const apiData = {
      ApiName: this.editingApiCopy.name,
      ApiIp: this.editingApiCopy.ip,
      ApiPort: null
    };

    this.https.patch(this.updateApi, apiData)
      .subscribe(() => {
        this.editingApi = null;  // Clear the editing state
        this.getApis();  // Refresh the API list
        this._snackBar.open('API Updated Successfully', 'Close', {
          duration: 3000,
          horizontalPosition: 'left',
          panelClass: ['le-u-bg-black'],
        });
      });
  } else {
    // Start editing the API, create a copy for editing
    this.editingApi = api;
    this.editingApiCopy = { ...api };  // Create a copy for safe editing
  }
}

// Filters the API list based on the search input
  search() {
    if (this.searchName) {
      this.apis = this.apis.filter((item:any) =>
        item.name.toLowerCase().includes(this.searchName.toLowerCase())
      );
      this.currentPage = 1;
      this.pagingConfig.currentPage = 1;
      this.pagingConfig.totalItems = this.apis.length;
    } else {
      this.apis = this.dataSource;
      this.currentPage = 1;
      this.pagingConfig.currentPage = 1;
      this.pagingConfig.totalItems = this.apis.length;
  
    }
  }
  // Toggles the search bar visibility
  toggleSearch() {
    this.isSearchOpen = !this.isSearchOpen;
    this.searchName = '';
    this.filteredItems = [];
    }
  closeSearch() {
    this.isSearchOpen = false;
    this.searchName = '';
    this.apis = this.dataSource;
    this.currentPage = 1;
    this.pagingConfig.currentPage = 1;
    this.pagingConfig.totalItems = this.apis.length;
  }
}
