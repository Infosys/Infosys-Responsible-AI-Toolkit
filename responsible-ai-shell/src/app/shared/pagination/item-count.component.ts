/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Input } from '@angular/core';

/**
 * A component that will take care of item count statistics of a pagination.
 */
@Component({
  selector: 'jhi-item-count',
  template: ` <div>Showing {{ first }} - {{ second }} of {{ total }} items.</div> `,
})
export class ItemCountComponent {
  /**
   * @param params  Contains parameters for component:
   *                    page          Current page number
   *                    totalItems    Total number of items
   *                    itemsPerPage  Number of items per page
   */
  @Input() set params(params: { page?: number; totalItems?: number; itemsPerPage?: number }) {
    if (params.page && params.totalItems !== undefined && params.itemsPerPage) {
      this.first = (params.page - 1) * params.itemsPerPage + 1;
      this.second = params.page * params.itemsPerPage < params.totalItems ? params.page * params.itemsPerPage : params.totalItems;
    } else {
      this.first = undefined;
      this.second = undefined;
    }
    this.total = params.totalItems;
  }

  first?: number;
  second?: number;
  total?: number;
}
