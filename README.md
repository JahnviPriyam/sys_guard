# SYS_GUARD (CloudGuard) // AWS Telemetry & FinOps Engine

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.115-green)
![Docker](https://img.shields.io/badge/docker-compose-blue)

**SYS_GUARD** is a high-performance Cloud Financial Operations (FinOps) engineering tool. It solves a critical problem in modern cloud architecture: **Resource Sprawl and Waste**. By actively auditing live AWS infrastructure, compiling telemetry, and applying real-time cost analysis algorithms, it provides actionable directives to recover lost capital.

## ⚠️ The FinOps Problem
Companies deploy thousands of cloud components across AWS. Over time, instances are left running idle, and storage buckets are abandoned, leading to thousands of dollars in continuous "cloud burn rate."

**SYS_GUARD** connects directly to an AWS environment, computes the exact cost of each instance dynamically (`cost = uptime_hours * hourly_tier_rate`), and identifies underutilized resources to calculate an immediate ROI on cleanup.

## 🚀 Key Features
- **Cost Engine Automation:** Maps live AWS EC2 types to hardcoded hourly pricing dictionaries to calculate exact monthly burn rate and potential recovery values.
- **Top Directive Routing:** An algorithmic sort locates the absolute highest-value remediation action and highlights it directly to the operator.
- **One-Click Remediation (`[EXECUTE]`):** A dedicated endpoint that simulates automating the termination of wasteful resources, purging the database and instantly adjusting the UI math.
- **Intense CSE Interface:** A custom-built, hardware-terminal style dashboard with typing load scripts, simulated real-time event logs, and dynamic grid layouts.

## 🧠 System Architecture

```text
[ Live AWS Cloud ]
      |
      | (boto3 / REST API)
      v
+-----------------------------------+
|         FastAPI Backend           | 
|                                   | 
| [ aws_collector.py (Data Sync) ]  |
| [ main.py (Cost Math Engine)   ]  |
+-----------------------------------+
      |                      ^
   (SQLAlchemy)              | (JSON REST Responses)
      v                      |
[ MySQL 8.0 ]         [ HTML/JS Client ]
 (Dockerized)         (Dynamic FinOps UI)
```

## ⚡ Deployment & Setup

### Prerequisites
- Docker and Docker Compose
- AWS IAM Access Keys with `AmazonEC2ReadOnlyAccess` and `AmazonS3ReadOnlyAccess`

### Initialization Protocol

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JahnviPriyam/sys_guard.git
   cd sys_guard
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory (this is gitignored for security) and add your AWS credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **Launch the Container Stack:**
   ```bash
   docker-compose up --build -d
   ```

4. **Operate Terminal:**
   Navigate to `http://localhost:8000`. Click `INIT_SYNC()` to dispatch the data pipeline. Review the `Top Directive`, or click `[EXECUTE]` on any detected waste anomaly to simulate automated infrastructure remediation.

---
> *Architected as a robust Computer Science Engineering project focusing on Cloud Infrastructure, FinOps Algorithms, and Full-Stack Visualization.*
