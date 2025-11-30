# AWS RDS + Linux Bash Scripting Lab

## **Lab Title:** Securely Connect to AWS RDS Using Bash Scripting (No Password Prompt)

## **Objective**
Learn how to connect to an AWS RDS database using Bash scripts **without typing your password**, using three professional methods:
1. AWS Secrets Manager (Best Practice)
2. MySQL `.my.cnf` (Secure local use)
3. Environment variable (For quick labs)

## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/AWS%20RDS%20+%20Linux%20Bash%20Scripting%20Lab.jpg?raw=true)
---

# **1. Prerequisites**
- AWS Account
- EC2 Linux instance with IAM Role
- AWS CLI installed
- RDS MySQL/PostgreSQL DB created
- Linux terminal access
- `jq` installed (for JSON parsing)

## Install jq:
```bash
sudo yum install jq -y  # Amazon Linux
```
## Install DB Client
```
sudo dnf update -y
sudo dnf install mariadb105 -y
```
---

# **2. Method 1 — AWS Secrets Manager (Most Secure & Recommended)**

## Step 1 — Store credentials in Secrets Manager
1. Go to **AWS Console → Secrets Manager**
2. Click **Store a new secret**
3. Choose **Credentials for RDS**
4. Enter:
   - username
   - password
   - RDS endpoint
   - database name
5. Save and copy the **Secret ARN**

---

## Step 2 — Create IAM Policy for EC2 to read secrets

### Policy JSON
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:*"
    }
  ]
}
```

Attach this policy to the **EC2 IAM Role**.

---

## Step 3 — Bash Script: Fetch secret + Connect to RDS

### `connect_rds_secret.sh`
```bash
#!/bin/bash

SECRET=$(aws secretsmanager get-secret-value --secret-id myrdssecret --query SecretString --output text)
USER=$(echo $SECRET | jq -r '.username')
PASS=$(echo $SECRET | jq -r '.password')
HOST=$(echo $SECRET | jq -r '.host')
DB=$(echo $SECRET | jq -r '.dbname')

mysql -h $HOST -u $USER -p$PASS $DB -e "SHOW TABLES;"
```

Make executable:
```bash
chmod +x connect_rds_secret.sh
```

Run:
```bash
./connect_rds_secret.sh
```

---

# **3. Method 2 — Using `.my.cnf` File (Secure Local Use)**

## Step 1 — Create the hidden config file
```bash
nano ~/.my.cnf
```

### Insert credentials
```
[client]
user=myuser
password=mypass
host=mydb.xxxxxx.rds.amazonaws.com
```

## Step 2 — Restrict file permissions
```bash
chmod 600 ~/.my.cnf
```

## Step 3 — Verify Your Connection Bash script
```bash
mysql --defaults-extra-file=~/.my.cnf -e "SHOW DATABASES;"
```
## Step 4 — Create a New Database
```
mysql --defaults-extra-file=~/.my.cnf -e "CREATE DATABASE my_new_database;"
```
## Step 5 — Run Table Creation and Insert Statements
```
mysql --defaults-extra-file=~/.my.cnf -e "
USE dbname;
CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
);
INSERT INTO users (name, email) VALUES ('Alamgir Hosen', 'alamgir@example.com'), ('Abir Ahmed', 'abir@example.com');
INSERT INTO users (name, email) VALUES ('ali khan', 'alikhan@example.com'), ('usman Ahmed', 'usmana@example.com');
INSERT INTO users (name, email) VALUES ('Alamgir j', 'alwmgir@example.com'), ('Abir Ahmaed', 'awwir@example.com');
"
```
## Step 5 — Verification
```
mysql --defaults-extra-file=~/.my.cnf -e "
USE dbname; 
SHOW TABLES; 
DESCRIBE users; 
SELECT * FROM users;"
```

## The Automated Setup Script


- First, create a file named rds_automationsetup.sh
- copy and paste bash script

```
#!/bin/bash

# --- CONFIGURATION (EDIT THESE) ---
RDS_USER="myuser"
RDS_PASS="mypass"
RDS_HOST="mydb.xxxxxx.rds.amazonaws.com"
DB_NAME="my_new_database"
CONFIG_FILE="$HOME/.my.cnf"
# ---------------------------------

## Section 1: Create and Secure the .my.cnf File 🔐
echo "## 1. Creating and securing the MySQL config file ($CONFIG_FILE)..."

# Use 'cat' to write the configuration to the file (non-interactively)
cat > "$CONFIG_FILE" << EOF
[client]
user=$RDS_USER
password=$RDS_PASS
host=$RDS_HOST
EOF

