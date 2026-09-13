import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminCreateEvent } from './admin-create-event';

describe('AdminCreateEvent', () => {
  let component: AdminCreateEvent;
  let fixture: ComponentFixture<AdminCreateEvent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminCreateEvent],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminCreateEvent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
