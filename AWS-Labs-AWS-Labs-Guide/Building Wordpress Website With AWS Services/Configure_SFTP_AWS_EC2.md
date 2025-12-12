### Method 1 — Configuring SFTP if you are using the simple Apache method

## Step 1 — Confirm SSH/SFTP Works

On EC2, SFTP uses the same service as SSH.

```
sudo systemctl status sshd
```

**If not running:**

```
sudo systemctl start sshd
```

```
sudo systemctl enable sshd
```

## Step 2 — Create user and directories

#### Create user without shell login

```
sudo adduser sftpuser
```

```
sudo passwd sftpuser
```
#### Set the user shell to nologin:

```
sudo usermod -s /usr/sbin/nologin sftpuser
```

#### Verify:

```
grep sftpuser /etc/passwd
```

##### Expected:

```
sftpuser:x:1001:1001::/home/sftpuser:/usr/sbin/nologin
```

#### Add them to Apache group:

```
sudo usermod -aG apache sftpuser
```

## Step 3 — Prepare Correct Chroot Directory

##### For SFTP chroot, the base directory must be owned by root.

#### Fix ownership:

```
sudo chown root:root /var/www
```

```
sudo chown root:root /var/www/html
```

#### Fix permissions:

```
sudo chmod 755 /var/www
```

```
sudo chmod 755 /var/www/html
```
## Step 4 — Create Writable Upload Directory for SFTP User

```
sudo mkdir -p /var/www/html/wp-content/uploads
```

```
sudo chown -R sftpuser:apache /var/www/html/wp-content/uploads
```

```
sudo chmod -R 775 /var/www/html/wp-content/uploads
```

##### This directory is writable by:

- **Apache (WordPress uploads)**

- **sftpuser (SFTP uploads)**




## Step 5 — Configure SFTP-only Access in SSHD

#### Open SSH config:

```
sudo nano /etc/ssh/sshd_config
```
### Ensure it says:

```
PasswordAuthentication yes
ChallengeResponseAuthentication yes
KbdInteractiveAuthentication yes
```
## Step 5 — Add this at the bottom:

```
Match User sftpuser
    PasswordAuthentication yes
    AuthenticationMethods password
    ForceCommand internal-sftp
    ChrootDirectory /home/sftpuser
    AllowTCPForwarding no
    X11Forwarding no
```
**Note: This overrides the EC2 Instance Connect defaults.**

- **Save & close.**

- **✔ No shell**

- **✔ No SSH login**

- **✔ SFTP only**

- **✔ Chroot locked to WordPress directory**


## Step 6 — Restart SSH

```
sudo systemctl restart sshd
```

## Step 7 — Open Security Group

### In AWS → EC2 → Security Group:

```
✅ Allow Port 22 (SSH/SFTP)
Source: 0.0.0.0/0 or your IP
```


## Step 8 — Test SFTP from Local Machine

### From your local PC:

```
sftp sftpuser@YOUR_PUBLIC_IP
```

**You should now get a password prompt:**

```
sftpuser@54.157.234.207's password: 
sftp>
```

**After login:**


```
cd html/uploads
put test.jpg
```

### Verify on server:

```
ls -l /var/www/html/wp-content/uploads
```




#### If You’re Using FileZilla

**use:**
```
| Setting  | Value                             |
| -------- | --------------------------------- |
| Protocol | SFTP – SSH File Transfer Protocol |
| Host     | Your EC2 Public IP                |
| Username | sftpuser                          |
| Password | Your password                     |
| Port     | 22                                |
```

#### Result

```
Now:
✅ Your WordPress runs in browser
✅ You can upload files securely via SFTP
✅ Files land directly in uploads folder
```


***

### Method 2 — Configuring SFTP if you are using the Nginx method

## Step 1 — Confirm SSH/SFTP Works

On EC2, SFTP uses the same service as SSH.

```
sudo systemctl status sshd
```

**If not running:**

```
sudo systemctl start sshd
```

```
sudo systemctl enable sshd
```

## Step 2 — Create user and directories

#### Create user without shell login

```
sudo adduser --home /home/sftpuser --shell /sbin/nologin sftpuser
```

#### Set password for SFTP user

```
sudo passwd sftpuser
```

## Step 3 — Prepare Chroot Directory (Required for SFTP Jail)


The SFTP user will be locked into /home/sftpuser.

