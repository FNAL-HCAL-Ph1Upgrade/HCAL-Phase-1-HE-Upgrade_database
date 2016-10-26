# CMS-QIE_database
A web-framework for the CMS HE Phase 1 Upgrade database. Initial QIE Card testing was performed at Fermilab, Summer 2016.
Website: https://nbay11.fnal.gov/cards/catalog
Username/Password: Please email me at caleb_smith2@baylor.edu to request access.
#### 1. Firmware programming of Bridge and Igloo Field Programable Gate Arrays (FPGA).
#### 2. Quality control (QC) tests of read/writes to all registers and micro HCAL Trigger and Readout (uHTR) tests.
#### 3. Calibration of QIE Chips using DC current charge injection.
# Reaout Box (RBX)
Each Readout Box (RBX) contains 4 Readout Modules (RM), 16 QIE Cards, 4 SiPM Control Cards, and 1 Calibration Unit (CU).
Each RBX has 4 MTP cabels, 32 fibers, 192 channels, 192 Silicon Photomultipliers (SiPM), and 192 Bias Voltages (BV).
## Readout Modules (RM)
There are 4 Reaout Modules (RM) per Readout Box (RBX). Each RM contains 4 QIE Cards and 1 SiPM Control Card. Thus each RM has 48 QIE Chips, 48 channels, 8 fibers within 1 MTP cable, and 48 Bias Voltages (BV). 
## QIE Cards
There are 4 QIE Cards per Readout Module (RM) and 16 QIE Cards per Readout Box (RBX). Each QIE Card has 12 QIE Chips, 12 channels, 2 fibers, and 12 Bias Voltages (BV). Note that each fiber has 6 channels.
## SiPM Control Cards
There is 1 SiPM Control Card per Readout Module (RM) and 4 SiPM Control Cards per Readout Box (RBX). Each SiPM Control Card has 48 channels and 48 Bias Voltages (BV) for 48 Silicon Photomultipliers (SiPM).
## Calibrations Units (CU)
There is 1 Calibration Unit (CU) per Readout Box (RBX). Each CU contains 1 Pulser Board and 1 QIE Card.
