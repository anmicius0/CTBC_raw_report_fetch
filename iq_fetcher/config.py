import os
from typing import Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, HttpUrl, ValidationInfo
from .utils import resolve_path

# Load .env at the module level
load_dotenv(dotenv_path=resolve_path("config/.env"))


class Config(BaseModel):
    """
    Configuration for connecting to the IQ Server and output settings.
    """

    iq_server_url: HttpUrl
    iq_username: str
    iq_password: str
    organization_id: Optional[str] = None
    output_dir: str = "raw_reports"

    @field_validator("iq_username", "iq_password")
    @classmethod
    def not_empty(cls, v: Any, info: ValidationInfo) -> str:
        if not v or not str(v).strip():
            raise ValueError(f"{info.field_name} must not be empty")
        return str(v)

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables with Pydantic validation.
        """
        url = os.getenv("IQ_SERVER_URL", "").rstrip("/")
        user = os.getenv("IQ_USERNAME", "")
        pwd = os.getenv("IQ_PASSWORD", "")
        org = os.getenv("ORGANIZATION_ID")
        out = os.getenv("OUTPUT_DIR", "raw_reports")

        # Let Pydantic handle all validation
        return cls(
            iq_server_url=url,  # type: ignore[arg-type]
            iq_username=user,
            iq_password=pwd,
            organization_id=org,
            output_dir=out,
        )
