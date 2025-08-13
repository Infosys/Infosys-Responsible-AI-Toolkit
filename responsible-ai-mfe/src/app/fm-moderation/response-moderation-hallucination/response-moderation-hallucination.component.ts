/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';

@Component({
  selector: 'app-response-moderation-hallucination',
  templateUrl: './response-moderation-hallucination.component.html',
  styleUrls: ['./response-moderation-hallucination.component.css']
})
export class ResponseModerationHallucinationComponent {
  @Input() customApipayloadStatus: any;
  @Input() bannedCategoriesDisplay: any;
  @Input() gibrishDisplayLabels: any;
  @Input() responseTime:any;
  @Input() nemoModerationRailRes:any;
  @Input() openAIRes: any;
  @Input() summaryStatus: any;
  @Input() responseModerationResult:any;
  @Input() llmEvalPayload: any;
  @Input() responseModerationTemplates:any;
  @Input() selectedUseCaseName: any;
  @Input() setLoadTemplateResMod:Boolean = false;
  @Input() templateBasedPayload:any;
  constructor(public dialog: MatDialog,public _snackBar:MatSnackBar) {
  }
  activeTab = 'Model-Based Guardrails';
  ngOnInit() {
    if (this.responseModerationTemplates && this.responseModerationTemplates.length == 0) {
      this.activeTab = 'Model-Based Guardrails';
    }
    if(this.customApipayloadStatus== true){
      this.dummyDataResult = {
        GibberishLabels: this.bannedCategoriesDisplay,
        BannedCategories: this.gibrishDisplayLabels,
      };}else
      {
        this.dummyDataResult = {
          GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
          BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
        };
      }
  }
  changeTab = (tab: string) => {
    this.activeTab = tab;
  }

  // Opens a right-side modal 
  openRightSideModal(data:any) {
    if (data.type == 'profanityCheckReq') {
      if (this.responseModerationResult?.profanityCheck['profaneWordsIdentified'].length == 0){
        this._snackBar.open('No profane words identified', 'Close', {
          duration: 2000,
        });
        return
      }
    }
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop'
    });
  }

  // Checks if an object is empty
  isEmptyObject(obj: any) {
    return Object.keys(obj).length === 0;
  }

  dummyDataResult = {
    GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
    BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
  };
}
