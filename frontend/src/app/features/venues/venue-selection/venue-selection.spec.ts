import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VenueSelection } from './venue-selection';

describe('VenueSelection', () => {
  let component: VenueSelection;
  let fixture: ComponentFixture<VenueSelection>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VenueSelection],
    }).compileComponents();

    fixture = TestBed.createComponent(VenueSelection);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
