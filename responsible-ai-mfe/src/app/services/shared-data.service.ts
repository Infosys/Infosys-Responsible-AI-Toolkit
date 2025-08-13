/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedDataService {
  private templateBasedResponsesSource = new BehaviorSubject<any>({});;
  templateBasedResponses = this.templateBasedResponsesSource.asObservable();
  private currentData: any = {};

  private naviTonemoderationRes: any = {};
  private naviToneModerationResSource = new BehaviorSubject<any>({});
  naviToneModerationRes = this.naviToneModerationResSource.asObservable();

  private imageBasedFailed: any = {
    modelBased: {},
    templateBased: {}
  };
  private imageBasedFailedChecksSource = new BehaviorSubject<any>({});
  imageBasedFailedChecks = this.imageBasedFailedChecksSource.asObservable();
  


  constructor() { }

  // Updates the template-based responses with a new key-value pair
  updateResponses(key: any,value:any) {
    this.currentData[key] = value;
    this.templateBasedResponsesSource.next(this.currentData);
  }

  // Updates the Navi Tone moderation responses with a new key-value pair
  updateNaviTonemoderationRes(key: any, value: any) {
    this.naviTonemoderationRes[key] = value;
    this.naviToneModerationResSource.next(this.naviTonemoderationRes);
  }

   // Updates the image-based failed checks for a specific type
  updateImageBasedModels(key: any, value: any, type: any) {
    // Type should be either 'modelBased' or 'templateBased'
    this.imageBasedFailed[type][key] = value;
    console.log(this.imageBasedFailed,"imageBasedFailed Service");
    this.imageBasedFailedChecksSource.next(this.imageBasedFailed);
  }

  // Clears all stored responses and resets the data
  clearResponses() {
    this.currentData = {};
    this.naviTonemoderationRes = {};
    this.imageBasedFailed = {
      modelBased: {},
      templateBased: {}
    };
    this.imageBasedFailedChecksSource.next(this.imageBasedFailedChecks);
    this.templateBasedResponsesSource.next(this.currentData);
    this.naviToneModerationResSource.next(this.naviToneModerationRes);
  }
}
