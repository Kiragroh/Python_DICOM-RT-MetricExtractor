#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dvhcalc.py
"""Calculate dose volume histogram (DVH) from DICOM RT Structure/Dose data."""
# Copyright (c) 2016 gluce
# Copyright (c) 2011-2016 Aditya Panchal
# Copyright (c) 2010 Roy Keyes
# This file is part of dicompyler-core, released under a BSD license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/dicompyler/dicompyler-core/

from __future__ import division
import pylab as pl
from dicompylercore import dicomparser, dvhcalc
import os
import tkinter as tk
from tkinter import *
import tkinter.filedialog
import pathlib
import pydicom as dicom
import time


import logging
#logger = logging.getLogger('dicompylercore.dvhcalc')

# --- functions ---

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles

def select_all():
    for j in checkbutton_list:
        j.select()

def deselect_all():
    for j in checkbutton_list:
        j.deselect()

def browse2():
    global filez2
    if window.counter < 1:
        opath=ent2.get()
        initialpath = pathlib.Path(opath)
        if initialpath.exists():
            filez2 = opath
        else:
            filez2 = tkinter.filedialog.askdirectory(parent=window, initialdir="currdir", title='Change Input-Path')
            if filez2 =="" and ent2.get()!="":
                return
    else:
        filez2 = tkinter.filedialog.askdirectory(parent=window, initialdir="currdir", title='Change Input-Path')
        if filez2 == "" and ent2.get() != "":
            return
    window.counter += 1
    ent2.delete(0, 'end')
    ent2.insert(20, filez2)

def browse():
    global filez
    if window.counter < 1:
        ipath="//localhost/TCS"
        initialpath = pathlib.Path(ipath)
        if initialpath.exists():
            filez = ipath
        else:
            filez = tkinter.filedialog.askdirectory(parent=window, initialdir="currdir", title='Change Input-Path')
            if filez =="" and ent1.get()!="":
                return
    else:
        #btn0['text'] = 'Change Input-Path'
        filez = tkinter.filedialog.askdirectory(parent=window, initialdir="currdir", title='Change Input-Path')
        if filez == "" and ent1.get() != "":
            return
    window.counter += 1
    #filez = tkinter.filedialog.askdirectory(parent=window, title='Choose a file')
    
    ent1.delete(0, 'end')
    ent1.insert(20, filez)
    

    dirs = getListOfFiles(filez)
    #create sorted list of dcm files
    included_extensions = ['dcm']
    dirs2 = [fn for fn in dirs
             if any(fn.endswith(ext) for ext in included_extensions)]
    #dirs2 = filter(os.path.isfile, glob.glob(dirs + "*.dcm"))
    #dirs2.sort(key=lambda x: os.path.getctime(x))
    global dirs3
    dirs3 = sorted(dirs2, key=lambda x: os.path.getmtime(x), reverse=True)


    # remove previous IntVars
    intvar_dict.clear()

    # remove previous Checkboxes
    for cb in checkbutton_list:
        cb.destroy()
    checkbutton_list.clear() 
    
    
    for filename in dirs3:
        # create IntVar for filename and keep in dictionary
        intvar_dict[filename] = tkinter.IntVar()

        # create Checkbutton for filename and keep on list
        dspd = dicom.read_file(filename)
        if dspd.Modality == 'RTPLAN':
            c = tkinter.Checkbutton(text,activebackground='green', cursor='arrow',text=str(dspd.Modality)+': '+str(dspd.PatientName)+'_'+str(dspd.RTPlanLabel)+'_'+str(dspd.InstanceCreationDate)+'_'+str(dspd.InstanceCreationTime), bg='#EDF5FF', variable=intvar_dict[filename])
            c.pack(anchor=W, padx=25, pady=2, side=TOP)
            checkbutton_list.append(c)
            text.window_create("end", window=c)
        #else:
        #    c = tkinter.Checkbutton(text,activebackground='green', cursor='arrow',text=str(dspd.Modality)+': '+str(dspd.PatientName)+'_'+str(dspd.InstanceCreationDate)+'_'+str(dspd.InstanceCreationTime),bg='white', variable=intvar_dict[filename])

            
