# Python_DICOM-RT-MetricExtractor
Process DICOM-RT files with a simple GUI to get specified metrics and a nice DVH plot. You can process many plans at once.

How to use?:
- start the program with your python compiler (maybe you have to install needed packages -> pydicom and dicompyler-core)
- choose a directory with DICOM-RT-files (you need the following files per plan: RT, RS, RD)
- the script is tested with Eclipse-Exports

Here is a standard use-case for this script

![GIF 1](https://github.com/Kiragroh/Python_DICOM-RT-MetricExtractor/blob/main/DICOM-RT%20Metric-Extractor.gif)

Note:
- For clinical use I compiled this program with Auto-Py-To-Exe in OneFile-Mode with terminal window (the terminal is utilized as a status viewer).
- I developed the GUI and the File-Management but the Metric-Extraction and DVH-generation is mainly dependend on the very nice Python-package Dicompyler-Core (https://github.com/dicompyler/dicompyler-core) but I did a few (optional) customizations to the site-package for clinical use (for example the extracted metrics used in the '.decribe-function').
- For dataMining purposes, I would recommend to change the metric-txt-Output per plan to a global csv-Output, where all plans are listed.
