
# 🧠 AWS RDS Cross-Region Read Replica Lab (Private Setup with VPC Peering & NAT)

**Author:** IT Charlie  
**Date:** November 2025  
**Purpose:** Hands-on lab to build and understand AWS RDS cross-region replication in a private environment using VPC Peering and NAT Gateways.  
**Focus Areas:** AWS RDS, VPC Peering, Subnet Groups, NAT Gateways, Private Networking, Replication  

---

## 🧩 1. Prerequisites
- AWS account with admin permissions (RDS, VPC, EC2, NAT, Peering)
- Two AWS regions selected (e.g., `us-east-1` → `us-west-2`)
- VPCs created in both regions with **at least 2 private subnets each**
- **NAT Gateways** deployed in both regions for outbound internet access (required for private RDS)
- **Inter-region VPC Peering** connection established
- Security Groups configured to allow traffic on RDS ports (3306 for MySQL / 5432 for PostgreSQL)

---

## 🌐 2. Network Setup

### **Region A (Primary)**
- **VPC CIDR:** `10.0.0.0/16`  
- **Private Subnets:**
  - `10.0.1.0/24` (AZ1)
  - `10.0.2.0/24` (AZ2)
- **NAT Gateway:** In a public subnet for outbound access  
- **RDS Subnet Group:** Includes both private subnets  
- **Security Group:** Allow inbound DB port from Region B’s CIDR  

### **Region B (Replica)**
- **VPC CIDR:** `10.1.0.0/16`  
- **Private Subnets:**
  - `10.1.1.0/24` (AZ1)
  - `10.1.2.0/24` (AZ2)
- **NAT Gateway:** In a public subnet for outbound access  
- **RDS Subnet Group:** Includes both private subnets  
- **Security Group:** Allow inbound DB port from Region A’s CIDR  

### **VPC Peering**
- Establish **inter-region peering** between Region A and Region B VPCs.  
- Update both VPCs’ private route tables to allow traffic to the opposite VPC’s CIDR range.

---

## 🛠️ 3. Create Primary RDS (Region A)
- Navigate to **RDS Console → Create Database**
- **Engine:** MySQL or PostgreSQL  
- **Deployment:** Single-AZ (Multi-AZ optional)  
- **Instance Type:** `db.t3.micro`  
- **Storage:** 20 GB  
- **Subnet Group:** `PrimarySubnetGroup` (private subnets)  
- **Security Group:** Allow inbound from Region B CIDR  
- **Automatic Backups:** ✅ Enabled (required for replication)  
- **Public Access:** ❌ Disabled (private only)  
- **Save credentials** (endpoint, username, password)

---

## 🔁 4. Create Cross-Region Read Replica (Region B)
- In the RDS console, select the **primary DB instance**  
- Choose **Actions → Create Read Replica**
- **Destination Region:** Region B  
- **Instance Identifier:** `read-replica-us-west-2`  
- **Instance Type:** `db.t3.micro`  
- **Subnet Group:** `ReplicaSubnetGroup` (private subnets)  
- **Security Group:** Allow inbound from Region A CIDR  
- **Public Access:** ❌ Disabled  
- Launch and wait until status = **Available**

---

## 🧪 5. Verify Replication
- Connect to the **read replica** using its private endpoint.  
- Run **read-only queries** — data should match the primary DB.  
- Insert new data into **primary DB** and verify replication on the replica.  
- Monitor replication lag in **CloudWatch Metrics**.

---

## ⚙️ 6. Optional Enhancements
- Enable **Multi-AZ** for primary RDS for HA.  
- Set up **replication monitoring** with CloudWatch and SNS alerts.  
- Simulate failover by promoting the read replica.  
- Test cross-region connectivity with EC2 instances in private subnets.  

---

## 📊 7. Subnet & Routing Summary

| Region | VPC CIDR | Private Subnet 1 | Private Subnet 2 | RDS Subnet Group | Notes |
|--------|-----------|------------------|------------------|------------------|--------|
| A (Primary) | 10.0.0.0/16 | 10.0.1.0/24 | 10.0.2.0/24 | PrimarySubnetGroup | Primary RDS, NAT Gateway, Peered |
| B (Replica) | 10.1.0.0/16 | 10.1.1.0/24 | 10.1.2.0/24 | ReplicaSubnetGroup | Read Replica, NAT Gateway, Peered |

✅ Each region requires **at least 2 private subnets**.  
✅ NAT Gateways enable replication for private RDS instances.  
✅ Security groups and routing must allow **cross-region private traffic**.

---

## 🧠 Key Takeaways
- Deep understanding of **cross-region RDS replication** setup and security.  
- Practical knowledge of **private network design** and **inter-region communication**.  
- Improved AWS skills in **VPC, Subnetting, NAT, Peering, and RDS configurations**.  
- Real-world exposure to **disaster recovery and high availability** architectures.  

---

**💡 Pro Tip:** Practicing labs like this enhances real-world confidence and demonstrates **hands-on AWS skills** — a must for anyone pursuing Cloud, DevOps, or Solutions Architect roles.

---
