/** SPDX-License-Identifier: MIT
Copyright 2024 - 2025 Infosys Ltd.
"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
*/
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NgxPaginationModule } from 'ngx-pagination';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { ProfanityResultComponent } from './profanity-result.component';

describe('ProfanityResultComponent', () => {
  let component: ProfanityResultComponent;
  let fixture: ComponentFixture<ProfanityResultComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProfanityResultComponent ],
      imports: [ NgxPaginationModule ],
      schemas: [ NO_ERRORS_SCHEMA ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfanityResultComponent);
    component = fixture.componentInstance;
    
    // Setup mock profanityRes input
    component.profanityRes = {
      AnazRes: {
        profanityScoreList: [
          { word: 'test1', score: 0.8 },
          { word: 'test2', score: 0.9 },
          { word: 'test3', score: 0.7 },
          { word: 'test4', score: 0.6 },
          { word: 'test5', score: 0.5 }
        ],
        profanity: [
          { text: 'profanity1', category: 'mild' },
          { text: 'profanity2', category: 'moderate' },
          { text: 'profanity3', category: 'severe' },
          { text: 'profanity4', category: 'mild' },
          { text: 'profanity5', category: 'moderate' }
        ]
      }
    };
    
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Constructor and Initialization', () => {
    it('should initialize with default pagination values', () => {
      expect(component.currentPage).toBe(1);
      expect(component.itemsPerPage).toBe(4);
      expect(component.totalItems).toBe(0);
    });

    it('should initialize with default pagination2 values', () => {
      expect(component.currentPage2).toBe(1);
      expect(component.itemsPerPage2).toBe(4);
      expect(component.totalItems2).toBe(0);
    });

    it('should initialize pagingConfig object with correct properties', () => {
      expect(component.pagingConfig).toBeDefined();
      expect(component.pagingConfig.itemsPerPage).toBe(4);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBe(0);
    });

    it('should initialize pagingConfig2 object with correct properties', () => {
      expect(component.pagingConfig2).toBeDefined();
      expect(component.pagingConfig2.itemsPerPage).toBe(4);
      expect(component.pagingConfig2.currentPage).toBe(1);
      expect(component.pagingConfig2.totalItems).toBe(0);
    });

    it('should accept profanityRes as input', () => {
      expect(component.profanityRes).toBeDefined();
      expect(component.profanityRes.AnazRes).toBeDefined();
    });
  });

  describe('onTableDataChange - Table 1 Pagination', () => {
    it('should update currentPage when page changes', () => {
      const newPage = 2;
      component.onTableDataChange(newPage);
      
      expect(component.currentPage).toBe(newPage);
    });

    it('should update pagingConfig.currentPage when page changes', () => {
      const newPage = 3;
      component.onTableDataChange(newPage);
      
      expect(component.pagingConfig.currentPage).toBe(newPage);
    });

    it('should update pagingConfig.totalItems based on profanityScoreList length', () => {
      component.onTableDataChange(1);
      
      expect(component.pagingConfig.totalItems).toBe(5);
      expect(component.pagingConfig.totalItems).toBe(component.profanityRes.AnazRes.profanityScoreList.length);
    });

    it('should handle page change to first page', () => {
      component.currentPage = 3;
      component.onTableDataChange(1);
      
      expect(component.currentPage).toBe(1);
      expect(component.pagingConfig.currentPage).toBe(1);
    });

    it('should handle page change with empty profanityScoreList', () => {
      component.profanityRes.AnazRes.profanityScoreList = [];
      component.onTableDataChange(1);
      
      expect(component.pagingConfig.totalItems).toBe(0);
    });

    it('should update all pagination properties in one call', () => {
      const testPage = 2;
      component.onTableDataChange(testPage);
      
      expect(component.currentPage).toBe(testPage);
      expect(component.pagingConfig.currentPage).toBe(testPage);
      expect(component.pagingConfig.totalItems).toBe(component.profanityRes.AnazRes.profanityScoreList.length);
    });
  });

  describe('onTableDataChange2 - Table 2 Pagination', () => {
    it('should update currentPage2 when page changes', () => {
      const newPage = 2;
      component.onTableDataChange2(newPage);
      
      expect(component.currentPage2).toBe(newPage);
    });

    it('should update pagingConfig2.currentPage when page changes', () => {
      const newPage = 3;
      component.onTableDataChange2(newPage);
      
      expect(component.pagingConfig2.currentPage).toBe(newPage);
    });

    it('should update pagingConfig2.totalItems based on profanity array length', () => {
      component.onTableDataChange2(1);
      
      expect(component.pagingConfig2.totalItems).toBe(5);
      expect(component.pagingConfig2.totalItems).toBe(component.profanityRes.AnazRes.profanity.length);
    });

    it('should handle page change to first page', () => {
      component.currentPage2 = 3;
      component.onTableDataChange2(1);
      
      expect(component.currentPage2).toBe(1);
      expect(component.pagingConfig2.currentPage).toBe(1);
    });

    it('should handle page change with empty profanity array', () => {
      component.profanityRes.AnazRes.profanity = [];
      component.onTableDataChange2(1);
      
      expect(component.pagingConfig2.totalItems).toBe(0);
    });

    it('should update all pagination2 properties in one call', () => {
      const testPage = 2;
      component.onTableDataChange2(testPage);
      
      expect(component.currentPage2).toBe(testPage);
      expect(component.pagingConfig2.currentPage).toBe(testPage);
      expect(component.pagingConfig2.totalItems).toBe(component.profanityRes.AnazRes.profanity.length);
    });
  });

  describe('Pagination Independence', () => {
    it('should not affect table 2 pagination when table 1 changes', () => {
      const initialPage2 = component.currentPage2;
      const initialTotalItems2 = component.pagingConfig2.totalItems;
      
      component.onTableDataChange(2);
      
      expect(component.currentPage2).toBe(initialPage2);
      expect(component.pagingConfig2.currentPage).toBe(initialPage2);
    });

    it('should not affect table 1 pagination when table 2 changes', () => {
      const initialPage1 = component.currentPage;
      
      component.onTableDataChange2(2);
      
      expect(component.currentPage).toBe(initialPage1);
      expect(component.pagingConfig.currentPage).toBe(initialPage1);
    });

    it('should handle both tables changing pages independently', () => {
      component.onTableDataChange(2);
      component.onTableDataChange2(3);
      
      expect(component.currentPage).toBe(2);
      expect(component.currentPage2).toBe(3);
      expect(component.pagingConfig.currentPage).toBe(2);
      expect(component.pagingConfig2.currentPage).toBe(3);
    });
  });

  describe('Edge Cases', () => {
    it('should handle numeric event values', () => {
      component.onTableDataChange(5);
      expect(component.currentPage).toBe(5);
      
      component.onTableDataChange2(7);
      expect(component.currentPage2).toBe(7);
    });

    it('should handle string event values converted to numbers', () => {
      component.onTableDataChange('2' as any);
      expect(component.currentPage).toBe('2' as any);
      
      component.onTableDataChange2('3' as any);
      expect(component.currentPage2).toBe('3' as any);
    });

    it('should maintain pagination config structure after multiple updates', () => {
      component.onTableDataChange(2);
      component.onTableDataChange(3);
      component.onTableDataChange(1);
      
      expect(component.pagingConfig).toBeDefined();
      expect(component.pagingConfig.itemsPerPage).toBe(4);
      expect(component.pagingConfig.currentPage).toBe(1);
      expect(component.pagingConfig.totalItems).toBeDefined();
    });

    it('should handle large profanityScoreList arrays', () => {
      const largeArray = Array(100).fill(null).map((_, i) => ({ word: `test${i}`, score: 0.5 }));
      component.profanityRes.AnazRes.profanityScoreList = largeArray;
      
      component.onTableDataChange(1);
      
      expect(component.pagingConfig.totalItems).toBe(100);
    });

    it('should handle large profanity arrays', () => {
      const largeArray = Array(150).fill(null).map((_, i) => ({ text: `profanity${i}`, category: 'mild' }));
      component.profanityRes.AnazRes.profanity = largeArray;
      
      component.onTableDataChange2(1);
      
      expect(component.pagingConfig2.totalItems).toBe(150);
    });
  });

  describe('Integration Tests', () => {
    it('should properly initialize and handle sequential pagination updates', () => {
      // Initial state
      expect(component.currentPage).toBe(1);
      expect(component.currentPage2).toBe(1);
      
      // Update table 1
      component.onTableDataChange(2);
      expect(component.currentPage).toBe(2);
      expect(component.pagingConfig.totalItems).toBe(5);
      
      // Update table 2
      component.onTableDataChange2(3);
      expect(component.currentPage2).toBe(3);
      expect(component.pagingConfig2.totalItems).toBe(5);
      
      // Verify independence
      expect(component.currentPage).toBe(2);
      expect(component.currentPage2).toBe(3);
    });

    it('should handle profanityRes structure with nested AnazRes properly', () => {
      expect(component.profanityRes.AnazRes).toBeDefined();
      expect(component.profanityRes.AnazRes.profanityScoreList).toBeDefined();
      expect(component.profanityRes.AnazRes.profanity).toBeDefined();
      
      component.onTableDataChange(1);
      component.onTableDataChange2(1);
      
      expect(component.pagingConfig.totalItems).toBeGreaterThan(0);
      expect(component.pagingConfig2.totalItems).toBeGreaterThan(0);
    });
  });
});
