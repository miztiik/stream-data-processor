from aws_cdk import core
from aws_cdk import aws_kinesis as _kinesis


class global_args:
    """
    Helper to define global statics
    """
    OWNER = "MystiqueAutomation"
    REPO_NAME = "stream-data-processor"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_04_04"
    POLYGLOT_SUPPORT_EMAIL = ["mystique@example.com", ]


class StreamDataProcessorStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here):

        ###########################################
        ################# OUTPUTS #################
        ###########################################

        self.kinesis_stream_pipe = _kinesis.Stream(
            self,
            "streamPipe",
            retention_period_hours=24,
            shard_count=1,
            stream_name="stream_pipe"
        )

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )
