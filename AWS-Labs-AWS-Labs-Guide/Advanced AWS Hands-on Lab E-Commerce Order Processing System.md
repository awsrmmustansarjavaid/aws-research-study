# Advanced AWS Hands-on Lab E-Commerce Order Processing System

## Prerequisites
- AWS account with permissions to create VPC, EC2, IAM, ALB/NLB, Auto Scaling, S3, Lambda, DynamoDB, CloudWatch, CloudTrail, SNS
- Use 2 Availability Zones (AZs) for HA — e.g. us-east-1a and us-east-1b
- Replace `your-ip/32` with your public IP when restricting SSH

## **AWS Visual Architecture Diagram**
![AWS Labs Visual Architecture Diagram.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/Advanced%20AWS%20Hands-on%20Lab%20E-Commerce%20Order%20Processing%20System.png?raw=true)
---




## 1 — VPC & Subnets

### Console → VPC → Create VPC
- **Name:** `lab-vpc`
- **IPv4 CIDR:** `10.0.0.0/16`
- **Tenancy:** Default

### Create 2 Public Subnets (one per AZ)
- `lab-public-a` → `10.0.1.0/24` (AZ: us-east-1a)
- `lab-public-b` → `10.0.2.0/24` (AZ: us-east-1b)
- **Auto-assign public IP:** Enable

### Create 2 Private Subnets (one per AZ)
- `lab-private-a` → `10.0.10.0/24` (AZ: us-east-1a)
- `lab-private-b` → `10.0.11.0/24` (AZ: us-east-1b)

### Internet Gateway
- Create IGW `lab-igw` → Attach to `lab-vpc`
- Route table for public subnets: Add route `0.0.0.0/0` → `lab-igw`
- Associate `lab-public-a` & `lab-public-b`

### NAT Gateway (for private → internet egress)
- In Console → NAT Gateways: create NAT in one public subnet (`lab-public-a`)
- *For production do 1 per AZ; lab: 1 is fine*
- Create route table `private-rt` with route `0.0.0.0/0` → NAT Gateway
- Associate `lab-private-a` & `lab-private-b`

---

## 2 — Network Security: Security Groups + NACL + Flow Logs

### Security Groups (SG)

Create 3 SGs in VPC:

#### web-sg
- **Type:** Security group `web-sg` (for ALB or public web servers if needed)
- **Inbound:**
  - HTTP (80) Source: `0.0.0.0/0`
  - HTTPS (443) Source: `0.0.0.0/0` (if you enable TLS)
  - SSH (22) Source: `YOUR_IP/32` (replace)
- **Outbound:** Allow all (default)

#### app-sg
- **Name:** `app-sg` (EC2 app)
- **Inbound:**
  - Custom TCP 8080 Source: `web-sg` (select security group as source)
  - SSH (22) Source: `YOUR_IP/32` (optional if you need direct SSH to app)
- **Outbound:** Allow all

#### db-sg
- **Name:** `db-sg` (if you had RDS; for this lab DB is DynamoDB so not required but keep for completeness)
- **Inbound:**
  - HTTPS (443) Source: `app-sg`
- **Outbound:** Allow all

> **Note:** When you use ALB in front of EC2s, the app-sg inbound should allow the ALB security group (not 0.0.0.0/0). In AWS Console there's an option to reference another SG as the source — use that.

### NACL (stateless)

Create NACLs for public and private subnets. NACLs are numeric-ordered rules:

#### Public Subnet NACL (`lab-public-nacl`)
- Rule 100 ALLOW TCP 80 `0.0.0.0/0`
- Rule 110 ALLOW TCP 443 `0.0.0.0/0`
- Rule 120 ALLOW TCP 1024-65535 `0.0.0.0/0` (ephemeral responses)
- Rule 32767 DENY ALL `0.0.0.0/0` (catch-all deny)

