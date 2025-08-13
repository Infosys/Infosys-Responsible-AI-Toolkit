/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { SessionStorageService } from 'ngx-webstorage';

@Injectable({ providedIn: 'root' })
export class StateStorageService {
  private previousUrlKey = 'previousUrl';

  constructor(private sessionStorageService: SessionStorageService) {}

  /**
   * @description This method is used to store the previous URL in the session storage.
   * @param url The URL to be stored.
   */
  storeUrl(url: string): void {
    this.sessionStorageService.store(this.previousUrlKey, url);
  }

  /**
   * @description This method is used to retrieve the previous URL from the session storage.
   * @returns The stored URL or null if not found.
   */
  getUrl(): string | null {
    return this.sessionStorageService.retrieve(this.previousUrlKey) as string | null;
  }

  /**
   * @description This method is used to clear the previous URL from the session storage.
   */
  clearUrl(): void {
    this.sessionStorageService.clear(this.previousUrlKey);
  }
}