def Auswertung():
    global rtssfile
    rtssfile = ''
    global rtdosefile
    rtdosefile = ''
    global rpfile
    rpfile = ''
    global counter
    counter=0
    global rpath
    rpath = ent2.get()

    # loop-info: for every selected plan the matching RS- and RD-file will be found and the now completed DICOM-RT-Dataset will be processed
    for key, value in intvar_dict.items():
        #print('CB-list:', key, value.get())
        if value.get() > 0:
            #print('selected:', key)
            counter+=1
            #print(counter)
            #if key.lower().startswith('rs') or key.lower().startswith('rts'):
            #    rtssfile = filez + '/' + key
            #if key.lower().startswith('rd') or key.lower().startswith('rtd'):
            #    rtdosefile = filez + '/' + key
            #if key.lower().startswith('rp') or key.lower().startswith('rtp'):

            rpfile = key
            dp = dicom.read_file(rpfile)
            plansopUID = dp.SOPInstanceUID
            planrefSSuid = dp.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID

            for filename in [x for x in dirs3 if (os.path.basename(os.path.realpath(x)).lower().startswith('rd') or os.path.basename(os.path.realpath(x)).lower().startswith('rtd'))]:
                dd = dicom.read_file(filename)
                if dd.Modality == 'RTDOSE' and dd.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID==plansopUID:
                    rtdosefile = filename
                    break
            for filename in [x for x in dirs3 if (os.path.basename(os.path.realpath(x)).lower().startswith('rs') or os.path.basename(os.path.realpath(x)).lower().startswith('rts'))]:
                ds = dicom.read_file(filename)
                if ds.Modality == 'RTSTRUCT' and ds.SOPInstanceUID==planrefSSuid:
                    rtssfile = filename
                    break
            
            if rtssfile == '' or rtdosefile == '':
                print('ERROR: DICOM-RT-Dataset (RP+RD+RS) for RTPLAN "{}" of "{}" is not complete and will be skipped.'.format(
                dp.RTPlanLabel, dp.PatientID))
                print('')
            else:
                print('Analysis for RTPLAN "{}" of "{}" has started.'.format(
                    dp.RTPlanLabel, dp.PatientID))
                RTss = dicomparser.DicomParser(rtssfile)
                dd = dicom.read_file(rtdosefile)
                dp = dicom.read_file(rpfile)
                dss = dicom.read_file(rtssfile)

                # print("planFile")
                # print(dp.SOPInstanceUID)
                # print(dp.ReferencedStructureSetSequence)
                # print("doseFile")
                # print(dd.ReferencedRTPlanSequence)
                # print("ssFile")
                # print(dss.SOPInstanceUID)

                if str(dss.PatientName) != str(dp.PatientName) != str(dd.PatientName):
                    print('ERROR: \nDICOM-Files unterschiedlicher Patienten ausgewählt.')
                    time.sleep(5)
                    sys.exit()

                totalPdose = 0

                # timestr = time.strftime("%Y%m%d-%H%M%S")

                # save location for results
                rpath = ent2.get()
                #resultpath = pathlib.Path(rpath)
                if len(rpath) > 0:
                    filez2 = rpath
                else:
                    filez2 = os.path.dirname(rpfile)

                ##start txt file
                orig_stdout = sys.stdout
                f = open(
                    filez2 + '/' + dp.InstanceCreationDate + '_' + dp.InstanceCreationTime + '_' + dp.PatientID + '_' + scriptname + '.txt',
                    'w')
                sys.stdout = f

                if getattr(dp, 'FractionGroupSequence', 'no') != "no":
                    if "Brachy Application Setup Dose" in str(dp.FractionGroupSequence):
                        totalPdose = dp.FractionGroupSequence[0].ReferencedBrachyApplicationSetupSequence[
                            0].BrachyApplicationSetupDose
                        print("TRAK[Gy]:\t{:0.5f}".format(
                            float(dp.ApplicationSetupSequence[0].TotalReferenceAirKerma) / 1000000))
                        i = 0
                        while i < len(dd.StructureSetROISequence):
                            if dd.StructureSetROISequence[i].ROINumber == dd.RTDoseROISequence[i].ReferencedROINumber:
                                print(
                                    "{}[{}]:\t{:0.2f}".format(dd.StructureSetROISequence[i].ROIName,
                                                              dd.RTDoseROISequence[i].DoseUnits.capitalize(),
                                                              dd.RTDoseROISequence[i].DoseValue))
                                # print (dd.StructureSetROISequence[i].ROIName)
                                # print (dd.RTDoseROISequence[i].DoseValue)
                                i = i + 1
                            else:
                                i = i + 1
                        print("")

                if getattr(dp, 'DoseReferenceSequence', 'no') != "no" and totalPdose == 0:
                    if "Target Prescription Dose" in str(dp.DoseReferenceSequence):
                        totalPdose = dp.DoseReferenceSequence[0].TargetPrescriptionDose

                # Obtain the structures and DVHs from the DICOM data
                RTstructures = RTss.GetStructures()
                # Generate the calculated DVHs
                calcdvhs = {}
                j = 0
                for key, structure in RTstructures.items():
                    if not (structure['name'].lower().startswith("z") or structure['type'].lower().startswith(
                            "control")):
                        calcdvhs[key] = dvhcalc.get_dvh(rtssfile, rtdosefile, key)
                        if calcdvhs[key].max > 0:
                            calcdvhs[key].rx_dose = totalPdose
                            print("Found PrescriptionDose[Gy]:\t{:0.2f}".format(totalPdose))
                            print(calcdvhs[key].describe())
                            print("")
                        if (key in calcdvhs) and (len(calcdvhs[key].counts) and calcdvhs[key].counts[0] != 0) and \
                                calcdvhs[key].max > 0 and not structure['type'].lower().startswith("external") and not structure['name'].lower().startswith("ph_"):
                            # print ('DVH found for ' + structure['name'])
                            # pl.plot(calcdvhs[key].counts * 100/calcdvhs[key].counts[0],
                            #        color=dvhcalc.np.array(structure['color'], dtype=float) / 255,
                            #        label=structure['name'],
                            #        linestyle='solid')
                            calcdvhs[key].relative_volume.plot()
                            pl.gca().get_lines()[j].set_color(dvhcalc.np.array(structure['color'], dtype=float) / 255)
                            j = j + 1

                sys.stdout = orig_stdout
                f.close()

                pl.xlabel('Dose [Gy]')
                pl.ylabel('Volume [%]')
                pl.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                pl.setp(pl.gca().get_legend().get_texts(), fontsize='x-small')
                pl.savefig(
                    filez2 + '/' + dp.InstanceCreationDate + '_' + dp.InstanceCreationTime + '_' + dp.PatientID + '_DVH' + '.png',
                    dpi=175, bbox_inches='tight')
                pl.close()

                print('DICOM-RT-Dataset (RP+RD+RS) for RTPLAN "{}" of "{}" was successfully processed.'.format(
                    dp.RTPlanLabel, dp.PatientID))
                print('')
    #window.destroy()
    #window.quit()
    #return rpath
    if len(rpath)==0:
     rpath = filez
    print('-----------------------------------------------------------------------------------------')
    print("Finish! Your selected plans were processed and the results are saved in %s" % rpath)
    print('')
    #print('Please close the program window to exit...')


