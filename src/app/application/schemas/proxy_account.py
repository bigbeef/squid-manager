from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


USERNAME_PATTERN = r"^[A-Za-z0-9._-]{1,128}$"


class ProxyAccountCreate(BaseModel):
    username: str = Field(pattern=USERNAME_PATTERN)
    password: str = Field(min_length=1, max_length=512)
    enabled: bool = True
    expires_at: datetime | None = None

    @field_validator("username")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return value.strip()


class ProxyAccountUpdate(BaseModel):
    username: str = Field(pattern=USERNAME_PATTERN)
    password: str = Field(min_length=1, max_length=512)
    enabled: bool = True
    expires_at: datetime | None = None

    @field_validator("username")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return value.strip()


class ProxyAccountPasswordUpdate(BaseModel):
    password: str = Field(min_length=1, max_length=512)


class ProxyAccountEnabledUpdate(BaseModel):
    enabled: bool


class ProxyAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    password: str
    enabled: bool
    expires_at: datetime | None
    expired_at: datetime | None
    created_at: datetime
    updated_at: datetime
    status: str


class ProxyAccountPage(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[ProxyAccountRead]
