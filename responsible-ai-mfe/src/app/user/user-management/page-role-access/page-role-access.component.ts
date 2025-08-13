/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Inject, ViewChild } from '@angular/core';
import { PageRoleAccessService } from './page-role-access.service';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatCheckboxChange } from '@angular/material/checkbox';
import { NgbPopover, NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NonceService } from 'src/app/nonce.service';
interface Tab {
  name: string;
  active: boolean;
  subtabs?: Subtab[];
}

interface Subtab {
  name: string;
  active: boolean;
  selectType?: SelectType[];
}

interface SelectType {
  name: string;
  active: boolean;
  options: any[]; // Add this property
}

@Component({
  selector: 'app-page-role-access',
  templateUrl: './page-role-access.component.html',
  styleUrls: ['./page-role-access.component.css']
})
export class PageRoleAccessComponent {
@ViewChild('p') p!: NgbPopover;
accessiblePagesFinalUrl : any
newRoleUrl : any;
getRoleUrl : any;
updatePagesUrl : any;
createPageAuthUrl : any;
selectedRole: string = 'Select A Role';
updatedRoles : any ;
pages: any;
originalPages : any;
workbenchTabs:any;
traditionalAIEnabled: boolean = true;
generativeAIEnabled: boolean = true;
selectAllEnabled: boolean = true;

unstructuredTextEnabled: boolean = true;
structuredTextEnabled: boolean = false;
imageEnabled: boolean = false;
videoEnabled: boolean = false;
codeEnabled: boolean = false;

// data assign
unstructuredtabsactive:any;
unstructuredimagetabs: any;
pagestabs:any;
originalpagestabs:any;
optionscheck : any ;
//
// Pop up form
AccountForm!: FormGroup;
NewAccPort!: FormGroup;

//
tabs!: Tab[];

  constructor(private snackBar:MatSnackBar,private pageRoleAccessService: PageRoleAccessService, @Inject(MAT_DIALOG_DATA) public data: any,private https: HttpClient,public nonceService:NonceService)
    {
      this.CreateNewRoleForm();
     }

     // Initializes the component and fetches accessible pages
  ngOnInit(): void {
    console.log(this.data.options);
    this.updatedRoles = this.data.options;
    // this.data.options = this.updatedRoles;
    this.newRoleUrl = this.data.accessiblePagesUrl + "/v1/rai/backend/newRole";
    this.getRoleUrl = this.data.accessiblePagesUrl + "/v1/rai/backend/users/authorities";
    this.createPageAuthUrl = this.data.accessiblePagesUrl + "/v1/rai/backend/createpageauthoritynew";
    // this.createPageAuthUrl = "http://localhost:30019/v1/rai/backend/createpageauthoritynew";
    // this.newRoleUrl = "http://localhost:30019/v1/rai/backend/newRole";
    //this.getRoleUrl = "http://localhost:30019/v1/rai/backend/users/authorities";
    this.accessiblePagesFinalUrl = this.data.accessiblePagesUrl + "/v1/rai/backend/pageauthoritynew";
    this.updatePagesUrl = this.data.accessiblePagesUrl + "/v1/rai/backend/pageauthoritynewupdate";
    let roleDefault = "ROLE_ADMIN"
    this.pageRoleAccessService.getAccessiblePages(this.accessiblePagesFinalUrl, roleDefault)
      .subscribe(
        data => {
          this.originalPages = data.pages;
          console.log(this.originalPages, "originalPages")
        },
        error => {
          console.error('There was an error!', error);
        }
      );

  }

// Handles the selection of a role and updates the accessible pages
  onOptionSelected() {
    // DATA ASSIGNING
    // WORKBENCH TABS
    let workbenchTabs1 = this.originalPages['Workbench'].subtabs; // Extract Workbench
    this.workbenchTabs = Object.keys(workbenchTabs1);
    // add Workbench key to this.workbenchtabs at the 0 position
    this.workbenchTabs.unshift('Workbench');
    console.log(this.workbenchTabs, "keys");

    // Unstructured Text tabs
    this.workbenchTabs = workbenchTabs1['Unstructured-Text'];

    this.pageRoleAccessService.getAccessiblePages(this.accessiblePagesFinalUrl, this.selectedRole)
      .subscribe(
        data => {
          this.pages = data.pages;
          this.pagesDisplay(data.pages);
          this.functionForOriginalPages(this.originalPages);
          this.functionForPages(this.pages);

          this.compareAndSetCheckboxes();
        },
        error => {
          console.error('There was an error!', error);
        }
      );
  }