# ========================== Main =========================== #

	
#print('After selecting a DICOM-folder with RD- & RS-file, the analysis begins....')

# Obtain the dose points from the DICOM data
version = "2.0"
scriptname = "MetricExtractor_v{}".format(version)
#global filez2
#global filez
#filez = ""
#filez2 = ""

# to keep all IntVars for all filenames
intvar_dict = {}
 # to keep all Checkbuttons for all filenames

checkbutton_list = []

window = tkinter.Tk()
window.counter = 0
window.title("Metric Extractor by MG (v.{}) - RP-File-Selection".format(version))
#window.iconbitmap("metric.ico")
#window..iconbitmap(default=resource_path("metric.ico"))

w = 600 # width for the Tk root
h = 650 # height for the Tk root

# get screen width and height
ws = window.winfo_screenwidth() # width of the screen
hs = window.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
window.geometry('%dx%d+%d+%d' % (w, h, x, y))


lbl = tkinter.Label(window, text="Input-Path")
lbl.pack(pady = (5,0))
ent1 = tkinter.Entry(window, width=100)
ent1.pack()
btn0 = tkinter.Button(window, text="  Browse Input-Path  ", bg = '#BAD9FF', command=browse)
btn0.pack(pady=(5,0))

lbl2 = tkinter.Label(window, text="Output-Path (empty: Input=Output)")
lbl2.pack(pady = (15,0))
ent2 = tkinter.Entry(window, width=100)
opath="//variancom/Daten/PhysikDB/Gyn Afterloading QA/Results_MetricExtractor"
#opath="/Users/Max/Desktop"
standardOpath = pathlib.Path(opath)
if standardOpath.exists():
    ent2.insert(END,opath)
ent2.pack()
btn1 = tkinter.Button(window, text="  Browse Output-Path  ", bg = '#BAD9FF',command=browse2)
btn1.pack(pady=(5,0))

btn2 = tkinter.Button(window, bg='#81F46A', text="   START   ", command=Auswertung)
btn2.pack(pady = (15,10))



vsb = tk.Scrollbar(orient="vertical")
text = tk.Text(window, width=40, height=20, yscrollcommand=vsb.set, bg='#EDF5FF')
text.config(state=DISABLED)
vsb.config(command=text.yview)
vsb.pack(side="right",fill="y")
text.pack(side="top",fill="both",expand=True)

btn3 = tkinter.Button(window, text="  Select All  ", command=select_all)
btn3.pack(side="left",pady = (0,0))
btn4 = tkinter.Button(window, text="  Deselect All  ", command=deselect_all)
btn4.pack(side="left",pady = (0,0))

window.mainloop()

#if counter != 3:
#    print('ERROR: \n3 Files sind für die Auswertung notwendig (RD+RS+RP).')
#    time.sleep(5)
#    sys.exit()
#save location for results
#print(rpath)
#if len(rpath)==0:
        #rpath = filez

#time.sleep(1)

#the_input = sys.stdin.readline()
input("Press Enter to exit...")




