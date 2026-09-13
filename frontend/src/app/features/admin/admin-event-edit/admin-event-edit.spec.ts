import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminEventEdit } from './admin-event-edit';

describe('AdminEventEdit', () => {
  let component: AdminEventEdit;
  let fixture: ComponentFixture<AdminEventEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminEventEdit],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminEventEdit);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
