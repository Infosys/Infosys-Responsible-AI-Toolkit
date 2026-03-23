/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Directive, EventEmitter, Input, Output } from '@angular/core';

@Directive({
  selector: '[jhiSort]',
})
export class SortDirective<T> {
  @Input()
  /**
   * The predicate to sort by.
   * The predicate is the field name to sort by.
   */
  get predicate(): T | undefined {
    return this._predicate;
  }

  /**
   * The predicate to sort by.
   * The predicate is the field name to sort by.
   */
  set predicate(predicate: T | undefined) {
    this._predicate = predicate;
    this.predicateChange.emit(predicate);
  }

  /**
   * The ascending order to sort by.
   * The ascending order is true for ascending and false for descending.
   */
  @Input()
  get ascending(): boolean | undefined {
    return this._ascending;
  }

  /**
   * The ascending order to sort by.
   * The ascending order is true for ascending and false for descending.
   */
  set ascending(ascending: boolean | undefined) {
    this._ascending = ascending;
    this.ascendingChange.emit(ascending);
  }

  @Output() predicateChange = new EventEmitter<T>();
  @Output() ascendingChange = new EventEmitter<boolean>();
  @Output() sortChange = new EventEmitter<{ predicate: T; ascending: boolean }>();

  private _predicate?: T;
  private _ascending?: boolean;

  /**
   * @param field The field to sort by.
   * The field is the name of the field to sort by.
   */
  sort(field: T): void {
    this.ascending = field !== this.predicate ? true : !this.ascending;
    this.predicate = field;
    this.predicateChange.emit(field);
    this.ascendingChange.emit(this.ascending);
    this.sortChange.emit({ predicate: this.predicate, ascending: this.ascending });
  }
}
