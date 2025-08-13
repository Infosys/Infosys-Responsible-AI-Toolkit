/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Input, Directive, ElementRef, OnChanges, OnInit, OnDestroy } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { translationNotFoundMessage } from '../../config/translation.config';

/**
 * A wrapper directive on top of the translate pipe as the inbuilt translate directive from ngx-translate is too verbose and buggy
 */
@Directive({
  selector: '[jhiTranslate]',
})
export class TranslateDirective implements OnChanges, OnInit, OnDestroy {
  @Input() jhiTranslate!: string;
  @Input() translateValues?: { [key: string]: unknown };

  private readonly directiveDestroyed = new Subject();

  constructor(private el: ElementRef, private translateService: TranslateService) {}

  ngOnInit(): void {
    this.translateService.onLangChange.pipe(takeUntil(this.directiveDestroyed)).subscribe(() => {
      this.getTranslation();
    });
    this.translateService.onTranslationChange.pipe(takeUntil(this.directiveDestroyed)).subscribe(() => {
      this.getTranslation();
    });
  }

  /**
   * * This method is called when the input properties of the directive change.
   * * It is used to update the translation when the input properties change.
   */
  ngOnChanges(): void {
    this.getTranslation();
  }

  /**
   * * This method is called when the directive is destroyed.
   * * It is used to clean up the resources used by the directive.
   */
  ngOnDestroy(): void {
    this.directiveDestroyed.next(null);
    this.directiveDestroyed.complete();
  }

  /**
   * * This method is used to get the translation for the given key and values.
   * * It uses the translate service to get the translation and sets the innerHTML of the element to the translation.
   */
  private getTranslation(): void {
    this.translateService
      .get(this.jhiTranslate, this.translateValues)
      .pipe(takeUntil(this.directiveDestroyed))
      .subscribe({
        next: value => {
          this.el.nativeElement.innerHTML = value;
        },
        error: () => `${translationNotFoundMessage}[${this.jhiTranslate}]`,
      });
  }
}
