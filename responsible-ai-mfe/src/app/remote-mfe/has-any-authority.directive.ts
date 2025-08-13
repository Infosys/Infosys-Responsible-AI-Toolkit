/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[authHasAnyAuthority]',
})
export class HasAnyAuthorityDirective {
  private authorities!: string | string[];


  constructor(private templateRef: TemplateRef<any>, private viewContainerRef: ViewContainerRef) {}
  @Input()
  set authHasAnyAuthority(value: string | string[]) {
    // Sets the authorities and updates the view
    this.authorities = Array.isArray(value) ? value : [value];
    this.updateView();
  }

  // Updates the view based on the user's role and authorities
  private updateView(): void {
    let role = localStorage.getItem('role'); // Get role from local storage
    if (role) {
      role = role.replace(/"/g, ''); // Remove extra quotes
    }
    const hasAnyAuthority = Array.isArray(this.authorities)
      ? this.authorities.some(authority => authority === role)
      : this.authorities === role;
    console.log('authorities', this.authorities)
    console.log('role', role);
    console.log('hasAnyAuthority', hasAnyAuthority);
    this.viewContainerRef.clear();
    if (hasAnyAuthority) {
      this.viewContainerRef.createEmbeddedView(this.templateRef);
    }
  }
}
