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
- Auto Scaling Group (in private subnets) with Lambda function
- Static S3 website with CloudFront
- EC2 backend using PHP
- RDS MySQL backend DB
- S3 frontend integrated with EC2 API → EC2 connects to RDS

---
## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/Highly%20Available,%20Scheduled,%203-Tier%20E-Commerce%20Architecture.jpg?raw=true)
---
___________________________________________________________________________

---

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

---

# 📌 SECTION 4  EC2 

### **1. Lauch Public EC2 (AZ-A)**
- Name: `ecommerce-Pub-EC2 

### **2. Lauch Private RDS DB EC2 (AZ-A)**
- Name: `ecommerce-RDS-BD-EC2


### **3. Add EC2 Userdata**

### **1. UserData For EC2 Info**
```
#!/bin/bash
# Update and install required packages
yum update -y
yum install -y httpd awscli jq

# Start Apache
systemctl start httpd
systemctl enable httpd

# Metadata token
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" -s)

# Basic metadata
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)
PRIVATE_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4)
AZ=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=$(echo "$AZ" | sed 's/[a-z]$//')

# Wait for IAM role credentials
echo "Waiting for IAM role credentials..."
for i in {1..10}; do
  aws sts get-caller-identity --region "$REGION" >/tmp/awsid.json 2>/dev/null && break
  sleep 5
done

# Retrieve VPC ID
VPC_ID=$(aws ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --region "$REGION" \
  --query "Reservations[0].Instances[0].VpcId" \
  --output text 2>/dev/null)

# Retrieve VPC Name tag (if any)
VPC_NAME=$(aws ec2 describe-vpcs \
  --vpc-ids "$VPC_ID" \
  --region "$REGION" \
  --query "Vpcs[0].Tags[?Key=='Name'].Value | [0]" \
  --output text 2>/dev/null)

# Handle missing info
if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
  VPC_ID="Unavailable"
fi
if [ -z "$VPC_NAME" ] || [ "$VPC_NAME" == "None" ]; then
  VPC_NAME="No Name Tag"
fi

# Current date and time
CURRENT_DATE=$(date)

# Create webpage
cat <<EOF > /var/www/html/index.html
<html>
  <head>
    <title>AWS Apache Web Server</title>
  </head>
  <body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h1>AWS Apache Web Server Status</h1>
    <p><strong>Instance ID:</strong> $INSTANCE_ID</p>
    <p><strong>Private IP Address:</strong> $PRIVATE_IP</p>
    <p><strong>Public IP Address:</strong> $PUBLIC_IP</p>
    <p><strong>Availability Zone:</strong> $AZ</p>
    <p><strong>Region:</strong> $REGION</p>
    <p><strong>VPC ID:</strong> $VPC_ID</p>
    <p><strong>VPC Name:</strong> $VPC_NAME</p>
    <p><strong>Current Date & Time:</strong> $CURRENT_DATE</p>
    <hr>
     <p style="color: gray;"><strong> Generated by EC2 user data script (Charlie)</strong></p>
  </body>
</html>
EOF
```
### **2. UserData For API.PHP**
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

# Set proper permissions
```
chmod 644 /var/www/html/api.php
chown apache:apache /var/www/html/api.php
```

# Restart Apache to apply changes
```
systemctl restart httpd
```

# Check the Main Output Log
```
sudo cat /var/log/cloud-init-output.log
```

# Check the Detailed Log
```
sudo cat /var/log/cloud-init.log
```

# Test the Application Outcome
# Verify HTTPD Status:
```
sudo systemctl status httpd
```

# Verify api.php Content:
```
sudo cat /var/www/html/api.php
```

# Test the API Call (Internal Test)
# Test the script locally
```
curl http://localhost/api.php
```
------------------------------------------------------------------------

# 🎉 END OF Task

# 📌 **SECTION 1 — Public Application Load Balancer ALB**

##  **Step 1 — Public Application Load Balancer ALB**

### **1. Create ALB**
- Name: `ecommerce-Public-ALB` 
- Type: Application LB
- Scheme: Internet-facing
- Subnets: Public Subnet A + another public subnet you create
- SG: Allow HTTP 80 from anywhere




