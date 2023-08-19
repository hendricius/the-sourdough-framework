#!/bin/bash
#

if [ "$#" -ne 1 ]; then
    for i in *.pdf
    do
      target=figures/`basename $1 .png.pdf`.png
      docker run -v $(pwd):/imgs dpokidov/imagemagick -density 900 -trim /imgs/$i -quality 100 /imgs/${target}
      rename 's/fig-/figure-/' *.png
    done
else
    target=figures/`basename $1 .png.pdf`.png
    echo "Converting: " $1 " to: " ${target}
    convert -density 900 -trim $1 -quality 100 ${target}
fi
