# AWS Hands-On Lab: API Gateway + Cognito + CloudFormation

This lab creates a simple secure API where:

**Cognito** = User signup/login

**API Gateway** = Protected API endpoint

**Lambda** = Backend function

**CloudFormation** = Deploy everything automatically

---
## **AWS LAB ARCHITECTURE OVERVIEW**

**User → Cognito Login → Gets Token → API Gateway (Authorizer) → Lambda → Response**

---
## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/AWS%20Hands-On%20Lab%20API%20Gateway%20+%20Cognito%20+%20CloudFormation.png?raw=true)
---

# ✅ AWS Console Working Guide

## PHASE 1 — Create a Cognito User Pool (Authentication)

### Console Method

---
## STEP 1: Create a Cognito User Pool (Authentication)

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

## STEP 2:  IAM ROLE

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


### ✅ IAM ROLE 2 — CloudFormation Deployment Role

**If you want CloudFormation to create all services on your behalf:**

* **Console → IAM → Roles → Create Role**

* **Trusted entity** → AWS service

* **Service** → CloudFormation

* **Attach policy:**

    * AmazonCognitoPowerUser

    * AWSLambdaFullAccess

    * AmazonAPIGatewayAdministrator

    * IAMFullAccess (optional, only if template creates roles)

    * CloudWatchFullAccess


**✔ Recommended CloudFormation Deployment Policy (least privilege)**  

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:*",
        "lambda:*",
        "apigateway:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}

```


**CloudFormation Trust Policy**

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudformation.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

```
* **Name it:** CloudFormationAPILabRole

---

## STEP 3:  Create a Lambda Function

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

## STEP 4:  Create API Gateway (Cognito Protected API)  
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

## STEP 5: Generate Access Token to Call API

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


---

### ✅ Last STEP  Deploy the Same Setup Using CloudFormation

##### 📌 Where to place IAM Role in CloudFormation template?

*  Create one YAML file:

```
AWSTemplateFormatVersion: '2010-09-09'
Resources:

  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: SimpleAPIPool

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: AppClient
      UserPoolId: !Ref UserPool
      GenerateSecret: false

  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.lambda_handler
      Runtime: python3.12
      Role: arn:aws:iam::<ACCOUNT-ID>:role/<YourLambdaRole>
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "statusCode": 200,
                  "body": "Hello from CloudFormation Lambda!"
              }

  ApiGateway:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: SimpleAPI
      ProtocolType: HTTP

Outputs:
  CognitoUserPoolId:
    Value: !Ref UserPool
  LambdaArn:
    Value: !GetAtt LambdaFunction.Arn
  ApiId:
    Value: !Ref ApiGateway

```
**Deploy:**

```
aws cloudformation deploy \
  --stack-name SimpleSecureAPI \
  --template-file template.yaml \
  --capabilities CAPABILITY_NAMED_IAM

```

* **Replace:**

```
Role: arn:aws:iam::<ACCOUNT-ID>:role/<YourLambdaRole>

```
* **With:**

```
Role: arn:aws:iam::<ACCOUNT-ID>:role/LambdaBasicExecutionRole

```

---

## LAB Verify Test

### ✅ Step 1 — Cognito User Pool Verification

#### Test 1: Verify User Pool Working

**Go to:**

* Cognito → User Pools → YourPool → Users

**You should see:**

* ✔ A user named testuser
* ✔ Status = FORCE_CHANGE_PASSWORD (after first login, becomes CONFIRMED)

#### Test 2: Sign in using AWS CLI

**Run:**

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id YOUR_APP_CLIENT_ID \
  --auth-parameters USERNAME=testuser,PASSWORD=Test@1234

```

**Success output includes:**

* ✔ AuthenticationResult
* ✔ IdToken
* ✔ AccessToken
* ✔ RefreshToken

**If Cognito fails → The entire chain fails → Fix Cognito before continuing.**

---

### ✅ Step 2 — API Gateway Authorizer Verification

#### Test 3: API Gateway should show 401 Unauthorized WITHOUT token

**Open your API URL:**

```
https://your-api-id.execute-api.region.amazonaws.com/

