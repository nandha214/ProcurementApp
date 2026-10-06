# CSE2025 – AWS Solution Architect: Final Project Documentation & Deployment Guide

**Course:** CSE2025 – AWS Solution Architect  
**Faculty:** Dr. Renita R  
**Assessment:** Design and Deploy a Cloud-Based Application Using Amazon Web Services (AWS) — 20 Marks  
**Project Title:** Procurement Standards Recommendation System (AI-Driven Semantic Search Engine)  
**GitHub Repository:** [https://github.com/nandha214/ProcurementApp](https://github.com/nandha214/ProcurementApp)  
**Deadline:** 09 October 2026  

---

## 1. Executive Summary & Problem Statement (2 Marks)

### Problem Statement
In public procurement and industrial engineering across India, tender specifications must comply with mandatory Indian Standards (IS codes) formulated by the Bureau of Indian Standards (BIS). Organizations frequently deal with complex, multi-page procurement requirements (e.g., high-tensile steel bars, street luminaire installations, solar PV modules). Manually identifying the exact applicable standards, verifying whether they fall under mandatory Quality Control Orders (QCOs) or Compulsory Registration Schemes (CRS), and mapping allied test methods is labor-intensive, error-prone, and causes compliance delays or legal disputes.

### Project Objectives
1. **Automated Semantic Retrieval:** Enable procurement officers to enter free-form, natural language requirement specifications and instantly retrieve ranked Indian Standards.
2. **Zero-Shot AI Recommendation:** Utilize Sentence Transformers (`all-MiniLM-L6-v2`) and ChromaDB vector indexing to capture semantic intent beyond traditional keyword matching.
3. **Cloud-Native AWS Architecture:** Design and deploy a resilient, cost-effective, and secure cloud solution on AWS utilizing **AWS IAM, Amazon EC2, Amazon S3, and Amazon DynamoDB**.
4. **Auditability & Observability:** Automatically persist query logs, inference latencies, and recommended standards into Amazon DynamoDB for compliance tracking and audit trails.

---

## 2. AWS Cloud Architecture Design (4 Marks)

### Architectural Overview

The application follows a 3-tier decoupled cloud architecture:
- **Presentation & Web Tier:** React (Vite + Tailwind CSS) served via Nginx reverse proxy on Amazon EC2.
- **Application & Compute Tier:** Django REST Framework running under Gunicorn WSGI on Amazon EC2, executing vector search via Sentence Transformers and ChromaDB.
- **Data & Storage Tier:** 
  - **Amazon S3:** Object storage hosting the master Indian Standards catalog (`bis_data.json`) and query report archives.
  - **Amazon DynamoDB:** Serverless NoSQL table (`bis_search_logs`) recording real-time search logs, query timestamps, and latency metrics.
- **Security & Identity Tier:** **AWS IAM** instance profile role attached to EC2, granting least-privilege permissions to S3 and DynamoDB without storing hardcoded API credentials.

```text
+-------------------------------------------------------------------------------+
|                             CLIENT / USER TIER                                |
|  Web Browser / Procurement Officer (Public Access via HTTP Port 80)           |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                    AMAZON EC2 COMPUTE TIER (Ubuntu 24.04 LTS)                 |
|                                                                               |
|   +-----------------------------------------------------------------------+   |
|   |                  Nginx Web Server & Reverse Proxy                     |   |
|   |   - Port 80: Serves React (Vite) Single Page Application              |   |
|   |   - Routes /api/* requests to Gunicorn WSGI Server                   |   |
|   +-----------------------------------------------------------------------+   |
|                                      |                                        |
|                                      v                                        |
|   +-----------------------------------------------------------------------+   |
|   |              Gunicorn WSGI Application Server (Port 8000)             |   |
|   |   - Django REST Framework (backend/api/views.py)                      |   |
|   |   - Semantic Recommendation Engine (all-MiniLM-L6-v2 + ChromaDB)      |   |
|   +-----------------------------------------------------------------------+   |
|                                      |                                        |
+-------------------------------------------------------------------------------+
          | (boto3 via IAM Role)                         | (boto3 via IAM Role)
          v                                              v
+-----------------------------------+          +--------------------------------+
|       STORAGE: AMAZON S3          |          |     DATABASE: AMAZON DYNAMODB  |
| Bucket: procurement-standards-... |          | Table: bis_search_logs         |
| Holds: bis_data.json Catalog      |          | Holds: Query Audit Logs,       |
| & Compliance Export Reports       |          | Latency & Timestamp Metrics    |
+-----------------------------------+          +--------------------------------+
                                       ^
                                       |
                   +---------------------------------------+
                   |           SECURITY: AWS IAM           |
                   | Role: EC2-ProcurementApp-Role         |
                   | Grants temporary IMDSv2 credentials   |
                   +---------------------------------------+
```

---

## 3. AWS Service Selection & Justification (4 Marks)

| Mandatory AWS Service | Role in Project | Architectural Justification | Free Tier Compliance |
| :--- | :--- | :--- | :--- |
| **AWS IAM** | Identity & Access Management | Implements the **Principle of Least Privilege**. Instead of embedding long-lived AWS Access Keys into source code or `.env` files, an IAM Instance Profile Role is attached directly to the EC2 instance. Boto3 automatically retrieves temporary credentials via the EC2 Instance Metadata Service (IMDSv2). | Always Free |
| **Amazon EC2** | Compute Service | Hosts the full-stack application (Nginx web server, Gunicorn, Django REST API, and the Sentence Transformer AI engine). Configured with Ubuntu 24.04 LTS on a `t2.micro` or `t3.micro` instance with 2GB swap space for memory stability during vector inference. | 750 hours/month free under Free Tier |
| **Amazon S3** | Object Storage Service | Provides 99.999999999% (11 9's) durability for storing the authoritative BIS dataset (`bis_data.json`) and generated tender compliance audit exports. Decouples dataset storage from compute, allowing data updates without redeploying code. | 5 GB standard storage free |
| **Amazon DynamoDB** | Database Service | Serverless, fully managed NoSQL key-value database. Ideal for storing semi-structured search audit logs (`id`, `query`, `timestamp`, `inference_ms`, `top_standards`). Delivers single-digit millisecond latency with zero database server management. | 25 GB storage + 25 RCU/WCU free |
| **Amazon CloudWatch** *(Optional)* | Monitoring & Alarms | Tracks EC2 CPU utilization, network I/O, and disk space to ensure system availability. | 10 custom metrics & basic monitoring free |

---

## 4. End-to-End AWS Free Tier Deployment Guide (6 Marks)

Follow these exact steps to launch your app on AWS, generate your live public link, and capture all required submission screenshots before October 9th:

### Step 1: Create the AWS IAM Role
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **IAM** > **Roles** > click **Create role**.
3. Select **AWS service** as Trusted entity type and choose **EC2**.
4. In permissions policies, attach:
   - `AmazonS3FullAccess`
   - `AmazonDynamoDBFullAccess`
5. Name the role: `EC2-ProcurementApp-Role` and click **Create role**.
> *Screenshot 1: Take screenshot of this IAM Role showing attached policies.*

### Step 2: Create the Amazon DynamoDB Table
1. Navigate to **DynamoDB** > click **Create table**.
2. **Table name:** `bis_search_logs`
3. **Partition key (Primary key):** `id` (Type: `String`).
4. Table settings: Select **Default settings** (or Customize > **On-Demand** capacity mode).
5. Click **Create table**.
> *Screenshot 2: Take screenshot of the `bis_search_logs` table details.*

### Step 3: Create the Amazon S3 Bucket
1. Navigate to **S3** > click **Create bucket**.
2. **Bucket name:** `procurement-standards-<your-rollnumber>` (e.g. `procurement-standards-nandha214`).
3. Keep **Block all public access** enabled.
4. Click **Create bucket**.
5. Open your new bucket, click **Upload**, and upload `backend/api/bis_data.json` from the repository.
> *Screenshot 3: Take screenshot of the S3 bucket showing `bis_data.json` uploaded.*

### Step 4: Launch the Amazon EC2 Instance
1. Navigate to **EC2** > click **Launch instance**.
2. **Name:** `ProcurementApp-Server`
3. **AMI:** **Ubuntu Server 24.04 LTS** (Free Tier eligible)
4. **Instance Type:** `t2.micro` (or `t3.micro`)
5. **Key pair:** Create or select an existing `.pem` key pair.
6. **Network Settings (Security Group):**
   - Allow **SSH** traffic (Port 22) from `My IP` (or `Anywhere`).
   - Allow **HTTP** traffic (Port 80) from **Anywhere (`0.0.0.0/0`)**.
7. **Advanced Details:**
   - Under **IAM instance profile**, select `EC2-ProcurementApp-Role`.
8. Click **Launch instance**.
> *Screenshot 4: Take screenshot of the running EC2 instance showing Public IPv4 and attached IAM Role.*

### Step 5: Connect and Run the Automated Deployment Script
1. SSH into your EC2 instance:
   ```bash
   ssh -i "your-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/nandha214/ProcurementApp.git
   cd ProcurementApp
   ```
3. Run the automated deployment script:
   ```bash
   chmod +x setup_ec2.sh
   ./setup_ec2.sh
   ```
4. The script automates everything: swap allocation, dependencies, build, Gunicorn service, and Nginx.

### Step 6: Test Your Live Public Link!
Open your web browser and visit:
```text
http://<YOUR-EC2-PUBLIC-IP>
```
You will see the **Procurement Standards Recommendation System** live on the public internet!
- Perform a search (e.g., click "We need 100W LED street lights for municipal roads").
- You will see the green badge: **"Logged to AWS DynamoDB"**.
- Click **"View AWS Architecture Status"** to see live confirmation of EC2, S3, DynamoDB, and IAM.
> *Screenshot 5: Take screenshot of the live web application in your browser showing search results and DynamoDB confirmation.*
> *Screenshot 6: Open AWS DynamoDB Console > `bis_search_logs` > Explore items. Take screenshot showing newly created log items.*

---

## 5. Viva Demonstration Guide (FAQ & Expected Questions)

**Q1: What are the 4 mandatory AWS services used in your project?**  
*Answer:*  
1. **AWS IAM:** EC2 Instance Profile Role (`EC2-ProcurementApp-Role`) managing secure, temporary access to S3 and DynamoDB without hardcoding secret keys.  
2. **Amazon EC2:** Compute instance hosting Ubuntu with Nginx and Gunicorn, running Django and Sentence Transformer model inference.  
3. **Amazon S3:** Object storage bucket hosting the master BIS dataset (`bis_data.json`) and audit archives.  
4. **Amazon DynamoDB:** Managed NoSQL database storing query transaction logs, inference timestamps, and latency metrics in the `bis_search_logs` table.  

**Q2: Why did you choose Amazon DynamoDB instead of Amazon RDS?**  
*Answer:*  
Search audit logs are event-driven, high-velocity, and semi-structured key-value documents. DynamoDB offers single-digit millisecond write latency, seamless horizontal scaling, zero relational overhead, and 25 GB of permanent free storage under AWS Free Tier. RDS would incur compute instance overhead and database connection pool costs that are unnecessary for write-heavy audit logging.

**Q3: How does your application authenticate with S3 and DynamoDB securely?**  
*Answer:*  
We follow the AWS Security Pillar best practice. We attached an IAM Instance Profile to the EC2 instance. When Python's `boto3` SDK makes calls to DynamoDB or S3, it queries the EC2 Instance Metadata Service (IMDS) at `169.254.169.254` to obtain temporary rotating STS credentials. No secret keys or access tokens are stored in the codebase or on the server.

**Q4: How does the AI recommendation model work?**  
*Answer:*  
The model utilizes zero-shot semantic retrieval. The BIS standards dataset contains 77 technical standards embedded using the pretrained `all-MiniLM-L6-v2` Sentence Transformer into 384-dimensional dense vectors and indexed in ChromaDB. When a procurement query is submitted, it is embedded using the same vector space, and approximate nearest neighbor (HNSW cosine similarity) search retrieves and ranks the top matching Indian Standards in under 50 milliseconds.

---

## 6. Resource Termination Policy (Avoid AWS Charges)

Immediately after your faculty marks your demonstration and viva:
1. Go to **EC2 Console** > select your instance > **Terminate instance**.
2. Go to **S3 Console** > select your bucket > **Empty**, then **Delete**.
3. Go to **DynamoDB Console** > select `bis_search_logs` > **Delete table**.
4. Go to **IAM Console** > delete the created role.
