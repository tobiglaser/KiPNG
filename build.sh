#!/bin/sh

echo "args:"
echo $#

if [[ $# -eq 0 ]]
    then
        echo "Specify Version e.g. 4.2.0"
        exit
    else
        VERSION=$1
        STATUS="testing"
fi

mkdir -p build/plugins/icons

cp -r resources/ build/
cp resources/icon.png build/plugins/icons/
cp src/icons/*.png build/plugins/icons/
cp src/*.py build/plugins/
cp src/requirements.txt build/plugins/requirements.txt
cp src/plugin.json build/plugins/plugin.json


jq  --arg version "$VERSION" \
    --arg status "$STATUS" \
    '(.versions[0]) += {"version": "$version", "status": "$status"}' \
    metadata.json > build/metadata.json


FULLSIZE=$(wc --bytes --total=only build/*)

cd build
zip KiPNG.zip -r ./*
cd -

ZIPSIZE=($(wc --bytes build/KiPNG.zip))
ZIPSHA=($(sha256sum build/KiPNG.zip))

LINK="https://tobiglaser.de/kicad-tests/KiPNG.zip"

jq  --argjson ds $ZIPSIZE \
    --argjson install $FULLSIZE \
    --arg sha $ZIPSHA \
    --arg url $LINK \
    --arg version $VERSION \
    --arg status $STATUS \
    '(.versions[0]) += {"version": $version, "status": $status, "download_size": $ds, "download_sha256": $sha, "install_size": $install, "download_url": $url}' \
    metadata.json > build/metadata.json

