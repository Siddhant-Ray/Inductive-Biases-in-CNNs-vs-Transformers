#!/bin/bash
echo "script to run resnet tasks"

if ls lsf.* 1> /dev/null 2>&1
then
    echo "lsf files do exist"
    echo "removing older lsf files"
    rm lsf.*
fi

module load gcc/8.2.0 python_gpu/3.8.5 eth_proxy
source ../venv/bin/activate

args=(
    -G s_stud_infk
    -n 2
    -W 4:00
    -R "rusage[mem=4500]"
)

if [ -z "$1" ]; then echo "CPU mode selected"; fi
while [ ! -z "$1" ]; do
    case "$1" in
        gpu)
            echo "GPU mode selected"
            args+=(-R "rusage[ngpus_excl_p=4]")
            ;;
        intr)
            echo "Interactive mode selected"
            args+=(-Is)
            ;;
    esac
    shift
done

#bsub "${args[@]}" python classifier_pretrained.py 
#bsub "${args[@]}" python classifier_scratch.py 
bsub "${args[@]}" python classifier_customimages.py combined 
bsub "${args[@]}" python classifier_customimages.py background 

