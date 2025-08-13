/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, ViewChild, OnInit, Input, ViewChildren } from '@angular/core';
import { CornerstoneDirective } from './cornerstone.directive';
import { ThumbnailDirective } from './thumbnail.directive';
import * as cornerstoneTools from "cornerstone-tools";
import * as cornerstone from "cornerstone-core";


// declare const cornerstone:any;
// declare const cornerstoneTools:any;

@Component({
  selector: 'dicom-viewer',
  templateUrl: './dicom-viewer.component.html',
  styleUrls: ['./dicom-viewer.component.css']
})
export class DICOMViewerComponent implements OnInit {
  

  @Input() public enableViewerTools = true; // enable viewer tools
  @Input() public enablePlayTools = false; // enable Play Clip tools
  @Input() public downloadImagesURL = '' // download images URL
  @Input() public maxImagesToLoad = 20; // limit for the automatic loading of study images

  public seriesList:any[]= []; // list of series on the images being displayed
  public currentSeriesIndex = 0;
  public currentSeries: any = {};
  public imageCount = 0; // total image count being viewed

  // control enable/disable image scroll buttons
  public get hidePreviousImage(): any { return { color: (this.viewPort.currentIndex < 1) ? 'black' : 'white' }; }
  public get hideNextImage(): any { return { color: (this.viewPort.currentIndex >= (this.imageCount - 1)) ? 'black' : 'white' }; }

  // control message for more images to load
  public get moreImagestoLoad(): string {
    if (this.loadedImages.length < this.imageIdList.length && !this.loadingImages) { // are there any more images to load?
      const imagesToLoad = (this.maxImagesToLoad <= 0) ? (this.imageIdList.length - this.loadedImages.length) : Math.min(this.maxImagesToLoad, this.imageIdList.length - this.loadedImages.length);
      return imagesToLoad.toString();
    } else return '';
  }

  // control exhibition of a loading images progress indicator
  public loadingImages = false;
  public get showProgress(): any { return { display: (this.loadingImages) ? 'inline-block' : 'none' } };

  @ViewChild(CornerstoneDirective, { static: true }) viewPort!: CornerstoneDirective; // the main cornertone view port
  @ViewChildren(ThumbnailDirective) thumbnails!: Array<ThumbnailDirective>;

  public loadedImages:any[] = [];
  public imageIdList: any[]=[];
  private element: any;
  private targetImageCount = 0;

  constructor() { }

  ngOnInit() {
    this.element = this.viewPort.element;
  }

  /**
   * Load dicom images for display
   *
   * @param imageIdList list of imageIds to load and display
   */
  loadStudyImages(imageIdList: Array<any>) {
    this.element = this.viewPort.element;
    this.imageIdList = imageIdList;
    this.viewPort.resetViewer();
    this.viewPort.resetImageCache(); // clean up image cache
    this.seriesList = []; // start a new series list
    this.currentSeriesIndex = 0; // always display first series
    this.loadedImages = []; // reset list of images already loaded

    //
    // loop thru all imageIds, load and cache them for exhibition (up the the maximum limit defined)
    //
    const maxImages = (this.maxImagesToLoad <= 0) ? imageIdList.length : Math.min(this.maxImagesToLoad, imageIdList.length);
    this.loadingImages = true; // activate progress indicator
    this.targetImageCount = maxImages;
    for (let index = 0; index < maxImages; index++) {
      const imageId = imageIdList[index];
      cornerstone.loadAndCacheImage(imageId).then((imageData:any) => { this.imageLoaded(imageData) });
    }

  }

  /**
   * Load the next batch of images
   */
  public loadMoreImages() {
    this.element = this.viewPort.element;
    //
    // loop thru all imageIds, load and cache them for exhibition (up the the maximum limit defined)
    //
    const maxImages = (this.maxImagesToLoad <= 0) ? (this.imageIdList.length - this.loadedImages.length) : Math.min(this.maxImagesToLoad, this.imageIdList.length - this.loadedImages.length);
    this.loadingImages = true; // activate progress indicator
    this.targetImageCount += maxImages;
    let nextImageIndex = this.loadedImages.length;
    for (let index = 0; index < maxImages; index++) {
      const imageId = this.imageIdList[nextImageIndex++];
      cornerstone.loadAndCacheImage(imageId)
        .then((imageData:any) => { this.imageLoaded(imageData) })
        .catch((err:any) => { this.targetImageCount--; });
    }

  }

