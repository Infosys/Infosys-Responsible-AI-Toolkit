/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ImageDialogComponent } from '../image-dialog/image-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { NgForm, FormControl, Validators } from '@angular/forms';
import { ImageReportChartComponent } from '../image-report-chart/image-report-chart.component';
import { RoleManagerService } from '../services/role-maganer.service';
import { FairnessSideModalComponent } from './fairness-side-modal/fairness-side-modal.component';
import { MatTooltip } from '@angular/material/tooltip';
import { NonceService } from '../nonce.service';

@Component({
  selector: 'app-image-generate',
  templateUrl: './image-generate.component.html',
  styleUrls: ['./image-generate.component.css']
})
export class ImageGenerateComponent implements AfterViewInit {
  @ViewChild('form') form: NgForm | undefined;
  @ViewChild('tooltip', { static: false }) tooltip!: MatTooltip;

  // FOR SHIMMER EFFECT
  isLoadingSelectType = true;
  isLoadingPrompt = true;
  /////
  promptControl = new FormControl('', Validators.required);
  imageGenerateUrl: any = ""
  public ip_port: any
  showSpinner: boolean = false;
  public prompt: string = '';
  imageOutput: any = false;
  imageBlurred = ""
  imageAnalysePath = ""
  imagePath: string = "";
  analyse: any = "";
  redactedImg = false
  analyze: any = "";
  selectedOptions: any = []
  options: any = ["Profanity", "Explainability"]
  tenantarr: any = []
  hasError: boolean = false;
  imgExpl: any
  userId = ""
  image: any;
  imageExplainabilityUrl: any;
  selectType: any = 'safety';
  fairness_image: any = '';
  imageGenerateModeration: any;
  image_explainability_analyze: any;
  image_superpixel_segment_image: any;
  portfolioName = '';
  accountName = '';
  fairnessRes: any = {
    status: false,
    generatedImage: '',
    report: {}
  }
  analyzeData: any = []
  tooltips: string[] = [
    'Harmless art, or picture of art',
    'Pornographic art, unsuitable for most work environments',
    'General, inoffensive content',
    'pornographic images, sexual acts',
    'sexually explicit images, not pornography'
  ];
  showFairnessResult: boolean = false;
  aestheticScore= 0;
  alignmentScore= 0;
  originalityScore= 0;
  alignment= '';
  aesthetics = '';
  genderBias= '';
  watermark= false;
  explain_analyse_res: any;
    // method to call explainability api
    imageUrl: string | null = null;
    rawimg:any =""
      explainImagetype=""
      isCollapsed: boolean = false;
        // FILE UPLOAD
  imageFileList: any = [];
  imageFile: any = '';
  selectedImageFileName: any = '';
  imageFiles: any = [];
  imgShowUrl: any = '';
  isImageFileUploaded: boolean = false; // Flag to indicate successful file upload
  isExplainabilitySelected: boolean = false;
  selectedButton: string = '';
  isListVisible: boolean = true;
  safetyItems: string[] = [
    'Man flexing his body Infront of mirror',
    'Person in Swim Suite posing for photo'
  ];
  explainabilityItems: string[] = [
    'Create a museum image of a nomad yurt, 5th century AD, black fabric background, realistic, 4k, correct anatomy, good detail',
    'Photographic portrait of a real life dragon resting peacefully in a zoo, curled up next to its pet sheep. Cinematics movie still, high quality DSLR photo'
  ];
  fairnessItems: string[] = [
    'Image of theoretical physicist from from Cal Tech university',
     'Chef\'s team from The Marriot hotel.'
  ];

