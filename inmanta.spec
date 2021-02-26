# Use release 0 for prerelease version.
%define release 1
%define version 1.0.0
%define buildid %{nil}
%define buildid_egg %{nil}
%define venv inmanta-venv
%define _p3 %{venv}/bin/python3
%define site_packages_dir %{venv}/lib/python3.6/site-packages
%define _unique_build_ids 0
%define _debugsource_packages 0
%define _debuginfo_subpackages 0
%define _enable_debug_packages 0
%define debug_package %{nil}

%define sourceversion %{version}%{?buildid}
%define sourceversion_egg %{version}%{?buildid_egg}

Name:           python3-inmanta-ui
Version:        %{version}

Release:        %{release}%{?buildid}%{?tag}%{?dist}
Summary:        Inmanta User Interface extension

Group:          Development/Languages
License:        EULA
URL:            http://inmanta.com
Source0:        inmanta-ui-%{sourceversion_egg}.tar.gz
Source1:        deps-%{sourceversion}.tar.gz
Source2:        inmanta-web-console-%{web_console_version}.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python3-inmanta < 2020.5.0
BuildRequires:  systemd
BuildRequires:  nodejs

Requires:  python3-inmanta < 2020.5.0

# Use the correct python for bycompiling
%define __python %{_p3}

%description

%prep
%setup -q -n inmanta-ui-%{sourceversion_egg}
%setup -T -D -a 1 -n inmanta-ui-%{sourceversion_egg}

%build

%install
# Copy the inmanta venv to BUILD directory to work around ownership issue
cp -r --no-preserve=ownership /opt/inmanta %{venv}
chmod -x LICENSE

# Save packages installed by python3-inmanta
files=$(find %{site_packages_dir} -maxdepth 1 -mindepth 1 ! -path %{site_packages_dir}/inmanta_ext)

# Install inmanta-ui
%{_p3} -m pip install --pre --no-index --find-links dependencies .

# Only keep new packages
rm -rf ${files}
# Remove inmanta_ext/core separately, to retain inmanta_ext/ui
find "%{site_packages_dir}/inmanta_ext" -maxdepth 1 -mindepth 1 ! -path "%{site_packages_dir}/inmanta_ext/ui" |xargs rm -rf

# Byte-compile source code
packages_to_bytecompile=("inmanta_ui" "inmanta_ext")
for p in "${packages_to_bytecompile[@]}"; do
   find "%{site_packages_dir}/${p}" -name '*.py' |xargs -I file_name python3.6 -c 'import py_compile; py_compile.compile(file="file_name", cfile="file_namec", doraise=True)'
   find "%{site_packages_dir}/${p}" -name '*.py' |xargs rm -f
   find "%{site_packages_dir}/${p}" -name '__pycache__' |xargs rm -rf
done

mkdir -p %{buildroot}/opt/inmanta/
cp -r %{venv}/lib/ %{buildroot}/opt/inmanta/

# Install web-console
mkdir -p %{buildroot}/usr/share/inmanta/web-console
tar -xf %{SOURCE2} --strip-components=2 --directory %{buildroot}/usr/share/inmanta/web-console

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
