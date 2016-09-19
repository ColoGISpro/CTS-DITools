import  os


print "updating Manifest.txt...."
CTS_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

print CTS_Root
#CTS_Root =r"C:\temp\maia\Latest\thefloof\CTS_Root"

manifestPath = os.path.join(CTS_Root,'Workspace','docs','Manifest.txt')

folderList  = [f for f in os.listdir(CTS_Root) if os.path.isdir(os.path.join(CTS_Root, f))]
fileList    = [f for f in os.listdir(CTS_Root) if os.path.isfile(os.path.join(CTS_Root, f))]

manifestContent = str("""Please do not move or edit this file.

why you ask?  ...well,  here's the deal:
This file contains a manifest of files and directories to be removed
when CTS-DITools get updated. Basically, tweaking with this file could result
in failure to clean up any files/folders that exist in the CTS_Root during update.
Especially they are reanmed or omitted in the new version.

tl;dr
below is a list of files that will get cleaned up during update

<DirectoriesToClean>{}<_DirectoriesToClean_>
<FilesToClean>{}<_FilesToClean_>
""").format(folderList,fileList)
print "manifestContent is as follows"
print manifestContent
print "over writing :"
print manifestPath


with open(manifestPath, 'w') as f:
    f.writelines(manifestContent)

print 'Success!'

