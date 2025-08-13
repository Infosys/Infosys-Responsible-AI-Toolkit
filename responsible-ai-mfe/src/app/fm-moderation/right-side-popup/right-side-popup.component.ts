/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Inject, Input } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-right-side-popup',
  templateUrl: './right-side-popup.component.html',
  styleUrls: ['./right-side-popup.component.css']
})
export class RightSidePopupComponent {
  @Input() data: any;
  apiUrlList: any = {};
  privacyCheckRes: any;
  toxicityRes: any;
  profanityRes: any;

  constructor(@Inject(MAT_DIALOG_DATA) public dialogData: any,public dialogRef: MatDialogRef<RightSidePopupComponent>,public _snackBar:MatSnackBar,private https : HttpClient) {
    this.data = dialogData;
  }

  // Closes the dialog
  closeDialog() {
    this.dialogRef.close();
  }

  // Initializes the component and sets up API calls based on dialog type
  ngOnInit() {
    let { ip_port } = this.retrieveLocalStorageData();
    this.setApiList(ip_port);
    if (this.dialogData.type == 'privacyCheck') {
      this.callPrivacyPopupAPI(this.dialogData.prompt);
    }else if (this.dialogData.type == 'privacyCheckRes') {
      this.callPrivacyPopupAPI(this.dialogData.openai_result);
    }else if (this.dialogData.type == 'toxicityCheckReq') {
      this.callReqToxicityInfoAPI(this.dialogData.prompt);
    }else if (this.dialogData.type == 'toxicityCheckRes') {
      this.callResToxicityInfoAPI(this.dialogData.summaryStatus,this.dialogData.openai_result);
    }else if (this.dialogData.type == 'profanityCheckReq') {
      this.callReqProfanityAPI(this.dialogData.text);
    }
  }

  // Sets the API list URLs
  setApiList(ip_port: any) {
    this.apiUrlList.privacyPopup = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_PrivacyPopup; //+ environment.fm_api_privacyShield
    this.apiUrlList.fm_api_inf_ToxicityPopup = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_ToxicityPopup; // + environment.fm_api_inf_ToxicityPopup
    this.apiUrlList.fm_api_inf_ProfanityPopup = ip_port.result.FM_Moderation + ip_port.result.Moderationlayer_ProfanityPopup; // + environment.fm_api_inf_ProfanityPopup

  }

  // Retrieves API configuration from local storage
  retrieveLocalStorageData() {
    let ip_port;
    if (localStorage.getItem('res') != null) {
      const x = localStorage.getItem('res');
      if (x != null) {
        ip_port = JSON.parse(x);
      }
    }
    return { ip_port };
  }

  // Handles API errors and displays a snackbar message
  handleError(error: any) {
    console.log(error.status);
    const action = 'Close';
    let message
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else if (error.error && (error.error.detail || error.error.message)) {
      message = error.error.detail || error.error.message;
    }
    this._snackBar.open(message, action, {
      duration: 3000,
      horizontalPosition: 'left',
      panelClass: ['le-u-bg-black'],
    });
    this.closeDialog()
  }

  // Calls the Privacy Check API
  callPrivacyPopupAPI(prompt:any) {
    const payload = {
      text: prompt,
      PiientitiesConfiguredToDetect: [
        'PERSON',
        'LOCATION',
        'DATE',
        'AU_ABN',
        'AU_ACN',
        'IN_AADHAAR',
        'AU_MEDICARE',
        'AU_TFN',
        'CREDIT_CARD',
        'CRYPTO',
        'DATE_TIME',
        'EMAIL_ADDRESS',
        'ES_NIF',
        'IBAN_CODE',
        'IP_ADDRESS',
        'IT_DRIVER_LICENSE',
        'IT_FISCAL_CODE',
        'IT_IDENTITY_CARD',
        'IT_PASSPORT',
        'IT_VAT_CODE',
        'MEDICAL_LICENSE',
        'IN_PAN',
        'PHONE_NUMBER',
        'SG_NRIC_FIN',
        'UK_NHS',
        'URL',
        'PASSPORT',
        'US_ITIN',
        'US_PASSPORT',
        'US_SSN',
      ],
      PiientitiesConfiguredToBlock: ['IN_AADHAAR', 'IN_PAN', 'US_PASSPORT', 'US_SSN'],
    };
    const options = {
      inputText: prompt,
    };
    this.https.post(this.apiUrlList.privacyPopup, payload).subscribe(
      (res: any) => {
        console.log(res.privacyCheck);
        this.privacyCheckRes = res.privacyCheck[0];
      },
      error => {
        this.handleError(error)
      }
    );
  }

  // Calls the Toxicity Info API for response text
  callResToxicityInfoAPI(summaryStatus:any,openai_result:any) {
    // if (((this.summaryStatus == "FAILED") || (this.reSstatus == 'FAILED')) || ((this.summaryStatus == 'FAILED') && (this.reSstatus == 'FAILED'))) {
    if (summaryStatus == 'PASSED') {
      const options = {
        text: openai_result,
        ToxicityThreshold: {
          ToxicityThreshold: 0.6,
          SevereToxicityThreshold: 0.6,
          ObsceneThreshold: 0.6,
          ThreatThreshold: 0.6,
          InsultThreshold: 0.6,
          IdentityAttackThreshold: 0.6,
          SexualExplicitThreshold: 0.6,
        },
      };
      this.toxicityRes = [];

      this.https.post(this.apiUrlList.fm_api_inf_ToxicityPopup, options).subscribe(
        (res: any) => {
          this.toxicityRes = res.toxicity;
        },
        error => {
          this.handleError(error)
        }
      );
    } else {
      const message = 'Failed to Load Toxicity Api as there is no Response Text';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 1000,
      });
    }
  }

  // Calls the Toxicity Info API for request text
  callReqToxicityInfoAPI(prompt:any) {
    const options = {
      text: prompt,
      ToxicityThreshold: {
        ToxicityThreshold: 0.6,
        SevereToxicityThreshold: 0.6,
        ObsceneThreshold: 0.6,
        ThreatThreshold: 0.6,
        InsultThreshold: 0.6,
        IdentityAttackThreshold: 0.6,
        SexualExplicitThreshold: 0.6,
      },
    };
    this.toxicityRes = [];

    this.https.post(this.apiUrlList.fm_api_inf_ToxicityPopup, options).subscribe(
      (res: any) => {
        this.toxicityRes = res.toxicity;
      },
      error =>{
        this.handleError(error)
      }
    );
    // }
  }

  // Calls the Profanity Check API
  callReqProfanityAPI(inputText:any) {
    const options = {
      text: inputText,
    };
    this.https.post(this.apiUrlList.fm_api_inf_ProfanityPopup, options).subscribe(
      (res: any) => {
        if (res.profanity.length == 0) {
          const message = 'There are no Profane Words in the Input Text';
          const action = 'Close';
          this._snackBar.open(message, action, {
            duration: 5000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black'],
          });
          this.closeDialog()
        } else {
          this.profanityRes = res.profanity;
        }
      },
      error => {
        this.handleError(error)
      }
    );
  }
}
