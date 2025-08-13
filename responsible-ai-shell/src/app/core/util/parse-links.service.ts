/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';

/**
 * An utility service for link parsing.
 */
@Injectable({
  providedIn: 'root',
})
export class ParseLinks {
  /**
   * Method to parse the links
   */
  parse(header: string): { [key: string]: number } {
    if (header.length === 0) {
      throw new Error('input must not be of zero length');
    }

    // Split parts by comma
    const parts: string[] = header.split(',');
    const links: { [key: string]: number } = {};

    // Parse each part into a named link
    parts.forEach(p => {
      const section: string[] = p.split(';');

      if (section.length !== 2) {
        throw new Error('section could not be split on ";"');
      }

      const url: string = section[0].replace(/<(.*)>/, '$1').trim();
      const queryString: { [key: string]: string | undefined } = {};

      url.replace(
        new RegExp('([^?=&]+)(=([^&]*))?', 'g'),
        ($0: string, $1: string | undefined, $2: string | undefined, $3: string | undefined) => {
          if ($1 !== undefined) {
            queryString[$1] = $3;
          }
          return $3 ?? '';
        }
      );

      if (queryString.page !== undefined) {
        const name: string = section[1].replace(/rel="(.*)"/, '$1').trim();
        links[name] = parseInt(queryString.page, 10);
      }
    });
    return links;
  }
}