### **2. Target Group**
- Name: `ecommerce-Public-TG` 
- Target Type: Instances
- Health Check: /api.php
- Add EC2 backend

### **3. Listener Rule**

- Port 80 → Forward to Target Group
- Save the ALB DNS Name.


##  **Step 2 — Private Application Load Balancer ALB**

### **1. Create Public ALB**
- Name: `ecommerce-Priavte-ALB` 
- Type: Application LB
- Scheme: internal
- Subnets: Priavte Subnet A + another pPriavte subnet B you create
- SG: Allow HTTP 80 from anywhere

### **2. Target Group**
- Name: `ecommerce-Private-TG` 
- Target Type: Instances
- Health Check: /api.php
- Add EC2 backend

### **3. Listener Rule**

- Port 80 → Forward to Target Group
- Save the ALB DNS Name.

# 📌 **SECTION 2 — Create a Cognito User Pool (Authentication)**
### Console Method

## STEP 1:  IAM ROLE

### ✅ IAM ROLE 1 — Lambda Execution Role

#### Create IAM Role for Lambda

* **Console → IAM → Roles → Create Role**

* **Trusted entity** → AWS service

* **Service** → Lambda

* **Attach policy:**

    * **AWSLambdaBasicExecutionRole**

➡ This allows Lambda to write logs to CloudWatch.

* **Name it:** LambdaBasicExecutionRole  

##### ✔ Lambda Execution Role — Inline Policy (optional but recommended)

* If you want to add more permissions later, here is the minimal logging policy:

    * **Policy: LambdaBasicLogging.json**

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}

```
**🎯 Final Lambda Trust Policy**

* Lambda automatically gets this trust policy:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

```
---

## STEP 2:  Create a Lambda Function

* **Go to Lambda → Create function**

* **Name:** demo-api-lambda

* **Runtime:** Python 3.12

* **Insert code:**

```
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": "🎉 Hello! API is working."
    }

```
* Click Deploy

**Result**

* Backend service ready

#### ✅ 1. Test the Lambda Function (Manual Test in Console)

* **Go to AWS Console → Lambda → demo-api-lambda**

* On the top-right, click Test

**If this is the first test:**

* Click **"Create new test event"**

* **Event name:** testEvent

* **Leave default JSON:**

```
{
  "key": "value"
}

```

* Click Save → Test

**Expected Output:**

###### You should see:

```
StatusCode: 200
{
  "statusCode": 200,
  "body": "🎉 Hello! API is working."
}
```


###### This confirms the function is working.

#### ✅ 2. Add Environment Variables

* **Open your Lambda function: demo-api-lambda**

* Scroll down to Environment variables

* Click Edit

* Add variables,

* **variable # 1**

**Key :** 

```
APP_NAME
```

**Value :** 

```
demo-api
```

* **variable # 2**

**Key :** 
```
STAGE
```
**Value :** 

```
dev
```

* **variable # 3**

**Key :** 
```
DB_HOST
```
**Value :** 

```
mydb.us-east-1.rds.amazonaws.com
```

* Click Save


---

## STEP 3: Create a Cognito User Pool (Authentication)

* **Go to Amazon Cognito → User Pools → Create User Pool**

**Choose:**

*  **Application type :** Traditional web application

*  **Name your application :** demolab

*  **Self-registration:** Enable self-registration

*  **Required attributes for sign-up :** email.

* **Keep defaults → Create User Pool**

**You do not need Return URL for this lab.**

* **Go to Users → Create user**

    * **Username:** testuser

    * **Temporary password:** Test@1234

**Result**

* A working Cognito User Pool

* A test user created

### Enable “USER_PASSWORD_AUTH” for the App Client

* **Console → Go to Cognito → User Pools**

* **Go to "App clients" or "App integration"**

* **Go to "App clients" or "App integration"**

###### (Depending on old or new console)

* **Click: Edit App Client Settings"**

###### Now enable these:

* **Authentication flows**

#### Turn ON:

* ✔️ USER_PASSWORD_AUTH

