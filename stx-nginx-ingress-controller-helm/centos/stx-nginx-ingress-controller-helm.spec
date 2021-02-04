# Application tunables (maps to metadata)
%global app_name nginx-ingress-controller
%global helm_repo stx-platform
%global sha 92b6289ae93816717a8453cfe62bad51cbdb8ad0

%global armada_folder  /usr/lib/armada

# Install location
%global app_folder /usr/local/share/applications/helm

# Build variables
%global helm_folder /usr/lib/helm
%global toolkit_version 0.1.0

Summary: StarlingX Nginx Ingress Controller Application Armada Helm Charts
Name: stx-nginx-ingress-controller-helm
Version: 1.0
Release: %{tis_patch_ver}%{?_tis_dist}
License: Apache-2.0
Group: base
Packager: Wind River <info@windriver.com>
URL: unknown

Source0: helm-charts-%{sha}.tar.gz
Source1: repositories.yaml
Source2: index.yaml
Source3: Makefile
Source4: metadata.yaml
Source5: nginx_ingress_controller_manifest.yaml

BuildArch: noarch

BuildRequires: helm
BuildRequires: chartmuseum

Patch01: 0001-Update-for-kubernetes-API-1.16.patch
Patch02: 0002-Update-nginx-ingress-chart-for-Helm-v3.patch

%description
StarlingX Nginx Ingress Controller Application Armada Helm Charts

%prep
%setup -n helm-charts

%patch01 -p1
%patch02 -p1

%build
# Host a server for the charts
chartmuseum --debug --port=8879 --context-path='/charts' --storage="local" --storage-local-rootdir="." &
sleep 2
helm repo add local http://localhost:8879/charts

# Create the tgz file
cp %{SOURCE3} stable
cd stable
make nginx-ingress
cd -

# Terminate helm server (the last backgrounded task)
kill %1

# Create a chart tarball compliant with sysinv kube-app.py
%define app_staging %{_builddir}/staging
%define app_tarball %{app_name}-%{version}-%{tis_patch_ver}.tgz

# Setup staging
mkdir -p %{app_staging}
cp %{SOURCE4} %{app_staging}
cp %{SOURCE5} %{app_staging}
mkdir -p %{app_staging}/charts
cp stable/*.tgz %{app_staging}/charts
cd %{app_staging}

# Populate metadata
sed -i 's/@APP_NAME@/%{app_name}/g' %{app_staging}/metadata.yaml
sed -i 's/@APP_VERSION@/%{version}-%{tis_patch_ver}/g' %{app_staging}/metadata.yaml
sed -i 's/@HELM_REPO@/%{helm_repo}/g' %{app_staging}/metadata.yaml

# package it up
find . -type f ! -name '*.md5' -print0 | xargs -0 md5sum > checksum.md5
tar -zcf %{_builddir}/%{app_tarball} -C %{app_staging}/ .

# Cleanup staging
rm -fr %{app_staging}

%install
install -d -m 755 %{buildroot}/%{app_folder}
install -p -D -m 755 %{_builddir}/%{app_tarball} %{buildroot}/%{app_folder}

%files
%defattr(-,root,root,-)
%{app_folder}/*