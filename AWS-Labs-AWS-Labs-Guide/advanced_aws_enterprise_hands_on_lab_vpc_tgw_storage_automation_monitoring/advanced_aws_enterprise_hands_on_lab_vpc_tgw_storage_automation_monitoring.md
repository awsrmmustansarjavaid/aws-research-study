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
mysql -h <RDS-ENDPOINT> -u wpadmin -p
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
sudo mkdir /efsdata
```

#### Mount EFS on EC2

###### You’ll find your EFS mount command in the AWS console under Access Points → EC2 mount instructions.

**Example:**

```
sudo mount -t efs -o tls fs-12345678:/ /efsdata
```

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

### Steps
- Name: - Name: advancedlab-secure-Lambda
- Create Lambda inside VPC
- Attach EFS access point
- Assign IAM role with:
  - AWSLambdaVPCAccessExecutionRole

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

# 🎉 All New Tasks Successfully Integrated Into the Main Lab

## You now have:



### EC2 + EBS + User/Group Permission Management

- **✔ Public EC2 with attached EBS**

- **✔ Mounted and persistent file system**

- **✔ New Linux user & group**

- **✔ Group-level permission control**

- **✔ User added to the group**

- **✔ Full integration with the main AWS architecture**



