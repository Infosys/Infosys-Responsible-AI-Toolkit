import { TestBed } from '@angular/core/testing';
import { BaseHrefService } from './base-href.service';

describe('BaseHrefService', () => {
    let service: BaseHrefService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(BaseHrefService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('setBaseHref', () => {
        it('should set baseHref to "/shell/" when condition is true', () => {
            service.setBaseHref(true);
            expect(service.getBaseHref()).toBe('/shell/');
        });

        it('should set baseHref to "/shell/" when condition is false', () => {
            service.setBaseHref(false);
            expect(service.getBaseHref()).toBe('/shell/');
        });

        it('should override previous baseHref value', () => {
            service.setBaseHref(true);
            expect(service.getBaseHref()).toBe('/shell/');
            
            service.setBaseHref(false);
            expect(service.getBaseHref()).toBe('/shell/');
        });
    });

    describe('getBaseHref', () => {
        it('should return default baseHref "/" when not set', () => {
            expect(service.getBaseHref()).toBe('/');
        });
    });
});
