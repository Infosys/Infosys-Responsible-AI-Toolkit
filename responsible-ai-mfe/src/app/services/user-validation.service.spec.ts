/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/ 
import { TestBed } from '@angular/core/testing';
import { UserValidationService } from './user-validation.service';

describe('UserValidationService', () => {
  let service: UserValidationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserValidationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('isValidEmail', () => {
    it('should return true for valid email addresses', () => {
      expect(service.isValidEmail('test@example.com')).toBe(true);
      expect(service.isValidEmail('user.name@domain.com')).toBe(true);
      expect(service.isValidEmail('user+tag@example.co.uk')).toBe(true);
      expect(service.isValidEmail('test123@test-domain.com')).toBe(true);
    });

    it('should return false for email without @', () => {
      expect(service.isValidEmail('testexample.com')).toBe(false);
    });

    it('should return false for email without domain', () => {
      expect(service.isValidEmail('test@')).toBe(false);
    });

    it('should return false for email without local part', () => {
      expect(service.isValidEmail('@example.com')).toBe(false);
    });

    it('should return false for email without dot in domain', () => {
      expect(service.isValidEmail('test@examplecom')).toBe(false);
    });

    it('should return false for email with spaces', () => {
      expect(service.isValidEmail('test @example.com')).toBe(false);
      expect(service.isValidEmail('test@ example.com')).toBe(false);
    });

    it('should return false for empty string', () => {
      expect(service.isValidEmail('')).toBe(false);
    });

    it('should return false for multiple @ symbols', () => {
      expect(service.isValidEmail('test@@example.com')).toBe(false);
    });

    it('should return true for email ending with dot (allowed by regex)', () => {
      expect(service.isValidEmail('test@example.com.')).toBe(true);
    });

    it('should return true for email starting with dot (allowed by regex)', () => {
      expect(service.isValidEmail('.test@example.com')).toBe(true);
    });

    it('should handle null or undefined', () => {
      expect(service.isValidEmail(null)).toBe(false);
      expect(service.isValidEmail(undefined)).toBe(false);
    });
  });

  describe('isValidName', () => {
    it('should return true for valid names with only letters', () => {
      expect(service.isValidName('John')).toBe(true);
      expect(service.isValidName('Mary')).toBe(true);
    });

    it('should return true for names with spaces', () => {
      expect(service.isValidName('John Doe')).toBe(true);
      expect(service.isValidName('Mary Jane Smith')).toBe(true);
    });

    it('should return true for names with mixed case', () => {
      expect(service.isValidName('JoHn DoE')).toBe(true);
    });

    it('should return false for names with numbers', () => {
      expect(service.isValidName('John123')).toBe(false);
      expect(service.isValidName('123John')).toBe(false);
    });

    it('should return false for names with special characters', () => {
      expect(service.isValidName('John@Doe')).toBe(false);
      expect(service.isValidName('John-Doe')).toBe(false);
      expect(service.isValidName('John_Doe')).toBe(false);
      expect(service.isValidName('John.Doe')).toBe(false);
    });

    it('should return false for empty string', () => {
      expect(service.isValidName('')).toBe(false);
    });

    it('should return true for single letter', () => {
      expect(service.isValidName('A')).toBe(true);
    });

    it('should return true for name with multiple spaces', () => {
      expect(service.isValidName('John  Doe')).toBe(true);
    });

    it('should return true for name starting with space (allowed by regex)', () => {
      expect(service.isValidName(' John')).toBe(true);
    });

    it('should return true for null or undefined (regex behavior)', () => {
      // The regex.test() converts null/undefined to string, which may pass the pattern
      expect(service.isValidName(null)).toBe(true);
      expect(service.isValidName(undefined)).toBe(true);
    });
  });

  describe('validateTextDesc', () => {
    it('should return true for alphanumeric text', () => {
      expect(service.validateTextDesc('Hello World')).toBe(true);
      expect(service.validateTextDesc('Test123')).toBe(true);
    });

    it('should return true for text with allowed special characters', () => {
      expect(service.validateTextDesc('Hello! How are you?')).toBe(true);
      expect(service.validateTextDesc('Test@#$%')).toBe(true);
      expect(service.validateTextDesc('Price: $100')).toBe(true);
    });

    it('should return true for text with parentheses', () => {
      expect(service.validateTextDesc('Test (with parentheses)')).toBe(true);
    });

    it('should return true for text with brackets', () => {
      expect(service.validateTextDesc('Array[0]')).toBe(true);
      expect(service.validateTextDesc('Object{key}')).toBe(true);
    });

    it('should return true for text with semicolon and colon', () => {
      expect(service.validateTextDesc('Key: Value; Another: Value')).toBe(true);
    });

    it('should return true for text with quotes', () => {
      expect(service.validateTextDesc('He said "Hello"')).toBe(true);
      expect(service.validateTextDesc("It's working")).toBe(true);
    });

    it('should return true for text with backslash', () => {
      expect(service.validateTextDesc('Path\\to\\file')).toBe(true);
    });

    it('should return true for text with pipe', () => {
      expect(service.validateTextDesc('Option1 | Option2')).toBe(true);
    });

    it('should return true for text with comparison operators', () => {
      expect(service.validateTextDesc('Value < 10 or > 20')).toBe(true);
    });

    it('should return true for text with forward slash', () => {
      expect(service.validateTextDesc('Path/to/file')).toBe(true);
    });

    it('should return true for empty string', () => {
      expect(service.validateTextDesc('')).toBe(true);
    });

    it('should return true for text with all allowed special characters', () => {
      const allSpecialChars = '!@#$%^&*()_+-=[]{};\'":\\|,.<>/?';
      expect(service.validateTextDesc(allSpecialChars)).toBe(true);
    });

    it('should return true for text with numbers and letters', () => {
      expect(service.validateTextDesc('abc123XYZ')).toBe(true);
    });

    it('should return true for text with spaces', () => {
      expect(service.validateTextDesc('Multiple   spaces   between')).toBe(true);
    });

    it('should return true for text with escaped newline characters (treated as literal characters)', () => {
      // The string 'Line1\\nLine2' contains literal backslash-n, not actual newline
      expect(service.validateTextDesc('Line1\\nLine2')).toBe(true);
    });

    it('should return true for text with escaped tab characters (treated as literal characters)', () => {
      // The string 'Column1\\tColumn2' contains literal backslash-t, not actual tab
      expect(service.validateTextDesc('Column1\\tColumn2')).toBe(true);
    });

    it('should return true for complex mixed content', () => {
      const complexText = 'User: John Doe (ID: 123), Email: john@example.com, Status: Active!';
      expect(service.validateTextDesc(complexText)).toBe(true);
    });

    it('should return true for mathematical expressions', () => {
      expect(service.validateTextDesc('(x + y) * 2 = z')).toBe(true);
    });

    it('should return true for code-like syntax', () => {
      expect(service.validateTextDesc('function() { return true; }')).toBe(true);
    });

    it('should return true for single character', () => {
      expect(service.validateTextDesc('a')).toBe(true);
    });

    it('should return true for only special characters', () => {
      expect(service.validateTextDesc('!@#$%')).toBe(true);
    });

    it('should return true for only numbers', () => {
      expect(service.validateTextDesc('1234567890')).toBe(true);
    });
  });
});
