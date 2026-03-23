/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
/**
 * Angular bootstrap Date adapter
 */
import { Injectable } from '@angular/core';
import { NgbDateAdapter, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap';
import dayjs from 'dayjs';

@Injectable()
export class NgbDateDayjsAdapter extends NgbDateAdapter<dayjs.Dayjs> {

  /**
   * @description Converts a NgbDateStruct to a dayjs date object.
   * @param date - date to be converted to NgbDateStruct
   * @returns a NgbDateStruct object or null if the date is invalid
   */
  fromModel(date: dayjs.Dayjs | null): NgbDateStruct | null {
    if (date && dayjs.isDayjs(date) && date.isValid()) {
      return { year: date.year(), month: date.month() + 1, day: date.date() };
    }
    return null;
  }

  /**
   * @description This method is to convert a NgbDateStruct to a dayjs date object.
   * @param date - date to be converted to NgbDateStruct
   * @returns a NgbDateStruct object or null if the date is invalid
   */
  toModel(date: NgbDateStruct | null): dayjs.Dayjs | null {
    return date ? dayjs(`${date.year}-${date.month}-${date.day}`) : null;
  }
}
