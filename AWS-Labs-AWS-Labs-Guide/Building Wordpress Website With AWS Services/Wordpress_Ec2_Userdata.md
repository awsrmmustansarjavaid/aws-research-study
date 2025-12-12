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

