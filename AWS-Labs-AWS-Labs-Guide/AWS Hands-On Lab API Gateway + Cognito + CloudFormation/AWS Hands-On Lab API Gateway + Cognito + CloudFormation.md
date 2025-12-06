# AWS Hands-On Lab: API Gateway + Cognito + CloudFormation

This lab creates a simple secure API where:

**Cognito** = User signup/login

**API Gateway** = Protected API endpoint

Lambda = Backend function

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

* Go to Amazon Cognito → User Pools → Create User Pool

* Choose:

    * **Authentication type:** Username & Password

    * **Password policy:** Easy (for lab)

* Keep defaults → Create User Pool

* Go to Users → Create user

    * **Username:** testuser

    * **Temporary password:** Test@1234

**Result**

* A working Cognito User Pool

* A test user created

---

## STEP 2:  IAM ROLE

### ✅ IAM ROLE 1 — Lambda Execution Role

#### Create IAM Role for Lambda

* Console → IAM → Roles → Create Role

* Trusted entity → AWS service

* Service → Lambda

* Attach policy:

    * **AWSLambdaBasicExecutionRole**

➡ This allows Lambda to write logs to CloudWatch.

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

* Console → IAM → Roles → Create Role

* Trusted entity → AWS service

* Service → CloudFormation

* Attach policy:

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

##### 📌 Where to place IAM Role in CloudFormation template?

* Modify your YAML:

```
LambdaRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: LambdaBasicExecutionRole
    AssumeRolePolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

LambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    Handler: index.lambda_handler
    Runtime: python3.12
    Role: !GetAtt LambdaRole.Arn
    Code:
      ZipFile: |
        def lambda_handler(event, context):
            return {
                "statusCode": 200,
                "body": "Hello from CloudFormation Lambda!"
            }

```

### Step-by-Step IAM Setup Guide

#### STEP 1 — Create Lambda Execution Role

* ✔ Go to IAM → Roles → Create Role
* ✔ Select Lambda
* ✔ Attach AWSLambdaBasicExecutionRole
* ✔ Name it: LambdaBasicExecutionRole

#### STEP 2 — Create CloudFormation Deployment Role (optional)

* ✔ IAM → Roles → Create Role
* ✔ Select CloudFormation
* ✔ Attach:

    * AmazonAPIGatewayAdministrator

    * AWSLambdaFullAccess

    * AmazonCognitoPowerUser

* Name it: CloudFormationAPILabRole

#### STEP 3 — Use the Role in your YAML template

* Replace:

```
Role: arn:aws:iam::<ACCOUNT-ID>:role/<YourLambdaRole>

```
* With:

```
Role: arn:aws:iam::<ACCOUNT-ID>:role/LambdaBasicExecutionRole

```



---


## STEP 3:  Create a Lambda Function

* Go to Lambda → Create function

* Runtime: Python 3.12

* Insert code:

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
---

## STEP 4:  Create API Gateway (Cognito Protected API)  
* Go to API Gateway

* Create → HTTP API

* Add integration → Lambda

* Choose your Lambda function

* In Authorization, choose:

    * Add Authorizer

    * Type: Cognito

    * Select the User Pool created in Step 1

* Attach Authorizer to / route

**Test**

* If you open this API in browser → Unauthorized (401)
Good! It means the API is protected.

---

## STEP 5: Generate Access Token to Call API
*  AWS CLI required.

*  Install AWS CLI

> (Linux/macOS/Windows)

*  Run command:

> Replace placeholders with your pool info:

```
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id YOUR_COGNITO_APPCLIENT \
  --auth-parameters USERNAME=testuser,PASSWORD=Test@1234

```
* From output, copy:

```
curl -H "Authorization: ACCESS_TOKEN_HERE" https://your-api-id.execute-api.region.amazonaws.com

```
**API will return:**


> **🎉 Hello! API is working.**


---


## STEP 6: Deploy the Same Setup Using CloudFormation

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

---

### ✅ Step 4 — Lambda Verification

#### Test 7: CloudFormation Stack Status

**Go to:**

* CloudFormation → Stacks

**Expected:**

* ✔ Status = CREATE_COMPLETE

**If it shows:**

* ❌ ROLLBACK_IN_PROGRESS
* ❌ ROLLBACK_COMPLETE

**Check Events tab.**

* Fix IAM or resource configurations accordingly.

#### Test 8: All resources should appear in the stack

* CloudFormation → Your Stack → Resources

**You should see ALL:**

* ✔ Cognito User Pool
* ✔ Cognito User Pool Client
* ✔ API Gateway
* ✔ Lambda Function
* ✔ IAM Role (if included)

**If items missing → Template incomplete.**

---

### ✅ Step 5 — End-to-End (E2E) Final Validation

#### Test 9: Full JWT Authentication Flow

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
