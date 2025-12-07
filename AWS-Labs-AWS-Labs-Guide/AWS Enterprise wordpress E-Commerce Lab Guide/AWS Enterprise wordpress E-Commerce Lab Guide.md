# AWS Enterprise E-Commerce Lab Guide

### WordPress + S3 Static Site + CloudFront + API Gateway + ALB + RDS + Cognito + Lambda Automation + Secrets Manager + CloudWatch

---

## 1. Lab Overview

This lab walks you through deploying a real enterprise-grade e-commerce architecture, combining:

* WordPress WooCommerce (Dynamic Content)
* S3 + CloudFront Static Website Hosting
* API Gateway (Login, Products, Cart, Checkout APIs)
* ALB → EC2 WordPress backend
* RDS MySQL Database
* Secrets Manager for credential security
* Cognito User Authentication
* Lambda (CloudFront Cache Invalidation Automation)
* CloudWatch + CloudTrail Monitoring & Auditing

---

---
## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Guide/AWS%20Enterprise%20wordpress%20E-Commerce%20Lab%20Guide/AWS%20Enterprise%20wordpress%20E-Commerce%20Lab%20Guide.png?raw=true)
---
___________________________________________________________________________

---


## 2. Architecture Visual Diagram (ASCII)

```
                        ┌────────────────────────┐
                        │        Clients         │
                        │  (Web / Mobile Users)  │
                        └───────────┬────────────┘
                                    │
                            ┌───────▼────────┐
                            │   CloudFront    │
                            │ (Global CDN)    │
                            └───────┬────────┘
                  ┌────────────────┼──────────────────┐
                  │                │                  │
         ┌────────▼──────┐   ┌────▼──────────┐  ┌────▼──────────┐
         │ S3 Static Site │   │  ALB (WordPress│  │ API Gateway   │
         │ (Images/HTML)  │   │   Dynamic API) │  │ Products/Login│
         └────────┬───────┘   └────┬──────────┘  └────┬──────────┘
                  │                │                  │
                  │                │                  │
         ┌────────▼──────┐   ┌────▼──────────┐   ┌───▼──────────┐
         │ CloudFront     │   │ EC2 WordPress │   │ VPC Link      │
         │ Distribution   │   │ WooCommerce   │   │ to ALB        │
         └────────┬──────┘   └────┬──────────┘   └───┬──────────┘
                  │                │                  │
            ┌─────▼────┐     ┌────▼──────┐           │
            │   S3      │     │ RDS MySQL │           │
            │ Offloaded │     │  Database │           │
            │  Media    │     └────┬──────┘           │
            └───────────┘          │                  │
                                   │                  │
                 ┌─────────────────▼──────────────────┐
                 │            Cognito                 │
                 │ (User Auth, Hosted UI, JWT Tokens)│
                 └────────────────┬───────────────────┘
                                  │
                              ┌───▼─────────┐
                              │  Lambda     │
                              │ Cache Inval │
                              └─────────────┘
```




---

## 3. Prerequisites

* AWS Admin privileges
* SSH Key Pair
* Basic WordPress knowledge
* Region: Any
* AZs: Two for HA

---

## 4. VPC & Networking Setup

1. Create VPC:

```
CIDR: 10.0.0.0/16
```

2. Create Subnets:

* Public: `10.0.1.0/24`, `10.0.2.0/24`
* Private: `10.0.3.0/24`, `10.0.4.0/24`

3. Internet Gateway → Attach to VPC

4. NAT Gateway → Public Subnet

5. Create two Route Tables

* Public → IGW
* Private → NAT GW

---

## 5. EC2 WordPress Deployment

### Launch EC2 in Private Subnet

* AMI: Amazon Linux 2023
* Type: t3.small or above
* IAM Role:

  * S3 Full Access
  * SecretsManagerReadOnly
* No public IP

### Install WordPress

```bash
sudo yum update -y
sudo yum install -y httpd php php-mysqlnd php-json php-fpm
sudo systemctl enable httpd
sudo systemctl start httpd
```

### Deploy WordPress

```bash
cd /var/www/html
sudo wget https://wordpress.org/latest.tar.gz
sudo tar -xzf latest.tar.gz
sudo mv wordpress/* .
sudo chown -R apache:apache /var/www/html
```

---

## 6. RDS MySQL Setup

1. Create RDS:

* Engine: MySQL 8
* Multi-AZ: Yes
* Private Subnets
* Security Group: allow EC2:3306

2. Create DB:

* Name: `wpdb`
* User: `wpadmin`
* Password: create random strong password

