# Advanced AWS Enterprise Hands-On Lab

> **Author:** AWS Cloud Trainer  
> **Level:** Advanced (Associate → Professional)  
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
- Type: Gateway Endpoint
- Service: S3
- Attach to private route table

---

## 8. RDS MySQL (Private)
- Engine: MySQL
- Instance: db.t3.micro
- Public access: No
- Subnet group: Private subnet
- SG: Allow 3306 only from private EC2

---

## 9. EC2 Instances
### 9.1 Public EC2 (Admin)
- Subnet: Public
- Elastic IP attached
- Used for administration

### 9.2 Private EC2 (Application)
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
```bash
sudo mkfs.xfs /dev/xvdf
sudo mkdir /data
sudo mount /dev/xvdf /data
```

### 12.3 Persistent Mount
Add to `/etc/fstab`:
```
/dev/xvdf /data xfs defaults,nofail 0 2
```

---

## 13. Linux User, Group & Permissions
### 13.1 Create Group
```bash
groupadd labgroup
```

### 13.2 Create User
```bash
useradd labuser
passwd labuser
```

### 13.3 Assign Directory Permissions
```bash
chgrp labgroup /data
chmod 2770 /data
```

### 13.4 Add User to Group
```bash
usermod -aG labgroup labuser
```

---

## 14. EFS Lab (Shared Storage)
### 14.1 Create EFS
- VPC: AdvancedLabVPC
- Mount target in private subnet
- SG: Allow NFS 2049 from EC2 SG

### 14.2 Mount EFS on EC2
```bash
sudo yum install -y amazon-efs-utils
sudo mkdir /efsdata
sudo mount -t efs -o tls fs-xxxx:/ /efsdata
```

### 14.3 Persistent Mount
```
fs-xxxx:/ /efsdata efs _netdev,tls 0 0
```

---

## 15. Lambda + EFS Automation (Scenario)
### Scenario
Lambda scans files written to EFS and logs metadata to CloudWatch.

### Steps
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

**END OF LAB**

