#!/bin/sh

#
# update-datfiles.sh
#

# This script downloads and unpacks the newest TOSEC and No-Intro DAT files for classic systems.

set -e

debug() {
  echo "[DEBUG] $@"
}

die() {
  echo "[ERROR] $@"
  exit 1
}

# Download TOSEC DATs.
tosec_domain=https://www.tosecdev.org
tosec_download_page_url="$tosec_domain/downloads"
debug "tosec_download_page_url = $tosec_download_page_url"
tosec_download_page_html=$(curl -fsL "$tosec_download_page_url")
tosec_category_page_url=$(echo "$tosec_download_page_html" | grep 'href="/downloads/category' | head -n1 | sed 's/.*href="\([^"]*\)".*/\1/')
case "$tosec_category_page_url" in
  /*) tosec_category_page_url="$tosec_domain$tosec_category_page_url" ;;
esac
debug "tosec_category_page_url = $tosec_category_page_url"
tosec_category_page_html=$(curl -fsL "$tosec_category_page_url")
tosec_archive_link=$(echo "$tosec_category_page_html" | grep -o '<a [^>]*>[^<]*TOSEC-v[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\})\.zip</a>' | head -n1)
debug "tosec_archive_link = $tosec_archive_link"
tosec_archive_url=$(echo "$tosec_archive_link" | sed 's/.*href="\([^"]*\)".*/\1/')
case "$tosec_archive_url" in
  /*) tosec_archive_url="$tosec_domain$tosec_archive_url" ;;
esac
debug "tosec_archive_url = $tosec_archive_url"
tosec_archive_filename=$(echo "$tosec_archive_link" | sed 's/.*>\([^<]*\.zip\)<.*/\1/')
debug "tosec_archive_filename = $tosec_archive_filename"
if [ -d TOSEC.backup ]; then rm -rf TOSEC.backup; fi
if [ -d TOSEC ]; then mv TOSEC TOSEC.backup; fi
mkdir -p dats/TOSEC
cd dats/TOSEC
echo "Downloading TOSEC DATs..."
curl -fL "$tosec_archive_url" > "$tosec_archive_filename"
echo "Unpacking TOSEC DATs..."
unzip "$tosec_archive_filename" >/dev/null
cd -

# Download No-Intro DATs (via RomCenter).
romcenter_download_page_url=https://www.romcenter.com/downloadpage/
debug "romcenter_download_page_url = $romcenter_download_page_url"
romcenter_download_page_html=$(curl -fsL "$romcenter_download_page_url")
romcenter_archive_href=$(echo "$romcenter_download_page_html" | grep -o 'href="[^"]*?file=[^"]*.7z"' | head -n1)
debug "romcenter_archive_href = $romcenter_archive_href"
romcenter_archive_url=$(echo "$romcenter_archive_href" | sed 's/href="\([^"]*\)"/\1/')
debug "romcenter_archive_url = $romcenter_archive_url"
romcenter_archive_filename=$(echo "$romcenter_archive_href" | sed 's/.*file=\(.*\.7z\)"$/\1/')
debug "romcenter_archive_filename = $romcenter_archive_filename"
if [ -d RomCenter.backup ]; then rm -rf RomCenter.backup; fi
if [ -d RomCenter ]; then mv RomCenter RomCenter.backup; fi
mkdir -p dats/RomCenter
cd dats/RomCenter
echo "Download No-Intro DATs..."
curl -fL "$romcenter_archive_url" > "$romcenter_archive_filename"
echo "Unpacking No-Intro DATs..."
7z x "$romcenter_archive_filename" >/dev/null
cd -
