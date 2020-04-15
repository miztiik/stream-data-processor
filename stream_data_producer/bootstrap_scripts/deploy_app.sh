#!/bin/bash -xe

# version: 05Apr2020

##################################################
#############     SET GLOBALS     ################
##################################################

REPO_NAME="stream-data-processor"

GIT_REPO_URL="https://github.com/miztiik/$REPO_NAME.git"

APP_DIR="/var/$REPO_NAME"

# Send logs to console
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1


function install_xray(){
    # Install AWS XRay Daemon for telemetry
    curl https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.rpm -o /home/ec2-user/xray.rpm
    yum install -y /home/ec2-user/xray.rpm
}

function install_nginx(){
    echo 'Begin NGINX Installation'
    sudo amazon-linux-extras install -y nginx1.12
    sudo systemctl start nginx
}

function clone_git_repo(){
    install_libs
    # mkdir -p /var/
    cd /var
    git clone $GIT_REPO_URL

}

function add_env_vars(){
    EC2_AVAIL_ZONE=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
    AWS_REGION="`echo \"$EC2_AVAIL_ZONE\" | sed 's/[a-z]$//'`"
    export AWS_REGION
    echo "AWS_REGION='$AWS_REGION'" >> "$APP_DIR/stream_data_producer/bootstrap_scripts/constants.py"
    echo "STREAM_NAME='$STREAM_NAME'" >> "$APP_DIR/stream_data_producer/bootstrap_scripts/constants.py"
}

function install_libs(){
    # Prepare the server for python3
    yum -y install python-pip python3 git
    yum install -y jq
    pip3 install boto3
}

function install_nodejs(){
    # https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
    . ~/.nvm/nvm.sh
    nvm install node
    node -e "console.log('Running Node.js ' + process.version)"
}

function install_cw_agent() {
# Installing AWS CloudWatch Agent FOR AMAZON LINUX RPM
agent_dir="/tmp/cw_agent"
cw_agent_rpm="https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm"
mkdir -p ${agent_dir} \
    && cd ${agent_dir} \
    && sudo yum install -y curl \
    && curl ${cw_agent_rpm} -o ${agent_dir}/amazon-cloudwatch-agent.rpm \
    && sudo rpm -U ${agent_dir}/amazon-cloudwatch-agent.rpm


cw_agent_schema="/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json"

# PARAM_NAME="/stream-data-processor/streams/data_pipe/stream_name"
# a=$(aws ssm get-parameter --name "$PARAM_NAME" --with-decryption --query "Parameter.{Value:Value}" --output text)
# LOG_GROUP_NAME="/stream-data-processor/producers"

cat > '/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json' << "EOF"
{
"agent": {
    "metrics_collection_interval": 5,
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
},
"metrics": {
    "metrics_collected": {
    "mem": {
        "measurement": [
        "mem_used_percent"
        ]
    }
    },
    "append_dimensions": {
    "ImageId": "${aws:ImageId}",
    "InstanceId": "${aws:InstanceId}",
    "InstanceType": "${aws:InstanceType}"
    },
    "aggregation_dimensions": [
    [
        "InstanceId",
        "InstanceType"
    ],
    []
    ]
},
"logs": {
    "logs_collected": {
    "files": {
        "collect_list": [
        {
            "file_path": "/var/log/stream-data-processor",
            "log_group_name": "/stream-data-processor/producers",
            "timestamp_format": "%b %-d %H:%M:%S",
            "timezone": "Local"
        }
        ]
    }
    },
    "log_stream_name": "{instance_id}"
}
}
EOF

    # Configure the agent to monitor ssh log file
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:${cw_agent_schema} -s
    # Start the CW Agent
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status

    # Just in case we need to troubleshoot
    # cd "/opt/aws/amazon-cloudwatch-agent/logs/"
}


install_libs
clone_git_repo
add_env_vars
install_cw_agent
cd "$APP_DIR/stream_data_producer/bootstrap_scripts/"
python3 "$APP_DIR/stream_data_producer/bootstrap_scripts/kinesis_producer.py"
