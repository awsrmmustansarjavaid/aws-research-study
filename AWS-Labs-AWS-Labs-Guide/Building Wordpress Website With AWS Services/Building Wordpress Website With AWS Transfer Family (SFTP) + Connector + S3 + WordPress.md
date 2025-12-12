## ☁️ AWS Hands-on Lab Guide 

# AWS Wordpress Configuration Lab Guide (EC2 + S3 + WordPress + RDS & SFTP + AWSTransfer Family (SFTP) + Connector) Architecture

### Architecture Designer: Charlie



----
## ☁️ AWS Architecture Method 1  —  AWS Wordpress Configuration Lab Guide (EC2 + WordPress + RDS & SFTP) Architecture
-----



---

# 🖥️ Lab Overview

This hands-on AWS lab guides you through building a production-style WordPress architecture using:

- Amazon EC2 (Amazon Linux 2023) running Nginx + PHP-FPM hosting WordPress

- Amazon RDS MySQL (private, only accessible by EC2 SG)

- Secure SFTP-only user (chrooted) for uploading WordPress assets

- CloudWatch Agent on EC2 to send metrics & log files (nginx, php-fpm, system)

- Full verification checks and troubleshooting steps

This setup provides:

- ⚡ High performance  
- 🔐 Secure DB isolation  
- 🛠 Easy maintenance  
- 📈 Scalable architecture  

---

# 🎓 AWS Architecture Diagram

![WordPress on EC2 + RDS Diagram](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Guide/Building%20Wordpress%20Website%20With%20AWS%20Services/Building%20Wordpress%20Website%20With%20EC2%20&%20RDS.png?raw=true)

---

# ⚖️ Architecture Flow

1. User → EC2 (Nginx + PHP-FPM)  
2. EC2 → Amazon RDS (MySQL database)  
3. EC2 security group allows HTTP/HTTPS  
4. RDS security group allows port **3306 only from EC2-SG**  
5. SFTP → Wordpress

---

# 📋 Step-by-Step Lab Guide



# 💻 Section 1 — Preparing the WordPress Prerequisites & Foundational Setup



# 🟦 Section 1 — IAM Role and Policies

## IAM Role 1- Create IAM Role for CloudWatch

- Open IAM Console

- AWS Console → IAM → Roles → Create Role

- Choose Trusted Entity (Very Important)

- **Select:**

```
AWS Service
```

Then choose:
```
EC2
```

- Click Next.

#### Attach Required Policies

You need two policies to fully monitor EC2 + CloudWatch Agent.

- **Required Policy 1: CloudWatchAgentServerPolicy**

This allows EC2 to send logs + metrics to CloudWatch.

- Search and select:

```
CloudWatchAgentServerPolicy
```

- **Required Policy 2: AmazonSSMManagedInstanceCore**

This allows SSM (Systems Manager) to run and manage CloudWatch Agent easily.

- Search and select:

```
AmazonSSMManagedInstanceCore
```

- **(Optional but Recommended)**

If you plan to store custom logs into S3:

```
AmazonS3ReadOnlyAccess
```

Only add this if you know you need it.

#### Name the Role

Use a clear name:

```
EC2-CloudWatchAgent-Role
```

- Click Create Role.

***

