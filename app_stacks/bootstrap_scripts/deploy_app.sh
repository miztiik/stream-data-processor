#!/bin/bash -xe

# version: 05Apr2020

##################################################
#############     SET GLOBALS     ################
##################################################

GIT_REPO_URL="https://github.com/miztiik/stream-data-processor.git"

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
    echo "AWS_REGION='$AWS_REGION'" >> "/var/stream-data-processor/app_stacks/bootstrap_scripts/constants.py"
    echo "STREAM_NAME='$STREAM_NAME'" >> "/var/stream-data-processor/app_stacks/bootstrap_scripts/constants.py"
}

function install_libs(){
    # Prepare the server for python3
    yum -y install python-pip python3 git
    yum install -y jq
    pip3 install boto3
}

install_libs
clone_git_repo
add_env_vars
python3 /var/stream-data-processor/app_stacks/bootstrap_scripts/kinesis_producer.py
