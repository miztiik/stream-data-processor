#!/usr/bin/env python3

from aws_cdk import core

from stream_data_pipe.stream_data_pipe_stack import StreamDataPipeStack
from stream_data_producer.vpc_stack import VpcStack
from stream_data_producer.stream_data_producer_stack import streamDataProducerStack
from stream_data_consumer.stream_data_consumer_stack import streamDataConsumerStack

app = core.App()

# Kinesis Data Stream Processor Stack
stream_pipe = StreamDataPipeStack(
    app, "stream-data-pipe", description="Kinesis Streams for recieving streaming data")


# VPC Stack for hosting EC2 & Other resources
vpc_stack = VpcStack(app, "web-app-vpc-stack",
                     description="VPC Stack for hosting EC2 & Other resources"
                     )

# Kinesis Data Producer on EC2
stream_producer = streamDataProducerStack(
    app, "stream-data-producer-stack",
    vpc=vpc_stack.vpc,
    stream_arn=stream_pipe.kinesis_data_pipe.stream_arn,
    data_pipe_ssm_param=stream_pipe.data_pipe_ssm_param,
    description="Web App: Kinesis Data Producer on EC2 Stack"
)


# Kinesis Data Stream Consumer Stack
stream_consumer = streamDataConsumerStack(
    app, "stream-data-consumer-stack",
    stream_arn=stream_pipe.kinesis_data_pipe.stream_arn,
    description="Kinesis Data Stream Consumer Stack"
)


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
