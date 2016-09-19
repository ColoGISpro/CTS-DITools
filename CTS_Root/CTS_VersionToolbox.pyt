#-------------------------------------------------------------------------------
# version: 1.1.3.master
#
# Changes since last version
# Created three new 'print' functions that provide user feedback on to progress
# via ArcGIS's  dialog box and geoprocessing history as the tool progress
#   -printException
#   -printFunctionInfoStart
#   -printFunctionInfoEnd
#
# functionsUpdated = [
#   checkInternetConnection,
#   checkInternetConnection,
#   parseVarsFromURL,
#   checkVersion,
#   promptUserForNextStep,
#   backupCTSData,
#   downloadExtractCleanUpdate] (renamed -->downloadCleanInstall)
#
# for code in functionsUpdated:
#   -integrated new print functions
#   -replaced 'print' statements w/ arcpy.AddMessage(), AddWarning(), AddError()
#   -improved error handling
#
# Overhauled downloadExtractCleanUpdate function
#   - renamed downloadCleanInstall
#   - updated workflow of how assests are cleaned during update to ensure user...
#       data will never be unintentionally deleted. (see manfest)
# implemented updateMissionControl!!!!!!
#
#-------------------------------------------------------------------------------
import arcpy, os, time

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [UpdateDITools]

class UpdateDITools(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update CTS-DITools"
        self.description = "Update CTS-DITools"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # First parameter
        param0 = arcpy.Parameter(
        displayName="CTS_Root Folder",
        name="CTS_Root",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")
        # Set default to path where this .pyt file is currently running
        #   This .pty should always be the 'CTS_Root' folder since all other
        param0.value = os.path.dirname(os.path.realpath(__file__))

        # Second parameter
        param1 = arcpy.Parameter(
        displayName="Local Version",
        name="LocalVersion",
        datatype="GPString",
        parameterType="Required",
        direction="Input",
        enabled=False)
        # Set expected relitive path of LocalVersion.txt (CTS_Root\Workspace...)
        LocalVersiontxt =   (os.path.join(param0.valueAsText,
                            r"Workspace\docs\LocalVersion.txt")
                            )
        # If LocalVersiontxt exist set default based on file contents
        if os.path.exists(LocalVersiontxt):
            with open(LocalVersiontxt) as f:
                param1.value = f.read()
        # If LocalVersiontxt does not exist set default to 0.0.0.master
        else:
            param1.value =  "0.0.0.master"

        # Third parameter
        param2 = arcpy.Parameter(
        displayName=    ("Build (Version of tools to be installed "
                        "based on Contributors's Publishing Method)"
                        ),
        name="Build",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        # Set default based on current LocalVersion parameter
        build = str(param1.valueAsText)
        build = build.split('.')[3]
        # Gives user the abilty to select build during inital install
        if build == 'master':
            param2.filter.type = "ValueList"
            param2.filter.list = ['admin','direct', 'active','master']
            param2.value = 'master'
        # Removes selection from user on update since changing is not supported
        # Future help docs will prompt user download new master to change builds
        else:
            param2.enabled = False
            param2.parameterType = "Optional"
            param2.direction="Output"
            param2.displayName =    ('Build can only set on inital '
                                    'setup when build = master')
            param2.value = build

        # Fourth parameter
        param3 = arcpy.Parameter(
        displayName="Backup Target Folder",
        name="BackupTargetFolder",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")
        # Set default value to one directory above CTS_Root folder
        param3.value = os.path.dirname(param0.valueAsText)
        # See comment in updateParameters fuction....

        # Fifth parameter
        param4 = arcpy.Parameter(
        displayName="Backup FileName (.zip)",
        name="BackupZipFileName",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        #Set default: CTS_Root-bu-v[x.x.x.build]-archived-[YYYY-MM-DD-HHMM].zip
        param4.value =  (os.path.basename(param0.valueAsText) +'-bu-'+
                        'v'+ param1.valueAsText + '-archived-'+
                        str(time.strftime('%Y-%m-%d-%H%M')) + '.zip'
                         )

        # Sixth parameter
        param5 = arcpy.Parameter(
        displayName="FullZipFilePath",
        name="FullZipFilePath",
        datatype="GPString",
        parameterType="Required",
        direction="Output",
        enabled=False)
        # Set default value by joining: [BackupTargetFolder]/ [BackupZipFileName]
        param5.value =  os.path.join(param3.valueAsText, param4.valueAsText)

        # Seventh parameter
        param6 = arcpy.Parameter(
        displayName="URL to CTS_DIT_LastestVersion.txt",
        name="LatestVersionTxtURL",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        # Sets default value to URL of CTS_DIT_LastestVersion.txt published
        # on github.com which contains two variables for each supported
        # build of the CTS-DITools:
        #       -LastetVersion (formatted as: MAJOR.MINOR.PATCH.BUILD)
        #       -URL to clone latest git repository as .zip file
        # These variables are nested inside expected tags that allow this tool
        # to parse the latest version & then download source code for updates.
        param6.value = (r'https://raw.githubusercontent.com/ColoGISpro/'
                        'CTS-DITools/VCS-Vars-Only/CTS_DIT_LastestVersion.txt'
                        )
        # List all parameter
        params = [param0, param1, param2, param3, param4, param5, param6]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        parameters[5].value=    (os.path.join(parameters[3].valueAsText,
                                parameters[4].valueAsText)
                                )
        #Future code here would prohibt from setting the BackupTargetFolder
            # paramerter (param3) to anywhere inside CTS_Root.
            # This would helpful given the purpose of backing up is to
            # recover user data unintentionally deleted during update

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        arcpy.AddMessage(str("{:<15}{: ^70}{: >15}\n"
            .format('',"keep calm and carry on",'')))

        arcpy.AddMessage("Importing python libraries:{}".format('\n')+
            "ast, ctypes , glob, inspect, linecache, {}".format('\n')+
            "shutil, socket, sys, textwrap, urllib, urllib2, zipfile")

        import ast, ctypes, glob, inspect, linecache, shutil, socket, sys
        import textwrap, urllib, urllib2, zipfile

        def printException(severity=2):
            """Prints exception info to ArcGIS's dialog box and history -
            identifies filename, linenumber, line itself and
            exception description and raises a message/warning/error/ based on
            severtiy parameter  1/2/3 respectively."""

            try:
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, f.f_globals)
                exceptionMessage =  ('EXCEPTION IN ({}, LINE {} "{}"): {}'
                                    .format(filename, lineno, line.strip(), exc_obj)
                                    )
            except:
                 try:
                    currentFrame = inspect.currentframe()
                    line = currentFrame.f_back.f_lineno
                 finally:
                        del currentFrame
                 exceptionMessage ='EXCEPTION NOT found at LINE {}'.format(line)
                 arcpy.AddMessage(exceptionMessage)
            if severity == 1:
                    arcpy.AddMessage(exceptionMessage)
            elif severity == 2:
                    arcpy.AddWarning(exceptionMessage)
            else:
                    arcpy.AddError(exceptionMessage)
            return exceptionMessage

        def printFunctionInfoStart(linesBelow_defCall=3, printVars=False):
            """Prints local function info to ArcGIS's dialog box and history.
            Genearlly incuded at the top of each function to provide user
            feedback as the tool progress."""
            try:
                currentFrame = inspect.currentframe()

                #localFuctInspectObject0 =inspect.getframeinfo(currentFrame)
                localFuctInspectObject1 =inspect.getframeinfo(currentFrame.f_back)
                localFuctInspectObject2 =inspect.getframeinfo(currentFrame.f_back.f_back)

                #localFunctionName0 = localFuctInspectObject0[2]
                localFunctionName1 = localFuctInspectObject1[2]
                localFunctionName2 = localFuctInspectObject2[2]

                #line0 = currentFrame.f_lineno
                line1 = currentFrame.f_back.f_lineno
                line2 = currentFrame.f_back.f_back.f_lineno

                # Printing Local variables to be implemented in the future
                #localVariables0 = currentFrame.f_locals
                #localVariables1 = currentFrame.f_back.f_locals
                #localVariables2 = currentFrame.f_back.f_back.f_locals
                StartMessage = str(
                    #"{:<15}{: ^70}{: >15}\n".format
                    #('',"keep calm and carry on",'')+
                    "{:*^100}\n".format('')+
                    "{: <5}{:~^90}{: >5}\n".format('','STARTING','')+
                    "{: <10}{:-^80}{: >10}\n".format('',localFunctionName1,'')+
                    #"{: <15}{:-^70}{: >15}\n".format('','','')+
                    "{:<49}{:^1}{:^49}\n".format
                        ("Execute function"
                        ,"-",localFunctionName1)+
                    "{:<49}{:^1}{:^49}\n".format(
                        "which is defined at Line No."
                            ,"-",line1- linesBelow_defCall)+
                    "{:<49}{:^1}{:^49}\n".format(
                        "and is currently being called at Line No.","-",line2)+
                    "{:<49}{:^1}{:^49}\n".format
                        ("within a funtion named","-",localFunctionName2)+
                "{:<49}{:^1}{:^49}\n".format
                    ("A list of variables may apeare below "
                    ,"-","Vars not printed by default")+
                #"{: <15}{:-^70}{: >15}\n".format('','','')+
                #"{: <10}{:-^80}{: >10}\n".format('',localFunctionName1,'')+
                "{: <10}{:-^80}{: >10}\n".format('','start','')
                )
                arcpy.AddMessage(StartMessage)
            finally:
                del currentFrame

        def printFunctionInfoEnd(severity=1, success=True,
            message='no info',linesAbove_returnCall=1):
            """Prints local function info to ArcGIS's dialog box and history.
            Generally incuded at the bottom of each function to provide user
            feedback as the tool progress. Raises a message|warning|error
            based on severtiy parameter value: 1|2|3 respectively."""
            if success:
                successStatment = 'Successful'
            else:
                successStatment = 'Failed'
            messageline1  = message[0:40]
            messageline2  = textwrap.fill(message[41:],99)
            try:
                currentFrame = inspect.currentframe()

                #localFuctInspectObject0 =inspect.getframeinfo(currentFrame)
                localFuctInspectObject1 =inspect.getframeinfo(currentFrame.f_back)
                localFuctInspectObject2 =inspect.getframeinfo(currentFrame.f_back.f_back)

                #localFunctionName0 = localFuctInspectObject0[2]
                localFunctionName1 = localFuctInspectObject1[2]
                localFunctionName2 = localFuctInspectObject2[2]

                line0 = currentFrame.f_lineno
                line1 = currentFrame.f_back.f_lineno
                line2 = currentFrame.f_back.f_back.f_lineno

                # Printing Local variables to be implemented in the future
                #localVariables0 = currentFrame.f_locals
                #localVariables1 = currentFrame.f_back.f_locals
                #localVariables2 = currentFrame.f_back.f_back.f_locals
                endMessage = str(
                    "{: <10}{:-^80}{: >10}\n".format('','end','')+
                    "{: <10}{:-^80}{: >10}\n".format('',localFunctionName1,'')+
                    #"{: <15}{:-^70}{: >15}\n".format('','','')+
                    "{:<49}{:^1}{:^49}\n".format
                        ("Ending execution of a function named"
                        ,"-",localFunctionName1)+
                    "{:<49}{:^1}{:^49}\n".format(
                        "at Line No"
                            ,"-",line1+ linesAbove_returnCall)+
                    "{:<49}{:^1}{:^49}\n".format(
                        "The results are as follows","-",successStatment)+
                    "{:<49}{:^1}{:^49}\n".format(
                        "Functions notes:","-",messageline1)+
                    "{:^99}\n".format(messageline2)+
                #"{: <15}{:-^70}{: >15}\n".format('','','')+
                #"{: <10}{:-^80}{: >10}\n".format('',localFunctionName1,'')+
                "{: <5}{:~^90}{: >5}\n".format('','ENDING','')+
                "{:*^100}\n".format('')
                )
                if severity == 3:
                    arcpy.AddError(endMessage)
                elif severity == 2:
                    arcpy.AddWarning(endMessage)
                else:
                    arcpy.AddMessage(endMessage)
            finally:
                del currentFrame


        def checkInternetConnection():
            """Check if user's machine is connected to internet"""
            printFunctionInfoStart(2)
            arcpy.AddMessage("Got internet?")
            try:
                socket.gethostbyname('www.google.com')
                arcpy.AddMessage("roger that")
                printFunctionInfoEnd(1,True,"connected to interwebs",1)
                return True
            except:
                try:
                    socket.gethostbyname('www.nytimes.com')
                    arcpy.AddMessage("roger that")
                    printFunctionInfoEnd(1,True,"connected to interwebs",1)
                    return True
                except:
                    exceptMessage = printException(2)
                    Title = 'Internet Connection Required!'
                    Message =('An internet connection is required to get '
                    'the lastest version. An error was encountered while '
                    'atempting to ping\n\nwww.google.com/nwww.nytimes.com\n\n'
                    'Please check your internet conection and try again later\n'
                    'The update will be aborted.')
                    self = ctypes.windll.user32.MessageBoxA
                    self(0,Message,Title,0x00200000L|0x00000000L|0x00000040L)

                    printFunctionInfoEnd(3,False,exceptmessage,1)
                    return False


        def parseVarsFromURL (LastestVersiontxt_URL, BUILD):
            """Parses the LatestVersion and LatestDownloadURL of a given build
            from a text document published on the web returning a list of str
            [LatestVersion, LatestDownloadURL]"""
            printFunctionInfoStart(4,False)

            # Get text CTS_DIT_LastestVersion.txt published on github.com
            arcpy.AddMessage("Get text CTS_DIT_LastestVersion.txt published on github.com")
            try:
                url = urllib2.urlopen(LastestVersiontxt_URL)
                htmltext = url.read()
                url.close()
                arcpy.AddMessage("Successfully copied raw text of CTS_DIT_LastestVersion.txt")
            except:
                exceptMsg = "Error reteriving LastestVersion.txt from url"
                arcpy.AddWarning(exceptMsg)

            ####################################################################
            # The CTS_DIT_LastestVersion.txt file contains a pair of varables
            # for each supported build of the CTS-DITools:
            #   -LastetVersion      (formatted as: MAJOR.MINOR.PATCH.BUILD)
            #   -LatestDownloadURL  (url to clone latest git repo as .zip)
            #
            # These variables are nested inside tags formatted as:
            #   <[BUILD]Version>value<_[BUILD]Version_>
            #   <[BUILD]URL>value<_[BUILD]URL_>
            #
            # An example for a 'master' BUILD with Version = 0.1.2:
            #
            #   <masterVersion>0.1.2.master<_masterVersion_>
            #   <masterURL>https://github.com/../bar.zip<_masterURL_>
            #
            # One more example of a 'direct' BUILD with Version = 3.4.5:
            #   <directVersion>3.4.5.direct<_directVersion_>
            #   <directURL>https://github.com/../foo.zip<_directURL_>
            ####################################################################
            try:
                arcpy.AddMessage("Atemping to parse out LastetVersion & LatestDownloadURL from text")
            # Create the StartIndex and EndIndex tags for the LastetVersion var
                StartIndex =  '<' + BUILD + 'Version>'
                EndIndex = '<_' + BUILD + 'Version_>'

                # Find starting position of the StartIndex as int
                StartIndexPosition = htmltext.find(StartIndex)

                # Find the Start position of LastetVersion value as int
                StartIndexPosition =  len(StartIndex) + StartIndexPosition

                # Find the Ending position of LastetVersion value as int
                EndIndexPosition = htmltext.find(EndIndex)

                #Parses out LatestVersion given known Starting and Ending postions
                LatestVersion = htmltext[StartIndexPosition:EndIndexPosition]

                #Parses out LatestDownloadURL varable
                StartIndex =  '<' + BUILD + 'URL>'
                EndIndex = '<_' + BUILD + 'URL_>'
                StartIndexPosition = htmltext.find(StartIndex)
                StartIndexPosition =  len(StartIndex) + StartIndexPosition
                EndIndexPosition = htmltext.find(EndIndex)
                LatestDownloadURL = htmltext[StartIndexPosition:EndIndexPosition]

                printFunctionInfoEnd(1,True, "lastest v{}".format(LatestVersion),1)
                return [LatestVersion, LatestDownloadURL]

            except:
                exceptMsg = printException(2)
                printFunctionInfoEnd(2,False,exceptMsg,1)
                return [LatestVersion, LatestDownloadURL]


        def checkVersion(LocalVersion, LatestVersion):
            """Compare LocalVersion to LatestVersion and returns difference
            with the greatest precedence given: MAJOR>MINOR>PATCH>BUILD"""
            printFunctionInfoStart(2,False)

            arcpy.AddMessage("Comparing:\nLocalVersion: {}\n"+"LocalVersion: {}"
            .format(LocalVersion,LatestVersion))

            # possible string values returned by CompareVersions
            cu = 'CURRENT'
            ma = 'MAJOR'
            mi = 'MINOR'
            pa = 'PATCH'
            bu = 'BUILD'
            e1 = 'ERROR: LocalVersion not formated as Int.Int.Int.str'
            e2 = 'ERROR: LatestVersion not formated as Int.Int.Int.str'
            e3 = 'ERROR: LocalVersion is newer than LatestVersion?'

            if LocalVersion == LatestVersion:
                printFunctionInfoEnd(1,True,cu,1)
                return cu
            else:
                Local_list = LocalVersion.split('.')
                try:
                    Local_major = int( Local_list[0])
                    Local_minor = int( Local_list[1])
                    Local_patch = int( Local_list[2])
                    Local_build = str(Local_list[3])
                except:
                    printFunctionInfoEnd(2,True,e1,1)
                    return e1

                Latest_list = LatestVersion.split('.')
                try:
                    Latest_major = int( Latest_list[0])
                    Latest_minor = int( Latest_list[1])
                    Latest_patch = int( Latest_list[2])
                    Latest_build = str(Latest_list[3])
                except:
                   printFunctionInfoEnd(1,True,e2,1)
                   return e2

                if Local_major < Latest_major:
                    printFunctionInfoEnd(1,True,ma,1)
                    return ma
                elif Local_minor < Latest_minor:
                    printFunctionInfoEnd(1,True,mi,1)
                    return mi
                elif Local_patch < Latest_patch:
                    printFunctionInfoEnd(1,True,pa,1)
                    return pa
                elif Local_build != Latest_build:
                     printFunctionInfoEnd(1,True,bu,1)
                     return bu
                else:
                    printFunctionInfoEnd(2,True,e3,1)
                    return e3

        def promptUserForNextStep(CheckVersionResult, LocalVer, LatestVer):
            """Conveys results of version check and asks user to update now"""
            printFunctionInfoStart(2,False)

            Result = CheckVersionResult[0:5]

            if  Result == 'CURRE':
                arcpy.AddMessage("if == CURRE code ran")
                Title = 'Your toolbox is up to date!'
                Message = str('The local CTS_Toolbox is up to date: \n\n' +
                    'Local   v' + LocalVer  + '\n' +
                    'Latest  v' + LatestVer + '\n\n' +
                    'No update required.')
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title,
                    0x00200000L|0x00000000L|0x00000040L)
                printFunctionInfoEnd()
                return False


            elif Result == 'MAJOR':
                arcpy.AddMessage("elif == MAJOR code ran")
                Title = 'Major new release available [MAJOR.minor.patch.build]'
                Message = join('The local CTS_Toolbox.tbx is out of date:\n\n',
                    'Local   v' + LocalVer  + '\n' ,
                    'Latest  v' + LatestVer + '\n\n')
                if LocalVer.split('.')[3] != 'active':
                    Message = Message + str( 'A major release indicates there has '+
                        'been significant changes to CTS schema. It is highly '+
                        'recommended to update before submitting '+
                        'a CTS_Published.gdb for publication.\n\n')
                Message = Message + 'Would you like to update now?'
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title,
                    0x00200000L|0x00000004L|0x00000010L)
                if response == 6:
                    printFunctionInfoEnd()
                    return True
                else:
                    printFunctionInfoEnd(1,True,'user elected not to update',1)
                    return False

            elif Result == 'MINOR':
                arcpy.AddMessage("elif == MINOR code ran")
                Title = 'Minor new release available [major.MINOR.patch.build]'
                Message = str('The local CTS_Toolbox.tbx is out of date:\n\n' +
                    'Local   v' + LocalVer  + '\n' +
                    'Latest  v' + LatestVer + '\n\n' +
                    'A minor release adds functionality to the CTS-DITools in a ' +
                    'backwards-compatible manner with current CTS schema.\n\n' +
                    'Would you like to update now?')
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title, 0x00200000L|0x00000004L|0x00000010L)
                if response == 6:
                    printFunctionInfoEnd()
                    return True
                else:
                    printFunctionInfoEnd(1,True,'user elected not to update',1)
                    return False

            elif Result == 'PATCH':
                arcpy.AddMessage("elif == PATCH code ran")
                Title = 'A new Patch is available [major.minor.PATCH.build]'
                Message = str('The local TS_Toolbox.tbx is out of date:\n\n' +
                    'Local   v' + LocalVer  + '\n' +
                    'Latest  v' + LatestVer + '\n\n' +
                    'A patch provides backwards-compatible bug fixes and ' +
                    'functionality to the CTS-DITools./n/n' +
                    'Would you like to update now?')
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title, 0x00200000L|0x00000004L|0x00000040L)
                if response == 6:
                    printFunctionInfoEnd()
                    return True
                else:
                    printFunctionInfoEnd(1,True,'user elected not to update',1)
                    return False

            #  THIS SECTION OF CODE NEEDS TO BE REVIEWED AND UPDATED!!!!!!!!!!!
            #  this section is depended on figuring out how various builds
            #  will be installed and distributed  to contributors
            #  ------------------START------------------------------------------

            elif Result == 'BUILD':
                arcpy.AddMessage("elif == BUILD code ran")
                Title = 'The Build differs [major.minor.patch.BUILD]'
                Message = str('The local CTS_Toolbox.tbx has a different build:\n\n'+
                    'Local   v' + LocalVer  + '\n' +
                    'Latest  v' + LatestVer + '\n\n' +
                'No update required.')
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title,
                    0x00200000L|0x00000000L|0x00000040L)
                printFunctionInfoEnd(2,True, "see comment ~553",1)
                return False
            #  ------------------START------------------------------------------

            elif Result == 'ERROR':
                arcpy.AddMessage("elif == ERROR code ran")
                # all three known error possibilties are handled here
                Title = 'whoops something went wrong'
                Message =str('Well this is weird...\n' +
                    'The error noted below was returned while comparing:\n\n'+
                    'Local   v' + LocalVer  + '\n' +
                    'Latest  v' + LatestVer + '\n\n' +
                    CheckVersionResult + '\n\n' +
                    "Would you like to open the CTS-DITools's issues page on github?")
                response = ctypes.windll.user32.MessageBoxA(
                    0, Message, Title,
                    0x00200000L|0x00000004L|0x00000040L)
                if response == 6:
                    import webbrowser
                    webbrowser.open_new_tab(
                        'https://github.com/ColoGISpro/CTS-DITools/issues')
                printFunctionInfoEnd(2,True, checkVersionResult,1)
                return False


                ##------- Message Box Return values  ------------------
                ##1  The OK button was selected.
                ##2  The Cancel button was selected.
                ##3  The Abort button was selected.
                ##4  The Retry button was selected.
                ##5  The Ignore button was selected.
                ##6  The Yes button was selected.
                ##7  The No button was selected.
                ##10 The Try Again button was selected.
                ##11 The Continue button was selected.



        def backupCTSData(CTS_RootFolderPath, NewZipFilePath):
            """Creates an archive of directory in .zip format"""
            printFunctionInfoStart(2,False)
            arcpy.AddMessage("be patient... this could take a hot second...")
            arcpy.AddMessage(str("""Why does Esri software says
            'Not Responding' in the menu when it's acually fine?"""))
            try:
                shutil.make_archive(
                    base_name=os.path.splitext(NewZipFilePath)[0],
                    format='zip',
                    root_dir=os.path.dirname(CTS_RootFolderPath),
                    base_dir=os.path.basename(CTS_RootFolderPath),
                    verbose=0, dry_run=0, owner=None, group=None, logger=None)

                arcpy.AddMessage("Successfully backed up: = {}".format(CTS_RootFolderPath))
                arcpy.AddMessage("As a zip file here = {}".format(NewZipFilePath))
                printFunctionInfoEnd()
                return True
            except:
                arcpy.AddMessage("Okay maybe it was right this time...crow for dinner")
                arcpy.AddWarning("Error backing up: = {}".format(CTS_RootFolderPath))
                arcpy.AddWarning("As a zip file here = {}".format(NewZipFilePath))
                exceptMesg = printException(2)
                printFunctionInfoEnd(3,False,exceptMesg,1)
                return False


        def downloadCleanInstall (ZipURL, RootFolder):
            """Downloads and installs CTS-DITools -
                1) create timestamped temp directory
                2) download repo as timestamped.zip to temp
                3) extract zip in temp
                4) clean up local CTS-DITools assets
                5) copies new assets from temp to CTS_Root
                6) deletes timestamped temp directory"""
            printFunctionInfoStart(8,False)

            #Create local vars
            arcpy.AddMessage('Create local variables...')
            TimeAsString = time.strftime('%Y_%m%d_%H%M')
            arcpy.AddMessage("TimeAsString = {}".format(TimeAsString))
            HomeFolder = os.path.dirname(RootFolder)
            arcpy.AddMessage("HomeFolder = {}".format(HomeFolder))
            WorkspaceFolder = os.path.join(RootFolder, 'Workspace')
            arcpy.AddMessage("WorkspaceFolder = {}".format(WorkspaceFolder))

            # 1) create timestamped temp directory
            arcpy.AddMessage('Step 1of6: create timestamped temp directory')
            try:
                TempWorkingPath = os.path.join(HomeFolder,
                    str('tmp_' +TimeAsString))
                arcpy.AddMessage("Creating...: TempWorkingPath = {}".format(
                    TempWorkingPath))
                os.mkdir(TempWorkingPath)

            except:
                exceptMesg = printException(2)
                try:
                    os.remove(TempWorkingPath)
                    arcpy.AddMessage("Deleted old: = {}".format(
                        TempWorkingPath))
                    os.mkdir(TempWorkingPath)
                    arcpy.AddMessage("Created new:  = {}".format(
                        TempWorkingPath))
                except:
                    printException(3)
                    printFunctionInfoEnd(3,False,exceptMesg,1)
                    return False

            # 2) download repo as timestamped.zip to temp
            arcpy.AddMessage(
                'Step 2of6: download repo as timestamped.zip into temp')

            NewZipFileName = 'CTS-Tools_DWNLD_' + TimeAsString  +'.zip'
            arcpy.AddMessage("NewZipFileName: = {}".format(NewZipFileName))

            NewZipPath = os.path.join(TempWorkingPath, NewZipFileName)

            arcpy.AddMessage("Atempting to download = {}".format(ZipURL))
            arcpy.AddMessage("to.........NewZipPath = {}".format(NewZipPath))

            try:
                newRepo = urllib.urlretrieve(ZipURL, NewZipPath)
                arcpy.AddMessage("downloaded zip from: {}".format(ZipURL))
                #newRepo.urlcleanup()  # throws exception? do we need to cleanup urllib object? perhaps using 'with' statement???
            except:
                arcpy.AddMessage("error downloading zip from {}".format(ZipURL))
                #newRepo.urlcleanup()   # throws exception? do we need to cleanup urllib object? perhaps using 'with' statement???
                ExceptMesg = printException(2)
                printFunctionInfoEnd(3,False,ExceptMesg,1)
                return False

            # 3) extract zip in temp
            arcpy.AddMessage('Step 3of6: extract zip in temp')
            try:
                z = zipfile.ZipFile(NewZipPath)
                z.extractall(TempWorkingPath)
                z.close()
                arcpy.AddMessage("Extracted zip to:= {}".format(TempWorkingPath))
            except:
                arcpy.AddMessage("ERROR Extracting zip to: = {}".format(TempWorkingPath))
                ExceptMesg = printException(2)
                printFunctionInfoEnd(3,False,ExceptMesg,1)
                return False

            #find the CTS_Root folder that was just extracted in the temp folder
            arcpy.AddMessage(
                "finding new 'CTS_Root' dir that was just extracted in {}"
                    .format(TempWorkingPath))

            NewRootFolder = ''
            for root, dirs, files in os.walk(TempWorkingPath):
                CurrentTempDirName = os.path.basename(root)
                if CurrentTempDirName == 'CTS_Root':
                    NewRootFolder = root
                    arcpy.AddMessage("Found NewRootFolder: = {}".format(NewRootFolder))
            if NewRootFolder == '':
                print 'ERROR: the extrated folder does not seem to have a CTS_Root folder????'
                arcpy.AddMessage("ERROR: the extrated folder does not seem to have a CTS_Root folder within: =".format(TempWorkingPath))

            # 4) clean up local CTS-DITools assets
            arcpy.AddMessage('Step 4of6: clean up local CTS-DITools assets')

            arcpy.AddMessage('Attempting to get Manifest of assets to clean up')
            try:
                manifestPath = os.path.join(RootFolder,'Workspace','docs','Manifest.txt')
                if os.path.exists(manifestPath):
                    arcpy.AddMessage("Reading Content of {}".format(manifestPath))

                    with open(manifestPath) as f:
                        manifestContent = f.read()
                        #Parses out Directory list
                        dirStartIndex = manifestContent.find('<DirectoriesToClean>') + 20
                        dirEndIndex   = manifestContent.find('<_DirectoriesToClean_>')
                        dirAsStr = manifestContent[dirStartIndex:dirEndIndex]
                        dirList = ast.literal_eval(dirAsStr)
                        arcpy.AddMessage("Old folders to remove: {}".format(dirList))

                        #Parses out File list
                        fileStartIndex = manifestContent.find('<FilesToClean>') + 14
                        fileEndIndex   = manifestContent.find('<_FilesToClean_>')
                        fileAsStr = manifestContent[fileStartIndex:fileEndIndex]
                        fileList = ast.literal_eval(fileAsStr)

                    arcpy.AddMessage("Old files to remove: {}".format(fileList))
                    arcpy.AddMessage("Atempting to clean (delete) old files...")
                    cleanUpErrorFlag = False
                    for dirs in dirList:
                        try:
                            path = os.path.join(RootFolder,dirs)
                            arcpy.AddMessage('Atempting to clean: {}'.format(path))
                            shutil.rmtree(path)
                            arcpy.AddMessage('Obblittteration of: {}'.format(path))
                        except:
                            printException(2)
                            cleanUpErrorFlag = True

                    for files in fileList:
                        try:
                            path = os.path.join(RootFolder,files)
                            arcpy.AddMessage('Atempting to clean: {}'.format(path))
                            os.remove(path)
                            arcpy.AddMessage('Obblittteration of: {}'.format(path))
                        except:
                            printException(2)
                            cleanUpErrorFlag = True
                    if(cleanUpErrorFlag):
                        arcpy.AddWarning(str("A minor error occurred during clean up ...\n" +
                                    "old assets files should still be overwritten"))
                    else:
                        arcpy.AddMessage("Old file successfully cleaned!!!!!!!")
                else:
                    arcpy.AddWarning("Manifest file does not exist: {}".format(manifestPath))
                    arcpy.AddWarning(str("Skipping old asset clean up...\n" +
                                    "old assets files should still be overwritten"))


            except:
                printException(2)
                arcpy.AddWarning(str("Skipping old asset clean up...\n" +
                                    "old assets are still expected overwritten"))

            # 5) copies new assets from temp to CTS_Root
            arcpy.AddMessage('Step 5of6: copy new assets from temp to CTS_Root')

            NewFolderList  = [f for f in os.listdir(NewRootFolder) if os.path.isdir(os.path.join(NewRootFolder, f))]
            NewFileList    = [f for f in os.listdir(NewRootFolder) if os.path.isfile(os.path.join(NewRootFolder, f))]

            arcpy.AddMessage('Atempting to copy: {}'.format(NewFolderList))
            arcpy.AddMessage('from: {}'.format(TempWorkingPath))
            arcpy.AddMessage('to: {}'.format(RootFolder))

            for dirs in NewFolderList:
                try:
                    tempPath_src = os.path.join( NewRootFolder,dirs)
                    arcpy.AddMessage('Atempting to copy: {}'.format(tempPath_src))

                    targetPath_dsc = os.path.join(RootFolder,dirs)
                    if os.path.exists(targetPath_dsc):
                        try:
                            arcpy.AddWarning('Target folder already exists: {}'.format(targetPath_dsc))
                            arcpy.AddMessage('Atempting to delete:          {}'.format(targetPath_dsc))
                            shutil.rmtree(tempPath_src)
                            arcpy.AddMessage('Successfully  deleted:        {}'.format(targetPath_dsc))
                        except:
                            exceptMesg = printException(2)
                            printFunctionInfoEnd(3,False,exceptMesg,1)
                            return False
                    arcpy.AddMessage('to: {}'.format(targetPath_dsc))
                    shutil.copytree(tempPath_src,targetPath_dsc)
                    arcpy.AddMessage('Successfully  copied: {}'.format(targetPath_dsc))

                except:
                    exceptMesg = printException(2)
                    printFunctionInfoEnd(3,False,exceptMesg,1)
                    return False
            arcpy.AddMessage('Successfully copied: {}'.format(NewFolderList))
            arcpy.AddMessage('from: {}'.format(TempWorkingPath))
            arcpy.AddMessage('to: {}'.format(RootFolder))


            for files in NewFileList:
                try:
                    tempPath_src = os.path.join( NewRootFolder,files)
                    arcpy.AddMessage('Atempting to copy: {}'.format(tempPath_src))
                    targetPath_dsc = os.path.join(RootFolder,files)
                    arcpy.AddMessage('to: {}'.format(targetPath_dsc))
                    shutil.copy2( tempPath_src,targetPath_dsc)
                    arcpy.AddMessage('Successfully copied: {}'.format(targetPath_dsc))

                except:
                    exceptMesg = printException(2)
                    printFunctionInfoEnd(3,False,exceptMesg,1)
                    return False
            arcpy.AddMessage('Successfully copied: {}'.format(NewFolderList))
            arcpy.AddMessage('from: {}'.format(TempWorkingPath))
            arcpy.AddMessage('to: {}'.format(RootFolder))

            # 6)  delete timestamped temp directory"""
            arcpy.AddMessage('delete timestamped temp directory')


            #delete tempfile
            try:
                arcpy.AddMessage('Atempting to delete:  {}'.format(TempWorkingPath))
                shutil.rmtree(TempWorkingPath)
                arcpy.AddMessage('Successfully  deleted:{}'.format(TempWorkingPath))
            except:
                arcpy.AddWarning('ERROR: deleting:     {}'.format(TempWorkingPath))
                exceptMesg = printException(2)
                printFunctionInfoEnd(2,True,exceptMesg,1)
                return True
            successMessage = arcpy.AddMessage("All 6 STEPS of downloadExtractCleanUpdate SUCCESSFUL!")
            printFunctionInfoEnd(1,True,"Hello World. IT WORKED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",1)
            return True

        # Update Tool Logic and flow control for testing purposes only
