#!/usr/local/bin/python

# Update Readout Module information for QIE Cards every hour.
import sys
import time
import django
import json

sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from qie_cards.models import ReadoutModule, CalibrationUnit

start_time = time.time()

# Update Readout Module Unique IDs and QIE Cards in database
rm_dict = {}
for rm in ReadoutModule.objects.all():
    rm.update()
    rm_dict[rm.rm_number] = rm.rm_uid
# Update Calibration Unit QIE Cards in db
cu_dict = {}
for cu in CalibrationUnit.objects.all():
    cu.update()
    cu_dict[cu.cu_number] = cu.qie_card.get_uid_mac_simple()

# Output Readout Module json file
with open('/home/django/testing_database/rm_update/rm.json', 'w') as j:
    json.dump(rm_dict, j, sort_keys=True, indent=4)
j.close()

# Output Calibration Unit json file
with open('/home/django/testing_database/rm_update/cu.json', 'w') as k:
    json.dump(cu_dict, k, sort_keys=True, indent=4)
k.close()

end_time = time.time()
run_time = end_time - start_time
print "Update run time: {0}".format(run_time)
# Log RM Update
with open('/home/django/testing_database/rm_update/rmUpdateLog.txt', 'a') as log:
    log.write("Updated RMs and CUs {0}\t| run time {1}\n".format(time.strftime("%c"), run_time))
log.close()

