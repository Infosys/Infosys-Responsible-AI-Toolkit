/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Component, OnDestroy } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';

import { AlertError } from './alert-error.model';
import { Alert, AlertService } from '../../../app/core/util/alert.service';
import { EventManager, EventWithContent } from '../../../app/core/util/event-manager.service';

@Component({
  selector: 'jhi-alert-error',
  templateUrl: './alert-error.component.html',
})
export class AlertErrorComponent implements OnDestroy {
  alerts: Alert[] = [];
  errorListener: Subscription;
  httpErrorListener: Subscription;

  constructor(private alertService: AlertService, private eventManager: EventManager) {
    this.errorListener = eventManager.subscribe('angularJwtfeApp.error', (response: EventWithContent<unknown> | string) => {
      const errorResponse = (response as EventWithContent<AlertError>).content;
      this.addErrorAlert(errorResponse.message);
    });

    this.httpErrorListener = eventManager.subscribe('angularJwtfeApp.httpError', (response: EventWithContent<unknown> | string) => {
      const httpErrorResponse = (response as EventWithContent<HttpErrorResponse>).content;
      switch (httpErrorResponse.status) {
        // connection refused, server not reachable
        case 0:
          this.addErrorAlert('Server not reachable');
          break;

        case 400: {
          const arr = httpErrorResponse.headers.keys();
          let errorHeader: string | null = null;
          for (const entry of arr) {
            if (entry.toLowerCase().endsWith('app-error')) {
              errorHeader = httpErrorResponse.headers.get(entry);
            }
          }
          if (errorHeader) {
            this.addErrorAlert(errorHeader);
          } else if (httpErrorResponse.error !== '' && httpErrorResponse.error.fieldErrors) {
            const fieldErrors = httpErrorResponse.error.fieldErrors;
            for (const fieldError of fieldErrors) {
              if (['Min', 'Max', 'DecimalMin', 'DecimalMax'].includes(fieldError.message)) {
                fieldError.message = 'Size';
              }
              // convert 'something[14].other[4].id' to 'something[].other[].id' so translations can be written to it
              const convertedField: string = fieldError.field.replace(/\[\d*\]/g, '[]');
              const fieldName: string = convertedField.charAt(0).toUpperCase() + convertedField.slice(1);
              this.addErrorAlert(`Error on field "${fieldName}"`);
            }
          } else if (httpErrorResponse.error !== '' && httpErrorResponse.error.message) {
            this.addErrorAlert(httpErrorResponse.error.detail ?? httpErrorResponse.error.message);
          } else {
            this.addErrorAlert(httpErrorResponse.error);
          }
          break;
        }

        case 404:
          this.addErrorAlert('Not found');
          break;

        default:
          if (httpErrorResponse.error !== '' && httpErrorResponse.error.message) {
            this.addErrorAlert(httpErrorResponse.error.detail ?? httpErrorResponse.error.message);
          } else {
            this.addErrorAlert(httpErrorResponse.error);
          }
      }
    });
  }

  /**
   * this menthod is used to set classes for the alert based on the alert type and position
   * @param alert   The alert object containing the type and position
   */
  setClasses(alert: Alert): { [key: string]: boolean } {
    const classes = { 'jhi-toast': Boolean(alert.toast) };
    if (alert.position) {
      return { ...classes, [alert.position]: true };
    }
    return classes;
  }

  ngOnDestroy(): void {
    this.eventManager.destroy(this.errorListener);
    this.eventManager.destroy(this.httpErrorListener);
  }

  /**
   * 
   * @param alert The alert object to be closed
   * This method is called when the close button of the alert is clicked.
   */
  close(alert: Alert): void {
    alert.close?.(this.alerts);
  }

  /**
   * This method is used to add error alert messages to the alert service.
   * @param message The error message to be added to the alert service.
   */
  private addErrorAlert(message?: string): void {
    this.alertService.addAlert({ type: 'danger', message }, this.alerts);
  }
}