# Restrict file permissions for security
chmod 600 "$CONFIG_FILE"

echo "Configuration file created and secured."
echo "---"

## Section 2: Create Database, Table, and Insert Data 🚀
echo "## 2. Running database setup commands..."

# We use the 'CREATE DATABASE IF NOT EXISTS' command to prevent errors
# if the script is run multiple times.
mysql --defaults-extra-file="$CONFIG_FILE" -e "
CREATE DATABASE IF NOT EXISTS $DB_NAME;
USE $DB_NAME;
CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
);
INSERT INTO users (name, email) VALUES 
('Alamgir Hosen', 'alamgir@example.com'), 
('Abir Ahmed', 'abir@example.com'),
('ali khan', 'alikhan@example.com'), 
('usman Ahmed', 'usmana@example.com'),
('Alamgir j', 'alwmgir@example.com'),
('Abir Ahmaed', 'awwir@example.com');
"

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
    echo "Database ($DB_NAME), Table (users), and data created successfully."
else
    echo "ERROR: Failed to run database setup commands. Check your credentials/security groups."
    exit 1
fi
echo "---"

## Section 3: Verification ✨
echo "## 3. Verifying setup..."

mysql --defaults-extra-file="$CONFIG_FILE" -e "
USE $DB_NAME;
SHOW TABLES;
DESCRIBE users;
SELECT * FROM users;
"
echo "Verification complete."
```

### How to Execute the Script
- Make it Executable

```
chmod +x rds_setup.sh
```

- Run the Script

```
./rds_setup.sh
```

---

# **4. Method 3 — Environment Variables (Easy Lab Only)**

## Step 1 — Set the Environment Variables
- You must replace the placeholder values with your actual RDS credentials and endpoint. The export command makes the variables available to sub-processes (like the mysql client).

```bash
# Replace these with your actual values!
export MYSQL_HOST="mydb.xxxxxx.rds.amazonaws.com"
export MYSQL_USER="myuser"
export MYSQL_PASSWORD="mypass"
export DB_NAME="my_new_database"
```
- Note: The mysql client uses these specific variable names: MYSQL_HOST, MYSQL_USER, and MYSQL_PASSWORD.

## Step 2 — Execute the Database Setup Commands
- Now, you can run the mysql commands without the --defaults-extra-file flag or the -h, -u, and -p flags. The mysql client automatically reads the values from the environment.

```bash
mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
```


### Script
```bash
mysql -h mydb.xxxxxx.rds.amazonaws.com -u admin -p$DBPASS -e "SHOW DATABASES;"
```


---
# **5. Method 4 — Simple EC2 Scripts (Easy Lab Only)**

### Step 1 Create a Bash Script file 


```
#!/bin/bash

### -------------------------------
### 1. RDS DATABASE CREDENTIALS
### -------------------------------
DB_HOST="your-rds-endpoint.amazonaws.com"
DB_USER="mydbuser"
DB_PASS="mydbpassword"
DB_NAME="mydatabase"
DB_PORT="3306"

### -------------------------------
### 2. UPDATE SYSTEM
### -------------------------------
yum update -y

### -------------------------------
### 3. INSTALL REQUIRED PACKAGES
### -------------------------------
yum install -y mariadb httpd php php-mysqli

systemctl enable httpd
systemctl start httpd

### -------------------------------
### 4. CREATE A TEST PHP APP
### -------------------------------
cat <<EOF > /var/www/html/index.php
<?php
\$servername = "$DB_HOST";
\$username = "$DB_USER";
\$password = "$DB_PASS";
\$dbname = "$DB_NAME";

\$conn = new mysqli(\$servername, \$username, \$password, \$dbname);

if (\$conn->connect_error) {
    die("Connection failed: " . \$conn->connect_error);
}
echo "Connected successfully to RDS!";
?>
EOF

### -------------------------------
### 5. TEST CONNECTION AND LOG OUTPUT
### -------------------------------
echo "Testing DB connectivity..." >> /var/log/rds-lab.log
mysql -h \$DB_HOST -u \$DB_USER -p\$DB_PASS -e "SHOW DATABASES;" >> /var/log/rds-lab.log 2>&1

echo "Setup Completed!" >> /var/log/rds-lab.log
```


### Step 2 How to Use This Script on EC2 (User Data)
- Upload bach script file on S3 Bucket 
- Copy the script into EC2 User Data:

```
#!/bin/bash
curl -o /root/setup_rds_app.sh https://your-s3-bucket.s3.amazonaws.com/setup_rds_app.sh
chmod +x /root/setup_rds_app.sh
/root/setup_rds_app.sh

