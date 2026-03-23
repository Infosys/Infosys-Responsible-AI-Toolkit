/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { SharedService } from './shared.service';

@Component({
  selector: 'app-configuration-parent',
  templateUrl: './configuration-parent.component.html',
  styleUrls: ['./configuration-parent.component.css']
})
export class ConfigurationParentComponent implements OnInit, OnDestroy {
  @ViewChild('accountMapping') accountMapping!: ElementRef;
  public subscription: Subscription = new Subscription;
  
  constructor(private sharedService: SharedService) {}
  selectedTab = 0;
  recoGnizers = true;
  accountMaping = false;
 
  toggleTab(){
    this.recoGnizers = !this.recoGnizers;
    this.accountMaping = !this.accountMaping;
  }
  ngOnInit() {
    this.subscription = this.sharedService.clickEvent$.subscribe(() => {
      this.clickAccountMapping();
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  clickAccountMapping() {
    this.accountMapping.nativeElement.click();
  }


}
