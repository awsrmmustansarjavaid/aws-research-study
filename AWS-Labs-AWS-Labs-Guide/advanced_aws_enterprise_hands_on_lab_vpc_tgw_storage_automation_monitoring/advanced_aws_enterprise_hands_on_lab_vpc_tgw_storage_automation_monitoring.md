# Advanced AWS Enterprise Hands-On Lab

> **Author:** Charlie
> 
> **Level:** Advanced (Associate → Professional)
>  
> **Purpose:** End‑to‑end enterprise AWS hands‑on lab covering networking, storage, automation, monitoring, and Linux administration.

---

## 1. Lab Scenario (Real‑World Context)
You are a cloud engineer designing a **secure, scalable, enterprise‑grade AWS architecture** similar to an on‑premises environment.  
The environment must support:
- Multi‑VPC connectivity
- Centralized routing (Transit Gateway)
- Private storage access
- Shared and non‑shared storage
- Linux user and permission management
- Automation using Lambda
- Monitoring using CloudWatch

No Active Directory or domain services are required.

---

## 2. Services Used
- Amazon VPC
- Transit Gateway (TGW)
- NAT Gateway
- VPC Endpoints (S3)
- EC2 (Public & Private)
- Elastic IP (EIP)
- Elastic Network Interface (ENI)
- EBS
- EFS
- S3
- RDS (MySQL)
- IAM Roles
- CloudWatch
- CloudTrail
- AWS Lambda

---

## 3. Network Architecture Overview
- VPC‑1 (Admin / Public access)
- VPC‑2 (Private application resources)
- Transit Gateway connects VPC‑1 and VPC‑2
- Private subnets use NAT Gateway for internet access
- S3 accessed privately via VPC Endpoint


# 🎓 AWS Architecture Diagram

