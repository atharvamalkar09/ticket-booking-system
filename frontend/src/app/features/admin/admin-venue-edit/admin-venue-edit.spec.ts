import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminVenueEdit } from './admin-venue-edit';

describe('AdminVenueEdit', () => {
  let component: AdminVenueEdit;
  let fixture: ComponentFixture<AdminVenueEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminVenueEdit],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminVenueEdit);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
