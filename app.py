#!/usr/bin/env python3

from aws_cdk import core
from app_stacks.web_app_stack import webAppStack
from app_stacks.vpc_stack import VpcStack
from stream_data_processor.stream_data_processor_stack import StreamDataProcessorStack


app = core.App()

# Kinesis Data Stream Processor Stack
stream_processor = StreamDataProcessorStack(
    app, "stream-data-processor", description="Kinesis Streams for recieving streaming data")


# VPC Stack for hosting EC2 & Other resources
vpc_stack = VpcStack(app, "web-app-vpc-stack",
                     description="VPC Stack for hosting EC2 & Other resources"
                     )

# Web App: HTTP EndPoint on EC2 Stack
web_app_stack = webAppStack(
    app, "web-app-stack",
    vpc=vpc_stack.vpc,
    stream_name=stream_processor.kinesis_stream_pipe.stream_name,
    stream_arn=stream_processor.kinesis_stream_pipe.stream_arn,
    description="Web App: HTTP EndPoint on EC2 Stack")


# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="ToKnowMore",
             value=app.node.try_get_context('youtube_profile'))

app.synth()
