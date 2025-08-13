/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { environment } from 'src/environments/environment';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { FormControl } from '@angular/forms';
import { FmModerationService } from '../services/fm-moderation.service';
import { NonceService } from '../nonce.service';
import { UserValidationService } from '../services/user-validation.service';

@Component({
  selector: 'app-semi-structured-text',
  templateUrl: './semi-structured-text.component.html',
  styleUrls: ['./semi-structured-text.component.css']
})
export class SemiStructuredTextComponent implements OnInit{
  selectType:any = 'Privacy';
  selectValue: string = '';
  files: any[] = [];
  demoFile: any[] = [];
  selectedFile: File | any;
  file: File | any;
  form: FormGroup;
  ocrvalue: string = 'Tesseract';
  ocr_options = ['Tesseract', 'EasyOcr', 'ComputerVision'];
  new_options: string[] = ['PDF Anonymize','PPT Anonymize', 'DOCX Anonymize', 'JSON Anonymize', 'CSV Anonymize' ];
  newDropdownValue: any="";


  portfolioName_value = '';
  accountName_value = '';
  exclusionList_value = '';
  keys_to_skip ='';
  filePreview: any = '';
  private url :any;
  private Privacy_PPT_anonymize :any;
  private privacyRecognizersList :any;
  private llm_explainability_file_upload_explanation :any;
  private Privacy_DOCX_anonymize :any;
  private Privacy_JSON_anonymize :any;
  private Privacy_CSV_anonymize :any;
  pdfSrc: SafeResourceUrl | null = null;
  output : boolean = false;
  spinner : boolean = false;
  sampleImg = environment.imagePathurl + '/assets/image/Doc.png';
  sampleImgXLSX = environment.imagePathurl + '/assets/image/csvIcon2.png';
  sampleImgpptx = environment.imagePathurl + '/assets/image/pptxIcon.png';
  sampleImgCSV = environment.imagePathurl + '/assets/image/csvIcon.png';
  sampleFile = environment.imagePathurl + '/assets/samplefiles/Healthcare_Application.pdf';
  sampleFile2 = environment.imagePathurl + '/assets/samplefiles/Life_Insurance.pdf';
  sampleFileExplain = environment.imagePathurl + '/assets/samplefiles/Prompts.xlsx';
  sampleFilePRivacycsv = environment.imagePathurl + '/assets/samplefiles/CustomerFinanceData.csv';
  sampleFilePRivacyppt = environment.imagePathurl + '/assets/samplefiles/ProjectStatusDetails.pptx';
  sampleFilePRivacyjson = environment.imagePathurl + '/assets/samplefiles/UserData.json';
  loggedUser: any;
  nlpOption:any = '';
  responseFileType: string = 'excel';
  piiEntitiesToBeRedactedOption = new FormControl([]);

  available_Recognizers =[];
  nlp_options = [
    { viewValue: 'Spacy-wb-lg (Basic)', value: 'basic' },
    { viewValue: 'Spacy-wb-trf (Good)', value: 'good' },
    { viewValue: 'PIIRanha (Medium)', value: 'ranha' },
    { viewValue: 'Roberta (High)', value: 'roberta' }
  ];
  nlptooltip = `Spacy-wb-lg (low accuracy & faster response),\n
  Spacy-wb-trf (medium accuracy & faster response) - Recommended,\n
  Roberta (high accuracy & slower response),\n
  PIIRanha (medium accuracy & medium response)`;

  explainabilityForm: FormGroup;
  anotherOptionControl: FormControl;
  anotherOptions: any[] = [ 'Token-Importance','ThoT', 'ReRead-ThoT', 'GoT', 'CoT', 'CoV', 'LoT'];
responseFileTypeOptions: any[] = ['json', 'excel'];

  constructor(private fb: FormBuilder,  public dialog: MatDialog,  public _snackBar: MatSnackBar, private https: HttpClient, private sanitizer: DomSanitizer,public fmService: FmModerationService,public nonceService:NonceService, private validationService:UserValidationService) {
    this.form = this.fb.group({
      languageModel: ['', Validators.required],
      newDropdown: ['']
    });

    this.explainabilityForm = new FormGroup({});
    this.anotherOptionControl = new FormControl();
  }

