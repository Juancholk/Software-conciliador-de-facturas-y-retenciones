import { TestBed } from '@angular/core/testing';
import { Conciliacion } from './conciliacion';

describe('Conciliacion', () => {
  let service: Conciliacion;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Conciliacion);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
