#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Digitalni-sef"
PACKAGE_NAME="digitalni-sef"
VERSION="${VERSION:?VERSION must be set}"
VERSION_NUMBER="${VERSION#v}"
RELEASE_DIR="release"

rm -rf build/deb-root build/AppDir build/tar-root
mkdir -p "$RELEASE_DIR" build/tar-root build/deb-root/DEBIAN build/deb-root/usr/lib/digitalni-sef \
  build/deb-root/usr/bin build/deb-root/usr/share/applications build/deb-root/usr/share/icons/hicolor/256x256/apps

cp -a "dist/$APP_NAME" "build/tar-root/$APP_NAME"
tar -C build/tar-root -czf "$RELEASE_DIR/$PACKAGE_NAME-$VERSION-linux-x86_64.tar.gz" "$APP_NAME"

cp -a "dist/$APP_NAME/." build/deb-root/usr/lib/digitalni-sef/
install -Dm755 packaging/run-digitalni-sef build/deb-root/usr/bin/digitalni-sef
install -Dm644 packaging/digitalni-sef.desktop build/deb-root/usr/share/applications/digitalni-sef.desktop
install -Dm644 assets/digitalni-sef.png build/deb-root/usr/share/icons/hicolor/256x256/apps/digitalni-sef.png
sed "s/@VERSION@/$VERSION_NUMBER/" packaging/debian-control > build/deb-root/DEBIAN/control
dpkg-deb --build build/deb-root "$RELEASE_DIR/$PACKAGE_NAME-$VERSION-linux-amd64.deb"

APPDIR="build/AppDir"
mkdir -p "$APPDIR/usr/lib/digitalni-sef" "$APPDIR/usr/bin"
cp -a "dist/$APP_NAME/." "$APPDIR/usr/lib/digitalni-sef/"
install -Dm755 packaging/run-digitalni-sef "$APPDIR/usr/bin/digitalni-sef"
install -Dm755 packaging/AppRun "$APPDIR/AppRun"
install -Dm644 packaging/digitalni-sef.desktop "$APPDIR/digitalni-sef.desktop"
install -Dm644 assets/digitalni-sef.png "$APPDIR/digitalni-sef.png"
ARCH=x86_64 "$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "$RELEASE_DIR/$PACKAGE_NAME-$VERSION-linux-x86_64.AppImage"
