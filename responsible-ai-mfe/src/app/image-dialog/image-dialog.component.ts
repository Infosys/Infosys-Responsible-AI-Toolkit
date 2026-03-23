/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA ,MatDialogRef} from '@angular/material/dialog';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-image-dialog',
  templateUrl: './image-dialog.component.html',
  styleUrls: ['./image-dialog.component.css']
})
export class ImageDialogComponent {
  pdfUrl?: SafeResourceUrl;
  videoUrl?: SafeResourceUrl;
  audioUrl?: SafeResourceUrl;
  isPdf: boolean = false;
  isImage: boolean = false;
  isCsv: boolean = false;
  isPlainText: boolean = false;
  isVideo: boolean = false;
  isAudio: boolean = false;
  textContent: string = '';

  constructor(public dialogRef: MatDialogRef<ImageDialogComponent>,@Inject(MAT_DIALOG_DATA) public data: any, private sanitizer: DomSanitizer) {
    console.log('Dialog Data:', this.data);

    if (this.data.pdf && this.data.pdf.startsWith('data:application/pdf;base64,')) {
      this.isPdf = true;
      this.pdfUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.data.pdf);
    } else if (this.data.image && this.data.image.startsWith('data:image/')) {
      this.isImage = true;
    } else if (this.data.csv && this.data.csv.startsWith('data:text/csv;base64,')) {
      this.isCsv = true;
      this.textContent = atob(this.data.csv.split(',')[1]);
    } else if (this.data.plainText && this.data.plainText.startsWith('data:text/plain;base64,')) {
      this.isPlainText = true;
      this.textContent = atob(this.data.plainText.split(',')[1]);
    } else if (this.data.video && this.data.video.startsWith('data:video/')) {
      this.isVideo = true;
      this.videoUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.data.video);
    } else if (this.data.audio && this.data.audio.startsWith('data:audio/')) {
      this.isAudio = true;
      this.audioUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.data.audio);
    } else {
      console.error('Unsupported data type');
    }

    console.log('Formatted PDF Data:', this.data.pdf);
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}