#! /bin/bash

. ~/.bash_aliases
shopt -s expand_aliases

ciao

. /data/legs/rpete/flight/analysis_functions/caldb_files.bash
. /data/legs/rpete/flight/analysis_functions/tmppdir.bash

obsid=24982

declare -A v
iqev=(
    [N0011]=/data/legs/rpete/flight/hrci_qe/N0011/qe
    [N0012]=/data/legs/rpete/flight/hrci_qe/N0012/qe
    [N0013.20210513]=/data/legs/rpete/flight/hrci_qe/N0013/qe.20210513
    [N0013.20210701]=/data/legs/rpete/flight/hrci_qe/N0013/qe.20210701
)

declare -A i pars
pars=(
    [plerion]='tbabs.nh=3.2;pl.phoindex=1.8'
    [halo]='tbabs.nh=2.4;pl.phoindex=2.1'
)

screen -dmS srcfluxtest bash -c 'exec bash'

punlearn ardlib

for v in "${!iqev[@]}"
do
    outdir=./test_srcflux/i_qe_$v
    evt2=$(ls ./data/$o/tg_reprocess/*evt2.fits*)
    pha2=$(ls ./data/$o/tg_reprocess/*pha.fits*)
    qedir=${iqev["$v"]}
    qefile=$(match_caldb_file "$pha2" qeu "$qedir" "$v")

    pset ardlib AXAF_HRC-I_QE_FILE="$qefile"

    srcflux \
        infile=./data/$obsid/tg_reprocess/*evt2.fits \
        pos="$pos" \
        outroot=$outdir/${o}_${type} \
        band=wide \
        srcreg=$srcreg \
        bkgreg=$bkgreg \
        psfmethod=ideal \
        model="xstbabs.tbabs*xspowerlaw.pl" \
        paramvals=${pars[$type]} \
        abund=wilm \
        asolfile=$asolfile \
        mskfile=$mskfile \
        bpixfile=$bpixfile \
        dtffile=$dtffile \
        clobber+
	
done