3. Store in Secrets Manager:

* Secret Name: `wp/database/credentials`

---

## 7. WordPress Integration with RDS

Edit `/var/www/html/wp-config.php`:

```php
define('DB_NAME', 'wpdb');
define('DB_USER', 'wpadmin');
define('DB_PASSWORD', '<SecretsManager>');
define('DB_HOST', '<RDS-endpoint>');
```

Optionally pull secrets using SSM init script.

---

## 8. S3 Static Site for WordPress Media

### Create S3 Bucket

* Name: `wp-static-<yourname>`
* Disable Block Public Access
* Enable Static Website Hosting

### Install Offload Media Plugin

* Go to WordPress → Plugins → Add New
* Install **WP Offload Media Lite**
* Configure S3 bucket

Uploads will now move automatically to S3.

---

## 9. CloudFront for S3 Static Site

1. Create CloudFront Distribution
2. Origin: S3 bucket
3. Origin Access Control (OAC) → Yes
4. Cache Policy → CachingOptimized
5. Default Root Object: `index.html`

---

## 10. Application Load Balancer

1. Create ALB

* Public Subnets
* SG: Allow HTTP/HTTPS

2. Create Target Group

* Target Type: Instance
* Port: 80
* Health path: `/wp-admin/install.php` or `/`

3. Register EC2 instance
4. Get ALB DNS name.

---

## 11. CloudFront for Dynamic (WordPress) Traffic

Create second CloudFront distribution:

* Origin = ALB
* Behaviors:

  * `/wp/*` → No cache
  * `/api/*` → No cache
  * `/*` → S3

---

## 12. API Gateway for WP WooCommerce APIs

### APIs to Deploy

| API      | Method | Path      | Backend              |
| -------- | ------ | --------- | -------------------- |
| Login    | POST   | /login    | WordPress endpoint   |
| Products | GET    | /products | WooCommerce REST API |
| Cart     | POST   | /cart     | WooCommerce          |
| Checkout | POST   | /checkout | WooCommerce          |

### Steps

1. Create REST API
2. Create Resources + Methods
3. Integration Type: HTTP
4. Endpoint URL = `http://<ALB-DNS>/api/...`
5. Deploy API

---

## 13. API Gateway → ALB (VPC Link)

1. Create VPC Link
2. Select private ALB
3. Use Link in Integration Request

---

## 14. Lambda — CloudFront Cache Invalidation

### Code

```python
import boto3

cf = boto3.client('cloudfront')

def lambda_handler(event, context):
    return cf.create_invalidation(
        DistributionId='YOUR_DISTRIBUTION_ID',
        InvalidationBatch={
            'Paths': {'Quantity': 1, 'Items': ['/*']},
            'CallerReference': 'invalidate-cache-001'
        }
    )
```

### Triggers

* S3 object update
* Deployment events
* WordPress media changes

---

## 15. Cognito Integration

### Steps

1. Create User Pool
2. Enable email sign-in
3. Create App Client (No Secret)
4. Enable Hosted UI
5. Add Callback URLs:

```
https://your-cloudfront-domain
```

### Secure APIs

* API Gateway → Authorizers → Cognito
* Protect `/cart` and `/checkout`

---

## 16. Monitoring & Logging

### CloudWatch

* Enable ALB Access Logs
* Enable API Gateway Logs
* Monitor:

  * EC2 CPU
  * RDS CPU + connections
  * ALB 4XX/5XX
  * Lambda errors

### CloudTrail

* Enable for entire account
* Store logs in dedicated S3 bucket
* Enable log integrity validation

---

## 17. Test & Validation

### Test Static Site

```
https://<cloudfront-s3-domain>
```

### Test WordPress Website

```
https://<cloudfront-alb-domain>/wp-admin
```

### Test APIs

```
GET https://<api-id>.execute-api.<region>.amazonaws.com/prod/products
```

### Test Cognito

* Hosted UI Login
* Get JWT token
* Call protected API

### Test Lambda Invalidation

* Upload new file to S3
* Verify CloudFront invalidates cache

---

## 18. Final Architecture Summary

This deployment includes:

✓ WordPress WooCommerce Backend
✓ S3 Static Site Frontend
✓ CloudFront Global Distribution
✓ API Gateway REST APIs
✓ ALB Dynamic Routing
✓ VPC Link integration
✓ RDS MySQL Database
✓ Cognito Secure Authentication
✓ Lambda Cache Automation
✓ Full Monitoring & Auditing
✓ Secrets Manager Credential Storage
