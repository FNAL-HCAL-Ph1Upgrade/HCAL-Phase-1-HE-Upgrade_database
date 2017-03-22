#!/usr/local/bin/python

# Applys RM and CU locations to QIE Cards every hour.
import sys
import time
import django
import json

# setup to edit django database
sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from qie_cards.models import QieCard, Location, ReadoutModule, RmLocation, CalibrationUnit, CuLocation

# Update QIE Card locations with RM locations
def setQieCardLocations():
    start_time = time.time()
    notInstalled = 0 
    qieCards = QieCard.objects.all().order_by("barcode")
    readMods = ReadoutModule.objects.all().order_by("rm_number")
    calUnits = CalibrationUnit.objects.all().order_by("cu_number")
    with open('/home/django/testing_database/location_update/qie_locations.txt', 'w') as q_file:
        for q in qieCards:
            q_locs = Location.objects.filter(card=q).order_by("date_received")
            current_loc = q_locs.reverse()[0].geo_loc
            rm_num = q.readout_module
            cu_num = q.calibration_unit
            if rm_num > 0: # the QIE card is installed in a RM (-1 default)
                try:
                    r = readMods.get(rm_number=rm_num)
                    rm_loc = RmLocation.objects.filter(rm=r).order_by("date_received").reverse()[0].geo_loc
                    if rm_loc != current_loc:
                        Location.objects.create(card=q, geo_loc=rm_loc)
                        current_loc = q_locs.reverse()[0].geo_loc
                    q_file.write("{:>3s} - {:>7s} :: RM {:50s} - QIE {:50s}\n".format(r, q, rm_loc, current_loc))
                except ReadoutModule.DoesNotExist:
                    notInstalled += 1
                    q_file.write("{:>3s} - {:>7s} :: RM {:50s} - QIE {:50s}\n".format("###", q, "RM does not exist", current_loc))
            elif cu_num > 0: # the QIE card is installed in a CU (-1 default)
                try:
                    c = calUnits.get(cu_number=cu_num)
                    cu_loc = CuLocation.objects.filter(cu=c).order_by("date_received").reverse()[0].geo_loc
                    if cu_loc != current_loc:
                        Location.objects.create(card=q, geo_loc=cu_loc)
                        current_loc = q_locs.reverse()[0].geo_loc
                    q_file.write("{:>3s} - {:>7s} :: CU {:50s} - QIE {:50s}\n".format(c, q, cu_loc, current_loc))
                except ReadoutModule.DoesNotExist:
                    notInstalled += 1
                    q_file.write("{:>3s} - {:>7s} :: CU {:50s} - QIE {:50s}\n".format("###", q, "CU does not exist", current_loc))
            else:   # the QIE card is not installed in RM or CU
                notInstalled += 1
                q_file.write("{:>3s} - {:>7s} :: Not Installed! {:50s} - QIE {:50s}\n".format("###", q, "No RM or CU for qie card.", current_loc))

    end_time = time.time()
    print "Number of QIE cards that are not installed: {0}".format(notInstalled)
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
            
    # Log RM Update
    with open('/home/django/testing_database/location_update/location.log', 'a') as log:
        log.write("updated readout module locations %s\n" % time.strftime("%c"))
    
    end_time = time.time()
    print "Number of RMs with no location: {0}".format(noLoc)
    print "Update RM locations run time: {0}".format(end_time - start_time)

# Set CU Location to assembly if no location history by default
def setCULocations():
    start_time = time.time()
    noLoc = 0
    assembly = "CERN B904 Clean Room"
    for c in CalibrationUnit.objects.all():
        # CU Location 
        l = CuLocation.objects.filter(cu=c).order_by("date_received")
        # Set location to assembly if no location exists
        if len(l) == 0:
            CuLocation.objects.create(geo_loc=assembly, cu=c)
            noLoc += 1
            print "Set assembly location CU {0}".format(c)
        print "CU {0}: {1}".format(c, l.reverse()[0].geo_loc)
            
    end_time = time.time()
    print "Number of CUs with no location: {0}".format(noLoc)
    print "Update RM locations run time: {0}".format(end_time - start_time)

if __name__=="__main__":
    setCULocations()
    setRMLocations()
    setQieCardLocations()

