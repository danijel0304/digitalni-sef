Name:           digitalni-sef
Version:        %{version}
Release:        1%{?dist}
Summary:        Local encrypted vault for subscriptions and accounts
License:        Proprietary
URL:            https://github.com/danijel0304/digitalni-sef
BuildArch:      x86_64

Requires:       gtk3
Requires:       libX11
Requires:       libxcb

%description
Digital Vault is a local encrypted desktop vault for subscriptions, accounts,
passwords, receipts, warranties, and reminders. Your saved data stays on your
computer and is protected with your master password.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_libdir}/digitalni-sef
cp -a %{_sourcedir}/dist/Digitalni-sef/. %{buildroot}%{_libdir}/digitalni-sef/
install -Dm755 %{_sourcedir}/packaging/run-digitalni-sef %{buildroot}%{_bindir}/digitalni-sef
install -Dm644 %{_sourcedir}/packaging/digitalni-sef.desktop %{buildroot}%{_datadir}/applications/digitalni-sef.desktop
install -Dm644 %{_sourcedir}/assets/digitalni-sef.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/digitalni-sef.png

%files
%{_bindir}/digitalni-sef
%{_libdir}/digitalni-sef
%{_datadir}/applications/digitalni-sef.desktop
%{_datadir}/icons/hicolor/256x256/apps/digitalni-sef.png
