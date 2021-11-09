files=$(ls)
for file in $files
do
    if [ -f $file ]
    then
        echo "load \"$file\"; csvwrite(\"$file.csv\", ETdata.pos)"
        octave --eval "load \"$file\"; csvwrite(\"$file.csv\", ETdata.pos)"
    fi
done