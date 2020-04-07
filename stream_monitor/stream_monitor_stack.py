from aws_cdk import aws_cloudwatch as _cloudwatch
from aws_cdk import aws_logs as _logs
from aws_cdk import core


class global_args:
    """ Helper to define global statics """
    OWNER = "MystiqueAutomation"
    REPO_NAME = "stream-data-processor"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_04_06"
    POLYGLOT_SUPPORT_EMAIL = ["mystique@example.com", ]


class streamMonitorStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, stream_producer_lg, stream_record_processor_fn, stream_record_processor_fn_2, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ):
        ##### MONITORING ######

        ##################################################
        ##########    STREAM PRODUCER METRICS    #########
        ##################################################
        # JSON Metric Filter - https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

        records_produced_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
            dimensions=[
                "records_produced",
                "records_produced"
            ],
            metric_name="recordsProducedCount",
            label="Total No. Of Records Produced",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )

        records_produced_metric_filter = _logs.MetricFilter(self, "recordsProducedCountFilter",
                                                            filter_pattern=_logs.FilterPattern.exists(
                                                                "$.records_produced"),
                                                            log_group=stream_producer_lg,
                                                            metric_namespace=records_produced_metric.namespace,
                                                            metric_name=records_produced_metric.metric_name,
                                                            default_value=0,
                                                            metric_value="$.records_produced",
                                                            )

        ##################################################
        ##########    STREAM CONSUMER METRICS    #########
        ##################################################

        records_processed_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
            # dimensions=[_cloudwatch.Dimension(
            #     name="records_processed",
            #     value="records_processed"
            # )],
            dimensions=[
                "records_processed",
                "records_processed"
            ],
            metric_name="recordsProcessedCount",
            label="Total No. Of Records Processed",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )

        records_processed_metric_filter_01 = _logs.MetricFilter(self, "processedRecordCountFilter01",
                                                                filter_pattern=_logs.FilterPattern.exists(
                                                                    "$.records_processed"),
                                                                log_group=stream_record_processor_fn.log_group,
                                                                metric_namespace=records_processed_metric.namespace,
                                                                metric_name=records_processed_metric.metric_name,
                                                                default_value=0,
                                                                metric_value="$.records_processed",
                                                                )

        records_processed_metric_filter_02 = _logs.MetricFilter(self, "processedRecordCountFilter02",
                                                                filter_pattern=_logs.FilterPattern.exists(
                                                                    "$.records_processed"),
                                                                log_group=stream_record_processor_fn_2.log_group,
                                                                metric_namespace=records_processed_metric.namespace,
                                                                metric_name=records_processed_metric.metric_name,
                                                                default_value=0,
                                                                metric_value="$.records_processed",
                                                                )

        # Create CloudWatch Dashboard for Streams
        stream_processor_dashboard = _cloudwatch.Dashboard(self,
                                                           id="streamProcessorDashboard",
                                                           dashboard_name="Stream-Processor"
                                                           )

        stream_processor_dashboard.add_widgets(
            _cloudwatch.SingleValueWidget(
                title="TotalRecordsProcessed",
                metrics=[records_processed_metric]
            )
        )

        stream_processor_dashboard.add_widgets(
            _cloudwatch.SingleValueWidget(
                title="TotalRecordsProduced",
                metrics=[records_produced_metric]
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
