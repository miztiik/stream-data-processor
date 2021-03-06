from aws_cdk import core
from aws_cdk import aws_kinesis as _kinesis
from aws_cdk import aws_ssm as _ssm


class global_args:
    """
    Helper to define global statics
    """
    OWNER = "MystiqueAutomation"
    REPO_NAME = "stream-data-processor"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_04_04"
    POLYGLOT_SUPPORT_EMAIL = ["mystique@example.com", ]


class StreamDataPipeStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, shard_count: int, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here):
        ##############################################
        #######   CDK STABILITY EXPERIMENTAL   #######
        ##############################################

        self.kinesis_data_pipe = _kinesis.Stream(
            self,
            "dataPipe",
            # retention_period_hours=24,
            # retention_period=core.Duration.minutes(300),
            shard_count=1,
            stream_name="data_pipe"
        )

        self.data_pipe_ssm_param = _ssm.StringParameter(self, "dataPipeParameter",
                                                        description="Kinesis Stream Name",
                                                        parameter_name=f"/{global_args.REPO_NAME}/streams/data_pipe/stream_name",
                                                        string_value=f"{self.kinesis_data_pipe.stream_name}"
                                                        )

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )
