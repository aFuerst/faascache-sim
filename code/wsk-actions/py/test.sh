#!/bin/sh

for dir in ./actions/*/
do
    dir=${dir%*/}      # remove the trailing "/"
    echo ${dir##*/}    # print everything after the final "/"
    zip_cmd="zip -r ${dir##*/}.zip ./virtualenv/bin/activate_this.py "
    reqs="./actions/${dir##*/}/reqs.txt"
    # echo $reqs
    
    if [ -f $reqs ]; then
        while read p; do
            # echo $line
            zip_cmd="$zip_cmd ./virtualenv/lib/python3.6/site-packages/$p"
            # echo $zip_cmd
        done < $reqs
    fi
    cp "./actions/${dir##*/}/__main__.py" .
    zip_cmd="$zip_cmd ../__main__.py"
    # cat "./actions/${dir##*/}/reqs.txt"
    echo $zip_cmd
    cd ./venv/
    # eval $zip_cmd
    cd ..
    rm "__main__.py"
done