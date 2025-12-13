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

***

### Method 3 — EC2 User Data Script (Amazon Linux 2023)

[Wordpress EC2 User Data Script](./Wordpress_Ec2_Userdata.md)


---



# 🔭 Section 4 — Configure SFTP On AWS

## 🟦 Section 1 — Configure SFTP on AWS EC2

We will create a chrooted SFTP user sftpuser whose jail is /home/sftpuser. To allow WordPress uploads, bind-mount ONLY the wp-content/uploads directory into the chroot. This is safer than mounting full webroot.

[Configure SFTP on AWS EC2 Script](./Configure_SFTP_AWS_EC2.md)


## 🟦 SECTION 2 — Configure SFTP ( AWS Transfer Family)

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

#### 5️⃣ Generate a Valid SSH Key Pair on EC2 for AWS Transfer Family

- **Connect to Your EC2 Instance**

- **Generate SSH Key Pair on EC2**

#### ➡️ Run the following command on your EC2 instance:

```
ssh-keygen -t rsa -b 2048 -f sftp-user-key
```

###### It will ask:

```
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
```

**✔️ You can press Enter twice for no passphrase (easier for SFTP automation).**


#### This generates two files in your EC2 home directory:

```
| File                | Purpose                                            |
| ------------------- | -------------------------------------------------- |
| `sftp-user-key`     | **Private key** (Keep safe)                        |
| `sftp-user-key.pub` | **Public key** (Use in AWS Transfer Family user)** |
```


#### ➡️ View the Public Key

```
cat sftp-user-key.pub
```

##### Output looks like:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7k3.... ec2-user@ip-10-0-0-123
```

✔  This line is exactly what you must copy into the AWS Transfer Family user “SSH public key” field.

✔ It must be on one line only.

✔ Copy the entire single line

✔ No extra spaces

✔ No new lines


#### ➡️ Add the Key to AWS Transfer Family User

- **Go to Transfer Family → Servers**

- **Open your server → Users → Add user**

- **Username:**  wpadmin

- **Role:**     AWS-Transfer-SFTP-S3-Access

- **Home directory:**   /your-s3-bucket-name

- **Paste the public key from last step** 

- **Click Add user**

🎉 If SSH key format is correct, the user will create successfully.


#### ⚠️ If You Still Get a Validation Error

##### Check these common issues:

1. Key is split into 2 lines

✔️ Must be one line only.

2. Key has spaces at beginning or end

✔️ Remove extra whitespace.

3. Key is copied with wrong encoding

✔️ Paste using plain-text mode (Shift+Right Click → "Paste" in Windows terminal).



#### ➡️ Use EC2 private key to Login via SFTP on EC2

```
sftp -i sftp-user-key sftpuser@<your-transfer-server-endpoint>
```

Example:


```
sftp -i sftp-user-key wpadmin@s-03b88312fec640798.server.transfer.us-east-1.amazonaws.com
```

#### 🔐 Important Notes
- **✔ The private key stays on EC2**

###### You must download the private key from EC2 to your local computer if you want to log in from your PC.

#### ➡️ Download using SCP On your local machine:

```
scp -i your-ec2-key.pem ec2-user@<EC2-IP>:/home/ec2-user/sftp-user-key .
```

Example:


```
scp -i sftp-user-key.pub ec2-user@34.230.90.7:/home/ec2-user/sftp-user-key .
```

**✔ Your private key must not have wrong permissions**

#### ➡️ Run on your local machine:

```
chmod 600 sftp-user-key
```

#### ➡️ Test SFTP Login On your local machine:

```
sftp -i sftp-user-key sftpuser@<your-transfer-server-endpoint>
```

###### If everything is correct, you will see:

```
Connected to s-03xxxxx.server.transfer.us-east-1.amazonaws.com.
sftp>
```

##### Run this EXACT command on one line If any kind error:

```
sftp -i "C:\Users\musta\Downloads\sftp-user-key" wpadmin@s-03b88312fec640798.server.transfer.us-east-1.amazonaws.com
```

- **✔ No trailing slash**

- **✔ No new line**

- **✔ Key path in quotes**

- **✔ Everything in one line**

#### 🟢 If the key matches AWS → This will connect instantly

##### If it doesn’t connect, then:

- The private key does not match the public key uploaded to AWS Transfer Family

- Not an encoding issue anymore (because your key prints correctly)



#### ➡️ Get your SFTP details from AWS Transfer Family

##### You need four things:

- **SFTP Server Endpoint:**

Example:

```
s-03b88312fec640798.server.transfer.us-east-1.amazonaws.com
```

- **Username:** 

Example:

```
wpadmin
```

- **Private Key File (not .pub):**

Example:

```
sftp-user-key
```

Must be:

```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

