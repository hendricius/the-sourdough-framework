#!/bin/bash
#
# Turns every SVG picture of an unpacked ebook into a PNG, for Kindle.
#
# Amazon's converter sends each SVG through Chromium, and for this book that
# step fails: KDP rejects the file with "Kindle conversion has encountered an
# internal error." Kindle does not support SVG anyway (Kindle Publishing
# Guidelines 11.4.1 and 11.4.11), only PNG and JPEG. Each PNG is at least
# 1200 px wide, on white because Kindle does not support transparency, and has
# at most 256 colours, which keeps the drawings small.
#
# Usage: kindle-images.sh <unpacked ebook directory>

set -euo pipefail

cd "$1/OEBPS"

for svg in $(find . -name '*.svg' | sed 's#^\./##' | sort); do
    png=${svg%.svg}.png
    if grep -q "width='0pt' height='0pt'" "$svg"; then
        # The picture environment of the printed cover leaves an empty picture
        # on the title page, which has nothing to show and cannot be rendered.
        sed -i "s#<img [^>]*src='$svg'[^>]*/>##" *.html
        sed -i "\#href='$svg'#d" content.opf
    else
        width=$(rsvg-convert "$svg" | identify -format '%w' -)
        width=$(( width * 2 > 1200 ? width * 2 : 1200 ))
        rsvg-convert --width "$width" --background-color white "$svg" |
            convert - -alpha off -colors 256 "PNG8:$png"
        sed -i "s#src='$svg'#src='$png'#g" *.html
        sed -i "s#href='$svg' \(id='[^']*'\) media-type='image/svg+xml'#href='$png' \1 media-type='image/png'#" content.opf
    fi
    rm "$svg"
done

# Nothing may still point at an SVG that is gone.
if grep -l -E "src='[^':]*\.svg'|media-type='image/svg\+xml'" *.html content.opf; then
    echo "ERROR: SVG still referenced in the Kindle ebook"
    exit 1
fi
