# SYS_GUARD (CloudGuard)

### AWS Telemetry & FinOps Engine

🚀 **Live FinOps system that detects cloud waste, calculates real-time cost impact, and simulates automated recovery.**

---

## ⚠️ The Problem

Modern cloud environments silently leak money.

Idle EC2 instances, unused storage, and forgotten resources create a continuous **cloud burn rate** that most teams don’t actively monitor.

---

## 💡 The Solution

SYS_GUARD is a **FinOps-focused cost intelligence engine** that:

* Connects to AWS infrastructure
* Translates resource usage into **real monetary cost**
* Detects inefficiencies
* Converts them into **actionable savings directives**

---

## 🔥 Key Features

### 💰 Real-Time Cost Engine

* Dynamically calculates cost using:

  ```
  cost = uptime_hours × hourly_rate
  ```
* Maps EC2 instance types to pricing models
* Displays total burn rate + potential savings

---

### ⚡ Top Directive System

* Identifies the **highest-impact optimization**
* Highlights it as a priority action for immediate ROI

---

### 🧠 Waste Detection Engine

Detects:

* Idle EC2 instances (low CPU usage)
* Underutilized resources (rightsizing candidates)
* Free-tier risk exposure

---

### 🎯 One-Click Remediation

* `[EXECUTE]` simulates optimization
* Updates system state instantly
* Recalculates:

  * total cost ↓
  * savings ↑

---

### 🖥️ Interactive FinOps Dashboard

* Terminal-inspired UI
* Real-time event logs
* Cost vs recovery visualization
* Optimization directives with severity levels

---

## 🧠 Architecture

```
[ AWS Cloud ]
      |
      | (boto3)
      v
+---------------------------+
|      FastAPI Backend      |
|---------------------------|
| Cost Engine               |
| Optimization Engine       |
| AWS Data Collector        |
+---------------------------+
      |
      v
[ MySQL (Docker) ]
      |
      v
[ Frontend Dashboard ]
```

---

## ⚡ How It Works

1. Fetch AWS resource data (EC2, S3)
2. Compute real-time cost using pricing logic
3. Apply optimization rules
4. Generate savings recommendations
5. Execute (simulate) actions → instantly reflect cost changes

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Cloud Integration:** boto3 (AWS SDK)
* **Database:** MySQL (Dockerized)
* **Frontend:** HTML, CSS, JavaScript, Chart.js
* **DevOps:** Docker, Docker Compose

---

## 🚀 Setup & Run

### Prerequisites

* Docker + Docker Compose
* AWS IAM credentials (ReadOnly access)

### Steps

```bash
git clone https://github.com/JahnviPriyam/sys_guard.git
cd sys_guard
```

Create `.env` file:

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

Run:

```bash
docker-compose up --build -d
```

Open:

```
http://localhost:8000
```

Click:

```
INIT_SYNC()
```

---

## 🎬 Demo Flow

1. System syncs AWS telemetry
2. Displays total cost + potential savings
3. Highlights top directive
4. Execute optimization
5. Watch cost drop in real-time

---

This system closes the loop:

> **Usage → Cost → Optimization → Impact**

It doesn’t just monitor infrastructure —
it **quantifies financial waste and drives cost recovery decisions**.

---

## ⭐ Impact

* Converts infrastructure data into **financial insights**
* Enables **cost-aware engineering decisions**
* Simulates real-world FinOps workflows

---