#### Private Subnet NACL (`lab-private-nacl`)
- Rule 100 ALLOW TCP 80 `10.0.1.0/24` (if needed)
- Rule 110 ALLOW TCP 443 `10.0.1.0/24`
- Rule 120 ALLOW TCP 8080 `10.0.1.0/24`
- Rule 200 ALLOW TCP 1024-65535 `0.0.0.0/0` (outbound ephemeral)
- Rule 32767 DENY ALL `0.0.0.0/0`

> NACLs apply to subnets. Security Groups are primary filter for instances.

### VPC Flow Logs
- Console → VPC → Flow Logs → Create
- **Resource type:** VPC
- **Filter:** All
- **Destination:** CloudWatch Logs group `lab-vpc-flowlogs`
- **IAM role:** create IAM role `flowlogs-role` as prompted

---

## 3 — IAM Roles & Policies (exact steps)

### EC2 Instance Role (attach to EC2)
- Create IAM role: `lab-ec2-role`
- **Trusted entity:** EC2
- **Attach inline policy (least privilege) — Policy JSON:**

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":["s3:PutObject"],
      "Resource":"arn:aws:s3:::myapp-logs/logs/*"
    },
    {
      "Effect":"Allow",
      "Action":["dynamodb:PutItem","dynamodb:DescribeTable"],
      "Resource":"arn:aws:dynamodb:*:*:table/Orders"
    },
    {
      "Effect":"Allow",
      "Action":["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
      "Resource":"*"
    }
  ]
}
```

Attach role to EC2 when launching (or attach later via Console → EC2 → Actions → Security → Modify IAM Role).

### Lambda Role
- Create `lab-lambda-role`
- **Trusted entity:** Lambda
- **Attach inline policy:**

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":["s3:GetObject"],
      "Resource":"arn:aws:s3:::myapp-uploads/orders/*"
    },
    {
      "Effect":"Allow",
      "Action":["dynamodb:PutItem"],
      "Resource":"arn:aws:dynamodb:*:*:table/Orders"
    },
    {
      "Effect":"Allow",
      "Action":["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
      "Resource":"*"
    }
  ]
}
```

Also add `AWSLambdaBasicExecutionRole` managed policy for CloudWatch logging (if you prefer).

---

## 4 — S3: buckets, public access block, event notification

### Create S3 bucket `myapp-uploads` (use unique name with account suffix)
- **Block all public access:** ON
- **Versioning:** Optional ON
- **Encryption:** Enable default SSE-S3 or SSE-KMS (lab: SSE-S3 OK)

### Create S3 bucket `myapp-logs`
- **Block all public access:** ON
- **Lifecycle:** Move `logs/` prefix to Glacier after X days if you want

### Create folder `orders/` under `myapp-uploads`
(can just upload with key `orders/123.json`)

### S3 Event Notification -> Lambda
In `myapp-uploads` → Properties → Event notifications → Create notification
- **Name:** OrderUpload
- **Event types:** PUT or All object create events
- **Prefix filter:** `orders/`
- **Send to:** Lambda function (select the Lambda you create later)

> **Tip:** If Lambda not yet created, you can configure the event via Lambda console (add S3 trigger) or create notification after.

---

## 5 — DynamoDB: Table config

Console → DynamoDB → Create table
- **Table name:** Orders
- **Partition key:** OrderID (String)
- **Provisioned mode:** On-demand (recommended for lab/testing)
- **Encryption:** AWS owned key (default)

### (Optional) Streams
If you want a second Lambda triggered by Streams, enable DynamoDB Stream (NEW_IMAGE) when creating.

---

## 6 — EC2 Launch & Autoscaling Group (ASG)

### EC2 Launch Template (recommended)
Console → EC2 → Launch Templates → Create launch template
- **Name:** `lab-web-template`
- **AMI:** Amazon Linux 2023
- **Instance type:** t3.micro or t3.small (lab)
- **Key pair:** Select key (for SSH)
- **Network interfaces:**
  - Subnet: Leave blank (ASG will launch into subnets)
  - Security groups: `app-sg` (or `web-sg` if direct public)
  - Auto-assign Public IP: Disable (instances are in private subnets; ALB is public)
