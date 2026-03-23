'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import base64
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import pydicom
from PIL import Image
from presidio_image_redactor import DicomImageRedactorEngine
import cv2
from io import BytesIO
# def compare_dicom_images(
#     instance_original: pydicom.dataset.FileDataset,
#     instance_redacted: pydicom.dataset.FileDataset,
#     figsize: tuple = (11, 11)
# ) -> None:
#     """Display the DICOM pixel arrays of both original and redacted as images.

#     Args:
#         instance_original (pydicom.dataset.FileDataset): A single DICOM instance (with text PHI).
#         instance_redacted (pydicom.dataset.FileDataset): A single DICOM instance (redacted PHI).
#         figsize (tuple): Figure size in inches (width, height).
#     """
#     _, ax = plt.subplots(1, 2, figsize=figsize)
#     print("DICOM")
#     ax[0].imshow(instance_original.pixel_array, cmap="gray")
#     ax[0].set_title('Original')
#     ax[1].imshow(instance_redacted.pixel_array, cmap="gray")
#     print(instance_redacted)
#     ax[1].set_title('Redacted')
#     plt.imshow(instance_redacted.pixel_array, cmap=plt.cm.bone)  # set the color map to bone
#     plt.show()
    
    
class DICOM:
    def dcmToPng(dcmObj):
        plt.imshow(dcmObj.pixel_array,cmap=plt.cm.bone)
        plt.axis('off')
        b=BytesIO()
        plt.savefig(b,format='png', bbox_inches='tight', pad_inches=0)
        b.seek(0)
        return base64.b64encode(b.getvalue())
        
    # def dicomReader():    
    #     engine = DicomImageRedactorEngine()
    #     op=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\privacy\temp\0_ORIGINAL.dcm"
    #     dicom_instance = pydicom.dcmread(op)
    #     print(type(dicom_instance))
    #     redacted_dicom_instance = engine.redact(dicom_instance, fill="contrast")
    #     # compare_dicom_images(dicom_instance, redacted_dicom_instance)
    #     # print(type(redacted_dicom_instance))
    #     # plt.imshow(redacted_dicom_instance.pixel_array, cmap=plt.cm.bone)  # set the color map to bone
    #     # plt.show()
    #     # dd=BytesIO()
    #     # redacted_dicom_instance.save_as(dd)
    #     image = redacted_dicom_instance.pixel_array
    #     # x=Image.fromarray(image)
    #     p=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\dicomResult.png"
    #     o=r"C:\WORK\GIT\responsible-ai-privacy\responsible-ai-privacy\src\dicomInput.png"
        
    #     # plt.imsave(p,image,cmap=plt.cm.bone)
    #     # plt.imsave(o,dicom_instance.pixel_array,cmap=plt.cm.bone)
    #     plt.imshow(dicom_instance.pixel_array,cmap=plt.cm.bone)
    #     b=BytesIO()
    #     plt.savefig(b,format='png')
    #     b.seek(0)
    #     # image=Image.open(b)
    #     # image.show()
    #     print(image)
    #     # d=redacted_dicom_instance.tobytes()
    #     # f=open(p,'rb')
    #     # of=open(o,'rb')
    #     print(b.getvalue())
    #     redicated=base64.b64encode(b.getvalue())
    #     # original=base64.b64encode(of.read())
    #     saveImage.saveImg(redicated)
    #     obj=image
    #     # obj={"original":original,"anonymize":redicated}
    #     return redicated
    
    def readDicom(payload):
        # print(type(payload))
        # print(payload.file)
        engine = DicomImageRedactorEngine()
        dicom_instance = pydicom.dcmread(payload.file)
        print(type(dicom_instance))
        redacted_dicom_instance = engine.redact(dicom_instance, fill="contrast")
        # compare_dicom_images(dicom_instance, redacted_dicom_instance)
        
        original=DICOM.dcmToPng(dicom_instance)
        redacted=DICOM.dcmToPng(redacted_dicom_instance)
        
        obj={"original":original,"anonymize":redacted}
        return obj


class saveImage:
    def saveImg(img_data):
        
        
        with open("file.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        