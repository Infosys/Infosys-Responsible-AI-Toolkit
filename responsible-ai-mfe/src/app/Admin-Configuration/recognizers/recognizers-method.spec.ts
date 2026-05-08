/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { of, throwError } from 'rxjs';

import { methods } from './recognizers-method';
import { RecognizersService } from './recognizers.service';

describe('methods', () => {
  let methodsInstance: methods;
  let httpMock: HttpTestingController;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let recognizerService: jasmine.SpyObj<RecognizersService>;
  let httpClient: HttpClient;

  beforeEach(() => {
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const recognizerServiceSpy = jasmine.createSpyObj('RecognizersService', ['deleteRecognizer']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, MatSnackBarModule],
      providers: [
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: RecognizersService, useValue: recognizerServiceSpy }
      ]
    });

    httpMock = TestBed.inject(HttpTestingController);
    httpClient = TestBed.inject(HttpClient);
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    recognizerService = TestBed.inject(RecognizersService) as jasmine.SpyObj<RecognizersService>;
    
    methodsInstance = new methods(httpClient, snackBar, recognizerService);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create an instance', () => {
    expect(methodsInstance).toBeTruthy();
  });

  describe('delete method', () => {
    const mockApi = 'http://test.com/delete';
    const mockHeaders = { Authorization: 'Bearer token' };
    const mockApi2 = 'http://test.com/reclist';

    it('should successfully delete recognizer when status is True', (done) => {
      const mockResponse = { status: 'True' };
      const mockRecogList = {
        RecogList: [
          { isPreDefined: 'No', id: 1, name: 'Recognizer1' },
          { isPreDefined: 'Yes', id: 2, name: 'Recognizer2' },
          { isPreDefined: 'No', id: 3, name: 'Recognizer3' }
        ]
      };

      recognizerService.deleteRecognizer.and.returnValue(of(mockResponse));
      spyOn(methodsInstance, 'getDataSource').and.returnValue(Promise.resolve([
        { isPreDefined: 'No', id: 1, name: 'Recognizer1' },
        { isPreDefined: 'No', id: 3, name: 'Recognizer3' }
      ]));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        expect(methodsInstance.getDataSource).toHaveBeenCalledWith(mockApi2);
        done();
      }, 100);
    });

    it('should handle delete when status is False', (done) => {
      const mockResponse = { status: 'False' };

      recognizerService.deleteRecognizer.and.returnValue(of(mockResponse));
      spyOn(methodsInstance, 'getDataSource').and.returnValue(Promise.resolve([]));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        expect(methodsInstance.getDataSource).toHaveBeenCalledWith(mockApi2);
        done();
      }, 100);
    });

    it('should handle delete when status is neither True nor False', (done) => {
      const mockResponse = { status: 'Unknown' };

      recognizerService.deleteRecognizer.and.returnValue(of(mockResponse));
      spyOn(methodsInstance, 'getDataSource').and.returnValue(Promise.resolve([]));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        expect(methodsInstance.getDataSource).toHaveBeenCalledWith(mockApi2);
        done();
      }, 100);
    });

    it('should handle error with status 430', (done) => {
      const errorResponse = {
        status: 430,
        error: {
          detail: 'Custom error message'
        }
      };

      recognizerService.deleteRecognizer.and.returnValue(throwError(errorResponse));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        done();
      }, 100);
    });

    it('should handle error with detail message', (done) => {
      const errorResponse = {
        status: 500,
        error: {
          detail: 'Server error detail'
        }
      };

      recognizerService.deleteRecognizer.and.returnValue(throwError(errorResponse));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        done();
      }, 100);
    });

    it('should handle error with message property', (done) => {
      const errorResponse = {
        status: 400,
        error: {
          message: 'Bad request message'
        }
      };

      recognizerService.deleteRecognizer.and.returnValue(throwError(errorResponse));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        done();
      }, 100);
    });

    it('should handle error with default message', (done) => {
      const errorResponse = {
        status: 500,
        error: {}
      };

      recognizerService.deleteRecognizer.and.returnValue(throwError(errorResponse));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      setTimeout(() => {
        expect(recognizerService.deleteRecognizer).toHaveBeenCalledWith(mockApi, mockHeaders);
        done();
      }, 100);
    });

    it('should log console messages on delete', () => {
      const mockResponse = { status: 'True' };
      spyOn(console, 'log');
      
      recognizerService.deleteRecognizer.and.returnValue(of(mockResponse));
      spyOn(methodsInstance, 'getDataSource').and.returnValue(Promise.resolve([]));

      methodsInstance.delete(mockApi, mockHeaders, mockApi2);

      expect(console.log).toHaveBeenCalledWith('in delete method');
    });
  });

  describe('getDataSource method', () => {
    const mockApi = 'http://test.com/reclist';

    it('should return filtered data source with only non-predefined recognizers', async () => {
      const mockResponse = {
        RecogList: [
          { isPreDefined: 'No', id: 1, name: 'Custom1' },
          { isPreDefined: 'Yes', id: 2, name: 'Predefined1' },
          { isPreDefined: 'No', id: 3, name: 'Custom2' },
          { isPreDefined: 'Yes', id: 4, name: 'Predefined2' }
        ]
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);

      const result = await promise;
      
      expect(result.length).toBe(2);
      expect(result[0].name).toBe('Custom1');
      expect(result[1].name).toBe('Custom2');
      expect(result.every((item: any) => item.isPreDefined === 'No')).toBe(true);
    });

    it('should return empty array when all recognizers are predefined', async () => {
      const mockResponse = {
        RecogList: [
          { isPreDefined: 'Yes', id: 1, name: 'Predefined1' },
          { isPreDefined: 'Yes', id: 2, name: 'Predefined2' }
        ]
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);

      const result = await promise;
      
      expect(result.length).toBe(0);
    });

    it('should return all items when none are predefined', async () => {
      const mockResponse = {
        RecogList: [
          { isPreDefined: 'No', id: 1, name: 'Custom1' },
          { isPreDefined: 'No', id: 2, name: 'Custom2' }
        ]
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);

      const result = await promise;
      
      expect(result.length).toBe(2);
    });

    it('should handle empty RecogList', async () => {
      const mockResponse = {
        RecogList: []
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);

      const result = await promise;
      
      expect(result.length).toBe(0);
    });

    it('should handle HTTP error and show snackbar with detail message', async () => {
      const errorResponse = {
        error: {
          detail: 'API error detail'
        },
        status: 500
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(errorResponse.error, { status: 500, statusText: 'Server Error' });

      try {
        await promise;
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(snackBar.open).toHaveBeenCalledWith(
          'API error detail',
          'Close',
          jasmine.objectContaining({
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black']
          })
        );
      }
    });

    it('should handle HTTP error and show snackbar with message property', async () => {
      const errorResponse = {
        error: {
          message: 'API error message'
        },
        status: 400
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(errorResponse.error, { status: 400, statusText: 'Bad Request' });

      try {
        await promise;
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(snackBar.open).toHaveBeenCalledWith(
          'API error message',
          'Close',
          jasmine.objectContaining({
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black']
          })
        );
      }
    });

    it('should handle HTTP error and show default message when no detail or message', async () => {
      const errorResponse = {
        error: {},
        status: 500
      };

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush({}, { status: 500, statusText: 'Server Error' });

      try {
        await promise;
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(snackBar.open).toHaveBeenCalledWith(
          'The Api has failed',
          'Close',
          jasmine.objectContaining({
            duration: 3000,
            horizontalPosition: 'left',
            panelClass: ['le-u-bg-black']
          })
        );
      }
    });

    it('should log console messages during processing', async () => {
      const mockResponse = {
        RecogList: [
          { isPreDefined: 'No', id: 1, name: 'Custom1' }
        ]
      };

      spyOn(console, 'log');

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);

      await promise;

      expect(console.log).toHaveBeenCalledWith('Noi print');
    });

    it('should log error status and error object on failure', async () => {
      spyOn(console, 'log');

      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush({}, { status: 404, statusText: 'Not Found' });

      try {
        await promise;
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(console.log).toHaveBeenCalledWith(error.status);
        expect(console.log).toHaveBeenCalledWith(error);
      }
    });

    it('should re-throw error after handling', async () => {
      const promise = methodsInstance.getDataSource(mockApi);

      const req = httpMock.expectOne(mockApi);
      req.flush({}, { status: 500, statusText: 'Server Error' });

      await expectAsync(promise).toBeRejected();
    });
  });

  describe('constructor', () => {
    it('should initialize with dependencies', () => {
      expect(methodsInstance).toBeDefined();
      expect((methodsInstance as any).https).toBeDefined();
      expect((methodsInstance as any)._snackBar).toBeDefined();
      expect((methodsInstance as any).recognizerService).toBeDefined();
    });
  });
});
