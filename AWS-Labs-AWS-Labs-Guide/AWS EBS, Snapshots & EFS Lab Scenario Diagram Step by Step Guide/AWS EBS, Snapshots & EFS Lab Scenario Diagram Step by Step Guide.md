# AWS EBS, Snapshots & EFS – Lab Scenario + Diagram + Step-by-Step Guide

---

## *1. Lab Scenario Overview*

You will create:

* *One EC2 instance* using *EBS volume*
* Create *Snapshot* of that EBS volume
* Restore Snapshot → Create new EBS volume
* Attach restored volume to EC2
* Configure *EFS*
* Mount EFS to EC2 instance
* Test file sharing (for EFS)

---

## *2. Architecture Diagram (Simple Text Diagram)*


                   +---------------------------+
                   |         AWS VPC           |
                   |---------------------------|
                   |                           |
     +-------------+-------------+   +----------------------+
     |     EC2 Instance          |   |       EFS            |
     |  (Amazon Linux / Ubuntu)  |   |  (Shared File System) |
     |---------------------------|   +----------+-----------+
     |  Root EBS Volume (8GB)    |              |
     |  Extra EBS Volume (5GB)   |              |
     +-------------+-------------+              |
                   |                            |
                   | Mount via NFS              |
                   +-------------->-------------+

   Snapshot Flow:

    Extra EBS Volume ----> Snapshot ----> New EBS Volume ----> Attach to EC2

# 🎓 AWS Architecture Diagram

![WordPress on EC2 + RDS Diagram](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Guide/AWS%20EBS,%20Snapshots%20&%20EFS%20Lab%20Scenario%20Diagram%20Step%20by%20Step%20Guide/0_veGPUDYqaETLy0P2.png?raw=true)
---

## *3. Step-by-Step Guide (Roman Urdu)*

### *Step 1: EC2 Instance Create karna*

1. EC2 console open karo
2. Launch Instance → Amazon Linux 2 select karo
3. VPC, Subnet default rakh sakte ho
4. Storage me by default *EBS root volume* hota hai (8 GB)
5. Launch instance

---

### *Step 2: Extra EBS Volume Create karna*

1. EC2 → Elastic Block Store → *Volumes*
2. Create Volume → 5GB GP3 select karo
3. Same AZ choose karo jahan EC2 hai
4. Create

*Attach Volume:*

* Volume select → Actions → Attach → Apna EC2 instance choose karo

---

### *Step 3: EC2 ke andar volume format + mount karna*

bash
df -h\lsblk
sudo mkfs -t xfs /dev/xvdf
sudo mkdir /data
sudo mount /dev/xvdf /data


---

### *Step 4: EBS Snapshot Create karna*

1. EBS Volume select karo
2. Actions → Create Snapshot
3. Name: ebs-backup-snap
4. Snapshot create ho jayega

---

### *Step 5: Snapshot se New Volume Restore karna*

1. Snapshot → Actions → Create Volume from Snapshot
2. Same AZ choose karo

*Attach karo EC2 pe:*

* Actions → Attach Volume

---

### *Step 6: EFS Create karna*

1. EFS console → Create File System
2. VPC select karo jahan EC2 hai
3. Mount Targets → har AZ me automatic create ho jate

---

### *Step 7: EC2 pe EFS mount karna*

*Amazon Linux:*

bash
sudo yum install -y amazon-efs-utils
sudo mkdir /efs
sudo mount -t efs fs-XXXX:/ /efs


*Check:*

bash
df -h


---

### *Step 8: EFS Test*

1. /efs me ek file banao
2. Agar doosra EC2 mount hoga to same file visible hogi

---

## *8. Summary*

* EBS → EC2 ke sath attach hoti block storage
* Snapshot → EBS ki backup image hoti
* Snapshot se new volume create kar sakte
* EFS → Shared file system for many EC2 (NFS)

---


Agar chaho to is ka *clean diagram image* bhi bana doon.