  /**
   *
   * @param imageData the dicom image data
   */
  public imageLoaded(imageData:any) {
    //console.log(imageData.imageId)
    // build list of series in all loadded images
    const series = {
      studyID: imageData.data.string('x0020000d'),
      seriesID: imageData.data.string('x0020000e'),
      seriesNumber: imageData.data.intString('x00200011'),
      studyDescription: imageData.data.string('x00081030'),
      seriesDescription: imageData.data.string('x0008103e'),
      imageCount: 1,
      imageList: [imageData]
    }
    // if this is a new series, add it to the list
    let seriesIndex = this.seriesList.findIndex((item:any) => item.seriesID === series.seriesID);
    if (seriesIndex < 0) {
      seriesIndex = this.seriesList.length;
      this.seriesList.push(series);
      this.seriesList.sort((a, b) => {
        if (a.seriesNumber > b.seriesNumber) return 1;
        if (a.seriesNumber < b.seriesNumber) return -1;
        return 0;
      })
    } else {
      let seriesItem = this.seriesList[seriesIndex];
      seriesItem.imageCount++;
      seriesItem.imageList.push(imageData);
      seriesItem.imageList.sort((a:any, b:any) => {
        if (a.data.intString('x00200013') > b.data.intString('x00200013')) return 1;
        if (a.data.intString('x00200013') < b.data.intString('x00200013')) return -1;
        return 0;
      })
    }

    this.loadedImages.push(imageData); // save to images loaded

    if (seriesIndex === this.currentSeriesIndex) {
      this.currentSeries = this.seriesList[seriesIndex];
      this.imageCount = this.currentSeries.imageCount; // get total image count
      this.viewPort.addImageData(imageData);
      this.showSeries(this.currentSeriesIndex)
    }

    if (this.loadedImages.length >= this.targetImageCount) { // did we finish loading images?
      this.loadingImages = false; // deactivate progress indicator
    }

  }

  // Displays the selected series
  public showSeries(index:any) {
           this.resetAllTools();
    this.currentSeriesIndex = index;
    this.currentSeries = this.seriesList[index];
    this.imageCount = this.currentSeries.imageCount; // get total image count
    this.viewPort.resetImageCache(); // clean up image cache
    //        this.loadingImages = true; // activate progress indicator
    for (let i = 0; i < this.currentSeries.imageList.length; i++) {
      const imageData = this.currentSeries.imageList[i];
      this.viewPort.addImageData(imageData);
    }
    //        this.loadingImages = false; // de-activate progress indicator
  }

  // Saves the current image as a file
  public saveAs() {
    cornerstoneTools.saveAs(this.element, "teste.jpg")
  }

  /**
   * Image scroll methods
   */
  public nextImage() {
    if (this.viewPort.currentIndex < this.imageCount) {
      this.viewPort.nextImage();
    }
  }

  public previousImage() {
    if (this.viewPort.currentIndex > 0) {
      this.viewPort.previousImage();
    }
  }

  /**
   * Methods to activate/deactivate viewer tools
   */

  // deactivate all tools
  public resetAllTools() {
    if (this.imageCount > 0) {
      this.viewPort.resetAllTools()
      this.stopClip();
    }
  }

