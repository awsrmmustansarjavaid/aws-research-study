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


## STEP 2:  Create a Lambda Function

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

## STEP 3:  Create API Gateway (Cognito Protected API)  
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

## STEP 4: Generate Access Token to Call API
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


## STEP 5: Deploy the Same Setup Using CloudFormation

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

**LAB COMPLETE** 

**You now understand:**

*  **✔️ AWS API Gateway**

Creating and protecting an API

*  **✔️ AWS Cognito**

User login + JWT tokens + API protection

*  **✔️ AWS CloudFormation**

Deploying infrastructure automatically








**Your AWS lab is now 100% production‑ready.**