* ✔️ ALLOW_USER_PASSWORD_AUTH

* ✔️ ALLOW_REFRESH_TOKEN_AUTH

* ✔️ ALLOW_ADMIN_USER_PASSWORD_AUTH (optional)

###### In old UI, the option is:

* ✔️ Enable username/password auth for Admin and User

#### Secret-based Auth checkbox

###### If your app client has a client secret → YOU MUST ALSO enable:

* ✔️ Enable SRP (Secure Remote Password)
###### (needed for USER_PASSWORD_AUTH when using a secret)

* Save Changes



---



---
# 📌 SECTION 3 — Create API Gateway (Cognito Protected API)

* **Go to API Gateway**

* **Create** → HTTP API

* **Add integration** → Lambda

* **Choose your Lambda function**

#### ✅ ADD Route

* **Click Add route**

**Choose:**

* **Method → ANY or GET**

* **Path → / or /auth**

* **Select Integration: Lambda (your lambda)**

#### ✅ Define Stages

* Stages = deployment versions for HTTP API.

**Choose:**

* **Default stage: Enabled**

* **Stage name: $default**

* Keep everything default.

* Click Next
* Click Create

#### ✅ In Authorization: 

**choose:**

**Add Authorizer**

* **Name:** CognitoAuth

* **Type:** JWT authorizer

* **Identity Source:** $request.header.Authorization

* **Issuer URL:**

**Select the User Pool created in Step 1**

```
https://cognito-idp.YOUR-REGION.amazonaws.com/YOUR_USER_POOL_ID
```

**Select the User Pool created in Step 1**
    
* **Audience:**

    **→ Enter the App Client ID (from Cognito)**

* Click Create and Attach Authorizer.

* Attach Authorizer to / route

#### 🎉 Test: Your HTTP API is now deployed

##### After creation:

**You will see: Invoke URL**

```
https://abcd1234.execute-api.us-east-1.amazonaws.com
```

#### Add your route:

```
https://<your gateway api invoke url>/<your route>
```

#### 🔥 Test the API

* Open your browser or use curl:

* **Test via browser:**

```
https://<your gateway api invoke url>/<your route>
```
> **If you open this API in browser → Unauthorized (401)**

**Good! It means the API is protected.**


* **Test via CLI:**

```
curl https://<your gateway api invoke url>/<your route>
```

**You should receive:**

```
{
  "statusCode": 200,
  "body": "🎉 Hello! API is working."
}
```

### 🛑 IMPORTANT — IAM Permission for API Gateway → Lambda

**API Gateway must have permission to invoke your Lambda.**

* **Go to your Lambda → Permissions → Resource-based policy**

**You should see something like:**

```
{
  "Effect": "Allow",
  "Principal": {
    "Service": "apigateway.amazonaws.com"
  },
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:us-east-1:<account-id>:function:api-lab-lambda"
}
```

**If not → API Gateway will fail with 500.**

---

# 📌 **SECTION 4 — Generate Access Token to Call API**

**AWS CLI required on EC2 or AWS CLI APP.**

*  Install AWS CLI

> **(Linux/macOS/Windows)**

#### Run command:

*  **Make Sure EC2 has AWS CLI Installed**

```
aws --version
```
If not installed:

```
sudo yum install -y awscli
```
#### 🟦 STEP 1 — You MUST Know 3 Things From Cognito

**From your Cognito User Pool, note these:**

* ✔️ User Pool ID

**Format:**
```
ap-south-1_XXXXXXX
```

* ✔️ App Client ID

**You already gave:**
```
6vesi9reukk6veomdk7e6k1q7q
```

* ✔️ App Client Secret

**(hidden in console but shown if you click “Show secret”)**

* ✔️ Username + Password of a registered user

**A user must exist in your user pool.**


#### 🟦 STEP 2 — Create SecretHash (Required Because Your App Client Has Secret)

**When an App Client has a client secret, Cognito requires a calculated HMAC value called SecretHash.**

> You can generate SecretHash inside EC2.

* **Create a file called secret_hash.py:**

```
nano secret_hash.py
```

**Paste this code:**

