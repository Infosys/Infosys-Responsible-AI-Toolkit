/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Directive, ElementRef, OnInit, Input, AfterViewChecked } from '@angular/core';


declare const cornerstone:any;


@Directive({
  selector: '[thumbnail]',
})

export class ThumbnailDirective implements OnInit, AfterViewChecked {

  @Input() public imageData: any;

  public element: any;

  constructor(private elementRef: ElementRef) {
  }

  ngOnInit() {
 // Retrieve the DOM element itself
    this.element = this.elementRef.nativeElement;

    // Enable the element with Cornerstone
    cornerstone.enable(this.element);
    this.setImageData(this.imageData);
  }

  ngAfterViewChecked() {
    this.refresh();
  }

  public refresh() {
    this.setImageData(this.imageData);
  }

  public setImageData(image:any) {
    this.imageData = image;
    if (this.imageData && this.element) {
      const viewport = cornerstone.getDefaultViewportForImage(this.element, this.imageData);
      cornerstone.displayImage(this.element, this.imageData, viewport);
      // Fit the image to the viewport window
      cornerstone.fitToWindow(this.element);
      cornerstone.resize(this.element, true);
    }

  }
}
