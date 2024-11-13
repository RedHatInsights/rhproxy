# Installing the Insights proxy

First install the `rhproxy` RPM, this installs the service controller. You then use the service controller to install and manage the rhproxy service.

First, enable the appropriate repo then install the `rhproxy` RPM:


## Enabling the RPM Repo:

### For Tech Preview Builds:

#### X86_64

```sh
# sudo subscription-manager repos --enable insights-proxy-1-tech-preview-for-rhel9-x86_64-rpms
```

#### AARCH64

```sh
# sudo subscription-manager repos --enable insights-proxy-1-tech-preview-for-rhel9-aarch64-rpms
```

### For Upstream Release Builds:

Enable the [COPR release build repo](https://copr.fedorainfracloud.org/coprs/g/rhproxy/rhproxy/builds) with the appropriate \${arch} of _x86\_64_ or _aarch64_:


```sh
# sudo dnf copr enable @rhproxy/rhproxy rhel-9-${arch}
# sudo dnf config-manager --set-enabled copr:copr.fedorainfracloud.org:group_rhproxy:rhproxy
```

### For Upstream Latest Builds:

Enable the [COPR latest build repo](https://copr.fedorainfracloud.org/coprs/g/rhproxy/rhproxy-latest/builds) with the appropriate \${arch} of _x86\_64_ or _aarch64_:


```
# sudo dnf copr enable @rhproxy/rhproxy-latest rhel-9-${arch}
# sudo dnf config-manager --set-enabled copr:copr.fedorainfracloud.org:group_rhproxy:rhproxy-latest
```


## Install the latest RPM:

Install the latest rhproxy RPM:

```sh
# sudo dnf install -y rhproxy
```

# Running the Insights proxy

## Installing the Insights proxy service:

When using the `rhproxy` service controller, ***all commands*** for installing and interacting with Insights proxy should be executed as a *regular non-root* user of the system.

Install the rhproxy service:

```
$ rhproxy install
```

## Running the Insights proxy:

Start the rhproxy service:

```
$ rhproxy start
```

Display status of the rhproxy service:

```
$ rhproxy status
```

To allow external access to the Insights proxy, run the following commands:

```sh
# sudo firewall-cmd --permanent --add-port=3128/tcp
# sudo firewall-cmd --permanent --add-port=8443/tcp
# sudo firewall-cmd --reload
```

A few seconds later, you may proxy-forward Red-Hat Insights traffic to http://\<rhproxy-hostname\>:3128

When running the Insights proxy, a self-signed certificate is created for accessing any resources served by the proxy
and is stored in the host's `~/.local/share/rhproxy/certs/` directory. You may provide your own
HTTPS certificate and key in this location before starting the Insights proxy:

- `~/.local/share/rhproxy/certs/rhproxy.crt`
- `~/.local/share/rhproxy/certs/rhproxy.key`

The web server part of the Insights proxy can be accessed via https://\<rhproxy-hostname\>:8443

The download content area for the Insights proxy web server is located in the following location:

- `~/.local/share/rhproxy/download/`

The usage of the rhproxy service controller is included here below:

```
Usage: rhproxy [-v | --verbose] <command>

Where <command> is one of:
  install           - Install Insights proxy
  uninstall [-f]    - Uninstall Insights proxy
                      specify -f to force remove the certs and download data

  start             - Start the Insights proxy Service
  stop              - Stop the Insights proxy Service
  restart           - Re-start the Insights proxy Service
  status            - Display Status of the Insights proxy Service

  update            - Update download files
```

### Updating the rhproxy configuration



- The list of allowed upstream servers are provided in:
  - `~/.config/rhproxy/env/redhat.servers` for RedHat Insights Servers
  - `~/.config/rhproxy/env/epel.servers` for Dnf/Yum EPEL Servers

  These are replaced with rhproxy RPM updates so any manual updates to them will be lost.

The configuration of rhproxy can be updated as follows:

- Update the Insights proxy parameters in `~/.config/rhproxy/env/rhproxy.env`
- Provide optional Dnf/Yum servers in the following file:
  - `~/.config/rhproxy/env/mirror.servers`

  Updates to that file are presistent and not touched with rhproxy RPM updates.

then restart the service:

```
$ rhproxy restart
```

The configuration parameters include:

- `RHPROXY_DISABLE` to disable the forward proxying, _defaults to 0_
- `RHPROXY_DEBUG_CONFIG` to log environment variable and Nginx configuration upon startup, _defaults to 0_
- `RHPROXY_SERVICE_PORT` to define the listening port of the forward proxy, _defaults to 3128_
- `RHPROXY_DNS_SERVER` to define which DNS server to use for name resolution, _defaults to 1.1.1.1_
- `RHPROXY_WEB_SERVER_DISABLE` to disable the insights proxy web server, _defaults to 0_
- `RHPROXY_WEB_SERVER_PORT` to define the listening port of the insights proxy web server, _defaults to 8443_



