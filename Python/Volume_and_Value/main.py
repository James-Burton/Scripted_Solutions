## script main

import os, sys, arcpy, shutil, xlsxwriter, psutil
from arcpy import env
import pandas as pd
from datetime import datetime
import time
import getpass
from openpyxl import load_workbook
sys.path.append(r'[/can/not/share/this.path')
import  custom_corp_library as corp_library
import VnV_library as vLib
## sequence is supposed to be script recepticle for all speradsheet items.
import VnV_table_library as rsqnc

sys.path.append(__file__)
__file__ = sys.argv[0]

##################### Set Date, Time; start timer, set memory access ##############################
test=1
## starts program timer
t0= time.clock()
## get username from system for Data Package Report
username = getpass.getuser()
## set script name for Data Package Report
##ScriptName=os.path.basename(__file__)
ScriptName='VnV_MainScript.py'
## set script contact info for Data Package Report
ScriptContact='REX'
## set whom created for, for Data Package Report
ScriptFor='requestee_name'
## set version and publish date for Data Package Report
ScriptV="Version: #TEST"
ScriptP='NOT PUBLISHED'
## set github link for script review for Data Package Report
GitLink='NA'
## set process for memory usage report, for determining data leaks
process = psutil.Process(os.getpid())
print(str((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))+" MB in use upon start.")
m0=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
## Set log tracker status to failed until script completes all functions successfuly
PrP="FAILED"
## gets date for temporary folder creation
rightnow= datetime.now()
## Sets date for temporary folder creation
Today= rightnow.strftime('%Y_%m_%d')

##################### Set connection environment ###############################
if test <0:
## import bc gov functions for bcgw connection
## opens one window at start for user to enter info in instead of looking for connection
    corp_python_utils = corp_library.corp_python_utilities()
    bcgw_connection = corp_python_utils.determain_connection_to_bcgw()
    print(bcgw_connection)

m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 1")

##################### Set Globally Needed Variables ###################################
## the container is set to the scripts file for now.
Container = (os.path.dirname(__file__))
## Make a temporary container path inside container folder
TempContainer=os.path.join(Container+ '\\FirstNation_trial_Temp%s' % Today)
## this is for your out report data package if you want to change the name
report_out=os.path.join(TempContainer+'\\DataPackage.xlsx')
#################### Set Spatial Locations  ################################
## This layer will become the AOI
aoiSubUnits= r'A/FIRST/Nation/inner_boundary.shp'
## Identify the three fields for the union from the aoiSubUnits input.
## col# is for output report column headers and various filters
col2="LAXWIIYIP"
col3= "SIMGIIGYET"
col4="WATERSHED_"
## This layer is locally stored Cash Sales
SkeenaD=    r'Local/Small/Scale/Harvest/Data.shp'
## BCGW roads is manually converted to shapefile and only needs updating once a year
## There is some sort of issue with road layer and caps itself off at ~ 85 thousand instead of showing all records
## last update: 2021
RDS =       r"NOT/REAL/PATH/FTEN_ROAD_SEGMENT_LINES_SVW.shp"
## TSA kept locally. Shapefile is dissolved by TSA Number and Desc, 2021.
## There is a topo error somewhere in BCGW Feature Class which prohibits automation.
TSA =       r'NOT/REAL/PATH/FADM_TSA.shp'
## The column for TSA Summary, Full field would be TSA NUMBER DESCRIPTION (too long)
tsa_col ="TSA_NUMBER"
## Test Data Location
HARVAUTH =  r"NOT/REAL/PATH/FTEN_HARVEST_AUTH_POLY_SVW.shp"
OPENINGS =  r"NOT/REAL/PATH/RSLT_OPENING_SVW.shp"
CUTBLOCK =  r"NOT/REAL/PATH/FTEN_CUT_BLOCK_POLY_SVW.shp"
RDS =       r"NOT/REAL/PATH/FTEN_ROAD_SEGMENT_LINES_SVW.shp"
RSRVS=      r"NOT/REAL/PATH/FTEN_FOREST_COVER_RESERVE_SVW.shp"
## Data location and name lists for various functions.
## If you add a data source, or remove, update this list. Ensure List matches heirachy of layer preferenced order for querying.
inData_list= [TSA,RDS,HARVAUTH,CUTBLOCK, SkeenaD,OPENINGS,RSRVS]
lyr_list = ['TSA','RDS', 'HARVAUTH','CUTBLOCK', 'SkeenaD','OPENINGS','RSRVS']
## Primary Timber Mark, Forest File ID, and Cutting Permit Field Names
## Primary work with everything except cutblocks, and does not always match tabular equivalent.
spatialTM1="TIMBER_MAR"
spatialFF1="FOREST_FIL"
cuttingPE1="CUTTING_PE"
## Secondary Timber Mark Forest File ID and Cutting Permit Field Names
## Works with Cutblocks.
spatialFF2="HARVEST__2"
cuttingPE2="HARVEST__1"



