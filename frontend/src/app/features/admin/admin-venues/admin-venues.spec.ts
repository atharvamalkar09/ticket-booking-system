import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminVenues } from './admin-venues';

describe('AdminVenues', () => {
  let component: AdminVenues;
  let fixture: ComponentFixture<AdminVenues>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminVenues],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminVenues);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
