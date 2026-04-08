# SYS_GUARD (CloudGuard) // AWS Telemetry & FinOps Pipeline

![Python](https://img.shields.io/badge/python-3.10-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.115-green)
![Docker](https://img.shields.io/badge/docker-compose-blue)

**SYS_GUARD (CloudGuard)** is an intense, high-performance Cloud Financial Operations (FinOps) monitoring dashboard. It combines a highly unique, terminal-inspired dark-mode interface with a robust Python/FastAPI backend to scan live AWS cloud environments, assess architectural loads, and identify cloud resource waste.

## 🚀 Features
- **Live AWS Telemetry:** Connects directly to AWS via `boto3` to scan EC2 instances and S3 Buckets recursively.
- **Anomaly & Waste Detection:** Analyzes metric patterns to flag underutilized infrastructure (Idle EC2s, Empty S3 Buckets) and calculates potential monthly cost recovery allocations.
- **Intense CSE Interface:** Features a custom-built, hardware-terminal style dashboard with typing load scripts, simulated real-time event logs, and dynamic grid layouts.
- **Containerized Architecture:** Fully dockerized stack containing a custom API and a dedicated MySQL server.

## 🧠 System Architecture

```text
[ AWS Cloud ]
      | (boto3 / REST API)
      v
+-------------------------------+
|         FastAPI Backend       | 
|  (Data Aggregation Engine)    | 
|                               |
|  [ aws_collector.py ]         |
|  [ models.py / schemas.py ]   |
+-------------------------------+
      |                 ^
   (SQLAlchemy)         | (JSON REST Responses)
      v                 |
[ MySQL 8.0 ]    [ HTML/JS Client ]
 (Dockerized)     (Intense Dashboard UI)
```

## 🛠 Tech Stack
- **Frontend:** Vanilla HTML5, CSS3 (*Custom `Rajdhani` & `JetBrains Mono` Typography*), JavaScript (ES6), Chart.js
- **Backend:** Python 3.10, FastAPI, Uvicorn, SQLAlchemy
- **Database:** MySQL 8.0, PyMySQL
- **Cloud Provider:** Amazon Web Services (AWS SDK / Boto3)
- **Deployment:** Docker & Docker Compose

## ⚡ Deployment & Setup

### Prerequisites
- Docker and Docker Compose installed
- AWS IAM Access Keys with `AmazonEC2ReadOnlyAccess` and `AmazonS3ReadOnlyAccess`

### Initialization Protocol

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sys_guard.git
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

4. **Access the Terminal:**
   Navigate to `http://localhost:8000` in your browser. Click `INIT_SYNC()` on the left sidebar to dispatch the data pipeline task and populate the charts with live metrics.

---
> *Built as a Computer Science Engineering project focusing on Cloud Architecture, FinOps, and interactive web visualization.*
