# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_rel	0.1
Summary:	Determine how much physical memory and swap is used by individual processes
Summary(pl):	Narzêdzie do analizowania zu¿ycia pamiêci fizycznej i wymiany przez poszczególne procesy
Name:		exmap
Version:	0.10
Release:	%{_rel}
Epoch:		0
License:	GPL v2
Group:		Applications/System
Source0:	http://www.berthels.co.uk/exmap/download/%{name}-%{version}.tgz
# Source0-md5:	b4f87fa02f6a218416b77ad4b9f48d74
Patch0:		%{name}-Makefile.patch
URL:		http://www.berthels.co.uk/exmap/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
#BuildRequires:	-
#Requires(postun):	-
#Requires(pre,post):	-
#Requires(preun):	-
#Requires:	-
#Provides:	-
#Obsoletes:	-
#Conflicts:	-
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Exmap is a tool which allows the real memory usage of a collection of
processes to be examined. A linux kernel loadable module is used to
export information to userspace, which is examined by a gtk
application to build a picture of how pages are shared amongst
processes and their shared libraries.

#%description -l pl

# kernel subpackages.

%package -n kernel%{_alt_kernel}-misc-exmap
Summary:	Linux driver for exmap
Summary(pl):	Sterownik dla Linuksa do exmap
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-misc-exmap
This is driver for exmap for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-misc-exmap -l pl
Sterownik dla Linuksa do exmap.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel%{_alt_kernel}-smp-misc-exmap
Summary:	Linux SMP driver for exmap
Summary(pl):	Sterownik dla Linuksa SMP do exmap
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-misc-exmap
This is driver for exmap for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-misc-exmap -l pl
Sterownik dla Linuksa do exmap.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q
%patch0 -p1
# remove binaries packed in src tarball
rm -f src/{*.so,munged-ls-threeloads,prelinked-amule}

# prepare makefile:
cat > kernel/Makefile << EOF
obj-m += exmap.o
CFLAGS += -DCONFIG_exmap_SOME_OPTION=1
%{?debug:CFLAGS += -DCONFIG_exmap_DEBUG=1}
EOF

%build
%if %{with userspace}
%{__make} \
	CXX="%{__cxx}" CXXFLAGS="%{rpmcxxflags}" CFLAGS="%{rpmcflags}"

%endif

%if %{with kernel}
%build_kernel_modules -C kernel -m exmap
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}
install src/gexmap $RPM_BUILD_ROOT%{_bindir}
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/exmap -d misc

# to avoid conflict with in-kernel modules, and prepare modprobe config:
#%%install_kernel_modules -s current -n NAME -m exmap -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-misc-exmap
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-misc-exmap
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-misc-exmap
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-misc-exmap
%depmod %{_kernel_ver}smp

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-misc-exmap
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-misc-exmap
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif

%if %{with userspace}
%files
%doc README TODO
%defattr(644,root,root,755) %{_bindir}/*
%endif
