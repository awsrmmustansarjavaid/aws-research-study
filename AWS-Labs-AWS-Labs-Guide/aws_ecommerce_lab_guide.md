# AWS E‑Commerce Hands‑On Lab Guide

A complete step‑by‑step AWS lab scenario for deploying a **static e‑commerce website on S3 + EC2 backend + RDS MySQL database**, with full VPC, subnets, ALB, NLB (optional), NAT Gateway, and VPC Endpoints.

This Markdown file is ready for GitHub.

---

# 📌 **Lab Title**
**Multi‑AZ AWS E‑Commerce Deployment with S3 Frontend, EC2 Backend, RDS MySQL, ALB, NAT, and Endpoints**

---

# 📌 **Key Architecture Features**
- Multi‑AZ VPC (AZ‑A + AZ‑B)
- Public + Private subnets
- Route Tables and IGW
- NAT Gateway and VPC Endpoints
- Application Load Balancer (ALB)
- Auto Scaling Group (in private subnets)
- Static S3 website with CloudFront
- EC2 backend using PHP
- RDS MySQL backend DB
- S3 frontend integrated with EC2 API → EC2 connects to RDS

---
## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/0%20(Deploying%20a%20Scalable,%20Secure,%20and%20Highly%20Available%20E-Commerce%20Application%20on%20AWS).jpg?raw=true)
---
___________________________________________________________________________



------------------------------ Basic Configurations SECTION ------------------------------

# 📌 **SECTION 1 — Create VPC and Subnets**

### **1. Create VPC**
- Go to **VPC → Your VPCs → Create VPC**
- Name: `ecommerce-vpc`
- IPv4 CIDR: `10.0.0.0/16`
- Create

### **2. Create Subnets**
#### **AZ‑A**
- Public Subnet A → `10.0.1.0/24`
- Private Subnet A → `10.0.2.0/24`

#### **AZ‑B**
- Private Subnet B1 → `10.0.3.0/24`
- Private Subnet B2 → `10.0.4.0/24`

Mark **Public Subnet A** as *Auto-assign public IP = ENABLED*.

---
# 📌 **SECTION 2 — Internet Gateway & Route Tables**

### **1. Create Internet Gateway (IGW)**
- VPC → Internet Gateways → Create → Attach to `ecommerce-vpc`.

### **2. Create Route Table for Public Subnet**
- Name: `public-rt`
- Add Route: `0.0.0.0/0 → IGW`
- Associate with **Public Subnet A**

### **3. Create Route Table for Private Subnets**
- Name: `private-rt`
- No internet route (will add NAT later)
- Associate with Private Subnet A + Private Subnet B1 + B2

---
# 📌 **SECTION 3 — NAT Gateway & VPC Endpoints**

### **1. Create NAT Gateway**
- Go to NAT Gateways → Create
- Subnet: **Public Subnet A**
- Elastic IP: Allocate New
- Create

### **2. Add Route in Private Route Table**
- `0.0.0.0/0 → NAT Gateway`

### **3. Create VPC Endpoints (Optional but Recommended)**
For S3:
- Endpoint type: **Gateway**
- Service: `com.amazonaws.region.s3`
- Route tables: Only **private-rt**


# 📌 **SECTION 4  EC2 

### **1. Lauch Public EC2 (AZ-A) **
- Name: `ecommerce-Pub-EC2 

### **2. Lauch Private RDS DB EC2 (AZ-A) **
- Name: `ecommerce-RDS-BD-EC2


### **3. Add EC2 Userdata**

```
#!/bin/bash
yum update -y
yum install -y httpd php php-mysqli

# Start Apache
systemctl start httpd
systemctl enable httpd

# Create api.php with correct CORS + Database code
cat << 'EOF' > /var/www/html/api.php
<?php
// --- CORS SETTINGS ---
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Credentials: true");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// OPTIONS request for browser preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// --- Database credentials ---
$host = "ecommerce-static-site-db.cm5oowikel4z.us-east-1.rds.amazonaws.com";
$db   = "ecommerce";
$user = "admin";
$pass = "admin987";

// Connect DB
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit();
}

// Query database
$sql = "SELECT * FROM products";
$result = $conn->query($sql);

$products = [];
while ($row = $result->fetch_assoc()) {
    $products[] = $row;
}

// Return JSON
echo json_encode($products);

$conn->close();
?>
EOF

# Set proper permissions
chmod 644 /var/www/html/api.php
chown apache:apache /var/www/html/api.php

# Restart Apache to apply changes
systemctl restart httpd
```

