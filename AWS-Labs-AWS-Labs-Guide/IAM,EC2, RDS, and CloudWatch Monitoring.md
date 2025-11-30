# IAM Roles for EC2, RDS, and CloudWatch Monitoring

## **AWS Visual Architecture Diagram**
![AWS RDS + Linux Bash Scripting Lab.](https://github.com/awsrmmustansarjavaid/aws-research-study/blob/main/AWS-Labs-AWS-Labs-Visual-Architecture-Diagram/IAM,EC2,%20RDS,%20and%20CloudWatch%20Monitoring.png?raw=true)
---


## 1. Create IAM Role for EC2 (CloudWatch + RDS Monitoring)



### Steps (Console)

1.  Go to **IAM → Roles → Create Role**
2.  Trusted entity: **AWS Service**
3.  Use case: **EC2**
4.  Attach the following policies:
    -   CloudWatchAgentServerPolicy
    -   AmazonEC2ReadOnlyAccess
    -   AmazonSSMManagedInstanceCore
    -   Custom policy provided below
5.  Name the role: **EC2-CloudWatch-RDSMonitoring-Role**

------------------------------------------------------------------------

## 2. Custom IAM Policy

### Policy Name: `Custom-EC2-RDS-CloudWatchMonitorPolicy`

``` json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:DescribeDBLogFiles",
        "rds:DownloadDBLogFilePortion"
      ],
      "Resource": "*"
    }
  ]
}
```

------------------------------------------------------------------------

## 3. Attach IAM Role to EC2 Instance

1.  EC2 → Instances\
2.  Select Instance\
3.  Actions → Security → **Modify IAM Role**\
4.  Select: **EC2-CloudWatch-RDSMonitoring-Role**

------------------------------------------------------------------------

## 4. Configure CloudWatch Agent on EC2

### Install CloudWatch Agent

``` bash
sudo yum install amazon-cloudwatch-agent -y || sudo apt install amazon-cloudwatch-agent -y
```

### Create agent config file:

`/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json`

``` json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/ec2/system",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/httpd/access_log",
            "log_group_name": "/ec2/apache",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

### Start Agent

``` bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
-a start -m ec2 \
-c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

------------------------------------------------------------------------

## 5. Enable RDS Logs to CloudWatch

### Enable Enhanced Monitoring

1.  RDS → DB Instance → Modify\
2.  Enhanced Monitoring → **Enable**\
3.  Choose role: **rds-monitoring-role**

### Enable Log Exports

Enable: - Error logs\
- General logs\
- Slow query logs\
- CloudWatch Logs Export

------------------------------------------------------------------------

## Summary Table

  ----------------------------------------------------------------------------
  Component          IAM Role / Policy                        Purpose
  ------------------ ---------------------------------------- ----------------
  EC2                EC2-CloudWatch-RDSMonitoring-Role        Monitoring EC2 +
                                                              RDS logs

  Custom Policy      Custom-EC2-RDS-CloudWatchMonitorPolicy   Full
                                                              CloudWatch + RDS
                                                              access

  Managed Policies   CloudWatchAgentServerPolicy              Required for log
                                                              shipping

  RDS Role           rds-monitoring-role                      Enhanced
                                                              monitoring
  ----------------------------------------------------------------------------