##        arcpy.AddMessage("{:~^80}\n{:-^80}\n{:~^80}".format
##                        (""," Set Local Varibles from Parameters ",""))

        #Set variable from parameters
        def updateMissionControl ():
            """Primary logic for 'UpdateCTS-DITools' which provides flow control
            for the following six step process: 1) checkInternetConnection,
            2) parseVarsFromURL, 3) checkVersion, 4) promptUserForNextStep,
            5) backupCTSData, 6) downloadCleanInstall"""
            printFunctionInfoStart(4,False)

            arcpy.AddMessage("Step 0of6: Set Local Varibles from Parameters")
            CTS_RootFolder      = parameters[0].valueAsText
            LocalVersion        = parameters[1].valueAsText
            Build               = parameters[2].valueAsText
            BackupTargetFolder  = parameters[3].valueAsText
            BackupZipFileName   = parameters[4].valueAsText
            FullZipFilePath     = parameters[5].valueAsText
            LatestVersionTxtURL = parameters[6].valueAsText
            arcpy.AddMessage("Value of CTS_RootFolder       = {}".format(CTS_RootFolder))
            arcpy.AddMessage("Value of LocalVersion         = {}".format(LocalVersion))
            arcpy.AddMessage("Value of Build                = {}".format(Build))
            arcpy.AddMessage("Value of BackupTargetFolder   = {}".format(BackupTargetFolder))
            arcpy.AddMessage("Value of BackupZipFileName    = {}".format(BackupZipFileName))
            arcpy.AddMessage("Value of FullZipFilePath      = {}".format(FullZipFilePath ))
            arcpy.AddMessage("Value of LatestVersionTxtURL  = {}".format(LatestVersionTxtURL))

            if checkInternetConnection():
                try:
                    LatestList = parseVarsFromURL(LatestVersionTxtURL,Build)
                    LatestVersion       = LatestList[0]
                    LatestDownloadURL   = LatestList[1]
                    arcpy.AddMessage("Value of LatestList           = {}".format(LatestList))
                    arcpy.AddMessage("Value of LatestVersion        = {}".format(LatestVersion))
                    arcpy.AddMessage("Value of LatestDownloadURL    = {}".format(LatestDownloadURL))
                except:
                    printException(2)
            checkVersionResult = checkVersion(LocalVersion,LatestVersion)
            if promptUserForNextStep(checkVersionResult,LocalVersion,LatestVersion):
                if backupCTSData(CTS_RootFolder,FullZipFilePath):
                    if downloadCleanInstall(LatestDownloadURL,CTS_RootFolder):
                        printFunctionInfoEnd(1,True,"IT WORKED!",1)
                        return True


        #On you marks, get set, Go!

        updateMissionControl()


        arcpy.AddMessage("{: <15}{: ^70}{: >15}\n"
        .format('',"The mountains are calling and I must go. - John Muir",''))
        return #def execute



