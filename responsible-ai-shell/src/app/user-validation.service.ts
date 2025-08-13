/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserValidationService {
     
  /**
   * Validates if the given email is in a proper format.
   * @param email - The email address to validate.
   * @returns true if the email matches the pattern, false otherwise.
   */
  isValidEmail(email: any) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
  }

  /**
   * Validates if the given name contains only alphabets and spaces.
   * @param name - The name to validate.
   * @returns true if the name matches the pattern, false otherwise.
   */
  isValidName(name: any) {
    const namePattern = /^[a-zA-Z\s]+$/;
    return namePattern.test(name);
  }

  /**
   * Validates if the given text description contains only valid characters.
   * Allowed characters include alphanumeric, spaces, and special characters.
   * @param textDesc - The text description to validate.
   * @returns true if the text description matches the pattern, false otherwise.
   */
  validateTextDesc(textDesc: string): boolean {
    const regex = /^[a-zA-Z0-9\s!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]*$/;
    return regex.test(textDesc);
  }
      
}