#### This script will not run on it's own. This script is called in from VnV main.

## sequence is supposed to be script recepticle for all speradsheet items.
import VnV_table_library as rsqnc
## Misc arcpy library hosts some of the larger geospatial items in order to spread memory usage over mulitple sources.
import VnV_arcpy_library as macpy
## arcpy for a few items in this script.
import arcpy
## os for folder exist check, make folder, path joins.
import os
## shutip for removing folders and copying datapackage.
import shutil
## during folder removal, a one second timer delays script from proceeding to ensure item was deleted.
import time
## pandas for internal list making from scale data
import pandas as pd
## loads excel, check if still needed.
from openpyxl import load_workbook

## Temporary Folder Function
def MakeTempFolder(TempContainer,report_out):
    ## check if folder exists
    if os.path.exists(TempContainer):
        ## delete folder if it exists
        shutil.rmtree(TempContainer)
        ## pause, let folder finish delete
        time.sleep (1)
        ## now make temp folder
        os.makedirs(TempContainer)
    ## if folder did not exist
    else:
        ## now make folder
        os.makedirs(TempContainer)
    ## once folder is made, copy blank data package to temp folder.
    shutil.copy(r'NOT/REAL/PATH/DataPackage.xlsx',report_out)

## if BCGW shapes are used, this will copy the FC as a shapefile. This is so we can check if an item was included into the equation. Needed for QA/QC and results defending..
def getBCGWshp(sde,sdeFC,TempContainer):
    ## sets the bcgw fc path to your path and bcgw name.
    sdeFC_PATH = os.path.join(sde,sdeFC)
    ## copies the sde fc, makes shapefile, places it in temp container.
    arcpy.FeatureClassToShapefile_conversion(sdeFC_PATH,TempContainer)

## Makes a LYR from the shapefiles (either local or from BCGW).
def makeSHPlyr(TempGDB,FCshp,lyrNAME):
    ## not sure if necessary but always important to tell the program where to store geospatial data..
    arcpy.env.workspace=str(TempGDB)
    ## name the layer of the feature class
    fcLYR=str(lyrNAME+"_lyr")
    ## make the lyr
    arcpy.MakeFeatureLayer_management(FCshp, fcLYR)

## makes a list of values from spatial for main script
def sumField(inDATASET,colNAME,outLIST):
    ## using cursor which searches records selected (if selected)
    with arcpy.da.SearchCursor(inDATASET,colNAME) as cursor:
        ## for each record
        for row in cursor:
            ## get the value, should be row not cursor but one cursor will equal row
            field_value=str(cursor)
            ## juggle value, strip beginning off
            field_val_temp = field_value.strip("(u'")
            ## juggle value back, strip end off
            field_value= field_val_temp.strip("'),")
            ## add our value to the lsit to be returned to main script.
            outLIST.append(field_value)
            ## delete variables for better data usage results?
            del field_value
            del field_val_temp

