/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
var url = "http://10.66.155.104" // goblal ip

export const environment = {
  production: true,
  api: "http://prod.api.com",
  build_type: "prod",

  // master link for all ip and port no
  master_url: url+":30016/api/v1/rai/admin/ConfigApi",
  //***** priAnzApiUrl is for Privacy Analyze API */
  priAnzApiUrl2: "/api/v1/privacy/pii/analyze",
  //***** priAnonApiUrl is for Privacy Anonymize API */
  priAnonApiUrl2: "/api/v1/privacy/pii/anonymize",
  //***** profAnzApUrli is for Profanity Analyze API */
  profAnzApiUrl: "/api/v1/safety/profanity/analyze",
  //***** profCenApiUrl is for Profanity Censor API */
  profCenApiUrl: "/api/v1/safety/profanity/censor",
  //***** explApiUrl is for Explainability API */
  explApiUrl: "https://api-aicloud.ad.infosys.com/api/v1/explainability/local/explain",
  //***** bloomApiUrl is for Bloom API */
  bloomApiUrl: "/api/v1/text_generator/bloom",



  //API FOR IMAGE COMPONENT
  //***** privAnonImgUrl is for Privacy Anonymize API */
  privAnonImgUrl2: "/api/v1/privacy/pii/image/anonymize",
  //***** privAnzImgUrl is for Privacy Analyze API */
  privAnzImgUrl2: "/api/v1/privacy/pii/image/analyze",

  //***** privVerImgUrl is for Privacy Verify API */
  privVerImgUrl: "/api/v1/privacy/pii/image/verify",
  //***** privVerImgUrl is for Privacy Verify API */
  privHashImgUrl: "/api/v1/privacy/pii/image/hashify",

  //***** fairnesApi is for Ai Fairness API in Ai fairness component*/
  fairnesApi: "/api/v1/fairness/bias/analyze",
  fairnessGetDatasetApi: "/api/v1/fairness/bias/getDataset",
  fairnessGetAttributeApi: "/api/v1/fairness/bias/getAttributes",

  //API FOR Batch-process COMPONENT
  //***** getDoccuments is for getting the table of documents in  batch-process component*/
  getDoccuments: "/bulkprocessing/docDtl",
  //***** postTable1 is for getting the table of documents in  batch-process component*/
  postTable1: "/bulkprocessing/docProcDtl",
  //***** postTable2 is for getting the table of documents in Ai batch-process component*/
  postTable2: "/bulkprocessing/pageDtl",
  //***** postPDF is for posting multiple pdf in  batch-process component*/
  postPDF: "/bulkprocessing/file",
  //***** resultJson is for showing responce in json format batch-process componentz*/
  resultJson: "/bulkprocessing/data",
  //***** report zip is for downloading report pdf in  batch-process componentz*/
  downResultFile: "/bulkprocessing/documentReport",

    // Api for ppt Processing (GPT USE CASE)
    pptUrl:"/docProcessing/process",
  
    getPpt:"/docProcessing/getFiles",
  

  // API FOR Fm component 

  ///***** fm_api  is for generating moderation response for fm componentz*/
  fm_api: "/api/v1/moderationlayer/completions",
  //***** fm_api_openAi  is for generating moderation response for fm componentz*/
  fm_api_openAi: "/api/v1/moderationlayer/openai",
  // ***** fm_api_time  is for generating moderation time List for fm componentz*/
  fm_api_time: "/api/v1/moderationlayer/ModerationTime",
  //***** fm_api_privacyShield  is for generating privacy list response for fm componentz*/
  // fm_api_privacyShield : url +":30002/api/v1/privacy/pii/privacyShield",// deepak
  fm_api_privacyShield: "/api/v1/moderationlayer/PrivacyPopup",// qutub
  fm_api_inf_ProfanityPopup: "/api/v1/moderationlayer/ProfanityPopup",
  fm_api_inf_ToxicityPopup: "/api/v1/moderationlayer/ToxicityPopup",

  // Api for Admin component sub component pattern recogniton
  //***** admin_pattern_rec  is for sending pattenr for  admin sub patttern componentz*/
  admin_pattern_rec: "/api/v1/rai/admin/ptrnRecognise",
  //***** admin_pattern_rec_get_list  is for generating patten list for admin sub patttern componentz*/
  admin_pattern_rec_get_list: "/api/v1/rai/admin/ptrnRecogniselist",
  /***** admin_pattern_rec_update_list  is for updating patten list data for admin sub patttern componentz*/
  admin_pattern_rec_update_list: "/api/v1/rai/admin/ptrnRecogniseUpdate",
  /***** admin_pattern_rec_delete_list  is for delete patten list data for admin sub patttern componentz*/
  admin_pattern_rec_delete_list: "/api/v1/rai/admin/ptrnRecogniseDelete",


  // Api for Admin component sub component list recogniton
  //***** admin_list_rec is for sending pattenr for  admin sub list  componentz*/
  admin_list_rec: "/api/v1/rai/admin/DataRecogGrp",
  //***** admin_list_rec_get_list  is for getting  response for  admin sub list  componentz*/
  admin_list_rec_get_list: "/api/v1/rai/admin/DataRecogGrplist",
  //***** admin_list_rec_get_list_DataRecogGrpEntites  is for getting  response for  admin sub list componentz*/
  admin_list_rec_get_list_DataRecogGrpEntites: "/api/v1/rai/admin/DataRecogGrpEntites",
  //***** admin_list_rec_get_list_Update_DataRecogGrpEntity  is for updating  response for  admin sub list componentz*/
  admin_list_rec_get_list_Update_DataRecogGrpEntity: "/api/v1/rai/admin/DataEntitesUpdate",
  //***** admin_list_rec_get_list_Update_DataRecogGrp  is for updating  response for  admin sub list componentz*/
  admin_list_rec_get_list_Update_DataRecogGrp: "/api/v1/rai/admin/DataGrpUpdate",
  //***** admin_list_rec_get_list_Update_AddnewlistItem  is for updating  response for  admin sub list componentz*/
  admin_list_rec_get_list_Update_AddnewlistItem: "/api/v1/rai/admin/DataEntityAdd",
  //***** admin_list_rec_get_list_Delete_DataRecogGrp  is for deleting  response for  admin sub list componentz*/
  admin_list_rec_get_list_Delete_DataRecogGrp: "/api/v1/rai/admin/DataRecogGrpDelete",
  //***** admin_list_rec_get_list_Delete_DataRecogGrpEntites  is for deleting  response for fm componentz*/
  admin_list_rec_get_list_Delete_DataRecogGrpEntites: "/api/v1/rai/admin/DataRecogEntityDelete",







  // Api for Admin component sub component Account recogniton
  //***** admin_list_AccountMaping_AccMasterentry  is for sending  response for  admin sub account componentz*/
  admin_list_AccountMaping_AccMasterentry: "/api/v1/rai/admin/AccMasterEntry",
  //***** admin_list_AccountMaping_AccMasterList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList: "/api/v1/rai/admin/AccMasterList",
  //***** admin_list_AccountMaping_AccMasterList_pattentList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList_pattentList: "/api/v1/rai/admin/AccPtrnList",
  //***** admin_list_AccountMaping_AccMasterList_dataList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList_dataList: "/api/v1/rai/admin/AccDataList",
  //***** admin_list_AccountMaping_AccMasterList_dataList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList_Delete: "/api/v1/rai/admin/AccMasterDelete",
  //***** admin_list_AccountMaping_AccMasterList_dataList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList_Delete_Data: "/api/v1/rai/admin/AccDataDelete",
  //***** admin_list_AccountMaping_AccMasterList_dataList  is for generating  response for admin sub account componentz*/
  admin_list_AccountMaping_AccMasterList_Update_Data: "/api/v1/rai/admin/AccEntityAdd",
  //***** admin_list_AccountMaping_Acc_PrivacyEncrypt  is for encrypting reconizers for admin sub account componentz*/
  admin_list_AccountMaping_Acc_PrivacyEncrypt: "/api/v1/rai/admin/PrivacyEncrypt",
  admin_list_AccountMaping_Acc_ThresholdUpdate: "/api/v1/rai/admin/ThresholdUpdate",
  admin_fm_admin_UserRole : "/api/v1/rai/admin/userRole",
  admin_fm_admin_get_OpenAiStatusandRoll : "/api/v1/rai/admin/getOpenAI",
  admin_fm_admin_Update_OpenAiStatus : "/api/v1/rai/admin/UpdateOpenAI",



  // Api for security
//** lists model names */
security_modelNames: "/Security/model/get",
//**create new model */
security_createNew:"/Security/Model/add",
//** activate model */
security_activateNew:"/Security/select/model",
//** generate assessment */
security_generate_assessment:"/Security/select/attack",

};