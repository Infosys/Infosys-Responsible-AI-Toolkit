/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable, SecurityContext, NgZone } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

export type AlertType = 'success' | 'danger' | 'warning' | 'info';

export interface Alert {
  id?: number;
  type: AlertType;
  message?: string;
  timeout?: number;
  toast?: boolean;
  position?: string;
  close?: (alerts: Alert[]) => void;
}

@Injectable({
  providedIn: 'root',
})
export class AlertService {
  timeout = 5000;
  toast = false;
  position = 'top right';

  // unique id for each alert. Starts from 0.
  private alertId = 0;
  private alerts: Alert[] = [];

  constructor(private sanitizer: DomSanitizer, private ngZone: NgZone) {}

  /**
   * @description this method is clear all alerts from the alert array.
   * @returns  void
   */
  clear(): void {
    this.alerts = [];
  }

  /**
   * @description this method is used to get the alerts array.
   * @returns  Alert[]
   */
  get(): Alert[] {
    return this.alerts;
  }

  /**
   * Adds alert to alerts array and returns added alert.
   * @param alert      Alert to add. If `timeout`, `toast` or `position` is missing then applying default value.
   * @param extAlerts  If missing then adding `alert` to `AlertService` internal array and alerts can be retrieved by `get()`.
   *                   Else adding `alert` to `extAlerts`.
   * @returns  Added alert
   */
  addAlert(alert: Alert, extAlerts?: Alert[]): Alert {
    alert.id = this.alertId++;

    alert.message = this.sanitizer.sanitize(SecurityContext.HTML, alert.message ?? '') ?? '';
    alert.timeout = alert.timeout ?? this.timeout;
    alert.toast = alert.toast ?? this.toast;
    alert.position = alert.position ?? this.position;
    alert.close = (alertsArray: Alert[]) => this.closeAlert(alert.id!, alertsArray);

    (extAlerts ?? this.alerts).push(alert);

    if (alert.timeout > 0) {
      // Workaround protractor waiting for setTimeout.
      // Reference https://www.protractortest.org/#/timeouts
      this.ngZone.runOutsideAngular(() => {
        setTimeout(() => {
          this.ngZone.run(() => {
            this.closeAlert(alert.id!, extAlerts ?? this.alerts);
          });
        }, alert.timeout);
      });
    }

    return alert;
  }

  /**
   * @description this method is used to close the alert.
   * @param alertId  alert id to close.
   * @param extAlerts  If missing then removing alert from `AlertService` internal array and alerts can be retrieved by `get()`.
   *                   Else removing alert from `extAlerts`.
   */
  private closeAlert(alertId: number, extAlerts?: Alert[]): void {
    const alerts = extAlerts ?? this.alerts;
    const alertIndex = alerts.map(alert => alert.id).indexOf(alertId);
    // if found alert then remove
    if (alertIndex >= 0) {
      alerts.splice(alertIndex, 1);
    }
  }
}
