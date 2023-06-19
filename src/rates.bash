#! /bin/bash

source /usr/local/ciao/bin/ciao.sh

srcreg=/data/legs/rpete/flight/g21.5-0.9/region/plerion.reg
bgreg=/data/legs/rpete/flight/g21.5-0.9/region/22855_bg.reg

# source region has radius 40"
# bg region is a 2100x350 box

backscal=$(echo '40/.1318*40/.1318*4*a(1)/2100/350' | bc -l)
echo $backscal

for o in 20657 22855
do
    evt=/data/legs/rpete/flight/g21.5-0.9/data/$o/tg_reprocess/hrcf${o}N002_evt2.fits
    #ds9 $evt -bin factor 32 -scale mode 99.5  -regions $srcreg -regions $bgreg

    exp=$(dmkeypar $evt exposure ec+)
    src=$(dmstat $evt"[sky=region($srcreg)][col time]" | grep good | perl -ae 'print $F[1]')
    bg=$(dmstat $evt"[sky=region($bgreg)][col time]" | grep good | perl -ae 'print $F[1]')
    net=$(echo "$src-$bg*$backscal" | bc -l)
    rate=$(echo "$net/$exp" | bc -l)
    echo obsid $o: \
	 src=$src, \
	 bg=$bg, \
	 net=$(printf '%.0f' $net), \
	 exptime=$(printf '%.0f' $exp), \
	 rate=$(printf '%.3g' $rate)
done