```
import hmac
import hashlib
import base64
import sys

client_id = sys.argv[1]
client_secret = sys.argv[2]
username = sys.argv[3]

message = username + client_id
digest = hmac.new(client_secret.encode('utf-8'),
                  msg=message.encode('utf-8'),
                  digestmod=hashlib.sha256).digest()
print(base64.b64encode(digest).decode())
```

* Save → Exit.

**Run this to generate SecretHash:**

```
python3 secret_hash.py CLIENT_ID CLIENT_SECRET USERNAME
```

##### Copy the output.

**(It will be something like: kfj2JHf8s93JfjsdJH==)**



#### 🟦 STEP 3 — Run Cognito initiate-auth Command



**Now run the AWS CLI:**

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 6vesi9reukk6veomdk7e6k1q7q \
  --auth-parameters USERNAME="YOUR_USERNAME",PASSWORD="YOUR_PASSWORD",SECRET_HASH="YOUR_SECRET_HASH"
```

**Replace placeholders with your pool info:**

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 6vesi9reukk6veomdk7e6k1q7q \
  --auth-parameters USERNAME="demolab",PASSWORD="Password123!",SECRET_HASH="pL7cFgKuFelu9mxpVqDbsiJGuwCMR+CvUNCMns+n3Ms="
```

#### 🟦 STEP 4 — Output (Successful)

**You will receive:**

```
{
  "AuthenticationResult": {
    "AccessToken": "eyJraWQiOi...",
    "IdToken": "eyJraWQiOi...",
    "RefreshToken": "eyJraWQiOi...",
    "TokenType": "Bearer",
    "ExpiresIn": 3600
  }
}
```

**Your AccessToken (JWT) is what you use to call your API Gateway endpoint.**

##### You can now call any API Gateway + Lambda endpoint that is protected with Cognito Authorizer using this header:

```
Authorization: <your AccessToken>
```

**You must use the AccessToken, NOT the ID token.**

### 🟩 Call Your API Using Token

##### First, save your Access Token to a variable in EC2:

```
ACCESS_TOKEN="eyJraWQiOiJSK09IK0lUYW56N2RM....(long token)"
```

**From output, copy:**

##### Now call your API Gateway endpoint:

```
curl -H "Authorization: ACCESS_TOKEN_HERE" 
https://your-api-id.execute-api.region.amazonaws.com

```


**API will return:**


```
🎉 Hello! API is working.**

```
#### 👍 If the token is valid:

##### You will get a 200 OK response from your Lambda.

**❌ If the token is wrong or expired:**

You will get:

```
401 Unauthorized
```

#### ⚠️ Very Important: Use Access Token, NOT IdToken

Cognito authorizers require the Access Token, NOT the ID token.

Access Token = Authorization for API

ID Token = Used by frontend apps for identity (email, username)

**Use this:**

```
Authorization: <AccessToken>
```

#### 🟩 QUICK TIP: REMOVE CLIENT SECRET (EASIER METHOD)

**If you want to avoid generating SecretHash every time:**

* **Go to: Cognito → User Pool → App Clients → demolab → Edit**

👉 **Uncheck: “Generate client secret”**

**Then you can simply run:**

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 6vesi9reukk6veomdk7e6k1q7q \
  --auth-parameters USERNAME="testuser@example.com",PASSWORD="User@12345"
```

###### Much easier.

### ✔️ Now generate the SECRET_HASH again (after fix error)

**You must use the correct Base64 HMAC SHA-256:**

###### 👇 Command (works in EC2 Linux)

```
SECRET_HASH=$(echo -n "demolabUSERNAME6vesi9reukk6veomdk7e6k1q7q" | \
openssl dgst -sha256 -hmac "YOUR_CLIENT_SECRET" -binary | base64)
```

**Replace:**

*  **USERNAME =** your username

*  **YOUR_CLIENT_SECRET =** the long secret Cognito gave you

*  **client id =** 6vesi9reukk6veomdk7e6k1q7q 

*  **app client =** namedemolab 

##### Now run your AWS CLI command again

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 6vesi9reukk6veomdk7e6k1q7q \
  --auth-parameters USERNAME="demolab",PASSWORD="1ncp7lsa1808v7nudr93jgvlslv894d4n2g8ap00ppjef1afrilu",SECRET_HASH="$SECRET_HASH"
```

