#!/bin/bash -xe

# version: 04Apr2020

##################################################
#############     SET GLOBALS     ################
##################################################

GIT_REPO_URL="https://github.com/miztiik/stream-data-processor.git"


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

function install_libs(){
    # Prepare the server for python3
    yum -y install python-pip python3 git
    yum install -y jq
    pip3 install boto3
}

install_libs
