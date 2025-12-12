## ☁️ AWS Hands-on Lab Guide 

# AWS Wordpress Configuration Lab Guide (EC2 + S3 + WordPress + RDS & SFTP + AWSTransfer Family (SFTP) + Connector) Architecture

### Architecture Designer: Charlie

-----

# 🛠️ Section 1 — Web / WordPress Troubleshooting


## Troubleshooting 1 — Nginx config test / restart:

```
sudo nginx -t
```

```
sudo systemctl restart nginx
```

```
sudo journalctl -u nginx -n 200
```

## Troubleshooting 2 — PHP-FPM restart & status:


```
sudo systemctl restart php-fpm
```

```
sudo systemctl status php-fpm
```

```
sudo journalctl -u php-fpm -n 200
```

---

# 🛠️ Section 2 — DataBase / DB Troubleshooting


## Troubleshooting 1 — Check connectivity to RDS:

```
mysql -h <RDS-ENDPOINT> -u wordpressuser -p -e "SHOW DATABASES;"
```

---

# 🛠️ Section 3 — Monirtoring  Troubleshooting


## Troubleshooting 1 — Tail logs:

```
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```
## Troubleshooting 2 — CloudWatch agent logs:

```
sudo tail -n 200 /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```


---

# 🛠️ Section 4 — SFTP  Troubleshooting

## Troubleshooting 1 — 