  //   imgExpl = {  "Score": {    "Aesthetics": {      "Description": "Creativity Score of image generated ,less creative being:0 and highly creative being:10`",      "Aesthetics": "LessCreative",      "AestheticsScore": 2.8177390098571777,      "FractalDimensionScore": 1.524390939460225     },    "Image_Alignment": {      "Probability": 24.964637756347656,      "AlignmentValue": "LowText-ImageAlignment"     },    "Bias": {      "Gender": {        "Male_Score": 17.568363189697266,        "Female_Score": 17.344619750976562,        "GenderBias": "NoGenderBias"       }    },    "Originality": {      "Has_WaterMark": true,      "Probability": 0.6004298329353333,
  //   "Description": "Probability Of Being Copy Of Trained Image0.6004298329353333"     }
  // }}


  // public hasError = false;
  tooltipContentInsights: string = `Insights:\n\nWatermark: Detects the presence of a watermark in the image.\n\nBias: Identifies any potential bias types based on the analysis.\n\nStyle: Classifies the image's style (e.g., Cartoon, Anime, Photorealism) by analyzing visual elements and distinctive characteristics.`;
  tooltipContentMetrics: string = `Metrics:\n\nCreativity Score: Quantitatively evaluates an image's visual appeal based on composition, color harmony, texture, and subject matter.\n\nRelevance Score: Evaluates how well the generated image aligns with the given prompt, indicating its accuracy in matching the intended description or context.`;

  constructor(public roleService: RoleManagerService, public https: HttpClient, public _snackBar: MatSnackBar, private dialog: MatDialog,public nonceService:NonceService) { }

    // Initializes the component and sets up API configurations
  ngOnInit() {
    this.options = this.roleService.getSelectedTypeOptions("Workbench", "Image", "Generative-AI")
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        this.ip_port = JSON.parse(x)
      }
    }
    let ip_port: any
    let user = this.getLogedInUser()
    ip_port = this.getLocalStoreApi()
    this.setApilist(ip_port)
    this.isLoadingSelectType = false;
    this.isLoadingPrompt = false;
  }

  // Retrieves the logged-in user from local storage
  getLogedInUser() {
    if (localStorage.getItem("userid") != null) {
      const x = localStorage.getItem("userid")
      if (x != null) {
        this.userId = JSON.parse(x)
        return JSON.parse(x)
      }
      console.log("userId", this.userId)
    }
  }

  // Retrieves API configuration from local storage
  getLocalStoreApi() {
    let ip_port
    if (localStorage.getItem("res") != null) {
      const x = localStorage.getItem("res")
      if (x != null) {
        return ip_port = JSON.parse(x)
      }
    }
  }

  // Sets the API list based on the configuration
  setApilist(ip_port: any) {
    // generate apis
    this.imageGenerateUrl = ip_port.result.Profanity + this.ip_port.result.Profan_Image_Generate;
    this.imageGenerateModeration = ip_port.result.FairnessAzure + ip_port.result.GenerateImage;
    // Analyze apis
    this.imageExplainabilityUrl = ip_port.result.Image_Explain + ip_port.result.ImageGen_Explain
    this.fairness_image = ip_port.result.FairnessAzure + ip_port.result.FairnessImage;
    this.image_explainability_analyze = ip_port.result.ExplainabilityAzure + ip_port.result.image_explainability_analyze;
    this.image_superpixel_segment_image = ip_port.result.image_superpixel_segment_image_ip + ip_port.result.image_superpixel_segment_image;
  }