## Make Master function. Debate if more should be in misc py library. kept together for review purposes.
def MakeMaster(TempGDB,lyr_list,wrkLYR_list,spatialFF1,spatialTM1,cuttingPE1,spatialFF2,cuttingPE2,aoiSubUnits,ScaleData,tabularTM, tabularFF, TempContainer,MasterSpatial,col5,col7,UniTM,report_out):

    arcpy.env.workspace=str(TempGDB)
    ## set missing timber mark list to master timber mark list. Items will be removed from missing list as they are found.
    mTMs=[]
    ## not all layers with yeild timber marks. Timber Mark spatial list will be compiled to aid in later process efficeincy.
    tmS_list=[]
    ## set yzy counter, for test purposes really
    yzy=0
    ## set container for max row counts for all input spatials
    MaxAll=[]
    xzx=len(wrkLYR_list)-2
    ## for each working layer in working layer lsit
    for x in wrkLYR_list:
        ## tsa is deleted before reaching this function.
        if x!="TSA_lyr":
            ## retrieve row count for layer as an integer
            mx = int(arcpy.GetCount_management(x).getOutput(0))
            ## append value to max row list
            MaxAll.append(int(mx))
            ## delete mx for better data usage results
            del mx
    ## iterate through unique timbermark master list.
    #print len(UniTM)
    #print UniTM
    for uni in UniTM:
        mTMs.append(uni)
        ## yzy counter for testing caps.

        if yzy<len(UniTM):##(unilen/8): ## 300 magic number for test

            ## set the sql statement to spatial tm1 and item in tm list
            sql=str(spatialTM1+" = '"+uni+"'")
            ## yy set to one to start on rds lyr
            yy=1
            ## identify the right layer to work with, always start with rds
            working_layer=wrkLYR_list[yy]
            ## identify max row count for layer
            ma=MaxAll[yy]
            ## get the road record count as integer
            inRDCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
            ## if our working layer in not in our tm spatial, kep the counter at zero.
            ## layer is added to spatial list on first match.
            if working_layer not in tmS_list:
                inRDCnt =0
            ## personal testing line
            ##print(str(inRDCnt)+" going in to "+working_layer)
            ## some times road layer has issue, try to select records, sometimes wont work hence exception
            try:
                arcpy.SelectLayerByAttribute_management(working_layer,"ADD_TO_SELECTION",sql)
            except:
                ## usually execute error, but not always..
                ## this note only appears in interpreter.
                print('Error!!!')
                print(working_layer)
            ## get record count after attempted selection
            outRDCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
            ## if the count after selection is greater than the seleection count before selection attempt, remove uni item from missing tm list.
            if outRDCnt>inRDCnt:
                mTMs.remove(uni)
                if working_layer not in tmS_list:
                    ## if layer had a record, we need it later. add it to our tm spatial list
                    tmS_list.append(working_layer)
            ## testing lines
            ##print('len of mtms list now :'+str(len(mTMs)))
            ##print(str(outRDCnt)+" going out of "+working_layer)
            print sql
            ## now to query the other layers. Since a road can have all types of timber marks, we know harvest shapes will not have R timber marks. If R timbermark, PASS this.
            if uni[0]!='R':
                ## set yy counter to two to catch Harv Auth layer in list
                yy=2

                ## while yy is less than working layer list.. iterate
                while yy<xzx:
                    ## set working layer to relevant spatial during iteration
                    working_layer=wrkLYR_list[yy]
                    ## set the sql statement to spatial tm1 and item in tm list
                    sql=str(spatialTM1+" = '"+uni+"'")
                    ## retrieve the max row count for relevant layer
                    ma=MaxAll[yy]
                    ## get record count of item before selection
                    inCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
                    ## if our working layer in not in our tm spatial, kep the counter at zero.
                    ## layer is added to spatial list on first match.
                    if working_layer not in tmS_list:
                        inCnt =0
                    ## test line
                    ##print(str(inCnt)+" going in to "+working_layer)
                    ## try instead of force. topo errors will mess with selections
                    try:
                        arcpy.SelectLayerByAttribute_management(working_layer,"ADD_TO_SELECTION",sql)
                    except:
                        print('Execute Error!!!')
                        print(working_layer)
                        print sql
                    ## get after selection record count
                    outCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
                    ## test line
                    ##print(str(outCnt)+" going out of "+working_layer)
                    ## if out selection is greater than selected records going in..
                    if outCnt>inCnt:
                        ## set yy to len of list to break loop
                        yy=len(wrkLYR_list)
                        ## test line
                        ##print("adding wrk lyr len")
                        ## since uni may be removed from missing list during road selection, try not force
                        print(str(working_layer+' found '+uni))
                        if uni in mTMs:
                            mTMs.remove(uni)
                        #except:
                            ## test line
                            # print('mtms list removed already :'+uni)
                        ## we are making a list of layers needed later
                        if working_layer not in tmS_list:
                            ## if layer had a record, we need it later. add it to our tm spatial list
                            tmS_list.append(working_layer)
                            ## test line
                            ##print tmS_list


                    
                    
                    ## add to our yy counter. if record was found, this addition puts the yy over lyr len and breaks loop
                    yy+=1
                try:
                    arcpy.SelectLayerByAttribute_management(wrkLYR_list[-2],"ADD_TO_SELECTION",sql)
                    print(str(wrkLYR_list[-2] + ' found '+uni))
                    if wrkLYR_list[-2] not in tmS_list:
                        ## if layer had a record, we need it later. add it to our tm spatial list
                        tmS_list.append(wrkLYR_list[-2])
                        # print(str(wrkLYR_list[-2]+' added to tms list successfully'))
                except:
                    print('Execute Error!!!')
                    print(working_layer)
                    print sql
                ## delete sql from legacy issue solution
                del sql
            ## keep an eye on this yzy indentation. yzy for testing, but gets moved around too often..
            yzy+=1

    ## get our tm spatial list in proper hierachy for rest of our calculations
    ## use try as not all layers in next steps
    for x in wrkLYR_list:
        ## if our working layer is going into tm spatial layer list
        if x in tmS_list:
            print('pay attention here ------------------')
            ## us the original order of our layers and pop the layers into the right place
            tmS_list.append(tmS_list.pop(tmS_list.index(x)))
            with arcpy.da.SearchCursor(x,spatialFF1) as cursor:
                for row in cursor:
                    print row
        else:
            ## test line
            print(str(x+' not in tms list'))
    ## test line
    print ("length of tmS_list :"+str(len(tmS_list)))
    tmS_listb=[]
    for x in tmS_list:
        print(str(x+' is becoming '+x+'_b'))
        working_layer_b=str(x+'_b')
        arcpy.CopyFeatures_management(x,working_layer_b)
        # if x ==tmS_list[0]:
        #     arcpy.CopyFeatures_management(x,'selectedx')
        #     arcpy.SelectLayerByAttribute_management(x,'CLEAR_SELECTION')
        #     arcpy.CopyFeatures_management(x,'blankx')
        arcpy.Delete_management(x)
        arcpy.MakeFeatureLayer_management(working_layer_b,x)
        tmS_listb.append(working_layer_b)
        del working_layer_b

    del tmS_list
    tmS_list=tmS_listb
    print tmS_list
    print('here you are ----------------------------------------------------------------------------')
    rem1="[u]',() "
    UniFF=[]
    for x in tmS_list:
        fields = [f.name for f in arcpy.ListFields(x)]
        if spatialFF1 in fields:
            with arcpy.da.SearchCursor(x,[spatialFF1,spatialTM1]) as cursor:
                for row in cursor:
                    myFF=str(row[0])
                    for char in rem1:
                        myFF=myFF.replace(char,"")
                    if myFF not in UniFF:
                        UniFF.append(myFF)
            
        else:
            print(spatialFF1+' not in fields')

    print(UniFF)
    print('above is uniFF -----------------------')
    ## encode our new unique forest file list
    y=0
    for x in UniFF:
        UniFF[y]=x.encode('ascii')
        y+=1
    del y

    ## this was for testing mid stream. can be removed once confidence is built in process
    dataOG = pd.read_excel(ScaleData)
    MissingTMs=dataOG[dataOG[tabularTM].isin(mTMs)]
    compMissingTM=os.path.join(TempContainer+ '\\Missing_TimberMarks.xlsx')
    MissingTMs.to_excel(compMissingTM, engine='xlsxwriter')
    del MissingTMs
    del compMissingTM
    rsqnc.writeDetails(2,39,len(mTMs),'RunSummary',report_out)
    
    #FoundTM=dataOG[~dataOG[tabularTM].isin(mTMs)]
    #compFoundTM=os.path.join(TempContainer+ '\\Found_TimberMarks.xlsx')
    #FoundTM.to_excel(compFoundTM, engine='xlsxwriter')
    #del compFoundTM
    #UniFF=FoundTM[tabularFF].unique().tolist()

    ## make list from all Timber Marks
    reportFF=dataOG[tabularFF].tolist()
    ## reduce list with lambda
    reportFF=reduce(lambda l, x: l.append(x) or l if x not in l else l, reportFF, [])

    print(len(UniFF))
    #UniLic=dataOG[tabularFF].unique().tolist()
    #rsqnc.writeDetails(2,41,len(UniLic),'RunSummary',report_out)


    y=0
    for x in reportFF:
        reportFF[y]=x.encode('ascii')
        y+=1
    ## delete the two variables we dont need.
    #del dataOG
    del y



    del mTMs
    # del FoundTM
    # for x in tmS_list:
    #     fields = [f.name for f in arcpy.ListFields(x)]
    #     if spatialFF1 in fields:
    #         with arcpy.da.SearchCursor(x,spatialFF1) as cursor:
    #             for row in cursor:
                    # print(row)
        #else:
            #print(spatialFF1+' not in fields')
        #print(fields)


    LookUpList = r'NOT/REAL/PATH/ScaleData_Master.xlsx'
    LuL=pd.read_excel(LookUpList)
    uniLuL = LuL[tabularFF].unique().tolist()
    x=0
    for uni in UniFF:
        if x!=-10:
            if uni in uniLuL:
                print('starting unilul')
                print(uni)
                tempPanda=pd.DataFrame()
                tempPanda=LuL.loc[LuL[tabularFF]==uni]
                tempDataFrame=dataOG.loc[dataOG[tabularFF]==uni]
                tdf=str(tempDataFrame['Timber_Mark'].unique().tolist()).split(",")
                rem=['"[u','" u',']"','"',"'"]
                tms=[]
                for t in tdf:
                    for rm in rem:
                        # print(t)
                        # print(rm)
                        try:
                            t=t.strip(rm)
                            # print(t)
                        except:
                            print('the same')
                    tms.append(t)
                    print(t)

                tempLuL=str(tempPanda['Associated_Files'].values).strip('["u'+'"'+'"]'+' '+"'").replace('u','').split(',')

                #print(tempPanda)
                #print(tempLuL)
                # L=L.strip(' u')
                print(tmS_list[0])
                with arcpy.da.UpdateCursor(tmS_list[0],[spatialFF1,spatialTM1]) as cursor:

                    for row in cursor:
                        for L in tempLuL:
                            L=L.strip(' u')
                            if len(L)>0:
                                if L[0]=='R':
                                    row0value=row[0].strip('u')
                                    row1value=row[1].strip(' '+'u'+"'")
                                    #print(row0value)
                                    #print(L)
                                    #print('treeble')
                                    if row0value == L :
                                        #print(row1value)
                                        for t in tms:
                                            #print(t)
                                            if t ==row1value:
                                                #print(t+' matches row1val '+uni+' will become row0 value')

                                                row[0]=uni
                                                cursor.updateRow(row)
                                                #rint(str(L+' changed to '+uni+' with timber mark '+t))
                                            # else:
                                            #     print('t and row value one dont match')
                                if L==' ' or L=='' or L is None:
                                    print('L is nothing no worries')
                    print('cursor done')
        x+=1 


    ## set container for missing forest file ids
    mFFs=[]
    ## for each input data, copy the slimmed lyr file from last run


    ffS_list=[]
    ## reset container for max row counts for all input spatials
    MaxAll=[]
    ## for each working layer in tm layer lsit
    for x in tmS_list:
        ## retrieve row count for layer as an integer
        mx = int(arcpy.GetCount_management(x).getOutput(0))
        ## append value to max row list
        MaxAll.append(int(mx))
        ## delete mx for better data usage results
        del mx
    print(MaxAll)
    ## xzx to count through input layers with out inline subtraction each cycle
    xzx=len(tmS_list)-1
    ## yzy counter reset to zero, for testing purposes
    yzy=0
    ## For each unique forest file that has a timber mark that may potentially be matched..
    for uni in reportFF:
        
        print('round three')
        print(uni)
        ## add uni to mffs list, will delete if matched
        mFFs.append(uni)


        ## yzy counter for testing, set to <uni length for full go
        if yzy<=5000000:##(unilen/8): ## 300 magic number for test

            ## set sql
            sql=str(spatialFF1+" = '"+uni+"'")

            ## set
            yy=0
            working_layer=tmS_list[yy]
            inRDCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
            ma=MaxAll[yy]
            if inRDCnt == ma :
                inRDCnt=0
            if working_layer not in ffS_list:
                inRDCnt =0
            print(str(inRDCnt)+" going in to "+working_layer)
            try:
                arcpy.SelectLayerByAttribute_management(working_layer,"ADD_TO_SELECTION",sql)
            except:# ExecuteError:
                # print('Execute Error!!!')
                print(working_layer+' has no records of '+uni)

            outRDCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))
            if outRDCnt>inRDCnt:
                mFFs.remove(uni)
                # print('len of mffs list now :'+str(len(mFFs)))
                if working_layer not in ffS_list:
                    ffS_list.append(working_layer)
                    print ffS_list
            print(str(outRDCnt)+" going out of "+working_layer)
            if uni[0]!='R':
                yy=1
                while yy<len(tmS_list):
                    working_layer=tmS_list[yy]
                    if working_layer=='CUTBLOCK_lyr':
                        spatialFF=spatialFF2
                    else:
                        spatialFF=spatialFF1

                    sql=str(spatialFF+" = '"+uni+"'")

                    inCount = int(arcpy.GetCount_management(working_layer).getOutput(0))

                    if working_layer not in ffS_list:
                        inCnt =0

                    print(uni+'is uni and ' + str(inCnt)+" going in to "+working_layer)
                    # try:
                    arcpy.SelectLayerByAttribute_management(working_layer,"ADD_TO_SELECTION",sql)
                    # except:# ExecuteError:
                    #     print('Execute Error!!! 18@#')
                    #     print(working_layer)

                    outCnt = int(arcpy.GetCount_management(working_layer).getOutput(0))

                    print(str(outCnt)+" going out of "+working_layer)

                    if outCnt>inCnt:
                        #yy=5
                        #print("adding five")

                        if uni in mFFs:
                            mFFs.remove(uni)                   

                        if working_layer not in ffS_list:
                            ffS_list.append(working_layer)
                            print ffS_list

                    del sql
                    yy+=1
            yzy+=1

    for x in tmS_list:
        if x in ffS_list:
            ffS_list.append(ffS_list.pop(ffS_list.index(x)))
        else:
            ## test line
            print(str(x+' not in ffs list'))
    ## test line
    print ("length of ffS_list :"+str(len(ffS_list)))
    rem=["[","]","'"]
    rem1="[u]' "
    for x in ffS_list:
        field_names = [f.name for f in arcpy.ListFields(x)]
        if x == 'CUTBLOCK_lyr':
            macpy.AddFieldPlease(x,"CUTTING_PE","TEXT",cuttingPE2)
            macpy.AddFieldPlease(x,"FOREST_FIL","TEXT",spatialFF2)
        if cuttingPE1 not in field_names:
            arcpy.AddField_management(x,cuttingPE1,"TEXT")

        DoG=pd.read_excel(ScaleData)
        xz=0
        #print('THIS IS ONE ITERATION ON CUTTING PERMIT FUNTION')
        #print(str(x+' is the layer in question'))
        # print(str(ScaleData))
        #print(str('UNITM: '+uni+'; X:'+x+'; SPATIALTM: '+spatialTM1+'; CUTTINGE1: '+cuttingPE1+';'))
        for uni in UniTM:
            if xz!=-10:
                temPanda=pd.DataFrame()
                tempPanda=DoG.loc[DoG[tabularTM]==uni]
                #print(tempPanda.head(1))
                CPid=str(tempPanda['Cutting_Permit_ID'].unique())
                #print(CPid)
                # abc=0
                # for cba in CPid:
                #     CPid[abc]= cba.encode('ascii')
                #     abc=+1
                #print('ABOVE IS RAW CPid')
                # abc=len(CPid)
                # efg=0
                #while efg<abc:
                for char in rem1:
                    CPid=CPid.replace(char,"")
                    # efg=+1
                # print(CPid)
                # for rm in rem:
                #     try:
                #         CPid=CPid.strip(rm)
                #     except:
                #         print('no concern here')
                # print('BELOW IS ADJUSTED CPid')
                # print(CPid)
                if CPid is not None or CPid != ' ' or CPid !='':
                    with arcpy.da.UpdateCursor(x,[spatialTM1,cuttingPE1]) as cursor:
                        for row in cursor:
                            #print row
                            if row[0]==uni:
                                #print('ROW[0] equals UNI')
                                #print(row[0]+' '+uni+' are the variables')

                                if row[1] is None or row[1] == '<Null>' or row[1] == ' ' or row[1]=='' :
                                #     try:
                                        #print('row 1 was nun')
                                    row[1]=CPid
                                    cursor.updateRow(row)
                                        # print(str(x+' cuting permit id set to '+CPid))
                                #     except:
                                #         print('rterr')
                                # elif row[1]==CPid:
                                #     print('Row and CPid match no worries')
                                # else:
                                #     print('What The Heck')
                                #     print(row[1]+' ' +CPid)


    print(ffS_list)

    yy=0
    while yy<len(ffS_list):
        working_layer=ffS_list[yy]
        with arcpy.da.UpdateCursor(working_layer,spatialFF1) as cursor:
            for row in cursor:
                if row[0] is None or row[0] == '<Null>' or row[0] == ' ' or row[0]=='':
                    cursor.deleteRow()
        if working_layer=='RDS_lyr_b':
            print('roads buffer')
            working_fc_out=str(working_layer.strip('_lyr_b')+"_out")
            macpy.RoadBuffer(TempGDB,working_layer,working_fc_out, spatialTM1,spatialFF1,ffS_list)
            working_fc_out=str(working_layer+"_out")
            macpy.MakeMasterSpatial(TempGDB,working_layer,working_fc_out,yy,MasterSpatial,col5,spatialTM1,spatialFF1,cuttingPE1,ffS_list)

        if working_layer=='CUTBLOCK_lyr':
            print("cutblock maniupaltion")
            del working_fc_out
            working_fc_out=str(working_layer.strip('_lyr_b')+"_out")

            arcpy.CopyFeatures_management(working_layer,working_fc_out)
            arcpy.Delete_management(working_layer)
            macpy.MakeMasterSpatial(TempGDB,working_layer,working_fc_out,yy,MasterSpatial,col5,spatialTM1,spatialFF2,cuttingPE2,ffS_list)
            #yy+=1

        if working_layer!='RDS_lyr_b' and working_layer!='CUTBLOCK_lyr_b'and yy <len(ffS_list):
            working_layer=ffS_list[yy]
            print("double != and on "+str(working_layer))
            #del working_fc_out
            working_fc_out=str(working_layer.strip('_lyr_b')+"_out")
            arcpy.CopyFeatures_management(working_layer,working_fc_out)
            arcpy.Delete_management(working_layer)
            macpy.MakeMasterSpatial(TempGDB,working_layer,working_fc_out,yy,MasterSpatial,col5,spatialTM1,spatialFF1,cuttingPE1,ffS_list)

        yy+=1

    print(">>>>>>>>>>>>>>>>>>>")

