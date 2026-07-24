/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { FmModerationService } from 'src/app/services/fm-moderation.service';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { RequestModerationService } from './request-moderation.service';
import { Subject, takeUntil } from 'rxjs';
@Component({
  selector: 'app-request-moderation',
  templateUrl: './request-moderation.component.html',
  styleUrls: ['./request-moderation.component.scss'],
  encapsulation: ViewEncapsulation.None
})

export class RequestModerationComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  @Input() customApipayloadStatus: any;
  @Input() bannedCategoriesDisplay: any;
  @Input() gibrishDisplayLabels: any;
  @Input() requestTime: any;
  @Input() openAITime: any;
  @Input() nemoChecksApiResponses: any;
  @Input() contentDetectorState: any;
  @Input() prompt: any;
  @Input() modelName: any;
  @Input() llmEvalPayload: any;
  @Input() requestModerationTemplates: any;
  @Input() templateBasedPayload: any;
  @Input() privAnzOutput: any;
  @Input() analyze: any;
  @Input() fairness_response: any;
  @Input() imagePromptInjection: any;
  @Input() imageJailbreak: any;
  @Input() imageRestrictedTopic: any;
  @Input() coupledModeration: any;
  @Input() hallucinationSwitchCheck: any;

  requestModerationResult: any = {};
  activeTab = 'Model-Based Guardrails';
  dummyDataResult = {
    GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
    BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
  };

  constructor(
    private fmService: FmModerationService,
    private dialog: MatDialog,
    private requestModService: RequestModerationService) { }

  // Initializes the component and sets up API calls
  ngOnInit() {
    if (this.requestModerationTemplates.length == 0) {
      this.activeTab = 'Model-Based Guardrails';
    }
    this.requestModService.fetchApiUrl();

    this.fmService.currentData.pipe(takeUntil(this.destroy$)).subscribe(data => {
      if (data) {
        this.requestModerationResult = data.moderationResults.requestModeration
      } else {
        console.log("No data")
      }
    });
    if (this.customApipayloadStatus == true) {
      this.dummyDataResult = {
        GibberishLabels: this.gibrishDisplayLabels,
        BannedCategories: this.bannedCategoriesDisplay,
      };
    } else {
      this.dummyDataResult = {
        GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
        BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
      };
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  changeTab = (tab: string) => {
    this.activeTab = tab;
  }

  // OPEN SIDE POPUP
  openRightSideModal(data: any) {
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop'
    });

    dialogRef.afterClosed().pipe(takeUntil(this.destroy$)).subscribe(() => {
      console.log("POPUP CLOSE")
    });
  }

}