#### Create main SFTP directory

```
sudo mkdir -p /home/sftpuser/uploads
```

#### Root must own the chroot directory

(This is required or SFTP jail will fail.)

```
sudo chown root:root /home/sftpuser
```

```
sudo chmod 755 /home/sftpuser
```

## Step 4 — Give user access only to uploads directory

(The user must not own the chroot root.)

```
sudo mkdir -p /home/sftpuser/uploads
```

```
sudo chown sftpuser:sftpuser /home/sftpuser/uploads
```

```
sudo chmod 700 /home/sftpuser/uploads
```

## Step 5 — Create WordPress Uploads Bind-Mount for SFTP

This ensures files uploaded via SFTP appear correctly in WordPress.

#### Prepare directories inside chroot jail

```
sudo mkdir -p /home/sftpuser/wordpress
```
```
sudo mkdir -p /home/sftpuser/wordpress/wp-content
```
```
sudo mkdir -p /home/sftpuser/wordpress/wp-content/uploads
```

## Step 6 — Ensure real WordPress uploads directory exists

#### Location for Nginx-based WordPress:

```
sudo mkdir -p /usr/share/nginx/html/wp-content/uploads
```
```
sudo chown -R nginx:nginx /usr/share/nginx/html/wp-content/uploads
```

## Step 7 — Bind real uploads directory to SFTP uploads directory

```
sudo mount --bind /usr/share/nginx/html/wp-content/uploads /home/sftpuser/wordpress/wp-content/uploads
```

#### Make the bind-mount permanent at boot

Add this line to /etc/fstab:

```
echo '/usr/share/nginx/html/wp-content/uploads /home/sftpuser/wordpress/wp-content/uploads none bind 0 0' | sudo tee -a /etc/fstab
```

##### Important: The chroot root /home/sftpuser must be owned by root and not writable by others. Only the uploads directory (or specific subdirs) should be owned by the sftp user. We bound only uploads.

## Step 8 — Configure OpenSSH for Chrooted SFTP

#### Edit SSH config:

```
sudo nano /etc/ssh/sshd_config
```

#### Add these lines at the bottom:

```
# Enable internal SFTP subsystem
Subsystem sftp internal-sftp

# Chrooted SFTP configuration
Match User sftpuser
    ChrootDirectory /home/sftpuser
    ForceCommand internal-sftp
    PasswordAuthentication yes
    X11Forwarding no
    AllowTcpForwarding no
```

### Restart SSH Service

```
sudo systemctl restart sshd
```
## Step 9 — Harden file permissions for WordPress

### Make wp-content Writable for WordPress (Uploads, Plugins, Themes)


WordPress must write inside the wp-content/ folder to upload media, install plugins, and install themes.

```
sudo chown -R nginx:nginx /usr/share/nginx/html/wp-content
```

**✔️ What This Does:**

- Makes the NGINX web server the owner of wp-content/

- Allows WordPress to upload media + install plugins/themes

- Prevents permission errors like:
```

“Unable to create directory uploads”

“Installation failed: Could not create directory”
```

### Secure wp-config.php (Critical Security Step)

Change Ownership of wp-config.php

```
sudo chown nginx:nginx /usr/share/nginx/html/wp-config.php
```

**✔️ What This Does:**

- Makes sure the web server owns the file but…

- Only the owner and group can read it (after next command)

- Prevents unauthorized read/write

### Restrict Read Permission to Owner + Group Only

```
sudo chmod 640 /usr/share/nginx/html/wp-config.php
```

### Restrict Read Permission to Owner + Group Only (Optional)

If you want your SFTP user to upload media only, but not edit plugins/themes, then use this:

```
sudo chown -R sftpuser:sftpuser /usr/share/nginx/html/wp-content/uploads
```

**✔️ What This Does:**

- Allows SFTP user to upload images only

- Keeps security strong

- Prevents SFTP user from modifying plugins/themes


## Step 10 — Test SFTP

#### Connect using command line:

```
sftp sftpuser@<EC2-PUBLIC-IP>
```

#### List available directories:

```
ls
```
**You should see:**

```
uploads
wordpress
```

#### Test file upload:

```
put testfile.jpg
```

#### TVerify on server:

```
ls /usr/share/nginx/html/wp-content/uploads
```

**You should see testfile.jpg.**


***