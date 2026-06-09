/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit,OnDestroy  } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { mergeMap, takeUntil } from 'rxjs/operators';

import { ActivateService } from './activate.service';
import { Subject } from 'rxjs';

@Component({
  selector: 'jhi-activate',
  templateUrl: './activate.component.html',
})
export class ActivateComponent implements OnInit,OnDestroy  {
  error = false;
  success = false;
private destroy$ = new Subject<void>();

  constructor(private activateService: ActivateService, private route: ActivatedRoute) {}
  ngOnDestroy(): void {
  this.destroy$.next();
    this.destroy$.complete();  }

  ngOnInit(): void {
    this.route.queryParams.pipe(mergeMap(params => this.activateService.get(params['key'])),takeUntil(this.destroy$)
      ).subscribe(
      () => (this.success = true),
      () => (this.error = true)
    );
  }
}
