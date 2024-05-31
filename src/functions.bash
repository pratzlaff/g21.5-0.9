dir=/data/legs/rpete/flight/g21.5-0.9

obsids()
{
    echo 28458; return
    grep '^[0-9]' "$dir"/obsids | cut -f 1 #| head -1
}

instrument()
{
    local obsid="$1"
    local f=$(ls "$dir"/data/"$obsid"/tg_reprocess/*_evt2.fits 2>/dev/null)

    if [ -z "$f" ]
    then
        grep "$obsid" "$dir"/obsids | perl -anle 'print $F[1]'
        return
    fi

    echo $(detnam "$f")
}

detnam()
{
    local evt2="$1"
    punlearn dmkeypar
    dmkeypar "$evt2" detnam echo+
}
