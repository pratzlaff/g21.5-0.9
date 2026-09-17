#! /bin/bash

dir=/data/legs/rpete/flight/g21.5-0.9

set -eo pipefail

. ~/.bash_aliases
shopt -s expand_aliases

ciao

obsids=$(\grep '^[0-9]' "$dir"/obsids | \grep -i hrc-i | perl -anle 'print $F[0]')
echo $obsids

# reverse order
obsids=$(echo "$obsids" | xargs -n 1 | tac)

for o in $obsids
do

    evt2=$(\ls "$dir"/data/$o/tg_reprocess/hrcf*${o}N*_evt2.fits)

    dmstat "$evt2[sky=region($dir/region/pulsar.reg)][col chipx]" verbose=0
    xmin=$(pget dmstat out_min)
    xmax=$(pget dmstat out_max)

    dmstat "$evt2[sky=region($dir/region/pulsar.reg)][col chipy]" verbose=0
    ymin=$(pget dmstat out_min)
    ymax=$(pget dmstat out_max)

    printf "$o: CHIPX=[%.0f, %.0f], CHIPY=[%.0f, %.0f]\n" $xmin $xmax $ymin $ymax

done
