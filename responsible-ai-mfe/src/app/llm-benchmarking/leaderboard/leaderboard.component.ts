/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { urlList} from 'src/app/urlList';
@Component({
  selector: 'app-leaderboard',
  templateUrl: './leaderboard.component.html',
  styleUrls: ['./leaderboard.component.css']
})
export class LeaderboardComponent {
  isLoadingTable = true;
  LeaderboardLLMendpoint: any = '';
  trustllm_getScores_explain: any = '';
  constructor(
    public https: HttpClient,
    private _snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef,
    // private logger: NGXLogger
  ) 
  { 
    this.anotherActiveTable = "Mathematical&Reasoning"   
  }

// Initializes the component and sets up API calls
  ngOnInit(): void {
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
      if(res != null){
      this.ip_port = JSON.parse(res)
      }
    }
    this.securityLLM_getLeaderBoard = this.ip_port.result.Security_llm + this.ip_port.result.SecurityLLM_getLeaderboard;
    this.securityLLM_availableDatasets = this.ip_port.result.Security_llm + this.ip_port.result.SecurityLLM_availableDataSets;
    this.securityLLMFairness_leaderboard = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.SecurityLLMF;
    this.externalRobustnessScore = this.ip_port.result.Security_llm + this.ip_port.result.SecurityLLM_ExternalRobustScore;
    this.externalAttackScore = this.ip_port.result.Security_llm + this.ip_port.result.SecurityLLM_ExternalAttackScore;
    this.LLMleaderboardPrivacy = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.SecurityLLMPrivacyLScore;
    this.LLMleaderboardSafety = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.SecurityLLMSafetyLScore;
    this.LLMLeaderboardEthics = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.SecurityLLMEthicsLScore;
    this.LLMLeaderboardTruthfullness = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.SecurityLLMTruthfullnessLScore;
    this.LeaderboardLLMendpoint = this.ip_port.result.SecurityLLMLeaderboard + this.ip_port.result.LeaderboardEndpoint;
    this.trustllm_getScores_explain = this.ip_port.result.Security_llm + this.ip_port.result.trustllm_getScores_explain;
    this.getFairnessLeaderboard();
    this.getExternalRobustnessScore();
    this.getExternalAttackScore();
    this.getPrivacyScore();
    // this.getSafetyScore();
    this.getEthicsScore();
    this.getTruthfullnessScore();
    this.isLoadingTable = false;
    if(urlList.enableInterpret){
      this.options.push({ name: 'Interpretability', value: 'interpretability' });
      this.getScoresExplain('explain', "Mathematical&Reasoning");
      }
  }

  // Handles API errors and displays a snackbar message
  handleError(error: any) {
    console.log(error)
    console.log(error.status);
    console.log(error.error.detail);
    let message
    if (error.status === 500) {
      message = "Internal Server Error. Please try again later.";
    } else {
      message = error.error.detail || error.error.message || "API has failed";
    }
    const action = 'Close';
    this.openSnackBar(message, action);
  }
  

  activeTable = 'Model Robustness'
  options = [
    { name: 'Model Robustness', value: 'Model Robustness' },
    //{ name: 'Adversarial Robustness', value: 'Adversarial Robustness' },
    { name: 'Model Fairness', value: 'Model-Fairness' },
    { name: 'Model Truthfullness', value: 'Model-Truthfullness' },
    // { name: 'Model Safety', value: 'Model-Safety' },
    { name: 'Model Privacy', value: 'Model-Privacy' },
    { name: 'Model Ethics', value: 'Model-Ethics' },
   // { name: 'Interpretability', value: 'interpretability' },
  ];

  anotherActiveTable: string = "Mathematical&Reasoning";
  isLoading: boolean = true;
  hasError: boolean = false;


  anotherOptions = [
    { value: 'Reclor', name: 'Reclor' },
    { value: 'Logiqa', name: 'Logiqa' },
    { value: 'Mathematical&Reasoning', name: 'Mathematical and Reasoning' },
    { value: 'Medical Condition', name: 'Medical Condition' },
    { value: 'Sentiment Analysis', name: 'Sentiment Analysis' },
    { value: 'Laws and Legal', name: 'Laws and Legal' },
    { value: 'Chemical Reaction', name: 'Chemical Reaction' },
    { value: 'Conciseousness', name: 'Conciseousness' },
    { value: 'All', name: 'All' }
];

  interpretabilityDatasource:any = []

  externalRobustnessScore = '';
  externalAttackScore = '';
  LLMleaderboardPrivacy = '';
  LLMleaderboardSafety = '';
  LLMLeaderboardEthics = '';
  LLMLeaderboardTruthfullness = '';
  avaiableDataSetsVariable: any;
  listOfaviablableDataSets: string[] = [];
  columnList: string[] = []
  securityLLM_getLeaderBoard = '';
  securityLLM_availableDatasets = '';
  securityLLMFairness_leaderboard = '';
  leaderboardModelLists: string[] = [];
  leaderBoardData: { [key: string]: { [key: string]: string } } = {};
  leaderboardDataSource: { [key: string]: string }[] = [];
  ip_port: any
  fairness: { [key: string]: { [key: string]: number } }[] = [];
  dataSourceFairness: any[] = [];
  fairnessKeys: string[] = []
  fairnessCol: string[] = [];

  // Fetches leaderboard data from the API
  getLeaderboard() {
    this.https.get(this.securityLLM_getLeaderBoard).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.leaderBoardData = res;
        this.leaderboardModelLists = Object.keys(this.leaderBoardData);
      },
      error => {
        // this.logger.log("Error status",error.status);
        this.handleError(error)
      }
    );
  }

  // Fetches available datasets from the API
  getAvailableDataSets() {
    this.https.get(this.securityLLM_availableDatasets).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.avaiableDataSetsVariable = res
        this.getListOfDataSets();
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed",error);
        this.handleError(error)

      }
    )
  }

  // Extracts the list of datasets from the API response
  getListOfDataSets() {
    try {
      for (let i = 0; i < this.avaiableDataSetsVariable.length; i++) {
        this.listOfaviablableDataSets.push(this.avaiableDataSetsVariable[i].DatasetName);
      }
      this.leaderboardMethod();
    } catch (error) {
      console.log("method failed",error);
    }
  }

   // Processes leaderboard data for display
  leaderboardMethod() {
    try {
      if (this.leaderboardModelLists.length != 0) {
        this.columnList = ['Model Name', ...this.listOfaviablableDataSets];
        // this.logger.debug("Leaderboard Column",this.columnList);
        this.leaderboardModelLists.forEach(model => {
          const dict: { [key: string]: string } = {};
          this.columnList.forEach(key => {
            if (key === 'Model Name') {
              dict[key] = model;
            }
            else {
              if (this.leaderBoardData[model][key] !== undefined) {
                dict[key] = this.leaderBoardData[model][key];
              }
              else {
                dict[key] = '--';
              }
            }
          });
          this.leaderboardDataSource.push(dict);
        });
      }
      else {
        this.leaderboardDataSource = [];
      }
    } catch (error) {
      console.log("method failed",error);
    }
  }

   // Fetches fairness leaderboard data from the API
  getFairnessLeaderboard() {
    // https://rai-toolkit-dev.az.ad.idemo-ppc.com/api/v1/trustllm/scores/getScores?category=fairness

    this.https.get(this.LeaderboardLLMendpoint + 'scores/getScores?category=fairness').subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.fairness = res;
        console.log("value", this.fairness)
      },
      error => {
        // this.logger.log("Error status",error.status);
        this.handleError(error)
      }
    );
  }

  // Processes fairness leaderboard data for display
  leaderboardFairnessMethod() {
    try {
      this.fairnessKeys = this.fairness.map((dict) => Object.keys(dict)[0]);
      this.fairnessCol = ['Model_Name', ...Object.keys(this.fairness[0][this.fairnessKeys[0]])];
      for (let i = 0; i < this.fairnessKeys.length; i++) {
        this.dataSourceFairness.push({ ...{ "Model_Name": this.fairnessKeys[i] }, ...this.fairness[i][this.fairnessKeys[i]] })
      }
    } catch (error) {
      console.log("leaderboardFairnessMethod method failed",error);
    }
  }
  dataSourceTruthfullness: any[] = [];
  dataSourceSafety: any[] = [];
  dataSourcePrivacy: any[] = [];
  dataSourceMachineEthics: any[] = [];
  dataSourceRobustness: any[] = []
  dataSourceAttackScore: any[] = [];

  // Fetches external robustness scores from the API
  getExternalRobustnessScore() {
    this.https.get(this.externalRobustnessScore).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceRobustness = res
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getExternalRobustnessScore method",error);
        this.handleError(error)
      }
    )
  }

  // Fetches external attack scores from the API
  getExternalAttackScore() {
    this.https.get(this.externalAttackScore).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceAttackScore = res
        this.cdr.detectChanges();
      }, error => {
        this.handleError(error)
      }
    )
  }

   // Fetches privacy scores from the API
  getPrivacyScore() {
    this.https.get(this.LeaderboardLLMendpoint + 'scores/getScores?category=privacy').subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourcePrivacy = res
        this.cdr.detectChanges();
      }, error => {
        this.handleError(error)
      }
    )
  }

   // Fetches safety scores from the API 
  getSafetyScore() {
    this.https.get(this.LLMleaderboardSafety).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceSafety = res
        this.cdr.detectChanges();
      }, error => {
        this.handleError(error)
      }
    )
  }

   // Fetches ethics scores from the API
  getEthicsScore() {
    this.https.get(this.LeaderboardLLMendpoint + 'scores/getScores?category=ethics').subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceMachineEthics = res
        this.cdr.detectChanges();
      }, error => {
        this.handleError(error)
      }
    )
  }

   // Fetches truthfulness scores from the API
  getTruthfullnessScore() {
    this.https.get(this.LeaderboardLLMendpoint + 'scores/getScores?category=truthfulness').subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceTruthfullness = res
        this.cdr.detectChanges();
      }, error => {
        this.handleError(error)
      }
    )
  }

  toString(value: any): string {
    return value != null ? String(value) : '';
}
sortColumn: string = '';
currentSortColumn: string = '';
  // sortDirection: boolean = true; // true for ascending, false for descending
  sortDirection: 'asc' | 'desc' = 'asc';

   // Sorts data based on the selected column
  sortData(column: string): void {
    if (this.currentSortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.currentSortColumn = column;
      this.sortDirection = 'asc';
    }
  
    this.fairness.sort((a, b) => {
      let valueA: any = a[column];
      let valueB: any = b[column];
  
      // Convert to number if the column is 'prefereence_rta'
      if (column === 'prefereence_rta') {
        valueA = parseFloat(valueA.toString()) || 0;
        valueB = parseFloat(valueB.toString()) || 0;
      }
  
      if (valueA < valueB) {
        return this.sortDirection === 'asc' ? -1 : 1;
      } else if (valueA > valueB) {
        return this.sortDirection === 'asc' ? 1 : -1;
      } else {
        return 0;
      }
    });
  }

  // Handles changes in the active table for interpretability
  onAnotherActiveTableChange(event: any) {
    console.log('Selected value:', event.target.value);
    // Add your logic here
    this.getScoresExplain('explain', event.target.value);
    this.isLoading = true;
  }
  
  // Fetches interpretability scores from the API
  getScoresExplain(category: string, subCategory: string) {
    const url = `${this.trustllm_getScores_explain}?category=${encodeURIComponent(category)}&sub_category=${encodeURIComponent(subCategory)}`;
    const headers = { 'accept': 'application/json' };

    this.https.get(url, { headers }).subscribe(
      (response: any) => {
        console.log('API response:', response);
        // Handle the response here
        if (response && response.length > 0) {
          this.interpretabilityDatasource = response;
          this.hasError = false;
          this.openSnackBar('Data loaded successfully', 'Close');
        } else {
          this.hasError = true;
          this.openSnackBar('No data available', 'Close');
        }
        this.isLoading = false;
      },
      (error) => {
        console.error('API error:', error);
        this.isLoading = false;
        this.hasError = true;
        this.openSnackBar('Failed to load data. Please try again later.', 'Close');
      }
    );
  }

  // Opens a snackbar with a custom message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'top',
      panelClass: ['le-u-bg-black'],
    });
  }
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  // Optional method to format headers (e.g., adding spaces to camel case keys)
  formatHeader(key: string): string {
    return key.replace(/([A-Z])/g, ' $1').toUpperCase();
  }
}
