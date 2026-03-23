/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-magnify-image-report',
  templateUrl: './magnify-image-report.component.html',
  styleUrls: ['./magnify-image-report.component.css']
})
export class MagnifyImageReportComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<MagnifyImageReportComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,private dialog: MatDialog,
    
    // @Inject(MAT_DIALOG_DATA) public tenant: any
  ) {}
  chartData: any;
  public chart: any;
  desc :any
  metric:any

  // Initializes the component and sets up the chart
  ngOnInit(): void{
    console.log("this.data=====",this.data)
    this.desc = this.data.analyze.description
    this.metric = this.data.metric
    console.log("this.metric======",this.metric)
    this.openChart();
  }

// Creates and displays the chart
  openChart() {
    const data = {
      labels: this.data.analyze.label,
      datasets: [
        {
         label:this.data.analyze.score_desc[0],
          data: this.data.analyze.analyze,
          backgroundColor: [
            'rgba(150, 53, 150, 0.7)',
            'rgba(255, 99, 132, 0.7)',
          ],
          borderColor: [
            
            'rgb(150, 53, 150)',
            'rgb(255, 99, 132)'
            
          ],
          borderWidth: 1
        }
      ]
      
    };
    console.log("data=====",data)
    
    
    this.chart = new Chart("aestheticsMagnify", {
      type: 'bar',
    data: data,
    options: {
      
      responsive: true,
      plugins: {
        
        legend: {
          // display: false,
          labels:{
            boxWidth: 0
          },
          
          position: 'top'
        }, 
        
       
      },
      scales: {
        y:{
          beginAtZero: true,
          ticks:{
            stepSize:2
          }
        
        }
      },
      
      
    },
    });
  }

// Closes the dialog
  closeDialog() {
    this.dialogRef.close();
  }

}
