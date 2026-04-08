from sqlalchemy import Column, Integer, String, Float

from database import Base

class EC2Instance(Base):
    __tablename__ = "ec2_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(255), unique=True, index=True, nullable=False)
    instance_type = Column(String(255), nullable=False)
    state = Column(String(50), nullable=False)
    cpu_utilization = Column(Float, default=0.0)
    uptime_hours = Column(Float, default=0.0)

class S3Bucket(Base):
    __tablename__ = "s3_buckets"

    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(String(255), unique=True, index=True, nullable=False)
    size_mb = Column(Float, default=0.0)
    days_since_last_access = Column(Integer, default=0)
