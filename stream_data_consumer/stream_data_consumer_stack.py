from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_cloudwatch as _cloudwatch
from aws_cdk import aws_s3 as _s3
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
            stream_record_processor_fn_handler_code = fp.read()
        stream_record_processor_fn = _lambda.Function(
            self,
            id='streamDataProcessor',
            function_name="stream_record_processor_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(stream_record_processor_fn_handler_code),
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
        stream_record_processor_fn.add_to_role_policy(roleStmt1)

        stream_record_processor_fn.add_event_source_mapping("dataPipeConsumer",
                                                            event_source_arn=stream_arn,
                                                            batch_size=2,
                                                            enabled=True,
                                                            starting_position=_lambda.StartingPosition.TRIM_HORIZON
                                                            )
        ###########################################
        #####      KINESIS CONSUMER 2       #######
        ###########################################
        with open("stream_data_consumer/lambda_src/stream_record_processor.js", encoding="utf8") as fp:
            stream_record_processor_fn_2_handler_code = fp.read()
        stream_record_processor_fn_2 = _lambda.Function(
            self,
            id='streamDataProcessor2',
            function_name="stream_record_processor_fn_2",
            runtime=_lambda.Runtime.NODEJS_12_X,
            code=_lambda.InlineCode(stream_record_processor_fn_2_handler_code),
            handler='index.handler',
            timeout=core.Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )

        stream_record_processor_fn_2.add_to_role_policy(roleStmt1)

        stream_record_processor_fn_2.add_event_source_mapping("dataPipeConsumer",
                                                              event_source_arn=stream_arn,
                                                              batch_size=2,
                                                              enabled=True,
                                                              starting_position=_lambda.StartingPosition.TRIM_HORIZON
                                                              )
        ##### MONITORING ######
        # JSON Metric Filter - https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

        record_count_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
            metric_name="processedRecordCount",
            label="Total No. Of Records Processed",
            period=core.Duration.minutes(1),
            statistic="Sum"
        )

        record_count_metric_filter_01 = _logs.MetricFilter(self, "processedRecordCountFilter01",
                                                           filter_pattern=_logs.FilterPattern.exists(
                                                               "$.sum_of_records"),
                                                           log_group=stream_record_processor_fn.log_group,
                                                           metric_namespace=record_count_metric.namespace,
                                                           metric_name=record_count_metric.metric_name,
                                                           default_value=0,
                                                           metric_value="$.sum_of_records",
                                                           )

        record_count_metric_filter_02 = _logs.MetricFilter(self, "processedRecordCountFilter02",
                                                           filter_pattern=_logs.FilterPattern.exists(
                                                               "$.sum_of_records"),
                                                           log_group=stream_record_processor_fn_2.log_group,
                                                           metric_namespace=record_count_metric.namespace,
                                                           metric_name=record_count_metric.metric_name,
                                                           default_value=0,
                                                           metric_value="$.sum_of_records",
                                                           )

        # Create CloudWatch Dashboard for Polyglot Service Team
        stream_processor_dashboard = _cloudwatch.Dashboard(self,
                                                           id="streamProcessorDashboard",
                                                           dashboard_name="Stream-Processor"
                                                           )

        stream_processor_dashboard.add_widgets(
            _cloudwatch.SingleValueWidget(
                title="TotalRecordsProcessed",
                metrics=[record_count_metric]
            )
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################

        output_0 = core.CfnOutput(self,
                                  "SecuirtyAutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )
