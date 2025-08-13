/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component } from '@angular/core';
import { RoleManagerService } from '../services/role-maganer.service';

@Component({
  selector: 'app-structure-text-parent',
  templateUrl: './structure-text-parent.component.html',
  styleUrls: ['./structure-text-parent.component.css']
})
export class StructureTextParentComponent {
  diffPrivacy = false;
  structureText = true;

  constructor(public roleService : RoleManagerService) { } 

  ngOnInit(): void {
    // console.log("HEYS",this.roleService.checkActiveTabExists('Workbench', 'Image', 'dicom'));
    // if (!this.roleService.checkActiveTabExists('Workbench','Structured-Text','Differential-Privacy') && !this.roleService.checkActiveTabExists('Workbench', 'Image', 'T-AI-DICOM')) {
    //   this.structureText = false;
    //   this.dicomMode = false;
    // }
    if (!this.roleService.checkActiveTabExists('Workbench', 'Unstructured-Text', 'Differential-Privacy')) {
      this.diffPrivacy = false;
      this.structureText = true;
    }
    // if(!this.roleService.checkActiveTabExists('Workbench', 'Image', 'Traditional-AI')){
    //   this.diffPrivacy = false;
    //   this.structureText = true;
    // }
  }

  // Toggles between Differential Privacy and Structured Text modes
  ontoglechange(event: any) {
    if(event.checked == true){
      this.diffPrivacy = false;
      this.structureText = true;
    }else{
      this.structureText = false;
      this.diffPrivacy = true;
    }
  } 



}
