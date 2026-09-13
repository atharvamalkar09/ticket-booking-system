from fastapi import APIRouter
from app.api.deps import (DBSession,CurrentAdmin)
from app.schemas.adminDashboard import (AdminDashboardResponse)
from app.services.adminDashboardService import (AdminDashboardService)


router = APIRouter(prefix="/admin/dashboard",tags=["Admin Dashboard"])


# ADMIN DASHBOARD
@router.get("",response_model=AdminDashboardResponse)
def get_admin_dashboard(current_admin: CurrentAdmin,db: DBSession):

    dashboard_service = AdminDashboardService(db)
    return dashboard_service.get_dashboard()