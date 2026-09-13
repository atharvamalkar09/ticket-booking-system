import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VenueSeats } from './venue-seats';

describe('VenueSeats', () => {
  let component: VenueSeats;
  let fixture: ComponentFixture<VenueSeats>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VenueSeats],
    }).compileComponents();

    fixture = TestBed.createComponent(VenueSeats);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