![Advanced AWS Enterprise Hands-On Lab Diagram](https://raw.githubusercontent.com/awsrmmustansarjavaid/aws-research-study/refs/heads/main/AWS-Labs-AWS-Labs-Guide/advanced_aws_enterprise_hands_on_lab_vpc_tgw_storage_automation_monitoring/advanced_aws_enterprise_hands_on_lab_vpc_tgw_storage_automation_monitoring.png)

---

## 4. Create VPC and Subnets
### 4.1 Create VPC
- Name: `AdvancedLabVPC`
- CIDR: `10.10.0.0/16`

### 4.2 Create Subnets
- Public Subnet: `10.10.1.0/24`
- Private Subnet: `10.10.2.0/24`

Enable auto‑assign public IP **only** on the public subnet.

---

## 5. Internet Gateway and NAT Gateway
### 5.1 Internet Gateway
- Create IGW and attach to VPC

### 5.2 NAT Gateway
- Create NAT in public subnet
- Name: advancedlab-secure-NATGW
- Allocate Elastic IP

### 5.3 Route Tables
- Public RT → `0.0.0.0/0` → IGW
- Private RT → `0.0.0.0/0` → NAT

---

## 6. Transit Gateway Configuration
### 6.1 Create Transit Gateway
- Name: `AdvancedLab-TGW`
- ASN: 64512

### 6.2 Attach VPCs
- Attach VPC‑1 and VPC‑2 to TGW
- Enable route propagation

### 6.3 Update Route Tables
- Add routes pointing remote VPC CIDRs to TGW

---

## 7. S3 Bucket with VPC Endpoint
### 7.1 Create S3 Bucket
- Name: `advancedlab-secure-bucket`
- Block all public access

### 7.2 Create VPC Endpoint
- Name : advancedlab-secure-GWEP
- Type: Gateway Endpoint
- Service: S3
- Attach to private route table

---

## 8. RDS MySQL (Private)
- DB instance identifier Name: advancedlab-secure-RDS
- User: admin
- Password: admin123
- Engine: MySQL
- Instance: db.t3.micro
- Public access: No
- Subnet group: Private subnet
- SG: Allow 3306 only from private EC2

### Install and Configure MariaDB (MySQL)

```
sudo dnf install mariadb105-server mariadb105 -y
```

#### Confirm versions:

```
mysql --version
```

### Connect to RDS:

```
mysql -h <RDS-ENDPOINT> -u <username> -p
```

### Create DB + User:

```
CREATE DATABASE wordpress;
```
```
CREATE USER 'wordpressuser'@'%' IDENTIFIED BY 'StrongPassword123!';
```
```
GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpressuser'@'%';
```
```
FLUSH PRIVILEGES;
```

```
USE wordpress;
```

```
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  price DECIMAL(10,2),
  description TEXT
);
```

```
INSERT INTO products (name, price, description) VALUES
 ('Laptop', 1200.00, 'Good laptop'),
 ('Phone', 800.00, 'Smartphone');

INSERT INTO products (name, price, description) VALUES
 ('PC', 30000, 'Good PC'),
 ('Samsung', 8000.00, 'Smartphone');

INSERT INTO products (name, price, description) VALUES
 ('Gaming PC', 6000.00, 'Good Gaming PC'),
 ('IPhone', 8700.00, 'Smartphone');

INSERT INTO products (name, price, description) VALUES
 ('Smart LED', 5400.00, 'A1 LED'),
 ('LCD', 700.00, 'LCD');

INSERT INTO products (name, price, description) VALUES
 ('Mouse', 600, 'Branded Mouse'),
 ('Headpne', 8700, 'Headphone');
 ```

 ```
 SHOW TABLES;
 ```

 ```
 SELECT * FROM products;
 ```


```
exit
```

---

## 9. EC2 Instances
### 9.1 Public EC2 (Admin)
- Name: advancedlab-secure-pub-ec
- Subnet: Public
- Elastic IP attached
- Used for administration

### 9.2 Private EC2 (Application)
- Name: advancedlab-secure-pvt-ec
- Subnet: Private
- Access via Bastion or SSM

---

## 10. Elastic IP (EIP) Lab
- Allocate EIP
- Associate with Public EC2
- Verify SSH using static IP

---

## 11. Elastic Network Interface (ENI) Lab
### 11.1 Create ENI
- Subnet: Private
- SG: PrivateEC2-SG

### 11.2 Attach ENI
- Attach as secondary interface

### 11.3 Verify
```bash
ip a
```

### 11.4 Detach and Reattach (Failover Concept)

---

## 12. EBS Lab (Block Storage)
### 12.1 Create & Attach EBS
- Size: 10 GiB
- Attach to Public EC2

### 12.2 Format and Mount

#### Create File System

```
sudo mkfs -t xfs /dev/xvdf
```

#### Create Directory to Mount Volume

```
sudo mkdir /data
```

#### Mount the Volume

```
sudo mount /dev/xvdf /data
```

### 12.3 Persistent Mount

#### Edit /etc/fstab:

```
sudo nano /etc/fstab
```

Add this line:

```
/dev/xvdf /data xfs defaults,nofail 0 2
```

#### Save & exit, then test:

```
sudo mount -a
```


```
lsblk
```




---

## 13. Linux User, Group & Permissions
### 13.1 Create Group
```
sudo groupadd labgroup
```

### 13.2 Create User
```
sudo useradd labuser
```
#### Set password:

```
sudo passwd labuser
```



### 13.3 Assign Directory Permissions

###### We will assign ownership of the /data directory to the group.

#### Change Group Ownership of Directory

```
sudo chgrp labgroup /data
```

#### Give the Group Permissions

##### Give read/write/execute:

```
sudo chmod 770 /data
```

##### OR if you want group to have elevated (root-like) privileges on this directory specifically:

##### Give setgid bit so new files belong to the group:

```
sudo chmod 2770 /data
```




### 13.4 Add User to Group

```
sudo usermod -aG labgroup labuser
```

#### Verify:

```
id labuser
```

###### You should see: labgroup in the groups list.

### 13.5 Test Permissions

#### Switch to the user:

```
su - labuser
```

##### Try writing into the directory:

```
touch /data/testfile.txt
```

```
ls -l /data
```

**🏆 If permissions are correct → success.**


---

## 14. EFS Lab (Shared Storage)

### 14.1 Create EFS
- **Go to Amazon EFS → Create File System**
- Name: AdvancedLabEFS
- VPC: AdvancedLabVPC
- Mount target in private subnet
- SG: Allow NFS 2049 from EC2 SG

##### Click Customize (important)

### 14.2 Choose Network Settings:

#### Availability Zones:

- **Select AZs where your private EC2 instance exists**

#### Add mount targets:

- **Subnet: Private Subnet (e.g., 10.10.2.0/24)**

- **Security Group: Create new → EFS-SG**

```
Allow inbound NFS (2049) from EC2 SG
```

##### Click Create File System

#### Configure EFS Security Group

##### EFS-SG (Inbound rules):

- **Type:** NFS

- **Port:** 2049

- **Source:** EC2 instance Security Group (e.g., PrivateEC2-SG)

##### PrivateEC2-SG (Outbound rules):

- **Allow outbound to EFS-SG on port 2049**

✔ This ensures only private EC2 instances can mount the EFS.



### 14.3 Mount EFS on EC2

#### Install NFS Utilities on Private EC2

##### SSH into the private EC2 instance through your bastion or SSM session manager:

```
sudo yum install -y amazon-efs-utils
```

#### Create a Mount Directory for EFS

```
sudo mkdir /<filename>
```

**Example:**

```
sudo mkdir /efsdata
```

##### Verify:

```
ls -ld /<filename>
```

**Example:**

```
ls -ld /efsdata
```



#### Mount EFS on EC2

- **Go to : EFS → Your File System → Attach**

###### You’ll find your EFS mount command in the AWS console under Access Points → EC2 mount instructions.

##### Copy the command like this:

**Example:**

##### Mount EFS using DNS



```
sudo mount -t efs -o tls fs-12345678:/ /efsdata
```
or 

##### Mount EFS using IP

```
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport 10.0.3.127:/ efsdata
```

##### If this works, test:

```
df -h | grep efsdata
```

**🎉 EFS is mounted**

**✅ This uses:**

- **✔ DNS**

- **✔ TLS encryption**

- **✔ AZ-aware mount targets**

#### Verify Mount

```
df -h
```

##### You should see:

```
fs-xxxxxxxx:/  →  /efs
```

#### Test write:

```
sudo touch /efsdata/testfile.txt
```

#### Verify 

```
ls -l /efsdata
```


#### 🔒 Why Private EC2 Can Mount EFS (No Internet Needed)

##### EFS is VPC-internal:

```
Private EC2 ───► EFS Mount Target (ENI)
```

- **✔ No NAT**
- **✔ No IGW**
- **✔ No Internet**
- **✔ Uses private IP only**

###### So your design is 100% correct.




**📣 Replace fs-12345678 with your actual file system ID.**

### 14.3 Make EFS Persistent (Automatic Mounting)

#### Edit the fstab file:

```
sudo nano /etc/fstab
```

#### Edit the fstab file:

Add this line:

```
fs-12345678:/ /efsdata efs _netdev,tls 0 0
```

Save & exit.

Test it:

```
sudo mount -a
```

### 14.4 Test EFS Shared Storage

#### On EC2 instance:

```
sudo touch /efsdata/app-file.txt
```

```
ls -l /efsdata
```


**🕛 If you mount EFS on multiple EC2 instances later, all will see the same file.**

---

## 15. Lambda + EFS Automation (Scenario)

### Scenario
Lambda scans files written to EFS and logs metadata to CloudWatch.

### 15.1 Create IAM Role 
- **Name:** AWSLambdaVPCAccessExecutionRole

- **Service:** Lambda

##### Trust relationship (must be EXACT)

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### Attach IAM Policies with IAM role 

##### Mandatory Managed Policies:

```
✔ AWSLambdaVPCAccessExecutionRole
✔ AWSLambdaBasicExecutionRole
✔ Custom Inline Policy
```

##### Custom Inline Policy (EFS Access – REQUIRED)

**Managed policies do NOT cover EFS access. You must add a custom inline policy.**

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEFSMount",
      "Effect": "Allow",
      "Action": [
        "elasticfilesystem:ClientMount",
        "elasticfilesystem:ClientWrite",
        "elasticfilesystem:ClientRootAccess"
      ],
      "Resource": "*"
    }
  ]
}
```

**👉 This allows Lambda to:**

- **✔ Mount EFS**

- **✔ Write to EFS**

- **✔ Use EFS access points**

##### 💡 In production, you should restrict Resource to:

```
arn:aws:elasticfilesystem:region:account-id:file-system/fs-xxxx
```

### 15.2 VPC Configuration for Lambda (VERY IMPORTANT)


- **Subnets:** Choose PRIVATE subnets

###### Must be in same AZs as EFS mount targets

#### Security Group (Lambda SG): 

- **Inbound:** NONE

- **Outbound:** TCP 2049 → EFS Security Group

### 15.3 EFS Configuration (Required for Lambda)

##### EFS must have:

- **Mount target in each AZ used by Lambda**

- **Security group allowing NFS**

- **EFS Security Group – Inbound :**

```
Type: NFS
Port: 2049
Source: Lambda Security Group
```

### 15.4 EFS Access Point (BEST PRACTICE)

- **Create Access Point**

- **Path:** /lambda

- **POSIX user:**

```
UID: 1000

