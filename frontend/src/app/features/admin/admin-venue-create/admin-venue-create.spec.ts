import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminVenueCreate } from './admin-venue-create';

describe('AdminVenueCreate', () => {
  let component: AdminVenueCreate;
  let fixture: ComponentFixture<AdminVenueCreate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminVenueCreate],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminVenueCreate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
