/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { TestBed } from '@angular/core/testing';
import { NonceService } from './nonce.service';

describe('NonceService', () => {
  let service: NonceService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NonceService]
    });
    service = TestBed.inject(NonceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('constructor', () => {
    it('should generate nonce on initialization', () => {
      const nonce = service.getNonce();
      expect(nonce).toBeDefined();
      expect(typeof nonce).toBe('string');
    });

    it('should generate non-empty nonce on initialization', () => {
      const nonce = service.getNonce();
      expect(nonce.length).toBeGreaterThan(0);
    });
  });

  describe('generateNonce', () => {
    it('should generate a string nonce', () => {
      service.generateNonce();
      const nonce = service.getNonce();
      expect(typeof nonce).toBe('string');
    });

    it('should generate nonce with expected length', () => {
      service.generateNonce();
      const nonce = service.getNonce();
      // Each byte becomes 2 characters after padding, 10 bytes = 20 characters
      expect(nonce.length).toBe(20);
    });

    it('should generate unique nonces on multiple calls', () => {
      service.generateNonce();
      const nonce1 = service.getNonce();
      
      service.generateNonce();
      const nonce2 = service.getNonce();
      
      service.generateNonce();
      const nonce3 = service.getNonce();

      expect(nonce1).not.toBe(nonce2);
      expect(nonce2).not.toBe(nonce3);
      expect(nonce1).not.toBe(nonce3);
    });

    it('should generate nonce using base36 characters', () => {
      service.generateNonce();
      const nonce = service.getNonce();
      // Base36 uses 0-9 and a-z
      const base36Pattern = /^[0-9a-z]+$/;
      expect(base36Pattern.test(nonce)).toBe(true);
    });

    it('should update the existing nonce when called', () => {
      const firstNonce = service.getNonce();
      service.generateNonce();
      const secondNonce = service.getNonce();
      
      expect(firstNonce).not.toBe(secondNonce);
    });

    it('should use crypto.getRandomValues', () => {
      spyOn(crypto, 'getRandomValues').and.callThrough();
      
      service.generateNonce();
      
      expect(crypto.getRandomValues).toHaveBeenCalled();
      expect(crypto.getRandomValues).toHaveBeenCalledWith(jasmine.any(Uint8Array));
    });

    it('should generate nonce from 10 random bytes', () => {
      spyOn(crypto, 'getRandomValues').and.callThrough();
      
      service.generateNonce();
      
      const callArgs = (crypto.getRandomValues as jasmine.Spy).calls.mostRecent().args[0];
      expect(callArgs.length).toBe(10);
    });

    it('should handle all possible byte values in base36 conversion', () => {
      // Mock crypto.getRandomValues to return specific values
      const mockBytes = new Uint8Array([0, 35, 100, 150, 200, 255, 128, 64, 32, 16]);
      spyOn(crypto, 'getRandomValues').and.returnValue(mockBytes);
      
      service.generateNonce();
      const nonce = service.getNonce();
      
      expect(nonce).toBeDefined();
      expect(nonce.length).toBe(20);
    });

    it('should pad each byte to 2 characters', () => {
      // Mock with small values that would need padding
      const mockBytes = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
      spyOn(crypto, 'getRandomValues').and.returnValue(mockBytes);
      
      service.generateNonce();
      const nonce = service.getNonce();
      
      // Each byte padded to 2 chars, 10 bytes = 20 chars
      expect(nonce.length).toBe(20);
    });

    it('should generate different nonces even with sequential calls', () => {
      const nonces = new Set<string>();
      
      for (let i = 0; i < 100; i++) {
        service.generateNonce();
        nonces.add(service.getNonce());
      }
      
      // All 100 nonces should be unique
      expect(nonces.size).toBe(100);
    });
  });

  describe('getNonce', () => {
    it('should return the current nonce value', () => {
      const nonce = service.getNonce();
      expect(nonce).toBeDefined();
    });

    it('should return the same nonce when called multiple times without regeneration', () => {
      const nonce1 = service.getNonce();
      const nonce2 = service.getNonce();
      const nonce3 = service.getNonce();
      
      expect(nonce1).toBe(nonce2);
      expect(nonce2).toBe(nonce3);
    });

    it('should return a string', () => {
      const nonce = service.getNonce();
      expect(typeof nonce).toBe('string');
    });

    it('should return the updated nonce after regeneration', () => {
      const originalNonce = service.getNonce();
      service.generateNonce();
      const newNonce = service.getNonce();
      
      expect(newNonce).not.toBe(originalNonce);
    });

    it('should not modify the nonce value when called', () => {
      const nonce1 = service.getNonce();
      const nonce2 = service.getNonce();
      const nonce3 = service.getNonce();
      
      expect(nonce1).toBe(nonce2);
      expect(nonce1).toBe(nonce3);
    });
  });

  describe('nonce properties', () => {
    it('should generate cryptographically secure random nonces', () => {
      // Generate multiple nonces and check they don't follow a pattern
      const nonces: string[] = [];
      for (let i = 0; i < 10; i++) {
        service.generateNonce();
        nonces.push(service.getNonce());
      }
      
      // Check all are different
      const uniqueNonces = new Set(nonces);
      expect(uniqueNonces.size).toBe(10);
    });

    it('should maintain nonce value across multiple getNonce calls', () => {
      service.generateNonce();
      const nonce = service.getNonce();
      
      // Call getNonce multiple times
      for (let i = 0; i < 10; i++) {
        expect(service.getNonce()).toBe(nonce);
      }
    });

    it('should generate nonce suitable for security purposes', () => {
      service.generateNonce();
      const nonce = service.getNonce();
      
      // Check it's not empty
      expect(nonce.length).toBeGreaterThan(0);
      // Check it contains alphanumeric characters
      expect(/^[0-9a-z]+$/.test(nonce)).toBe(true);
      // Check it has sufficient length for security
      expect(nonce.length).toBeGreaterThanOrEqual(20);
    });
  });

  describe('integration tests', () => {
    it('should work correctly when creating multiple service instances', () => {
      const service1 = new NonceService();
      const service2 = new NonceService();
      
      const nonce1 = service1.getNonce();
      const nonce2 = service2.getNonce();
      
      // Different instances should have different nonces
      expect(nonce1).not.toBe(nonce2);
    });

    it('should handle rapid successive nonce generations', () => {
      const nonces: string[] = [];
      
      for (let i = 0; i < 50; i++) {
        service.generateNonce();
        nonces.push(service.getNonce());
      }
      
      // All nonces should be unique
      const uniqueNonces = new Set(nonces);
      expect(uniqueNonces.size).toBe(50);
    });

    it('should maintain state between generate and get operations', () => {
      service.generateNonce();
      const nonce1 = service.getNonce();
      const nonce2 = service.getNonce();
      
      expect(nonce1).toBe(nonce2);
      
      service.generateNonce();
      const nonce3 = service.getNonce();
      const nonce4 = service.getNonce();
      
      expect(nonce3).toBe(nonce4);
      expect(nonce1).not.toBe(nonce3);
    });
  });

  describe('edge cases', () => {
    it('should handle crypto.getRandomValues returning zeros', () => {
      const mockBytes = new Uint8Array(10).fill(0);
      spyOn(crypto, 'getRandomValues').and.returnValue(mockBytes);
      
      service.generateNonce();
      const nonce = service.getNonce();
      
      expect(nonce).toBeDefined();
      expect(nonce.length).toBe(20);
      expect(nonce).toBe('00000000000000000000');
    });

    it('should handle crypto.getRandomValues returning max values', () => {
      const mockBytes = new Uint8Array(10).fill(255);
      spyOn(crypto, 'getRandomValues').and.returnValue(mockBytes);
      
      service.generateNonce();
      const nonce = service.getNonce();
      
      expect(nonce).toBeDefined();
      expect(nonce.length).toBe(20);
    });

    it('should handle mixed byte values correctly', () => {
      const mockBytes = new Uint8Array([0, 1, 10, 35, 36, 100, 127, 200, 254, 255]);
      spyOn(crypto, 'getRandomValues').and.returnValue(mockBytes);
      
      service.generateNonce();
      const nonce = service.getNonce();
      
      expect(nonce).toBeDefined();
      expect(nonce.length).toBe(20);
      expect(/^[0-9a-z]+$/.test(nonce)).toBe(true);
    });
  });
});
