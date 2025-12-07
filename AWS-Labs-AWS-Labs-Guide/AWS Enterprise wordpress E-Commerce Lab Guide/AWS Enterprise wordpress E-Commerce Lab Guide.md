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


### Folder Structure

wordpress-lab/
├── index.html        ← Homepage
├── product.html      ← Product listing page
├── cart.html         ← Shopping cart page
├── checkout.html     ← Checkout page
├── login.html        ← Login page
├── css/              ← Molla CSS
├── js/               ← Molla JS + custom API integration JS
├── assets/           ← Images, fonts, icons
└── api/
    ├── products.php
    ├── cart.php
    ├── checkout.php
    └── login.php


### front-end files

#### 1. index.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    	<link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-left">
                <!-- Store Logo + Name -->
                <a href="index.html" class="logo">
                    <img src="https://cdn-icons-png.flaticon.com/512/3144/3144456.png" 
                         alt="Charlie Store" width="50" style="vertical-align: middle;">
                    <span style="font-size: 24px; font-weight: bold; margin-left: 10px;">Charlie Store</span>
                </a>
            </div>
            <div class="header-right">
                <nav>
                    <ul class="menu">
                        <li><a href="product.html">Products</a></li>
                        <li><a href="cart.html">Cart</a></li>
                        <li><a href="checkout.html">Checkout</a></li>
                        <li><a href="login.html">Login</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <main>
        <section id="featured-products">
            <h2>Featured Products</h2>
            <div id="products" class="products-grid"></div>
        </section>
    </main>

    <script src="js/app.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('api/products.php')
            .then(res => res.json())
            .then(products => {
                const container = document.getElementById('products');
                container.innerHTML = '';
                products.forEach(p => {
                    const div = document.createElement('div');
                    div.className = 'product';
                    div.innerHTML = `
                        <div class="product-media">
                            <img src="https://via.placeholder.com/200x200.png?text=${p.name}" alt="${p.name}">
                        </div>
                        <div class="product-body">
                            <h3 class="product-title">${p.name}</h3>
                            <div class="product-price">$${p.price}</div>
                            <a href="cart.html" class="btn btn-primary" onclick="addToCart(${p.id})">Add to Cart</a>
                        </div>
                    `;
                    container.appendChild(div);
                });
            });
        });
    </script>
</body>
</html>
```

#### 2. product.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Products - My Online Store</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <a href="index.html">Home</a> | <a href="cart.html">Cart</a>
    </header>

    <main>
        <h2>All Products</h2>
        <div id="products" class="products-grid"></div>
    </main>

    <script src="js/app.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('api/products.php')
            .then(res => res.json())
            .then(products => {
                const container = document.getElementById('products');
                container.innerHTML = '';
                products.forEach(p => {
                    const div = document.createElement('div');
                    div.className = 'product';
                    div.innerHTML = `
                        <h3>${p.name}</h3>
                        <p>Price: $${p.price}</p>
                        <button onclick="addToCart(${p.id})">Add to Cart</button>
                    `;
                    container.appendChild(div);
                });
            });
        });
    </script>
</body>
</html>
```

#### 3. cart.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cart - My Online Store</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <a href="index.html">Home</a> | <a href="checkout.html">Checkout</a>
    </header>

    <main>
        <h2>Your Cart</h2>
        <div id="cart" class="cart-items"></div>
        <button onclick="checkout()">Checkout</button>
        <p id="checkout-message"></p>
    </main>

    <script src="js/app.js"></script>
    <script>
        function loadCart() {
            fetch('api/cart.php')
            .then(res => res.json())
            .then(cart => {
                const container = document.getElementById('cart');
                container.innerHTML = '';
                for (const id in cart) {
                    container.innerHTML += `<p>Product ID: ${id}, Quantity: ${cart[id]}</p>`;
                }
            });
        }
        document.addEventListener('DOMContentLoaded', loadCart);
    </script>
</body>
</html>
```

#### 4. checkout.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Checkout - My Online Store</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <a href="index.html">Home</a> | <a href="cart.html">Cart</a>
    </header>

    <main>
        <h2>Checkout</h2>
        <button id="checkout-btn">Place Order</button>
        <p id="checkout-msg"></p>
    </main>

    <script src="js/app.js"></script>
    <script>
        document.getElementById('checkout-btn').addEventListener('click', function(){
            fetch('api/checkout.php', {method:'POST'})
            .then(res => res.json())
            .then(data => {
                document.getElementById('checkout-msg').innerText = data.message || data.error;
            });
        });
    </script>
</body>
</html>
```

