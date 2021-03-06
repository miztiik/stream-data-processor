#!/usr/bin/env python3
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import aws_ssm as _ssm
from aws_cdk import core


class global_args:
    """
    Helper to define global statics
    """
    OWNER = "MystiqueAutomation"
    REPO_NAME = "stream-data-processor"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_04_04"
    POLYGLOT_SUPPORT_EMAIL = ["mystique@example.com", ]


class streamDataProducerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, stream_arn, data_pipe_ssm_param, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # CloudWatch LogGroup for Stream Producer):

        self.stream_producer_lg = _logs.LogGroup(
            self,
            "streamProducerLoggroup",
            log_group_name=(
                f"/{global_args.REPO_NAME}"
                f"/producers"
            ),
            removal_policy=core.RemovalPolicy.DESTROY
        )

        self.data_pipe__producer_lg_ssm_param = _ssm.StringParameter(self, "dataPipeLgParameter",
                                                                     description="Kinesis Stream Name",
                                                                     parameter_name=f"/{global_args.REPO_NAME}/streams/data_pipe/produce/log_group_name",
                                                                     string_value=f"{self.stream_producer_lg.log_group_name}"
                                                                     )

        # Read BootStrap Script):
        try:
            with open("stream_data_producer/bootstrap_scripts/deploy_app.sh", mode="r") as file:
                user_data = file.read()

            # Let us add the stream name to our user_data script
            # Ideally can also use SSM Parameter Store
            # user_data = file_data + f"export STREAM_PARAM_NAME='{data_pipe_ssm_param}'"

        except OSError:
            print('Unable to read UserData script')

        # Get the latest AMI from AWS SSM
        linux_ami = _ec2.AmazonLinuxImage(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)

        # Get the latest ami
        amzn_linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )
        # ec2 Instance Role
        _instance_role = _iam.Role(self, "webAppClientRole",
                                   assumed_by=_iam.ServicePrincipal(
                                       'ec2.amazonaws.com'),
                                   managed_policies=[
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AmazonSSMManagedInstanceCore'
                                       ),
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AWSXRayDaemonWriteAccess'
                                       )
                                   ]
                                   )

        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "kinesis:Get*",
                "kinesis:DescribeStream",
                "kinesis:DescribeStreamSummary",
                "kinesis:ListStreams",
                "kinesis:PutRecord",
                "kinesis:PutRecords"
            ],
            resources=[stream_arn]
        ))

        # Allow CW Agent to create Logs
        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "logs:Create*",
                "logs:PutLogEvents"
            ],
            resources=["arn:aws:logs:*:*:*"]
        ))

        # Allow Instance to read SSM Parameters
        data_pipe_ssm_param.grant_read(_instance_role)

        # web_app_server Instance
        self.web_app_server = _ec2.Instance(self,
                                            "webAppServer",
                                            instance_type=_ec2.InstanceType(
                                                instance_type_identifier="t2.micro"),
                                            instance_name="web_app_server",
                                            machine_image=amzn_linux_ami,
                                            vpc=vpc,
                                            vpc_subnets=_ec2.SubnetSelection(
                                                subnet_type=_ec2.SubnetType.PUBLIC
                                            ),
                                            role=_instance_role,
                                            user_data=_ec2.UserData.custom(
                                                user_data)
                                            )

        # Allow Web Traffic to WebServer
        self.web_app_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(80), description="Allow Web Traffic"
        )

        self.web_app_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(443), description="Allow Secured Web Traffic"
        )

        # Add dependency for the CW Log group before creating the server
        core.Tag.add(self.web_app_server, key="CustomLogGroup", value=f"{self.stream_producer_lg.log_group_name}",
                     include_resource_types=[])

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  "ApplicationServerUrl",
                                  value=f'http://{self.web_app_server.instance_public_ip}',
                                  description=f"Appication Serer url, http://<EC2_IP_ADDRESS>"
                                  )