  // activate windowing
  public enableWindowing() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.wwwc.activate(this.element, 1);
      // cornerstoneTools.wwwcTouchDrag.activate(this.element);
      cornerstoneTools.setToolActiveForElement(this.element, 'Wwwc', { mouseButtonMask: 1 }, ['Mouse']);

    }
  }

  // activate zoom
  public enableZoom() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.zoom.activate(this.element, 5); // 5 is right mouse button and left mouse button
      // cornerstoneTools.zoomTouchDrag.activate(this.element);
      cornerstoneTools.setToolActiveForElement(this.element, 'Zoom', { mouseButtonMask: 1 }, ['Mouse']); // zoom left mouse
      // cornerstoneTools.setToolActiveForElement(this.element, 'ZoomTouchPinch', { }, ['Mouse']);
      cornerstoneTools.setToolActiveForElement(this.element, 'Pan', { mouseButtonMask: 2 }, ['Mouse']); // pan right mouse

    }
  }

  // activate pan
  public enablePan() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.pan.activate(this.element, 3); // 3 is middle mouse button and left mouse button
      // cornerstoneTools.panTouchDrag.activate(this.element);
      cornerstoneTools.setToolActiveForElement(this.element, 'Pan', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate image scroll
  public enableScroll() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.stackScroll.activate(this.element, 1);
      // cornerstoneTools.stackScrollTouchDrag.activate(this.element);
      // cornerstoneTools.stackScrollKeyboard.activate(this.element);
      cornerstoneTools.setToolActiveForElement(this.element, 'StackScroll', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate length measurement
  public enableLength() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.length.activate(this.element, 1);
      cornerstoneTools.setToolActiveForElement(this.element, 'Length', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate angle measurement
  public enableAngle() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.simpleAngle.activate(this.element, 1);
      cornerstoneTools.setToolActiveForElement(this.element, 'Angle', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate pixel probe
  public enableProbe() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.probe.activate(this.element, 1);
      cornerstoneTools.setToolActiveForElement(this.element, 'Probe', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate Elliptical ROI
  public enableElliptical() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.ellipticalRoi.activate(this.element, 1);
      cornerstoneTools.setToolActiveForElement(this.element, 'EllipticalRoi', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // activate Rectangle ROI
  public enableRectangle() {
    if (this.imageCount > 0) {
      this.resetAllTools();
      // cornerstoneTools.rectangleRoi.activate(this.element, 1);
      cornerstoneTools.setToolActiveForElement(this.element, 'RectangleRoi', { mouseButtonMask: 1 }, ['Mouse']);
    }
  }

  // Play Clip
  public playClip() {
    if (this.imageCount > 0) {
      let frameRate = 10;
      let stackState = cornerstoneTools.getToolState(this.element, 'stack');
      if (stackState) {
        frameRate = stackState.data[0].frameRate;
        // Play at a default 10 FPS if the framerate is not specified
        if (frameRate === undefined || frameRate === null || frameRate === 0) {
          frameRate = 10;
        }
      }
      cornerstoneTools.playClip(this.element, frameRate);
    }
  }

  // Stop Clip
  public stopClip() {
    cornerstoneTools.stopClip(this.element);
  }

  // invert image
  public invertImage() {
    if (this.imageCount > 0) {
      let viewport = cornerstone.getViewport(this.element);
      // Toggle invert
      if (viewport.invert === true) {
        viewport.invert = false;
      } else {
        viewport.invert = true;
      }
      cornerstone.setViewport(this.element, viewport);
    }
  }

  // reset image
  public resetImage() {
    // console.log("Inside reste button")
    if (this.imageCount > 0) {
      // console.log("number==",this.imageCount)
      let toolStateManager = cornerstoneTools.getElementToolStateManager(this.element);
      // Note that this only works on ImageId-specific tool state managers (for now)
      // toolStateManager.clear(this.element);
      cornerstoneTools.clearToolState(this.element, "Length");
      cornerstoneTools.clearToolState(this.element, "Angle");
      // cornerstoneTools.clearToolState(this.element, "simpleAngle");
      cornerstoneTools.clearToolState(this.element, "Probe");
      cornerstoneTools.clearToolState(this.element, "EllipticalRoi");
      cornerstoneTools.clearToolState(this.element, "RectangleRoi");
      cornerstone.updateImage(this.element);
      // console.log("elem==",this.element)
      this.resetAllTools();
    }
  }

  public clearImage() {
    this.viewPort.resetViewer();
    this.viewPort.resetImageCache();
    this.seriesList = []; // list of series on the images being displayed
    this.currentSeriesIndex = 0;
    this.currentSeries = {};
    this.imageCount = 0; // total image count being viewed

  }
}
