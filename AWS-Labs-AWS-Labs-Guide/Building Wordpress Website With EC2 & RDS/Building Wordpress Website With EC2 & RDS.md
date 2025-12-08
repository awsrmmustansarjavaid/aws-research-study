# AWS Enterprise E-Commerce Lab Guide  
## Building a WordPress Website Using EC2 + RDS MySQL (Enterprise-Ready Architecture)

---

## 1. Lab Overview

This hands-on AWS lab guides you through building a production-style WordPress architecture using:

- **Amazon EC2** → Hosts WordPress (Nginx + PHP-FPM)  
- **Amazon RDS (MySQL)** → Secure managed database  
- **Security Groups** → Controlled network access  
- **Linux + Bash** → Server configuration  

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

---

# 4. Step-by-Step WordPress Deployment

---

# Step 1 — Launch EC2 Instance

### EC2 Config:
- **AMI:** Amazon Linux 2023  
- **Instance type:** t2.micro / t3.micro  
- **Storage:** 20 GB  
- **Security Group Rules:**  
  - 22 (SSH) – Your IP  
  - 80 (HTTP) – 0.0.0.0/0  
  - 443 (HTTPS) – 0.0.0.0/0  

### Connect:

```
ssh -i yourkey.pem ec2-user@<EC2-PUBLIC-IP>
```

# Step 2 — Install Nginx, PHP-FPM & Required Packages

### Update

```
sudo dnf update -y
```

### Install Nginx

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

Adjust permissions

```
sudo usermod -a -G nginx ec2-user
```

```
sudo chown -R ec2-user:nginx /var/www
```

# Step 3 — Launch RDS MySQL

### RDS Settings

- **Engine:** MySQL 8.x

- **Instance class:** db.t3.micro

- **Public Access:** NO (private)

- **Initial DB name:** wordpressdb

- **Master User:** wpadmin

- **RDS Security Group**

- **Inbound:**

```
PORT: 3306
SOURCE: EC2-SG
```

# Step 4 — Install MySQL Client on EC2

```
sudo dnf install -y mariadb105
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

# Step 5 — Install WordPress

### Download:

```
cd /tmp
```

```
curl -O https://wordpress.org/latest.tar.gz
```

```
tar -xzf latest.tar.gz
```

### Move files to Nginx root:

```
sudo rm -rf /usr/share/nginx/html/*
```

```
sudo cp -r /tmp/wordpress/* /usr/share/nginx/html/
```

```
sudo chown -R nginx:nginx /usr/share/nginx/html
```

# Step 6 — Configure wp-config.php

### Create config:

```
cd /usr/share/nginx/html
```

```
cp wp-config-sample.php wp-config.php
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

#### Generate keys:

https://api.wordpress.org/secret-key/1.1/salt/

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

Paste into wp-config.php

# Step 7 — Configure Nginx for WordPress

### Create config:

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

# Step 8 — Start WordPress Installer


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

# 9. Security Best Practices

- EC2 in public subnet → RDS in private subnet

- Restrict DB access to EC2-SG

- Use HTTPS with Let’s Encrypt

- Store secrets in AWS Secrets Manager

- Enable automatic backups on RDS

# 10. Cost Optimization

- Use t3.micro for learning

- Stop RDS/EC2 when not needed

- Use GP3 storage

- Enable RDS AutoStop



