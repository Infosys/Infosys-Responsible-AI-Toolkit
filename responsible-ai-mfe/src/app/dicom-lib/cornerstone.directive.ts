/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Directive, ElementRef, HostListener, OnInit, AfterViewChecked } from '@angular/core';
import * as Hammer from 'hammerjs';
import * as cornerstoneTools from "cornerstone-tools";
import * as cornerstone from "cornerstone-core";
import * as cornerstoneMath from "cornerstone-math";


// declare const cornerstone:any;
// declare const cornerstoneTools:any;
// declare const cornerstoneMath:any;




@Directive({
  selector: '[cornerstone]',
})

export class CornerstoneDirective implements OnInit, AfterViewChecked {

  public element: any;

  public imageList:any[] = [];
  private imageIdList:any[] = [];
  public currentIndex = 0;
  public currentImage: any;
  public patientName = ''; // current image Patient name, do display on the overlay
  public hospital = ''; // current image Institution name, to display on the overlay
  public instanceNumber = ''; // current image Instance #, to display on the overlay

  // cornersTone Tools we use
  private WwwcTool = cornerstoneTools.WwwcTool;
  private PanTool = cornerstoneTools.PanTool;
  private ZoomTool = cornerstoneTools.ZoomTool;
  private ProbeTool = cornerstoneTools.ProbeTool;
  private LengthTool = cornerstoneTools.LengthTool;
  private AngleTool = cornerstoneTools.AngleTool;
  private EllipticalRoiTool = cornerstoneTools.EllipticalRoiTool;
  private RectangleRoiTool = cornerstoneTools.RectangleRoiTool;
  private DragProbeTool = cornerstoneTools.DragProbeTool;
  private ZoomTouchPinchTool = cornerstoneTools.ZoomTouchPinchTool;
  private PanMultiTouchTool = cornerstoneTools.PanMultiTouchTool;
  private StackScrollTool = cornerstoneTools.StackScrollTool;
  private StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool;


  public get windowingValue(): string {
    if (this.isCornerstoneEnabled) {
      let viewport = cornerstone.getViewport(this.element);
      if (this.currentImage && viewport) { return Math.round(viewport.voi.windowWidth) + "/" + Math.round(viewport.voi.windowCenter); }
    }
    return '';
  }

  public get zoomValue(): string {
    if (this.isCornerstoneEnabled) {
      let viewport = cornerstone.getViewport(this.element);
      if (this.currentImage && viewport) { return viewport.scale.toFixed(2); }
    }
    return '';
  }

  private isCornerstoneEnabled = false;

  constructor(private elementRef: ElementRef) {
  }

  @HostListener('window:resize', ['$event'])
  onResize(event:any) {
    if (this.isCornerstoneEnabled) {
      cornerstone.resize(this.element, true);
    }
  }

  @HostListener('wheel', ['$event'])
  onMouseWheel(event:any) {
    event.preventDefault();

    if (this.imageList.length > 0) {
      const delta = Math.max(-1, Math.min(1, (event.wheelDelta || -event.detail)));
      // console.log(event);


      if (delta > 0) {
        this.currentIndex++;
        if (this.currentIndex >= this.imageList.length) {
          this.currentIndex = this.imageList.length - 1;
        }
      } else {

        this.currentIndex--;
        if (this.currentIndex < 0) {
          this.currentIndex = 0;
        }

      }

      this.displayImage(this.imageList[this.currentIndex]);
    }

  }

  ngOnInit() {

    // Retrieve the DOM element itself
    this.element = this.elementRef.nativeElement;

    // now add the Tools we use
    cornerstoneTools.external.cornerstone = cornerstone;
    cornerstoneTools.external.Hammer = Hammer;
    cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
    cornerstoneTools.init({ globalToolSyncEnabled: true });

    cornerstoneTools.addTool(this.WwwcTool);
    cornerstoneTools.addTool(this.PanTool);
    cornerstoneTools.addTool(this.ZoomTool);
    cornerstoneTools.addTool(this.ProbeTool);
    cornerstoneTools.addTool(this.LengthTool);
    cornerstoneTools.addTool(this.AngleTool);
    cornerstoneTools.addTool(this.EllipticalRoiTool);
    cornerstoneTools.addTool(this.RectangleRoiTool);
    cornerstoneTools.addTool(this.DragProbeTool);
    cornerstoneTools.addTool(this.ZoomTouchPinchTool);
    cornerstoneTools.addTool(this.PanMultiTouchTool);
    cornerstoneTools.addTool(this.StackScrollTool);
    cornerstoneTools.addTool(this.StackScrollMouseWheelTool);

    // Enable the element with Cornerstone
    this.resetViewer();
  }

  ngAfterViewChecked() {
  //  if (this.currentImage) cornerstone.resize(this.element, true);
  }

  //
  // reset the viewer, so only this current element is enabled
  //
  public resetViewer() {
    this.disableViewer();
    cornerstone.enable(this.element);
    this.isCornerstoneEnabled = true;
  }

  public disableViewer() {
    this.element = this.elementRef.nativeElement;
    try {
      cornerstone.disable(this.element);
    } finally { }

    this.isCornerstoneEnabled = false;
  }

  public resetImageCache() {
    this.imageList = [];
    this.imageIdList = [];
    this.currentImage = null;
    this.currentIndex = 0;
    this.patientName = '';
    this.hospital = '';
    this.instanceNumber = '';
  }

