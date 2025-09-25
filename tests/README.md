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
systems running RHEL 8 and 9, both using x86\_64. The current date (YYYYMMDD) is used for the name.

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
offline_token=<YOUR OFFLINE API TOKEN GENERATED AT https://access.redhat.com/management/api>

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

### Examples

Here are a few examples demonstrating alternative ways to run the test suite.

#### Preparing the systems and leaving them in this state

If you only want to set the environment up because you wish to keep it running:

```
$ ansible-playbook -i hosts_insights_proxy_20250205.cfg test.yml --tags subscribe,build_firewall,rpm_install,user_create,user_login,service_install,service_start,service_status,fetch_helper,run_helper
```

In this case, don't forget to unsubscribe the systems from RHSM before you terminate them. If the
complete playbook is run, this happens automatically during the final cleanup, unless a task fails.

#### Overriding the rhproxy RPM

If you want to test an rhproxy RPM different from the one in RHSM, you can supply a local
(pre-downloaded) RPM, or you can specify a URL that's reachable from the proxy node. Such a
non-default RPM may even be unsigned or signed with an unknown key. To use this feature, run the
`ansible-playbook` command with extra variables as follows:

```
--extra-vars "rpm_override=/tmp/rhproxy-V-R.noarch.rpm unsigned=True"
```

or:

```
--extra-vars "rpm_override=http://example.com/rhproxy-V-R.noarch.rpm unsigned=True"
```

#### Overriding the rhproxy engine

You can also override the image path in the quadlet service file if you want to pull an image that
differs from the one in this file: for example, to pull a new test image at Quay while testing an
rhproxy RPM build that uses the Red Hat registry. To do so, add the following extra variable:

```
--extra-vars "image_override=quay.io/insights_proxy/rhproxy-engine:X.Y.Z registry_alias=quay"
```

(don't forget about the registry alias to make sure the proxy node gets logged in to Quay) or:

```
--extra-vars "image_override=registry.redhat.io/insights-proxy/insights-proxy-container-rhel9:X.Y.Z"
```

#### Checking the rhproxy engine version

If you want to be really sure that a particular engine version is pulled, you can specify this
version and let the test suite compare it with the running version. To do so, use:

```
--extra-vars "expected_engine_version=X.Y.Z"
```

Note: This is actually done by checking the image tag.

#### Checking if certain RPMs are installed in the container

Common Vulnerabilities and Exposures (CVEs) affect every distribution, and in turn every container
image, including Insights proxy becomes vulnerable easily. To address the CVEs, the Insights proxy
container image must often be recreated with a newer version of the underlying UBI containing
updates that resolve recent CVEs.

By default, the test suite collects a list of all installed RPMs from the container, saves it on
the proxy server host, and also fetches it to the Ansible control node. The file location is
`/tmp/rhproxy_container_rpms` on both the server and the control node, and no action is taken with
either copy of the list. If you want, you can examine it at your convenience.

In addition, though, you can have the test suite check if one or more RPMs, specified as
`name-version-release`, are actually installed in the container, making it safe from the known
recent vulnerabilities. To do so, use the `check_rpms` extra variable and set it to a
comma-separated list of NVRs that are known to contain fixes for the recent CVEs. For example,
with Insights proxy container version 1.5.6, you could use:

```
--extra-vars check_rpms=libarchive-3.5.3-6.el9_6,libxml2-2.9.13-12.el9_6
```

Caveat lector: the exact strings are checked for; if a newer version/release of any of these
packages is installed, the test will fail even though the container is (supposedly) still
invulnerable.

## Notes
To enable logging for easier sharing of the output, run the `ansible-playbook` command with
`ANSIBLE_LOG_PATH=/some/file`.
