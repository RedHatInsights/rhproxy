#!/usr/bin/python3
#
# Merrily purloined from RedHatQE/rhui4-automation and modified for Insights Proxy!
#
""" Create CloudFormation stack """

import os
import socket
import argparse
import time
import logging
import sys
import random
import string
import json
import re

import boto3
import yaml

instance_types = {"arm64": "t4g.small", "x86_64": "t2.small"}

argparser = argparse.ArgumentParser(description='Create CloudFormation stack for Insights proxy',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

argparser.add_argument('--name', help='common name for stack members', default=time.strftime("%Y%m%d"))
argparser.add_argument('--cli8', help='number of RHEL8 clients', type=int, default=1)
argparser.add_argument('--cli8-arch', help='RHEL 8 clients\' architectures (comma-separated list)', default='x86_64', metavar='ARCH')
argparser.add_argument('--cli9', help='number of RHEL9 clients', type=int, default=1)
argparser.add_argument('--cli9-arch', help='RHEL 9 clients\' architectures (comma-separated list)', default='x86_64', metavar='ARCH')
argparser.add_argument('--cli10', help='number of RHEL10 clients', type=int, default=1)
argparser.add_argument('--cli10-arch', help='RHEL 10 clients\' architectures (comma-separated list)', default='x86_64', metavar='ARCH')
argparser.add_argument('--server-arch', default="x86_64", help='use this architecture for the proxy server')
argparser.add_argument('--input-conf', default="/etc/ec2.yaml", help='use supplied yaml config file')
argparser.add_argument('--output-conf', help='output file')
argparser.add_argument('--region', default="eu-west-1", help='use specified region')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug mode')
argparser.add_argument('--dry-run', action='store_const', const=True,
                       default=False, help='only validate the data and print what would be used')
argparser.add_argument('--timeout', type=int,
                       default=10, help='stack creation timeout (in minutes)')

argparser.add_argument('--vpcid', help='VPCid (overrides the configuration for the region)')
argparser.add_argument('--subnetid', help='Subnet id (for VPC) (overrides the configuration for the region)')
argparser.add_argument('--novpc', help='do not use VPC, use EC2 Classic', action='store_const', const=True, default=False)

argparser.add_argument('--ami-8-override', help='RHEL 8 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ami-9-override', help='RHEL 9 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ami-10-override', help='RHEL 10 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ami-8-arm64-override', help='RHEL 8 ARM64 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ami-9-arm64-override', help='RHEL 9 ARM64 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ami-10-arm64-override', help='RHEL 10 ARM64 AMI ID to override the mapping', metavar='ID')
argparser.add_argument('--ansible-ssh-extra-args', help='Extra arguments for SSH connections established by Ansible', metavar='ARGS')
argparser.add_argument('--key-pair-name', help='the name of the key pair in the given AWS region, if your local user name differs and SSH configuraion is undefined in the yaml config file')

args = argparser.parse_args()

if args.server_arch not in instance_types:
    logging.error(f'Invalid server arch \'{args.server_arch}\'. Use one of: {list(instance_types.keys())}.')
    sys.exit(1)

if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

REGION = args.region

logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

if (args.vpcid and not args.subnetid) or (args.subnetid and not args.vpcid):
    logging.error("vpcid and subnetid parameters should be set together!")
    sys.exit(1)
if args.novpc:
    instance_types["x86_64"] = "m3.large"

try:
    with open(args.input_conf, 'r') as confd:
        valid_config = yaml.safe_load(confd)

    if "ssh" in valid_config.keys() and REGION in valid_config["ssh"].keys():
        (ssh_key_name, ssh_key) = valid_config["ssh"][REGION]
    else:
        ssh_key = False
        ssh_key_name = args.key_pair_name or os.getlogin()
    ec2_name = re.search("[a-zA-Z]+", ssh_key_name).group(0)
    if not args.novpc:
        (vpcid, subnetid) = (args.vpcid, args.subnetid) if args.vpcid else valid_config["vpc"][REGION]

except Exception as e:
    logging.error("got '%s' error processing: %s", e, args.input_conf)
    logging.error("Please, check your config or and try again")
    sys.exit(1)

json_dict = {}

json_dict['AWSTemplateFormatVersion'] = '2010-09-09'

if args.cli8 == -1:
    args.cli8 = len(instance_types)
    args.cli8_arch = ",".join(instance_types.keys())
if args.cli9 == -1:
    args.cli9 = len(instance_types)
    args.cli9_arch = ",".join(instance_types.keys())
if args.cli10 == -1:
    args.cli10 = len(instance_types)
    args.cli10_arch = ",".join(instance_types.keys())


proxy_os = "RHEL9"

json_dict['Description'] = "Insights proxy stack"

json_dict['Mappings'] = {u'RHEL8': {args.region: {}},
                         u'RHEL9': {args.region: {}},
                         u'RHEL10': {args.region: {}}}

cli_os_versions = (8, 9, 10)

try:
    for i in cli_os_versions:
        if override := args.__getattribute__(f"ami_{i}_override"):
            json_dict["Mappings"][f"RHEL{i}"][args.region]["AMI"] = override
        else:
            with open(f"RHEL{i}mapping.json") as mjson:
                mapping = json.load(mjson)
                json_dict["Mappings"][f"RHEL{i}"] = mapping
except Exception as e:
    sys.stderr.write("Got '%s' error \n" % e)
    sys.exit(1)

def concat_name(node='', cfgfile=False):
    return '_'.join(filter(None,
                           ['hosts' if cfgfile else ec2_name,
                            'insights_proxy',
                            args.name,
                            node])
                    ) + ('.cfg' if cfgfile else '')

json_dict['Parameters'] = \
{u'KeyName': {u'Description': u'Name of an existing EC2 KeyPair to enable SSH access to the instances',
              u'Type': u'String'}}

json_dict['Resources'] = \
{u'IPPsecuritygroup': {u'Properties': {u'GroupDescription': u'Insights proxy security group',
                                        u'SecurityGroupIngress': [{u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'22',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'22'},
                                                                   {u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'8443',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'8443'},
                                                                   {u'CidrIp': u'0.0.0.0/0',
                                                                   u'FromPort': u'3128',
                                                                   u'IpProtocol': u'tcp',
                                                                   u'ToPort': u'3128'}]},
                        u'Type': u'AWS::EC2::SecurityGroup'}}

# Insights proxy
mapping_file = 'RHEL9mapping.json' if args.server_arch == 'x86_64' else f"RHEL9mapping_{args.server_arch}.json"
#if args.server_arch == "x86_64":
#    image_id = {u'Fn::FindInMap': [os, {u'Ref': u'AWS::Region'}, u'AMI']}
#else:
#    with open(f"RHEL9mapping_{args.server_arch}.json") as mjson:
with open(mapping_file) as mjson:
       image_ids =  json.load(mjson)
       image_id = image_ids[args.region]["AMI"]

json_dict['Resources']["proxy"] = \
    {u'Properties': {u'ImageId': image_id,
                           u'InstanceType': instance_types[args.server_arch],
                           u'KeyName': {u'Ref': u'KeyName'},
                           u'SecurityGroups': [{u'Ref': u'IPPsecuritygroup'}],
                           u'Tags': [{u'Key': u'Name', u'Value': concat_name(u'proxy')},
                                     {u'Key': u'Role', u'Value': u'Proxy'},
                                     ]},
               u'Type': u'AWS::EC2::Instance'}

# clients
for i in cli_os_versions:
    if num_cli_ver := args.__getattribute__(f"cli{i}"):
        os = f"RHEL{i}"
        for j in range(1, num_cli_ver + 1):
            try:
                cli_arch = args.__getattribute__(f"cli{i}_arch").split(",")[j-1]
                if not cli_arch:
                    cli_arch = "x86_64"
            except (AttributeError, IndexError):
                cli_arch = "x86_64"
            try:
                # RHEL 6 can't run on m5
                instance_type = instance_types[cli_arch] if i >= 7 else 'm3.large' if args.novpc else 'i3.large'
            except KeyError:
                logging.error("Unknown architecture: %s" % cli_arch)
                sys.exit(1)
            if cli_arch == "x86_64":
                image_id = {u'Fn::FindInMap': [os, {u'Ref': u'AWS::Region'}, u'AMI']}
            else:
                if args.novpc:
                    logging.error("EC2 Classic can only be used with x86_64 instances.")
                    logging.error("Stack creation would fail. Quitting.")
                    sys.exit(1)
                if i == 8 and args.ami_8_arm64_override:
                    image_id = args.ami_8_arm64_override
                elif i == 9 and args.ami_9_arm64_override:
                    image_id = args.ami_9_arm64_override
                elif i == 10 and args.ami_10_arm64_override:
                    image_id = args.ami_10_arm64_override
                else:
                    with open("RHEL%smapping_%s.json" % (i, cli_arch)) as mjson:
                       image_ids =  json.load(mjson)
                       image_id = image_ids[args.region]["AMI"]
            json_dict['Resources']["cli%inr%i" % (i, j)] = \
                {u'Properties': {u'ImageId': image_id,
                                   u'InstanceType': instance_type,
                                   u'KeyName': {u'Ref': u'KeyName'},
                                   u'SecurityGroups': [{u'Ref': u'IPPsecuritygroup'}],
                                   u'Tags': [{u'Key': u'Name', u'Value': concat_name(u'cli%i_%i' % (i, j))},
                                             {u'Key': u'Role', u'Value': u'CLI'},
                                             {u'Key': u'OS', u'Value': u'%s' % os[:5]}]},
                   u'Type': u'AWS::EC2::Instance'}

if not args.novpc:
    # Setting VpcId and SubnetId
    json_dict['Outputs'] = {}
    for key in list(json_dict['Resources']):
        # We'll be changing dictionary so retyping to a list is required to ensure compatibility with Python 3.7+.
        if json_dict['Resources'][key]['Type'] == 'AWS::EC2::SecurityGroup':
            json_dict['Resources'][key]['Properties']['VpcId'] = vpcid
        elif json_dict['Resources'][key]['Type'] == 'AWS::EC2::Instance':
            json_dict['Resources'][key]['Properties']['SubnetId'] = subnetid
            json_dict['Resources'][key]['Properties']['SecurityGroupIds'] = json_dict['Resources'][key]['Properties'].pop('SecurityGroups')
            json_dict['Resources']["%sEIP" % key] = \
            {
                "Type" : "AWS::EC2::EIP",
                "Properties" : {"Domain" : "vpc",
                                "InstanceId" : {"Ref" : key}
                               }
            }


json_dict['Outputs'] = {}

json_body = json.dumps(json_dict, indent=4)

STACK_ID = "STACK-IPP-%s-%s-%s" % (ec2_name, args.name, ''.join(random.choice(string.ascii_lowercase) for x in range(10)))
logging.info("Creating stack with ID " + STACK_ID)

parameters = [{"ParameterKey": "KeyName", "ParameterValue": ssh_key_name}]

if args.dry_run:
    print("Dry run.")
    print("This would be the template:")
    print(json_body)
    print("This would be the parameters:")
    print(parameters)
    sys.exit(0)

cf_client = boto3.client("cloudformation", region_name=args.region)
cf_client.create_stack(StackName=STACK_ID,
                       TemplateBody=json_body,
                       Parameters=parameters,
                       TimeoutInMinutes=args.timeout)

is_complete = False
success = False
while not is_complete:
    time.sleep(10)
    response = cf_client.describe_stacks(StackName=STACK_ID)
    status = response["Stacks"][0]["StackStatus"]
    if status == "CREATE_IN_PROGRESS":
        continue
    if status == "CREATE_COMPLETE":
        logging.info("Stack creation completed")
        is_complete = True
        success = True
    elif status in ("ROLLBACK_IN_PROGRESS", "ROLLBACK_COMPLETE"):
        logging.info("Stack creation failed: %s", status)
        is_complete = True
    else:
        logging.error("Unexpected stack status: %s", status)
        break

if not success:
    print("Review the stack in the CloudFormation console and diagnose the reason.")
    print("Be sure to delete the stack. Even stacks that were rolled back still consume resources!")
    sys.exit(1)

# obtain information about the stack
resources = cf_client.describe_stack_resources(StackName=STACK_ID)
# create a dict with items such as proxy1EIP: 50:60:70:80
ip_addresses = {resource["LogicalResourceId"]: resource["PhysicalResourceId"] \
                for resource in resources['StackResources'] \
                if resource["ResourceType"] == "AWS::EC2::EIP"}
# create another, more useful dict with roles: hostnames
hostnames = {lri.replace("EIP", ""): socket.getfqdn(ip) \
             for lri, ip in ip_addresses.items()}
# also create a list of instance IDs to print in the end
instance_ids = [resource["PhysicalResourceId"] \
                for resource in resources['StackResources'] \
                if resource["ResourceType"] == "AWS::EC2::Instance"]

# output file
if args.output_conf:
    outfile = args.output_conf
else:
    outfile = concat_name(cfgfile=True)

try:
    with open(outfile, 'w') as f:
        # proxy
        f.write('[PROXY]\n')
        for role, hostname in hostnames.items():
            if role.startswith("proxy"):
                f.write(hostname)
                if ssh_key:
                    f.write(' ansible_ssh_private_key_file=%s' % ssh_key)
                if args.ansible_ssh_extra_args:
                    f.write(' ansible_ssh_extra_args="%s"' % args.ansible_ssh_extra_args)
                f.write('\n')
        # cli
        f.write('\n[CLI]\n')
        for role, hostname in hostnames.items():
            if role.startswith("cli"):
                f.write(hostname)
                if ssh_key:
                    f.write(' ansible_ssh_private_key_file=%s' % ssh_key)
                if args.ansible_ssh_extra_args:
                    f.write(' ansible_ssh_extra_args="%s"' % args.ansible_ssh_extra_args)
                f.write('\n')

except Exception as e:
    logging.error("got '%s' error processing: %s", e, args.output_conf)
    sys.exit(1)

print("Instance IDs:")
print(" ".join(instance_ids))
print(f"Inventory file contents ({outfile}):")
with open(outfile, encoding="utf-8") as outfile_fd:
    print(outfile_fd.read())
