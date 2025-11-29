# 🚀 AWS Hands-on Lab: RDS Read Replica Across Availability Zones (Multi-AZ Replication)

## 🧠 Lab Objective
Create an **RDS Read Replica** in a different **Availability Zone (AZ)** to learn how to:
- Improve **read performance** by offloading queries.
- Increase **availability** and **fault tolerance**.
- Understand **replication mechanisms** within AWS RDS.

---

## 🧩 Architecture Overview

**Components:**
- 1 VPC with 2 Public + 2 Private Subnets (across AZs)
- 1 RDS Primary (Writer) Instance in **AZ-A**
- 1 RDS Read Replica (Reader) Instance in **AZ-B**
- 1 Bastion Host (EC2) in Public Subnet for access
- Security Groups configured for controlled access

**Topology:**
```
                +---------------------------+
                |        AWS Cloud          |
                |        (1 VPC)            |
                +---------------------------+
                    |                 |
               (AZ-A)             (AZ-B)
            +----------+       +----------+
            |  RDS     |       |  RDS     |
            | Primary  | --->  | Read     |
            | (Writer) |       | Replica  |
            +----------+       +----------+
                   ↑                ↑
                   |                |
             +---------------------------+
             | EC2 Bastion Host (SSH)   |
             | MySQL/Aurora Client Tool |
             +---------------------------+
```

---

## ⚙️ Step-by-Step Lab Guide

### Step 1: Create a Custom VPC
1. Go to **VPC Console → Create VPC**  
   - VPC name: `rds-replica-lab-vpc`  
   - CIDR: `10.0.0.0/16`  
   - Create 4 subnets:  
     - Public Subnet A (10.0.1.0/24, AZ-a)  
     - Public Subnet B (10.0.2.0/24, AZ-b)  
     - Private Subnet A (10.0.3.0/24, AZ-a)  
     - Private Subnet B (10.0.4.0/24, AZ-b)
2. Attach **Internet Gateway**
3. Create **Route Tables**
   - Public route → IGW
   - Private route → no IGW

---

### Step 2: Launch Bastion Host (EC2)
- Launch Amazon Linux 2 instance in **Public Subnet A**
- Allow SSH (port 22) from your IP only
- Attach IAM Role: `AmazonRDSFullAccess`
- Connect using EC2 Instance Connect or SSH

---

### Step 3: Create RDS Primary Instance
1. Go to **RDS → Create Database**
2. Choose engine: **MySQL** (or PostgreSQL)
3. Choose **Standard Create**
4. Deployment Option: **Single DB instance**
5. DB instance identifier: `rds-primary`
6. Credentials:
   - Username: `admin`
   - Password: (your password)
7. DB Instance Class: `db.t3.micro`
8. Storage: 20GB (gp2)
9. Availability Zone: `us-east-1a`
10. VPC: `rds-replica-lab-vpc`
11. Subnet group: private subnets only
12. Public access: **No**
13. Security group: allow MySQL (3306) from Bastion Host SG
14. Click **Create Database**

---

### Step 4: Create Read Replica
1. Select the primary DB instance (`rds-primary`)
2. Actions → **Create read replica**
3. DB instance identifier: `rds-read-replica`
4. Availability Zone: `us-east-1b`
5. Instance class: `db.t3.micro`
6. Enable “Auto minor version upgrade”
7. Click **Create read replica**

---

### Step 5: Verify Replication
1. Go to **RDS → Databases**
   - Primary = “Source DB”
   - Read Replica = “Read Replica”
2. Connect via EC2 Bastion:
   ```bash
   mysql -h <primary-endpoint> -u admin -p
   ```
3. Create test DB and table:
   ```sql
   CREATE DATABASE testdb;
   USE testdb;
   CREATE TABLE demo (id INT, name VARCHAR(20));
   INSERT INTO demo VALUES (1, 'Charlie');
   ```
4. Connect to the Read Replica:
   ```bash
   mysql -h <replica-endpoint> -u admin -p
   SHOW DATABASES;
   USE testdb;
   SELECT * FROM demo;
   ```

✅ You should see the same data replicated.

---

### Step 6: Test Read Scalability
Run multiple read queries on the replica:
```sql
SELECT * FROM demo;
```
Replica offloads read traffic, reducing load on the primary DB.

---

### Step 7: (Optional) Promote Replica
- Go to RDS → Read Replica → **Actions → Promote read replica**
- It becomes a standalone writable DB instance.

---

## 🎯 Learning Outcomes
- Configure RDS in Multi-AZ architecture  
- Understand asynchronous replication  
- Learn how to promote a replica for failover  
- Practice DB connectivity via Bastion Host  
- Experience real-world scalability architecture
