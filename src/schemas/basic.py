from pydantic import BaseModel, Field


class TextOnly(BaseModel):
    text: str = Field(..., title="Text", description="Text content")


class Token(BaseModel):
    access_token: str = Field(default='example_token')
    token_type: str = Field(default='bearer')


class UploadedFile(BaseModel):
    path: str = Field(..., title="Local Path")
    original_file_name: str = Field(..., title="Original File Name")
    extension: str = Field(..., title="File Extension")
    content_type: str = Field(..., title="Content Type")


class ServiceStatus(BaseModel):
    status: str = Field(..., title="Status", description="Service status: healthy or unhealthy")
    message: str = Field(default="", title="Message", description="Additional information")


class HealthCheck(BaseModel):
    status: str = Field(..., title="Overall Status", description="Overall health status")
    mysql: ServiceStatus = Field(..., title="MySQL Status")
    redis: ServiceStatus = Field(..., title="Redis Status")