### **2. Test EC2 Userdata**

# Check the Main Output Log
sudo cat /var/log/cloud-init-output.log

# Check the Detailed Log
sudo cat /var/log/cloud-init.log

# Test the Application Outcome
# Verify HTTPD Status:
sudo systemctl status httpd

# Verify api.php Content:
sudo cat /var/www/html/api.php

# Test the API Call (Internal Test)
# Test the script locally
curl http://localhost/api.php



------------------------------------------------------ END---------------------------------------------


-------------------------------------------------- ASG & ALB Load Balancer SECTION ----------------------



# 📌 **SECTION 1 — Application Load Balancer ALB**

1. Create ALB
- Name: `ecommerce-static-site-ALB` 
Type: Application LB

Scheme: Internet-facing

Subnets: Public Subnet A + another public subnet you create

SG: Allow HTTP 80 from anywhere

2. Target Group
- Name: `ecommerce-static-site-TG` 
Target Type: Instances

Health Check: /api.php

Add EC2 backend

3. Listener Rule

Port 80 → Forward to Target Group

Save the ALB DNS Name.


# 📌 **SECTION 2 — Auto Scaling Group (ASG)**

### **1. Create Launch Template**
- Name: `ecommerce-static-site-xyz` 
- Same EC2 configuration
- User Data (optional): Install Apache + PHP automatically

### **2. Create ASG**
- Subnets: Private A + Private B1
- Target Group: Attach to internal ALB TG
- Desired Capacity: 2
- Min: 1
- Max: 3



------------------------------------------------------ END---------------------------------------------



-------------------------------------------------- S3 Static Website SECTION ----------------------

# 📌 **SECTION 1 — S3 Static Website**

### **1. Create S3 Bucket**
- Name: `ecommerce-static-site-xyz`
- Disable Block Public Access
- Upload `index.html`
- Enable Static Website Hosting

### **2. Open Bucket Policy**
Use policy:
```
{
 "Version": "2012-10-17",
 "Statement": [{
   "Effect": "Allow",
   "Principal": "*",
   "Action": "s3:GetObject",
   "Resource": "arn:aws:s3:::ecommerce-static-site-xyz/*"
 }]
}
```

---
# 📌 **SECTION 2 — Create CloudFront for S3 & ALB API.PHP**

