#!/bin/bash
function my_date {
  date "+%y-%m-%d::%H:%M"
}

file="backup_$(my_date).json"
prodfile="prodbackup_$(my_date).json"

echo $file

export DJANGO_DATABASE='dev'
python manage.py dumpdata > migratedbs/$file
export DJANGO_DATABASE='prod'
# taking prod backup
python manage.py dumpdata > prodbackup/$prodfile
python manage.py loaddata migratedbs/$file
export DJANGO_DATABASE='dev'

# cleaning up migrate jsons older than 7 days
find ./migratedbs -mtime +7 -type f -delete

# cleaning up backups older than 15 days
find ./prodbackup -mtime +15 -type f -delete
