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

## Troubleshooting 3 — Check connectivity to RDS:

```
mysql -h <RDS-ENDPOINT> -u wordpressuser -p -e "SHOW DATABASES;"
```

## Troubleshooting 4 — Tail logs:

```
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```
## Troubleshooting 5 — CloudWatch agent logs:

```
sudo tail -n 200 /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```