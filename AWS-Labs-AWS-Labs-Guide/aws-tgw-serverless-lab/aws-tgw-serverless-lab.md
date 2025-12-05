# Building a Secure Multi-VPC Mesh Using AWS Transit Gateway, Private Endpoints & Serverless Applications

A hands‑on lab that builds a multi-VPC production‑grade AWS environment using Transit Gateway, VPC endpoints, IAM policies, Lambda, DynamoDB, S3, CloudTrail, CloudWatch, AWS Config, and SSM.

---

## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/The%20Cloud%20Secure%20Mesh%20%E2%80%94%20Multi-VPC,%20Zero%E2%80%91Trust,%20Serverless%20Data%20Flow%20Architecture.png?raw=true)
---

# ✅ AWS Console Working Guide

## PHASE 1 — NETWORK FOUNDATION (VPCs & Subnets)

### **Create Three Fully Functional VPCs**

---

## **VPC 1 — Prod‑VPC**

* Open **AWS Console → VPC**  
* Click **Create VPC**  
* Select **VPC Only**  
* Name: `Prod-VPC`  
* IPv4 CIDR: `10.0.0.0/16`  
* Keep defaults → **Create VPC**  
* Confirm VPC appears

### **Add Subnets to Prod-VPC**  
* Go to **Subnets → Create subnet**  
* Select **Prod-VPC**  
* Create `Prod-private-1` → `10.0.1.0/24`  
* Create `Prod-private-2` → `10.0.2.0/24`  
* Disable public IPv4 auto-assign  

---

## **VPC 2 — Dev‑VPC**  
* Go to **VPC → Create VPC**  
*  Name: `Dev-VPC`  
*  IPv4: `10.1.0.0/16`  
*  Click **Create**  
*  Create `Dev-private-1 (10.1.1.0/24)`  
*  Create `Dev-private-2 (10.1.2.0/24)`  
*  Disable auto‑assign IPv4  

---

## **VPC 3 — Shared-Services-VPC**  
*  Create VPC  
*  Name: `Shared-Services-VPC`  
*  CIDR: `10.2.0.0/16`  
*  Create VPC  
*  Create `Shared-private-1 (10.2.1.0/24)`  
*  Create `Shared-private-2 (10.2.2.0/24)`  
*  Disable auto‑assign IPv4  
*  Confirm all subnets  

---

# PHASE 2 — TRANSIT GATEWAY (TGW)

## Create & Attach TGW

*  Go to **VPC → Transit Gateways**  
*  Create TGW  
*  Name: `Cloud-TGW`  
*  Enable DNS support  
*  Disable auto‑accept  
*  Create TGW  
*  Go to **Attachments → Create attachment**  
*  Attach **Prod-VPC** (select both subnets)  
*  Attach **Dev-VPC**  
*  Attach **Shared-Services-VPC**  

__Note: Wait for attachments to become *Available*__

*  Edit TGW route tables  
*  Allow Prod ↔ Shared and Dev ↔ Shared, deny Prod ↔ Dev  

## Step 2: Create TGW Attachments (Very Important)

**Do this 3 times:**

###### ✔ Attachment 1 — Prod-VPC

* Name: prod-attach

* VPC: Prod-VPC

* Subnets: choose 1 subnet from each AZ (private subnets recommended)

###### ✔ Attachment 2 — Dev-VPC

* Name: dev-attach

* VPC: Dev-VPC

* Subnets: private subnets

###### ✔ Attachment 3 — Shared-Services-VPC

* Name: shared-attach

* VPC: Shared-Services-VPC

* Subnets: private subnets

__Wait until all attachments show AVAILABLE.__

----

## Step 3: Update Private Route Tables (All VPCs)
###### For Prod VPC Private Route Table:

* Add route: All VPC

###### For Dev VPC Private Route Table:

* Add route: All VPC

###### For Shared-Services VPC Private Route Table:

* Add route: All VPC
---

# PHASE 3 — VPC ENDPOINTS

## Gateway & Interface Endpoints

### **Gateway Endpoints — S3 & DynamoDB**

*   Go to **Endpoints → Create endpoint**  
*   Select service: `com.amazonaws.<region>.s3`  
*   Type: **Gateway**  
*   Select **The location only where you want to create**  
*   Create endpoint  
*   Repeat for **DynamoDB**  

### **Interface Endpoints — Lambda, CloudWatch, CloudTrail, SSM, EC2 API, EventBridge**

* For each service:  
* Create endpoint  
* Select **Interface**  
* Select **Prod-VPC private subnets**  
* Enable **Private DNS**  

