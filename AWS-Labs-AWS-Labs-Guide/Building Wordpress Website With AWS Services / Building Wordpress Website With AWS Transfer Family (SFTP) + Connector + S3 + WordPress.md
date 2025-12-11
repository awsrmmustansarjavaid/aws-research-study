## AWS Hands-on Lab Guide 

# AWS Wordpress Configuration Lab Guide (EC2 + S3 + WordPress + RDS & SFTP + AWSTransfer Family (SFTP) + Connector) Architecture

### Architecture Designer: Charlie

----
## ✅ AWS Architecture Method 2  —  AWS Transfer Family (SFTP) + Connector + S3 + WordPress
-----

### 1. Architecture Overview

```
SFTP Client → AWS Transfer Family (SFTP Server)
         → Transfer Family CONNECTOR (To S3)
         → Amazon S3 bucket (wp-content-store)
         → WordPress (EC2) using S3 Offload Plugin
```

#### 📌 You DO NOT use EC2 for SFTP

#### 📌 You DO NOT manage Linux users or passwords

#### 📌 You DO NOT need file-system permissions

##### Everything is offloaded using IAM + S3 + Transfer Family.

---

## 2. AWS Architecture Diagram

![WordPress on EC2 + RDS Diagram](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Guide/Building%20Wordpress%20Website%20With%20EC2%20&%20RDS/Building%20Wordpress%20Website%20With%20EC2%20&%20RDS.png?raw=true)

---

# 4. Step-by-Step WordPress Deployment

## 🟦 SECTION 1 — Create S3 Bucket for WordPress Files

### 1️⃣ Create S3 Bucket

#### Name example:

```
my-wp-media-bucket-123
```

### 2️⃣ Enable Bucket Options

#### Enable:

```
✔ Versioning
✔ Block Public Access (KEEP ON)
✔ Default encryption (SSE-S3 OK)
```

### 3️⃣ Create Folder Structure (Optional)

```
/uploads/
/themes/
/plugins/
```

---

## 🟦 SECTION 2 — Create IAM Role for Transfer Family (SFTP)

### 1️⃣ Create IAM Role

- **Go to IAM → Roles → Create Role**

#### Trusted entity:

```
Transfer
```

#### Attach policy (create custom):

##### 📌 IAM Policy to allow SFTP access to S3

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-wp-media-bucket-123",
                "arn:aws:s3:::my-wp-media-bucket-123/*"
            ]
        }
    ]
}
```

#### Name the role:

```
AWS-Transfer-SFTP-S3-Access
```

---

## 🟦 SECTION 3 — Configure AWS Transfer Family (SFTP Server)

### 1️⃣ Create AWS Transfer Family

- **Go to AWS Transfer Family → Create Server**

#### Choose:

```
✔ SFTP (NOT FTP/FTPS)
✔ Identity Provider: Service managed
✔ Publicly accessible
✔ Choose VPC and Subnets
✔ Logging (Optional but recommended — CloudWatch)
```

- **Create server.**

##### It will give you:

```
s-xxxxxxxxxxxx.server.transfer.us-east-1.amazonaws.com
```

---

## 🟦 SECTION 4 — Create SFTP User

### 1️⃣ Create Transfer Family User

- **Go to: Transfer Family → Server → USERS → Add User**

#### 1️⃣ Username:

```
wpfileadmin
```

#### 2️⃣ Role:

Select role created earlier:

```
AWS-Transfer-SFTP-S3-Access
```

#### 3️⃣ Home Directory:

```
/my-wp-media-bucket-123/uploads
```

#### 4️⃣ Add SSH Key:

- **✔  Paste user’s public key (.pub)**

- **✔ AWS Transfer DOES NOT support password login.**

- **✔ Only SSH keys.**

###### If you want password login → I can provide Lambda-based password auth.

---

## 🟦 SECTION 5 — Create AWS Transfer Family CONNECTOR

##### This is the MOST IMPORTANT part.

- **Go to: Transfer Family → Connectors → Create connector**

#### 1️⃣ Type:

```
S3
```

#### 2️⃣ S3 Bucket:


```
my-wp-media-bucket-123
```

#### 3️⃣ IAM role:

Create a new role if needed:

```
AWS-Transfer-S3ConnectorRole
```

##### Attach policy:

```
AmazonS3FullAccess
```

#### 4️⃣ Encryption (optional):

```
S3 Managed Keys (SSE-S3)
```


#### 5️⃣ Activation:

```
Enable the connector.
```

---

🟦 SECTION 6 — Link Connector to User

Now:

Transfer Family → Servers → Select your server → Users → Edit user → Add connector

Choose:

```
S3 connector (the connector you created)
```

This makes AWS Transfer route:

```
SFTP uploads → Connector → S3 bucket
```

---

🟦 SECTION 7 — Test SFTP Upload to S3

From any SFTP client:


