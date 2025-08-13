/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import Chart from 'chart.js/auto';
import { MagnifyImageReportComponent } from '../magnify-image-report/magnify-image-report.component';
@Component({
  selector: 'app-image-report-chart',
  templateUrl: './image-report-chart.component.html',
  styleUrls: ['./image-report-chart.component.css']
})
export class ImageReportChartComponent implements OnInit {
  analyze:any;
  public chart: any;
  labelValue:any;
  dataValue:any;
  aesData :any
  image_AlignmentData:any
  public chartRef: any;
  tenent:any
  labelImage_Alignment: any;
  originality: any;
  labeloriginality: any;
  aesLable: any;
  biasData: any;
  labelbias: any;
  tenant:any="Safety"
  aestheticsFlag=false
  knowledgeData: any;
  alignmentValue: any;
  imageType:any
  newData:any

  constructor(public dialogRef: MatDialogRef<ImageReportChartComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,private dialog: MatDialog,
    private modalService: NgbModal
    // @Inject(MAT_DIALOG_DATA) public tenant: any
  ) {}

    // Initializes the component and sets up charts
  ngOnInit(): void {
    console.log("32data=====",this.data)
    console.log("this.data=====",this.data.analyze)
    this.tenant = this.data.tenent
    console.log("this.this.tenant=====",this.tenant)
    this.imageType = this.data.type
    if(this.data.analyze){
      this.analyze = this.data?.analyze;
    }
      // this.dataValue = Object.values(this.analyze.Score.Aesthetics[2]);
    // this.labelValue = Object.keys(this.analyze);
    // this.dataValue = Object.values(this.analyze);
    if(this.tenant=="Safety"){
      console.log("Inside Safety =====")
      this.analyze = this.data?.analyze;
      this.labelValue = Object.keys(this.analyze);
    this.dataValue = Object.values(this.analyze);
    console.log("this.dataValue=====",this.dataValue)
    console.log("this.labelValue=====",this.labelValue)
        this.createChart();
    }
    else if(this.tenant=="Explainability"){
      this.aesData=this.data.analyze.Score.Aesthetics.AestheticsScore
      
      this.originality = this.data.analyze.Score.Originality.Probability
      this.biasData = this.data.analyze.Score.Bias.Gender
      this.labelValue = Object.keys(this.analyze.Score.Aesthetics);
      
      this.labeloriginality = Object.keys(this.analyze.Score.Originality);
      console.log("labelValue::", this.labelValue)
      this.aesLable =this.data.analyze.Score.Aesthetics.Aesthetics
      this.labelbias = Object.keys(this.biasData)
      console.log("this.aesData=====",this.aesData)
      console.log("this.aesLable======= ",this.labelbias)
      if(this.imageType == "generate"){
        this.image_AlignmentData=this.data.analyze.Score.Image_Alignment.Probability
      this.knowledgeData = this.data.analyze.Score.Image_Alignment.KnowledgeAlignment
      this.alignmentValue =this.data.analyze.Score.Image_Alignment.AlignmentValue
      this.labelImage_Alignment = Object.keys(this.analyze.Score.Image_Alignment);
      this.createImage_AlignmentChart() 
      }
        this.createAestheticsChart()
        
        this.createOriginalityChart()
        this.createBiasChart()
    }
  // this.createBiasChart()
  // this.createBarChart()

}

  // Creates a doughnut chart for safety analysis
createChart() { 
  const data = {
    labels: this.labelValue,
    datasets: [
      {
       label: 'Dataset 1',
        data: this.dataValue,
        backgroundColor: [
          'rgb(255, 99, 132)',
                   'rgb(54, 162, 235)',
                   'rgb(255, 205, 86)',
                  'rgb(75, 192, 192)',
                   'rgb(153, 102, 255)'
        ],
      }
    ]
  };
  this.chart = new Chart("MyChart", {
    type: 'doughnut',
  data: data,
  options: {
    
    responsive: true,
    plugins: {
      legend: {
        position: 'right'
      }, 
     
    },
    
  },
  });
}