- **IAM instance profile:** `lab-ec2-role` (choose role created earlier)
- **User data:** add the corrected deploy script (will run at boot)

### User data example (paste into Launch Template -> Advanced details):

```bash
#!/bin/bash
APP_DIR="/var/myapp"
LOGFILE="$APP_DIR/logs/app.log"
S3_BUCKET="myapp-logs"
mkdir -p $APP_DIR/logs
dnf update -y >> $LOGFILE
dnf install httpd -y >> $LOGFILE
systemctl enable httpd
systemctl start httpd
echo "Deployment completed at $(date)" >> $LOGFILE
aws s3 cp $LOGFILE s3://$S3_BUCKET/logs/$(hostname)-$(date +%s).log
```

### Auto Scaling Group
Create ASG:
- **Name:** `lab-web-asg`
- **Launch template:** `lab-web-template`
- **VPC:** `lab-vpc`
- **Subnets:** `lab-private-a`, `lab-private-b` (private subnets)
- **Desired capacity:** 2 (for HA)
- **Min:** 2, **Max:** 4
- **Health check type:** ELB (if using ALB) and Health check grace period 300s
- **Attach to Target Group:** (create next)

---

## 7 — ALB (Application Load Balancer) — exact settings

### When to choose scheme:
- **Internet-facing** → Accept requests from the internet (typical for public web apps)
- **Internal** → Only reachable inside VPC (for service-to-service traffic)

> **Recommendation for lab:** ALB Internet-facing in public subnets to receive user traffic. Use NLB internal for specific TCP pass-through if needed.

### Create ALB
Console → EC2 → Load Balancers → Create Load Balancer → Application Load Balancer
- **Name:** `lab-alb`
- **Scheme:** Internet-facing
- **IP address type:** IPv4
- **Listeners:** Add listener HTTP 80 (and HTTPS 443 if you want TLS)
- **Availability Zones:** Select `lab-public-a`, `lab-public-b` subnets
- **Security Group:** `web-sg` (allow HTTP/HTTPS)

### Target Group (for ALB)
- **Type:** instance or ip — choose instance (since ASG uses EC2)
- **Protocol:** HTTP
- **Port:** 80
- **Target group name:** `lab-alb-tg`
- **VPC:** `lab-vpc`
- **Health checks:**
  - Protocol: HTTP
  - Path: `/health` (Make sure EC2 has /health endpoint returning 200 — add a simple file or route)
  - Port: traffic port
  - Healthy threshold: 3
  - Unhealthy threshold: 2
  - Timeout: 5
  - Interval: 30
- **Register targets:** don't need to manually register if ASG attaches the target group. When creating ASG attach `lab-alb-tg` so EC2 instances auto-register.

### ALB Configuration
- **ALB idle timeout:** Default 60s. If long-polling or websockets need higher (e.g. 300s), adjust in ALB attributes.
- **(Optional) Stickiness:** enable if you need session affinity (for stateful apps). Not necessary if app is stateless.

---

## 8 — NLB (Network Load Balancer) — exact settings

### When to choose scheme:
- If you need TCP-level load balancing with very low latency or static IPs, use NLB.
- For an internal service-to-service load balancer in VPC use **Internal** scheme.
- For public/bare-metal TCP services choose **Internet-facing**.

> **Recommendation for lab:** Use internal NLB if you want a second entry to EC2 from internal sources (e.g., service that needs Layer-4 load balancing on port 8080). If you intended the NLB to be public, set scheme to Internet-facing. I'll use Internal (private) as lab often puts app servers in private subnets.

