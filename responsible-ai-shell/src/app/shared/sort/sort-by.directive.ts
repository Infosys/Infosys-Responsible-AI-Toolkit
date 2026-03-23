/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { AfterContentInit, ContentChild, Directive, Host, HostListener, Input, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faSort, faSortDown, faSortUp, IconDefinition } from '@fortawesome/free-solid-svg-icons';

import { SortDirective } from './sort.directive';

@Directive({
  selector: '[jhiSortBy]',
})
export class SortByDirective<T> implements AfterContentInit, OnDestroy {
  @Input() jhiSortBy!: T;

  @ContentChild(FaIconComponent, { static: false })
  iconComponent?: FaIconComponent;

  sortIcon = faSort;
  sortAscIcon = faSortUp;
  sortDescIcon = faSortDown;

  private readonly destroy$ = new Subject<void>();

  constructor(@Host() private sort: SortDirective<T>) {
    sort.predicateChange.pipe(takeUntil(this.destroy$)).subscribe(() => this.updateIconDefinition());
    sort.ascendingChange.pipe(takeUntil(this.destroy$)).subscribe(() => this.updateIconDefinition());
  }

  /**
   * * Sort the table by the given predicate.
   * * The predicate is the field name to sort by.
   */
  @HostListener('click')
  onClick(): void {
    if (this.iconComponent) {
      this.sort.sort(this.jhiSortBy);
    }
  }

  /**
   * * Sort the table by the given predicate.
   * * The predicate is the field name to sort by.
   */
  ngAfterContentInit(): void {
    this.updateIconDefinition();
  }

  /**
   * * Sort the table by the given predicate.
   * * The predicate is the field name to sort by.
   */
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * * Sort the table by the given predicate.
   * * The predicate is the field name to sort by.
   */
  private updateIconDefinition(): void {
    if (this.iconComponent) {
      let icon: IconDefinition = this.sortIcon;
      if (this.sort.predicate === this.jhiSortBy) {
        icon = this.sort.ascending ? this.sortAscIcon : this.sortDescIcon;
      }
      this.iconComponent.icon = icon.iconName;
      this.iconComponent.render();
    }
  }
}