#### 5. login.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - My Online Store</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <main>
        <h2>Login</h2>
        <form id="login-form">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p id="login-message"></p>
    </main>

    <script src="js/app.js"></script>
    <script>
        document.getElementById('login-form').addEventListener('submit', function(e){
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            fetch('api/login.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('login-message').innerText = data.message || data.error;
            });
        });
    </script>
</body>
</html>
```

#### 6. css/style.css (basic styling)

```
body { font-family: Arial, sans-serif; margin:20px; }
header { display:flex; justify-content: space-between; align-items:center; margin-bottom:20px; }
header a { margin-right:15px; text-decoration:none; color:#333; font-weight:bold; }
.products-grid { display:flex; flex-wrap:wrap; gap:15px; }
.product { border:1px solid #ccc; padding:10px; width:200px; text-align:center; }
button { padding:5px 10px; cursor:pointer; }
```

#### 7. js/app.js (all API calls)

```
// Add to Cart
function addToCart(productId){
    fetch('api/cart.php', {
        method:'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `product_id=${productId}&quantity=1`
    })
    .then(res=>res.json())
    .then(data => { alert(data.message); });
}

// Checkout
function checkout(){
    fetch('api/checkout.php', {method:'POST'})
    .then(res=>res.json())
    .then(data => { alert(data.message || data.error); });
}
```

#### ✅ Result:

* index.html → central hub with store logo + store name

* Dynamic products, cart, checkout, login integrated via JS API calls

* All other pages (product.html, cart.html, checkout.html, login.html) are ready-to-use

* CSS/JS files handle the styling and API functions



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

### WooCommerce REST API


### Create a folder /api on your EC2 WordPress server. 

##### Sample files:

#### a. products.php

```
<?php
// Example: Return list of products
require_once('wp-load.php');

header('Content-Type: application/json');

$args = array(
    'post_type' => 'product',
    'posts_per_page' => 10
);

$loop = new WP_Query($args);
$products = array();

while ($loop->have_posts()) : $loop->the_post();
    global $product;
    $products[] = array(
        'id' => $product->get_id(),
        'name' => $product->get_name(),
        'price' => $product->get_price(),
        'link' => get_permalink($product->get_id())
    );
endwhile;

echo json_encode($products);
?>
```

#### b. cart.php

```
<?php
require_once('wp-load.php');
header('Content-Type: application/json');

session_start();

$product_id = $_POST['product_id'];
$quantity = $_POST['quantity'];

if (!isset($_SESSION['cart'])) {
    $_SESSION['cart'] = array();
}

$_SESSION['cart'][$product_id] = $quantity;

echo json_encode(array('message' => 'Product added to cart', 'cart' => $_SESSION['cart']));
?>
```

#### c. checkout.php

```
<?php
require_once('wp-load.php');
header('Content-Type: application/json');

session_start();

if (!isset($_SESSION['cart']) || empty($_SESSION['cart'])) {
    echo json_encode(array('error' => 'Cart is empty'));
    exit;
}

// Here you could integrate payment gateway or order creation
$order_status = 'success';
$order_id = rand(1000, 9999); // Sample order ID

// Clear cart
$_SESSION['cart'] = array();

echo json_encode(array('message' => 'Order placed', 'order_id' => $order_id, 'status' => $order_status));
?>
```

#### d. login.php

```
<?php
require_once('wp-load.php');
header('Content-Type: application/json');

$username = $_POST['username'];
$password = $_POST['password'];

$user = wp_signon(array(
    'user_login' => $username,
    'user_password' => $password,
    'remember' => true
));

if (is_wp_error($user)) {
    echo json_encode(array('error' => $user->get_error_message()));
} else {
    echo json_encode(array('message' => 'Login successful', 'user_id' => $user->ID));
}
?>
```

#### Integration Tips

* Place all /api/*.php files in WordPress root or a /api folder.

* Use API Gateway → HTTP integration → point to http://<ALB-DNS>/api/<file>.php.

* For production lab testing, secure APIs using Cognito Authorizer.

* Update WordPress permalinks to Plain to ensure PHP API endpoints work.




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
