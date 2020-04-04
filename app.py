#!/usr/bin/env python3

from aws_cdk import core

from stream_data_processor.stream_data_processor_stack import StreamDataProcessorStack


app = core.App()
StreamDataProcessorStack(app, "stream-data-processor")

app.synth()
