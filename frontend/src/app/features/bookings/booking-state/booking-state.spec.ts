import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BookingState } from './booking-state';

describe('BookingState', () => {
  let component: BookingState;
  let fixture: ComponentFixture<BookingState>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BookingState],
    }).compileComponents();

    fixture = TestBed.createComponent(BookingState);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
