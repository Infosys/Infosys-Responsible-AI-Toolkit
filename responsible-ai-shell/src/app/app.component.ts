/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit } from '@angular/core';
import { NavigationStart, Router } from '@angular/router';
import { BaseHrefService } from './base-href.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {

  title = 'AI_Demo';

  // subscription: any;

   constructor(private baseHrefService: BaseHrefService) {}
   ngOnInit(): void {
       const condition = environment.isSSO;
       this.baseHrefService.setBaseHref(condition);

       const baseHref = this.baseHrefService.getBaseHref();
       const baseElement = document.querySelector('base');
       if (baseElement) {
        baseElement.setAttribute('href', baseHref);
        }

   }
  //   this.subscription = router.events.subscribe((event) => {
  //     if (event instanceof NavigationStart) {
  //       const browserRefresh = !router.navigated;
  //     }
  //   });
  // }
}
