/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import {  Component, Input } from '@angular/core';
import { PagingConfig } from 'src/app/_models/paging-config.model';

@Component({
  selector: 'app-privacy-result',
  templateUrl: './privacy-result.component.html',
  styleUrls: ['./privacy-result.component.css']
})
export class PrivacyResultComponent {
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
  pagingConfig: PagingConfig = {} as PagingConfig;
  pagingConfig2: PagingConfig = {} as PagingConfig;

  currentPage: number = 1;
  itemsPerPage: number = 5;
  totalItems: number = 0;
  // 2nd pagination
  currentPage2: number = 1;
  itemsPerPage2: number = 5;
  totalItems2: number = 0;
  @Input() privacyRes: any;
  @Input() prompt: any;
  @Input() privacyOption: string = 'Choose Options';
  decryptedtoggle: boolean = false;

  // Toggles the decrypted state of the privacy result
  onClickx(){
    console.log("Decrypting the privacy result");
    this.privacyRes.decryptedtoggle = !this.privacyRes.decryptedtoggle;
    // this.decryptedtoggle = true;
  }

   // Returns the background color based on the entity type
  getBackgroundColor(type: string): string {
    switch (type) {
      case 'PERSON':
        return '#b7e4c7';
    case 'LOCATION':
        return '#ffffb3'; 
    case 'AADHAR_NUMBER':
        return '#add8e6'; 
    case 'CREDIT_CARD':
        return '#ffaaaa';
    case 'PHONE_NUMBER':
        return '#dabfff'; 
    case 'EMAIL_ADDRESS':
        return '#ffbf87'; 
    default:
        return '#dddddd'; 
    }
}
// getProcessedPrompt(): { text: string; color: string | null, type: string | null }[] {
//   if (!this.prompt) return [];
  
//   const words = this.prompt.split(' ');
//   return words.map((word: string) => {
//     const matchingEntities = this.privacyRes.AnazRes.PIIEntities.filter((entity: { responseText: string; score: number; type: string }) => 
//       entity.responseText.trim().toLowerCase() === word.trim().toLowerCase()
//     );

//     const highestScoreEntity = matchingEntities.sort((a: { score: number; type: string }, b: { score: number; type: string }) => b.score - a.score)[0];

//     return {
//       text: word + (highestScoreEntity ? ` [${highestScoreEntity.type}]` : ''),
//       color: highestScoreEntity ? this.getBackgroundColor(highestScoreEntity.type) : null,
//       type: highestScoreEntity ? highestScoreEntity.type : null
//     };
//   });
// }

// Processes the prompt to highlight identified entities
getProcessedPrompt(): { text: string; color: string | null, type: string | null }[] {
  if (!this.prompt || !this.privacyRes.AnazRes.PIIEntities) return [];
  
  let processedPrompt = [];
  let remainingPrompt = this.prompt;
  interface Entity {
    responseText: string;
    score: number;
    type: string;
  }
  
  this.privacyRes.AnazRes.PIIEntities.forEach((entity: Entity) => {
    let entityIndex = remainingPrompt.toLowerCase().indexOf(entity.responseText.toLowerCase());
    if (entityIndex !== -1) {

      if (entityIndex > 0) {
        processedPrompt.push({ text: remainingPrompt.substring(0, entityIndex), color: null, type: null });
      }

      processedPrompt.push({
        text: `${entity.responseText} [${entity.type}]`, // Append the entity type
        color: this.getBackgroundColor(entity.type),
        type: entity.type
      });

      remainingPrompt = remainingPrompt.substring(entityIndex + entity.responseText.length);
    }
  });

  if (remainingPrompt.length > 0) {
    processedPrompt.push({ text: remainingPrompt, color: null, type: null });
  }
  
  return processedPrompt;
}
// pagination for table 1
onTableDataChange(event: any) {
  this.currentPage = event;
  this.pagingConfig.currentPage = event;
  this.pagingConfig.totalItems = this.privacyRes.AnazRes.PIIEntities.length;

}
onTableSizeChange(event: any): void {
  this.pagingConfig.itemsPerPage = event.result.value;
  this.pagingConfig.currentPage = 1;
  this.pagingConfig.totalItems = this.privacyRes.AnazRes.PIIEntities.length;
}
// pagination for table 2
onTableDataChange2(event: any) {
  this.currentPage2 = event;
  this.pagingConfig2.currentPage = event;
  this.pagingConfig2.totalItems = this.privacyRes.EncryptRes.items.length;

}
onTableSizeChange2(event: any): void {
  this.pagingConfig2.itemsPerPage = event.result.value;
  this.pagingConfig2.currentPage = 1;
  this.pagingConfig2.totalItems = this.privacyRes.EncryptRes.items.length;
}
}
