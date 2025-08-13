/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Directive, HostBinding, HostListener, Input } from '@angular/core';
import { DomSanitizer, SafeStyle } from '@angular/platform-browser';

@Directive({
  selector: '[appImageSelect]',
})
export class ImageSelectDirective {
  @Input() toggle: any = false;
  @Input() color: string = 'rgba(134,38,195,0.3)';

  constructor(private doms: DomSanitizer) {}

  /**
   * Dynamically binds the style of the element based on the toggle state.
   * If `toggle` is true, applies a border and background color.
   * Otherwise, removes the border.
   * @returns A sanitized style string.
   */
  @HostBinding('style') get myStyle(): SafeStyle {
    const style: string =
      this.toggle === true
        ? ` border:3px solid #8626C3;
    background: ${this.color}`
        : 'border: none';
    return this.doms.bypassSecurityTrustStyle(style);
  }

  /**
   * Handles the click event on the element.
   * Toggles the `toggle` state and resets it to false after 7 seconds.
   */
  @HostListener('click') onClick() {
    this.toggle = !this.toggle;
    setTimeout(() => {
      this.toggle = false;
    }, 7000);
  }

  /**
   * Resets the form by clearing the color and toggle state.
   * Logs a message to the console for debugging purposes.
   */
  resetForm() {
    this.color; // Placeholder for resetting color (currently unused).
    this.toggle = undefined; // Clears the toggle state.
    console.log('hello'); // Debugging log.
  }
}