def RSRV_del(TempGDB, lyr_list,xx, workingLYR, TSA,MasterSpatial,spatialFF,spatialTM,cuttingPE,col7,aoiSubUnits):
    print("Starting RSRV_del Function in vLib.")
    print("netit starting")
    macpy.NetIt(lyr_list,xx,MasterSpatial,spatialFF,spatialTM,cuttingPE,col7,aoiSubUnits)

MasterSpatial='MasterSpatial'
def BridgeTheGap(TempGDB, aoiSubUnits,MasterSpatial,MasterSpatial2,col5,col6,col7,col8,spatialTM1,spatialFF1,cuttingPE1,col2,col3,col4):
    print("in vLib Bridge")
    col5 ="TM_Gross_Area_HA"
    col6 ="TM_AOI_Gross_Area_HA"
    macpy.bigUnionA(TempGDB, aoiSubUnits,MasterSpatial2,col5,col6,spatialTM1,spatialFF1,cuttingPE1,col2,col3,col4)
    print('half way trhough vLib bridge')
    macpy.bigUnionB(TempGDB, aoiSubUnits,MasterSpatial,col7,col8,spatialTM1,spatialFF1,cuttingPE1,col2,col3,col4)
    print('finsihed vLib Bridge')



def TLR(MasterSpatial2,MasterSpatial5,spatialFF1,spatialTM1,col0,col1,col2,col3,col4,col5,col6,col7,col8,TempContainer,masterPD):
    macpy.TheLastRex(MasterSpatial2,MasterSpatial5,spatialFF1,spatialTM1,col0,col1,col2,col3,col4,col5,col6,col7,col8,TempContainer, masterPD)

