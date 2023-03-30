#!/bin/bash
for i in *.pdf
do
  docker run -v $(pwd):/imgs dpokidov/imagemagick -density 900 -trim /imgs/$i -quality 100 /imgs/$i.png
  rename 's/pdf.png/png/' *.png
  rename 's/fig-/figure-/' *.png
done