## IAM Role 2- Create IAM Role for Transfer Family (SFTP)

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
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":[
        "s3:ListBucket"
      ],
      "Resource":[
        "arn:aws:s3:::my-transfer-sftp-bucket-12345"
      ]
    },
    {
      "Effect":"Allow",
      "Action":[
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObjectAcl",
        "s3:PutObjectAcl"
      ],
      "Resource":[
        "arn:aws:s3:::my-transfer-sftp-bucket-12345/*"
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

# 🟦 SECTION 2 — Create S3 Bucket for WordPress Files

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

---

# 🟦 Section 3 — Download and install the CloudWatch agent package (Amazon Linux 2023)

```
sudo dnf install -y amazon-cloudwatch-agent
```

### Create config file

Create agent config /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

```
sudo nano /opt/aws/amazon-cloudwatch-agent/bin/config.json
```

**Paste:** Example config (collects nginx logs, php-fpm logs, system logs and CPU/memory/disk metrics)


```
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },

  "metrics": {
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}"
    },
    "metrics_collected": {
      "cpu": {
        "measurement": [
          "cpu_usage_idle",
          "cpu_usage_user",
          "cpu_usage_system"
        ],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [
          "used_percent"
        ],
        "resources": [
          "/"
        ],
        "metrics_collection_interval": 60
      }
    }
  },

  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "wordpress-lab",
            "log_stream_name": "ec2-system-log"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "wordpress-lab",
            "log_stream_name": "nginx-access"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "wordpress-lab",
            "log_stream_name": "nginx-error"
          },
          {
            "file_path": "/var/log/php-fpm/www-error.log",
            "log_group_name": "wordpress-lab",
            "log_stream_name": "php-fpm-error"
          }
        ]
      }
    }
  }
}
```

### 📝 Important Notes

#### ✔️ 1. PHP-FPM Log Path Might Be Different

##### Common paths:

```
/var/log/php-fpm/error.log
/var/log/php7.4-fpm.log
/var/log/php-fpm/www-error.log
```


**Note: Adjust php-fpm log path to your distro’s path. If php-fpm uses /var/log/php-fpm/error.log or /var/log/php-fpm/www-error.log, set accordingly. To find php-fpm error log path:**

##### Test it:

```
php -i | grep error_log
# or inspect /etc/php-fpm.d/www.conf for 'error_log'
sudo grep -R "error_log" /etc/php*
```

#### ✔️ 2. Restart CloudWatch Agent

```
sudo systemctl restart amazon-cloudwatch-agent
```

```
sudo systemctl status amazon-cloudwatch-agent
```

#### ✔️ 3. Logs will now appear like this:

##### Log Group:

```
wordpress-lab
```

##### Log Streams:

```
ec2-system-log
nginx-access
nginx-error
php-fpm-error
```

**And metrics will appear automatically under EC2 → Monitoring and CloudWatch → Metrics.**


---

# 🟦 Section 4 — Launch RDS MySQL

## Step 1 — RDS Recommended Settings

- **Engine:** MySQL 8.x

- **Instance class:** db.t3.micro

- **Storage:** 20 GB

- **Public Access:** NO (private)

- **Initial DB name:** wordpressdb (or wordpressdb)

- **Master User:** wpadmin

- **Master Password:** wpadmin123

- **RDS Security Group** 

- **Inbound:**

```
rds-db-sg that allows 3306 from web-server-sg
```

## Step 2 — Install MySQL Client on EC2

### Install and Configure MariaDB (MySQL)

```
sudo dnf install mariadb105-server mariadb105 -y
```

#### Start & enable DB

```
sudo systemctl start mariadb
```

```
sudo systemctl enable mariadb
```

#### Confirm versions:

```
mysql --version
```

#### Secure DB

##### Run secure installation:

```
sudo mysql_secure_installation
```

#### Use the following answers:

```
| Prompt                 | Answer                    |
| ---------------------- | ------------------------- |
| Switch to unix_socket  | n                         |
| Set root password      | y → Enter strong password |
| Remove anonymous       | y                         |
| Disallow remote root   | y                         |
| Remove test DB         | y                         |
| Reload privilege table | y                         |
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
exit
```
##### Note: Use a strong password and store it securely (Secrets Manager recommended for production).




---


# 💻 Section 1 — Preparing the WordPress Foundational Deployment Setup


# 🟦 Section 1 — Configure AWS EC2 

## Step 1 Network & Security Group plan:


- **EC2-SG (web-server-sg)** — inbound:

```
SSH (22) → Your_IP/32 only

HTTP (80) → 0.0.0.0/0 (or restrict to your test IPs)

HTTPS (443) → 0.0.0.0/0 (recommended)
```

- **RDS-SG (rds-db-sg)** — inbound:

```
MySQL/Aurora (3306) → Source: web-server-sg (allow from web server SG only)
```
- Keep outbound egress open (or default 0.0.0.0/0) for EC2 so it can access RDS endpoint / updates.


### EC2 Config:
- **AMI:** Amazon Linux 2023  
- **Instance type:** t2.micro / t3.micro  
- **Storage:** 20 GB  
- **Security Group Rules:**  
  - 22 (SSH) – Your IP  
  - 80 (HTTP) – 0.0.0.0/0  
  - 443 (HTTPS) – 0.0.0.0/0  

- **Attach IAM Role:**  

```
EC2-CloudWatchAgent-Role
```



#### Attach IAM Role to Your EC2 Instance (if you forgot to do so during launch)

- Go to EC2 → Instances → Select your WordPress EC2 → Actions → Security → Modify IAM Role

```
EC2-CloudWatchAgent-Role
```
- save

## Step 2 Connect:


```
ssh -i yourkey.pem ec2-user@<EC2-PUBLIC-IP>
```

## Step 3 — Install apache or Nginx, PHP-FPM & Required Packages

### Method 1 — Install apache, PHP-FPM & Required Packages


## Step 1 — Update

```
sudo dnf update -y
```

## Step 2 — Install & Start Apache

```
sudo yum install httpd -y
```

```
sudo systemctl start httpd
```

```
sudo systemctl enable httpd
```

## Step 3 — Now test in browser:

```
http://YOUR_PUBLIC_IP
```

**You should see Apache test page ✅**

## Step 4 — Fix Permissions (Very Important for WordPress)

```
sudo chown -R apache:apache /var/www/html
```

```
sudo chmod -R 755 /var/www
```

## Step 5 — Install PHP for WordPress

```
sudo dnf install php php-mysqlnd php-fpm php-json php-zip php-gd php-curl php-xml php-mbstring -y
```

```
sudo systemctl restart httpd
```
###### ✔ Fully compatible modules

###### ✔ Required for WordPress to work properly

#### Confirm Apache + PHP Works

```
curl -I http://localhost
```

##### Expected:

```
HTTP/1.1 200 OK
Server: Apache
```

#### Confirm Security Group

**Make sure your EC2 Security Group has:**

```
✅ HTTP – Port 80 – 0.0.0.0/0
✅ HTTPS – Port 443 – 0.0.0.0/0 (optional)
```

## Step 6 —  WordPress Directory

```
cd /tmp
```

```
wget https://wordpress.org/latest.tar.gz
```

```
tar -xzf latest.tar.gz
```

```
sudo cp -R wordpress/* /var/www/html/
```

## Step 7 — Set permissions

```
sudo chown -R apache:apache /var/www/html
```

```
sudo find /var/www/html -type d -exec chmod 755 {} \;
```

```
sudo find /var/www/html -type f -exec chmod 644 {} \;
```

```
sudo systemctl restart httpd
```

#### Now Open WordPress

Go to browser:

```
http://YOUR_PUBLIC_IP
```

**You should see:**

##### ✅ WordPress setup screen

## Step 8 — Check Your Web Directory

```
ls -lah /var/www/html
```

## Step 9 — Configure wp-config.php

### Create config:

```
cd /var/www/html
```

```
sudo cp wp-config-sample.php wp-config.php
```

### Edit:

```
sudo nano wp-config.php
```
### Update database connection:

```
define( 'DB_NAME', 'wordpress' );
define( 'DB_USER', 'wordpressuser' );
define( 'DB_PASSWORD', 'StrongPassword123!' );
define( 'DB_HOST', '<RDS-ENDPOINT>' );
```

##### Example RDS endpoint:

```
mydb.abcdefghijkl.us-east-1.rds.amazonaws.com
```



### Add AUTH keys:

Add auth keys (generate unique salts):
 

#### Generate keys:

- Open  

https://api.wordpress.org/secret-key/1.1/salt/

in your browser, copy and paste the output into wp-config.php replacing the placeholder keys.

```
define('AUTH_KEY',         '+7CA?k*Ju&8eCfg=/aFKo0tO5Tn73Cg 9|Ed73k|Gw(3^');
define('SECURE_AUTH_KEY',  ':H$M&FvbE6t:EwH5ik/D!@]@%Dv3!-Q^hNH3*O+-$L6c*|');
define('LOGGED_IN_KEY',    'g9?;b_A BNW[; $9N^E2^jt$LkF 8_^baTmjhp<eE5GUd');
define('NONCE_KEY',        'G;Wf@|;jzQh>R812&-x^cPoq`tOOu>q)#JVa Y%No%.JpZ[');
define('AUTH_SALT',        'up^dE)4&x/?]1[thjghhjjhz6Vhiohr(dVMh+d5=R<.l_#l');
define('SECURE_AUTH_SALT', '@%ka=9?}BQ[m#29D+@jkgjkhjkhjkhkjhkjdTZ`MT{|fypE~');
define('LOGGED_IN_SALT',   'o!UX5|LW4eijhjkbhkjhkjkjbnjjb/1JSPS?e`YW*nrWb|FG ');
define('NONCE_SALT',       '+t}kH4DA`jhbjkbjkbjkbjkbjkbt8(iWX(]e?&tV;k:>|)IoE');
```

- Paste into wp-config.php

- Save and exit.

#### Set proper ownership:

```
sudo chown apache:apache /var/www/html/wp-config.php
```

```
sudo chmod 640 /var/www/html/wp-config.php
```

#### restart apache

```
sudo systemctl restart httpd php-fpm
```

#### Confirm Apache + PHP Works

```
curl -I http://localhost
```

##### Expected:

```
HTTP/1.1 200 OK
Server: Apache
```



***


### Method 2 — Install Nginx, PHP-FPM & Required Packages

### Step 1 — Installation Web Required Packages:

#### Update

```
sudo dnf update -y
```

#### Install Nginx

```
sudo dnf install -y nginx
```

#### Start and enable service

```
sudo systemctl start nginx
```

```
sudo systemctl enable --now nginx
```

```
sudo systemctl status nginx
```

**Visit your server public IP → You should see NGINX Welcome Page**

### Install PHP + Extensions

```
sudo dnf install php php-fpm php-mysqlnd php-json php-opcache php-xml php-gd php-curl php-mbstring php-intl php-zip php-cli -y
```

### Start PHP-FPM

```
sudo systemctl start php-fpm
```

```
sudo systemctl enable php-fpm
```

```
sudo systemctl status php-fpm
```

### Prepare web root & permissions

We will serve WordPress from /usr/share/nginx/html.

```
sudo chown -R nginx:nginx /var/lib/php/
```

```
sudo usermod -a -G nginx ec2-user
```

```
sudo chown -R ec2-user:nginx /var/www
```

##### Note: The nginx user runs the webserver. We keep the owner nginx:nginx and ensure uploads are writable by nginx or specific sftp user (see SFTP config below).


#### Confirm versions:

```
nginx -v
```

```
php -v
```

#### Confirm Apache + PHP Works

```
curl -I http://localhost
```

##### Expected:

```
HTTP/1.1 200 OK
Server: Apache
```
#### Remove default config:

```
sudo rm /etc/nginx/nginx.conf
```

#### Create new NGINX config:

```
sudo nano /etc/nginx/nginx.conf
```

##### Paste exact correct configuration:

```
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name _;

        root /var/www/wordpress;
        index index.php index.html index.htm;

        location / {
            try_files $uri $uri/ /index.php?$args;
        }

        location ~ \.php$ {
            include fastcgi.conf;
            fastcgi_pass unix:/run/php-fpm/www.sock;
        }

        location ~ /\.ht {
            deny all;
        }
    }
}
```

#### Test config:

```
sudo nginx -t
```

#### Reload:

```
sudo systemctl restart nginx
```



### Step 2 — Download WordPress:

```
cd /tmp
```

```
curl -O https://wordpress.org/latest.tar.gz
```

```
tar -xzf latest.tar.gz
```

## Step 3 — Move files to Nginx root:

#### Move to web directory

```
sudo mv wordpress /var/www/
```

#### Set permissions

```
sudo chown -R nginx:nginx /var/www/wordpress
```

```
sudo chmod -R 755 /var/www/wordpress
```

## Step 4 — Configure wp-config.php

### Create config:

```
cd /var/www/wordpress
```

```
sudo cp wp-config-sample.php wp-config.php
```

### Edit:

```
sudo nano wp-config.php
```
### Update database connection:

```
define( 'DB_NAME', 'wordpress' );
define( 'DB_USER', 'wordpressuser' );
define( 'DB_PASSWORD', 'StrongPassword123!' );
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8');
```

### Add AUTH keys:

Add auth keys (generate unique salts):
 

#### Generate keys:

- Open  

https://api.wordpress.org/secret-key/1.1/salt/

in your browser, copy and paste the output into wp-config.php replacing the placeholder keys.

```
define('AUTH_KEY',         '+7CA?k*Ju&8eCfg=/aFKo0tO5Tn73Cg 9|Ed73k|Gw(3^');
define('SECURE_AUTH_KEY',  ':H$M&FvbE6t:EwH5ik/D!@]@%Dv3!-Q^hNH3*O+-$L6c*|');
define('LOGGED_IN_KEY',    'g9?;b_A BNW[; $9N^E2^jt$LkF 8_^baTmjhp<eE5GUd');
define('NONCE_KEY',        'G;Wf@|;jzQh>R812&-x^cPoq`tOOu>q)#JVa Y%No%.JpZ[');
define('AUTH_SALT',        'up^dE)4&x/?]1[thjghhjjhz6Vhiohr(dVMh+d5=R<.l_#l');
define('SECURE_AUTH_SALT', '@%ka=9?}BQ[m#29D+@jkgjkhjkhjkhkjhkjdTZ`MT{|fypE~');
define('LOGGED_IN_SALT',   'o!UX5|LW4eijhjkbhkjhkjkjbnjjb/1JSPS?e`YW*nrWb|FG ');
define('NONCE_SALT',       '+t}kH4DA`jhbjkbjkbjkbjkbjkbt8(iWX(]e?&tV;k:>|)IoE');
```

- Paste into wp-config.php

- Save and exit.

- Set proper ownership:

```
sudo chown nginx:nginx wp-config.php
```

```
sudo chmod 640 wp-config.php
```

#### Restart All Services

```
sudo systemctl restart nginx
```

```
sudo systemctl restart php-fpm
```

```
sudo systemctl restart mariadb
```

### Test & Restart:

```
sudo nginx -t
```

```
sudo systemctl restart nginx
```

## Step 6 — Start WordPress Installer

#### Confirm Apache + PHP Works

```
curl -I http://localhost
```

##### Expected:

```
HTTP/1.1 200 OK
Server: Apache
```
### Open browser:

```
http://<EC2-PUBLIC-IP>
```

### Complete setup:

- **Site Title**

- **Admin user**

- **Admin password**

- **Email**

## 🎉 WordPress is now running on EC2 + RDS!

---

### Method 3 — EC2 User Data Script (Amazon Linux 2023)

#### EC2 User Data Script 1 — NGINX + PHP-FPM + required PHP modules 

- ✔ Installs NGINX + PHP-FPM + required PHP modules

- ✔ Downloads & configures WordPress

- ✔ Sets correct permissions

- ✔ Prepares WordPress to connect to RDS MySQL

- ✔ Confirms NGINX + WordPress is running properly

- ✔ Confirms RDS MySQL connectivity from EC2

#### 📌 Copy/paste directly into EC2 → Advanced Options → User data

##### You MUST replace:

```
<RDS-ENDPOINT>