### Create NLB
Console → EC2 → Load Balancers → Create Load Balancer → Network Load Balancer
- **Name:** `lab-nlb`
- **Scheme:** Internal
- **Listener:** TCP 8080
- **Subnets:** `lab-private-a`, `lab-private-b`
- **IP Type:** IPv4

### Target Group (for NLB)
- **Type:** instance
- **Protocol:** TCP
- **Port:** 8080
- **Name:** `lab-nlb-tg`
- **Health checks:** TCP (NLB supports TCP-level health checks)
  - Interval: 10s
  - Healthy threshold: 3
  - Unhealthy threshold: 3
- **Register targets:** the EC2 instances from ASG will be attached automatically if you configure ASG to attach `lab-nlb-tg` too.

### Deregistration delay
ALB default is 300s; NLB uses connection draining and behaves differently. For ALB set deregistration delay to 300s (in target group attributes) to allow in-flight requests to complete.

---

## 9 — Health check & readiness

- **ALB health check:** `/health` → return HTTP 200. If you use a static HTML or a simple CGI endpoint on EC2, ensure the server returns 200.
- **EC2 bootstrapping:** use user-data to install dependencies and create `/health` endpoint (e.g., `echo "OK" > /var/www/html/health`).
- **ASG health check grace period:** 300s to let user-data finish.

---

## 10 — Lambda: create function & connect to S3

### Console → Lambda → Create function
- **Name:** `lab-order-processor`
- **Runtime:** Python 3.11 (or 3.10)
- **Role:** Use existing role `lab-lambda-role` or create one with the policy above
- **Timeout:** 30 seconds (set to 60 if large files)
- **Memory:** 256 MB (128 MB could be enough)

### Add S3 trigger
In Lambda console → Configuration → Triggers → Add trigger
- **Select:** S3
- **Bucket:** `myapp-uploads`
- **Event type:** PUT (ObjectCreated)
- **Prefix:** `orders/`
- **(Optional) Suffix:** `.json`

**Deploy code:** paste the improved Lambda code from the .md (with try/except and boto3 calls).

**Test:** Upload small JSON to `myapp-uploads/orders/test-order-1.json` and check Lambda logs in CloudWatch and that DynamoDB entry appears.

---

## 11 — CloudWatch Agent on EC2 (install + config)

### Install & configure agent on Amazon Linux 2023
On EC2 instance (user-data or SSH):

```bash
sudo dnf install -y amazon-cloudwatch-agent
```

### Example config `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json` 
(monitor `/var/log/messages` and `/var/myapp/app.log`):

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/lab/var/log/messages",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/myapp/logs/app.log",
            "log_group_name": "/lab/myapp/app.log",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

### Start agent:

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
```

Ensure the EC2 IAM role has `logs:PutLogEvents`, `logs:CreateLogGroup`, `logs:CreateLogStream`.

---

## 12 — CloudWatch Alarms & SNS

- Create SNS topic `lab-alerts` → subscribe your email.
- CloudWatch → Alarms → Create alarm
  - **Resource:** EC2 instance or Auto Scaling Group
  - **Metric:** CPUUtilization (Minimum/Maximum/Average)
  - **Threshold:** > 70% for 5 minutes
  - **Actions:** Send to SNS topic `lab-alerts`.

---

## 13 — CloudTrail

Console → CloudTrail → Create trail `lab-trail`
- **Apply to all regions:** yes (recommended)
- **Management events:** Read/Write as needed (default all)
- **Storage location:** choose S3 bucket (e.g., `lab-cloudtrail-logs-<acctid>`)
- **Enable log file validation:** optional
- **SNS:** optional for alerts on delete operations

---

## 14 — Cron Job on EC2 for periodic upload to S3

On EC2 instance (as ec2-user or root) create `/var/myapp/deploy.sh` (executable). We included earlier.

Edit crontab:

```bash
sudo crontab -e
# add:
*/30 * * * * /var/myapp/deploy.sh >> /var/myapp/logs/deploy_cron.log 2>&1
```

Verify: `sudo systemctl status crond` and check `deploy_cron.log`.

---

## 15 — Attach ALB & NLB target groups to ASG

When creating your Auto Scaling Group, in the ASG settings attach:
- **Target group:** `lab-alb-tg`
- **(Optional) Target group:** `lab-nlb-tg`

ASG will register instances automatically. Verify in EC2 → Target Groups that healthy instances are registered.

---

## 16 — Test plan (quick checklist)

1. Browse to ALB DNS name (found in Load Balancers console). Expect default page served by EC2 via ALB: `http://<alb-dns>/` and `http://<alb-dns>/health` returns 200.
2. Upload `orders/1001.json` to S3 → verify Lambda invoked and writes to DynamoDB Orders table.
3. Force high CPU on EC2 (stress tool) → CloudWatch alarm triggers email via SNS.
4. Check CloudTrail S3 bucket has recent log files; check VPC Flow Logs in CloudWatch.
5. Verify CloudWatch logs include `/var/myapp/app.log` entries being delivered.