```

- Or upload script manually to EC2 via SSH:

```
scp setup_rds_app.sh ec2-user@EC2-IP:~
ssh ec2-user@EC2-IP
chmod +x setup_rds_app.sh
sudo ./setup_rds_app.sh
```
### Optional: Create a Version Using Environment Variables
- Instead of hardcoding:
```
export DB_HOST="your-rds-endpoint.amazonaws.com"
export DB_USER="mydbuser"
export DB_PASS="mydbpassword"
```
- Then source them:

```
source /etc/rds.env
```




# **6. What Not To Do**
❌ Never hardcode passwords in Bash scripts
❌ Never store passwords in GitHub
❌ Avoid using `mysql -p mypass` (shell history risk)

---

# **7. Recommended Method for AWS Hands‑On Labs**
Use **AWS Secrets Manager**, because it teaches:
- IAM Policies
- EC2 Roles
- Secure automation
- AWS CLI usage

---

# **8. Optional: Add Logging to CloudWatch**
You can send script logs using:
```bash
logger "RDS script executed successfully"
```

---

# **9. Next Steps (If You Want)**
I can generate:
- A complete **4‑tier AWS advanced lab** (.md file)
- Bash automation scripts
- CloudWatch + Lambda integration
- API Gateway + DynamoDB workflows
- High‑security SG + NACL setup guide

# IAM Roles for EC2, RDS, and CloudWatch Monitoring


## Next Task

## **AWS Visual Architecture Diagram**
![AWS Visual Architecture Diagram](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/1_VnZWZ37dIjzoKc7pfDqH0w.png?raw=true)
---

## 1. Create IAM Role for EC2 (CloudWatch + RDS Monitoring)

### Steps (Console)

1.  Go to **IAM → Roles → Create Role**
2.  Trusted entity: **AWS Service**
3.  Use case: **EC2**
4.  Attach the following policies:
    -   CloudWatchAgentServerPolicy
    -   AmazonEC2ReadOnlyAccess
    -   AmazonSSMManagedInstanceCore
    -   Custom policy provided below
5.  Name the role: **EC2-CloudWatch-RDSMonitoring-Role**

------------------------------------------------------------------------

## 2. Custom IAM Policy

### Policy Name: `Custom-EC2-RDS-CloudWatchMonitorPolicy`

``` json
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
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:DescribeDBLogFiles",
        "rds:DownloadDBLogFilePortion"
      ],
      "Resource": "*"
    }
  ]
}
```

------------------------------------------------------------------------

## 3. Attach IAM Role to EC2 Instance

1.  EC2 → Instances\
2.  Select Instance\
3.  Actions → Security → **Modify IAM Role**\
4.  Select: **EC2-CloudWatch-RDSMonitoring-Role**

------------------------------------------------------------------------

## 4. Configure CloudWatch Agent on EC2

### Install CloudWatch Agent

``` bash
sudo yum install amazon-cloudwatch-agent -y || sudo apt install amazon-cloudwatch-agent -y
```

### Create agent config file:

`/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json`

``` json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/ec2/system",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/httpd/access_log",
            "log_group_name": "/ec2/apache",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

### Start Agent

``` bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
-a start -m ec2 \
-c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

------------------------------------------------------------------------

## 5. Enable RDS Logs to CloudWatch

### Enable Enhanced Monitoring

1.  RDS → DB Instance → Modify\
2.  Enhanced Monitoring → **Enable**\
3.  Choose role: **rds-monitoring-role**

### Enable Log Exports

Enable: - Error logs\
- General logs\
- Slow query logs\
- CloudWatch Logs Export

------------------------------------------------------------------------

## Summary Table

  ----------------------------------------------------------------------------
  Component          IAM Role / Policy                        Purpose
  ------------------ ---------------------------------------- ----------------
  EC2                EC2-CloudWatch-RDSMonitoring-Role        Monitoring EC2 +
                                                              RDS logs

  Custom Policy      Custom-EC2-RDS-CloudWatchMonitorPolicy   Full
                                                              CloudWatch + RDS
                                                              access

  Managed Policies   CloudWatchAgentServerPolicy              Required for log
                                                              shipping

  RDS Role           rds-monitoring-role                      Enhanced
                                                              monitoring
  ----------------------------------------------------------------------------