MasterSpatial="MasterSpatial"
MasterSpatial2="MasterSpatial2"


wrkData_list = []
wrkLYR_list = []


## This is the Scale Data spreadsheet with Scale Data and D-Mark appended manually.
ScaleData = r'NOT/REAL/PATH/ScaleData.xlsx'
## Tabular Field names in Scale Data spreadsheet.
## be sure to remove spaces and replace with _ before processing..
tabularTM = "Timber_Mark"
tabularFF="Licence"
tabularCuttingPE="Cutting_Permit_ID"
tabularYear = "Scaled_Year"
tabularVolume= "Total_Volume"
tabularValue = "Total_Value"
## Hold unique Timber Marks from input scale data
UniTM=[]
## open scale data as pandas dataframe
dataOG = pd.read_excel(ScaleData)
## make list from all Timber Marks
UniTM=dataOG[tabularTM].tolist()
## reduce list with lambda
UniTM=reduce(lambda l, x: l.append(x) or l if x not in l else l, UniTM, [])
## encode list to appropriate type.
y=0
for x in UniTM:
    UniTM[y]=x.encode('ascii')
    y+=1
## delete the two variables we dont need.
del dataOG
del y
## set the rest of the variables for out report
col0=spatialFF1
col1=spatialTM1
col5 ="TM_Gross_AREA_HA"
col6 ="TM_AOI_Gross_AREA_HA"
col7='TM_NET_AREA_HA'
col8='TM_AOI_NET_AREA_HA'
## this will be the pandas dataframe with our out report matches
masterPD=pd.DataFrame()



################ unsure unsure unsure sunurenuernusrse

TM_VolAv_HA='Gross_Volume_Average'
TM_ValAv_HA='Gross_Value_Average'
TM_VolAv_Net='Net_Volume_Average'
TM_ValAv_Net='Net_Value_Average'
##UniTM=[]
##UniPE=[]
z=1 ## for triple strip counter



m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 2")

## Make temp folder from VnV Library
vLib.MakeTempFolder(TempContainer, report_out)
## Make the temp GDB and set the Temp GDB variable for global use.
TempGDB = arcpy.CreateFileGDB_management(TempContainer, 'TempGDB.gdb', '10.0')
## write initial details to data apckage called in from report sequence Library
rsqnc.reportBasics(username,ScaleData,TSA,HARVAUTH,OPENINGS,RDS,CUTBLOCK,RSRVS,aoiSubUnits,SkeenaD,col2,col3,col4,Today,report_out,ScriptName,ScriptContact,ScriptFor,ScriptV, ScriptP,GitLink, UniTM)
del username,ScriptName,ScriptContact,ScriptFor,ScriptV, ScriptP,GitLink

m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 3")

## Copying input SDE data and pasting to Temp Folder as a SHPs
## OR
## map to local.
for sdeFC in inData_list:
    ## if input data is a shp
    if ".shp" in sdeFC:
        ## split the file path at back slashes
        FC_splitter=sdeFC.split('\\')
        ## take the last item in new list, adds shapefile to our working data list
        wrkData_list.append(str(FC_splitter[-1]))
    ## if input item not a shp
    else:
        ## make the bcgw layer into a shapefile
        vLib.getBCGWshp(bcgw_connection,sdeFC,TempContainer)
        ## split the file path at .
        FC_splitter=sdeFC.split('.')
        ## add shapefile to working data list.
        wrkData_list.append(str(FC_splitter[1]+".shp"))

m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 4")

