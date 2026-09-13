# app/scripts/create_admin.py
from datetime import datetime, timezone
import os
import sys
import getpass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from app.models.user import User, UserRole
from app.models.event import Event     
from app.models.booking import Booking  
from app.models.venue import Venue
from app.models.seat import Seat

from app.db.database import Sessionlocal
from app.repositories.userRepo import UserRepository
from app.core import security


def main():
    db = Sessionlocal()
    user_repo = UserRepository(db)
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL") or input("Enter Admin Email: ").strip()
    username = os.getenv("BOOTSTRAP_ADMIN_USERNAME") or input("Enter Admin Username: ").strip()
    phone_no = os.getenv("BOOTSTRAP_ADMIN_PHONE") or input("Enter Admin Phone No: ").strip()
    city = os.getenv("BOOTSTRAP_ADMIN_CITY") or input("Enter Admin City: ").strip()
    address = os.getenv("BOOTSTRAP_ADMIN_ADDRESS") or input("Enter Admin Address (Optional): ").strip() or None

    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if not password:
        password = getpass.getpass("Enter Admin Password: ").strip()
        confirm_password = getpass.getpass("Confirm Admin Password: ").strip()
        if password != confirm_password:
            print("\n[Error] Passwords do not match. Aborting.")
            sys.exit(1)
    existing_user = user_repo.get_by_email_or_username(email, username)
    if existing_user:
        print(f"\n[Warning] A user with email '{email}' or username '{username}' already exists.")
        print("Skipping admin account creation.")
        sys.exit(0)
    hashed_pwd = security.hash_password(password)

    admin_user = User(
        username=username,
        email=email,
        phone_no=phone_no,
        city=city,
        address=address,
        hashed_password=hashed_pwd,
        role=UserRole.ADMIN,
        created_at=datetime.now(timezone.utc),
    )
    try:
        db.add(admin_user)
        db.commit()
        print(f"\n[Success] Created admin user '{username}' ({email}) with role ADMIN.")
    except Exception as e:
        db.rollback()
        print(f"\n[Error] Failed to create admin user: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()