###################################
# Script:  TierIIPointPolyLocatorScript_ZipRevision.py
# Author:  Conrad Schaefer
# Date Created:  08/31/2017
# Purpose:  Gets latitude and longitude strings, creates a point object, selects by location the zip code tabulation area,
#           county, and LEPC where the point is located. Writes the names of these features to a text file.
# Inputs:  Latitude (String), Longitude (String)
# Outputs:  Text File (.txt)
# Modifications: Added Zip Code Tabulation Area
###################################
import sys

# Import the bare minimum to increase speed
from arcpy import env as env
from arcpy import GetParameterAsText, SetParameterAsText
from arcpy import AddMessage, AddWarning
from arcpy import da
from arcpy import Point, PointGeometry
from arcpy import SelectLayerByLocation_management
from arcpy import SpatialReference
from arcpy import GetCount_management

# Environment Settings
env.overwriteOutput = True

# Get Inputs
strLatitude = GetParameterAsText(0)
strLongitude = GetParameterAsText(1)
flZCTA = GetParameterAsText(2)
flLEPC = GetParameterAsText(3)
flCounty = GetParameterAsText(4)
strFilePath = GetParameterAsText(5)

# Convert values from text to float
floLatitude = float(strLatitude)
floLongitude = float(strLongitude)

# Make a Point Geometry object.
try:
    ptPointOfInterest = Point(X=floLongitude,Y=floLatitude,Z=None,M=None,ID=0)
    spatial_ref = SpatialReference(4269)
    ptGeometry = PointGeometry(ptPointOfInterest,spatial_ref)
except:
    strErrorMsg = "Error creating Point or PointGeometry objects."
    AddWarning(strErrorMsg)
    SetParameterAsText(6, strErrorMsg)
    sys.exit()

# Open Output File for use
try:
    fhand = open(strFilePath, 'w')
except:
    strErrorMsg = "File did not open"
    AddWarning(strErrorMsg)
    SetParameterAsText(6, strErrorMsg)
    sys.exit()

# Make a dictionary of layer name and layer variable for iteration purposes
dictLayers = {"zip":flZCTA,"lepc":flLEPC,"county":flCounty}
dictNames = {}

# Iterate through layers in dictionary and run SelectLayerByLocation
for key in dictLayers:
    lyrLayer = dictLayers.get(key)
    try:
        SelectLayerByLocation_management(in_layer=lyrLayer, overlap_type="CONTAINS", select_features=ptGeometry,search_distance="", selection_type="NEW_SELECTION",invert_spatial_relationship="NOT_INVERT")
    except:
        strErrorMsg = "Error with SelectLayerByLocation_management."
        AddWarning(strErrorMsg)
        SetParameterAsText(6, strErrorMsg)
        sys.exit()
    intSelectionCount = 0
    resultSelectionCount = GetCount_management(lyrLayer) # Result Object, not an actual number
    intSelectionCount = int(GetCount_management(lyrLayer).getOutput(0)) # Cast to int because returns as unicode

    '''' During development, a point was used that fell on more than one polygon. The process
        returned two counties selected and two lepc's selected. But, they were not in the same order so they weren't written to the
        file identically. Example: Burleson and Robertson (counties) and Burleson LEPC and Roberston LEPC. The file had Burleson for county, 
        and Robertson LEPC for lepc. So, the record count check was kept and an error message added.'''
    # Check for selection of one feature only. Exception: Zip Codes do not have full coverage of the state. There are gaps where no selection will occur.
    if (key != "zip" and intSelectionCount == 0):
        strErrorMsg = "No features selected in  " + key + "."
        AddWarning(strErrorMsg)
        SetParameterAsText(6, strErrorMsg)
        sys.exit()
    elif (intSelectionCount > 1):
        AddMessage("Count for " + key + " is " + str(intSelectionCount))
        strErrorMsg = "More than one feature selected in " + key + "."
        AddWarning(strErrorMsg)
        SetParameterAsText(6, strErrorMsg)
        sys.exit()
    else:
        pass

    # Grab value of interest from selected feature in each layer and add to the dictionary of name values.
    try:
        if key == "lepc" or key == "county":
            with da.SearchCursor(lyrLayer, "NAME") as cursorB:
                for row in cursorB:
                    dictNames[key] = row[0]
                    # AddWarning(row[0])
        elif key == "zip":
            with da.SearchCursor(lyrLayer, "ZCTA5CE10") as cursorB:
                for row in cursorB:
                    dictNames[key] = row[0]
                    # AddWarning(row[0])
        else:
            strErrorMsg = "Error searching " + key + " for identifying value."
            SetParameterAsText(6, strErrorMsg)
            sys.exit()
    except:
        strErrorMsg = "Error executing cursor."
        AddWarning(strErrorMsg)
        SetParameterAsText(6, strErrorMsg)
        sys.exit()

# Iterate through the names dictionary, write the layer name (key) and the associated Name (value) to the output file
for key in dictNames:
    try:
        fhand.write(key + "=" + dictNames.get(key) + "\n")
    except:
        strErrorMsg = "Error writing to file."
        AddWarning(strErrorMsg)
        SetParameterAsText(6, strErrorMsg)
        sys.exit()
try:
    fhand.close()
except:
    strErrorMsg = "Error closing file."
    AddWarning(strErrorMsg)
    SetParameterAsText(6, strErrorMsg)