### **1. Create S3 Bucket Origin **
- Go to CloudFront → Create distribution 
- Name: `ecommerce-static-site-xyz` 
- Origin → S3 Static Website Endpoint
- Cache policy → CachingOptimized
- Enable HTTPS
- Viewer protocol policy → Redirect HTTP to HTTPS
- Allowed HTTP methods → GET, HEAD, OPTIONS and checkbok Cache HTTP methods → OPTIONS 
- Create invalidation → /* 
- General → Default root object - optional → index.html   
- General → IPv6 → Off  
- Create

### **2. Create ALB API.PHP Origin **

### **2.1 Add ALB as a new origin **

- Go to CloudFront → Distribution → Origins → Add origin
- Origin ID → `ALB-API-Origin` 
- Origin domain → paste your ALB DNS: demo-alb-1270704550.us-east-1.elb.amazonaws.com
- Protocol → HTTP only (since your ALB is HTTP)
- Save

### **2.2 Create a new Behavior for API path **

- Go to CloudFront → Behaviors → Create Behavior
- Path pattern → /api.php 
- Origin → Select the ALB origin you just created
- Allowed methods → GET, HEAD, OPTIONS
- Cache policy → CachingDisabled (recommended for APIs)
- Origin request policy → AllViewerExceptHostHeader
- Viewer Protocol Policy → HTTP ONLY (because ALB is HTTP)
- Save  

### **2.3 Add ALB as a new origin **
- Go to CloudFront → Invalidations → Create invalidation
- add path → /* 
- add path → /api.php

Save the **CloudFront URL**.

------------------------------------------------------ END---------------------------------------------



-------------------------------------------------- RDS MySQL Database SECTION ----------------------


# 📌 **SECTION 1 — RDS MySQL Database**

### **1. Create Subnet Group**
- Include Private Subnet A + Private Subnet B1

### **2. Create RDS Instance**
- Name: `ecommerce-static-site-DB` 
- Engine: MySQL
- Free Tier: `db.t3.micro`
- Multi-AZ: Enabled (if budget allows)
- Public Access: **NO**
- Credentials: root / password
- VPC Security Group → Allow MySQL port 3306 only from EC2 SG

### **3. Create Table**
Run in RDS Query Editor or EC2:

```
sudo dnf update -y

sudo dnf install mariadb105 -y

mysql --version

mysql -h ecommerce-static-site-db.cm5oowikel4z.us-east-1.rds.amazonaws.com -u admin -p

SHOW DATABASES;

CREATE DATABASE ecommerce;
USE ecommerce;

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  price DECIMAL(10,2),
  description TEXT
);

INSERT INTO products (name, price, description) VALUES
 ('Laptop', 1200.00, 'Good laptop'),
 ('Phone', 800.00, 'Smartphone');


SHOW TABLES;

SELECT * FROM products;
```

------------------------------------------------------ END---------------------------------------------




------------------ Integrating Static S3 E-Commerce Site with RDS via EC2 Backend (PHP API) SECTION ------------------


### **1. Launch EC2 Instance**
- AMI: Amazon Linux 2
- Type: t2.micro
- Subnet: **Private Subnet A**
- Auto-assign Public IP: No
- SG: Allow port 80 from ALB only

### **2. Install Backend Requirements**
SSH from Bastion or SSM:
```
sudo yum update -y
sudo dnf install httpd -y
sudo systemctl enable httpd
sudo systemctl start httpd
sudo dnf install php php-mysqli php-json -y
sudo systemctl restart httpd
```

### **3. Upload Backend File**
Upload `api.php` into:
```
Go to Apache directory
cd /var/www/html
sudo nano api.php


<?php
// --- CORS SETTINGS ---
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// OPTIONS request for browser preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// --- Database credentials ---
$host = "demo-rds-db.cm5oowikel4z.us-east-1.rds.amazonaws.com";
$db   = "ecommerce";
$user = "admin";
$pass = "admin987";

// Connect DB
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit();
}

// Query database
$sql = "SELECT * FROM products";
$result = $conn->query($sql);

$products = [];
while ($row = $result->fetch_assoc()) {
    $products[] = $row;
}

// Return JSON
echo json_encode($products);

$conn->close();
?>
```

### **4.Save the file → restart Apache
sudo systemctl restart httpd

### **5.Test the API (Use curl inside EC2:)
curl http://localhost/api.php

_____________ Note _________________________
If you see: 

[{"id":1,"name":"Laptop","price":"1200.00","image":"laptop.png"}, ...]

Then API is working!
________________________________________________


### **6. ALB Routing (If needed) Test**
If your static site calls:
curl http://demo-alb-1270704550.us-east-1.elb.amazonaws.com/api.php



### **7. Connect Front-End (S3) to EC2 Backend**

# Access S3 from the CLI List all buckets (if the IAM role allows it)
aws s3 ls

# List contents of a specific bucket
aws s3 ls s3://ecommerce-static-site-xyz/

# Access and Download the File
aws s3 cp s3://ecommerce-static-site-xyz/index.html ./

# View the File Content
cat index.html

# Edit the File Locally
nano index.html

# Upload the Updated File
aws s3 cp index.html s3://ecommerce-static-site-xyz/index.html

# Static S3 site will call EC2 API using JavaScript (AJAX/Fetch) in index.html:
Add below JavaScript in index.html 

<script>
async function loadProducts() {
  const res = await fetch('http://demo-alb-1270704550.us-east-1.elb.amazonaws.com/api.php'); // Use ALB DNS
  const products = await res.json();
  console.log(products);
  // Render products on page
}
loadProducts();
</script>


Note: Replace http://ALB-DNS with your Application Load Balancer public DNS that points to EC2 backend.

------------------------------------------------------ END---------------------------------------------



------------------ Final Lab Test Section ------------------

### **1. CloudFront Loads S3 Website

✔ CloudFront URL opens
✔ Shows “result as per index.html”

➡ This confirms:

S3 static hosting is correct

CloudFront distribution working

Permissions + OAC working

Status: PASS


### **2. EC2 Backend API Works Locally

curl http://localhost/api.php

Output: [{"id":"1","name":"Laptop"...}]

This proves:

Apache/PHP installed correctly

api.php scripted correctly

EC2 can connect to RDS

Security groups between EC2 → RDS working

Status: PASS

### **3. ALB & CloudFront Public DNS Returns API Output

curl http://ecommerce-static-site-ALB-1602237105.us-east-1.elb.amazonaws.com/api.php
curl -I http://ecommerce-static-site-ALB-1602237105.us-east-1.elb.amazonaws.com/api.php

You MUST see:

HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Content-Type: application/json

If this test returns 200 OK →
CloudFront → S3 → JS Fetch → ALB → EC2 → RDS will work.


Test in your browser
http://ecommerce-static-site-ALB-1602237105.us-east-1.elb.amazonaws.com/api.php

And got:
[{"id":"1","name":"Laptop"...}]

Then press F12 → Network → api.php → Headers

You MUST see:

Access-Control-Allow-Origin: *

If not → the file did not update, and I will help you locate the correct path.


https://d38zya3b3h11cl.cloudfront.net/api.php

And got:
[{"id":"1","name":"Laptop"...}]

Then press F12 → Network → api.php → Headers

You MUST see:

Access-Control-Allow-Origin: *
x-cache : Miss from cloudfront


If not → the file did not update, and I will help you locate the correct path.



This confirms:

ALB listener works

Target group healthy

ALB → EC2 routing correct

EC2 subnet private networking correct

Status: PASS

### **4. CloudFront Website Must Call ALB API via JavaScript
Right now your setup is working backend only.

But to call the API from frontend, you need:

1️⃣ Correct API URL in index.html

Example:
fetch("https://demo-alb-123456.elb.amazonaws.com/api.php")
  .then(res => res.json())
  .then(data => console.log(data));

CORS enabled on ALB / EC2
In api.php:
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

If you don’t add CORS, CloudFront → ALB request will be blocked.
Test it in browser console:
Open CloudFront URL → Press F12 → Console → run:
fetch('/api.php')

If you get JSON → PASS
If you get CORS error → FIX IT.

### **5. Health Checks on ALB Target Group
EC2 Console → Target Groups → Your-TG → Targets
You must see:
Status = healthy
Both AZ EC2 instances = healthy
If any instance is unhealthy → your architecture is not fully correct.

### **6. Security Group Validation
Your SGs must be:

ALB SG

Allow inbound 80 or 443 from 0.0.0.0/0

Allow outbound to EC2 SG

EC2 SG

Allow inbound from ALB SG only

Allow outbound to RDS SG only

RDS SG

Allow inbound 3306 from EC2 SG only

If SGs allow 0.0.0.0 → WRONG (security issue).


### **7. Private Subnet Isolation Check
Your EC2 instance must NOT be accessible from internet:

Test:

curl http://<EC2-public-IP>/api.php


Expected:

❌ Should NOT work
✔ Only ALB should access EC2

If direct EC2 access succeeds → EC2 is in public subnet → WRONG.


sudo systemctl restart httpd
sudo tail -f /var/log/httpd/access_log
sudo systemctl status httpd
sudo systemctl start httpd

ls -l /var/www/html/api.php
curl -I http://localhost/api.php
------------------------------------------------------ END---------------------------------------------



------------------ Template File Content Files SECTION ------------------


### **1. index.html (S3 Frontend)**
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    
    <title>🛍️ Charlie's Store | AWS Demo</title>

    <style>
        /* --- General Body and Typography --- */
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f4f7f6; /* Light gray background */
            color: #333;
            margin: 0;
            padding: 0;
            text-align: center;
        }

        /* --- Header Styling --- */
        header {
            background-color: #007bff; /* Vibrant Blue */
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }

        h1 {
            font-weight: 700;
            font-size: 2.5em;
            margin: 0;
        }

        /* --- Loading State --- */
        .loading {
            color: #007bff;
            font-weight: 600;
            padding: 20px;
        }

        /* --- Products Grid/Layout --- */
        #products {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 25px;
            padding: 0 20px;
        }

        /* --- Individual Product Card --- */
        .product-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            padding: 25px;
            width: 300px;
            text-align: left;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 5px solid #ffc107; /* Gold accent line */
        }

        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
        }

        .product-card h3 {
            color: #333;
            font-weight: 600;
            margin-top: 0;
            border-bottom: 1px dashed #ccc;
            padding-bottom: 10px;
        }

        .product-card .price {
            color: #28a745; /* Green for price */
            font-size: 1.4em;
            font-weight: 700;
            margin: 10px 0;
        }

        .error-message {
            color: #dc3545; /* Red for errors */
            font-weight: 600;
            padding: 20px;
            background-color: #ffebeb;
            border: 1px solid #dc3545;
            border-radius: 5px;
            margin: 20px auto;
            max-width: 600px;
        }
    </style>