// Handles API errors and displays a snackbar message
  handleError(error: any, customErrorMessage?: string) {
    console.error('Error:', error);
  
    const message = error.status === 500
      ? "Internal Server Error. Please try again later."
      : error.error?.detail || error.error?.details || error.error?.message || customErrorMessage || "API has failed";
  
    this.showSpinner = false;
    this.openSnackBar(message);
  }

  // Opens a snackbar with a custom message
  openSnackBar(message: string, action: string = 'Close') {
    this._snackBar.open(message, action, {
      duration: 3000,
      panelClass: ['le-u-bg-black'],
    });
  }

  // Displays data based on the selected button
  showData(button: string) {
    this.selectedButton = button;
    this.isListVisible = true;
  }

   // Adds a selected item to the prompt
  addToPrompt(data:any){
    console.log("data==",data);
    this.isListVisible = false;
    this.promptControl.setValue(data);
    this.selectedButton = '';
  }

  // Calls the image explainability API
  imageExplainability(fileData: any) {
    const localImageExplainabilityUrl = "http://10.68.120.142:31016/api/v1/rai/helm/imageGenerate"
    this.https.post(this.imageExplainabilityUrl, fileData).subscribe((data: any) => {
      this.imageOutput = true
      this.imagePath = data.img;
      this.analyze = data
      this.imgExpl = data
      this.redactedImg = false
      this.imageAnalysePath = data.img;
      this.showSpinner = false;
      this.aesthetics = data.Score?.Aesthetics?.Aesthetics || '';
      this.aestheticScore = data.Score?.Aesthetics?.AestheticsScore || 0;
      this.alignment = (data.Score?.Image_Alignment?.AlignmentValue || '').replace(/Text-ImageAlignment$/, '');
      this.alignmentScore = data.Score?.Image_Alignment?.Probability || 0;
      this.genderBias = data.Score?.Bias?.Gender?.GenderBias || '';
      this.watermark = data.Score?.Originality?.Has_WaterMark ;
      this.originalityScore = data.Score?.Originality?.Probability || 0;
    }, error => {
      this.handleError(error)
    })

  }

  // Opens the right-side modal for safety analysis
  openRightSideModal() {
    const dialogRef = this.dialog.open(ImageReportChartComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)',
      position: {
        top: '57px',
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: {
        analyze: this.analyze,
        tenent: "Safety"
      },
    });
  }

  // Opens the fairness side modal
  openFairnessSideModal() {
    const dialogRef = this.dialog.open(FairnessSideModalComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)',
      position: {
        top: '57px',
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: this.fairnessRes.report,
    });
  }

   // Opens the explainability right-side modal
  openExplRightSideModal() {
    const dialogRef = this.dialog.open(ImageReportChartComponent, {
      width: '52vw',
      height: 'calc(100vh - 57px)', // Subtract the height of the navbar
      position: {
        top: '57px', // Position the modal below the navbar
        right: '0'
      },
      backdropClass: 'custom-backdrop',
      data: {
        analyze: this.imgExpl,
        tenent: "Explainability",
        type: "generate"
      }
    });
  }

  // Handles the form submission
  async onSubmit(data: any) {
    console.log(data);
    console.log(data.value);
    if ((!this.promptControl.valid || this.selectType == '') && !(this.imageFiles.length && this.selectType == 'explainability')) {
      this.hasError = true;
      this._snackBar.open('Please enter a prompt & select type before submitting.', '✖', {
        horizontalPosition: 'center',
        verticalPosition: 'top',
        duration: 3000,
        panelClass: ['custom-snackbar']
      });
      return;
    }
    this.resetResult();
    this.imageOutput = false;
    this.redactedImg = true
    let { prompt, portfolioName, accountName } = data.value
    this.showSpinner = true
    // const config = '{"drawings":0.5,"hentai":0.25,"neutral":0.5,"porn":0.25,"sexy":0.25}'
    // const payload = {
    //   prompt: prompt,
    //   config: config
    // }
    const fileData = new FormData();
    prompt = this.promptControl.value
    fileData.append('prompt', prompt);
    if(this.portfolioName!=''){
    fileData.append('portfolio', this.portfolioName)
    }
    if(this.accountName!=''){
    fileData.append('account', this.accountName)
    }
    
    if (this.selectType == 'explainability') {
      let queryFlag = false;
      const fileDataExp = new FormData();
      fileDataExp.append('prompt', prompt);
      if (this.isImageFileUploaded) {
        console.log("Image file uploaded",this.explainImagetype)
         queryFlag = prompt.length > 0 ? true : false;
        this.explainImagetype = "Uploaded Image"
        const fileName = this.imageFile.name;
        this.imageUrl = URL.createObjectURL(this.imageFile);
        console.log('File Name:', fileName);
        this.imageUrl = URL.createObjectURL(this.imageFile);
    const base64String = await this.convertImageToBase64(this.imageFile);
    this.rawimg = base64String.replace(/^data:image\/[a-z]+;base64,/, '');
        this.imageFileExplainAnalyse(this.imageFile, prompt,fileName,queryFlag);
        this.triggerSegmentImage2(this.imageFile,fileName)
      } else {
        this.explainImagetype = "Generated Image"
        console.log("Image file not uploaded only prompt",this.explainImagetype)
        const body = new URLSearchParams();
        body.set('prompt', prompt); // Adjust the prompt as needed
        this.imageExplainability2(body,prompt,queryFlag)
      }
      // this.imageExplainability(fileDataExp);
    }
    if (this.selectType == 'safety') {
    
      this.imageProfanity(fileData)
    }
    if(this.selectType == 'Fairness'){
      this.imageFairness(this.promptControl.value)
    }

  }

  // Calls the image profanity API
  imageProfanity(fileData: any) {
    this.https.post(this.imageGenerateUrl, fileData).subscribe((data: any) => {
    // this.https.post("http://localhost:8001/api/v1/safety/profanity/imageGenerate", fileData).subscribe((data: any) => {
      this.imageOutput = true
      this.imagePath = data.img;
      this.analyze = data.analyze
      this.imageAnalysePath = data.ORIGINAL;
      this.imageBlurred = data.BLURRED;
      this.showSpinner = false;
      this.analyzeData = {
        drawings: data.analyze.drawings,
        hentai: data.analyze.hentai,
        neutral: data.analyze.neutral,
        porn: data.analyze.porn,
        sexy: data.analyze.sexy
      };
      console.log(this.analyzeData)
    }, error => {
      this.handleError(error)
    })
  }

  // Calls the image fairness API
  imageFairness(prompt: any) {  
    const fileData = new FormData();
    fileData.append('prompt', prompt);
    this.https.post(this.imageGenerateModeration, { prompt: prompt,model: "DALL-E-2"}).subscribe((data: any) => {
      // console.log(typeof data)
      // this.imagePath = data;
      // this.imageOutput = true
      // this.imageAnalysePath = data;
      this.fairnessRes.generatedImage = data.image;
      this.callFairnessAnalysis(data.image, prompt)
    }, error => {
      this.handleError(error)
    })
  }

  // Calls the fairness analysis API
  callFairnessAnalysis(img: any,prompt: any) {
    console.log("data.image::",img)
    try {
      const byteCharacters = atob(img);
      const byteNumbers = Array.from(byteCharacters, char => char.charCodeAt(0));
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpeg' });

      const formPayload = new FormData();
      formPayload.append('prompt', prompt);
      formPayload.append('evaluator', "GPT_4o");
      formPayload.append('image', blob, 'image.jpg');
      this.https.post(this.fairness_image, formPayload).subscribe((res: any) => {
        this.fairnessRes.status = true;
        this.fairnessRes.report = res;
        console.log("fairnessRes.report", this.fairnessRes.report['Bias score'])
        this.showSpinner = false;
      }, error => {
        this.handleError(error)
      })
    } catch (error) {
      console.log(error)
    }
  }

  // Filters selected options and updates the tenant array
  viewoptions() {
    // console.log("Array===",this.selectedOptions)
    // [Privacy: true, Profanity: true, Explainability: true, FM-Moderation: true]
    const myObject = { ...this.selectedOptions };
    console.log("myObject===", myObject)
    const filteredKeys = this.filterKeysByBoolean(myObject);
    console.log("only keys", filteredKeys);
    this.tenantarr = filteredKeys
  }

  // Filters keys in an object based on boolean values
  filterKeysByBoolean(obj: Record<string, boolean>): string[] {
    return Object.keys(obj).filter((key) => obj[key]);
  }

  // Resets the form and clears all fields
  reset() {    
    this.prompt = '';
    this.portfolioName = '';
    this.accountName = '';
    this.imageOutput = false;
    this.imagePath = "";
    this.analyze = "";
    this.imageAnalysePath = "";
    this.imageBlurred = "";
    this.showSpinner = false;
    this.tenantarr = []
    this.promptControl.reset();
    this.selectedButton = '';
    this.isListVisible = false;
    this.resetValuesofFileupload();
    this.form?.reset();
    for (let option in this.selectedOptions) {
      if (this.selectedOptions.hasOwnProperty(option)) {
        this.selectedOptions[option] = false;
      }
    }
  }

  // Resets the result-related fields
  resetResult() {
    this.imageOutput = false;
    this.imagePath = '';
    this.analyze = ''
    this.imageAnalysePath = '';
    this.imageBlurred = ''
    this.imgExpl = ''
    this.fairnessRes = {  
      status: false,
      generatedImage: '',
      report: {}
    }
    
  }

  // Opens a dialog to display an image
  openDialog(data: any) {
    console.log("data===", data)
    let imageData = data;
    if (!data.startsWith('data:image/')) {
      imageData = `data:image/png;base64,${data}`; 
    }
    console.log("imageData", imageData)
    this.dialog.open(ImageDialogComponent, {
      data: { image: imageData, flag: true},
       backdropClass: 'custom-backdrop'
    });
  }

  // Toggles the collapse state of a panel
  togglePanel(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  // Handles image file selection for upload
  async fileBrowseHandlerImageFile(file: any) {
    console.log("FILE HANDLER IMAGE FILE")
    this.prepareImageFileList(file.target.files);
    this.imageFileList = this.imageFiles;
    this.imageFile = this.imageFiles[0];
    console.log('Raw Image:', this.rawimg);
    const files = file.target.files;
    if (!files[0].type.startsWith('image/')) {
      this.imageFiles = [];
      this.imageFileList = [];
      this.selectedImageFileName = '';
      this.imagePath = '';
      this.isImageFileUploaded = false; // Set flag to false if the file is not an image
      const message = 'Please upload an image file';
      const action = 'Close';
      this._snackBar.open(message, action, {
        duration: 3000,
        horizontalPosition: 'left',
        panelClass: ['le-u-bg-black'],
      });
      return;
    }
    if (files.length > 0) {
      this.selectedImageFileName = files[0].name;
      this.isImageFileUploaded = true; // Set flag to true if the file is successfully uploaded
    }
    const reader = new FileReader();
    this.imagePath = files;
    reader.readAsDataURL(files[0]);
    reader.onload = (_event) => {
      const base64String = reader.result as string;
      this.imgShowUrl = base64String;
    };
    // this.hallucinationSwitchCheck = false // making file upload as false
  }
  
  // Prepares the list of image files for upload
  prepareImageFileList(files: Array<any>) {
    this.imageFiles = Array.from(files);
  }
  
  // Removes the selected image file
  removeImageFile() {
    console.log("REMOVE IMAGE FILE")
    this.imageFiles = [];
    this.isImageFileUploaded = false; // Reset flag when the file is removed
  }

   // Resets the values related to file upload
  resetValuesofFileupload() {
    this.imageFileList = [];
    this.imageFile = '';
    this.selectedImageFileName = '';
    this.imageFiles = [];
    this.imgShowUrl = '';
    this.isImageFileUploaded = false;
  }
// to check if explainability is slected in the radio if slected then only show the image file upload options

  toggleTooltip() {
    this.tooltip.show();
    setTimeout(() => {
      this.tooltip.hide();
    }, 2000); // Hide the tooltip after 2 seconds
  }
  ngAfterViewInit() {
    console.log('Tooltip initialized:', this.tooltip);
  }

  // Method to handle explainability change
  onExplainabilityChange(value: string) {
    this.isExplainabilitySelected = (value === 'explainability');
    if (this.isExplainabilitySelected) {
      setTimeout(() => {
        this.toggleTooltip();
      }, 100); // Delay of 100 milliseconds
    }
    this.resetResult();
  }

  // Calls the image explainability API with additional parameters
  imageExplainability2(body: any,prompt:any,queryFlag:any) {
    // const headers = new HttpHeaders({
    //   'Content-Type': 'application/x-www-form-urlencoded',
    //   'accept': 'application/json'
    // });

    this.https.post(this.imageGenerateModeration,{ prompt: prompt,model: "DALL-E-2"})
      .subscribe({
        next: (data: any) => {
          // Assuming the response is an HTML document, parse it to extract the image URL
          this._snackBar.open('Image generated successfully.', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
            panelClass: ['custom-snackbar']
          });
          this.rawimg = data.image; // Assign the base64 string to x
          
          this.imageUrl = `data:image/png;base64,${data.image}`; // Assuming the image is a PNG. Adjust the MIME type if necessary.
          let imgblob = this.base64ToBlob(data.image, 'image/png');        
          this.imageFileExplainAnalyse(imgblob, prompt,"image.png",queryFlag);
          this.triggerSegmentImage(this.rawimg);  // Call the second API function
        }, error: (error) => {
          console.error('Error:', error);
        }
      });
  }

  // Triggers the superpixel segmentation API
  triggerSegmentImage(base64Image:string) {
    // Prepare the base64 string as a file
    const byteCharacters = atob(base64Image);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const file = new Blob([byteArray], { type: 'image/png' }); // Adjust the MIME type as needed

    // Create FormData and append the file
    const formData = new FormData();
    formData.append('file', file, 'image.png'); 

    // Call the Second API
    this.https.post(this.image_superpixel_segment_image, formData)
    .subscribe({
      next: (response:any) => {
        this.image = `data:image/png;base64,${response.superpixel_data}`;
        console.log('Response:', this.image);
      }, error: (error) =>{
        console.error('Error:', error);
      }
    });
  }
  triggerSegmentImage2(file:any,name:any) {
    // Prepare the base64 string as a file
    

    // Create FormData and append the file
    const formData = new FormData();
    formData.append('file', file, name); 

    // Call the Second API
    this.https.post(this.image_superpixel_segment_image, formData)
    .subscribe({
      next: (response:any) => {
        this.image = `data:image/png;base64,${response.superpixel_data}`;
        console.log('Response:', this.image);
      }, error: (error) =>{
        console.error('Error:', error);
      }
    });
  }

  // Method to handle image file explain anazlyse
  imageFileExplainAnalyse(imgFile: any,prompt:any,fileName:any,queryFlag:any) {
    const formData = new FormData();
    formData.append('image', imgFile,fileName); // Assuming you have a file input and selectedFile is set
    formData.append('evaluator', 'GPT_4o');
    formData.append('prompt', prompt);
    formData.append('query_flag', queryFlag);
    const headers = new HttpHeaders({
      'accept': 'multipart/form-data'
    });
  
    this.https.post(this.image_explainability_analyze, formData, { headers })
      .subscribe({
        next: (response) => {
          console.log('Response:', response);
          this.explain_analyse_res = response;
          this.showSpinner = false;
          this.imageOutput = true;
          this._snackBar.open('Image analysis successful.', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
            panelClass: ['custom-snackbar']
          });
        },
        error: (error) => {
          this.showSpinner = false;
          console.error('Error:', error);
          this._snackBar.open('Image analysis failed.', '✖', {
            horizontalPosition: 'center',
            verticalPosition: 'top',
            duration: 3000,
            panelClass: ['custom-snackbar']
          });
        }
      });
  }

  // Converts a base64 string to a Blob object
  base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = Array.from(byteCharacters, char => char.charCodeAt(0));
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  // Converts an image file to a base64 string
  convertImageToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  }

  async handleImageConversion() {
    try {
      const base64String = await this.convertImageToBase64(this.imageFile);
      console.log('Base64 String:', base64String);
      // You can now use the base64String as needed
    } catch (error) {
      console.error('Error converting image to Base64:', error);
    }
  }
}
