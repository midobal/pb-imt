#!/bin/bash

####################
## Default values ##
####################
export pth=$(dirname ${0})
export reference=''
export search_graph=''
export dest_dir=''
export wg=''

#####################
## Parse arguments ##
#####################
while getopts ":r:s:d:w:" opt; do
    case ${opt} in
	r )
	    export reference=${OPTARG}
	    ;;
	s )
	    export search_graph=${OPTARG}
	    ;;
  d )
    	export dest_dir=${OPTARG}
    	;;
  w )
    	export wg=${OPTARG}
    	;;
	\? )
	    >&2 echo "Usage: ${0} -r reference -s search_graph -d dest_dir -w wg"
	    exit 1
	    ;;
    esac
done

if [[ ${reference} == '' || ${search_graph} == '' || ${dest_dir} == '' || ${wg} == '' ]];then
  >&2 echo "Usage: ${0} -r reference -s search_graph -d dest_dir -w wg"
  exit 1
fi

for f in ${reference} ${search_graph} ${wg}
do
  if [ ! -f ${f} ]
  then
    >&2 echo "${f} does not exist."
    exit 1
  fi
done

mkdir -p ${dest_dir}
mkdir -p ${dest_dir}/tmp
export tmp=${dest_dir}/tmp

echo "$(date): Starting converting search graph into htk format."

cat ${search_graph} | awk -v dd="$tmp/" '{ print $0 > dd$1 }'
gzip ${tmp}/*
nfiles=$[$(ls ${tmp} | wc -l)-1]

for i in `seq 0 1 $nfiles`; do
    python2 ${pth}/scr/moses2htkGraph.py -i ${tmp}/$i.gz -o ${tmp}/$i.htk.gz
    echo $(readlink -f ${tmp}/$i.htk.gz) >> ${tmp}/graphs
done

echo "$(date): Starting dividing file."

for (( i = 0; i < $(cat ${reference} | wc -l); ++i ))
do
    head -n $(echo $i + 1 | bc) ${reference} | tail -n 1 > ${tmp}/$i.txt
    echo ${tmp}/$i.txt >> ${tmp}/translations
done

echo "$(date): Starting simulation."

${wg} -w ${tmp}/graphs -t ${tmp}/translations -d -n 0 > ${dest_dir}/simulation_log

characters=$(cat ${reference} | sed 's/.$//g' | sed 's/ //g' | wc -m)
strokes=$(grep "TOTAL WORD STROKES:" ${dest_dir}/simulation_log | awk -F ":" '{print $2}')
MAR=$(echo "scale=4;(" $strokes "+ " $(cat ${reference} | wc -l) ") * 100 / " $characters | bc)
echo "MAR: " $MAR >> ${dest_dir}/simulation_log

echo "$(date): Cleaning temp files."
rm -rf ${tmp}

echo "$(date): Process finished!"
