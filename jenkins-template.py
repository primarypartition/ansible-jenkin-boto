from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2
t = Template()

sg = ec2.SecurityGroup("JenkinsSg")
sg.GroupDescription = "Allow access to ports 22 and 8080"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "8080", ToPort = "8080", CidrIp = "0.0.0.0/0")
	]

t.add_resource(sg)

# This is the keypair that CloudFormation will ask you about when launching the stack
keypair = t.add_parameter(Parameter(
    "KeyName",
    Description="Name of the SSH key pair that will be used to access the instance",
    Type="String",
))

instance = ec2.Instance("Jenkins")
instance.ImageId = "ami-e689729e"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)
instance.IamInstanceProfile=Ref("InstanceProfile")

t.add_resource(instance)

t.add_output(Output(
    "InstanceAccess",
    Description="Command to use to SSH to instance",
    Value=Join("", ["ssh -i ~/.ssh/LampKey.pem ec2-user@", GetAtt(instance, "PublicDnsName")])
))
t.add_output(Output(
    "WebURL",
    Description="The URL of the application",
    Value=Join("",["http://", GetAtt(instance,"PublicDnsName"),":8080"])
))
print(t.to_json())