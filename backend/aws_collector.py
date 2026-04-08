import boto3
import os
from datetime import datetime, timedelta

class AWSCollector:
    def __init__(self):
        # boto3 will automatically pick up AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION
        self.ec2_client = boto3.client('ec2')
        self.s3_client = boto3.client('s3')
        self.cloudwatch_client = boto3.client('cloudwatch')

    def get_ec2_instances(self):
        instances_data = []
        try:
            response = self.ec2_client.describe_instances()
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId')
                    instance_type = instance.get('InstanceType')
                    state = instance.get('State', {}).get('Name')
                    
                    launch_time = instance.get('LaunchTime')
                    uptime_hours = 0
                    if launch_time:
                        uptime_hours = (datetime.now(launch_time.tzinfo) - launch_time).total_seconds() / 3600.0

                    cpu_utilization = 0.0
                    if state == 'running':
                        cpu_utilization = self._get_avg_cpu(instance_id)

                    instances_data.append({
                        "instance_id": instance_id,
                        "instance_type": instance_type,
                        "state": state,
                        "cpu_utilization": cpu_utilization,
                        "uptime_hours": uptime_hours
                    })
        except Exception as e:
            print(f"Error fetching EC2 data: {e}")
            
        return instances_data

    def _get_avg_cpu(self, instance_id):
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400, # 1 day
                Statistics=['Average']
            )
            datapoints = response.get('Datapoints', [])
            if datapoints:
                return datapoints[0].get('Average', 0.0)
            return 0.0
        except Exception as e:
            print(f"Error fetching CPU metric for {instance_id}: {e}")
            return 0.0

    def get_s3_buckets(self):
        buckets_data = []
        try:
            response = self.s3_client.list_buckets()
            for bucket in response.get('Buckets', []):
                bucket_name = bucket.get('Name')
                size_mb, days_since_last_access = self._get_s3_metrics(bucket_name)
                
                buckets_data.append({
                    "bucket_name": bucket_name,
                    "size_mb": size_mb,
                    "days_since_last_access": days_since_last_access
                })
        except Exception as e:
            print(f"Error fetching S3 data: {e}")
            
        return buckets_data

    def _get_s3_metrics(self, bucket_name):
        try:
            # Note: Fetching accurate last access date is complex without server access logging or paid tools (S3 Storage Lens/Cloudtrail). 
            # We approximate size using CloudWatch basic metrics to stay strictly within free tier.
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=2)
            
            response_size = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=['Average']
            )
            
            size_mb = 0.0
            datapoints = response_size.get('Datapoints', [])
            if datapoints:
                size_mb = datapoints[0].get('Average', 0.0) / (1024 * 1024)

            # Simulated 'days since last access' for the purpose of the free basic tier limit
            # Since true access logs cost money
            days_since_last_access = 0
            if size_mb == 0.0:
                days_since_last_access = 30 # assume unused if empty
                
            return size_mb, days_since_last_access
        except Exception as e:
            print(f"Error fetching metrics for bucket {bucket_name}: {e}")
            return 0.0, 0
