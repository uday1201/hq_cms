#!/bin/bash

export DJANGO_DATABASE='dev'

unset -v latest
for file in prodbackup/*; do
  [[ $file -nt $latest ]] && latest=$file
done
echo $latest
python manage.py loaddata prodbackup/$latest
