# Insights proxy tests

## About
This is the test suite for Insights proxy. Test cases are written as Ansible tasks that are
executed on the proxy server and a client machine. This pair of systems must be launched
beforehand.

A script is provided to facilitate the creation of test systems in AWS, including the correct
security group settings. It creates an inventory file which is then used by the Ansible playbook.

## Requirements
* Ansible
* Red Hat account
* Optionally, if using test systems in AWS:
    * RPMS: python3-boto awscli2
    * AWS credentials; run `aws configure` to obtain access keys
    * `~/.ssh/config` with the configuration for EC2 VMs
    * `/etc/ec2.yaml` with VPC data, format: `region: [VPC ID, subnet ID]` under `vpc`

Examples:

SSH configurtion:

```
Host *.amazonaws.com
    User ec2-user
    IdentityFile ~/.ssh/id_rsa_or
```

VPC configuration:

```
vpc:
  eu-west-1: [vpc-123abc, subnet-456def]
  us-east-1: [vpc-0099ff, subnet-eeda11]
```

Note: these VPCs and subnets must exist in your AWS acount first.

* If not using AWS:
    * One RHEL 9 system for the proxy server and one supported client, e.g. also running RHEL 9.
    * An inventory file with `[PROXY]` and `[CLI]` groups with the hostnames inside.

Example:

```
[PROXY]
proxy.example.com

[CLI]
cli01.example.com
```

## Creating a CloudFormation Stack in AWS
Note: skip this step if not using AWS.

Run the provided script:

```
$ ./create-cf-stack.py
```

With no arguments, it creates a stack with a RHEL 9 x86\_64 system for the proxy and two more client
sytems running RHEL 8 and 9, both using x86\_64. The current date (YYYYMMDD) is used for the name.

See the output from `--help` for more information. Notably, you may wish to use a different region,
name, architecture for the proxy server, or change the number of RHEL 9 or 8 clients (even to 0).

`RHEL*.json` files are provided to automate the selection of the AMIs. AMI IDs can be overridden
on the command line or changed in these JSON files.

When this script has finished, it creates an inventory file called
`hosts_insights_proxy_<NAME>.cfg` and also prints its contents.

## Creating the file with credentials
Create the `credentials.conf` file, in this very directory, as follows:

```
[rh]
username=<YOUR RED HAT USERNAME>
password=<YOUR RED HAT PASSWORD>

[quay]
username=<YOUR QUAY USERNAME>
password=<YOUR QUAY PASSWORD>
```

This data is used in order to register the systems to RHSM (to be able to access the Insights proxy
dnf repository and install the RPM), and to log in to the registry that the proxy container is in.

The credentials for Quay are only needed if testing unreleased versions from Quay. However, in that
case you're going to need a scratch build of the rhproxy RPM that pulls the image from Quay, too.

## Running the test suite
As simple as:

```
$ ansible-playbook -i <INVENTORY FILE> test.yml
```

See the tags in the individual YAML files in subdirectories. If you only want to run some tasks,
use the relevant tags, comma separated, as the argument of `--tags`.

Test data is kept in `group_vars/all.yml`.
Any variable can be overridden on the command line.
In addition, two more variables are used in the code and can be set to a non-default value.

### Example

If you only want to set the environment up because you wish to keep it running:

```
$ ansible-playbook -i hosts_insights_proxy_20250205.cfg test.yml --tags subscribe,build_firewall,rpm_install,user_create,user_login,service_install,service_start,service_status,fetch_helper,run_helper
```

In this case, don't forget to unsubscribe the systems from RHSM before you terminate them. If the
complete playbook is run, this happens automatically during the final cleanup, unless a task fails.

If you want to test an unsigned RPM that uses an image from quay.io, use the following argument
on the `ansible-playbook` command line:

```
--extra-vars "local_rpm=<PATH_TO_LOCAL_RHPROXY_RPM> unsigned=True registry_alias=quay"
```

The RPM must exist on the system where the playbook was launched, and it will be copied to the
proxy node. Alternatively, if the RPM is reachable from the proxy node using a URL, set the
`rpm_name` variable to this URL; also use `unsigned=True` if this RPM isn't signed.

You can also override the image path in the quadlet service file if you want to pull an image that
differs from the one in this file: for example, to pull a new test image at Quay while testing an
rhproxy RPM build that uses the Red Hat registry. To do so, add the following extra variable:

```
image_override=<REGISTRY_HOST/IMAGE_PATH:VERSION>
```

## Notes
To enable logging for easier sharing of the output, run the `ansible-playbook` command with
`ANSIBLE_LOG_PATH=/some/file`.
