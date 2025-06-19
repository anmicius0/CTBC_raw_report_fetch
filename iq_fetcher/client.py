from typing import Optional, List, Dict, Any
import requests
from pydantic import BaseModel
from .utils import ErrorHandler, IQServerError, logger


# Simplified models - only what we actually need
class Application(BaseModel):
    id: str
    publicId: str
    name: str

    class Config:
        extra = "allow"


class ReportInfo(BaseModel):
    reportId: Optional[str] = None
    scanId: Optional[str] = None
    reportDataUrl: Optional[str] = None

    class Config:
        extra = "allow"


class IQServerClient:
    """Simple IQ Server API client with error handling built-in."""

    def __init__(self, url: str, user: str, pwd: str) -> None:
        self.base_url = url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (user, pwd)
        self.session.headers.update({"Accept": "application/json"})

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make HTTP requests with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            r = self.session.request(method, url, **kwargs)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            logger.error(f"{method} {endpoint} failed: {e}")
            raise IQServerError(f"{method} {endpoint} failed: {e}")

    @ErrorHandler.handle_api_error
    def get_applications(
        self, org_id: Optional[str] = None
    ) -> Optional[List[Application]]:
        """Fetch all applications and return as validated models."""
        ep = (
            f"/api/v2/applications/organization/{org_id}"
            if org_id
            else "/api/v2/applications"
        )
        response = self._request("GET", ep)
        apps_data = response.json().get("applications", [])
        return [Application(**app) for app in apps_data]

    @ErrorHandler.handle_api_error
    def get_latest_report_info(self, app_id: str) -> Optional[ReportInfo]:
        """Get the latest report info for an application."""
        response = self._request("GET", f"/api/v2/reports/applications/{app_id}")
        reports = response.json()
        return ReportInfo(**reports[0]) if reports else None

    @ErrorHandler.handle_api_error
    def get_policy_violations(
        self, public_id: str, report_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch raw report data."""
        response = self._request(
            "GET",
            f"/api/v2/applications/{public_id}/reports/{report_id}/policy?includeViolationTimes=true",
        )
        return response.json()
