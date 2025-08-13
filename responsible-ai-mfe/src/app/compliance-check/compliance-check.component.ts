import { Component, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef, OnInit } from '@angular/core';
import { Chart } from 'chart.js/auto';
import { HttpClient } from '@angular/common/http';
import { PagingConfig } from '../_models/paging-config.model';
import { environment } from 'src/environments/environment';
import { trigger } from '@angular/animations';


@Component({
  selector: 'app-compliance-check',
  templateUrl: './compliance-check.component.html',
  styleUrls: ['./compliance-check.component.css']
})
export class ComplianceCheckComponent implements OnInit {

  euAiChart: any;  // Reference for EU-AI chart
  isoChart: any;

  panelOpenStateEuAi = false;
  panelOpenStateIso = false;

  @ViewChild('fileInput') fileInput!: ElementRef; // Reference to the file input element
  files: File[] = [];
  complianceEuAiPieChart: Chart | null = null;
  complianceIsoPieChart: Chart | null = null;

  fileLoading: boolean = false;
  dataReceived: boolean = false;
  loader: boolean = false;
  isTableCollapsed: boolean = false;
  isGapsCollapsed: boolean = false;
  isRecommendationCollapsed: boolean = false;

  activeChartTab: string = 'ISO';
  activeTableTab: string = 'ISO';
  activeGapsTab: string = 'Critical';
  activeRecommendationTab: string = 'ISO';

  complianceData: any;
  compliance: any;
  recommendations: any;

  avgEuAiScore: any;
  avgIsoScore: any;

  complianceEuAiData: any[] = [];
  EuAiDataKeys: any[] = [];
  complianceIsoData: any[] = [];
  IsoDataKeys: any[] = [];

  complianceGapsCriticalData: any[] = [];
  complianceGapsSignificantData: any[] = [];
  complianceGapsMinorData: any[] = [];

  complianceEuAiRecommendationData: any[] = [];
  EuAiReccKeys: any[] = [];
  selectedEuAiRecommendation: any;
  complianceIsoRecommendationData: any[] = [];
  IsoReccKeys: any[] = [];
  selectedIsoRecommendation: any;

  // paging - EU-AI
  currentEuAiPage: number = 1;
  itemsEuAiPerPage: number = 5;
  totalEuAiItems: number = 0;
  pagingEuAiConfig: PagingConfig = {} as PagingConfig;

  // paging - ISO
  currentIsoPage: number = 1;
  itemsIsoPerPage: number = 5;
  totalIsoItems: number = 0;
  pagingIsoConfig: PagingConfig = {} as PagingConfig;

  // paging - gaps - critical
  currentCriticalPage: number = 1;
  itemsCriticalPerPage: number = 5;
  totalCriticalItems: number = 0;
  pagingCritical: PagingConfig = {} as PagingConfig;

  // paging - gaps - significant
  currentSigPage: number = 1;
  itemsSigPerPage: number = 5;
  totalSigItems: number = 0;
  pagingSig: PagingConfig = {} as PagingConfig;

  // paging - gaps - minor
  currentMinorPage: number = 1;
  itemsMinorPerPage: number = 5;
  totalMinorItems: number = 0;
  pagingMinor: PagingConfig = {} as PagingConfig;

  private complianceCheckUrl: any;
  private ComplianceCompianceResultUrl: any;
  private CompianceRecommondationsUrl: any;

