%global base_version 1.5
%global patch_version 2
%global engine_version 1.5.0

Name:           rhproxy
Version:        %{base_version}.%{patch_version}
Release:        1%{?dist}
Summary:        Insights proxy Service v%{version}

License:        GPLv3
URL:            https://github.com/RedHatInsights/rhproxy
Source0:        %{url}/archive/%{version}.tar.gz

BuildArch:      noarch

Requires:       bash
Requires:       podman >= 4.9.4
Requires:       polkit

%description
This RPM installs the Insights proxy Service on the System.
The rhproxy service controller installs and manages
the Insights proxy via a systemd quadlet service.

%prep
%autosetup -n %{name}-%{version}

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_datadir}/%{name}/bin
cp bin/%{name} %{buildroot}/%{_bindir}/%{name}
cp bin/rhproxy-configure %{buildroot}/%{_datadir}/%{name}/bin/rhproxy-configure
mkdir -p %{buildroot}/%{_datadir}/%{name}/config
cp config/*.container %{buildroot}/%{_datadir}/%{name}/config/
mkdir -p %{buildroot}/%{_datadir}/%{name}/env
cp env/*.env %{buildroot}/%{_datadir}/%{name}/env/
cp env/*.servers %{buildroot}/%{_datadir}/%{name}/env/
mkdir -p %{buildroot}/%{_datadir}/%{name}/download/bin
cp download/bin/*.template %{buildroot}/%{_datadir}/%{name}/download/bin/

# Let's make sure we pick the major.minor released version of the engine
sed -i 's/{{RHPROXY_ENGINE_RELEASE_TAG}}/%{engine_version}/' %{buildroot}/%{_datadir}/%{name}/config/rhproxy.container

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/bin/rhproxy-configure
%{_datadir}/%{name}/config/rhproxy.container
%{_datadir}/%{name}/env/rhproxy.env
%{_datadir}/%{name}/env/redhat.servers
%{_datadir}/%{name}/env/epel.servers
%{_datadir}/%{name}/env/mirror.servers
%{_datadir}/%{name}/download/bin/configure-client.sh.template

%changelog
* Mon Jan 27 2025 Alberto Bellotti <abellott@redhat.com> - 1.5.2
- Updated the container image repo path in registry.redhat.io.

* Sat Jan 25 2025 Alberto Bellotti <abellott@redhat.com> - 1.5.1
- Fixed an issue where the mirror.server file was getting overwritten.

* Thu Jan 23 2025 Alberto Bellotti <abellott@redhat.com> - 1.5.0
- GA Release of Insights proxy
- Now pulling the rhproxy-engine container image 1.5.0 from registry.redhat.io

* Wed Jan 22 2025 Alberto Bellotti <abellott@redhat.com> - 1.3.9
- Added mirrormanager.fedoraproject.org as allowed Red Hat server.

* Tue Nov 26 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.8
- Require the polkit RPM if not installed
- Fixed DNF repo specification for the tech preview in the README

* Tue Nov 12 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.7
- Using the 1.3.6 Konflux built rhproxy engine
- Pulling rhproxy-engine from the quay.io/insights_proxy/rhproxy-engine repo

* Tue Nov 05 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.6
- Using 1.3.4 rhproxy engine which includes cleanup of the source
- Default DNS Server to 1.1.1.1 to be consistent with the rhproxy engine
- Dynamically fetch EPEL versions and architectures
- Used the mirrorlist endpoint to Fetch EPEL mirrors (similar to metalink)
- Fetch servers from all Geo locations

* Fri Nov 01 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.5
- Using 1.3.3 rhproxy engine which is built with included sources
- Enabling user lingering upon rhproxy install
- Disabling user lingering upon rhproxy uninstall
- Require the specific x.y.z patched versions of the rhproxy engine

* Thu Oct 24 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.4
- Adding podman requirement to the RPM spec

* Fri Oct 18 2024 Alberto Bellotti <abellott@redhat.com> - 1.3.3
- Adding support for EPEL server via epel.servers
- Adding support for optional mirror servers via mirror.servers

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