### Confirm the User Exists

*  Run this on EC2:

```
aws cognito-idp list-users --user-pool-id YOUR_POOL_ID
```

**Look for the username**

### Create a New User in Cognito

*  Use this command:

```
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_nO6YO9b5d \
  --username demolab \
  --user-attributes Name=email,Value="demo@example.com" \
  --message-action SUPPRESS
```

###### Explanation:

*  --message-action SUPPRESS → avoids sending email

*  Creates the user in unconfirmed state

### Set a Permanent Password

*  Now apply a permanent password:

```
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_nO6YO9b5d \
  --username demolab \
  --password "Password123!" \
  --permanent
```



### Reset Password & Make Permanent (if you need to reset)

###### Even if you're confident about the password, reset it once more:

```
aws cognito-idp admin-set-user-password \
  --user-pool-id YOUR_POOL_ID \
  --username demolab \
  --password "Password123!" \
  --permanent
```

**This ensures:**

*  The user is CONFIRMED

*  The password is PERMANENT

*  No force-change-password state

### Re-calculate SECRET_HASH (must be correct)

Your SECRET_HASH is almost always the cause.

###### Use this EXACT command on EC2:

#### Replace:

*  CLIENT_ID → your client ID

*  CLIENT_SECRET → your secret

*  USERNAME → demolab

```
CLIENT_ID="6vesi9reukk6veomdk7e6k1q7q"
CLIENT_SECRET="YOUR_CLIENT_SECRET"
USERNAME="demolab"

SECRET_HASH=$(echo -n "$USERNAME$CLIENT_ID" | openssl dgst -sha256 -hmac "$CLIENT_SECRET" -binary | base64)

echo $SECRET_HASH
```

*  Copy the output.

*  Use it in the next command.

##### Now the user is:

*  ✔️ Created
*  ✔️ Confirmed
*  ✔️ Password set
*  ✔️ Ready for USER_PASSWORD_AUTH


### Verify user exists

```
aws cognito-idp list-users --user-pool-id us-east-1_nO6YO9b5d
```

##### You should now see:

```
{
 "Username": "demolab",
 "UserStatus": "CONFIRMED"
}
```

### Set your variables in EC2

*  Run this on your EC2:

```
USERNAME="demolab"
CLIENT_ID="6vesi9reukk6veomdk7e6k1q7q"
CLIENT_SECRET="PUT_YOUR_CLIENT_SECRET_HERE"
```

###### ⚠️ Replace PUT_YOUR_CLIENT_SECRET_HERE with your real long secret.

### Generate the correct SecretHash

```
SECRET_HASH=$(echo -n "$USERNAME$CLIENT_ID" | openssl dgst -sha256 -hmac "$CLIENT_SECRET" -binary | base64)

echo $SECRET_HASH
```

*  This must output a Base64 string.

*  Copy this output.

### Use that SecretHash

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$CLIENT_ID" \
  --auth-parameters USERNAME="$USERNAME",PASSWORD="Password123!",SECRET_HASH="$SECRET_HASH"
```


### Login Again

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 6vesi9reukk6veomdk7e6k1q7q \
  --auth-parameters USERNAME="demolab",PASSWORD="Password123!",SECRET_HASH="$SECRET_HASH"
```

*  Now it will work.

##### Now you will receive:

```
ID Token

Access Token

Refresh Token
```

## 🟢 NEXT STEPS — What You Can Do Now

###### You successfully completed Cognito authentication.

#### Now you can:

### 1️⃣ Protect API Gateway with Cognito Authorizer

*  **Go to API Gateway → Authorizers → Create New Authorizer**

#### Select:

*  **Type:** Cognito

*  **User Pool:** your pool

*  **Token source:** Authorization

### 2️⃣ Test your Lambda through API Gateway with the token
### 3️⃣ Build full login flow:

*  User signs in → Cognito returns tokens

