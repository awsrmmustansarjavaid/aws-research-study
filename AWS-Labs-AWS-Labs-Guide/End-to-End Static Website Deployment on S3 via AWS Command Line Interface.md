
# End-to-End Static Website Deployment on S3 via AWS Command Line Interface


## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/End-to-End%20Static%20Website%20Deployment%20on%20S3%20via%20AWS%20Command%20Line%20Interface.jpg?raw=true)
---


## **1. Create an S3 Bucket**

```
aws s3 mb s3://demotestnov-s3b1
```

## **2. Enable Static Website Hosting**

```
aws s3 website s3://demotestnov-s3b1/ --index-document index.html --error-document error.html
```

```
aws s3api put-public-access-block \
  --bucket demotestnov-s3b1 \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

## **3. Set Public Read Policy**

- Create a file named policy.json:

```
echo '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::demotestnov-s3b1/*"
    }
  ]
}' > policy.json
```

- Apply the policy:

```
aws s3api put-bucket-policy --bucket demotestnov-s3b1 --policy file://policy.json
```

## **4. Upload Website Files**
```
mkdir website
```
```
cd website
```
```
vi index.html
```
```
cd ..
```
```
aws s3 cp ./website/ s3://demotestnov-s3b1/ --recursive
```
## **5. Get Website URL**
```
aws s3 website s3://demotestnov-s3b1/ --index-document index.html
```

### Access your site at:
```
aws s3api get-public-access-block --bucket demotestnov-s3b1
```

```
aws s3api put-public-access-block \
  --bucket demotestnov-s3b1 \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```
```
http://demotestnov-s3b1.s3-website-us-east-1.amazonaws.com
```
## **6. Remove S3 Bucket**
```
aws s3 rb s3://demotestnov-s3b1 --force
```