  // Processes the pages structure into the desired format
functionForPages(pages: any) {
    this.pagestabs = Object.entries(pages).map(([name, value]: [string, any]) => {
        const tab: Tab = {
            name,
            active: this.isTabActive(name, value.active)
        };

        if (value.subtabs) {
            tab.subtabs = Object.entries(value.subtabs).map(([subtabName, subtabValue]: [string, any]) => {
                const subtab: Subtab = {
                    name: subtabName,
                    active: this.isSubTabActive(subtabName, subtabValue.active),
                    selectType: []
                };

                // Handle active select types
                if (Array.isArray(subtabValue.active)) {
                    subtabValue.active.forEach((item: string) => {
                        subtab.selectType!.push({
                            name: item,
                            active: this.isSelectTypeActive(subtabName, item, subtabValue.selectType),
                            options: []
                        });
                    });
                }

                // Handle selectType property
                if (subtabValue.selectType) {
                    Object.entries(subtabValue.selectType).forEach(([selectTypeName, selectTypeValue]: [string, any]) => {
                        const existingSelectType = subtab.selectType!.find(type => type.name === selectTypeName);
                        if (existingSelectType) {
                            existingSelectType.active = this.isSelectTypeActive(subtabName, selectTypeName, selectTypeValue);
                            existingSelectType.options = Array.isArray(selectTypeValue) ? selectTypeValue : [];
                        } else {
                            subtab.selectType!.push({
                                name: selectTypeName,
                                active: this.isSelectTypeActive(subtabName, selectTypeName, selectTypeValue),
                                options: Array.isArray(selectTypeValue) ? selectTypeValue : []
                            });
                        }
                    });
                }

                return subtab;
            });
        }

        return tab;
    });
    console.log(this.pagestabs, "pagestabs");
}

// Processes the original pages structure into the desired format
functionForOriginalPages(originalPages: any) {
    // Function to process the originalPages structure into the desired format
    this.originalpagestabs = Object.entries(originalPages).map(([name, value]: [string, any]) => {
        const tab: Tab = {
            name,
            active: this.isTabActive(name, value.active)
        };

        if (value.subtabs) {
            tab.subtabs = Object.entries(value.subtabs).map(([subtabName, subtabValue]: [string, any]) => {
                const subtab: Subtab = {
                    name: subtabName,
                    active: this.isSubTabActive(subtabName, subtabValue.active),
                    selectType: []
                };

                // Handle active select types
                if (Array.isArray(subtabValue.active)) {
                    subtabValue.active.forEach((item: string) => {
                        subtab.selectType!.push({
                            name: item,
                            active: this.isSelectTypeActive(subtabName, item, subtabValue.selectType),
                            options: []
                        });
                    });
                }

                // Handle selectType property
                if (subtabValue.selectType) {
                    Object.entries(subtabValue.selectType).forEach(([selectTypeName, selectTypeValue]: [string, any]) => {
                        const existingSelectType = subtab.selectType!.find(type => type.name === selectTypeName);
                        if (existingSelectType) {
                            existingSelectType.active = this.isSelectTypeActive(subtabName, selectTypeName, selectTypeValue);
                            existingSelectType.options = Array.isArray(selectTypeValue) ? selectTypeValue : [];
                        } else {
                            subtab.selectType!.push({
                                name: selectTypeName,
                                active: this.isSelectTypeActive(subtabName, selectTypeName, selectTypeValue),
                                options: Array.isArray(selectTypeValue) ? selectTypeValue : []
                            });
                        }
                    });
                }

                return subtab;
            });
        }

        return tab;
    });
    console.log(this.originalpagestabs, "originalpagestabs");
}

// Compares original pages and current pages to set checkbox states
compareAndSetCheckboxes() {
    this.tabs = this.originalpagestabs.map((tab: Tab) => {
        const tabInPages = this.pagestabs.find((t: Tab) => t.name === tab.name);
        // Set the active state for the tab based on pages
        tab.active = tabInPages !== undefined;

        if (tab.subtabs) {
            tab.subtabs = tab.subtabs.map((subtab: Subtab) => {
                const subtabInPages = tabInPages?.subtabs?.find((st: Subtab) => st.name === subtab.name);
                // Set the active state for the subtab based on pages
                subtab.active = subtabInPages !== undefined;

                if (subtab.selectType) {
                    subtab.selectType = subtab.selectType.map((selectType: SelectType) => {
                        const selectTypeInPages = subtabInPages?.selectType?.find((st: SelectType) => st.name === selectType.name);
                        // Set the active state for the select type based on pages and options presence
                        selectType.active = selectTypeInPages !== undefined && selectTypeInPages.options !== undefined && selectTypeInPages.options.length > 0;

                        if (selectType.options && selectTypeInPages?.options) {
                            // Map options to include the active state
                            selectType.options = selectType.options.map(option => ({
                                name: option,
                                active: selectTypeInPages.options.includes(option)
                            }));
                        } else {
                            // Ensure options are initialized with active set to false if no selectTypeInPages
                            selectType.options = selectType.options.map(option => ({
                                name: option,
                                active: false
                            }));
                        }

                        return selectType;
                    });
                }

                return subtab;
            });
        }

        return tab;
    });
    console.log(this.tabs, "tabs");
}