##    -------------------------------------   Old flow control for testing-------------------------------------------------
##        if checkInternetConnection:
##            LatestList = parseVarsFromURL(LatestVersionTxtURL,Build)
##        LatestVersion       = LatestList[0]
##        LatestDownloadURL   = LatestList[1]
##

##
##        checkVersionResult = checkVersion(LocalVersion,LatestVersion)
##        arcpy.AddMessage("Value of checkVersionResult = {:>30}".format(checkVersionResult))
##
##        promptUserForNextStepResult = promptUserForNextStep(checkVersionResult,LocalVersion,LatestVersion)
##        arcpy.AddMessage("Value of promptUserForNextStepResult = {:>30}".format(promptUserForNextStepResult))
##
##        if promptUserForNextStepResult:
##            arcpy.AddMessage('User Said UPDATE!')
##            if backupCTSData(CTS_RootFolder,FullZipFilePath):
##                arcpy.AddMessage("Created Zip achive = {}".format(FullZipFilePath))
##                arcpy.AddMessage("Backing up CTS_Root = {}".format(CTS_RootFolder))
##        if downloadExtractCleanUpdate(LatestDownloadURL, CTS_RootFolder):
##            arcpy.AddMessage("SUCCESS updating to {}".format(LatestVersion)+"!!!!!!!!!!!!!!!!!!!!")

##        arcpy.AddMessage("Value of CheckInternetConnection = {}".format(x))
##        arcpy.AddMessage("You clicked OK")





  
