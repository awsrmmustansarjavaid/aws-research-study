Download and install the stress test tool
sudo amazon-linux-extras install epel -y
sudo yum install stress -y
Launch the stress test in background (for 800 seconds in that example)
sudo stress --cpu 8 --timeout 800 &
Manually stop the stress test (if needed)
sudo killall stress


 sudo su -
yum update -y
yum install stress -y
stress --cpu 5
top
after stressing it will create ec2



