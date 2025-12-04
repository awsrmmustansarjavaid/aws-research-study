------ Creating Key Pairs -----
1/ Create your key pairs if you don't have any:
	a/ Go EC2
	b/ On left pan: "Key Pairs"
	c/ Create Key Pair
	d/ Enter the name you want then create


------ Elastic IPs -----
2/ Create 1 Elastic IPs, one for the NAT Gateway
	a/ Go to "Service"
	b/ In left pan select "Elastic IPs"
	c/ Select "Allocate new address" (in new opened window, just choose "Allocate" then "close")


------ Create your VPC ---------	
3/ In the AWS Management Console, on the Services menu, click VPC.
4/ Click Start VPC Wizard.
5/ In the navigation pane, click VPC with Public and Private Subnets.
6/ Click Select.
7/ Configure the following settings (and ignore any settings that aren't listed):
	a/ IPV4CIDR block: Type: 10. 0. 0. 0/16
	b/ VPC name: "VPC_LoadBalancer"
	c/ Public subnet's IPv4 CIDR: Type 10. 0. 0. 0/24 
	d/ Availability Zone: Click the first Availability Zone.
	e/ Public subnet name: type "VPC_LoadBalancer AZ1 Public Subnet"
	f/ Private subnet's IPv4 CIDR: Type 10. 0. 1. 0/24
	g/ Availability Zone: Click the first Availability Zone. The same as used for "VPC_LoadBalancer AZ1 Public Subnet"
	h/ Private subnet name: type "VPC_LoadBalancer AZ1 Private Subnet"
	i/ Specify the details of your NAT gateway: "Choose one of the Elastic IP previously defined"
8/	Click Create VPC.
9/	In the success message, click OK.


------ Add 2 other subnets in created VPC ---------	
10/ In the AWS Management Console, on the Services menu, click Subnets.
11/ in the poped window fill the following elements
	a/ Name Tag: "VPC_LoadBalancer AZ2 Public Subnet"
	b/ VPC: "VPC_LoadBalancer"
	c/ Availability Zone: Select another one than previously selected 
	d/ IPv4 CIDR: "10. 0. 2. 0/24"
12/ Create another subnet using the same procedures as previous:
	a/ Name Tag: "VPC_LoadBalancer AZ2 Private Subnet"
	b/ VPC: "VPC_LoadBalancer"
	c/ Availability Zone: Select the same as previous one
	d/ IPv4 CIDR: "10. 0. 3. 0/24"
	
	
------ Route Tables ---------	
13/ You need to have 4 route tables, 1 for each subnet, normally all of them were created during the step of subnet creation, but need to be correctly setted
	a/ In the AWS Management Console, on the Services menu, click Route Tables. You will normally see 4 route tables attached to your VPC, if not create the missing ones
	b/ For each of the 4 route tables, chech them one by one the follosing settings:
		i/ In bottom pan, in tab Routes, for the 2 public subnets you need to have "local" and "internet gateway", normally internet gateway is not setted, if this is the case edit and add it (Destination: 0.0.0.0/0 and Target: name of the internate gateway)
		ii/ In bottom pan, in tab Routes, for the 2 private subnets you need to have "local" and "nat-blabla", normally the nat is not setted by default, if this is the case edit and add it (Destination: 0.0.0.0/0 and Target: name of the nat)
		iii/ In bottom pan, in tab subnet associations, for the all route tables in need to only one subnet, check if you have the right ones

		
------- Create Security Group for public subnet -----
14/ In the navigation pane, click Security Groups.
15/ Click Create Security Group.
16/ In the Create Security Group dialog box, configure the following settings (and ignore
	any settings that aren't listed)
	a/ Name tag: "VPC_LoadBalancer public security group"
	b/ Group name: "VPC_LoadBalancer public security group"
	c/ Description: "VPC_LoadBalancer public security group"
	d/ VPC: Click "VPC_LoadBalancer" 
17/ Click Yes, Create.
18/ Select "AWS Project 1 public security group".
19/ Click the Inbound Rules tab.
20/ Click Edit.
21/ Click Add.
22/ For Type, click HTTP (80)
23/ Click in the Source "Anywhere"
24/ Click Add again.
25/ For Type, click HTTPS (443)
26/ Click in the Source "Anywhere"
27/ Click Add again.
28/ For Type, click SSH (22)
29/ Click in the Source "Anywhere"
30/ Click Save.


------- Create Security Group for private subnet -----
31/ Click again on Create Security Group.
32/ In the Create Security Group dialog box, configure the following settings (and ignore
	any settings that aren't listed)
	a/ Name tag: "VPC_LoadBalancer private security group"
	b/ Group name: "VPC_LoadBalancer private security group"
	c/ Description: "VPC_LoadBalancer private security group"
	d/ VPC: Click "VPC_LoadBalancer" 
33/ Click Yes, Create.
34/ Select "VPC_LoadBalancer private security group".
35/ Click the Inbound Rules tab.
36/ Click Edit.
37/ Click Add.
38/ For Type, click HTTP (80)
39/ Click in the Source "Anywhere"
40/ Click Add again.
41/ For Type, click HTTPS (443)
42/ Click in the Source "Anywhere"
43/ Click Add again.
44/ For Type, click SSH (22)
45/ Click in the Source "Anywhere"
46/ Click Save.


------- Create WEBSERVER Instance1 ------
47/ On the Services menu, click EC2.
48/ Click Launch Instance.
49/ In the row for Amazon Linux AM
50/ On the Step 2: Choose an Instance Type Linux
51/ On the Step 3: Configure Instance Details page, configure the following settings (and ignore any settings that aren't listed)
	a/ Network: "VPC_LoadBalancer"
	b/ Subnet: "VPC_LoadBalancer AZ1 Private Subnet"
	c/ Expand "Advanced Details" and add in "User Data" the following lines to create an HTLM page:
	
	
		#!/bin/bash
		sudo yum update -y
		sudo yum -y install httpd
		sudo service httpd start
		sudo bash -c 'echo HELLO PRAS WEBSERVER1 TRIAL 1 NAT FOR BOTH WEBSERVER > /var/www/html/index.html'
		
		
		
52/ Click Next: Add Storage.
53/ Click Next: Add Tags.
54/ Click Add Tag, and configure the following settings (and ignore any settings that aren't listed):
	a/ Key: "Name"
	b/ Value: "VPC_LoadBalancer_WEBSERVER1"
55/ Click Next: Configure Security Group.
56/ On the Step 6: Configure Security Group page, click Select an existing security group, and then select the security group you created previously "VPC_LoadBalancer private security group"
57/ Review and launch instance


------- Create WEBSERVER Instance2 ------
58/ On the Services menu, click EC2.
59/ Click Launch Instance.
60/ In the row for Amazon Linux AM
61/ On the Step 2: Choose an Instance Type Linux 
62/ On the Step 3: Configure Instance Details page, configure the following settings (and ignore any settings that aren't listed)
	a/ Network: "VPC_LoadBalancer"
	b/ Subnet: "VPC_LoadBalancer AZ2 Private Subnet"
	c/ Expand "Advanced Details" and add in "User Data" the following lines to create an HTLM page:
	
	
		#!/bin/bash
		sudo yum update -y
		sudo yum -y install httpd
		sudo service httpd start
		sudo bash -c 'echo BYE BYE PRAS WEBSERVER2 TRIAL 1 NAT FOR BOTH WEBSERVER > /var/www/html/index.html'
		
		
		
63/ Click Next: Add Storage.
64/ Click Next: Add Tags.
65/ Click Add Tag, and configure the following settings (and ignore any settings that aren't listed):
	a/ Key: "Name"
	b/ Value: "VPC_LoadBalancer_WEBSERVER2"
66/ Click Next: Configure Security Group.
67/ On the Step 6: Configure Security Group page, click Select an existing security group, and then select the security group you created previously "VPC_LoadBalancer private security group"
68/ Review and launch instance


------- Create LOAD BALANCER ------
69/ On the Services menu, click EC2.
70/ Click on Load Balancer in the left pan.
71/ Click on Create Load BALANCER
72/ Select application load balancer HTTP/HTTPS and create
73/ Fill the following elements	
	a/ In Basic cofniguration, Name: "VPCLoadBalancerLB"
	b/ In Availability Zones, VPC: "VPC_LoadBalancer"
	c/ Select for each availability zone the public subnet and next configure security group
	d/ You probably a warning message, just ignore it, and click next again
	e/ Create a new security group and add HTTP, HTTPS, and next to configure routing
	f/ Just add a new for target groups and next for register
	g/ Choose the both launched instances, and add to register, then review and create
74/ Wait until state pass to "active", and copy/paste the DNS of your load balancer in your browser, you will have something like:
	VPCLoadBalancerLB-1329298645.eu-west-1.elb.amazonaws.com, refresh your browser fastly you will see the 2 messages we have add in HTML page when we have created the instances

That's ALL!