<DB_PASSWORD>
```


```
#!/bin/bash
set -xe

###########################################
# UPDATE SYSTEM
###########################################
dnf update -y

###########################################
# INSTALL NGINX + PHP + MARIADB CLIENT
###########################################
dnf install -y nginx php php-mysqlnd php-fpm php-json php-zip php-gd \
php-curl php-xml php-mbstring mariadb105

systemctl enable nginx
systemctl enable php-fpm
systemctl start nginx
systemctl start php-fpm

###########################################
# DOWNLOAD WORDPRESS
###########################################
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz

mkdir -p /usr/share/nginx/html
cp -R /tmp/wordpress/* /usr/share/nginx/html/

###########################################
# SET PERMISSIONS
###########################################
chown -R nginx:nginx /usr/share/nginx/html
find /usr/share/nginx/html -type d -exec chmod 755 {} \;
find /usr/share/nginx/html -type f -exec chmod 644 {} \;

###########################################
# CREATE NGINX WORDPRESS CONFIG
###########################################
cat << 'EOF' > /etc/nginx/conf.d/wordpress.conf
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.php index.html;

    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }

    location ~ \.php$ {
        include fastcgi.conf;
        fastcgi_pass unix:/run/php-fpm/www.sock;
    }
}
EOF

nginx -t && systemctl restart nginx

###########################################
# CONFIGURE WORDPRESS wp-config.php TEMPLATE
###########################################
cd /usr/share/nginx/html
cp wp-config-sample.php wp-config.php

# Replace DB name/user/host dynamically using EC2 user data variables
# *** MODIFY THESE VALUES BELOW BEFORE LAUNCH ***
DB_NAME="wordpressdb"
DB_USER="admin"
DB_PASSWORD="YOUR_RDS_PASSWORD"
DB_HOST="YOUR_RDS_ENDPOINT"

sed -i "s/database_name_here/$DB_NAME/" wp-config.php
sed -i "s/username_here/$DB_USER/" wp-config.php
sed -i "s/password_here/$DB_PASSWORD/" wp-config.php
sed -i "s/localhost/$DB_HOST/" wp-config.php

###########################################
# CONFIRM WORDPRESS (NGINX + PHP-FPM) WORKING
###########################################
echo "=== TESTING NGINX + WORDPRESS ===" | tee /var/log/wordpress-test.log

# If index.php loads locally → success
curl -I http://localhost | tee -a /var/log/wordpress-test.log

###########################################
# CONFIRM RDS MYSQL CONNECTIVITY
###########################################
echo "=== TESTING RDS MYSQL CONNECTION ===" | tee -a /var/log/wordpress-test.log

mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW DATABASES;" \
  | tee -a /var/log/wordpress-test.log || echo "MYSQL CONNECTION FAILED" >> /var/log/wordpress-test.log

###########################################
# COMPLETE
###########################################
echo "SETUP COMPLETE" | tee -a /var/log/wordpress-test.log
```

##### ✅ What This Script Confirms Automatically

### 1️⃣ WordPress + NGINX Confirmation

#### The script runs:

```
curl -I http://localhost
```

#### Expected Output (saved in /var/log/wordpress-test.log):

```
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html; charset=UTF-8
```

##### ✔ Means NGINX + PHP-FPM + WordPress is serving web pages properly.

### 2️⃣ RDS MySQL Confirmation

#### The script runs:

```
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW DATABASES;"
```

#### Expected Output:

```
Database
information_schema
mysql
performance_schema
wordpressdb
```

##### ✔ Means EC2 can reach RDS

##### ✔ Credentials are correct

##### ✔ Security Groups / NACLs are not blocking traffic

#### This log also goes into:

```
/var/log/wordpress-test.log
```

***

#### EC2 User Data Script  — WordPress + Apache + PHP + required PHP modules 

- ✔ Installs Apache

- ✔ Installs PHP + required modules

- ✔ Downloads and configures WordPress

- ✔ Sets permissions correctly

- ✔ Configures wp-config.php automatically

- ✔ Confirms Apache & PHP

- ✔ Confirms RDS connectivity

#### 📌 Copy/paste directly into EC2 → Advanced Options → User data

##### You MUST replace:

```
<RDS-ENDPOINT>

<DB_PASSWORD>
```

```
#!/bin/bash
set -e

### =======================================
###  Step 1 - Update system
### =======================================
dnf update -y

### =======================================
###  Step 2 - Install & enable Apache
### =======================================
dnf install httpd -y
systemctl start httpd
systemctl enable httpd

### Fix ownership for Apache
chown -R apache:apache /var/www/
chmod -R 755 /var/www/

### =======================================
###  Step 3 - Install PHP + WordPress required modules
### =======================================
dnf install php php-mysqlnd php-fpm php-json php-zip php-gd php-curl php-xml php-mbstring -y

# Restart Apache to load PHP
systemctl restart httpd

### =======================================
###  Step 4 - Download WordPress
### =======================================
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
cp -R wordpress/* /var/www/html/

### =======================================
###  Step 5 - Set WordPress permissions
### =======================================
chown -R apache:apache /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

systemctl restart httpd

### =======================================
###  Step 6 - Configure WordPress (wp-config.php)
### =======================================
cd /var/www/html
cp wp-config-sample.php wp-config.php

# Update database settings
sed -i "s/database_name_here/wordpress/" wp-config.php
sed -i "s/username_here/wordpressuser/" wp-config.php
sed -i "s/password_here/<DB_PASSWORD>/" wp-config.php
sed -i "s/localhost/<RDS-ENDPOINT>/" wp-config.php

### =======================================
###  Step 7 - Add Secret Keys (Auto fetch from WordPress API)
### =======================================
curl -s https://api.wordpress.org/secret-key/1.1/salt/ > /tmp/wp.keys
sed -i '/AUTH_KEY/d' wp-config.php
sed -i '/SECURE_AUTH_KEY/d' wp-config.php
sed -i '/LOGGED_IN_KEY/d' wp-config.php
sed -i '/NONCE_KEY/d' wp-config.php
sed -i '/AUTH_SALT/d' wp-config.php
sed -i '/SECURE_AUTH_SALT/d' wp-config.php
sed -i '/LOGGED_IN_SALT/d' wp-config.php
sed -i '/NONCE_SALT/d' wp-config.php

# Append generated keys
cat /tmp/wp.keys >> wp-config.php

### Secure wp-config.php
chown apache:apache /var/www/html/wp-config.php
chmod 640 /var/www/html/wp-config.php

### =======================================
###  Step 8 - Confirm Apache + PHP
### =======================================
echo "===== Apache Test =====" >> /var/log/user-data.log
curl -I http://localhost >> /var/log/user-data.log

### =======================================
###  Step 9 - Install MySQL client to test RDS
### =======================================
dnf install mariadb105 -y

echo "===== Testing RDS Connection =====" >> /var/log/user-data.log
mysql -h <RDS-ENDPOINT> -u wordpressuser -p<DB_PASSWORD> -e "SHOW DATABASES;" >> /var/log/user-data.log || echo "RDS Connection Failed" >> /var/log/user-data.log

### Final restart
systemctl restart httpd
```

##### ✅ WHAT THIS SCRIPT DOES AUTOMATICALLY

- ✔ Installs Apache (httpd)

- ✔ Installs PHP + required modules

- ✔ Downloads latest WordPress

- ✔ Moves files to /var/www/html/

- ✔ Fixes permissions correctly

- ✔ Generates & injects WordPress security keys

- ✔ Configures RDS MySQL settings

- ✔ Tests Apache

- ✔ Tests RDS connection

- ✔ Logs results to /var/log/user-data.log



# 🔭 Section 4 — Configure SFTP On AWS

# 🟦 Section 1 — Configure SFTP on AWS EC2

We will create a chrooted SFTP user sftpuser whose jail is /home/sftpuser. To allow WordPress uploads, bind-mount ONLY the wp-content/uploads directory into the chroot. This is safer than mounting full webroot.

### Method 1 — Configuring SFTP if you are using the simple Apache method

## Step 1 — Confirm SSH/SFTP Works

On EC2, SFTP uses the same service as SSH.

```
sudo systemctl status sshd
```

**If not running:**

```
sudo systemctl start sshd
```

```
sudo systemctl enable sshd
```

## Step 2 — Create user and directories

#### Create user without shell login

```
sudo adduser sftpuser
```

```
sudo passwd sftpuser
```
#### Set the user shell to nologin:

```
sudo usermod -s /usr/sbin/nologin sftpuser
```

#### Verify:

```
grep sftpuser /etc/passwd
```

##### Expected:

```
sftpuser:x:1001:1001::/home/sftpuser:/usr/sbin/nologin
```

#### Add them to Apache group:

```
sudo usermod -aG apache sftpuser
```

## Step 3 — Prepare Correct Chroot Directory

##### For SFTP chroot, the base directory must be owned by root.

#### Fix ownership:

```
sudo chown root:root /var/www
```

```
sudo chown root:root /var/www/html
```

#### Fix permissions:

```
sudo chmod 755 /var/www
```

```
sudo chmod 755 /var/www/html
```
## Step 4 — Create Writable Upload Directory for SFTP User

```
sudo mkdir -p /var/www/html/wp-content/uploads
```

```
sudo chown -R sftpuser:apache /var/www/html/wp-content/uploads
```

```
sudo chmod -R 775 /var/www/html/wp-content/uploads
```

##### This directory is writable by:

- **Apache (WordPress uploads)**

- **sftpuser (SFTP uploads)**




## Step 5 — Configure SFTP-only Access in SSHD

#### Open SSH config:

```
sudo nano /etc/ssh/sshd_config
```
### Ensure it says:

```
PasswordAuthentication yes
ChallengeResponseAuthentication yes
KbdInteractiveAuthentication yes
```
## Step 5 — Add this at the bottom:

```
Match User sftpuser
    PasswordAuthentication yes
    AuthenticationMethods password
    ForceCommand internal-sftp
    ChrootDirectory /home/sftpuser
    AllowTCPForwarding no
    X11Forwarding no
```
**Note: This overrides the EC2 Instance Connect defaults.**

- **Save & close.**

- **✔ No shell**

- **✔ No SSH login**

- **✔ SFTP only**

- **✔ Chroot locked to WordPress directory**


## Step 6 — Restart SSH

```
sudo systemctl restart sshd
```

## Step 7 — Open Security Group

### In AWS → EC2 → Security Group:

```
✅ Allow Port 22 (SSH/SFTP)
Source: 0.0.0.0/0 or your IP
```


## Step 8 — Test SFTP from Local Machine

### From your local PC:

```
sftp sftpuser@YOUR_PUBLIC_IP
```

**You should now get a password prompt:**

```
sftpuser@54.157.234.207's password: 
sftp>
```

**After login:**


```
cd html/uploads
put test.jpg
```

### Verify on server:

```
ls -l /var/www/html/wp-content/uploads
```




#### If You’re Using FileZilla

**use:**
```
| Setting  | Value                             |
| -------- | --------------------------------- |
| Protocol | SFTP – SSH File Transfer Protocol |
| Host     | Your EC2 Public IP                |
| Username | sftpuser                          |
| Password | Your password                     |
| Port     | 22                                |
```

#### Result

```
Now:
✅ Your WordPress runs in browser
✅ You can upload files securely via SFTP
✅ Files land directly in uploads folder
```


***

### Method 2 — Configuring SFTP if you are using the Nginx method

## Step 1 — Confirm SSH/SFTP Works

On EC2, SFTP uses the same service as SSH.

```
sudo systemctl status sshd
```

**If not running:**

```
sudo systemctl start sshd
```

```
sudo systemctl enable sshd
```

## Step 2 — Create user and directories

#### Create user without shell login

```
sudo adduser --home /home/sftpuser --shell /sbin/nologin sftpuser
```

#### Set password for SFTP user

```
sudo passwd sftpuser
```

## Step 3 — Prepare Chroot Directory (Required for SFTP Jail)


The SFTP user will be locked into /home/sftpuser.

#### Create main SFTP directory

```
sudo mkdir -p /home/sftpuser/uploads
```

#### Root must own the chroot directory

(This is required or SFTP jail will fail.)

```
sudo chown root:root /home/sftpuser
```

```
sudo chmod 755 /home/sftpuser
```

## Step 4 — Give user access only to uploads directory

(The user must not own the chroot root.)

```
sudo mkdir -p /home/sftpuser/uploads
```

```
sudo chown sftpuser:sftpuser /home/sftpuser/uploads
```

```
sudo chmod 700 /home/sftpuser/uploads
```

## Step 5 — Create WordPress Uploads Bind-Mount for SFTP

This ensures files uploaded via SFTP appear correctly in WordPress.

#### Prepare directories inside chroot jail

```
sudo mkdir -p /home/sftpuser/wordpress
```
```
sudo mkdir -p /home/sftpuser/wordpress/wp-content
```
```
sudo mkdir -p /home/sftpuser/wordpress/wp-content/uploads
```

## Step 6 — Ensure real WordPress uploads directory exists

#### Location for Nginx-based WordPress:

```
sudo mkdir -p /usr/share/nginx/html/wp-content/uploads
```
```
sudo chown -R nginx:nginx /usr/share/nginx/html/wp-content/uploads
```

## Step 7 — Bind real uploads directory to SFTP uploads directory

```
sudo mount --bind /usr/share/nginx/html/wp-content/uploads /home/sftpuser/wordpress/wp-content/uploads
```

#### Make the bind-mount permanent at boot

Add this line to /etc/fstab:

```
echo '/usr/share/nginx/html/wp-content/uploads /home/sftpuser/wordpress/wp-content/uploads none bind 0 0' | sudo tee -a /etc/fstab
```

##### Important: The chroot root /home/sftpuser must be owned by root and not writable by others. Only the uploads directory (or specific subdirs) should be owned by the sftp user. We bound only uploads.

## Step 8 — Configure OpenSSH for Chrooted SFTP

#### Edit SSH config:

```
sudo nano /etc/ssh/sshd_config
```

#### Add these lines at the bottom:

```
# Enable internal SFTP subsystem
Subsystem sftp internal-sftp

# Chrooted SFTP configuration
Match User sftpuser
    ChrootDirectory /home/sftpuser
    ForceCommand internal-sftp
    PasswordAuthentication yes
    X11Forwarding no
    AllowTcpForwarding no
```

### Restart SSH Service

```
sudo systemctl restart sshd
```
## Step 9 — Harden file permissions for WordPress

### Make wp-content Writable for WordPress (Uploads, Plugins, Themes)


WordPress must write inside the wp-content/ folder to upload media, install plugins, and install themes.

```
sudo chown -R nginx:nginx /usr/share/nginx/html/wp-content
```

**✔️ What This Does:**

- Makes the NGINX web server the owner of wp-content/

- Allows WordPress to upload media + install plugins/themes

- Prevents permission errors like:
```

“Unable to create directory uploads”

“Installation failed: Could not create directory”
```

### Secure wp-config.php (Critical Security Step)

Change Ownership of wp-config.php

```
sudo chown nginx:nginx /usr/share/nginx/html/wp-config.php
```

**✔️ What This Does:**

- Makes sure the web server owns the file but…

- Only the owner and group can read it (after next command)

- Prevents unauthorized read/write

### Restrict Read Permission to Owner + Group Only

```
sudo chmod 640 /usr/share/nginx/html/wp-config.php
```

### Restrict Read Permission to Owner + Group Only (Optional)

If you want your SFTP user to upload media only, but not edit plugins/themes, then use this:

```
sudo chown -R sftpuser:sftpuser /usr/share/nginx/html/wp-content/uploads
```

**✔️ What This Does:**

- Allows SFTP user to upload images only

- Keeps security strong

- Prevents SFTP user from modifying plugins/themes


## Step 10 — Test SFTP

#### Connect using command line:

```
sftp sftpuser@<EC2-PUBLIC-IP>
```

#### List available directories:

```
ls
```
**You should see:**

```
uploads
wordpress
```

#### Test file upload:

```
put testfile.jpg
```

#### TVerify on server:

```
ls /usr/share/nginx/html/wp-content/uploads
```

**You should see testfile.jpg.**


***
### 🟦 SECTION 2 — Configure SFTP ( AWS Transfer Family)

### Step 1 — Configure AWS Transfer Family (SFTP Server)

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

### Step 2 — Create SFTP User

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

### Step 3 — Create AWS Transfer Family CONNECTOR

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

### Step 4 — Link Connector to User

#### 1️⃣ Now: Transfer Family → Servers → Select your server → Users → Edit user → Add connector

#### Choose:

```
S3 connector (the connector you created)
```

##### This makes AWS Transfer route:

```
SFTP uploads → Connector → S3 bucket
```

---

### Step 5 — Test SFTP Upload to S3

#### 1️⃣ From any SFTP client:

```
sftp -i mykey.pem wpfileadmin@s-xxxxxxxxxxxx.server.transfer.us-east-1.amazonaws.com
```

#### Inside SFTP:

```
put testfile.jpg
ls
```

##### Then check S3 → bucket → files should appear!

---

### Step 6 — Connect WordPress to S3

**Now we integrate WordPress on EC2 with S3 so WordPress uses S3 as storage.**

#### 1️⃣ Install plugin:

- **✔ “WP Offload Media Lite”**

or

- **✔ “Media Cloud”**

##### Both support S3.

#### 2️⃣ After activation → Configure:

#### Bucket:

```
my-wp-media-bucket-123
```

- **✔ Region:** Your region

- **✔ Path:** /uploads/

#### 3️⃣ IAM role:

**✔ “Add IAM Access for WordPress EC2”**

#### IAM role attached to EC2 must include:

```
AmazonS3FullAccess
```

#### or minimal:

```
s3:PutObject
s3:GetObject
s3:DeleteObject
s3:ListBucket
```

**✔ “Now ANY image uploaded in WordPress → S3.”**

**✔ “ANY SFTP upload → S3.”**

**📌 WordPress automatically reads S3 files.**

---

## 🎉 RESULT: Full Enterprise Workflow

- **✔ SFTP user uploads → S3**

- **✔ WordPress accesses → S3**

- **✔ EC2 does NOT store media**

- **✔ Storage is scalable, secure, durable**

- **✔ No OS to manage for SFTP**

- **✔ Fully serverless + scalable**


---

# 🔭 Section 4 — Infrastructure Test & Verification



# 🟦 Section 1 —  Troubleshooting quick commands


## Troubleshooting 1 — Nginx config test / restart:

```
sudo nginx -t
```

```
sudo systemctl restart nginx
```

```
sudo journalctl -u nginx -n 200
```

## Troubleshooting 2 — PHP-FPM restart & status:


```
sudo systemctl restart php-fpm
```

```
sudo systemctl status php-fpm
```

```
sudo journalctl -u php-fpm -n 200
```

## Troubleshooting 3 — Check connectivity to RDS:

```
mysql -h <RDS-ENDPOINT> -u wordpressuser -p -e "SHOW DATABASES;"
```

## Troubleshooting 4 — Tail logs:

```
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```
## Troubleshooting 5 — CloudWatch agent logs:

```
sudo tail -n 200 /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

# 🟦 Section 2 —  Verification Tests

Run these steps and record the outputs/screenshots.

## Test 1 — Web server & PHP

```
curl -I http://localhost
# Response should include HTTP/1.1 200 OK or 302 redirect to /wp-admin/install.php
php -v
nginx -v
```

## Test 2 — Database connectivity test from EC2

```
mysql -h <RDS-ENDPOINT> -u wordpressuser -p -e "SELECT USER(), CURRENT_DATE(), VERSION();"
# You should see user and server version without errors
```

## Test 3 — WordPress GUI test

Open in browser:

```
http://<EC2-PUBLIC-IP>/
```

- The WordPress site loads → run the installer if not already done.

- Login to WP Admin (/wp-admin) with credentials created earlier.

- Upload media via WP Dashboard → Media → Add New. File should appear in /usr/share/nginx/html/wp-content/uploads/... and also visible in SFTP.


## Test 4 — SFTP test (from your workstation)

```
sftp sftpuser@<EC2-PUBLIC-IP>
# then
cd wordpress/wp-content/uploads
put test-sftp.txt
ls -l
```
File should be visible in WordPress Media or at least in /usr/share/nginx/html/wp-content/uploads.

## Test 5 — CloudWatch verification

- In AWS Console → CloudWatch → Logs → confirm entries appear for:
```

wordpress-nginx-access (access logs)

wordpress-nginx-error (errors)
```

- In CloudWatch Metrics → check memory, cpu, disk metrics are being reported for your instance.

## Test 6 — Permissions & Security checks

#### Verify wp-config.php is not world-readable:

```
ls -l /usr/share/nginx/html/wp-config.php
# should be -rw-r----- (640) or similar
```

#### Verify ChrootDirectory ownership:

```
ls -ld /home/sftpuser
# should be owned by root:root and 755, /home/sftpuser/uploads owned by sftpuser
```

## Test 7 — Final functional test — upload and serve

- Upload an image file via SFTP to wordpress/wp-content/uploads/<YYYY>/<MM>/ (or uploads/).

- On WordPress admin → Media, the file should be visible (may require correct file permissions and ownership).

- Insert the image into a post and open the public page to ensure Nginx serves it.









