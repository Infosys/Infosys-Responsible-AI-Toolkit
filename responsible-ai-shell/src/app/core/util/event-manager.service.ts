/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { Injectable } from '@angular/core';
import { Observable, Observer, Subscription } from 'rxjs';
import { filter, share } from 'rxjs/operators';

export class EventWithContent<T> {
  constructor(public name: string, public content: T) {}
}

/**
 * An utility class to manage RX events
 */
@Injectable({
  providedIn: 'root',
})
export class EventManager {
  observable: Observable<EventWithContent<unknown> | string>;
  observer?: Observer<EventWithContent<unknown> | string>;

  constructor() {
    this.observable = new Observable((observer: Observer<EventWithContent<unknown> | string>) => {
      this.observer = observer;
    }).pipe(share());
  }

  /**
   * Method to broadcast the event to observer
   */
  broadcast(event: EventWithContent<unknown> | string): void {
    if (this.observer) {
      this.observer.next(event);
    }
  }

  /**
   * Method to subscribe to an event with callback
   * @param eventNames  Single event name or array of event names to what subscribe
   * @param callback    Callback to run when the event occurs
   */
  subscribe(eventNames: string | string[], callback: (event: EventWithContent<unknown> | string) => void): Subscription {
    if (typeof eventNames === 'string') {
      eventNames = [eventNames];
    }
    return this.observable
      .pipe(
        filter((event: EventWithContent<unknown> | string) => {
          for (const eventName of eventNames) {
            if ((typeof event === 'string' && event === eventName) || (typeof event !== 'string' && event.name === eventName)) {
              return true;
            }
          }
          return false;
        })
      )
      .subscribe(callback);
  }

  /**
   * Method to unsubscribe the subscription
   */
  destroy(subscriber: Subscription): void {
    subscriber.unsubscribe();
  }
}
