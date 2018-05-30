%define install_base /usr/lib/perfsonar/
%define config_base  /etc/perfsonar

%define relnum   0.1rc1 

Name:			perfsonar-pslocate
Version:		1.0
Release:		%{relnum}
Summary:		perfSONAR Locate Script
License:		ASL 2.0
Group:			Development/Libraries
URL:			http://www.perfsonar.net
Source0:		%{name}-%{version}.tar.gz
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:		noarch
Requires:       python
Requires:		python-elasticsearch

%description
Provides the pslocate command and library for finding perfSONAR measurement points 
closest to a given IP. It determines this by looking at indexed information from regular 
traceroute tests stored in an ElasticSearch cache of lookup service information

%pre
/usr/sbin/groupadd perfsonar 2> /dev/null || :
/usr/sbin/useradd -g perfsonar -r -s /sbin/nologin -c "perfSONAR User" -d /tmp perfsonar 2> /dev/null || :

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%post

%files -f INSTALLED_FILES
%defattr(0755,perfsonar,perfsonar,0755)

%changelog
* Wed May 18 2018 andy@es.net 1.0-0.1rc1
- Initial RPM
