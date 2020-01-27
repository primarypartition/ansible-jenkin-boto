from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
from troposphere.iam import InstanceProfile, PolicyType as IAMPolicy, Role
from awacs.aws import Action, Allow, Policy, Principal, Statement
from awacs.sts import AssumeRole
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

# Create the role 
principal = Principal("Service",["ec2.amazonaws.com"])
statement = Statement(Effect=Allow,Action=[AssumeRole],Principal=principal)
policy = Policy(Statement=[statement])
role = Role("Role",AssumeRolePolicyDocument=policy)
t.add_resource(role)
t.add_resource(
    InstanceProfile(
        "InstanceProfile",
        Path="/",
        Roles=[Ref("Role")]
    )
)

t.add_resource(IAMPolicy(
    "Policy",
    PolicyName = "AllowS3",
    PolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow, Action=[Action("s3","*")],
                Resource=["*"]
                )
            ]
        ),
        Roles=[Ref("Role")]
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