---

# PHASE 4 — S3 BUCKETS

## Create Secure Buckets

*   Go to S3 → Create bucket  
*   Name: `cloud-app-data`  
*   Block public access  
*   Enable versioning  
*   Enable encryption (SSE-S3)  
*   Create  

*   Create second bucket: `cloudtrail-logs`  
*   Block public access  
*   Enable versioning  
*   Add CloudTrail write policy  

- just need to replace bucket arn and account id 

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::<BUCKET-NAME>",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "<ACCOUNT-ID>"
        }
      }
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::<BUCKET-NAME>/AWSLogs/<ACCOUNT-ID>/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control",
          "aws:SourceAccount": "<ACCOUNT-ID>"
        }
      }
    }
  ]
}
```

*   Save  

---

# PHASE 5 — CLOUDTRAIL

## Configure Trail

*   Open CloudTrail → Create trail  
*   Name: `Cloud-OrgTrail`  
*   Select S3 bucket for logs  
*   Enable CloudWatch logs  
*   Create log group `/aws/cloudtrail/aws-logs`  
*   Auto-create IAM role  
*   Enable Insight events  
*   Enable management events  
*   Enable S3 data events  
*   Create trail  

---

# PHASE 6 — IAM POLICIES

## Create Policies

*  Create policy `S3-AppBucket-Access`  
*  Grant access ONLY to `cloud-app-data`  
*  Create policy 

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3AccessToAppBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::demo-test-s3-b",
        "arn:aws:s3:::demo-test-s3-b/*"
      ]
    }
  ]
}
```

__✅ Notes:__


> **ListBucket is required on the bucket itself.**
>> 
> **GetObject, PutObject, DeleteObject allow reading/writing objects.**
>> 
> **Restricts access only to your cloudmalangi-app-data bucket.**

*  Create DynamoDB policy  
*  Allow: PutItem / UpdateItem  
*  Restrict to table `AppEvents`  
*  Name: `DynamoDB-AppEventsWriter` 

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPutUpdateOnAppEvents",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:<REGION>:<ACCOUNT-ID>:table/AppEvents"
    }
  ]
}
```

__Notes:__

> **Replace <REGION> with your AWS region, e.g., us-east-1.**
>> 
> **Replace <ACCOUNT-ID> with your 12-digit AWS account ID.**
>> 
> **This policy only allows writing/updating items in the AppEvents table.**
>> 
> **It does NOT allow reading or deleting items (principle of least privilege).**

--- 

*  Create  

--- 

## The SINGLE IAM Policy You Need (CloudWatch Full Logging)


* Attach this policy to the IAM Role:

* cloud-cloudwatch-logging-policy

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "logs:DescribeLogGroups",
        "logs:PutRetentionPolicy",
        "logs:PutResourcePolicy",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}

```


**Note:** This gives FULL logging ability.

## 3. IAM Role (Trust Policy)

* For CloudWatch logging from multiple services, use this multi-service trust policy:

* cloud-cloudwatch-logging-role (Trust Policy)


```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "ec2.amazonaws.com",
          "lambda.amazonaws.com",
          "delivery.logs.amazonaws.com",
          "vpc-flow-logs.amazonaws.com",
          "transitgateway.amazonaws.com",
          "dynamodb.amazonaws.com",
          "s3.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

----

## Create IAM Role:

*  **Attach these IAM policies:**

    * S3-AppBucket-Access → allows Lambda to read/write in your S3 bucket

    * DynamoDB-AppEventsWriter → allows Lambda to write to AppEvents table

    * AWSLambdaBasicExecutionRole → allows Lambda to log to CloudWatch


----
# PHASE 7 — DYNAMODB

## Create Table

*  Open DynamoDB  
*  Create table: `AppEvents`  
*  PK: `EventID (String)`  
*  SK: `Timestamp (String)`  

---

# PHASE 8 — LAMBDA

## Lambda Setup

###  Create Lambda Function

*  Go to AWS Console → Lambda → Create function

*  Choose Author from scratch

* Function name: EventWriterLambda

* Runtime: Python 3.x (latest available)
---

###  Create Execution Role

* Under Permissions → Execution role → Create new role from AWS policy templates

* Role name: EventWriterLambdaRole


**Notes:** Do not select any templates (we will attach custom policies next)

---
###  Attach Policies to the Role

#### Attach these IAM policies:

* S3-AppBucket-Access → allows Lambda to read/write in your S3 bucket

* DynamoDB-AppEventsWriter → allows Lambda to write to AppEvents table

* AWSLambdaBasicExecutionRole → allows Lambda to log to CloudWatch

---
###  Configure Lambda Networking (VPC)

* Go to Configuration → VPC

* Select VPC: Prod-VPC

* Subnets → choose private subnets (both AZs)

* Security group → allow outbound to DynamoDB + S3 endpoints

* Outbound Rules (for general AWS access inside VPC): Type : All traffic , Protocol : All, Port Range: All, Destination : 0.0.0.0/0


**Note:** Lambda in private subnets needs VPC endpoints for S3/DynamoDB or NAT to access them.

---
###  Add Environment Variables

* Go to Configuration → Environment variables

* **Add key/value:**

    * **Key:** BUCKET_NAME
    * **Value:** cloud-app-data


**Note:*** You can reference this in Python code: os.environ['BUCKET_NAME']

###  Lambda Function Code

**Example** Python 3.x code that writes an item to DynamoDB and uploads a file to S3:

```
import os
import boto3
from datetime import datetime
import json

