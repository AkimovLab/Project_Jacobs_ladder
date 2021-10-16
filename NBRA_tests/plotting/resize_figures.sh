#!/bin/bash

# resizes figures to typical size I use in reports
mogrify -resize 640x460 ../figures/*/*.png