  image1: any;
  image2: any;
  image3: any;
  dynamicImage: string = '';
  loadingInterval: any = null;
  loadingTimeout: any = null;

  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef) {
    this.pagingEuAiConfig = {
      itemsPerPage: this.itemsEuAiPerPage,
      currentPage: this.currentEuAiPage,
      totalItems: this.totalEuAiItems
    };

    this.pagingIsoConfig = {
      itemsPerPage: this.itemsIsoPerPage,
      currentPage: this.currentIsoPage,
      totalItems: this.totalIsoItems
    };

    this.pagingCritical = {
      itemsPerPage: this.itemsCriticalPerPage,
      currentPage: this.currentCriticalPage,
      totalItems: this.totalCriticalItems
    };

    this.pagingSig = {
      itemsPerPage: this.itemsSigPerPage,
      currentPage: this.currentSigPage,
      totalItems: this.totalSigItems
    };

    this.pagingMinor = {
      itemsPerPage: this.itemsMinorPerPage,
      currentPage: this.currentMinorPage,
      totalItems: this.totalMinorItems
    };
  }

    // Initializes the component and sets up API endpoints
  ngOnInit() {
    let ip_port: any;
    ip_port = this.getLocalStoreApi();
    this.setApilist(ip_port);

    this.image1 = environment.imagePathurl + '/assets/loader-images/loader1.gif';
    this.image2 = environment.imagePathurl + '/assets/loader-images/loader2.gif';
    this.image3 = environment.imagePathurl + '/assets/loader-images/loader3.gif';
    this.dynamicImage = this.image1; // Initialize with the first image
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if (res != null) {
        return ip_port = JSON.parse(res)
      }
    }
  }

  // sets the API list URLs
  setApilist(ip_port: any) {
    this.complianceCheckUrl = ip_port.result.Compliance + ip_port.result.ComplianceUpload;
    this.ComplianceCompianceResultUrl = ip_port.result.Compliance + ip_port.result.ComplianceCompianceResult;
    this.CompianceRecommondationsUrl = ip_port.result.Compliance + ip_port.result.CompianceRecommondations;
  }

  // Handles tab change for charts
  onChartTab(tab: string): void {
    this.activeChartTab = tab;
    // Trigger change detection manually
    this.cdRef.detectChanges();
    if (tab === 'EU-AI') {
      console.log('EU-AI');
      this.destroyCharts();  // Destroy any existing chart
      this.renderEuAiPieChart();  // Render EU-AI chart
    } else if (tab === 'ISO') {
      console.log('ISO');
      this.destroyCharts();  // Destroy any existing chart
      this.renderIsoPieChart();  // Render ISO chart
    }
  }

  // Destroy existing charts to prevent memory leaks and multiple chart instances
  destroyCharts(): void {
    if (this.euAiChart) {
      this.euAiChart.destroy();
      this.euAiChart = null;
    }
    if (this.isoChart) {
      this.isoChart.destroy();
      this.isoChart = null;
    }
  }

  onChangeTab(tab: string) {
    this.activeTableTab = tab;
  }

  onChangeGapsTab(tab: string) {
    this.activeGapsTab = tab;
  }

   // Handles tab change for recommendations
  onChangeRecommendationTab(tab: string) {
    this.activeRecommendationTab = tab;
  }

  // Handles pagination for EU-AI table
  onTableEuAiChange(event: any) {
    this.currentEuAiPage = event;
    this.pagingEuAiConfig.currentPage = event;
    this.pagingEuAiConfig.totalItems = this.EuAiDataKeys.length;
  }

  // Handles pagination for ISO table
  onTableIsoChange(event: any) {
    this.currentIsoPage = event;
    this.pagingIsoConfig.currentPage = event;
    this.pagingIsoConfig.totalItems = this.IsoDataKeys.length;
  }

  // Handles pagination for critical gaps
  onTableCriticalChange(ev: any) {
    this.currentCriticalPage = ev;
    this.pagingCritical.currentPage = ev;
    this.pagingCritical.totalItems = this.complianceGapsCriticalData.length;
  }

  // Handles pagination for significant gaps
  onTableSignificantChange(ev: any) {
    this.currentCriticalPage = ev;
    this.pagingCritical.currentPage = ev;
    this.pagingCritical.totalItems = this.complianceGapsSignificantData.length;
  }

  onTableMinorChange(ev: any) {
    this.currentCriticalPage = ev;
    this.pagingCritical.currentPage = ev;
    this.pagingCritical.totalItems = this.complianceGapsMinorData.length;
  }

  // Handles file input change and validates files
  onFileChange(event: any) {
    const selectedFiles = event.target.files;
    const validFiles: File[] = [];
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
      'application/rtf',
      'application/zip',
      'text/csv',
      'application/json',
      'text/plain',
      'application/rtf'
    ];
    const maxFileSizeMB = 20;

    for (const file of selectedFiles) {
      if (allowedTypes.includes(file.type) || file.name.endsWith('.zip') || file.name.endsWith('.rtf') || file.name.endsWith('.txt')) {
        if (file.size / (1024 * 1024) <= maxFileSizeMB) {
          validFiles.push(file);
        } else {
          alert(`File ${file.name} exceeds the maximum size of ${maxFileSizeMB} MB.`);
        }
      } else {
        alert(`File type not supported: ${file.name}`);
      }
    }

    this.files = [...this.files, ...validFiles]; // Append valid files to the existing list
    this.fileInput.nativeElement.value = ''; // Reset the file input value
  }

  // Removes a file from the list
  removeFile(index: number) {
    this.files.splice(index, 1);
  }

  // Fetches compliance results for a document
  fetchComplianceResult(Document_ID: any): void {
    const url = `${this.ComplianceCompianceResultUrl}${Document_ID}`;
    const headers = { 'accept': 'application/json' };

    this.http.post(url, {}, { headers }).subscribe(
      (response: any) => {
        console.log('Compliance Result:', response);
        // Handle the response here
        this.triggerLoading('end');
        this.dataReceived = true;

        setTimeout(() => {
          this.renderIsoPieChart(); // Re-render EU-AI chart after data is loaded
          // Trigger change detection after data is received
          this.cdRef.detectChanges();
        }, 2000);

        this.complianceData = response.compliance_result;

        //Compliance Summary

        this.compliance = response.compliance_result.compliance;


        // Compliance - overall status
        // this.avgEuAiScore = Math.round(this.complianceData?.compliance_eu_score * 100);
        // this.avgIsoScore = Math.round(this.complianceData?.compliance_iso_score * 100);
        this.avgEuAiScore = this.complianceData?.compliance_eu_score;
        this.avgIsoScore = this.complianceData?.compliance_iso_score;

        // Compliance - Status mapping
        this.complianceEuAiData = this.complianceData.eu_scores;
        this.EuAiDataKeys = Object.keys(this.complianceEuAiData);

        this.complianceIsoData = this.complianceData.iso_scores;
        this.IsoDataKeys = Object.keys(this.complianceIsoData);

        // Compliance - Gaps mapping
        this.complianceGapsCriticalData = this.complianceData.gaps.critical.map((item: any) => ({
          ...item,
          score: Math.round(item.score * 100) // Multiply by 100 and round off
        }));
        this.complianceGapsSignificantData = this.complianceData.gaps.significant.map((item: any) => ({
          ...item,
          score: Math.round(item.score * 100) // Multiply by 100 and round off
        }));
        this.complianceGapsMinorData = this.complianceData.gaps.minor.map((item: any) => ({
          ...item,
          score: Math.round(item.score * 100) // Multiply by 100 and round off
        }));

        // Compliance - Recommendation mapping
        this.complianceEuAiRecommendationData = this.complianceData.recommendations.eu_ai_act;
        this.EuAiReccKeys = Object.keys(this.complianceEuAiRecommendationData);

        this.complianceIsoRecommendationData = this.complianceData.recommendations.iso_controls;
        this.IsoReccKeys = Object.keys(this.complianceIsoRecommendationData);

        this.pagingEuAiConfig.totalItems = this.EuAiDataKeys.length;
        this.onTableEuAiChange(1);
        this.pagingIsoConfig.totalItems = this.IsoDataKeys.length;
        this.onTableIsoChange(1);
        this.pagingCritical.totalItems = this.complianceGapsCriticalData.length;
        this.onTableCriticalChange(1);
        this.pagingSig.totalItems = this.complianceGapsSignificantData.length;
        this.onTableSignificantChange(1);
        this.pagingMinor.totalItems = this.complianceGapsMinorData.length;
        this.onTableMinorChange(1);
      },
      (error) => {
        console.error('Error fetching compliance result:', error);
        this.triggerLoading('end');
      }
    );
  }
  
  // Fetches compliance recommendations for a document
  fetchComplianceRecommendations(Document_ID: string): void {
    const url = `${this.CompianceRecommondationsUrl}${Document_ID}`;
    const headers = { 'accept': 'application/json' };
  
    this.http.post(url, {}, { headers }).subscribe(
      (response: any) => {
        console.log('Compliance Recommendations:', response);
  
        // Handle the response
        this.recommendations = response.recommendations;
        this.loader = false; // Stop the loader
  
        // Check if the status is "completed"
        if (response.recommendations.status === 'completed') {
          console.log('Recommendations fetching completed.');
          
        } else {
          console.log('Recommendations not yet completed. Retrying in 3 seconds...');
          setTimeout(() => {
            this.fetchComplianceRecommendations(Document_ID); // Recursive call
          }, 3000); // Retry after 3 seconds
        }
      },
      (error) => {
        console.error('Error fetching compliance recommendations:', error);
        alert('Failed to fetch compliance recommendations.');
        this.loader = false; // Stop the loader in case of an error
      }
    );
  }

   // Submits the uploaded files for compliance check
  submit() {
    if (this.files.length === 0) {
      alert('No files to upload');
      return;
    }

    const formData = new FormData();
    this.files.forEach((file, index) => {
      formData.append('files', file);
    });
    formData.append('document_type', 'policy');

    this.triggerLoading('start');

    // Dummy API call
    this.http.post(this.complianceCheckUrl, formData).subscribe((response: any) => {
      // Pass the Document_ID to fetchComplianceResult
      this.fetchComplianceResult(response.Document_ID)
      this.fetchComplianceRecommendations(response.Document_ID)

    },
      (error) => {
        console.error('Upload failed', error);
        alert('Failed to upload files.');
        this.triggerLoading('end');
      });
  }

  // Triggers the loading animation
  triggerLoading(action: string) {
    if (action === 'start') {
      this.fileLoading = true;

      let index = 0;
      this.dynamicImage = this.image1; // Initialize with the first image

      // Start looping through images
      this.loadingInterval = setInterval(() => {
        index = (index + 1) % 3; // Cycle through 0, 1, 2
        this.dynamicImage = [this.image1, this.image2, this.image3][index];
      }, 30000); // Change image every 30 seconds

      // Stop the loop after 90 seconds and pause at loader3
      this.loadingTimeout = setTimeout(() => {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
        this.dynamicImage = this.image3; // Pause at loader3
      }, 90000); // 90 seconds
    }

    if (action === 'end') {
      this.fileLoading = false;

      // Stop the image loop
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
      }

      // Clear the timeout
      if (this.loadingTimeout) {
        clearTimeout(this.loadingTimeout);
        this.loadingTimeout = null;
      }
    }

  }

  // Resets all data and clears the form
  resetAll() {
    this.files = [];
    this.fileInput.nativeElement.value = ''; // Reset the file input value
    this.fileLoading = false;
    this.dataReceived = false;
    this.complianceData = null;
  }

  // Renders the EU-AI compliance pie chart
  renderEuAiPieChart(): void {
    const canvas = document.getElementById('complianceEuAiPieChart') as HTMLCanvasElement;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Extract compliance.eu data
        const euData = this.compliance.eu;
        const totalScore = euData.compliant+ euData.partial+ euData.missing; // Total score to normalize
        const compliant = (euData.compliant / totalScore) * 100;
        const partial = (euData.partial / totalScore) * 100;
        const missing = (euData.missing / totalScore) * 100;

        // Destroy the existing chart if it exists
        if (this.euAiChart) {
          this.euAiChart.destroy();
        }

        // Create the pie chart
        this.euAiChart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: ['Fully Compliant', 'Partial Compliant', 'Non Compliant'],
            datasets: [
              {
                label: 'Compliance EU-AI Scores',
                data: [compliant, partial, missing],
                backgroundColor: [
                  '#8bc34a', // Light Green for Compliant
                  '#ffc107', // Amber for Partial
                  '#f44336', // Red for Missing
                ],
                borderColor: '#ffffff',
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const label = context.label || '';
                    const value = Number(context.raw) || 0; // Ensure value is a number
                    return `${label}: ${value.toFixed(2)}%`;
                  },
                },
              },
            },
          },
        });
      }
    }
  }

  // Renders the ISO compliance pie chart
  renderIsoPieChart(): void {
    const canvas = document.getElementById('complianceIsoPieChart') as HTMLCanvasElement;
    if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
            // Extract compliance.iso data
            const isoData = this.compliance.iso;
            const totalScore = isoData.compliant+ isoData.partial +isoData.missing ; // Total score to normalize
            const compliant = (isoData.compliant / totalScore) * 100;
            const partial = (isoData.partial / totalScore) * 100;
            const missing = (isoData.missing / totalScore) * 100;

            // Destroy the existing chart if it exists
            if (this.isoChart) {
                this.isoChart.destroy();
            }

            // Create the pie chart
            this.isoChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Fully Compliant', 'Partial Compliant', 'Non Compliant'],
                    datasets: [
                        {
                            label: 'Compliance ISO Scores',
                            data: [compliant, partial, missing],
                            backgroundColor: [
                                '#8bc34a', // Light Green for Compliant
                                '#ffc107', // Amber for Partial
                                '#f44336', // Red for Missing
                            ],
                            borderColor: '#ffffff',
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.label || '';
                                    const value = Number(context.raw) || 0; // Ensure value is a number
                                    return `${label}: ${value.toFixed(2)}%`;
                                },
                            },
                        },
                    },
                },
            });
        }
    }
}

// Renders the CSS class for priority levels
  getPriorityClass(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'low':
        return 'priority-low';
      case 'medium':
        return 'priority-medium';
      case 'high':
        return 'priority-high';
      default:
        return '';
    }
  }

  // Returns the CSS class for border based on priority
  getBorderClass(priority: string): string {
    switch (priority.toLowerCase()) {
      case 'low':
        return 'card-low';
      case 'medium':
        return 'card-medium';
      case 'high':
        return 'card-high';
      default:
        return '';
    }
  }

  // Returns the severity level as a string
  getSeverity(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'low':
        return 'low';
      case 'medium':
        return 'medium';
      case 'high':
        return 'high';
      default:
        return '';
    }
  }

}