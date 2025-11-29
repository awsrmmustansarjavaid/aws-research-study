# 🛡️ WireGuard on AWS EC2 (Free Tier Setup Guide)

## 📘 Overview
WireGuard is a modern, lightweight VPN protocol that provides fast and secure communication.  
This guide shows how to set up WireGuard on an AWS EC2 instance using the **Free Tier**.

---

## 💰 Free Tier Eligibility

| Component | Free Tier Status | Details |
|------------|------------------|----------|
| **EC2 Instance** | ✅ Yes (12 months) | 750 hours/month of `t2.micro` or `t3.micro` (1 vCPU, 1GB RAM). Perfect for WireGuard. |
| **EBS Storage** | ✅ Yes | 30 GB of SSD storage free. |
| **Data Transfer OUT** | ⚠️ Limited | First **1 GB/month** of outbound data is free. Charges apply afterward. |
| **Inbound Data** | ✅ Free | All incoming traffic to EC2 is free. |

> ✅ You can run WireGuard on AWS Free Tier **as long as you stay within these limits**.

---

## ⚙️ Step-by-Step Setup Guide

### 1. Launch EC2 Instance
- Log in to your **AWS Console** → **EC2 Dashboard** → **Launch Instance**
- Choose an OS:
  - **Ubuntu 22.04 LTS**
  - or **Amazon Linux 2**
- Select instance type: **t2.micro** or **t3.micro** (Free Tier eligible)
- Configure:
  - Network: default VPC
  - Subnet: any public subnet
  - Security Group:
    - Allow **UDP port 51820** (WireGuard)
    - Allow **SSH port 22** (for admin access)
- Launch the instance and connect via SSH.

---

### 2. Connect via SSH
```bash
ssh -i <your-key.pem> ubuntu@<EC2-Public-IP>
```

---

### 3. Update System and Install WireGuard
```bash
sudo apt update -y
sudo apt install wireguard -y
```

---

### 4. Generate Keys
```bash
wg genkey | tee privatekey | wg pubkey > publickey
```

Save both keys somewhere safe:
```bash
cat privatekey
cat publickey
```

---

### 5. Configure WireGuard Interface

Create and edit the configuration file:
```bash
sudo nano /etc/wireguard/wg0.conf
```

Paste the following content:
```ini
[Interface]
PrivateKey = <server-private-key>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.0.0.2/32
```

Save and exit (`Ctrl + O`, `Ctrl + X`).

---

### 6. Enable IP Forwarding
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

To make it permanent, edit `/etc/sysctl.conf` and uncomment or add:
```
net.ipv4.ip_forward=1
```

---

### 7. Start WireGuard Service
```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

Check the status:
```bash
sudo systemctl status wg-quick@wg0
```

---

### 8. Configure WireGuard Client

On your **client device** (Windows/Linux/Mac/Android):
1. Install **WireGuard app**
2. Create a new tunnel with the following template:

```ini
[Interface]
PrivateKey = <client-private-key>
Address = 10.0.0.2/32
DNS = 1.1.1.1

[Peer]
PublicKey = <server-public-key>
Endpoint = <EC2-Public-IP>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

---

### 9. Test the Connection

On the client:
```bash
ping 10.0.0.1
```

On the server:
```bash
sudo wg
```

You should see your client peer connected.

---

## 🌐 Cost Management Tips
- Stop your EC2 instance when not using WireGuard to save resources.
- Monitor **Free Tier usage** from:
  - AWS Console → **Billing Dashboard → Free Tier Usage**
- Avoid streaming or large data transfers to stay within the **1 GB free outbound data limit**.

---

## 📊 Summary

| Task | Completed |
|------|------------|
| Launch EC2 (Free Tier) | ✅ |
| Install & Configure WireGuard | ✅ |
| Enable IP Forwarding | ✅ |
| Connect Client | ✅ |
| Test Connection | ✅ |

---

## 🧠 Pro Tip
Use **AWS region nearest to you** for lower latency and faster VPN speeds.

---

## ✅ Conclusion
You have successfully deployed a **WireGuard VPN on AWS EC2** using only Free Tier resources.  
This setup gives you a **secure**, **lightweight**, and **cost-effective** personal VPN server.

---