# Environment variables
S3_BUCKET = os.environ['BUCKET_NAME']
DYNAMO_TABLE = "AppEvents"

# Clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMO_TABLE)

def lambda_handler(event, context):
    # DynamoDB PutItem
    item = {
        'EventID': str(datetime.utcnow().timestamp()),
        'Timestamp': datetime.utcnow().isoformat(),
        'Message': 'Test Event'
    }
    table.put_item(Item=item)

    # S3 Upload
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"logs/event-{item['EventID']}.json",
        Body=json.dumps(item)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Event written to DynamoDB and uploaded to S3!')
    }

```

###  Test Lambda

* Go to Test → Configure test event

* Create a simple event (can be empty JSON: {})

* Click Test

* Verify CloudWatch logs → see Lambda execution logs

* Check S3 bucket → see the new file

* Check DynamoDB → AppEvents table → new item inserted

###  Validation

* Lambda is running in Prod-VPC private subnets

* Lambda writes to DynamoDB only via AppEventsWriter policy

* Lambda uploads to S3 bucket only via S3-AppBucket-Access policy

* CloudWatch logs show successful execution

---



---
# ✅ POST‑LAB VALIDATION CHECKLIST

## **1. Global Validation Tests**

### **1.1 VPC Connectivity**
Ping between VPCs via TGW.

### **1.2 Gateway Endpoint Test**
Access S3 without internet.

#### Test S3 Access

Run AWS CLI commands using your IAM role or keys attached to the EC2 instance:

#### List buckets:

```
aws s3 ls
```

__You should see your S3 buckets.__

#### Upload a file:

```
echo "Hello S3" > test.txt
```

```
aws s3 cp test.txt s3://cloudmalangi-app-data/test.txt
```

#### Download the file back:

```
aws s3 cp s3://cloudmalangi-app-data/test.txt downloaded.txt
```

```
cat downloaded.txt
```
---

### **1.3 Interface Endpoint Test**

```
Run `aws dynamodb list-tables`
```
---

## **2. S3 Validation**

Upload/download file  
Check CloudTrail logs

---

## **3. DynamoDB Validation**
Run put-item / get-item

---

## **4. Lambda Validation**
Invoke via CLI → confirm CloudWatch logs

---

## **5. IAM Validation**
Ensure IAM user has restricted access

---

## **6. CloudWatch & CloudTrail Tests**
Confirm API events + metrics

---

## **7. TGW Route Table Verification**

Ensure routes exist:

```
10.x.x.x/16 → Transit Gateway
```

---

## **8. Subnet IP Allocation**
AWS reserves:

| IP | Purpose |
|----|---------|
| .0 | Network |
| .1 | Router |
| .2 | AWS reserved |
| .3 | AWS reserved |
| .255 | Broadcast |

---

## **9. VPC Endpoint IP Verification**
Check ENIs using:

```
aws ec2 describe-network-interfaces --filters Name=interface-type,Values=interface-endpoint
```

---

## **10. NAT Gateway Test**
Only works if NAT GW exists.

---

# ✅ FINAL SUCCESS CHECKLIST

✔ VPCs communicate via TGW  
✔ S3 through gateway endpoints  
✔ DynamoDB/Lambda through interface endpoints  
✔ Lambda logs to CloudWatch  
✔ CloudTrail logs everything  
✔ IAM restrictions working  
✔ Subnet IP allocation verified  
✔ All ENIs have correct IPs  

---

**Your Cloud Secure Mesh lab is now 100% production‑ready.**
