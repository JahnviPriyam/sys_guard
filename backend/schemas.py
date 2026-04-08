from pydantic import BaseModel
from typing import List, Optional

class EC2InstanceBase(BaseModel):
    instance_id: str
    instance_type: str
    state: str
    cpu_utilization: float
    uptime_hours: float

class EC2Instance(EC2InstanceBase):
    id: int
    class Config:
        from_attributes = True

class S3BucketBase(BaseModel):
    bucket_name: str
    size_mb: float
    days_since_last_access: int

class S3Bucket(S3BucketBase):
    id: int
    class Config:
        from_attributes = True

class Recommendation(BaseModel):
    resource_id: str
    resource_type: str
    issue: str
    recommendation: str
    severity: str
    estimated_savings_monthly: float

class SummaryResponse(BaseModel):
    total_ec2: int
    total_s3: int
    waste_count: int
    estimated_savings_monthly: float
