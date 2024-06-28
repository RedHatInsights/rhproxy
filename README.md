# Installing Insights-Proxy

## Using the official RPM

Using the `insights-proxy` service controller, ***all commands*** for installing and interacting with Insights-Proxy should be executed as a *regular non-root* user. 

To use the service controller to install and manage the Insights-Proxy service, first install the controller:


```sh
# sudo dnf install -y insights-proxy
```

You must then run the insights-proxy service controller as a regular non-root user of the system.

Install the Insights-Proxy service:

```
$ insights-proxy install
```

Required before starting the Insights-Proxy service for pulling down the
service image from Quay.io:

```
$ podman login quay.io  
```


Start the Insights-Proxy service:
```
$ insights-proxy start
```

Display status of the Insights-Proxy service:
```
$ insights-proxy status
```

To allow external access to the Insights proxy, run the following commands:

```sh
# sudo firewall-cmd --permanent --add-port=3128/tcp 
# sudo firewall-cmd --reload
```

A few seconds later, you may proxy-forward Red-Hat Insights traffic to http://\<server-hosting-the-proxy\>:3128

When running Insights-Proxy, a self-signed certificate is created for accessing any resources served by the proxy 
nd is stored in the host's `~/.local/share/insights-proxy/certs/` directory. You may provide your own
HTTPS certificate and key in this location before starting the Insights-Proxy:

- `~/.local/share/insights-proxy/certs/insights-proxy.crt`
- `~/.local/share/insights-proxy/certs/insights-proxy.key`

The usage of the insights-proxy service controller is included here below:

```
Usage: insights-proxy [-v | --verbose] <command>

Where <command> is one of:
  install                  - Install Insights-Proxy
  uninstall                - Uninstall Insights-Proxy
  start                    - Start the Insights-Proxy Service
  stop                     - Stop the Insights-Proxy Service
  restart                  - Re-start the Insights-Proxy Service
  status                   - Display Status of the Insights-Proxy Service
```

