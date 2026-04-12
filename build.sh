#!/bin/bash

if [[ $# -eq 0 ]]
    then
        echo 'Specify Version e.g. "4.2.0"'
        exit
    else
        VERSION=$1
        STATUS="testing"
fi

echo ENV:
env

rm -rf build/*
mkdir -p build/plugins/icons

cp -rv resources/ build/
cp -v resources/icon.png build/plugins/icons/
cp -v src/icons/*.png build/plugins/icons/
cp -v src/*.py build/plugins/
cp -v src/requirements.txt build/plugins/requirements.txt
cp -v src/plugin.json build/plugins/plugin.json


jq  --arg version $VERSION \
    --arg status $STATUS \
    '(.versions[0]) += {"version": $version, "status": $status}' \
    metadata.json > build/metadata.json


FULLSIZE=($(du build/ -bcs))

cd build
zip KiPNG.zip -rv ./* 
cd -

ZIPSIZE=($(wc --bytes build/KiPNG.zip))
ZIPSHA=($(sha256sum build/KiPNG.zip))

if [[ $CI ]]
    then
        LINK="https://github.com/tobiglaser/KiPNG/releases/download/$VERSION/KiPNG.zip"
    else
        LINK="https://tobiglaser.de/kicad-tests/KiPNG.zip"
fi

jq  --argjson ds $ZIPSIZE \
    --argjson install $FULLSIZE \
    --arg sha $ZIPSHA \
    --arg url $LINK \
    --arg version $VERSION \
    --arg status $STATUS \
    '(.versions[0]) += {"version": $version, "status": $status, "download_size": $ds, "download_sha256": $sha, "install_size": $install, "download_url": $url}' \
    metadata.json > build/metadata.json

echo Metadata:
cat build/metadata.json