```
**Expected result:**

* ❌ {"message": "Unauthorized"}
* ✔ Means Cognito Authorizer is correctly protecting your API.

**If API is accessible without token → Authorizer is NOT attached.**

#### Test 4: API Works With Token

**Use CURL:**

```
curl -H "Authorization: ACCESS_TOKEN_HERE" \
https://your-api-id.execute-api.region.amazonaws.com/
```

**Expected output:**

* ✔ "🎉 Hello! API is working."

* If you see 403 Forbidden → Wrong token (probably ID token, instead of access token).
* If you see 401 Unauthorized → Authorizer misconfiguration.
* If you see 500 → Lambda error.

---

### ✅ Step 3 — Lambda Verification

#### Test 5: Lambda executes successfully

##### Run test from AWS console:

* Lambda → Test → Create Test Event → Run

**Expected output:**

* ✔ StatusCode: 200
* ✔ Body: Hello! API is working.

#### Test 6: Check CloudWatch Logs

* CloudWatch → Logs → /aws/lambda/YourFunctionName

* You should see new logs after each execution.

* If logs do not appear:

    * ❌ IAM role missing
    * Fix by attaching:

      * ➡ AWSLambdaBasicExecutionRole

#### Test 7: Environment Variables in Code

* Update your Lambda code:

```
import os

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": f"API OK. APP={os.environ.get('APP_NAME')} STAGE={os.environ.get('STAGE')}"
    }

```

* Click Deploy.

#### Test 8: Test Again

* Click Test → Run.

**Expected result:**

```
StatusCode: 200
{
  "statusCode": 200,
  "body": "API OK. APP=demo-api STAGE=dev"
}
```

**This confirms:**

* ✔ Lambda is working
* ✔ Environment variables are readable
* ✔ Latest deployment is running

#### Test 9: Test Using the Lambda Console "Test Tool" with Custom Event

* Create a custom event like:

```
{
  "action": "health-check",
  "source": "console-test"
}
```
* Click Test.

#### Test 10: Verify Logs in CloudWatch (VERY IMPORTANT)

* Go to console search → CloudWatch

* Left side → Logs → Log groups

**Look for:**

```
/aws/lambda/demo-api-lambda
```

* Open the latest log stream.

**You will see logs like:**

```
START RequestId: xxxx
END RequestId: xxxx
REPORT RequestId: xxxx  Duration: 2.34 ms...
```

**This verifies:**

* ✔ Lambda executed
* ✔ Logs are generating
* ✔ Lambda role has correct permissions

#### Test 11: Test Lambda via API Gateway (ONLY if API created)

* If you connect Lambda → API Gateway:

* Go to API Gateway → Your API

* Select GET / or POST /

* Click Test

**You should see the Lambda response.**

#### Test 12: Test Lambda Environment via AWS CLI

* Run on your terminal (or CloudShell):

**Get env vars:**

```
aws lambda get-function-configuration --function-name demo-api-lambda
```

**Invoke Lambda:**

```
aws lambda invoke \
  --function-name demo-api-lambda \
  --payload '{"test": "cli"}' \
  output.json

```
**Check output:**

```
cat output.json

```
---

### ✅ Step 4 — IAM Verification

#### Test 13: Validate IAM Role Permissions

**Make sure your Lambda execution role has at least:**

* AWSLambdaBasicExecutionRole (for CloudWatch logs)

**To verify:**

* Go to IAM → Roles

* Search AWSLambdaBasicExecutionRole

**Check Permissions → must include:**
```
CloudWatchLogs: CreateLogGroup
CloudWatchLogs: CreateLogStream
CloudWatchLogs: PutLogEvents
```

**If logs are appearing — your role is correct.**

---

### ✅ Step 5 — Lambda Verification

#### Test 14: CloudFormation Stack Status

**Go to:**

* CloudFormation → Stacks

**Expected:**

* ✔ Status = CREATE_COMPLETE

**If it shows:**

* ❌ ROLLBACK_IN_PROGRESS
* ❌ ROLLBACK_COMPLETE

**Check Events tab.**

* Fix IAM or resource configurations accordingly.

#### Test 15: All resources should appear in the stack

* CloudFormation → Your Stack → Resources

**You should see ALL:**

* ✔ Cognito User Pool
* ✔ Cognito User Pool Client
* ✔ API Gateway
* ✔ Lambda Function
* ✔ IAM Role (if included)

**If items missing → Template incomplete.**

---

### ✅ Step 6 — End-to-End (E2E) Final Validation

#### Test 16: Full JWT Authentication Flow

* 1️⃣ Login (CLI) → Get Access Token
* 2️⃣ Call API WITHOUT token → should fail
* 3️⃣ Call API WITH token → should succeed
* 4️⃣ Token expires → API should return 401
* 5️⃣ Call API with invalid token → 401
* 6️⃣ Call Lambda directly → Works with test event

**If all 6 steps pass → Lab is 100% complete.**


---


## 🟢 100% SUCCESS CONDITION

**Your lab is considered 100% successful only when ALL conditions are true:**

* ✔ User successfully signs in via Cognito → Token received
* ✔ API Gateway rejects requests WITHOUT token
* ✔ API Gateway allows requests WITH valid token
* ✔ Lambda executes and returns output
* ✔ CloudFormation deployed full infrastructure
* ✔ IAM role allowed Lambda to log into CloudWatch
* ✔ CloudWatch shows logs for each API call







**Your AWS lab is now 100% production‑ready.**
