import arcpy, os, time

class Toolbox(object):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [Update]


class Update(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update"
        self.description = "Update"
        self.canRunInBackground = False


    def getParameterInfo(self):
        """Define parameter definitions"""

        #First parameter
        param0 = arcpy.Parameter(
        displayName="CTS_Root Folder",
        name="CTS_Root",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")
        param0.value = os.path.dirname(os.path.realpath(__file__))


        #Second parameter
        param1 = arcpy.Parameter(
        displayName="Local Version",
        name="LocalVersion",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        TextFilePath = os.path.join(param0.valueAsText,
            r"Workspace\docs\LocalVersion.txt")
        with open(TextFilePath) as f:
            param1.value = f.read()



        # Third parameter
        param2 = arcpy.Parameter(
        displayName="Build (Subset of tools to be installed based on Contributors's Publishing Method)",
        name="Build",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        build = str(param1.valueAsText)
        build = build.split('.')[3]
        if build == 'master':
            param2.filter.type = "ValueList"
            param2.filter.list = ['admin','direct', 'active','master']
            param2.value = 'master'
        else:
            param2.enabled = False
            param2.parameterType = "Optional"
            param2.direction="Output"
            param2.displayName = 'Build can only be changed from master'
            param2.value = build

        # Fourth parameter
        param3 = arcpy.Parameter(
        displayName="Backup Target Folder",
        name="BackupTargetFolder",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")
        param3.value = os.path.dirname(param0.valueAsText)

        # Fifth parameter
        param4 = arcpy.Parameter(
        displayName="Backup FileName (.zip)",
        name="BackupZipFileName",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        param4.value =  os.path.basename(param0.valueAsText) +'-bu-'+ \
            str(time.strftime('%Y-%m%d-%H%M')) + '.zip'



        # Sixth parameter
        param5 = arcpy.Parameter(
        displayName="FullZipFilePath",
        name="FullZipFilePath",
        datatype="GPString",
        parameterType="Required",
        direction="Output",
        enabled=False)
        param5.value =  os.path.join(param3.valueAsText, param4.valueAsText)

        #Seventh parameter
        param6 = arcpy.Parameter(
        displayName="URL to CTS_DIT_LastestVersion.txt",
        name="LatestVersionTxtURL",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        param6.value = r'https://raw.githubusercontent.com/ColoGISpro/CTS-DITools/VCS-Vars-Only/CTS_DIT_LastestVersion.txt'


        params = [param0, param1, param2, param3, param4, param5, param6]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        parameters[5].value= os.path.join(parameters[3].valueAsText,parameters[4].valueAsText)

##        parameters[4].value = os.path.join(
##            parameters[2].valueAsText,
##            parameters[3].valueAsText)
##        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        import ctypes, shutil, urllib2, socket, glob


        def checkInternetConnection():
            """Check if local machine is connected to internet"""
            try:
                socket.gethostbyname('www.google.com')
                return True
            except:
                try:
                    socket.gethostbyname('www.nytimes.com')
                    return True
                except:
                    Title = 'Internet Connection Required!'
                    Message = 'An internet connection is required to get '+ \
                    'the lastest version. An error was encountered while ' +\
                    'atempting to ping\n\nwww.google.com/nwww.nytimes.com\n\n'+\
                    'Please check you internet conection and try again later'+\
                    '\nThe update has been aborted.'
                    self = ctypes.windll.user32.MessageBoxA
                    self(0,Message,Title,0x00200000L|0x00000000L|0x00000040L)
                    return False


        def parseVarsFromURL (WebPage, BUILD):
            """Parse the Latest Version from a text document on the web
            returns a list of str [LatestVersion, LatestVersDownloadURL"""
            url = urllib2.urlopen(WebPage)
            htmltext = url.read()
            url.close()

            StartIndex =  '<' + BUILD + 'Version>'
            EndIndex = '<_' + BUILD + 'Version_>'
            #  Calculates the starting position of the StartIndex and EndIndex
            StartIndexPosition = htmltext.find(StartIndex)
            #Gets the Starting Postion of value
            StartIndexPosition =  len(StartIndex) + StartIndexPosition
            #Calculates the ending postion of the var
            EndIndexPosition = htmltext.find(EndIndex)
            #Parses out Version
            Version = htmltext[StartIndexPosition:EndIndexPosition]
            StartIndex =  '<' + BUILD + 'URL>'
            EndIndex = '<_' + BUILD + 'URL_>'
            #  Calculates the starting position of the StartIndex and EndIndex
            StartIndexPosition = htmltext.find(StartIndex)
            #Adds the lenth of StartIndex string  to the startIndexPostion to get startng position variable
            StartIndexPosition =  len(StartIndex) + StartIndexPosition
            #Calculates the ending postion of the var
            EndIndexPosition = htmltext.find(EndIndex)
            #Parses out URL
            URL = htmltext[StartIndexPosition:EndIndexPosition]
            LatestList = [Version, URL]
            return LatestList


        def checkVersion(LocalVersion, LatestVersion):
            """Compairs LocalVersion to Latest Version and returns difference"""

            if LocalVersion == LatestVersion:
                return 'CURRENT'
            else:
                Local_list = LocalVersion.split('.')
                try:
                    Local_major = int( Local_list[0])
                    Local_minor = int( Local_list[1])
                    Local_patch = int( Local_list[2])
                    Local_build = str(Local_list[3])
                except:
                    return 'ERROR: LocalVersion not formated as Int.Int.Int.str'

                Latest_list = LatestVersion.split('.')
                try:
                    Latest_major = int( Latest_list[0])
                    Latest_minor = int( Latest_list[1])
                    Latest_patch = int( Latest_list[2])
                    Latest_build = str(Latest_list[3])
                except:
                    return 'ERROR: LatestVersion not formated as Int.Int.Int.str'

                if Local_major < Latest_major:
                    return 'MAJOR'
                elif Local_minor < Latest_minor:
                    return 'MINOR'
                elif Local_patch < Latest_patch:
                    return 'PATCH'
                elif Local_build != Latest_build:
                    return 'BUILD'
                else:
                    return 'ERROR: LocalVersion is newer than LatestVersion?'
                # possible strin values returned by CompareVersions
                    #CURRENT
                    #MAJOR
                    #MINOR
                    #PATCH
                    #BUILD
                    #ERROR: LocalVersion not formated as Int.Int.Int.str
                    #ERROR: LatestVersion not formated as Int.Int.Int.str
                    #ERROR: LocalVersion is newer than LatestVersion?



        def promptUserForNextStep(CheckVersionResult, LocalVer, LatestVer):
            """Conveys results of version check and asks user to update now"""
            Result = CheckVersionResult[0:5]
            arcpy.AddMessage("Result([0:5] = {}".format(Result))
            print 'Result: ' + Result

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
                return False


            elif Result == 'MAJOR':
                arcpy.AddMessage("elif == MAJOR code ran")
                Title = 'Major new release available [MAJOR.minor.patch.build]'
                Message = str('The local CTS_Toolbox.tbx is out of date:\n\n' +
                    'Local   v' + LocalVer  + '\n' +
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
                    return True
                else:
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
                    return True
                else:
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
                self = ctypes.windll.user32.MessageBoxA
                return self(0, Message, Title, 0x00200000L|0x00000004L|0x00000040L)


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
                return False

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
            try:
                shutil.make_archive(
                    base_name=os.path.splitext(NewZipFilePath)[0],
                    format='zip',
                    root_dir=os.path.dirname(CTS_RootFolderPath),
                    base_dir=os.path.basename(CTS_RootFolderPath),
                    verbose=0, dry_run=0, owner=None, group=None, logger=None)
                print 'Successfully created: ' + NewZipFilePath
                return True
            except:
                print 'Error atempting to create: '+ NewZipFilePath
                return False


        def DownloadExtractCleanUpdate (ZipURL, RootFolder):
            #Create local vars
            TimeAsString = time.strftime('%Y_%m%d_%H%M')
            print 'TimeAsString: ' +TimeAsString

            HomeFolder = os.path.dirname(RootFolder)
            print 'HomeFolder: ' + HomeFolder

            WorkspaceFolder = os.path.join(RootFolder, 'Workspace')
            print 'WorkspaceFolder: ' + WorkspaceFolder

            try:
                TempWorkingPath = os.path.join(HomeFolder, str('tmp_' +TimeAsString))
                os.mkdir(TempWorkingPath)
                print 'Created: TempWorkingPath: ' + TempWorkingPath
            except:
                os.remove(TempWorkingPath)
                print 'Deleted old: ' + TempWorkingPath
                os.mkdir(TempWorkingPath)
                print 'Created new: ' + TempWorkingPath


            NewZipFileName = 'CTS-Tools_DWNLD_' + TimeAsString  +'.zip'
            print 'NewZipFileName: ' + NewZipFileName

            NewZipPath = os.path.join(TempWorkingPath, NewZipFileName)
            print 'NewZipPath: ' + NewZipPath

            try:
                x = urllib.urlretrieve(ZipURL, NewZipPath)
                print 'downloaded zip from: ' + ZipURL
            except:
                print 'error downloading zip from: ' + ZipURL

            try:
                z = zipfile.ZipFile(NewZipPath)
                z.extractall(TempWorkingPath)
                z.close()
                print 'Extracted zip to: ' + TempWorkingPath
            except:
                print 'ERROR:  Extracting zip to: ' + TempWorkingPath


            #find the CTS_Root folder that was just extracted in the temp folder

            NewRootFolder = ''
            for root, dirs, files in os.walk(TempWorkingPath):
                CurrentTempDirName = os.path.basename(root)
                if CurrentTempDirName == 'CTS_Root':
                    NewRootFolder = root
                    print 'found CTS_root folder:'
                    print root
            if NewRootFolder == '':
                print 'ERROR: the extrated folder does not seem to have a CTS_Root folder????'

            NewHomeFolder = os.path.dirname(NewRootFolder)
            print 'NewHomeFolder: ' + NewHomeFolder

            NewWorkspaceFolder = os.path.join(NewRootFolder,'Workspace')
            print 'NewWorkspaceFolder: ' + NewWorkspaceFolder

            #Delete Workspace folder and CTS_Tools.tbx from CTS_Root folder so new assets can be copied there

            try:
                shutil.rmtree(WorkspaceFolder)
                print 'Obbbblitttteration of: ' + WorkspaceFolder
            except:
                print 'ERROR: Could not delete: ' +  WorkspaceFolder

            try:
                ToolboxPath = os.path.join(RootFolder,'CTS_Toolbox.tbx')
                os.remove(ToolboxPath)
                print 'Obbliteration of: '+ ToolboxPath
            except:
                print 'ERROR: deleting: ' +  ToolboxPath
                try:
                    #old Toolbox name had a space in leiu of a _
                    ToolboxPathOld = os.path.join(RootFolder,'CTS Toolbox.tbx')
                    os.remove(ToolboxPathOld)
                    print 'Obbliteration of: '+ ToolboxPathOld
                except:
                    print 'ERROR: deleting: ' +  ToolboxPathOld
            #Copy updated files from temp CTS_Root to real path

            shutil.copytree(NewWorkspaceFolder, WorkspaceFolder)
            print 'Copied: ' + NewWorkspaceFolder
            print 'to: ' + WorkspaceFolder

            NewToolboxPath = os.path.join(NewRootFolder,'CTS_Toolbox.tbx')

            shutil.copy2(NewToolboxPath, ToolboxPath)
            print 'Copied: ' + NewToolboxPath
            print 'to: ' + ToolboxPath

            # Copy new update toolbox if filename changed
            NewVersionManagerToolbox = glob.glob(NewHomeFolder +'\\*.tbx')
            NewVersionManagerToolboxPath = NewVersionManagerToolbox[0]
            print 'NewVersionManagerToolboxPath: ' + NewVersionManagerToolboxPath
            NewToolboxName = os.path.basename(NewVersionManagerToolboxPath)
            LocalVersionManagerToolboxPath = os.path.join(HomeFolder,NewToolboxName)
            print 'LocalVersionManagerToolboxPath: ' + LocalVersionManagerToolboxPath
            DoesLocalTooboxExist = os.path.exists(LocalVersionManagerToolboxPath)
            print 'DoesLocalTooboxExist: '
            print DoesLocalTooboxExist

            if DoesLocalTooboxExist:
                print 'it does exist so do nothing'
            else:
                OldVersionManagerToolbox = glob.glob(HomeFolder +'\\*.tbx')
                if OldVersionManagerToolbox == []:
                    print 'no need to promt user to delete becasue no toolbox current exists in HomeFolder'
                else:
                    OldVersionManagerToolboxPath = OldVersionManagerToolbox[0]
                    print 'promt use to delete: ' + OldVersionManagerToolboxPath

                shutil.copy2(NewVersionManagerToolboxPath, LocalVersionManagerToolboxPath)
                print 'Copied: '  + NewVersionManagerToolboxPath
                print 'To:     '  + LocalVersionManagerToolboxPath




            #delete tempfile
            try:
                shutil.rmtree(TempWorkingPath)
                print 'Obbbblitttteration of: ' + TempWorkingPath
            except:
                print 'ERROR: deleting: ' +  TempWorkingPath


        #Set variable from parameters
        CTS_RootFolder      = parameters[0].valueAsText
        LocalVersion        = parameters[1].valueAsText
        Build               = parameters[2].valueAsText
        BackupTargetFolder  = parameters[3].valueAsText
        BackupZipFileName   = parameters[4].valueAsText
        FullZipFilePath     = parameters[5].valueAsText
        LatestVersionTxtURL = parameters[6].valueAsText
        if checkInternetConnection:
            LatestList = parseVarsFromURL(LatestVersionTxtURL,Build)
        LatestVersion       = LatestList[0]
        LatestDownloadURL   = LatestList[1]

        arcpy.AddMessage("Value of CTS_RootFolder = {}".format(CTS_RootFolder))
        arcpy.AddMessage("Value of LocalVersion = {}".format(LocalVersion))
        arcpy.AddMessage("Value of Build = {}".format(Build))
        arcpy.AddMessage("Value of BackupTargetFolder = {}".format(BackupTargetFolder))
        arcpy.AddMessage("Value of BackupZipFileName = {}".format(BackupZipFileName))
        arcpy.AddMessage("Value of FullZipFilePath  = {}".format(FullZipFilePath ))
        arcpy.AddMessage("Value of LatestVersionTxtURL = {}".format(LatestVersionTxtURL))

        arcpy.AddMessage("Value of LatestList = {}".format(LatestList))
        arcpy.AddMessage("Value of LatestVersion = {}".format(LatestVersion))
        arcpy.AddMessage("Value of LatestDownloadURL = {}".format(LatestDownloadURL))

        checkVersionResult = checkVersion(LocalVersion,LatestVersion)
        arcpy.AddMessage("Value of checkVersionResult = {}".format(checkVersionResult))

        promptUserForNextStepResult = promptUserForNextStep(checkVersionResult,LocalVersion,LatestVersion)
        arcpy.AddMessage("Value of promptUserForNextStepResult = {}".format(promptUserForNextStepResult))

        if promptUserForNextStepResult:
            arcpy.AddMessage('GO1!')
            backupCTSData(CTS_RootFolder,FullZipFilePath)







##        arcpy.AddMessage("Value of CheckInternetConnection = {}".format(x))
##        arcpy.AddMessage("You clicked OK")




        return #def execute



################################# TEMPLATE #####################################
##class Tool(object):
##    def __init__(self):
##        """Define the tool (tool name is the name of the class)."""
##        self.label = "Tool"
##        self.description = ""
##        self.canRunInBackground = False
##
##    def getParameterInfo(self):
##        """Define parameter definitions"""
##        params = None
##        return params
##
##    def isLicensed(self):
##        """Set whether tool is licensed to execute."""
##        return True
##
##    def updateParameters(self, parameters):
##        """Modify the values and properties of parameters before internal
##        validation is performed.  This method is called whenever a parameter
##        has been changed."""
##        return
##
##    def updateMessages(self, parameters):
##        """Modify the messages created by internal validation for each tool
##        parameter.  This method is called after internal validation."""
##        return
##
##    def execute(self, parameters, messages):
##        """The source code of the tool."""
################################# TEMPLATE #####################################
