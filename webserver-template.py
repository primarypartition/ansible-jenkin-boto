from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2
t = Template()



sg = ec2.SecurityGroup("LampSg")
sg.GroupDescription = "Allow access to ports 22 and 80"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp = "0.0.0.0/0")
	]

t.add_resource(sg)

# This is the keypair that CloudFormation will ask you about when launching the stack
keypair = t.add_parameter(Parameter(
    "KeyName",
    Description="Name of the SSH key pair that will be used to access the instance",
    Type="String",
))

ud = Base64(Join('\n',[
        "#!/bin/bash",
        "sudo yum -y install apache",
        "chown -R ec2-user /var/www/html"
        "echo '<html><body><h1>Welcome to DevOps on AWS</h1></body></html>' > /var/www/html/test.html",
        "sudo service apache start",
        "sudo chkconfig apache on"
    ]))

instance = ec2.Instance("Webserver")
instance.ImageId = "ami-e689729e"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)
instance.UserData = ud

t.add_resource(instance)

t.add_output(Output(
    "InstanceAccess",
    Description="Command to use to SSH to instance",
    Value=Join("", ["ssh -i ~/.ssh/LampKey.pem ec2-user@", GetAtt(instance, "PublicDnsName")])
))
t.add_output(Output(
    "WebURL",
    Description="The URL of the application",
    Value=Join("",["http://", GetAtt(instance,"PublicDnsName")])
))
print(t.to_json())