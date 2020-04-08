from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_cloudwatch as _cloudwatch
from aws_cdk import aws_logs as _logs
from aws_cdk import core


class global_args:
    """ Helper to define global statics """
    OWNER = "MystiqueAutomation"
    REPO_NAME = "stream-data-processor"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_04_05"
    POLYGLOT_SUPPORT_EMAIL = ["mystique@example.com", ]


class streamDataConsumerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, stream_arn, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Defines an AWS Lambda resource):
        ###########################################
        #####      KINESIS CONSUMER 1       #######
        ###########################################
        with open("stream_data_consumer/lambda_src/stream_record_processor.py", encoding="utf8") as fp:
            py_stream_record_processor_fn_handler_code = fp.read()
        self.py_stream_record_processor_fn = _lambda.Function(
            self,
            id='pyStreamDataProcessor',
            function_name="py_stream_record_processor_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                py_stream_record_processor_fn_handler_code),
            handler='index.lambda_handler',
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "WARNING"
            }
        )

        # Add permissions to lambda to read Kinesis
        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[f"{stream_arn}"],
            actions=[
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:ListStreams",
                "kinesis:DescribeStream",
            ]
        )
        roleStmt1.sid = "AllowKinesisToTriggerLambda"
        self.py_stream_record_processor_fn.add_to_role_policy(roleStmt1)

        self.py_stream_record_processor_fn.add_event_source_mapping("dataPipeConsumer",
                                                                    event_source_arn=stream_arn,
                                                                    batch_size=2,
                                                                    enabled=True,
                                                                    starting_position=_lambda.StartingPosition.TRIM_HORIZON
                                                                    )
        ###########################################
        #####      KINESIS CONSUMER 2       #######
        ###########################################
        with open("stream_data_consumer/lambda_src/stream_record_processor.js", encoding="utf8") as fp:
            node_stream_record_processor_fn_handler_code = fp.read()
        self.node_stream_record_processor_fn = _lambda.Function(
            self,
            id='streamDataProcessor2',
            function_name="node_stream_record_processor_fn",
            runtime=_lambda.Runtime.NODEJS_12_X,
            code=_lambda.InlineCode(
                node_stream_record_processor_fn_handler_code),
            handler='index.handler',
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )

        self.node_stream_record_processor_fn.add_to_role_policy(roleStmt1)

        self.node_stream_record_processor_fn.add_event_source_mapping("dataPipeConsumer",
                                                                      event_source_arn=stream_arn,
                                                                      batch_size=2,
                                                                      enabled=True,
                                                                      starting_position=_lambda.StartingPosition.TRIM_HORIZON
                                                                      )

        ###########################################
        ################# OUTPUTS #################
        ###########################################

        output_0 = core.CfnOutput(self,
                                  "SecuirtyAutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )
