# Add 3rd Party License to .spec File Guidelines

### Step 1: Bump release number
```
Name:           %{?scl_prefix}python-%{pypi_name}
Version:        4.0.0
Release:        1.0.2%{?dist}
```

### Step 2: Add Source1
```
Source0:        https://files.pythonhosted.org/packages/source/d/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
Source1:        THIRD_PARTY_LICENSES
```

### Step 3: Copy SOURCE1 to BUILD/<WORK_DIR>
```
# Add 3rd party license
%{__cp} %{SOURCE1} .
```

### Step 4: Add %license
```
%files -n %{?scl_prefix}python%{python3_pkgversion}-%{pypi_name}
%license LICENSE THIRD_PARTY_LICENSES
```

### Step 5: Add Changelog
```
%changelog
* Fri Jun 30 2023 Lans Hung <lans.hung@oracle.com> - 
- Add 3rd party licenses
```