*  App stores Access Token

*  App calls API with Authorization header

### 4️⃣ Build refresh token flow (optional)


------------------------------------------------------------------------

# 🎉 END OF Task

---


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

### **1. Create S3 Bucket Origin**
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

### **2. Create ALB API.PHP Origin**

### **2.1 Add ALB as a new origin**

- Go to CloudFront → Distribution → Origins → Add origin
- Origin ID → `ALB-API-Origin` 
- Origin domain → paste your ALB DNS: demo-alb-1270704550.us-east-1.elb.amazonaws.com
- Protocol → HTTP only (since your ALB is HTTP)
- Save

### **2.2 Create a new Behavior for API path**

- Go to CloudFront → Behaviors → Create Behavior
- Path pattern → /api.php 
- Origin → Select the ALB origin you just created
- Allowed methods → GET, HEAD, OPTIONS
- Cache policy → CachingDisabled (recommended for APIs)
- Origin request policy → AllViewerExceptHostHeader
- Viewer Protocol Policy → HTTP ONLY (because ALB is HTTP)
- Save  

### **2.3 Add ALB as a new origin**
- Go to CloudFront → Invalidations → Create invalidation
- add path → /* 
- add path → /api.php

Save the **CloudFront URL**.


---
# 📌 **SECTION 3 — AWS CloudFront Cache Invalidation Using Lambda**

## 📌 Overview
This task demonstrates how to automatically invalidate **CloudFront
cache** using **AWS Lambda**, avoiding manual invalidation from
CloudFront console.  
This ensures your CloudFront URL always loads the **latest content**,
even in normal Chrome mode.


## 🎯 Task Objectives

-   Create an IAM role for Lambda with CloudFront permissions  
-   Deploy a Lambda function to trigger CloudFront invalidation  
-   Configure environment variables  
-   Optionally integrate Lambda with EventBridge for automation  
-   Test invalidation with sample events  
-   Verify CloudFront is clearing cache correctly

------------------------------------------------------------------------

## 🏗 Architecture

    User Uploads Code → Lambda Triggered → CloudFront Invalidation → Edge Caches Cleared

------------------------------------------------------------------------

## 🧰 Prerequisites

-   AWS Account  
-   CloudFront Distribution ID  
-   IAM permissions to create Lambda, IAM Roles, and CloudFront
    invalidations

------------------------------------------------------------------------

# 🚀 Step 1: Create IAM Role for Lambda

### **IAM Policy (attach to Lambda execution role)**

``` json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"cloudfront:CreateInvalidation",
				"cloudfront:GetInvalidation",
				"cloudfront:ListInvalidations"
			],
			"Resource": "*"
		},
		{
			"Sid": "CloudWatchLogs",
			"Effect": "Allow",
			"Action": [
				"logs:CreateLogGroup",
				"logs:CreateLogStream",
				"logs:PutLogEvents"
			],
			"Resource": "arn:aws:logs:*:*:*"
		}
	]
}
```

------------------------------------------------------------------------

# 🚀 Step 2: Create Lambda Function (Python 3.x)

### **Lambda Code**

``` python
import boto3
import time
import os

client = boto3.client('cloudfront')

def lambda_handler(event, context):
    distribution_id = os.environ['DISTRIBUTION_ID']

    invalidation_paths = event.get('paths', ['/*'])

    response = client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(invalidation_paths),
                'Items': invalidation_paths
            },
            'CallerReference': str(time.time())
        }
    )

    return {
        'statusCode': 200,
        'body': f"Invalidation created: {response['Invalidation']['Id']}"
    }
```

------------------------------------------------------------------------

# 🚀 Step 3: Add Environment Variable

| Key               | Value                                  |
|-------------------|----------------------------------------|
| `DISTRIBUTION_ID` | Your actual CloudFront Distribution ID |

------------------------------------------------------------------------

# 🚀 Step 4: Test Lambda Manually

### **Test Event JSON**

Invalidate everything:

``` json
{
  "paths": ["/*"]
}
```

Invalidate specific paths:

``` json
{
  "paths": [
    "/index.html",
    "/index.html",
    "/api.php",
    "/css/*",
    "/js/*"
  ]
}
```

------------------------------------------------------------------------

# 🚀 Step 5: Optional Automation (EventBridge)

### Create Scheduled Rule:

-   Every 5 minutes  
-   Hourly  
-   Or on code deploy

Target → your Lambda function

------------------------------------------------------------------------

# 🔍 Step 6: Verify Cache Invalidation

Go to:

**CloudFront → Your Distribution → Invalidations**

You should see:

    Status: InProgress → Completed

After completion: - Open CloudFront URL in normal Chrome mode  
- Latest version loads immediately

------------------------------------------------------------------------

# 🧾 Summary

This lab provided:  
✔ Fully automated CloudFront invalidation via Lambda  
✔ Ability to invalidate dynamic paths like /api.php  
✔ No more manual console invalidation  
✔ Works with CI/CD or EventBridge

------------------------------------------------------------------------

# 🎉 END OF Task

---

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

INSERT INTO products (name, price, description) VALUES
 ('PC', 30000, 'Good PC'),
 ('Samsung', 8000.00, 'Smartphone');

INSERT INTO products (name, price, description) VALUES
 ('Gaming PC', 6000.00, 'Good Gaming PC'),
 ('IPhone', 8700.00, 'Smartphone');

INSERT INTO products (name, price, description) VALUES
 ('Smart LED', 5400.00, 'A1 LED'),
 ('LCD', 700.00, 'LCD');

INSERT INTO products (name, price, description) VALUES
 ('Mouse', 600, 'Branded Mouse'),
 ('Headpne', 8700, 'Headphone');

SHOW TABLES;

SELECT * FROM products;
```

------------------------------------------------------------------------

# 🎉 END OF Task

---

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

- Go to Apache directory

```
cd /var/www/html
sudo nano api.php
```

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

### **4.Save the file**
- Press Ctrl+O
- Press Enter
- Press Ctrl+X
- Type 

```
cd ~
```

### **5.restart Apache**

```
sudo systemctl restart httpd
```

### **6.Test the API (Use curl inside EC2:)**

```
curl http://localhost/api.php
```

```
_____________ Note _________________________
If you see: 

[{"id":1,"name":"Laptop","price":"1200.00","image":"laptop.png"}, ...]

Then API is working!
________________________________________________
```

### **7. ALB Routing (If needed) Test**

If your static site calls:

```
curl http://ecommerce-public-alb-477076023.us-east-1.elb.amazonaws.com/api.php
```


### **8. Connect Front-End (S3) to EC2 Backend**

# Access S3 from the CLI List all buckets (if the IAM role allows it)

```
aws s3 ls
```

# List contents of a specific bucket

```
aws s3 ls s3://ecommerce-static-site-xyz/
```

# Access and Download the File

```
aws s3 cp s3://ecommerce-static-site-xyz/index.html ./
```

# View the File Content

```
cat index.html
```

# Edit the File Locally
```
nano index.html
```
# Upload the Updated File
```
aws s3 cp index.html s3://ecommerce-static-site-xyz/index.html
```
# Static S3 site will call EC2 API using JavaScript (AJAX/Fetch) in index.html:
```
Add below JavaScript in index.html 
```

```
<script>
async function loadProducts() {
  const res = await fetch('http://demo-alb-1270704550.us-east-1.elb.amazonaws.com/api.php'); // Use ALB DNS
  const products = await res.json();
  console.log(products);
  // Render products on page
}
loadProducts();
</script>
```

```
Note: Replace http://ALB-DNS with your Application Load Balancer public DNS that points to EC2 backend.
```
### ** Status: PASS**
---

### **1. CloudFront Loads S3 Website**
```
✔ CloudFront URL opens
✔ Shows “result as per index.html”

➡ This confirms:

S3 static hosting is correct

CloudFront distribution working

Permissions + OAC working

```
### **Status: PASS**
---

### **2. EC2 Backend API Works Locally**
```
curl http://localhost/api.php
```


### **Output: [{"id":"1","name":"Laptop"...}]**

```
This proves:

Apache/PHP installed correctly

api.php scripted correctly

EC2 can connect to RDS

Security groups between EC2 → RDS working

```
### **Status: PASS**

---

### **3. ALB & CloudFront Public DNS Returns API Output**

```
curl http://ecommerce-static-site-ALB-1379179567.us-east-1.elb.amazonaws.com/api.php
curl -I http://ecommerce-static-site-ALB-1379179567.us-east-1.elb.amazonaws.com/api.php
```

### **You MUST see:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Content-Type: application/json
```
If this test returns 200 OK →
CloudFront → S3 → JS Fetch → ALB → EC2 → RDS will work.


### **Test in your browser**

```
http://ecommerce-static-site-ALB-1602237105.us-east-1.elb.amazonaws.com/api.php
```

### **And got:**

```
[{"id":"1","name":"Laptop"...}]
```

- Then press F12 → Network → api.php → Headers

### **You MUST see:**
```
Access-Control-Allow-Origin: *
```
- If not → the file did not update, and I will help you locate the correct path.


```
https://d38zya3b3h11cl.cloudfront.net/api.php
```

### **And got:**

```
[{"id":"1","name":"Laptop"...}]
```

- Then press F12 → Network → api.php → Headers

### **You MUST see:**

```
Access-Control-Allow-Origin: *
x-cache : Miss from cloudfront
```

- If not → the file did not update, and I will help you locate the correct path.


```
This confirms:

ALB listener works

Target group healthy

ALB → EC2 routing correct

EC2 subnet private networking correct
```

### **Status: PASS**

---

### **4. CloudFront Website Must Call ALB API via JavaScript**
- Right now your setup is working backend only.

- But to call the API from frontend, you need:

- Correct API URL in index.html

```
Example:
fetch("https://demo-alb-123456.elb.amazonaws.com/api.php")
  .then(res => res.json())
  .then(data => console.log(data));

CORS enabled on ALB / EC2
In api.php:
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");
```

- If you don’t add CORS, CloudFront → ALB request will be blocked.

### **Test it in browser console:**
- Open CloudFront URL → Press F12 → Console → run:

```
fetch('/api.php')
```

- If you get JSON → PASS
- If you get CORS error → FIX IT.

### **Status: PASS**
---

### **5. Health Checks on ALB Target Group**
- EC2 Console → Target Groups → Your-TG → Targets

### **You must see:**

```
Status = healthy
Both AZ EC2 instances = healthy
```

- If any instance is unhealthy → your architecture is not fully correct.

---
### **6. Security Group Validation**
- Your SGs must be:

# ALB SG

```
Allow inbound 80 or 443 from 0.0.0.0/0

Allow outbound to EC2 SG
```

# EC2 SG
```
Allow inbound from ALB SG only

Allow outbound to RDS SG only
```
# RDS SG
```
Allow inbound 3306 from EC2 SG only
```
# If SGs allow 0.0.0.0 → WRONG (security issue).

---
### **7. Private Subnet Isolation Check**
- Your EC2 instance must NOT be accessible from internet:

### **Test:**
```
curl http://<EC2-public-IP>/api.php
```

### **Expected:**
```
❌ Should NOT work
✔ Only ALB should access EC2
```
- If direct EC2 access succeeds → EC2 is in public subnet → WRONG.

```
sudo systemctl restart httpd
sudo tail -f /var/log/httpd/access_log
sudo systemctl status httpd
sudo systemctl start httpd

ls -l /var/www/html/api.php
curl -I http://localhost/api.php
```
---

### **8. Testing EventBridge** 

- Test launch_new_instanc

```

{
  "desired": 2
}


```

- Test terminate_asg_instance

```

{}


```

```
✔ Check CloudWatch → Logs to confirm
✔ Check ASG console to see changes happening live
```


------------------------------------------------------------------------

# 🎉 END OF Task
---


# 📌 **Index & API.php Files**

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
        const API_URL = "https://dde029484eyt2.cloudfront.net/api.php";
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

---

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

------------------------------------------------------------------------

# 🎉 END AWS HAND-ON LAB
---




