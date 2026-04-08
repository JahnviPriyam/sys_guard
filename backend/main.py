from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from database import engine, get_db, Base
import models, schemas
from aws_collector import AWSCollector

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CloudGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_aws_data(db: Session):
    collector = AWSCollector()
    
    # EC2
    ec2_data = collector.get_ec2_instances()
    db.query(models.EC2Instance).delete() # Reset table for simplicity
    for data in ec2_data:
        db.add(models.EC2Instance(**data))
        
    # S3
    s3_data = collector.get_s3_buckets()
    db.query(models.S3Bucket).delete()
    for data in s3_data:
        db.add(models.S3Bucket(**data))
        
    db.commit()

@app.post("/api/sync")
def sync_aws_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger AWS data collection in background to avoid long web requests."""
    background_tasks.add_task(update_aws_data, db)
    return {"message": "Data sync started. Please check back in a few moments."}

@app.get("/api/ec2", response_model=list[schemas.EC2Instance])
def get_ec2(db: Session = Depends(get_db)):
    return db.query(models.EC2Instance).all()

@app.get("/api/s3", response_model=list[schemas.S3Bucket])
def get_s3(db: Session = Depends(get_db)):
    return db.query(models.S3Bucket).all()

@app.get("/api/recommendations", response_model=list[schemas.Recommendation])
def get_recommendations(db: Session = Depends(get_db)):
    recommendations = []
    
    for instance in db.query(models.EC2Instance).all():
        # Recommendations logic
        if instance.state == 'running':
            if instance.cpu_utilization < 5.0:
                recommendations.append(schemas.Recommendation(
                    resource_id=instance.instance_id,
                    resource_type="EC2",
                    issue="Idle Instance",
                    recommendation="Stop or Terminate to save costs.",
                    severity="High",
                    estimated_savings_monthly=8.50 # roughly a t2.micro
                ))
            elif instance.cpu_utilization < 20.0:
                recommendations.append(schemas.Recommendation(
                    resource_id=instance.instance_id,
                    resource_type="EC2",
                    issue="Underutilized Resource",
                    recommendation="Consider rightsizing to a smaller instance.",
                    severity="Medium",
                    estimated_savings_monthly=4.00
                ))
        
        if instance.uptime_hours > 650:
            recommendations.append(schemas.Recommendation(
                resource_id=instance.instance_id,
                resource_type="EC2",
                issue="Free Tier Risk",
                recommendation="Uptime nearing 750h free tier limit for the month. Consider stopping if not needed.",
                severity="Critical",
                estimated_savings_monthly=0.0 # Preventative
            ))

    for bucket in db.query(models.S3Bucket).all():
        if bucket.size_mb == 0.0 or bucket.days_since_last_access >= 30:
             recommendations.append(schemas.Recommendation(
                resource_id=bucket.bucket_name,
                resource_type="S3",
                issue="Unused Bucket",
                recommendation="Delete empty or unused buckets.",
                severity="Low",
                estimated_savings_monthly=0.0 # Small costs typically
            ))
            
    return recommendations

@app.get("/api/summary", response_model=schemas.SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    total_ec2 = db.query(models.EC2Instance).count()
    total_s3 = db.query(models.S3Bucket).count()
    
    recommendations = get_recommendations(db)
    waste_count = len(recommendations)
    estimated_savings = sum([r.estimated_savings_monthly for r in recommendations])
    
    return schemas.SummaryResponse(
        total_ec2=total_ec2,
        total_s3=total_s3,
        waste_count=waste_count,
        estimated_savings_monthly=estimated_savings
    )

if os.path.exists("/frontend"):
    app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")
elif os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