  // Initializes the component and sets up API calls
  ngOnInit() {
    let ip_port: any;
    ip_port = this.getLocalStoreApi();
    this.setApilist(ip_port);
    this.getRecognizers();
    this.anotherOptionControl = new FormControl([]);
    this.explainabilityForm = this.fb.group({
      anotherOptionControl: this.anotherOptionControl
    })
    if (window && window.localStorage && typeof localStorage !== 'undefined') {
      const x = localStorage.getItem("userid") ? JSON.parse(localStorage.getItem("userid")!) : "NA";
      if (x != null && (this.validationService.isValidEmail(x) || this.validationService.isValidName(x))) {
        this.loggedUser = x ;
      }
      console.log("userId", this.loggedUser)
    }
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() { 
let ip_port
if (window && window.localStorage && typeof localStorage !== 'undefined') {
  const res = localStorage.getItem("res") ? localStorage.getItem("res") : "NA";
  if(res != null){
    return ip_port = JSON.parse(res)
  }
}

  }

  // Sets the API endpoints for the component
  setApilist(ip_port: any) {
    this.url = ip_port.result.Privacy + ip_port.result.Privacy_Pdf;  
    this.Privacy_PPT_anonymize = ip_port.result.Privacy + ip_port.result.Privacy_PPT_anonymize;  
    this.privacyRecognizersList = ip_port.result.Privacy + ip_port.result.Privacy_getRecognizer;  
    this.llm_explainability_file_upload_explanation = ip_port.result.Llm_Explain + ip_port.result.llm_explainability_file_upload_explanation; 
    this.Privacy_DOCX_anonymize = ip_port.result.Privacy + ip_port.result.Privacy_DOCX_anonymize;
    this.Privacy_JSON_anonymize = ip_port.result.Privacy + ip_port.result.Privacy_JSON_anonymize;
    this.Privacy_CSV_anonymize = ip_port.result.Privacy + ip_port.result.Privacy_CSV_anonymize; 
   }

    // Resets all form fields and file inputs
  resetAll() {
    this.portfolioName_value = '';
    this.accountName_value = '';
    this.exclusionList_value = '';
    this.keys_to_skip ='';
    this.output = false;
    this.spinner = false;
    this.removeFile();
  }

  // Removes the uploaded files
  removeFile() {
    this.demoFile = [];
    this.files = [];
  }
  // pptSrc: SafeResourceUrl | null = null;

  
  submit1(){
    console.log("this.piiEntitiesToBeRedactedOption::", this.piiEntitiesToBeRedactedOption.value!.join(','));
  }

  // Handles the form submission based on the selected type
  submit() {
    this.output = false;
    this.spinner = true;
    if (this.selectType == 'Privacy') {
      this.getSelectedValues();
      if (this.newDropdownValue === '') {
        {
          this.openSnackBar('Please select method type before submitting', 'Close');
        }
        return;
      }
      if (this.files.length === 0) {
        this.openSnackBar('Please upload a file before submitting', 'Close');
        return
      }
      const formData = new FormData();
      formData.append('pdf', this.demoFile[0]);
      formData.append('portfolio', this.portfolioName_value);
      formData.append('account', this.accountName_value);
      formData.append('exclusionList', this.exclusionList_value);
      formData.append('nlp', this.nlpOption);
      if (!this.accountName_value || !this.portfolioName_value) {
        formData.append('piiEntitiesToBeRedacted', this.piiEntitiesToBeRedactedOption.value!.join(','));
      }

      if (this.newDropdownValue === 'PDF Anonymize') {
        // Logic for Pdf Anonymize
        console.log('Selected option: PDF Anonymize');
        const file = this.demoFile[0];
        const allowedTypes = ['application/pdf'];
        if (!allowedTypes.includes(file.type)) {
          this.openSnackBar('Please upload a valid PDF file', 'Close');
          this.spinner = false;
          return;
        } else {
          this.https.post(`${this.url}?ocrvalue=${encodeURIComponent(this.ocrvalue)}`, formData, { responseType: 'blob' }).subscribe(
            response => {
              console.log('Upload successful', response);
              const blob = new Blob([response], { type: 'application/pdf' });
              const url = URL.createObjectURL(blob);
              this.pdfSrc = this.sanitizer.bypassSecurityTrustResourceUrl(url);
              this.output = true;
              this.spinner = false;
            },
            error => {
              console.error('Upload failed', error);
              let errorMessage = 'API Failed';
              if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                  try {
                    const errorJson = JSON.parse(text);
                    if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                      errorMessage = errorJson.detail;
                    }
                  } catch (e) {
                    console.error('Error parsing error response', e);
                  }
                  this.openSnackBar(errorMessage, 'Close');
                });
              } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                  errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
              }
              this.openSnackBar(errorMessage, 'Close');
              this.spinner = false;
              this.output = false;
            }
          );
        }
      } else if (this.newDropdownValue === 'PPT Anonymize') {
        // Logic for PPT Anonymize
        console.log('Selected option: PPT Anonymize');
        const file = this.demoFile[0];
        const allowedTypes = [
          'application/vnd.ms-powerpoint',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ];
        if (!allowedTypes.includes(file.type)) {
          this.openSnackBar('Please upload a valid PPT file', 'Close');
          this.spinner = false;
          return;
        } else {

          // Add any additional form data or logic specific to PPt Anonymize

          const formDatappt = new FormData();
          formDatappt.append('ppt', this.demoFile[0]);
          formDatappt.append('portfolio', this.portfolioName_value);
          formDatappt.append('account', this.accountName_value);
          formDatappt.append('exclusionList', this.exclusionList_value);
          formDatappt.append('nlp', this.nlpOption);

          if (!this.accountName_value || !this.portfolioName_value) {
            formDatappt.append('piiEntitiesToBeRedacted', this.piiEntitiesToBeRedactedOption.value!.join(','));
          }

          let url = this.Privacy_PPT_anonymize + `?ocr=${encodeURIComponent(this.ocrvalue)}`;

          console.log('Selected option: PPt Anonymize');
          this.https.post(url, formDatappt, { responseType: 'blob' }).subscribe(
            response => {
              console.log('Upload successful', response);
              const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'anonymized_presentation.pptx';
              link.click();
              window.URL.revokeObjectURL(url);
              // this.pptSrc = this.sanitizer.bypassSecurityTrustResourceUrl(url);
              // this.output = true;
              this.spinner = false;
            },
            error => {
              console.error('Upload failed', error);
              let errorMessage = 'API Failed';
              if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                  try {
                    const errorJson = JSON.parse(text);
                    if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                      errorMessage = errorJson.detail;
                    }
                  } catch (e) {
                    console.error('Error parsing error response', e);
                  }
                  this.openSnackBar(errorMessage, 'Close');
                });
              } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                  errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
              }
              this.openSnackBar(errorMessage, 'Close');
              this.spinner = false;
            }
          );
        }
      }
      else if(this.newDropdownValue === 'DOCX Anonymize'){
        console.log('Selected option: DOCX Anonymize');
        const file = this.demoFile[0];
        const allowedTypes = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
          this.openSnackBar('Please upload a valid Docx file', 'Close');
          this.spinner = false;
          return;
        } else {
          const formDataDoc = new FormData();
          formDataDoc.append('docx', this.demoFile[0]);
          formDataDoc.append('portfolio', this.portfolioName_value);
          formDataDoc.append('account', this.accountName_value);
          formDataDoc.append('exclusionList', this.exclusionList_value);
          formDataDoc.append('nlp', this.nlpOption);

          if (!this.accountName_value || !this.portfolioName_value) {
            formDataDoc.append('piiEntitiesToBeRedacted', this.piiEntitiesToBeRedactedOption.value!.join(','));
          }

          let url = this.Privacy_DOCX_anonymize + `?ocr=${encodeURIComponent(this.ocrvalue)}`;

          this.https.post(url, formDataDoc, { responseType: 'blob' }).subscribe(
            response => {
              console.log('Upload successful', response);
              const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'anonymized_Document.docx';
              link.click();
              window.URL.revokeObjectURL(url);
              this.spinner = false;
            },
            error => {
              console.error('Upload failed', error);
              let errorMessage = 'API Failed';
              if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                  try {
                    const errorJson = JSON.parse(text);
                    if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                      errorMessage = errorJson.detail;
                    }
                  } catch (e) {
                    console.error('Error parsing error response', e);
                  }
                  this.openSnackBar(errorMessage, 'Close');
                });
              } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                  errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
              }
              this.openSnackBar(errorMessage, 'Close');
              this.spinner = false;
            }
          );
        }
      }
      else if(this.newDropdownValue === 'JSON Anonymize'){
        console.log('Selected option: Json Anonymize');
        const file = this.demoFile[0];
        const allowedTypes = ['application/json'];
        if (!allowedTypes.includes(file.type)) {
          this.openSnackBar('Please upload a valid Json file', 'Close');
          this.spinner = false;
          return;
        } else {
          const formDataJson = new FormData();
          formDataJson.append('file', this.demoFile[0]);
          formDataJson.append('keys_to_skip', this.keys_to_skip);
          formDataJson.append('portfolio', this.portfolioName_value);
          formDataJson.append('account', this.accountName_value);
          formDataJson.append('exclusionList', this.exclusionList_value);
          formDataJson.append('nlp', this.nlpOption);

          if (!this.accountName_value || !this.portfolioName_value) {
            formDataJson.append('piiEntitiesToBeRedacted', this.piiEntitiesToBeRedactedOption.value!.join(','));
          }

          let url = this.Privacy_JSON_anonymize + `?ocr=${encodeURIComponent(this.ocrvalue)}`;

          this.https.post(url, formDataJson, { responseType: 'blob' }).subscribe(
            response => {
              console.log('Upload successful', response);
              const blob = new Blob([response], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'anonymized_JSON.json';
              link.click();
              window.URL.revokeObjectURL(url);
              this.spinner = false;
            },
            error => {
              console.error('Upload failed', error);
              let errorMessage = 'API Failed';
              if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                  try {
                    const errorJson = JSON.parse(text);
                    if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                      errorMessage = errorJson.detail;
                    }
                  } catch (e) {
                    console.error('Error parsing error response', e);
                  }
                  this.openSnackBar(errorMessage, 'Close');
                });
              } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                  errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
              }
              this.openSnackBar(errorMessage, 'Close');
              this.spinner = false;
            }
          );
        }
      }
      else if(this.newDropdownValue === 'CSV Anonymize'){
        console.log('Selected option: CSV Anonymize');
        const file = this.demoFile[0];
        const allowedTypes = ['text/csv'];
        if (!allowedTypes.includes(file.type)) {
          this.openSnackBar('Please upload a valid CSV file', 'Close');
          this.spinner = false;
          return;
        } else {
          const formDataCSV = new FormData();
          formDataCSV.append('file', this.demoFile[0]);
          formDataCSV.append('keys_to_skip', this.keys_to_skip);
          formDataCSV.append('portfolio', this.portfolioName_value);
          formDataCSV.append('account', this.accountName_value);
          formDataCSV.append('exclusionList', this.exclusionList_value);
          formDataCSV.append('nlp', this.nlpOption);

          if (!this.accountName_value || !this.portfolioName_value) {
            formDataCSV.append('piiEntitiesToBeRedacted', this.piiEntitiesToBeRedactedOption.value!.join(','));
          }

          let url = this.Privacy_CSV_anonymize + `?ocr=${encodeURIComponent(this.ocrvalue)}`;

          this.https.post(url, formDataCSV, { responseType: 'blob' }).subscribe(
            response => {
              console.log('Upload successful', response);
              const blob = new Blob([response], { type: 'text/csv' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'anonymized_CSV.csv';
              link.click();
              window.URL.revokeObjectURL(url);
              this.spinner = false;
            },
            error => {
              console.error('Upload failed', error);
              let errorMessage = 'API Failed';
              if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                  try {
                    const errorJson = JSON.parse(text);
                    if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                      errorMessage = errorJson.detail;
                    }
                  } catch (e) {
                    console.error('Error parsing error response', e);
                  }
                  this.openSnackBar(errorMessage, 'Close');
                });
              } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                  errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
              }
              this.openSnackBar(errorMessage, 'Close');
              this.spinner = false;
            }
          );
        }
      }

      else {
        console.log('No specific option selected');
      }

    }
    else if (this.selectType == 'Explainability') {
      const file = this.demoFile[0]; // Replace with the actual file object
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
      ];
    
      if (!allowedTypes.includes(file.type)) {
        this.openSnackBar('Please upload a valid Excel or CSV file', 'Close');
        this.spinner = false;
        return;
      } else {
        // console.log('anotherOptionControl Value:', this.anotherOptionControl.value);
        if (!this.anotherOptionControl.value || this.anotherOptionControl.value.length === 0) {
          this.openSnackBar('Please select at least one method', 'Close');
          this.spinner = false;
          return;
        }else{

          this.explainapicall(file)
        }
        
      }
    }

  }

   // Displays a snackbar with a message
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, '✖', {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'top',
      panelClass: ['le-u-bg-black'],
    });
  }

  // Updates the OCR value based on the selected option
  selectOptionOcr(e: any) {
    console.log('Selected option ID:', e.value);
    this.ocrvalue = e.value;
  }

  // Resets the selected value when the type changes
  handleSelectTypeChange(){
      this.selectValue = '';
  }

  // Handles file input changes
  onFileChange(event: any) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
     // console.log(text);
    };
    reader.readAsText(event.target.files[0]);
  }

   // Handles file browsing and prepares the file list
  fileBrowseHandler(File: any) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/csv', 'application/json','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const allowedExtensions = ['.xlsx', '.xls', '.csv', '.json', '.pdf', '.docx', '.pptx']
    console.log("fileBrowseHandler", File.target.files[0].type)
    if (!allowedTypes.includes(File.target.files[0].type)) {
      this._snackBar.open('Please select a valid file type', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
      });
      // return;
    }else{
    this.prepareFilesList(File.target.files);
    this.demoFile = this.files;
    this.file = this.files[0];
    const reader = new FileReader();
    reader.readAsDataURL(this.files[0]);
    reader.onload = (_event) => {
      const base64String = reader.result as string;
      this.filePreview = base64String;
      //console.log("filePreview",this.filePreview )
    };
   }
  }

  // Prepares the list of files for upload
  prepareFilesList(files: Array<any>) {
    this.files = [];
    this.demoFile = [];
    for (const item of files) {
      const cleanedName = item.name.replace(/\[object Object\]/g, '');
      const newFile = new File([item], cleanedName, { type: item.type });
      this.files.push(newFile);
    }
    this.uploadFilesSimulator(0, files);
  }

  // Simulates file upload progress
  uploadFilesSimulator(index: number, files: any) {
    setTimeout(() => {
      if (index === this.files.length) {
        console.log('RETURN');
        return;
      } else {
        this.files[index].progress = 0;
        const progressInterval = setInterval(() => {
          if (this.files[index].progress >= 100) {
            clearInterval(progressInterval);
          } else {
            console.log('ELSE BLOCK');
            this.files[index].progress += 10;
          }
        }, 200);
      }
    }, 1000);
  }

  // Uploads a sample PDF file
  uploadSampleFile(fileType: string) {
    const fileToFetch = fileType === 'sampleFile' ? this.sampleFile : this.sampleFile2;
  
    fetch(fileToFetch)
        .then(response => response.blob())
        .then(blob => {
            const fileName = fileToFetch.split('/').pop() || 'sample_document.pdf';
            const samplePdf = new File([blob], fileName, { type: "application/pdf" });
            const event = { target: { files: [samplePdf] } };
            this.onFileChange(event);
            this.fileBrowseHandler(event);
        })
        .catch(error => {
            console.error('Error fetching the sample file:');
        });
  }

  // Uploads a sample XLSX file
  uploadSampleXlsxFile(fileType: string) {
    // const fileToFetch = this.sampleFileExplain;
    const fileToFetch = fileType === 'sampleFileExplain' ? this.sampleFileExplain : this.sampleFileExplain;

    fetch(fileToFetch)
        .then(response => response.blob())
        .then(blob => {
            const fileName = fileToFetch.split('/').pop() || 'Prompts.xlsx';
            const sampleXlsx = new File([blob], fileName, { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
            const event = { target: { files: [sampleXlsx] } };
            this.onFileChange(event);
            this.fileBrowseHandler(event);
        })
        .catch(error => {
            console.error('Error fetching the sample file:');
        });
}

// Uploads a sample CSV file
uploadSampleCsvFile(fileType: string) {
  const fileToFetch = fileType === 'sampleFilePRivacycsv' ? this.sampleFilePRivacycsv : this.sampleFilePRivacycsv;

  fetch(fileToFetch)
      .then(response => response.blob())
      .then(blob => {
          const fileName = fileToFetch.split('/').pop() || 'sampleFilePRivacycsv.csv';
          const sampleCsv = new File([blob], fileName, { type: "text/csv" });
          const event = { target: { files: [sampleCsv] } };
          this.onFileChange(event);
          this.fileBrowseHandler(event);
      })
      .catch(error => {
          console.error('Error fetching the sample file:');
      });
}

// Uploads a sample PPTX file
uploadSamplePptxFile(fileType: string) {
  const fileToFetch = fileType === 'sampleFilePRivacyppt' ? this.sampleFilePRivacyppt : this.sampleFilePRivacyppt;

  fetch(fileToFetch)
      .then(response => response.blob())
      .then(blob => {
          const fileName = fileToFetch.split('/').pop() || 'sampleFilePRivacyppt.pptx';
          const samplePptx = new File([blob], fileName, { type: "application/vnd.openxmlformats-officedocument.presentationml.presentation" });
          const event = { target: { files: [samplePptx] } };
          this.onFileChange(event);
          this.fileBrowseHandler(event);
      })
      .catch(error => {
          console.error('Error fetching the sample file:');
      });
}

 // Opens a dialog for file preview
openDialog(data: any) {
  const fileType = this.files[0].name.split('.').pop().toLowerCase();
  if (fileType === 'pdf') {
      this.dialog.open(ImageDialogComponent, {
          data: { pdf: data, flag: true },
          backdropClass: 'custom-backdrop'
      });
      console.log("data", data);
  } else {
      this._snackBar.open('Preview on this file type is not available', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
      });
  }
}

 // Retrieves selected portfolio and account values
  getSelectedValues(): void {
    this.portfolioName_value = localStorage.getItem('selectedPortfolio') ?? '';
    this.accountName_value = localStorage.getItem('selectedAccount') ?? '';
    console.log('Selected Portfolio:', this.portfolioName_value);
    console.log('Selected Account:', this.accountName_value);
  }

  // Fetches the list of available recognizers
  getRecognizers() {
    
    let url = this.privacyRecognizersList;
    const headers = { 'accept': 'application/json' };
    
    this.https.get(url, { headers }).subscribe(
      (response: any) => {
        const availableRecognizers = response['Available Recognizers'];
        this.available_Recognizers = availableRecognizers;
      },
      (error) => {
        console.error('API error:', error);
      }
    );
  }

   // Updates the selected value for the new dropdown
  selectOptionNewDropdown(target: any): void {
    this.newDropdownValue = target.value;
    console.log('Selected new dropdown option:', this.newDropdownValue);
  }

  // Handles selection changes for the explainability options
  onSelectionChange(event: any): void {
    const selectedValues = event.value;
    if (selectedValues.includes('All')) {
      this.anotherOptionControl.setValue(['All']);
    }
  }

  // Disables options based on the selected values
  isOptionDisabled(option: string): boolean {
    const selectedValues = this.anotherOptionControl.value;
    return selectedValues.includes('All') && option !== 'All';
  }

  // Calls the explainability API with the selected file
  explainapicall(file: File) {
    const url = this.llm_explainability_file_upload_explanation;
    const formData: FormData = new FormData();
    const payload = {
      methods: this.anotherOptionControl.value,
      responseFileType: this.responseFileType,
      userId: this.loggedUser
    }
    formData.append('payload', JSON.stringify(payload));
    formData.append('file', file, file.name);

    const headers = new HttpHeaders({
        'accept': '*/*'
    });

    this.https.post(url, formData, { headers: headers, observe: 'response', responseType: 'blob' }).subscribe(
        response => {
            console.log('Upload successful', response);
            if (response.body) {
                const blob = new Blob([response.body], { type: file.type });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;

                // Extract file name from response headers
                const contentDisposition = response.headers.get('Content-Disposition');
                let fileName = "modified"+file.name; // Default to original file name
                if (contentDisposition) {
                    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
                    if (matches != null && matches[1]) {
                        fileName = matches[1].replace(/['"]/g, '');
                    }
                }

                link.download = fileName;
                link.click();
                window.URL.revokeObjectURL(url);
            } else {
                console.error('Response body is null');
            }

            this.spinner = false;
        },
        error => {
            this.spinner = false;
            console.error('Upload failed', error);
            let errorMessage = 'API Failed';
            if (error.error instanceof Blob) {
                error.error.text().then((text: string) => {
                    try {
                        const errorJson = JSON.parse(text);
                        if (errorJson.detail === 'Portfolio/Account Is Incorrect') {
                            errorMessage = errorJson.detail;
                        }
                    } catch (e) {
                        console.error('Error parsing error response', e);
                    }
                    this.openSnackBar(errorMessage, 'Close');
                });
            } else {
                if (error.error?.detail === 'Portfolio/Account Is Incorrect') {
                    errorMessage = error.error.detail;
                }
                this.openSnackBar(errorMessage, 'Close');
            }
            this.spinner = false;
        }
    );
}

// Downloads a file from the given URL
downloadFile(file: string, event: MouseEvent) {
  event.preventDefault(); // Prevent the default context menu from appearing

  const link = document.createElement('a');
  link.href = file; // Assuming `file` is the URL to the file
  link.download = file.split('/').pop() || 'downloaded-file'; // Provide a default file name if undefined
  link.click();
}
}
