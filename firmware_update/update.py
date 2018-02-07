#!/usr/local/bin/python
# Update Firmware Versions and Verify Readout Modules and Calibration Units

import sqlite3
import os
import sys
import time
from shutil import copyfile
import django
import json
from pprint import pprint

sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from qie_cards.models import QieCard, ReadoutModule, CalibrationUnit, Location, RmLocation, CuLocation

def printRMFW(rm):
    output = "{0} - {1} {2} {3} - {4} {5}"
    print output.format(rm.card_1, rm.card_1.bridge_major_ver, rm.card_1.bridge_minor_ver, rm.card_1.bridge_other_ver,
                        rm.card_1.igloo_major_ver, rm.card_1.igloo_minor_ver)
    print output.format(rm.card_2, rm.card_2.bridge_major_ver, rm.card_2.bridge_minor_ver, rm.card_2.bridge_other_ver,
                        rm.card_2.igloo_major_ver, rm.card_2.igloo_minor_ver)
    print output.format(rm.card_3, rm.card_3.bridge_major_ver, rm.card_3.bridge_minor_ver, rm.card_3.bridge_other_ver,
                        rm.card_3.igloo_major_ver, rm.card_3.igloo_minor_ver)
    print output.format(rm.card_4, rm.card_4.bridge_major_ver, rm.card_4.bridge_minor_ver, rm.card_4.bridge_other_ver,
                        rm.card_4.igloo_major_ver, rm.card_4.igloo_minor_ver)

# Update QIE Card Bridge Firmware in database
def updateBridge(card, fw):
    b_fw = fw.split(' ')
    card.bridge_major_ver = "0x" + b_fw[0][-1:].zfill(2)
    card.bridge_minor_ver = "0x" + b_fw[1][-1:].zfill(2)
    card.bridge_other_ver = "0x" + b_fw[2][-4:].zfill(4)
    card.save()

# Update QIE Card Igloo Firmware in database
def updateIgloo(card, fw):
    i_fw = fw.split(' ')
    card.igloo_major_ver = "0x" + i_fw[0][-1:].zfill(2)
    card.igloo_minor_ver = "0x" + i_fw[1][-1:].zfill(2)
    card.save()

# Process files in directory
def process(directory):
    readMods = ReadoutModule.objects.all()
    qieCards = QieCard.objects.all()
    file_list = []
    rm_count = 0
    loc_count = 0
    for subdir, dirs, files in os.walk(directory):
        for f in files:
            file_list.append(os.path.join(subdir,f))
    for fileName in file_list:
        # Process File 
        rbx = fileName[-2:]
        rbx = str(int(rbx))
        print "\nFile: {0} RBX: {1}".format(fileName,rbx)
        with open(fileName) as dataFile:
            data = json.load(dataFile)
        #pprint(data)
        
        # Get RM Unique IDs from File
        rm_uid_list = []
        rm_list = []
        rm_slot_list = []
        bridge_fw_list = []
        igloo_fw_list = []
        for i in xrange(1,5):
            b_fw = []
            i_fw = []
            try:
                # RM UID from RBX Run 
                uid = data["{0}_{1}_RMID".format(rbx,i)]
                try:
                    # Get RM from database using UID from RBX Run
                    rm = readMods.get(rm_uid=uid)
                    rm_uid_list.append(uid)
                    rm_list.append(rm)
                    rm_slot_list.append(i)
                    print "RM_{0}: {1} --- {2}".format(i, uid, rm)
                    for j in xrange(4):
                        b_fw.append(data["{0}_{1}_BRIDGE_FW_{2}".format(rbx,i,j)])
                        i_fw.append(data["{0}_{1}_IGLOO_FW_{2}".format(rbx,i,j)])
                    bridge_fw_list.append(b_fw)
                    igloo_fw_list.append(i_fw)
                except ReadoutModule.DoesNotExist:
                    print "RM_{0}: {1} does not exist in database".format(i, uid)
            except KeyError:
                print "RM_{0}: Not found in rbx run file".format(i)
        for i, rm in enumerate(rm_list):
            # RM Number 
            print "\nRM {0}".format(rm)
            # Previous and Current Location
            previous_location = RmLocation.objects.filter(rm=rm).order_by("date_received").reverse()[0].geo_loc
            current_location = "Installed in RBX {0} RM-Slot {1} for B904 Burn-In".format(rbx, rm_slot_list[i])
            print "Previous Location: {0}".format(previous_location)
            # Previous Firmware
            print "Previous Firmware"
            printRMFW(rm)
            card_list = [rm.card_1, rm.card_2, rm.card_3, rm.card_4]
            for j, card in enumerate(card_list):
                b_fw = bridge_fw_list[i][j]
                i_fw = igloo_fw_list[i][j]
                updateBridge(card, b_fw)
                updateIgloo(card, i_fw)
            
            if previous_location != current_location:
                RmLocation.objects.create(geo_loc=current_location, rm=rm)
                loc_count += 1
            
            # Updated Location and Firmware 
            current_location = RmLocation.objects.filter(rm=rm).order_by("date_received").reverse()[0].geo_loc
            print "Current Location: {0}".format(current_location)
            print "Current Firmware"
            printRMFW(rm)
            rm_count += 1
    return (loc_count, rm_count)

