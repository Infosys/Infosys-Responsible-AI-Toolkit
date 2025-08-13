/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input } from '@angular/core';
import { FmModerationService } from 'src/app/services/fm-moderation.service';
import { RightSidePopupComponent } from '../right-side-popup/right-side-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

interface TopicScore {
  [topic: string]: string;
}

interface ToxicScore {
  metricName: string;
  metricScore: number;
}

interface ResponseModeration {
  generatedText: string;
  privacyCheck: {
    entitiesConfiguredToBlock: string[];
    entitiesRecognised: string[];
    result: string;
  };
  profanityCheck: {
    profaneWordsIdentified: string[];
    profaneWordsthreshold: string;
    result: string;
  };
  refusalCheck: {
    RefusalThreshold: string;
    refusalSimilarityScore: string;
    result: string;
  };
  restrictedtopic: {
    result: string;
    topicTypesConfiguredToBlock: string[];
    topicTypesRecognised: string[];
  };
  summary: {
    reason: string[];
    status: string;
  };
  textQuality: {
    readabilityScore: string;
    textGrade: string;
  };
  textRelevanceCheck: {
    PromptResponseSimilarityScore: string;
  };
  toxicityCheck: {
    result: string;
    toxicityTypesConfiguredToBlock: string[];
    toxicityTypesRecognised: string[];
  };
  bancodeCheck: {
    result: string;
   label: string;
  };
  gibberishCheck: {
    gibberishScore: { gibberish_label: string; gibberish_score: number }[];
    result: string;
    threshold: string;
  };
  invisibleTextCheck: {
    invisibleTextIdentified: string[];
    result: string;
    threshold: string;
  };
  sentimentCheck: {
    result: string;
    score: string;
    threshold: string;
  };
}

@Component({
  selector: 'app-response-moderation',
  templateUrl: './response-moderation.component.html',
  styleUrls: ['./response-moderation.component.scss'],
})
export class ResponseModerationComponent {

  @Input() customApipayloadStatus: any;
  @Input() bannedCategoriesDisplay: any;
  @Input() gibrishDisplayLabels: any;
  @Input() responseTime: any;
  @Input() openAITime: any;
  @Input() nemoModerationRailRes: any;
  @Input() openAIRes: any;
  @Input() summaryStatus: any;
  @Input() llmEvalPayload: any;
  @Input() responseModerationTemplates: any;
  @Input() selectedUseCaseName: any;
  @Input() setLoadTemplateResMod: Boolean = false;
  @Input() hallucinationSwitchCheck: any;
  @Input() templateBasedPayload: any;
  activeTab = 'Model-Based Guardrails';
  changeTab = (tab: string) => {
    this.activeTab = tab;
  };
  responseModerationResult: ResponseModeration = {
    generatedText: '',
    privacyCheck: {
      entitiesConfiguredToBlock: [],
      entitiesRecognised: [],
      result: '',
    },
    profanityCheck: {
      profaneWordsIdentified: [],
      profaneWordsthreshold: '',
      result: '',
    },
    refusalCheck: {
      RefusalThreshold: '',
      refusalSimilarityScore: '',
      result: '',
    },
    restrictedtopic: {
      result: '',
      topicTypesConfiguredToBlock: [],
      topicTypesRecognised: [],
    },
    summary: { reason: [], status: '' },
    textQuality: { readabilityScore: '', textGrade: '' },
    textRelevanceCheck: { PromptResponseSimilarityScore: '' },
    toxicityCheck: {
      result: '',
      toxicityTypesConfiguredToBlock: [],
      toxicityTypesRecognised: [],
    },
    bancodeCheck: { result: '', label: '' },
    gibberishCheck: { gibberishScore: [], result: '', threshold: '' },
    invisibleTextCheck: {
      invisibleTextIdentified: [],
      result: '',
      threshold: '',
    },
    sentimentCheck: { result: '', score: '', threshold: '' },
    //
  };
  constructor(
    private fmService: FmModerationService,
    public dialog: MatDialog,
    public _snackBar: MatSnackBar
  ) {}

  // Opens a right-side modal with the provided data
  openRightSideModal(data: any) {
    if (data.type == 'profanityCheckReq') {
      if (
        this.responseModerationResult?.profanityCheck['profaneWordsIdentified']
          .length == 0
      ) {
        this._snackBar.open('No profane words identified', 'Close', {
          duration: 2000,
        });
        return;
      }
    }
    const dialogRef = this.dialog.open(RightSidePopupComponent, {
      width: '52vw',
      data: data,
      backdropClass: 'custom-backdrop',
    });

    dialogRef.afterClosed().subscribe(() => {
      console.log('POPUP CLOSE');
    });
  }

   // Checks if an object is empty
  isEmptyObject(obj: any) {
    return Object.keys(obj).length === 0;
  }
  
  // Initializes the component and sets up API calls
  ngOnInit() {
    if (this.responseModerationTemplates.length == 0) {
      this.activeTab = 'Model-Based Guardrails';
    }
    this.fmService.currentData.subscribe((data) => {
      if (data) {
        // Display the data in your table
        console.log('_______________________________________________');
        this.responseModerationResult =
          data.moderationResults.responseModeration;
        console.log(
          '_______________responseModerationResult________________________________',
          this.responseModerationResult
        );
      } else {
        console.log('No data');
      }
    });
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
  dummyDataResult = {
    GibberishLabels: ['word salad', 'noise', 'mild gibberish', 'clean'],
    BannedCategories: ['Cf', 'Co', 'Cn', 'So', 'Sc'],
  };

}