## Make LYRs of our shapefiles. You can skip
x=0
for lyrNAME in lyr_list:
    ## set the feature class shp root name
        FCshp=inData_list[x]
        ## pass shp and lyr name thru
        vLib.makeSHPlyr(TempGDB,FCshp,lyrNAME)
        ## now make a working lyr list which is lyr list with suffix lyr
        wrkLYR_list.append(str(lyrNAME+"_lyr"))
        ## add one to lyr counter
        x+=1
## delete lyr coutner.
del x

m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 5")

## delete bcgw connection to save on memory use.
if test<0:
    del corp_python_utils
    del bcgw_connection

## Begin main iteration component
x=0
## in a while loop from legacy script transfer. Can modify if time later to just be entire function.
while x<len(wrkLYR_list):
    ## set environment for function
    arcpy.env.workspace=str(TempGDB)
    ## working layer is from our working layer list, which is layer list, + _lyr suffix
    workingLYR =  wrkLYR_list[x]
    ## make tsa list container
    tsa_list=[]
    ## intersect tsa with AOI to create a list of what TSA's the AOI intersects
    arcpy.SelectLayerByLocation_management(workingLYR, 'intersect', aoiSubUnits)
    ## VnV library examines identified column and creates list of TSA with "manual encoding"
    vLib.sumField(workingLYR,tsa_col,tsa_list)
    ## fcname is supposed to be used more often, but I seem to only find one reference for this variable. Consider change.
    fcname=str(lyr_list[0])
    ## copy selected records from working tsa layer and save selection as a feature class in our temp gdb. This will be for cartography purposes done manually by GIS tech.
    arcpy.CopyFeatures_management(workingLYR,fcname)
    ## delete the working lyr to save on space
    arcpy.Delete_management(workingLYR)
    ## write the tsa list to Main Page of our data package report.
    rsqnc.writeDetails(2,11,tsa_list,'MainPage',report_out)
    ## delete tsa list container
    del tsa_list
    ## delete fcname variable to maintain minimal space use.
    del fcname
    ## add one to x, legacy counter for while loop. X needs to go into Make Master.
    x+=1
    ## Make Master goes through everything and selects what we need and does everything all the way to making master spatial.
    ## view VnV library for details.
    vLib.MakeMaster(TempGDB,lyr_list,wrkLYR_list,spatialFF1,spatialTM1,cuttingPE1,spatialFF2,cuttingPE2,aoiSubUnits,ScaleData,tabularTM, tabularFF, TempContainer,MasterSpatial,col5,col7,UniTM,report_out)
    ## x counter becomes x to represent 6 layer manipulation time (6 layer is RSRVS (remember 0 is a number, so counts start at 0))
    x=6
    ## Begin the reserves delete function. This is for net area calculations.
    vLib.RSRV_del(TempGDB, lyr_list,x, workingLYR, TSA, MasterSpatial,spatialFF1,spatialTM1,cuttingPE1,col7,aoiSubUnits)
    ## sets x counterto 7 which is lenght of lyr list. Loops to top, passes everything.
    x+=1
## delete x again to save that tiny bit of space.
del x
## This function in VnV library does both Gross AOI TM and Net AOI TM functions

vLib.BridgeTheGap(TempGDB, aoiSubUnits,MasterSpatial,MasterSpatial2,col5,col6,col7,col8,spatialTM1,spatialFF1,cuttingPE1,col2,col3,col4)
## This function makes a new spatial layer and adds the net columns to gross column. Theoritically this created spacial is saved for cartographic purposes, if needed as determined by the gis tech and actual request.
vLib.TLR('MasterSpatial2','MasterSpatial5',spatialFF1,spatialTM1,col0,col1,col2,col3,col4,col5,col6,col7,col8,TempContainer, masterPD)

m1=int((psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2))
m2=m1-m0
m0=m1
print(str(m2)+" MB increase 6")

## ending script. Tells me done in interpreter, adds overall time to report and then tells us the overall time in interpreter, which will be a bit larger than actual time posted to datapackage. This number, multipled by 6 is roughly the time it takes to do something similar, manually, with more mistakes.
print('DONE :)')
t1 = time.clock() - t0
book=load_workbook(report_out)
sheet4=book['RunSummary']
runtime=(t1 - t0)
sheet4['B7']=runtime
book.save(report_out)
print('Time elapsed: ', (t1 - t0)) # CPU seconds elapsed (floating point)

