#Code source https://geonet.esri.com/message/526142#526142

import arcpy  
import os  
  
# Set workspace  
myGDB = arcpy.GetParameterAsText(0)  
  
# Get domains that are assigned to a field  
domains_used = []  
for dirpath, dirnames, filenames in arcpy.da.Walk(myGDB, datatype=["FeatureClass", "Table"]):  
    for filename in filenames:  
        print "Checking {}".format(os.path.join(dirpath, filename))
        print arcpy.GetMessages()  
        try:  
            ## Check for normal field domains  
            for field in arcpy.ListFields(os.path.join(dirpath, filename)):  
                if field.domain:  
                    domains_used.append(field.domain)  
            ## Check for domains used in a subtype field  
            subtypes = arcpy.da.ListSubtypes(os.path.join(dirpath, filename))  
            for stcode, stdict in subtypes.iteritems():  
                if stdict["SubtypeField"] != u'':  
                    for field, fieldvals in stdict["FieldValues"].iteritems():  
                        if not fieldvals[1] is None:  
                            domains_used.append(fieldvals[1].name)  
        except Exception, err:  
            print "Error:", err  
  
# Get domains that exist in the geodatabase  
domains_existing = [dom.name for dom in arcpy.da.ListDomains(myGDB)]  
  
# Find existing domains that are not assigned to a field  
domains_unused = set(domains_existing) ^ set(domains_used)  
print "{} unused domains in {}".format(len(domains_unused), myGDB)  
for domain in domains_unused:  
    arcpy.DeleteDomain_management(myGDB, domain)  
    print "{} deleted".format(domain) 