GID: 1000

```

- **Root directory permissions:**

```
Owner UID: 1000
Owner GID: 1000
Permissions: 750
```

**This avoids permission issues.**

### 15.5 Create Lambda Function

- Name: advancedlab-secure-Lambda
- Create Lambda inside VPC
- Attach EFS access point


### 15.6 Attach EFS to Lambda (THIS STEP IS OFTEN MISSED)

- **In Lambda → Configuration → File system**

- **File system:** AdvancedLabEFS

- **Access point:** fsap-xxxx

- **Local mount path:**

```
/mnt/efs
```

**✔ Lambda automatically mounts EFS here.**

### 15.7 Lambda Code Example (Validation Test)

**✔ Use this to prove everything works.**

#### Python code

```
import os

def lambda_handler(event, context):
    path = "/mnt/efs/lambda-test.txt"

    with open(path, "a") as f:
        f.write("Lambda wrote to EFS successfully\n")

    files = os.listdir("/mnt/efs")

    return {
        "statusCode": 200,
        "message": "EFS write successful",
        "files": files
    }
```

### 15.8 Test & Validate (DO NOT SKIP)

#### Invoke Lambda

- **Test event → empty JSON {}**


- **Check CloudWatch Logs**

##### You should see:

**✔ No permission errors**

**✔ No mount errors**

#### Verify from EC2

##### On EC2 (mounted EFS):

```
cat /efs/lambda-test.txt
```

**✔ If file exists → Lambda ↔ EFS integration is SUCCESSFUL**

---

## 16. CloudWatch Monitoring
### Resources Monitored
- EC2 (CPU, Disk)
- RDS
- NAT Gateway
- Lambda
- S3

### Alarms
- CPU > 70%
- RDS storage < 20%

---

## 17. Transit Gateway Metrics Lab
### 17.1 Enable TGW Flow Logs
- Destination: CloudWatch Logs

### 17.2 View Metrics
- BytesIn
- BytesOut
- PacketsDropCount

### 17.3 Create Alarm
- BytesIn > 10 MB

---

## 18. Cross‑VPC SMB File Sharing (Important Concept)
### Key Rule
❌ EBS cannot be shared directly

### Working Method
```
EBS → EC2 → SMB → TGW → Another VPC EC2
```

### SMB Setup (Linux)
```bash
yum install -y samba
systemctl enable smb --now
```

`smb.conf`:
```
[ebsshare]
path = /data
read only = no
```

---

## 19. Security Best Practices
- Least‑privilege IAM roles
- SG‑to‑SG rules
- NACL hardening
- CloudTrail enabled
- S3 access only via VPC Endpoint

---

## 20. Final Outcome
You now understand and implemented:
- Enterprise AWS networking
- TGW routing & monitoring
- EBS vs EFS
- Linux permissions
- ENI & EIP
- Lambda automation
- Cross‑VPC file access (without AD)

---

## 21. Recommended Next Steps
- Convert to Terraform
- Add Auto Scaling
- Replace SMB with EFS or FSx
- Add AWS Backup

---

#### END OF LAB

---

# 🛠️ Troubleshooting 

## EFS

### 🔵 How to Verify amazon-efs-utils Is Installed (Before Mounting)

####  1. Check if the Package Is Installed (RPM level)

```
rpm -qa | grep amazon-efs-utils
```

##### Expected output (example):

```
amazon-efs-utils-1.39-1.amzn2023.noarch
```

✔ This confirms the package is installed.


####  2. Check the EFS Mount Helper Exists (MOST IMPORTANT)

```
which mount.efs
```
##### Expected output:

```
/usr/bin/mount.efs
```

✔ This confirms the EFS mount helper is available.

If this command returns nothing, the install did not succeed.



####  3. Check Version of amazon-efs-utils

```
mount.efs --version
```

or:

```
amazon-efs-utils --version
```

✔ Confirms the tool is working.


####  4. Verify Required NFS Utilities Are Present

EFS uses NFS under the hood.

```
which mount.nfs4
```

##### Expected:

```
/usr/sbin/mount.nfs4
```

✔ Required for EFS mounting.

####  5. Confirm Package Files Are Installed

(Optional but useful)

```
rpm -ql amazon-efs-utils
```

##### You should see files like:

```
/usr/bin/mount.efs
/etc/amazon/efs/efs-utils.conf
```

####  6. Check TLS Support (Used by -o tls)

EFS with TLS uses stunnel.

```
which stunnel
```

or:

```
rpm -qa | grep stunnel
```

✔ If installed, TLS mounting will work.


####  🧪 Quick Pre-Mount Readiness Test

##### Before mounting, run these commands in order:

```
sudo mkdir -p /efs
which mount.efs
mount.efs --version
```

✔ If all return valid outputs → you are ready to mount.


####  🚨 If Something Is Missing

##### Reinstall safely:

```
sudo yum remove -y amazon-efs-utils
sudo yum clean all
sudo yum install -y amazon-efs-utils
```







----

# 🎉 All New Tasks Successfully Integrated Into the Main Lab

## You now have:



### EC2 + EBS + User/Group Permission Management

- **✔ Public EC2 with attached EBS**

- **✔ Mounted and persistent file system**

- **✔ New Linux user & group**

- **✔ Group-level permission control**

- **✔ User added to the group**

- **✔ Full integration with the main AWS architecture**



