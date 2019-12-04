# Use release 0 for prerelease version.
%define release 1
%define version 1.0.0
%define venv inmanta-venv
%define _p3 %{venv}/bin/python3
%define _unique_build_ids 0
%define _debugsource_packages 0
%define _debuginfo_subpackages 0
%define _enable_debug_packages 0
%define debug_package %{nil}

%define sourceversion %{version}%{?buildid}

Name:           python3-inmanta-ui
Version:        %{version}

Release:        %{release}%{?buildid}%{?tag}%{?dist}
Summary:        Inmanta User Interface extension

Group:          Development/Languages
License:        EULA
URL:            http://inmanta.com
Source0:        inmanta-ui-%{sourceversion}.tar.gz
Source1:        deps-%{sourceversion}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python3-inmanta
BuildRequires:  systemd
BuildRequires:  nodejs

Requires:  python3-inmanta

# Use the correct python for bycompiling
%define __python %{_p3}

%description

%prep
%setup -q -n inmanta-ui-%{sourceversion}
%setup -T -D -a 1 -n inmanta-ui-%{sourceversion}

# Download the package from github npm repository
npm set //npm.pkg.github.com/:_authToken %{github_token}
npm pack @inmanta/web-console@%{web_console_version} --registry=https://npm.pkg.github.com

%build

%install
# Copy the inmanta venv to BUILD directory to work around ownership issue
cp -r --no-preserve=ownership /opt/inmanta inmanta-venv
chmod -x LICENSE

# Save packages installed by python3-inmanta
files=$(find inmanta-venv/lib/python3.6/site-packages/ -maxdepth 1 -mindepth 1 ! -path inmanta-venv/lib/python3.6/site-packages/inmanta_ext)

# Install inmanta-ui
%{_p3} -m pip install --no-index --find-links deps-%{sourceversion} inmanta-ui

# Only keep new packages
rm -rf ${files}
# Remove inmanta_ext/core separately, to retain inmanta_ext/ui
rm -rf inmanta-venv/lib/python3.6/site-packages/inmanta_ext/core

mkdir -p %{buildroot}/opt/inmanta/
cp -r inmanta-venv/lib/ %{buildroot}/opt/inmanta/

# Install web-console
mkdir -p %{buildroot}/usr/share/inmanta/web-console
tar -xf inmanta-web-console-%{web_console_version}.tgz --strip-components=2 --directory %{buildroot}/usr/share/inmanta/web-console

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE
/opt/inmanta/lib/
/usr/share/inmanta/web-console

%preun
# Stop and disable the inmanta-server service before this package is uninstalled
%systemd_preun inmanta-server.service

%postun
# Restart the inmanta-server service after an upgrade of this package
%systemd_postun_with_restart inmanta-server.service

%changelog
* Tue Dec 03 2019 Andras Kovari <andras.kovari@inmanta.com> - 0.1
- Initial release
