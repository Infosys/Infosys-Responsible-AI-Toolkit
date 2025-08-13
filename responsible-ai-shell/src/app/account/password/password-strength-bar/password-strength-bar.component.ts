/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ElementRef, Input, Renderer2 } from '@angular/core';

@Component({
  selector: 'jhi-password-strength-bar',
  templateUrl: './password-strength-bar.component.html',
  styleUrls: ['./password-strength-bar.component.scss'],
})
export class PasswordStrengthBarComponent {
  colors = ['#F00', '#F90', '#FF0', '#9F0', '#0F0'];

  constructor(private renderer: Renderer2, private elementRef: ElementRef) {}

  /**
   * @description it measures the strength of entered string
   * @param p 
   * @returns number
   */
  measureStrength(p: string): number {
    let force = 0;
    const regex = /[$-/:-?{-~!"^_`[\]]/g; // "
    const lowerLetters = /[a-z]+/.test(p);
    const upperLetters = /[A-Z]+/.test(p);
    const numbers = /[0-9]+/.test(p);
    const symbols = regex.test(p);

    const flags = [lowerLetters, upperLetters, numbers, symbols];
    const passedMatches = flags.filter((isMatchedFlag: boolean) => isMatchedFlag === true).length;

    force += 2 * p.length + (p.length >= 10 ? 1 : 0);
    force += passedMatches * 10;

    force = p.length <= 6 ? Math.min(force, 10) : force;

    // penalty (poor variety of characters)
    force = passedMatches === 1 ? Math.min(force, 10) : force;
    force = passedMatches === 2 ? Math.min(force, 20) : force;
    force = passedMatches === 3 ? Math.min(force, 40) : force;

    return force;
  }
  
  /**
   * @description to get color based on number
   * @param s 
   * @returns {Id, color}
   */
  getColor(s: number): { idx: number; color: string } {
    let idx = 0;
    if (s > 10) {
      if (s <= 20) {
        idx = 1;
      } else if (s <= 30) {
        idx = 2;
      } else if (s <= 40) {
        idx = 3;
      } else {
        idx = 4;
      }
    }
    return { idx: idx + 1, color: this.colors[idx] };
  }


  @Input()
  set passwordToCheck(password: string) {
    if (password) {
      const c = this.getColor(this.measureStrength(password));
      const element = this.elementRef.nativeElement;
      if (element.className) {
        this.renderer.removeClass(element, element.className);
      }
      const lis = element.getElementsByTagName('li');
      for (let i = 0; i < lis.length; i++) {
        if (i < c.idx) {
          this.renderer.setStyle(lis[i], 'backgroundColor', c.color);
        } else {
          this.renderer.setStyle(lis[i], 'backgroundColor', '#DDD');
        }
      }
    }
  }
}
