/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component } from '@angular/core';
import { RoleManagerService } from '../services/role-maganer.service';

@Component({
  selector: 'app-image-parent',
  templateUrl: './image-parent.component.html',
  styleUrls: ['./image-parent.component.css']
})
export class ImageParentComponent {
  imageMode = true;
  generateMode = false;

  uploadMode = true;
  dicomMode = false;
  constructor(public roleService : RoleManagerService) { } 

  ngOnInit(): void {
    console.log("HEYS",this.roleService.checkActiveTabExists('Workbench', 'Image', 'dicom'));
    if (!this.roleService.checkActiveTabExists('Workbench', 'Image', 'T-AI-Upload') && !this.roleService.checkActiveTabExists('Workbench', 'Image', 'T-AI-DICOM')) {
      this.uploadMode = false;
      this.dicomMode = false;
    }else if (!this.roleService.checkActiveTabExists('Workbench', 'Image', 'T-AI-Upload')) {
      this.uploadMode = false;
      this.dicomMode = true;
    }

    if(!this.roleService.checkActiveTabExists('Workbench', 'Image', 'Traditional-AI')){
      this.imageMode = false;
      this.generateMode = true;
    }
  }

  ontoglechange(event: any) {
    console.log(event.checked);
    if (event.checked == true) {
      this.imageMode = false;
      this.generateMode = true;
    } else {
      this.imageMode = true;
      this.generateMode = false;
    }
  }
  toggleUploadGenerate(){
    this.uploadMode = !this.uploadMode;
    this.dicomMode = !this.dicomMode;
  }



}
