# Building a Secure Multi-VPC Mesh Using AWS Transit Gateway, Private Endpoints & Serverless Applications

A hands‑on lab that builds a multi-VPC production‑grade AWS environment using Transit Gateway, VPC endpoints, IAM policies, Lambda, DynamoDB, S3, CloudTrail, CloudWatch, AWS Config, and SSM.

---

## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/The%20Cloud%20Secure%20Mesh%20%E2%80%94%20Multi-VPC,%20Zero%E2%80%91Trust,%20Serverless%20Data%20Flow%20Architecture.png?raw=true)
---

# ✅ 100‑Step AWS Console Working Guide

## PHASE 1 — NETWORK FOUNDATION (VPCs & Subnets)

### **1–20: Create Three Fully Functional VPCs**

---

## **VPC 1 — Prod‑VPC (Steps 1–7)**

1. Open **AWS Console → VPC**  
2. Click **Create VPC**  
3. Select **VPC Only**  
4. Name: `Prod-VPC`  
5. IPv4 CIDR: `10.0.0.0/16`  
6. Keep defaults → **Create VPC**  
7. Confirm VPC appears

### **Add Subnets to Prod-VPC (Steps 8–12)**  
8. Go to **Subnets → Create subnet**  
9. Select **Prod-VPC**  
10. Create `Prod-private-1` → `10.0.1.0/24`  
11. Create `Prod-private-2` → `10.0.2.0/24`  
12. Disable public IPv4 auto-assign  

---

## **VPC 2 — Dev‑VPC (Steps 13–19)**  
13. Go to **VPC → Create VPC**  
14. Name: `Dev-VPC`  
15. IPv4: `10.1.0.0/16`  
16. Click **Create**  
17. Create `Dev-private-1 (10.1.1.0/24)`  
18. Create `Dev-private-2 (10.1.2.0/24)`  
19. Disable auto‑assign IPv4  

---

## **VPC 3 — Shared-Services-VPC (Steps 20–27)**  
20. Create VPC  
21. Name: `Shared-Services-VPC`  
22. CIDR: `10.2.0.0/16`  
23. Create VPC  
24. Create `Shared-private-1 (10.2.1.0/24)`  
25. Create `Shared-private-2 (10.2.2.0/24)`  
26. Disable auto‑assign IPv4  
27. Confirm all subnets  

---

# PHASE 2 — TRANSIT GATEWAY (TGW)

## Steps 28–40: Create & Attach TGW

28. Go to **VPC → Transit Gateways**  
29. Create TGW  
30. Name: `CloudMalangi-TGW`  
31. Enable DNS support  
32. Disable auto‑accept  
33. Create TGW  
34. Go to **Attachments → Create attachment**  
35. Attach **Prod-VPC** (select both subnets)  
36. Attach **Dev-VPC**  
37. Attach **Shared-Services-VPC**  
38. Wait for attachments to become *Available*  
39. Edit TGW route tables  
40. Allow Prod ↔ Shared and Dev ↔ Shared, deny Prod ↔ Dev  

---

# PHASE 3 — VPC ENDPOINTS

## Steps 41–55: Gateway & Interface Endpoints

### **Gateway Endpoints — S3 & DynamoDB**

41. Go to **Endpoints → Create endpoint**  
42. Select service: `com.amazonaws.<region>.s3`  
43. Type: **Gateway**  
44. Select **ALL VPCs + ALL private subnets**  
45. Create endpoint  
46. Repeat for **DynamoDB**  

### **Interface Endpoints — Lambda, CloudWatch, CloudTrail, SSM, EC2 API, EventBridge**

47–55. For each service:  
- Create endpoint  
- Select **Interface**  
- Select **Prod-VPC private subnets**  
- Enable **Private DNS**  

---

# PHASE 4 — S3 BUCKETS

## Steps 60–70: Create Secure Buckets

60. Go to S3 → Create bucket  
61. Name: `cloudmalangi-app-data`  
62. Block public access  
63. Enable versioning  
64. Enable encryption (SSE-S3)  
65. Create  

66. Create second bucket: `cloudmalangi-cloudtrail-logs`  
67. Block public access  
68. Enable versioning  
69. Add CloudTrail write policy  
70. Save  

---

# PHASE 5 — CLOUDTRAIL

## Steps 71–80: Configure Trail

71. Open CloudTrail → Create trail  
72. Name: `CloudMalangi-OrgTrail`  
73. Select S3 bucket for logs  
74. Enable CloudWatch logs  
75. Create log group `/aws/cloudtrail/malangi`  
76. Auto-create IAM role  
77. Enable Insight events  
78. Enable management events  
79. Enable S3 data events  
80. Create trail  

---

# PHASE 6 — IAM POLICIES

## Steps 81–88: Create Policies

81. Create policy `S3-AppBucket-Access`  
82. Grant access ONLY to `cloudmalangi-app-data`  
83. Create policy  
84. Create DynamoDB policy  
85. Allow: PutItem / UpdateItem  
86. Restrict to table `AppEvents`  
87. Name: `DynamoDB-AppEventsWriter`  
88. Create  

---

# PHASE 7 — DYNAMODB

## Steps 89–92: Create Table

89. Open DynamoDB  
90. Create table: `AppEvents`  
91. PK: `EventID (String)`  
92. SK: `Timestamp (String)`  

---

# PHASE 8 — LAMBDA

## Steps 93–100: Lambda Setup

93. Create function: Python 3.x  
94. Name: `EventWriterLambda`  
95. Execution role → create new  
96. Attach policies:  
   - S3-AppBucket-Access  
   - DynamoDB-AppEventsWriter  
   - AWSLambdaBasicExecutionRole  
97. Configure VPC: Prod-VPC private subnets  
98. Add environment variable (S3 bucket name)  
99. Add DynamoDB put-item logic  
100. Test Lambda (writes to DynamoDB + uploads to S3)  

---

# ✅ POST‑LAB VALIDATION CHECKLIST

## **1. Global Validation Tests**

### **1.1 VPC Connectivity**
Ping between VPCs via TGW.

### **1.2 Gateway Endpoint Test**
Access S3 without internet.

### **1.3 Interface Endpoint Test**
Run `aws dynamodb list-tables`

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

**Your CloudMalangi Secure Mesh lab is now 100% production‑ready.**
