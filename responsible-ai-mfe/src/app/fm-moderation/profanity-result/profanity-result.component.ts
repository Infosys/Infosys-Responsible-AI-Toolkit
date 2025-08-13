/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input } from '@angular/core';
import { PagingConfig } from 'src/app/_models/paging-config.model';

@Component({
  selector: 'app-profanity-result',
  templateUrl: './profanity-result.component.html',
  styleUrls: ['./profanity-result.component.css']
})
export class ProfanityResultComponent {
  constructor() {
    this.pagingConfig = {
      itemsPerPage: this.itemsPerPage,
      currentPage: this.currentPage,
      totalItems: this.totalItems
    }
    this.pagingConfig2 = {
      itemsPerPage: this.itemsPerPage2,
      currentPage: this.currentPage2,
      totalItems: this.totalItems2
    }
   }
  @Input() profanityRes:any;
  pagingConfig: PagingConfig = {} as PagingConfig;
  pagingConfig2: PagingConfig = {} as PagingConfig;

  currentPage: number = 1;
  itemsPerPage: number = 4;
  totalItems: number = 0;
  // 2nd pagination
  currentPage2: number = 1;
  itemsPerPage2: number = 4;
  totalItems2: number = 0;


  // pagination for table 1
onTableDataChange(event: any) {
  this.currentPage = event;
  this.pagingConfig.currentPage = event;
  this.pagingConfig.totalItems = this.profanityRes.AnazRes.profanityScoreList.length;

}
onTableSizeChange(event: any): void {
  this.pagingConfig.itemsPerPage = event.result.value;
  this.pagingConfig.currentPage = 1;
  this.pagingConfig.totalItems = this.profanityRes.AnazRes.profanityScoreList.length;
}
// pagination for table 2
onTableDataChange2(event: any) {
  this.currentPage2 = event;
  this.pagingConfig2.currentPage = event;
  this.pagingConfig2.totalItems = this.profanityRes.AnazRes.profanity.length;

}
onTableSizeChange2(event: any): void {
  this.pagingConfig2.itemsPerPage = event.result.value;
  this.pagingConfig2.currentPage = 1;
  this.pagingConfig2.totalItems = this.profanityRes.AnazRes.profanity.length;
}

}
