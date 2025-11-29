**1. Steps to Create VPC — MyVPC1:**



* In AWS Management Console, search VPC and open the VPC Dashboard.
* Click Create VPC.
* Select VPC only.
* Enter Name tag: MyVPC1.
* Enter IPv4 CIDR block: 10.0.0.0/16.
* Leave IPv6 CIDR block as None.
* Keep Tenancy as Default.
* Click Create VPC.
* Go to Your VPCs and confirm that MyVPC1 is created with CIDR 10.0.0.0/16.



**2. Steps to Create Public Subnet:**



* Go to VPC Dashboard → Subnets → Create subnet.
* Select VPC: MyVPC1.
* Enter Subnet name: MyPublicSubnet1.
* Choose an Availability Zone (for example, us-east-1a).
* Enter IPv4 CIDR block: 10.0.1.0/24.
* Click Create subnet.
* After creation, select the subnet → Actions → Edit subnet settings → Enable auto-assign public IPv4 address → Save.



**3. Steps to Create Internet Gateway:**



* Go to Internet Gateways → Create internet gateway.
* Enter Name tag: InternetGateway1.
* Click Create internet gateway.
* Select the newly created IGW → Actions → Attach to VPC → Select MyVPC1 → Attach internet gateway
* 

**4. Steps to Create Routing Table:**



* Go to Route Tables → Create route table.
* Enter Name tag: RoutingTable1.
* Select VPC: MyVPC1.
* Click Create route table.
* Select RoutingTable1 → go to Routes → Edit routes → Add route.
* In Destination, enter 0.0.0.0/0.
* In Target, select InternetGateway1.
* Click Save changes.
* In the same route table, go to Subnet associations → Edit subnet associations.
* Check MyPublicSubnet1 → click Save associations.



**5. Steps to Create Security Group:**

Go to VPC Dashboard → Security Groups → Create security group.

* Enter Security group name: MyEC2-SG.
* Enter Description: Allow SSH and future DB access.
* Select VPC: MyVPC1.
* Under Inbound rules, click Add rule.
* Rule 1 → Type: SSH | Protocol: TCP | Port range: 22 | Source: My IP.
* (Optional for now) Rule 2 → Type: HTTP | Protocol: TCP | Port range: 80 | Source: 0.0.0.0/0.
* Click Create security group.



**6. Steps to Create EC2 Instance:**



* Go to EC2 Dashboard → Instances → Launch instance.
* Name: MyEC2Instance.
* Application and OS Image (AMI): Amazon Linux 2 (x86).
* Instance type: t2.micro.
* Key pair: Choose an existing key pair or create a new one.
* Under Network settings, choose: VPC: MyVPC1, Subnet: MyPublicSubnet1, Auto-assign Public IP: Enable, Firewall (security groups): Select existing → MyEC2-SG.
* Under Advanced details → User data, (optional) you can add startup commands if needed.
* Click Launch instance.
* Wait until the instance state is Running and note the Public IPv4 address.





**7. Create Private Subnets**



* Go to VPC Dashboard → Subnets → Create subnet.
* VPC: MyVPC1
* Subnet name: MyPrivateSubnet1
* Availability Zone: pick one (Europe (Stockholm), eu-north-1b)
* IPv4 CIDR block: e.g., 10.0.2.0/24
* Click Create subnet.
* Repeat for another subnet:
* Name: MyPrivateSubnet2
* Availability Zone: another AZ (Europe (Stockholm), eu-north-1c)
* CIDR block: 10.0.3.0/24
* Repeat for another subnet:
* Name: MyPrivateSubnet3
* Availability Zone: another AZ (Europe (Stockholm), eu-north-1a)
* CIDR block: 10.0.4.0/24





**8: Create a DB Subnet Group:**



Go to RDS Dashboard → Subnet groups → Create DB Subnet Group.

Name: MyDBSubnetGroup

VPC: MyVPC1

Description: Subnet group for Aurora DB.

Add subnets: Select all three private subnets (MyPrivateSubnet1, MyPrivateSubnet2, and MyPrivateSubnet3).

Click Create.



**9. Create a Security Group for the Database**



* Go to VPC Dashboard → Security Groups → Create security group.
* Name: MyDB-SG
* Description: Allow MySQL access from EC2 instance.
* VPC: MyVPC1
* Under Inbound rules → Add rule:
* Type: MySQL/Aurora
* Port range: 3306
* Source: Select MyEC2-SG (the security group of your EC2 instance).
* Click Create security group.





**9. Steps to Create an Amazon Aurora MySQL Cluster with Two Replicas:**



