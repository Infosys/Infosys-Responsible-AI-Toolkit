/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RecognizersService } from './recognizers.service';
import { map } from 'rxjs/operators';
export class methods {


    constructor(private https: HttpClient, public _snackBar: MatSnackBar, private recognizerService: RecognizersService) { }

    // static hi(): string {
    //     // Your date formatting logic here
    //     return 'Hello world';
    // }
    delete(api: any, headers: any, api2: any) {
        console.log("in delete method")

        // this.https.delete(this.admin_list_rec_get_list_Delete_DataRecogGrp, options).subscribe
        this.recognizerService.deleteRecognizer(api, headers).subscribe
            ((res: any) => {
                console.log("delete Resonce" + res.status)
                if (res.status === "True") {

                    // this.https.get(this.admin_list_rec_get_list).subscribe
                    //     ((res: any) => {
                    //         this.dataSource = []
                    //         // this.showSpinner1=false;

                    //         // console.log("data sent to database" + res.PtrnList)
                    //         // this.dataSource = res.RecogList
                    //         res.RecogList.forEach((i: any) => {
                    //             console.log(i.isPreDefined + "i print")
                    //             if (i.isPreDefined == "No") {
                    //                 this.dataSource.push(i)
                    //             }

                    //         });

                    //     })

                    //
                    
                    const message = "Data Group Deleted Successfully"
                    const action = "Close"
                    // this._snackBar.open(message, action, {
                    //     duration: 1000,
                    //     panelClass: ['le-u-bg-black'],
                    // });
                    return this.getDataSource(api2);
                } else if (res.status === "False") {
                    const message = "Data Group Deletion was unsucessful"
                    const action = "Close"
                    // this._snackBar.open(message, action, {
                    //     duration: 1000,
                    //     panelClass: ['le-u-bg-black'],
                    // });
                    return this.getDataSource(api2);
                }
                return this.getDataSource(api2);
            }, error => {
                // You can access status:
                console.log(error.status);
                if (error.status == 430) {
                    console.log(error.error.detail)
                    console.log(error)
                    const message = error.error.detail
                    const action = "Close"
                    // this._snackBar.open(message, action, {
                    //     duration: 3000,
                    //     horizontalPosition: 'left',
                    //     panelClass: ['le-u-bg-black'],
                    // });
                } else {

                    // console.log(error.error.detail)
                    console.log(error)
                    const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
                    const action = "Close"
                    // this._snackBar.open(message, action, {
                    //     duration: 3000,
                    //     horizontalPosition: 'left',
                    //     panelClass: ['le-u-bg-black'],
                    // });

                }
            })

    }

    //  getRecognizers(api: any) {
    //     let dataSource: any = []
    //     dataSource =  this.https.get(api).subscribe((res: any) => {
    //             let dataSource1:any = []

    //             res.RecogList.forEach((i: any) => {
    //                 console.log(i.isPreDefined + "i print")
    //                 if (i.isPreDefined == "No") {
    //                     dataSource1.push(i)
    //                 }

    //             });

    //             return dataSource1





    //         }, error => {
    //             // You can access status:
    //             console.log(error.status);


    //             // console.log(error.error.detail)
    //             console.log(error)
    //             const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
    //             const action = "Close"
    //             this._snackBar.open(message, action, {
    //                 duration: 3000,
    //                 horizontalPosition: 'left',
    //                 panelClass: ['le-u-bg-black'],
    //             });


    //         })

    //         return dataSource
    // }

    // 

    // getRecognizers(api: any) {
    //     let dataSource: any = []
    //     dataSource = this.http.get(api).subscribe({
    //         next: (res: any) => {
    //             let dataSource1: any = []

    //             res.RecogList.forEach((i: any) => {
    //                 console.log(i.isPreDefined + "i print")
    //                 if (i.isPreDefined == "No") {
    //                     dataSource1.push(i)
    //                 }
    //             });

    //             return dataSource1
    //         },
    //         error: (error) => {
    //             console.log(error.status);
    //             console.log(error)
    //             const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed"
    //             const action = "Close"
    //             this._snackBar.open(message, action, {
    //                 duration: 3000,
    //                 horizontalPosition: 'left',
    //                 panelClass: ['le-u-bg-black'],
    //             });
    //         }
    //     })

    //     return dataSource
    // }



    async getDataSource(api: string): Promise<any[]> {
        try {
            const res: any = await this.https.get(api).pipe(map((res: any) => {
                let dataSource: any = [];
                res.RecogList.forEach((i: any) => {
                    console.log(i.isPreDefined + "i print");
                    if (i.isPreDefined == "No") {
                        dataSource.push(i);
                    }
                });
                return dataSource;
            })).toPromise();
            return res;
        } catch (error: any) {
            console.log(error.status);
            console.log(error);
            const message = (error.error && (error.error.detail || error.error.message)) || "The Api has failed";
            const action = "Close";
            this._snackBar.open(message, action, {
                duration: 3000,
                horizontalPosition: 'left',
                panelClass: ['le-u-bg-black'],
            });
            throw error; // re-throw the error so it can be handled by the caller
        }
    }

}


// 