  public previousImage() {
    if (this.imageList.length > 0) {
      this.currentIndex--;
      if (this.currentIndex < 0) {
        this.currentIndex = 0;
      }
      this.displayImage(this.imageList[this.currentIndex]);
    }

  }

  public nextImage() {
    if (this.imageList.length > 0) {
      this.currentIndex++;
      if (this.currentIndex >= this.imageList.length) {
        this.currentIndex = this.imageList.length - 1;
      }
      this.displayImage(this.imageList[this.currentIndex]);
    }
  }

  public addImageData(imageData: any) {
    console.log("image==",imageData)
    this.element = this.elementRef.nativeElement;
    //if (!this.imageList.filter(img => img.imageId === imageData.imageId).length) {
    this.imageList.push(imageData);
    this.imageIdList.push(imageData.imageId);
    if (this.imageList.length === 1) {
      this.currentIndex = 0;
      this.displayImage(imageData);
    }
    //}

    cornerstone.resize(this.element, true);
  }

  public displayImage(image:any) {
    this.element = this.elementRef.nativeElement;
    const viewport = cornerstone.getDefaultViewportForImage(this.element, image);
    cornerstone.displayImage(this.element, image, viewport);
    this.currentImage = image;
    // Fit the image to the viewport window
    cornerstone.fitToWindow(this.element);
    cornerstone.resize(this.element, true);

    // get image info to display in overlays
    if (image.data.string('x00100010')) this.patientName = image.data.string('x00100010').replace(/\^/g, '');
    this.hospital = image.data.string('x00080080');
    this.instanceNumber = image.data.intString('x00200011') + '/' + image.data.intString('x00200013');

    // Activate mouse clicks, mouse wheel and touch
    // cornerstoneTools.mouseInput.enable(this.element);
    // cornerstoneTools.mouseWheelInput.enable(this.element);
    // //cornerstoneTools.touchInput.enable(this.element);
    // cornerstoneTools.keyboardInput.enable(this.element);

    // Enable all tools we want to use with this element
    cornerstoneTools.setToolActiveForElement(this.element, 'Wwwc', { mouseButtonMask: 1 }, ['Mouse']); // ww/wc is the default tool for left mouse button
    cornerstoneTools.setToolActiveForElement(this.element, 'Pan', { mouseButtonMask: 4 }, ['Mouse']); // pan is the default tool for middle mouse button
    cornerstoneTools.setToolActiveForElement(this.element, 'Zoom', { mouseButtonMask: 2 }, ['Mouse']); // zoom is the default tool for right mouse button

    /*     cornerstoneTools.wwwc.activate(this.element, 1); // ww/wc is the default tool for left mouse button
        cornerstoneTools.pan.activate(this.element, 2); // pan is the default tool for middle mouse button
        cornerstoneTools.zoom.activate(this.element, 4); // zoom is the default tool for right mouse button
        cornerstoneTools.probe.enable(this.element);
        cornerstoneTools.length.enable(this.element);
        cornerstoneTools.angle.enable(this.element);
        cornerstoneTools.simpleAngle.enable(this.element);
        cornerstoneTools.ellipticalRoi.enable(this.element);
        cornerstoneTools.rectangleRoi.enable(this.element);
        cornerstoneTools.wwwcTouchDrag.activate(this.element) // - Drag
        cornerstoneTools.zoomTouchPinch.activate(this.element) // - Pinch
        cornerstoneTools.panMultiTouch.activate(this.element) // - Multi (x2) */

    // Stack tools

    // Define the Stack object
    const stack = {
      currentImageIdIndex: this.currentIndex,
      imageIds: this.imageIdList
    };

    cornerstoneTools.addStackStateManager(this.element, ['playClip']);
    // Add the stack tool state to the enabled element
    cornerstoneTools.addStackStateManager(this.element, ['stack']);
    cornerstoneTools.addToolState(this.element, 'stack', stack);
    // cornerstoneTools.stackScrollWheel.activate(this.element);
    // Enable all tools we want to use with this element
    cornerstoneTools.setToolActiveForElement(this.element, 'StackScroll', {});
    //cornerstoneTools.stackPrefetch.enable(this.element);

  }


  // cornerstone.displayImage(this.element, image);
  // deactivate all tools
  public resetAllTools() {
    cornerstoneTools.setToolDisabledForElement(this.element, 'Wwwc');
    cornerstoneTools.setToolDisabledForElement(this.element, 'Pan');
    cornerstoneTools.setToolDisabledForElement(this.element, 'Zoom');
    cornerstoneTools.setToolDisabledForElement(this.element, 'Probe');
    cornerstoneTools.setToolDisabledForElement(this.element, 'Length');
    cornerstoneTools.setToolDisabledForElement(this.element, 'Angle');
    cornerstoneTools.setToolDisabledForElement(this.element, 'EllipticalRoi');
    cornerstoneTools.setToolDisabledForElement(this.element, 'RectangleRoi');
    cornerstoneTools.setToolDisabledForElement(this.element, 'DragProbe');
    cornerstoneTools.setToolDisabledForElement(this.element, 'ZoomTouchPinch');
    cornerstoneTools.setToolDisabledForElement(this.element, 'PanMultiTouch');
    cornerstoneTools.setToolDisabledForElement(this.element, 'StackScroll');
    cornerstoneTools.setToolDisabledForElement(this.element, 'StackScrollMouseWheel');
  }

}
