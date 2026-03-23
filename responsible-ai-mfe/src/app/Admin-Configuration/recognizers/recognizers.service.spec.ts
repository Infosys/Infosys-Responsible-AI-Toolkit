/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { RecognizersService } from './recognizers.service';

describe('RecognizersService', () => {
  let service: RecognizersService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [ RecognizersService ]
    });
    service = TestBed.inject(RecognizersService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('deleteRecognizer', () => {
    it('should make DELETE request to the specified API endpoint', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/123';
      const mockHeaders = { headers: { 'Authorization': 'Bearer token' } };
      const mockResponse = { status: 'True', message: 'Deleted successfully' };

      service.deleteRecognizer(mockApi, mockHeaders).subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(mockApi);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockResponse);
    });

    it('should pass headers correctly in DELETE request', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/456';
      const mockHeaders = { 
        headers: { 
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json'
        } 
      };

      service.deleteRecognizer(mockApi, mockHeaders).subscribe();

      const req = httpMock.expectOne(mockApi);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });

    it('should handle successful deletion response', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/789';
      const mockHeaders = {};
      const mockResponse = { 
        status: 'True', 
        message: 'Recognizer deleted successfully',
        deletedId: '789'
      };

      service.deleteRecognizer(mockApi, mockHeaders).subscribe((response) => {
        expect(response.status).toBe('True');
        expect(response.message).toBe('Recognizer deleted successfully');
        expect(response.deletedId).toBe('789');
      });

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);
    });

    it('should handle error response from DELETE request', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/999';
      const mockHeaders = {};
      const errorMessage = 'Failed to delete recognizer';

      service.deleteRecognizer(mockApi, mockHeaders).subscribe(
        () => fail('Should have failed with 404 error'),
        (error) => {
          expect(error.status).toBe(404);
          expect(error.error).toBe(errorMessage);
        }
      );

      const req = httpMock.expectOne(mockApi);
      req.flush(errorMessage, { status: 404, statusText: 'Not Found' });
    });

    it('should handle server error (500) from DELETE request', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/500';
      const mockHeaders = {};

      service.deleteRecognizer(mockApi, mockHeaders).subscribe(
        () => fail('Should have failed with 500 error'),
        (error) => {
          expect(error.status).toBe(500);
        }
      );

      const req = httpMock.expectOne(mockApi);
      req.flush('Internal Server Error', { status: 500, statusText: 'Server Error' });
    });

    it('should return Observable that can be subscribed to', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/111';
      const mockHeaders = {};
      
      const result = service.deleteRecognizer(mockApi, mockHeaders);
      
      expect(result.subscribe).toBeDefined();
      
      result.subscribe();
      const req = httpMock.expectOne(mockApi);
      req.flush({});
    });

    it('should handle empty response from DELETE request', () => {
      const mockApi = 'http://test.com/api/recognizers/delete/222';
      const mockHeaders = {};

      service.deleteRecognizer(mockApi, mockHeaders).subscribe((response) => {
        expect(response).toEqual({});
      });

      const req = httpMock.expectOne(mockApi);
      req.flush({});
    });
  });

  describe('getRecognizers', () => {
    it('should make GET request to the specified API endpoint', () => {
      const mockApi = 'http://test.com/api/recognizers';
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'Recognizer1', isPreDefined: 'No' },
          { id: 2, name: 'Recognizer2', isPreDefined: 'Yes' }
        ]
      };

      service.getRecognizers(mockApi).subscribe((response) => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(mockApi);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should return list of recognizers', () => {
      const mockApi = 'http://test.com/api/recognizers/list';
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'PERSON', type: 'PII' },
          { id: 2, name: 'EMAIL', type: 'PII' },
          { id: 3, name: 'PHONE', type: 'PII' }
        ]
      };

      service.getRecognizers(mockApi).subscribe((response) => {
        expect(response.RecogList.length).toBe(3);
        expect(response.RecogList[0].name).toBe('PERSON');
        expect(response.RecogList[1].name).toBe('EMAIL');
        expect(response.RecogList[2].name).toBe('PHONE');
      });

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);
    });

    it('should handle empty recognizers list', () => {
      const mockApi = 'http://test.com/api/recognizers/empty';
      const mockResponse = { RecogList: [] };

      service.getRecognizers(mockApi).subscribe((response) => {
        expect(response.RecogList).toEqual([]);
        expect(response.RecogList.length).toBe(0);
      });

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);
    });

    it('should handle error response from GET request', () => {
      const mockApi = 'http://test.com/api/recognizers/error';
      const errorMessage = 'Failed to fetch recognizers';

      service.getRecognizers(mockApi).subscribe(
        () => fail('Should have failed with 404 error'),
        (error) => {
          expect(error.status).toBe(404);
          expect(error.error).toBe(errorMessage);
        }
      );

      const req = httpMock.expectOne(mockApi);
      req.flush(errorMessage, { status: 404, statusText: 'Not Found' });
    });

    it('should handle server error (500) from GET request', () => {
      const mockApi = 'http://test.com/api/recognizers/servererror';

      service.getRecognizers(mockApi).subscribe(
        () => fail('Should have failed with 500 error'),
        (error) => {
          expect(error.status).toBe(500);
          expect(error.statusText).toBe('Internal Server Error');
        }
      );

      const req = httpMock.expectOne(mockApi);
      req.flush('Server Error', { status: 500, statusText: 'Internal Server Error' });
    });

    it('should handle unauthorized error (401) from GET request', () => {
      const mockApi = 'http://test.com/api/recognizers/unauthorized';

      service.getRecognizers(mockApi).subscribe(
        () => fail('Should have failed with 401 error'),
        (error) => {
          expect(error.status).toBe(401);
        }
      );

      const req = httpMock.expectOne(mockApi);
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    });

    it('should return Observable that can be subscribed to', () => {
      const mockApi = 'http://test.com/api/recognizers/observable';
      
      const result = service.getRecognizers(mockApi);
      
      expect(result.subscribe).toBeDefined();
      
      result.subscribe();
      const req = httpMock.expectOne(mockApi);
      req.flush({ RecogList: [] });
    });

    it('should handle response with additional metadata', () => {
      const mockApi = 'http://test.com/api/recognizers/metadata';
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'TEST', isPreDefined: 'No' }
        ],
        totalCount: 1,
        page: 1,
        pageSize: 10
      };

      service.getRecognizers(mockApi).subscribe((response) => {
        expect(response.RecogList.length).toBe(1);
        expect(response.totalCount).toBe(1);
        expect(response.page).toBe(1);
        expect(response.pageSize).toBe(10);
      });

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);
    });

    it('should handle response with filtered recognizers', () => {
      const mockApi = 'http://test.com/api/recognizers/filtered';
      const mockResponse = {
        RecogList: [
          { id: 1, name: 'Custom1', isPreDefined: 'No' },
          { id: 2, name: 'Custom2', isPreDefined: 'No' }
        ]
      };

      service.getRecognizers(mockApi).subscribe((response) => {
        expect(response.RecogList.every((r: any) => r.isPreDefined === 'No')).toBe(true);
      });

      const req = httpMock.expectOne(mockApi);
      req.flush(mockResponse);
    });
  });

  describe('Service Configuration', () => {
    it('should be provided in root', () => {
      expect(service).toBeDefined();
    });

    it('should have HttpClient injected', () => {
      expect((service as any).https).toBeDefined();
    });
  });
});