def writeMasterDictionary(ax, TempContainer,ay,masterPD):

    TSA = r'NOT/REAL/PATH/FADM_TSA_D.shp'
    spatialTM="TIMBER_MAR"
    spatialFF="FOREST_FIL"
    cuttingPE="CUTTING_PE"
    ha_tm_list=[]
    Test=1
    if Test !=1:
        HARVAUTH = "WHSE_FOREST_TENURE.FTEN_HARVEST_AUTH_POLY_SVW"
        OPENINGS = "WHSE_FOREST_VEGETATION.RSLT_OPENING_SVW"
        CUTBLOCK = "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW"
        RDS = "WHSE_FOREST_TENURE.FTEN_ROAD_SEGMENT_LINES_SVW"
        RSRVS="WHSE_FOREST_VEGETATION.RSLT_FOREST_COVER_RESERVE_SVW"

    else:
        HARVAUTH = r"NOT/REAL/PATH/FTEN_HARVEST_AUTH_POLY_SVW.shp"
        OPENINGS = r"NOT/REAL/PATH/RSLT_OPENING_SVW.shp"
        CUTBLOCK = r"NOT/REAL/PATH/FTEN_CUT_BLOCK_POLY_SVW.shp"
        RDS = r"NOT/REAL/PATH/FTEN_ROAD_SEGMENT_LINES_SVW.shp"
        RSRVS=r"NOT/REAL/PATH/RSLT_FOREST_COVER_RESERVE_SVW.shp"

    inData_list= [TSA,RDS,OPENINGS,CUTBLOCK, HARVAUTH, RSRVS]
    MasterDictionary=pd.DataFrame()
    MasterDictionary2=pd.DataFrame()


    z=1
    xxx=1
    yyy=len(inData_list)-1
    print(str(yyy)+' is yyy')
    while xxx<yyy:
        working_layer=str(inData_list[xxx])
        inDATASET=working_layer
        fcLYR=str(working_layer+"_lyr")
        arcpy.MakeFeatureLayer_management(working_layer,fcLYR)
        if xxx==3:
            spatialFF="HARVEST__2"
            cuttingPE="HARVEST__1"
        else:
            spatialFF="FOREST_FIL"
            cuttingPE="CUTTING_PE"
            a=''
        b=''
        #c='None'
        temp_dict={}
        #arcpy.Dissolve
        result = arcpy.GetCount_management(inDATASET)
        out_pd=pd.DataFrame()
        print('{} has {} records'.format(inDATASET, result[0]))
        with arcpy.da.SearchCursor(inDATASET,[spatialFF,spatialTM]) as cursor:
            for row in cursor:
                field_value=str(cursor[0])
                field_val_temp = field_value.strip("(u'")
                field_value= field_val_temp.strip("'),")
                a=str(field_value)
                field_value=str(cursor[1])
                field_val_temp = field_value.strip("(u'")
                field_value= field_val_temp.strip("'),")
                b=str(field_value)
                out_d=[a,b]
                #print(out_d)
                out_d2={z:out_d}
                temp_dict.update(out_d2)
                #print(out_d2)

                #print(out_pd.head())

                #print(out_pd.head())
                #out_pd=out_pd.columns['FOREST_FIL','TIMBER_MAR','CUTTING_PE']


                del out_d
                z+=1
        print("Length of temp_dict: %d" % len (temp_dict))

        out_pd=pd.DataFrame.from_dict(temp_dict)
        total_rows = len(out_pd.axes[1])
        print("Length col before T: " + str(total_rows))

        out_pd=out_pd.T
        total_rows = len(out_pd.axes[0])
        print("Length row after T: " + str(total_rows))

        MasterDictionary= pd.concat([out_pd],ignore_index=True,axis=0)
        total_rows = len(MasterDictionary.axes[0])
        print("Length before drop: " + str(total_rows))
        MasterDictionary=MasterDictionary.drop_duplicates()
        total_rows = len(MasterDictionary.axes[0])
        print("Length after drop: " + str(total_rows))
        print(MasterDictionary.head())
        print(str("THAT WAS "+fcLYR+" Master Dictionary"))
        xxx+=1

    MasterDictionary= MasterDictionary.rename(columns={0: spatialFF, 1: spatialTM})
    print(MasterDictionary.head(25))
    total_rows = len(MasterDictionary.axes[0])
    print("total master dict : " + str(total_rows))

    ScaleData = r'NOT/REAL/PATH/ScaleData_Full.xlsx'
    dataOG = pd.read_excel(ScaleData)
    dataOG2 = [dataOG["FOREST_FIL"],dataOG["TIMBER_MAR"]]
    dataOG1=pd.concat(dataOG2,axis=1,keys=['FOREST_FIL','TIMBER_MAR'])
    print(dataOG1.head(5))
    xcldoc2='HAvnv.xlsx'
    MasterDictionary.to_excel(xcldoc2)

    missmark=dataOG1.merge(how='left', indicator=True).query('_merge == "left_only"').drop(['_merge'],axis=1)
    xcldoc3='MMvnv.xlsx'
    missmark.to_excel(xcldoc3)

    col0="FOREST_FIL"
    col1="TIMBER_MAR"
    col2="TM_Gross_Area_HA"
    #arcpy.MakeFeatureLayer_management(MS,'MS')
    ##col0_col=[]
    ##col1_col=[]
    ##col2_col=[]
    ##with arcpy.da.SearchCursor('MS', [col0,col1,col2]) as cursor:
    ##    for row in cursor:
    ##        col0_col.append(row[0])
    ##        col1_col.append(row[1])
    ##        col2_col.append(row[2])
    ##
    ##masterMS=pd.DataFrame(list(zip(col0_col,col1_col,col2_col)),columns=[col0,col1,col2])

    arcpy.env.workspace(r'NOT/REAL/PATH/TempGDB.gdb')
    arcpy.MakeFeatureLayer_management('MasterSpatial2','rsx')
    with arcpy.da.SearchCursor('MS', [col0,col1,col2]) as cursor:
        for row in cursor:
            col0_col.append(row[0])
            col1_col.append(row[1])
            col2_col.append(row[2])

    masterMD=pd.DataFrame(list(zip(col0_col,col1_col,col2_col)),columns=[col0,col1,col2])

    outReport=dataOG.merge(masterPD, on=[col0,col1], how='left', indicator=True).query('_merge == "both"').drop(['_merge'],axis=1)
    outReport['TM_Gross_Vol_per_HA']=outReport.apply(lambda row: 0 if row.Total_Volume==0 or row.TM_Gross_Area_HA ==0 else row.Total_Volume/row.TM_Gross_A, axis=1)
    outReport['TM_Gross_Val_per_HA']=outReport.apply(lambda row: 0 if row.Total_Value==0 or row.TM_Gross_Area_HA ==0 else row.Total_Value/row.TM_Gross_A, axis=1)

    xcldoc1='MSvnv.xlsx'
    outReport.to_excel(xcldoc1)
