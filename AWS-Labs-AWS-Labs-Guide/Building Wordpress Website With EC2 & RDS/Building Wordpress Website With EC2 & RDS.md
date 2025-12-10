# AWS Hands-on Lab Guide 

## ✅ AWS Wordpress Configuration Lab Guide (EC2 + WordPress + RDS & SFTP) Architecture


### Architecture Designer: Charlie

---

## 1. Lab Overview

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

## 2. AWS Architecture Diagram

![WordPress on EC2 + RDS Diagram](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Guide/Building%20Wordpress%20Website%20With%20EC2%20&%20RDS/Building%20Wordpress%20Website%20With%20EC2%20&%20RDS.png?raw=true)

---

## 3. Architecture Flow

1. User → EC2 (Nginx + PHP-FPM)  
2. EC2 → Amazon RDS (MySQL database)  
3. EC2 security group allows HTTP/HTTPS  
4. RDS security group allows port **3306 only from EC2-SG**  
5. SFTP → Wordpress

---

# 4. Step-by-Step WordPress Deployment

---

# Section 1 — IAM Role and Policies

## Step 1  Create IAM Role for EC2

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


---


# Section 2 — Launch EC2 Instance

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


#### Update

```
sudo dnf update -y
```

#### Install & Start Apache

```
sudo yum install httpd -y
```

```
sudo systemctl start httpd
```

```
sudo systemctl enable httpd
```

#### Now test in browser:

```
http://YOUR_PUBLIC_IP
```

**You should see Apache test page ✅**

#### Fix Permissions (Very Important for WordPress)

```
sudo chown -R apache:apache /var/www/html
```

```
sudo chmod -R 755 /var/www
```

#### Install PHP for WordPress

```
sudo yum install php php-mysqlnd php-fpm -y
```

```
sudo systemctl restart httpd
```

#### Confirm Security Group

**Make sure your EC2 Security Group has:**

```
✅ HTTP – Port 80 – 0.0.0.0/0
✅ HTTPS – Port 443 – 0.0.0.0/0 (optional)
```

#### WordPress Directory

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
sudo cp -r wordpress/* /var/www/html/
```

#### Set permissions

```
sudo chown -R apache:apache /var/www/html
```

```
sudo chmod -R 755 /var/www
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

#### Check Your Web Directory

```
ls -lah /var/www/html
```



***


### Method 2 — Install Nginx, PHP-FPM & Required Packages


#### Update

```
sudo dnf update -y
```

#### Install Nginx

```
sudo dnf install -y nginx
```

```
sudo systemctl enable --now nginx
```

### Install PHP + Extensions

```
sudo dnf install -y php php-fpm php-mysqlnd php-gd php-json php-xml php-mbstring php-opcache php-cli
```

### Enable PHP-FPM

```
sudo systemctl enable --now php-fpm
```

### Prepare web root & permissions

We will serve WordPress from /usr/share/nginx/html.

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

## Step 4 — Download and install the CloudWatch agent package (Amazon Linux 2023)

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

# Section 3 — Launch RDS MySQL

## Step 1 — RDS Recommended Settings

- **Engine:** MySQL 8.x

- **Instance class:** db.t3.micro

- **Storage:** 20 GB

- **Public Access:** NO (private)

- **Initial DB name:** wordpressdb (or wordpressdb)

- **Master User:** wpadmin

- **Master Password:** store securely

- **RDS Security Group** 

- **Inbound:**

```
rds-db-sg that allows 3306 from web-server-sg
```

## Step 2 — Install MySQL Client on EC2

```
sudo dnf install -y mariadb105
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
exit
```
##### Note: Use a strong password and store it securely (Secrets Manager recommended for production).


---

# Section 4 — Install WordPress

## Step 1 — Download:

```
cd /tmp
```

```
curl -O https://wordpress.org/latest.tar.gz
```

```
tar -xzf latest.tar.gz
```

## Step 2 — Move files to Nginx root:

```
sudo rm -rf /usr/share/nginx/html/*
```

```
sudo cp -r /tmp/wordpress/* /usr/share/nginx/html/
```

```
sudo chown -R nginx:nginx /usr/share/nginx/html
```

```
sudo find /usr/share/nginx/html -type d -exec chmod 755 {} \;
```

```
sudo find /usr/share/nginx/html -type f -exec chmod 644 {} \;
```



## Step 3 — Configure wp-config.php

### Create config:

```
cd /usr/share/nginx/html
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


---

# Section 5 — Configure Nginx for WordPress

## Step 1 — Create config:

#### Method : 1

```
sudo nano /etc/nginx/conf.d/wordpress.conf
```


### Paste:

```
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include /etc/nginx/fastcgi.conf;
        fastcgi_pass unix:/run/php-fpm/www.sock;
    }

    location ~ /\.ht {
        deny all;
    }
}
```


### Test & Restart:

```
sudo nginx -t
```

```
sudo systemctl restart nginx
```

#### Method : 2

```
sudo tee /etc/nginx/conf.d/wordpress.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.php index.html index.htm;

    client_max_body_size 50M;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include /etc/nginx/fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_index index.php;
        # php-fpm socket (default on Amazon Linux 2023)
        fastcgi_pass unix:/run/php-fpm/www.sock;
    }

    location ~ /\.ht {
        deny all;
    }

    # Deny access to wp-config.php
    location = /wp-config.php {
        deny all;
    }
}
EOF

# test nginx config and restart
sudo nginx -t && sudo systemctl restart nginx
```



## Step 2 — Start WordPress Installer


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

# Section 6 —  Configure SFTP on AWS EC2  WordPress

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

#### Add them to Apache group:

```
sudo usermod -aG apache sftpuser
```

## Step 3 — Create Upload Directory

```
sudo mkdir -p /var/www/html/uploads
```

```
sudo chown sftpuser:apache /var/www/html/uploads
```

```
sudo chmod 755 /var/www/html/uploads
```

## Step 4 — Configure SSH for SFTP-only Access

**Edit SSH config:**

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


### Check sftpuser shell

```
grep sftpuser /etc/passwd
```

###### You MUST see:

```
sftpuser:x:1001:1001::/home/sftpuser:/usr/sbin/nologin
```

###### If NOT, set it:

```
sudo usermod -s /usr/sbin/nologin sftpuser
```

###### OR:

```
sudo usermod -s /bin/false sftpuser
```

## Step 6 — Fix for Chroot

Chroot directory must be owned by root, not the user.

```
sudo chown root:root /var/www
```

or 

```
sudo chown root:root /home/sftpuser
```

```
sudo chmod 755 /var/www
```
or

```
sudo chmod 755 /home/sftpuser
```


**Then fix inside directory:**

```
sudo chown -R sftpuser:apache /var/www/html/uploads
```

or

```
sudo mkdir -p /home/sftpuser/upload
```

```
sudo chown sftpuser:sftpuser /home/sftpuser/upload
```






## Step 7 — Restart SSH

```
sudo systemctl restart sshd
```

## Step 8 — Open Security Group

- In AWS → EC2 → Security Group:

```
✅ Allow Port 22 (SSH/SFTP)
Source: 0.0.0.0/0 or your IP
```


## Step 9 — Test SFTP from Local Machine

**From your local PC:**

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


---

# Section 7 —  Troubleshooting quick commands


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

# Section 8 —  Verification Tests

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