def getCUBarcode(rbx):
    cuBarcodes = [36, 19, 43, 20, 42, 7, 35, 31, 9, 37, 
                  8, 32, 33, 34, 40, 38, 41, 44, 39, 30]
    return cuBarcodes[rbx]

def updateCU(rbx,uid):
    calibUnits = CalibrationUnit.objects.all()
    qieCards = QieCard.objects.all()
    barcode = getCUBarcode(rbx)
    try:
        cu = calibUnits.get(cu_number=barcode)
        return cu 
    except CalibrationUnit.DoesNotExist:
        print "CU {0} not found in DB".format(barcode)
        for q in qieCards:
            q_uid = q.get_uid_mac_simple()
            if uid == q_uid:
                cu_qie = q
                break
        print "Uploading CU {0} : QIE card {1} : UID {2}".format(barcode,cu_qie,cu_qie.get_uid_mac_simple())
        builder = "Mandakini"
        building = "CERN B904"
        CU = CalibrationUnit(cu_number=barcode,
                             cu_uid=uid,
                             qie_card=cu_qie,
                             assembler=builder,
                             place=building)
        CU.save()
        CuLocation.objects.create(geo_loc=building, cu=CU)
        return CU

def fwUpdate(logFile):
    updatedRM = 0
    updatedCU = 0
    readMods = ReadoutModule.objects.all()
    qieCards = QieCard.objects.all()
    with open(logFile) as dataFile:
        data = json.load(dataFile)
    rbxList = list(i for i in xrange(1,19))
    rmList  = list(i for i in xrange(1,5))
    cardList  = list(i for i in xrange(1,5))
    for rbx in rbxList:
        # Readout Modules 
        for rm in rmList:
            try:
                # RM UID from RBX Run 
                uid = data["{0}_{1}_RMID".format(rbx,rm)]
                print "{0}_{1}_RMID : {2}".format(rbx,rm,uid)
                try:
                    RM = readMods.get(rm_uid=uid)
                    rmCards = [RM.card_1, RM.card_2, RM.card_3, RM.card_4]
                    for card in cardList:
                        b_fw = data["{0}_{1}_BRIDGE_FW_{2}".format(rbx,rm,card-1)]
                        i_fw = data["{0}_{1}_IGLOO_FW_{2}".format(rbx,rm,card-1)]
                        updateBridge(rmCards[card-1], b_fw)
                        updateIgloo(rmCards[card-1], i_fw)
                    previous_location = RmLocation.objects.filter(rm=RM).order_by("date_received").reverse()[0].geo_loc
                    current_location = "Installed in RBX {0} RM-Slot {1} for B904 Burn-In 2".format(rbx, rm)
                    if previous_location != current_location:
                        RmLocation.objects.create(geo_loc=current_location, rm=RM)
                    updatedRM += 1
                except ReadoutModule.DoesNotExist:
                    print "{0}_{1} : RM {2} does not exist in the DB".format(rbx,rm,uid)
            except KeyError:
                print "{0}_{1}_RMID : {2}".format(rbx,rm,"RM not found in RBX Log File")
        # Calibration Unit
        try:
            # CU UID from RBX Run 
            uid = data["{0}_CALIB_QIEID".format(rbx)]
            print "{0}_CALIB_QIEID : {1}".format(rbx,uid)
            
            CU = updateCU(rbx,uid)
            b_fw = data["{0}_CALIB_BRIDGE_FW".format(rbx)]
            i_fw = data["{0}_CALIB_IGLOO_FW".format(rbx)]

            updateBridge(CU.qie_card, b_fw)
            updateIgloo(CU.qie_card, i_fw)
                    
            previous_location = CuLocation.objects.filter(cu=CU).order_by("date_received").reverse()[0].geo_loc
            current_location = "Installed in RBX {0} B904 Burn-In 2".format(rbx)
            if previous_location != current_location:
                CuLocation.objects.create(geo_loc=current_location, cu=CU)
            
            updatedCU += 1
        except KeyError:
            print "{0}_CALIB_QIEID : {1}".format(rbx,"CU not found in RBX Log File")

    return (updatedRM,updatedCU)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        #result = process(sys.argv[1])
        #print "\nLocation Updated for {0} Readout Modules".format(result[0])
        #print "Firmware Updated for {0} Readout Modules\n".format(result[1])
        result = fwUpdate(sys.argv[1])
        print "Number RM Updated: {0}".format(result[0])
        print "Number CU Updated: {0}".format(result[1])
    else:
        #print "Please provide a directory containing rbx runs."
        print "Please provide an RBX log file."