* Go to AWS Console → RDS service.
* Click Create database.
* Choose Database creation method → select Standard create.



**Under Engine options, choose:**



* Engine type: MySQL
* Version: Select the latest available MySQL version (e.g., MySQL 8.x).
* Under Templates, select Dev/Test (for basic setup) or Production if you need Multi-AZ standby
* Select "Multi-AZ DB cluster deployment (3 instances)"



**Under Settings, enter:**



* DB instance identifier: MyMySQLDB
* Master username: admin
* Master password: choose a strong password
* Confirm password





**Under DB instance class, choose:**



* Example: db.r5d (2vCPU, 16GB RAM)
* Storage type: SSD gp3
* Allocated Storage: 50



**Under Instance configuration, choose:**



* DB instance class: db.t3.medium (or any supported small class)
* Number of Aurora Replicas: 2
* (AWS will automatically distribute replicas across your private subnets / AZs.)
* Under Storage, leave defaults (Aurora is auto-scaling by design).



**Under Connectivity:**



* VPC: select MyVPC1
* DB Subnet Group: select MyDBSubnetGroup (the one with three private subnets)
* Public access: No (private only)
* VPC security group: choose existing → MyDB-SG
* Availability Zone: leave default or select one AZ (for primary DB).



**Under Database authentication:**



* keep Password authentication.
* Leave other options (Monitoring, Backups, Maintenance) as default.
* Scroll down → click Create database.



**Installing SQL Tool on EC2 Instance:**



yum install -y mariadb105

mysql --version



**Accesing Master Database and Create a Database and Table:**



mysql -h mymysqldb-instance-1.ch662cs8q4lf.eu-north-1.rds.amazonaws.com -u admin -p

show databases;

create database my\_rds\_sample;

use my\_rds\_sample

**# create user table**

 CREATE TABLE users (

 id INT AUTO\_INCREMENT PRIMARY KEY,

 name VARCHAR(100) NOT NULL,

 email VARCHAR(100) UNIQUE NOT NULL

 );



**# insert sample data**

 INSERT INTO users (name, email)

VALUES

('Khurram Shahzad', 'khurramshahzadansari1509@gmail.com'),

 ('Shah Fahad', 'shahfahad@gmail.com');



MySQL \[my\_rds\_sample]> select \* from users;

+----+---------------+---------------------+

| id | name          | email               |

+----+---------------+---------------------+

|  1 | Alamgir Hosen | alamgir@example.com |

|  2 | Abir Ahmed    | abir@example.com    |

+----+---------------+---------------------+



**Accessing Reader Instance1 to check database and table creation:**





mysql -h mymysqldb-instance-2.ch662cs8q4lf.eu-north-1.rds.amazonaws.com -u admin -p



MySQL \[(none)]> show databases;

+--------------------+

| Database           |

+--------------------+

| information\_schema |

| my\_rds\_sample      |

| mysql              |

| performance\_schema |

| sys                |

+--------------------+

5 rows in set (0.002 sec)



MySQL \[my\_rds\_sample]> select \* from users;

+----+---------------+---------------------+

| id | name          | email               |

+----+---------------+---------------------+

|  1 | Alamgir Hosen | alamgir@example.com |

|  2 | Abir Ahmed    | abir@example.com    |

+----+---------------+---------------------+

2 rows in set (0.001 sec)



**Accessing Reader Instance2 to check database and table creation:**





mysql -h mymysqldb-instance-3.ch662cs8q4lf.eu-north-1.rds.amazonaws.com -u admin -p



MySQL \[(none)]> show databases;

+--------------------+

| Database           |

+--------------------+

| information\_schema |

| my\_rds\_sample      |

| mysql              |

| performance\_schema |

| sys                |

+--------------------+

5 rows in set (0.001 sec)



MySQL \[my\_rds\_sample]> select \* from users;

+----+---------------+---------------------+

| id | name          | email               |

+----+---------------+---------------------+

|  1 | Alamgir Hosen | alamgir@example.com |

|  2 | Abir Ahmed    | abir@example.com    |

+----+---------------+---------------------+

2 rows in set (0.000 sec)



**Replica is unable to write data(Because it is only in read only option):**



MySQL \[my\_rds\_sample]> INSERT INTO users (name, email)

    -> VALUES

    -> ('Khurram Shahzad', 'khurramshahzadansari1509@gmail.com'),

    ->  ('Shah Fahad', 'shahfahad@gmail.com');

ERROR 1290 (HY000): The MySQL server is running with the --read-only option so it cannot execute this statement

MySQL \[my\_rds\_sample]>

















