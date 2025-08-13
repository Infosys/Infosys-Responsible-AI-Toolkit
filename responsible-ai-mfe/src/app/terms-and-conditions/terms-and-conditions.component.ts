/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-terms-and-conditions',
  templateUrl: './terms-and-conditions.component.html',
  styleUrls: ['./terms-and-conditions.component.css']
})
export class TermsAndConditionsComponent {
  isCloseDisabled: boolean = true; // Set this to true or false as needed
  isChecked = false;
  userId=""
  setUserConsentUrl=""
  getUserConsentUrl=""

  
  constructor(
    public https: HttpClient,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<TermsAndConditionsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.userId = data.userId;
    this.setUserConsentUrl = data.setUserConsentUrl;
    this.getUserConsentUrl = data.getUserConsentUrl;
  }

  // Closes the dialog window
  closeWindow(): void {
    this.dialogRef.close();
  }

   // Fetches the user's consent status from the server
  getUserConsent() {
    let userId = this.userId;
    let getUserConsent = this.getUserConsentUrl
    console.log('Fetching user consent for user:', userId);
    
    const url = `${getUserConsent}${userId}`;
    this.https.get(url, { headers: { 'accept': 'application/json' } }).subscribe(
      (response: any) => {
        console.log('User consent:', response);
        if (response.userConsentStatus == true) {
          console.log('User has given consent');
          this.closeWindow();
        } else {
          console.log('User has not given consent');
          this.snackBar.open('Please accept terms and conditions to continue', 'Close', {
            duration: 3000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
          });
          
        }
      },
      (error) => {
        console.error('Error fetching user consent:', error);
      }
    );
  }

  // Handles the click event for accepting user consent
  onClickAcceptUserConsent() {
    console.log("value of check box", this.isChecked);
    if (this.isChecked == true) {
      this.setUserConsent();
    } else {
      this.snackBar.open('Please read the Terms & Conditions then click on the checkbox to proceed', 'Close', {
        duration: 3000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
      });
    }
  }

   // Sends the user's consent status to the server
  setUserConsent() {
    const url:any = this.setUserConsentUrl;
    const payload = {
      userId: this.userId,
      userConsentStatus: true
    };
  
    this.https.post(url, payload, {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).subscribe(
      (response) => {
        console.log('User consent set successfully:', response);
        this.snackBar.open('User consent Accepted successfully', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
        });
        this.closeWindow();
      },
      (error) => {
        console.error('Error setting user consent:', error);
        this.snackBar.open('Failed to set user consent', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
        });
      }
    );
  }

  
}
