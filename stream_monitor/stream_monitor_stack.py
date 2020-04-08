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

    def __init__(self, scope: core.Construct, id: str,
                 stream_producer_lg,
                 stream_pipe,
                 py_stream_record_processor_fn,
                 node_stream_record_processor_fn,
                 ** kwargs
                 ) -> None:
        super().__init__(scope, id, **kwargs)

        # ):
        ##### MONITORING ######

        ##################################################
        ##########        STREAM  METRICS        #########
        ##################################################

        # Shows you the ingestion rate into the shard.
        stream_in_bytes_metric = _cloudwatch.Metric(
            namespace="AWS/Kinesis",
            metric_name="IncomingBytes",
            dimensions={
                "StreamName": f"{stream_pipe.stream_name}"
            },
            label="IncomingBytes",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )
        stream_in_records_metric = _cloudwatch.Metric(
            namespace="AWS/Kinesis",
            metric_name="IncomingRecords",
            dimensions={
                "StreamName": f"{stream_pipe.stream_name}"
            },
            label="IncomingRecords",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )
        stream_w_throttle_metric = _cloudwatch.Metric(
            namespace="AWS/Kinesis",
            metric_name="WriteProvisionedThroughputExceeded",
            dimensions={
                "StreamName": f"{stream_pipe.stream_name}"
            },
            label="WriteProvisionedThroughputExceeded",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )
        stream_r_throttle_metric = _cloudwatch.Metric(
            namespace="AWS/Kinesis",
            metric_name="ReadProvisionedThroughputExceeded",
            dimensions={
                "StreamName": f"{stream_pipe.stream_name}"
            },
            label="ReadProvisionedThroughputExceeded",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )

        ##################################################
        ##########    STREAM PRODUCER METRICS    #########
        ##################################################
        # JSON Metric Filter - https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

        records_produced_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
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

        py_records_processed_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
            # dimensions={
            #     "RecordsProcessed": "py_processor"
            # },
            metric_name="pyRecordsProcessedCount",
            label="Total No. Of Records Processed",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )

        py_stream_record_processor = _logs.MetricFilter(self, "processedRecordCountFilter01",
                                                        filter_pattern=_logs.FilterPattern.exists(
                                                            "$.records_processed"),
                                                        log_group=py_stream_record_processor_fn.log_group,
                                                        metric_namespace=py_records_processed_metric.namespace,
                                                        metric_name=py_records_processed_metric.metric_name,
                                                        default_value=0,
                                                        metric_value="$.records_processed",
                                                        )
        node_records_processed_metric = _cloudwatch.Metric(
            namespace=f"{global_args.OWNER}-stream-data-processor",
            metric_name="nodeRecordsProcessedCount",
            label="Total No. Of Records Processed",
            period=core.Duration.minutes(30),
            statistic="Sum"
        )
        node_stream_record_processor = _logs.MetricFilter(self, "processedRecordCountFilter02",
                                                                filter_pattern=_logs.FilterPattern.exists(
                                                                    "$.records_processed"),
                                                                log_group=node_stream_record_processor_fn.log_group,
                                                                metric_namespace=node_records_processed_metric.namespace,
                                                                metric_name=node_records_processed_metric.metric_name,
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
                title="TotalRecordsProduced",
                metrics=[records_produced_metric]
            )
        )

        # Stream Incoming bytes Graph
        stream_processor_dashboard.add_widgets(
            _cloudwatch.Row(
                _cloudwatch.Column(
                    _cloudwatch.GraphWidget(
                        title="Stream Ingestion Metrics",
                        left=[stream_in_bytes_metric],
                        right=[stream_in_records_metric]
                    )
                ),
                _cloudwatch.Column(
                    _cloudwatch.GraphWidget(
                        title="Stream Throttle Metrics",
                        left=[stream_w_throttle_metric],
                        right=[stream_r_throttle_metric]
                    )
                )
            )
        )

        stream_processor_dashboard.add_widgets(
            _cloudwatch.SingleValueWidget(
                title="RecordsProcessed-by-Python-Consumer",
                metrics=[py_records_processed_metric]
            )
        )
        stream_processor_dashboard.add_widgets(
            _cloudwatch.SingleValueWidget(
                title="RecordsProcessed-by-Node-Consumer",
                metrics=[node_records_processed_metric]
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
