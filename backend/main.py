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

HOURLY_RATES = {
    "t1.micro": 0.0116,
    "t2.nano": 0.0058,
    "t2.micro": 0.0116,
    "t3.micro": 0.0104,
    "t2.small": 0.023,
    "t3.small": 0.0208,
    "t2.medium": 0.0464,
    "t3.medium": 0.0416,
    "m5.large": 0.096,
    "default": 0.05
}

def get_monthly_cost(instance_type: str) -> float:
    rate = HOURLY_RATES.get(instance_type, HOURLY_RATES["default"])
    return rate * 730

def update_aws_data(db: Session):
    collector = AWSCollector()
    
    ec2_data = collector.get_ec2_instances()
    db.query(models.EC2Instance).delete()
    for data in ec2_data:
        db.add(models.EC2Instance(**data))
        
    s3_data = collector.get_s3_buckets()
    db.query(models.S3Bucket).delete()
    for data in s3_data:
        db.add(models.S3Bucket(**data))
        
    db.commit()

@app.post("/api/sync")
def sync_aws_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(update_aws_data, db)
    return {"message": "Data sync started."}

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
        if instance.state == 'running':
            cost = get_monthly_cost(instance.instance_type)
            
            if instance.cpu_utilization < 5.0:
                recommendations.append(schemas.Recommendation(
                    resource_id=instance.instance_id,
                    resource_type="EC2",
                    issue="Idle Instance Component",
                    recommendation=f"Terminate. Recovers ${cost:.2f}/mo.",
                    severity="Critical",
                    estimated_savings_monthly=cost
                ))
            elif instance.cpu_utilization < 20.0:
                rightsize_savings = cost * 0.5 # Assuming rightsize yields 50%
                recommendations.append(schemas.Recommendation(
                    resource_id=instance.instance_id,
                    resource_type="EC2",
                    issue="Underutilized Node",
                    recommendation=f"Rightsize to lower tier. Recovers ~${rightsize_savings:.2f}/mo.",
                    severity="Medium",
                    estimated_savings_monthly=rightsize_savings
                ))

    return recommendations

@app.get("/api/summary", response_model=schemas.SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    ec2_instances = db.query(models.EC2Instance).all()
    total_ec2 = len(ec2_instances)
    total_s3 = db.query(models.S3Bucket).count()
    
    total_cost_monthly = sum([get_monthly_cost(i.instance_type) for i in ec2_instances if i.state == 'running'])
    
    recommendations = get_recommendations(db)
    waste_count = len(recommendations)
    estimated_savings = sum([r.estimated_savings_monthly for r in recommendations])
    
    recommendations.sort(key=lambda x: x.estimated_savings_monthly, reverse=True)
    
    top_rec = None
    if recommendations and recommendations[0].estimated_savings_monthly > 0:
        best = recommendations[0]
        top_rec = f"Stop {best.resource_type} node {best.resource_id} -> Recovers ${best.estimated_savings_monthly:.2f}/month"
        
    return schemas.SummaryResponse(
        total_ec2=total_ec2,
        total_s3=total_s3,
        waste_count=waste_count,
        total_cost_monthly=total_cost_monthly,
        estimated_savings_monthly=estimated_savings,
        top_recommendation=top_rec
    )

@app.post("/api/action/simulate")
def simulate_action(req: schemas.ActionSimulateRequest, db: Session = Depends(get_db)):
    if req.resource_type == "EC2":
        db.query(models.EC2Instance).filter(models.EC2Instance.instance_id == req.resource_id).delete()
    if req.resource_type == "S3":
        db.query(models.S3Bucket).filter(models.S3Bucket.bucket_name == req.resource_id).delete()
        
    db.commit()
    return {"status": "success", "message": f"Resource {req.resource_id} terminated locally for simulation."}

if os.path.exists("/frontend"):
    app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")
elif os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