 // Checks if a tab is active
  isTabActive(tabName: string, active: any): boolean {
    const tabInPages = this.pages[tabName];
    // console.log(tabInPages, "tabInPages")
    return tabInPages ? true : false;
  }

   // Checks if a tab is active
  isSubTabActive(subtabName: string, active: any): boolean {
    const subtabInPages = this.pages[subtabName];
    // console.log(subtabInPages, "subtabInPages")
    return subtabInPages ? true : false;
  }

   // Checks if a select type is active
  isSelectTypeActive(subtabName: string, selectTypeName: string, selectTypeValue: any): boolean {
    const subtabInPages = this.pages[subtabName];
    // console.log(subtabInPages, "subtabInPages")
    if (subtabInPages && subtabInPages.selectType && subtabInPages.selectType[selectTypeName]) {
      return subtabInPages.selectType[selectTypeName].length > 0;
    }
    return false;
  }
  pagesDisplay(pages: any) {
    console.log(pages, "pages");
  }
  toggleAll() {
    this.traditionalAIEnabled = this.selectAllEnabled;
    this.generativeAIEnabled = this.selectAllEnabled;
  }

   // Handles changes in the select type checkboxes
  onSelectTypeChange(event: MatCheckboxChange, tabName: string, subTabName: string, selectTypeName: string) {
    const tab = this.originalpagestabs.find((t: { name: string; }) => t.name === tabName);
    const subtab = tab?.subtabs.find((st: { name: string; }) => st.name === subTabName);
    const selectType = subtab?.selectType.find((st: { name: string; }) => st.name === selectTypeName);
    if (selectType) {
        selectType.active = event.checked;
        selectType.options.forEach((option: { active: boolean; }) => {
            option.active = event.checked; // Set all options active state based on select type
        });
    }
}

// Handles changes in the options checkboxes
onOptionsSelect(event: MatCheckboxChange, tabName: string, subTabName: string, selectTypeName: string, optionName: string) {
  const tab = this.originalpagestabs.find((t: { name: string; }) => t.name === tabName);
  const subtab = tab?.subtabs.find((st: { name: string; }) => st.name === subTabName);
  const selectType = subtab?.selectType.find((st: { name: string; }) => st.name === selectTypeName);
  const option = selectType?.options.find((opt: { name: string; }) => opt.name === optionName);
  if (option) {
      option.active = event.checked;
  }
}
// Handles changes in the tab checkboxes
  onTabCheckboxChange(event: MatCheckboxChange, tabName: string) {
    const tab = this.originalpagestabs.find((t: { name: string; }) => t.name === tabName);
    if (tab) {
        tab.active = event.checked;
        tab.subtabs.forEach((subtab: { active: boolean; selectType: any[]; }) => {
            subtab.active = event.checked; // Set all subtabs active state based on tab
            subtab.selectType.forEach(select => {
                select.active = event.checked; // Set all select types active state based on subtab
                select.options.forEach((option: { active: boolean; }) => {
                    option.active = event.checked; // Set all options active state based on select type
                });
            });
        });
    }
}

 // Handles changes in the subtab checkboxes
onSubTabCheckboxChange(event: MatCheckboxChange, tabName: string, subTabName: string) {
    const tab = this.originalpagestabs.find((t: { name: string; }) => t.name === tabName);
    const subtab = tab?.subtabs.find((st: { name: string; }) => st.name === subTabName);
    if (subtab) {
        subtab.active = event.checked;
        subtab.selectType.forEach((select: { active: boolean; options: any[]; }) => {
            select.active = event.checked; // Set all select types active state based on subtab
            select.options.forEach(option => {
                option.active = event.checked; // Set all options active state based on select type
            });
        });
    }
}

  closeModal() {
    // Add your logic to close the modal here
  }

