#!/bin/bash
function my_date {
  date "+%y-%m-%d::%H:%M"
}

file="backup_$(my_date).json"

echo $file

export DJANGO_DATABASE='dev'
python manage.py dumpdata > dbbackups/$file
export DJANGO_DATABASE='prod'
python manage.py loaddata dbbackups/$file
export DJANGO_DATABASE='dev'
