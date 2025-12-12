## Test 1 — Web server & PHP

```
curl -I http://localhost
# Response should include HTTP/1.1 200 OK or 302 redirect to /wp-admin/install.php
php -v
nginx -v
```

## Test 2 — Database connectivity test from EC2

```
mysql -h <RDS-ENDPOINT> -u wordpressuser -p -e "SELECT USER(), CURRENT_DATE(), VERSION();"
# You should see user and server version without errors
```

## Test 3 — WordPress GUI test

Open in browser:

```
http://<EC2-PUBLIC-IP>/
```

- The WordPress site loads → run the installer if not already done.

- Login to WP Admin (/wp-admin) with credentials created earlier.

- Upload media via WP Dashboard → Media → Add New. File should appear in /usr/share/nginx/html/wp-content/uploads/... and also visible in SFTP.


## Test 4 — SFTP test (from your workstation)

```
sftp sftpuser@<EC2-PUBLIC-IP>
# then
cd wordpress/wp-content/uploads
put test-sftp.txt
ls -l
```
File should be visible in WordPress Media or at least in /usr/share/nginx/html/wp-content/uploads.

## Test 5 — CloudWatch verification

- In AWS Console → CloudWatch → Logs → confirm entries appear for:
```

wordpress-nginx-access (access logs)

wordpress-nginx-error (errors)
```

- In CloudWatch Metrics → check memory, cpu, disk metrics are being reported for your instance.

## Test 6 — Permissions & Security checks

#### Verify wp-config.php is not world-readable:

```
ls -l /usr/share/nginx/html/wp-config.php
# should be -rw-r----- (640) or similar
```

#### Verify ChrootDirectory ownership:

```
ls -ld /home/sftpuser
# should be owned by root:root and 755, /home/sftpuser/uploads owned by sftpuser
```

## Test 7 — Final functional test — upload and serve

- Upload an image file via SFTP to wordpress/wp-content/uploads/<YYYY>/<MM>/ (or uploads/).

- On WordPress admin → Media, the file should be visible (may require correct file permissions and ownership).

- Insert the image into a post and open the public page to ensure Nginx serves it.