---

## 17 — Helpful CLI snippets

### Create target group (ALB) via AWS CLI:

```bash
aws elbv2 create-target-group \
  --name lab-alb-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxxxxx \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --target-type instance
```

### Create ALB (CLI simplified):

```bash
aws elbv2 create-load-balancer \
  --name lab-alb \
  --subnets subnet-aaa subnet-bbb \
  --security-groups sg-aaa \
  --scheme internet-facing \
  --type application
```

### Create NLB (internal):

```bash
aws elbv2 create-load-balancer \
  --name lab-nlb \
  --subnets subnet-private-a subnet-private-b \
  --scheme internal \
  --type network
```

> Create S3 event notification (via CLI is more verbose; easiest to do in Console or via Lambda console).

---

## 18 — Extra recommendations & troubleshooting tips

- **ALB health check failing:** Verify `/health` exists and returns 200. Check instance security groups and route tables.
- **NLB not registering:** Use TCP health checks and ensure instance security group allows the NLB source (for internal NLB source is the subnet CIDR).
- **IAM Errors:** Check CloudWatch logs for permissions denied; attach the least-privilege policies described earlier.
- **S3 → Lambda not triggered:** Ensure S3 bucket and Lambda are in same region and the Lambda has permission `s3:InvokeFunction` (Console auto-adds the permission when adding trigger).
- **CloudWatch Agent not sending logs:** Ensure role has `logs:PutLogEvents` and the agent config paths are correct.
- **DNS latency or ALB not reachable:** Check ALB scheme (internet-facing) and that ALB is in public subnets with IGW route.

---

## 19 — Minimal resource naming map for your lab

| Resource Type | Name |
|---------------|------|
| **VPC** | `lab-vpc` |
| **Public subnets** | `lab-public-a`, `lab-public-b` |
| **Private subnets** | `lab-private-a`, `lab-private-b` |
| **IGW** | `lab-igw` |
| **NAT** | `lab-nat` |
| **ALB** | `lab-alb`, TG: `lab-alb-tg` |
| **NLB** | `lab-nlb`, TG: `lab-nlb-tg` |
| **ASG** | `lab-web-asg`, Launch template `lab-web-template` |
| **EC2 IAM role** | `lab-ec2-role` |
| **Lambda** | `lab-order-processor`, role `lab-lambda-role` |
| **S3** | `myapp-uploads`, `myapp-logs` |
| **DynamoDB** | `Orders` |
| **CloudWatch Log Groups** | `/lab/var/log/messages`, `/lab/myapp/app.log`, `/aws/vpc/flowlogs/...` |
| **SNS topic** | `lab-alerts` |
| **CloudTrail trail** | `lab-trail` |

---

*This guide provides a complete, production-ready AWS infrastructure setup with high availability, security best practices, monitoring, and automated scaling.*