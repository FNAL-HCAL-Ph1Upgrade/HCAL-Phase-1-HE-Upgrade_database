#!/usr/local/bin/python

# Update Readout Module information for QIE Cards every hour.
import sys
import time
import django
import json

sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from qie_cards.models import QieCard, Location, ReadoutModule, RmLocation

# Update QIE Card locations with RM locations
def setQieCardLocations():
    start_time = time.time()
    
    qieCards = QieCard.objects.all().order_by("barcode")
    readMods = ReadoutModule.objects.all().order_by("rm_number")
    with open('/home/django/testing_database/location_update/qie_locations.txt', 'w') as q_file:
        for q in qieCards:
            q_loc = Location.objects.filter(card=q).order_by("date_received")
            current_loc = q_loc.reverse()[0].geo_loc
            rm_num = q.readout_module
            try:
                r = readMods.get(rm_number=rm_num)
                rm_loc = RmLocation.objects.filter(rm=r).order_by("date_received").reverse()[0].geo_loc
                if rm_loc != current_loc:
                    Location.objects.create(card=q, geo_loc=rm_loc)
                    current_loc = q_loc.reverse()[0].geo_loc
                q_file.write("{:>3s} - {:>7s} :: RM {:50s} - QIE {:50s}\n".format(r, q, rm_loc, current_loc))
            except ReadoutModule.DoesNotExist:
                q_file.write("{:>3s} - {:>7s} :: RM {:50s} - QIE {:50s}\n".format("###", q, "None", current_loc))
    q_file.close() 
    end_time = time.time()
    print "Update QIE Card location run time: {0}".format(end_time - start_time)

# Set RM Location to assembly if no location history by default
def setRMLocations():
    start_time = time.time()
    noLoc = 0
    assembly = "CERN B904 Clean Room"
    for r in ReadoutModule.objects.all():
        # RM Location 
        l = RmLocation.objects.filter(rm=r).order_by("date_received")
        # Set location to assembly if no location exists
        if len(l) == 0:
            RmLocation.objects.create(geo_loc=assembly, rm=r)
            noLoc += 1
            print "Set assembly location RM {0}".format(r)
        print "RM {0}: {1}".format(r, l.reverse()[0].geo_loc)
            
    print "Number of RMs with no location: {0}".format(noLoc)
    end_time = time.time()
    
    # Log RM Update
    with open('/home/django/testing_database/location_update/location.log', 'a') as log:
        log.write("updated readout module locations %s\n" % time.strftime("%c"))
    log.close()
    
    print "Update RM locations run time: {0}".format(end_time - start_time)

if __name__=="__main__":
    setRMLocations()
    setQieCardLocations()

