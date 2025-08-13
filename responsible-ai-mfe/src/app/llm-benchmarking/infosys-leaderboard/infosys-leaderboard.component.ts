/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-infosys-leaderboard',
  templateUrl: './infosys-leaderboard.component.html',
  styleUrls: ['./infosys-leaderboard.component.css']
})
export class InfosysLeaderboardComponent {
  // FOR SHIMMER
  isLoadingTable = true;
  ///
  constructor(
    public https: HttpClient,
    private _snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef,
  ){}

   // Initializes the component and sets up API calls
  ngOnInit(): void {
  if (window && window.localStorage && typeof localStorage !== 'undefined') {
    const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
    if(res != null){
    this.ip_port = JSON.parse(res)
    }
  }
    this.securityLLM_getLeaderBoard = this.ip_port.result.SecurityLLMInfo +this.ip_port.result.SecurityLLMInfo_leadeboard;
    this.securityLLM_availableDatasets = this.ip_port.result.SecurityLLMInfo +this.ip_port.result.SecurityLLMInfo_datasets;
    this.securityLLMFairnesInfo_leaderboard = this.ip_port.result.SecurityLLMLeaderboard +this.ip_port.result.SecurityLLMInfoFairnessLScore;
    this.LLMLeaderboardTruthfullness = this.ip_port.result.SecurityLLMLeaderboard +this.ip_port.result.SecurityLLMInfoTruthfullnessLScore;
    this.LLMleaderboardSafety = this.ip_port.result.SecurityLLMLeaderboard +this.ip_port.result.SecurityLLMInfoSafetyLScore;
    this.LLMleaderboardPrivacy = this.ip_port.result.SecurityLLMLeaderboard +this.ip_port.result.SecurityLLMInfoPrivacyLScore;
    this.LLMLeaderboardEthics = this.ip_port.result.SecurityLLMLeaderboard +this.ip_port.result.SecurityLLMInfoEthicsLScore;
    this.getLeaderboard();
    this.getAvailableDataSets();
    this.getFairnessLeaderboard();
    this.getTruthfullnessScore();
    this.getSafetyScore();
    this.getPrivacyScore();
    this.getEthicsScore();
    this.isLoadingTable = false;
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

  // Opens a snackbar with a custom message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  activeTable = 'Model Robustness'
  options = [
    { name: 'Model Robustness', value: 'Model Robustness' },
    { name: 'Model Fairness', value: 'Model-Fairness' },
    { name: 'Model Truthfulness', value: 'Model-Truthfulness' },
    { name: 'Model Safety', value: 'Model-Safety' },
    { name: 'Model Privacy', value: 'Model-Privacy' },
    { name: 'Model Ethics', value: 'Model-Ethics' },
  ];

  ip_port:any
  LLMLeaderboardEthics='';
  LLMleaderboardPrivacy='';
  LLMleaderboardSafety='';
  LLMLeaderboardTruthfullness='';
  securityLLM_availableDatasets='';
  securityLLM_getLeaderBoard='';
  securityLLMFairnesInfo_leaderboard='';
  avaiableDataSetsVariable:any;
  listOfaviablableDataSets:string[]=[];
  leaderboardModelLists:string[]=[];
  leaderBoardData:{ [key: string]: { [key: string]: string } }={};
  leaderboardDataSource: { [key: string]: string }[] = [];
  columnList:string[]=[]
  fairness: { [key: string]: { [key: string]: number } }[]=[];
  dataSourceFairness: any[] = [];
  fairnessKeys:string[]=[]
  fairnessCol:string[]=[];

  // Fetches leaderboard data from the API
  getLeaderboard(){
    this.https.get(this.securityLLM_getLeaderBoard).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.leaderBoardData = res;
        this.leaderboardModelLists = Object.keys(this.leaderBoardData);
      },
      error => {
        this.handleError(error);
      }
    );
  }

  // Fetches available datasets from the API
  getAvailableDataSets(){
    this.https.get(this.securityLLM_availableDatasets).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.avaiableDataSetsVariable = res
        this.getListOfDataSets();
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getAvailableDataSets method",error);
          this.handleError(error)
        }
    )
  }

   // Extracts the list of datasets from the API response
  getListOfDataSets(){
    try{
    for(let i=0;i<this.avaiableDataSetsVariable.length;i++){
      this.listOfaviablableDataSets.push(this.avaiableDataSetsVariable[i].DatasetName);
    }
    this.leaderboardMethod();
  }catch(error){
    console.log("getListOfDataSets method failed",error);
  }
  }

  // Processes leaderboard data for display
  leaderboardMethod(){
    try{
    if(this.leaderboardModelLists.length!=0){
    this.columnList = ['Model_Name',...this.listOfaviablableDataSets];
    // this.logger.debug("Leaderboard Column",this.columnList);
    this.leaderboardModelLists.forEach(model => {
      const dict: { [key: string]: string } = {};
      this.columnList.forEach(key => {
        if (key === 'Model_Name') {
          dict[key] = model;
        }
        else{
          if(this.leaderBoardData[model][key] !== undefined){
            dict[key] = this.leaderBoardData[model][key];
          }
          else{
            dict[key]='--';
          }
        }
      });
      this.leaderboardDataSource.push(dict);
    });
  }
  else{
    this.leaderboardDataSource=[];
  }
}catch(error){
  console.log("leaderboardMethod method failed",error);
}
  }

  // Fetches fairness leaderboard data from the API
  getFairnessLeaderboard(){
    this.https.get(this.securityLLMFairnesInfo_leaderboard).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.fairness =res;
      },
      error => {
        // this.logger.log("Error status",error.status);
        this.handleError(error)
      }
    );
  }

  // Processes fairness leaderboard data for display
  leaderboardFairnessMethod(){
    try{
    this.fairnessKeys = this.fairness.map((dict) => Object.keys(dict)[0]);
    this.fairnessCol=['Model_Name',...Object.keys(this.fairness[0][this.fairnessKeys[0]])];
    for(let i=0;i<this.fairnessKeys.length;i++){
      this.dataSourceFairness.push({...{"Model_Name":this.fairnessKeys[i]},...this.fairness[i][this.fairnessKeys[i]]})
    }
  }catch(error){
    console.log("leaderboardFairnessMethod method failed",error);
  }
  }
  dataSource1Robustness:any[]=[{"Model_Name":"infosys/mixtral8x7b-instruct/versions/1/infer","qqp":"0.496","sst2":"0.773","cola":"0.657"}]
  dataSourceTruthfullness:any[]=[]
  dataSourceSafety:any[]=[];
  dataSourcePrivacy:any[]=[];
  dataSourceMachineEthics:any[]=[]

  // Fetches truthfulness scores from the API
  getTruthfullnessScore(){
    this.https.get(this.LLMLeaderboardTruthfullness).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceTruthfullness = res
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getTruthfullnessScore method",error);
          this.handleError(error)
        }
    )
  }

  // Fetches safety scores from the API
  getSafetyScore(){
    this.https.get(this.LLMleaderboardSafety).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceSafety = res
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getSafetyScore method",error);
          this.handleError(error)

        }
    )
  }

  // Fetches privacy scores from the API
  getPrivacyScore(){
    this.https.get(this.LLMleaderboardPrivacy).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourcePrivacy = res
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getPrivacyScore method",error);
          this.handleError(error)
        }
    )
  }

  // Fetches ethics scores from the API
  getEthicsScore(){
    this.https.get(this.LLMLeaderboardEthics).subscribe(
      (res: any) => {
        // this.logger.info("Api call has been successfull");
        this.dataSourceMachineEthics = res
        this.cdr.detectChanges();
      }, error => {
        // this.logger.error("Api call get failed for getEthicsScore method",error);
          this.handleError(error)

        }
    )
  }
}
