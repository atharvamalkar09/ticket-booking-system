import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminVenueDetails } from './admin-venue-details';

describe('AdminVenueDetails', () => {
  let component: AdminVenueDetails;
  let fixture: ComponentFixture<AdminVenueDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminVenueDetails],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminVenueDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