  // Submits the updated role access data
  onSubmit() {
    // add your code here
    console.log(this.originalpagestabs, "originalpagestabs before submit");
    let databasestruct = this.transformToDatabaseFormat(this.originalpagestabs);
    console.log(databasestruct, "originalpagestabs after submit");
    // this.pageRoleAccessService.updateRoleAccess(this.selectedRole, databasestruct);
    this.pageRoleAccessService.updateRoleAccess(this.selectedRole, databasestruct, this.updatePagesUrl).subscribe(
      response => {
        console.log('Data sent successfully', response);
        this.snackBar.open('Role access updated successfully', 'Close', {
          duration: 2000,
        });
      },
      error => {
        console.error('Error sending data', error);
      }
    );

  }

// Transform the data to the format that the database expects
transformToDatabaseFormat(originalPages: any): any {
  const transformedData: any = {
      pages: {}
  };

  originalPages.forEach((tab: any) => {
      const tabName = tab.name;

      // Initialize the tab in transformed data only if it is active
      if (tab.active) {
          transformedData.pages[tabName] = {
              active: [], // Initialize active as an empty array
              subtabs: {}
          };

          if (tab.subtabs) {
              tab.subtabs.forEach((subtab: any) => {
                  const subtabName = subtab.name;

                  // Only process the subtab if it is active
                  if (subtab.active) {
                      transformedData.pages[tabName].subtabs[subtabName] = {
                          active: [],
                          selectType: {}
                      };

                      // Collect active select types
                      subtab.selectType.forEach((selectType: any) => {
                          if (selectType.active) {
                              transformedData.pages[tabName].subtabs[subtabName].active.push(selectType.name);
                              transformedData.pages[tabName].subtabs[subtabName].selectType[selectType.name] = [];

                              // Collect active options for the select type
                              selectType.options.forEach((option: any) => {
                                  if (option.active) {
                                      transformedData.pages[tabName].subtabs[subtabName].selectType[selectType.name].push(option.name);
                                  }
                              });
                          }
                      });
                  }
              });
          }
      }
  });

  // Clean up empty structures
  for (const tabName in transformedData.pages) {
      const tab = transformedData.pages[tabName];

      // If no subtabs, remove them
      if (Object.keys(tab.subtabs).length === 0) {
          delete tab.subtabs;
      }

      // If no active states, set active to an empty array
      if (tab.active.length === 0) {
          tab.active = [];
      }
  }

  return transformedData;
}




// when click on reset button this function will call will reset all the checkboxes
resetCheckbox(){
  this.tabs = this.originalpagestabs.map((tab: Tab) => {
    tab.active = false;
    if (tab.subtabs) {
        tab.subtabs = tab.subtabs.map((subtab: Subtab) => {
            subtab.active = false;
            if (subtab.selectType) {
                subtab.selectType = subtab.selectType.map((selectType: SelectType) => {
                    selectType.active = false;
                    selectType.options = selectType.options.map(option => ({
                        name: option.name,
                        active: false
                    }));
                    return selectType;
                });
            }
            return subtab;
        });
    }
    return tab;
});
}

// Toggles the popover state
test(p:any){
  if (this.p.isOpen()) {
    console.log('Popover is open');
    this.p.toggle();
  } else {
    this.p.toggle();
    console.log('Popover is closed');
  }
}

// Creates the form for adding a new role
CreateNewRoleForm(){
  this.NewAccPort = new FormGroup({
    role: new FormControl('', [Validators.required]),
  });
}

 // Submits the new role form
submitRoleForm() {
  if (this.NewAccPort.valid) {
    const formData = this.NewAccPort.value;
    console.log("FORM SUBMIT",formData.role);
    this.https.post(this.newRoleUrl, formData).subscribe(
      (response: any) => {
        // Handle success response
        console.log(response);
        this.getUpdatedRoles()
        this.snackBar.open('Role created successfully', 'Close', {
          duration: 2000,
        });

      },
      (error: any) => {
        // Handle error response
        console.error(error);
      }
    );
    this.https.post(this.createPageAuthUrl, formData).subscribe(
      (response: any) => {
        // Handle success response
        console.log(response);
      },
      (error: any) => {
        // Handle error response
        console.error(error);
      }
    );

  }
}

// Fetches the updated list of roles
getUpdatedRoles(){
  this.https.get(this.getRoleUrl).subscribe(
    (response: any) => {
      // Handle successful response here
      console.log(response);
      this.updatedRoles = response;
      console.log(this.updatedRoles, "updatedRoles")
    },
    (error: any) => {
      // Handle error response here
      console.error(error);
    }
  );
}


}
