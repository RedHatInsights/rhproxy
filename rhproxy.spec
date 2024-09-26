%global base_version 1.3
%global patch_version 2

Name:           rhproxy
Version:        %{base_version}.%{patch_version}
Release:        1%{?dist}
Summary:        Insights Proxy Service v%{version}

License:        GPLv3
URL:            https://github.com/RedHatInsights/rhproxy
Source0:        %{url}/archive/%{version}.tar.gz

BuildArch:      noarch

Requires:       bash
Requires:       python3
Requires:       python3-pip

%description
This RPM installs the Insights Proxy Service on the System.
The rhproxy service controller installs and manages
the Insights Proxy via a systemd quadlet service.

%prep
%autosetup -n %{name}-%{version}

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_datadir}/%{name}/bin
cp bin/%{name} %{buildroot}/%{_bindir}/%{name}
cp bin/rhproxy-configure %{buildroot}/%{_datadir}/%{name}/bin/rhproxy-configure
cp bin/get-mirrors %{buildroot}/%{_datadir}/%{name}/bin/get-mirrors
mkdir -p %{buildroot}/%{_datadir}/%{name}/config
cp config/*.container %{buildroot}/%{_datadir}/%{name}/config/
mkdir -p %{buildroot}/%{_datadir}/%{name}/env
cp env/*.env %{buildroot}/%{_datadir}/%{name}/env/
cp env/*.servers %{buildroot}/%{_datadir}/%{name}/env/
mkdir -p %{buildroot}/%{_datadir}/%{name}/download/bin
cp download/bin/*.template %{buildroot}/%{_datadir}/%{name}/download/bin/

# Let's make sure we pick the major.minor released version of the engine
sed -i 's/{{RHPROXY_ENGINE_RELEASE_TAG}}/%{base_version}/' %{buildroot}/%{_datadir}/%{name}/config/rhproxy.container

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/bin/rhproxy-configure
%{_datadir}/%{name}/bin/get-mirrors
%{_datadir}/%{name}/config/rhproxy.container
%{_datadir}/%{name}/env/rhproxy.env
%{_datadir}/%{name}/env/redhat.servers
%{_datadir}/%{name}/env/mirror.servers
%{_datadir}/%{name}/download/bin/configure-client.sh.template

%changelog
* Thu Oct 17 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.2
- Now using URL based Source in the RPM spec

* Wed Sep 18 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.1
- Sharing rhproxy env directory with the rhproxy-engine
- No longer the need to create an env variable for the list of servers
- Now supporting redhat.servers and mirror.servers

* Tue Sep 17 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.0
- Moving to major.minor.patch version of the RPM.
- Moving to major.minor released versions of the container engine.

* Wed Aug 21 2024 Alberto Bellotti <abellott@redhat.com> - 1.3
- Renaming to rhproxy

* Tue Jul 02 2024 Alberto Bellotti <abellott@redhat.com> - 1.2
- Additional enhancements

* Fri Jun 28 2024 Alberto Bellotti <abellott@redhat.com> - 1.1
- Initial prototype