</head>
<body>

<header>
    <h1><i class="fas fa-store"></i> Charlie's Store</h1>
</header>

<p id="loading-message" class="loading">Loading products...</p>

<div id="products"></div>

<script>
    // 🔥 Paste your ALB DNS here:
    // IMPORTANT: Use the CloudFront URL in production!
    const API_URL = "https://d38zya3b3h11cl.cloudfront.net/api.php";
    const productsDiv = document.getElementById("products");
    const loadingMessage = document.getElementById("loading-message");

    async function loadProducts() {
        try {
            // 1. Fetch data
            const response = await fetch(API_URL);
            
            // Check for HTTP errors (e.g., 404, 500)
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();

            // 2. Hide loading message
            loadingMessage.style.display = 'none';

            // 3. Build HTML
            let html = "";
            data.forEach(item => {
                // Using the new 'product-card' class for styling
                html += `<div class="product-card">
                            <h3>${item.name}</h3>
                            <p class="price">$${item.price}</p>
                            <p>${item.description}</p>
                        </div>`;
            });

            productsDiv.innerHTML = html;

        } catch (error) {
            // 4. Handle API failure
            loadingMessage.style.display = 'none'; // Hide loading message
            
            productsDiv.innerHTML =
                `<div class="error-message">
                    <p>API Request Failed! The issue is likely a **CORS** error or **Network connectivity** (ALB/CloudFront). Please check your browser console for details.</p>
                </div>`;
            
            console.error("Product loading error:", error);
        }
    }

    // A small delay to make the "Loading" state more visible
    setTimeout(loadProducts, 500); 
</script>

</body>
</html>
```
------------

### **2. api.php (EC2 Backend)**
```
<?php
// --- CORS SETTINGS ---
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// OPTIONS request for browser preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// --- Database credentials ---
$host = "ecommerce-static-site-db.cm5oowikel4z.us-east-1.rds.amazonaws.com";
$db   = "ecommerce";
$user = "admin";
$pass = "admin987";

// Connect DB
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit();
}

// Query database
$sql = "SELECT * FROM products";
$result = $conn->query($sql);

$products = [];
while ($row = $result->fetch_assoc()) {
    $products[] = $row;
}

// Return JSON
echo json_encode($products);

$conn->close();
?>
```

------------------------------------------------------ END---------------------------------------------
---