 // Opens a popup with detailed metric information
openPopup(metric:any){
  if(metric == "Aesthetics"){
     this.newData = {
      analyze: [this.aesData,10],
      label : [this.labelValue[2]],
      score_desc:[this.aesLable],
      description : "Aesthetics involves evaluating various aspects such as composition, coherence with the input text, style consistency, diversity, realism, and subjective appeal"


    }
  }
  else if(metric == "Alignment" ){
    this.newData = {
     analyze: [this.image_AlignmentData,this.image_AlignmentData,35],
     label : ["Alignment","Knowledge"],
     score_desc:[this.knowledgeData,this.alignmentValue],
     
   }
 }
 else if(metric == "originality"){
  this.newData = {
   analyze: [this.originality,1],
   label : [this.labeloriginality[1]],
   score_desc:["Has WaterMark : "+this.data.analyze.Score.Originality.Has_WaterMark]

 }
}
else if(metric == "Bias"){
  this.newData = {
   analyze: [this.biasData.Male_Score,this.biasData.Female_Score,35],
   label : ["Male","Female"],
   score_desc:[this.biasData.GenderBias]

 }
}
  const dialogRef = this.dialog.open(MagnifyImageReportComponent, {
    width: '52vw',
    height: 'calc(100vh - 57px)', // Subtract the height of the navbar
    position: {
      top: '57px', // Position the modal below the navbar
      right: '0'
    },
    backdropClass: 'custom-backdrop',
    data: {
      analyze: this.newData,
      metric:metric

        },
    // tenant:{
    //   tenant: this.tenantarr
    //     }
  });

  dialogRef.afterClosed().subscribe(() => {
  });
  // const modalRef = this.modalService.open(MagnifyImageReportComponent);
  // modalRef.componentInstance.chartData = this.aesData;
}

// Creates a bar chart for aesthetics analysis
createAestheticsChart() { 
  // var ctx = document.getElementById("aesthetics");
  // if (ctx) {
  //   var context = (ctx as HTMLCanvasElement).getContext("2d");
  // }

  const data = {
    labels: [this.labelValue[2]],
    datasets: [
      {
       label:this.aesLable,
        data: [this.aesData,10],
        backgroundColor: [
          'rgba(150, 53, 150, 0.7)',
        ],
        borderColor: [
          
          'rgb(150, 53, 150)'
          
        ],
        borderWidth: 1
      }
    ]
    
  };
  console.log("data=====",data)
  
  
  this.chart = new Chart("aesthetics", {
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

// Creates a bar chart for image alignment analysis
createImage_AlignmentChart() { 
  console.log("this.labelImage_Alignment[0]====",this.labelImage_Alignment)
  // var ctx = document.getElementById("image_Alignment");
  // if (ctx) {
  //   var context = (ctx as HTMLCanvasElement).getContext("2d");
  // }

  const data = {
    
    labels: ["Alignment","Knowledge"],
    datasets: [
      {
       label:this.data.analyze.Score.Image_Alignment.AlignmentValue,
        data: [this.image_AlignmentData,this.image_AlignmentData,35],
        backgroundColor: [
          'rgba(150, 53, 150, 0.7)',
          'rgba(255, 99, 132, 0.7)',
        ],
        borderColor: [
          
          'rgb(150, 53, 150)',
          'rgb(255, 99, 132)'
          
        ],
        borderWidth: 1,
      }
    ]
    
  };
  console.log("data=====",data)
  
  
  this.chart = new Chart("image_Alignment", {
    type: 'bar',
  data: data,
  options: {
    
    responsive: true,
    plugins: {
      legend: {
       labels:{
          boxWidth: 0,
  
        },
        display: false,
        // position: 'top'
      }, 
     
    },
    
  },
  });
}

// Creates a bar chart for originality analysis
createOriginalityChart() { 
  // var ctx = document.getElementById("aesthetics");
  // if (ctx) {
  //   var context = (ctx as HTMLCanvasElement).getContext("2d");
  // }

  const data = {
    labels: [this.labeloriginality[1]],
    datasets: [
      {
       label: "Has WaterMark : "+this.data.analyze.Score.Originality.Has_WaterMark,
        data: [this.originality,1],
        backgroundColor: [
          'rgba(150, 53, 150, 0.7)',
        ],
        borderColor: [
          
          'rgb(150, 53, 150)'
          
        ],
        borderWidth: 1
      }
    ]
    
  };
  console.log("data=====",data)
  
  
  this.chart = new Chart("originality", {
    type: 'bar',
  data: data,
  options: {
    
    responsive: true,
    plugins: {
      legend: {
       labels:{
          boxWidth: 0
        },
        // display: false,
        position: 'top'
      }, 
     
    },
    
  },
  });
}

// Creates a bar chart for originality analysis
createBiasChart() { 
  // var ctx = document.getElementById("bias");
  // if (ctx) {
  //   var context = (ctx as HTMLCanvasElement).getContext("2d");
  // }

  const data = {
    labels: ["Male","Female"],
    datasets: [
      {
       label:this.biasData.GenderBias,
        data: [this.biasData.Male_Score,this.biasData.Female_Score,35],
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
  
  
  this.chart = new Chart("bias", {
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
          stepSize:5
        }
      
      }
    },
    
    
  },
  });
}



// Opens a dialog for aesthetics analysis
openDialogAesthetics(){
  this.aestheticsFlag=true
  this.createAestheticsChart()

  // const dialogRef = this.dialog.open(ImageReportChartComponent, {
  //   width: '52vw',
  //   height: 'calc(100vh - 57px)', // Subtract the height of the navbar
  //   position: {
  //     top: '57px', // Position the modal below the navbar
  //     right: '0'
  //   },
  //   backdropClass: 'custom-backdrop',
  //   data: {
  //     analyze: this.data.analyze,
  //     tenent:"Explainability"
  //       }
  // });

  // dialogRef.afterClosed().subscribe(() => {
  // });
}



// CLOSE MODAL
closeDialog() {
  this.dialogRef.close();
}

// public chartOptions: any = {
//   // Other chart options...
//   plugins: {
//     afterDraw: (chart: any) => {
//       const ctx = chart.ctx;

//       chart.data.datasets.forEach((dataset: any, datasetIndex: number) => {
//         const meta = chart.getDatasetMeta(datasetIndex);

//         meta.data.forEach((bar: any, index: number) => {
//           const data = dataset.data[index];

//           ctx.fillStyle = '#000';
//           ctx.textAlign = 'center';
//           ctx.textBaseline = 'bottom';
//           ctx.font = '12px Arial';

//           ctx.fillText(data, bar.x, bar.y - 5);
//         });
//       });
//     }
//   }
// };

// ngAfterViewInit() {
//   const canvas = document.getElementById('barChart') as HTMLCanvasElement;
//   const ctx = canvas.getContext('2d');
//   if (ctx) {
//     this.chartRef = new Chart(ctx, {
//       type: 'bar',
//       data: this.aesData,
//       options: this.chartOptions
//     });
//   }
// }

// Generates a sample pie chart
genChart(){
  const ctx = document.getElementById('myPieChart') as HTMLCanvasElement;
const data = {
  labels: ['Red', 'Blue', 'Yellow'],
  datasets: [{
    data: [10, 20, 30],
    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56'],
  }],
};

new Chart(ctx, {
  type: 'pie',
  data: data,
});

//   const ctx = document.getElementById("chart-line") as HTMLCanvasElement;
// var myLineChart = new Chart(ctx, {
//     type: 'pie',
//     data: {
//         labels: ["Spring", "Summer", "Fall", "Winter"],
//         datasets: [{
//             data: [1200, 1700, 800, 200],
//             backgroundColor: ["rgba(255, 0, 0, 0.5)", "rgba(100, 255, 0, 0.5)", "rgba(200, 50, 255, 0.5)", "rgba(0, 100, 255, 0.5)"]
//         }]
//     },
//     options: {
//         title: {
//             display: true,
//             text: 'Weather'
//         }
//     }
// });
 }

 // Generates a sample doughnut chart
new(){
  const chartOptions = {
	  animationEnabled: true,
	  title:{
		text: "Project Cost Breakdown"
	  },
	  data: [{
		type: "doughnut",
		yValueFormatString: "#,###.##'%'",
		indexLabel: "{name}",
		dataPoints: [
		  { y: 28, name: "Labour" },
		  { y: 10, name: "Legal" },
		  { y: 20, name: "Production" },
		  { y: 15, name: "License" },
		  { y: 23, name: "Facilities" },
		  { y: 17, name: "Taxes" },
		  { y: 12, name: "Insurance" }
		]
	  }]
	}
}

}