- **Port:** 22


#### ➡️ Convert your private key to PPK (WinSCP format)

WinSCP cannot use an OpenSSH private key directly.
You must convert it to a PuTTY/PPK file.

#### ✔ Do this:

- **Open PuTTYgen (installed with WinSCP).**

- **Click Load**

- **Change file filter to All Files (*.*)**

- **Select your key:**

```
C:\Users\musta\Downloads\sftp-user-key
```

- **PuTTYgen will import it.**

- **Click Save private key**

- **Save as:**

```
sftp-user-key.ppk
```

This PPK file is what WinSCP will use.


#### ➡️ Configure WinSCP

- **Open WinSCP → New Site**

- **File protocol:** SFTP

- **Host name:**  s-03b88312fec640798.server.transfer.us-east-1.amazonaws.com

- **Port:** 22

- **Username:**

```
wpadmin
```

- **Password:**
(leave empty)

#### Now click:

##### 🔑 Advanced… → SSH → Authentication

- **Private key file:**

Choose:

```
C:\Users\musta\Downloads\sftp-user-key.ppk
```

- **Click OK → Save.**

- **Then click Login.**

#### 🟢 If everything is correct → You will connect instantly.

#### ❗ If it shows “Permission denied (publickey)”

##### One of these is wrong:

✔ The private key does not match the public key in AWS

Check on EC2:

```
cat ~/sftp-user-key.pub
```

##### This MUST match the key in:

- **AWS Transfer Family → Users → wpadmin → SSH Public Keys.**

- **✔ The PPK file was generated from the wrong private key**

##### You must convert the exact private key associated with that .pub.







#### ➡️ Export a REAL OpenSSH key from WinSCP / PuTTYgen

Since WinSCP can read your key, we will use it to export a valid OpenSSH key for PowerShell.

#### ✅ Open your working key in PuTTYgen

- Open PuTTYgen

- Click Load

- Change file type to All Files (*.*)

- Select the key that WinSCP connected with (could be .ppk or your original file)

#### ✅ Export an OpenSSH private key (this is the key PowerShell needs)

##### Inside PuTTYgen:

- **✔ Go to menu: Conversions → Export OpenSSH key**

##### Save file as:

```
sftp-openssh
```

##### This file will contain the correct format:

```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

##### PuTTYgen ensures:

- No BOM

- Correct LF endings

- Valid OpenSSH structure

- No corruption

- No unusual wrapping

#### ✅ Use this exported key with PowerShell SFTP

```
sftp -i "C:\Users\musta\Downloads\sftp-openssh" wpadmin@s-03b88312fec640798.server.transfer.us-east-1.amazonaws.com
```

This WILL connect successfully.

#### 🎯 Why this fixes it

- WinSCP can read multiple key formats → including PPK

- PowerShell’s built-in OpenSSH client is strict → only reads exact OpenSSH format

- Your current key file = valid for WinSCP but not valid OpenSSH formatting

- Exporting via PuTTYgen converts it to 100% correct OpenSSH structure





----

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

[Testing of Wordpress](./Troubleshooting.md)


# 🟦 Section 2 —  Verification Tests

Run these steps and record the outputs/screenshots.

[Testing of Wordpress](./Testing%20Wordpress%20Website%20With%20EC2%20%26%20RDS.md)





