# 🌍 AWS Hands-on Lab: Global Static Website Deployment with S3, CloudFront, Global Accelerator, and ALB

## 🧩 Overview

In this lab, you will design and deploy a globally distributed static
website architecture integrating multiple AWS services for speed,
scalability, and global reach.

### Services Used

-   **Amazon S3** -- Static website hosting.
-   **Amazon CloudFront** -- Content Delivery Network (CDN) for global
    caching and delivery.
-   **Application Load Balancer (ALB)** -- Load balancing across EC2
    instances.
-   **AWS Global Accelerator** -- Network-level acceleration for global
    traffic optimization.

------------------------------------------------------------------------

## 🪜 Step-by-Step Implementation

### Phase 1 -- Create and Configure the Static Website on S3

1.  Create an S3 bucket (e.g., `my-global-static-site-lab`).
2.  Disable "Block all public access" for testing.
3.  Upload website files (`index.html`, `error.html`).
4.  Enable **Static website hosting**:
    -   Index document: `index.html`
    -   Error document: `error.html`
5.  Note the **S3 website endpoint URL**.

------------------------------------------------------------------------

### Phase 2 -- Distribute via Amazon CloudFront

1.  Go to **CloudFront** → Create Distribution.
2.  Choose your S3 bucket as the **origin**.
3.  Viewer Protocol Policy: Redirect HTTP to HTTPS.
4.  (Optional) Add custom domain and SSL certificate via ACM.
5.  Deploy and test your CloudFront URL.

✅ Result: Your static site is now globally cached and delivered with
low latency.

------------------------------------------------------------------------

### Phase 3 -- Create an Application Load Balancer (ALB)

1.  Launch **2 EC2 instances** in different Availability Zones.

    ``` bash
    #!/bin/bash
    yum update -y
    yum install -y httpd
    echo "<h1>Hello from $(hostname -f)</h1>" > /var/www/html/index.html
    systemctl start httpd
    systemctl enable httpd
    ```

2.  Create a **Target Group** and register both EC2 instances.

3.  Create an **Application Load Balancer**:

    -   Internet-facing
    -   Public subnets
    -   Forward to your target group

4.  Test the ALB DNS endpoint.

✅ Result: Load-balanced, fault-tolerant backend is online.

------------------------------------------------------------------------

### Phase 4 -- Create AWS Global Accelerator

1.  Open **Global Accelerator** → Create Accelerator.
2.  Add listener (port 80 or 443).
3.  Add endpoint group (region same as ALB).
4.  Add **ALB** as endpoint.
5.  Deploy --- note your **two static Anycast IPs**.

✅ Result: Global users are now routed over AWS's global backbone to
your ALB.

------------------------------------------------------------------------

### Phase 5 -- Integrate and Test

You can now test three routes: - S3 Website Endpoint → Direct bucket
access - CloudFront → CDN delivery - Global Accelerator + ALB →
Optimized backend traffic

(Optional) Use **Route 53** for domain mapping: - `www.example.com` →
CloudFront - `api.example.com` → Global Accelerator

------------------------------------------------------------------------

## 💡 What You Learned

-   Hosting static websites using **Amazon S3**.
-   Accelerating content via **CloudFront CDN**.
-   Ensuring high availability with **ALB and EC2**.
-   Reducing latency globally with **AWS Global Accelerator**.
-   The difference between **application-layer (CDN)** and
    **network-layer (Accelerator)** optimization.

------------------------------------------------------------------------

## 📘 LinkedIn Post Example

> 🚀 Completed an advanced AWS hands-on lab integrating **S3 Static
> Hosting**, **CloudFront CDN**, and **Global Accelerator with ALB** to
> build a globally optimized, highly available web application
> architecture.
>
> Learned how AWS services enhance performance and resilience through
> intelligent routing and caching across global networks.

**#AWS #CloudComputing #S3 #CloudFront #GlobalAccelerator
#ApplicationLoadBalancer #CloudEngineer #Networking #TechLab
#HandsOnAWS**

------------------------------------------------------------------------
