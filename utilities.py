import os
import os.path
import sys
import platform
import subprocess

import re
import random

import urllib.parse
import datetime


import clrprint






# Prints path formated so that 
# substrings enclosed by delim in the directory or file name
# is displayed with different color.
#
# Used to display matching directory or file paths when
# doing a search.

def printPath(parent, resourceName, delim, color='red'):
    print( parent,'/', sep='', end='')
    parts = resourceName.split(delim)
    for idx, p in enumerate(parts):
        if idx%2 == 1:
           clrprint.clrprint(p, clr=color, end='')
        else:
           print( p, end='')
    print('')     




# Joins and creates a path string to file
# with fixed slashes/backslashes
# TODO: Should make use or .normpath(), relpath(), normcase(), abspath()???? etc.
#       See: https://docs.python.org/3/library/os.path.html#os.path.normcase
# 
def normalizedPathJoin(base, pth):
    
    if os.path.isabs(pth): 
       return(os.path.normpath(pth) )

    return( os.path.normpath(os.path.join(base, pth)) )




# Checks if obect name on complies to exclusion and inclusion pattern.
# nameComplies returns True, if name does NOT match exclusion regex pattern (xP)
# AND matches inclusion regex pattern (iP).
# An empty imclusion regex pattern means no inclusion pattern i.e. all
# object names are good.
#
# TODO: Has not been tested.
def nameComplies( on, xP='', iP='', dbg=False ):
    #print(xP, iP)
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
              print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return(False) 

    if re.search(iP, on) is None:
       if dbg:
          print( lvl*"-", "NOT MATCHING INCLUSION:[", on, "] lvl:", lvl )
       return(False)

    return(True)




# This is a special one, like nameComplies, but only
# for use in the searchDirectory function.
# This function not only checks for compliance - it
# also replaces the matches with a special string to
# enable formated output later on.
#
# Returns empty string if on does not comply and
# on with matches replaced if it complies
def searchNameComplies(on, xP='', iP='', matchReplacement='', dbg=False):
    
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
          print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return('')
    
    result = re.subn(iP, matchReplacement, on)
    if result[1] > 0:
       return(result[0])

    # This means no match 
    return('')






def makeHtmlLink(itemPath, displayAnchor, urlEncode):
    
    if urlEncode:
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8') ) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 
    


#
# Taken from here:
#   https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times
#
# For an explanation see:
#   http://stackoverflow.com/a/39501288/1709587
#
def fileCreationDate(filePath):
  try:  
    epochTime = -1
    if platform.system() == 'windows':
        epochTime = os.path.getctime(filePath)
    else:
        stat = os.stat(filePath)
        try:
            epochTime = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            epochTime = stat.st_mtime

    return( datetime.datetime.fromtimestamp(epochTime).strftime("%d/%m/%Y, %H:%M:%S") )    

  except Exception as fcEx:
      print('Exception getting creation date:', str(fcEx))
      return('')  
  
 


# File metadata.
# All fields are returned as strings...
# TODO: should this be changed???
def fileInfo( filePath ):
    fInf = {}
    try:
      fInf['size']  = str(os.path.getsize(filePath))
    except Exception as fszEx:
          fInf['size'] = "-1"

    try:
       lmd = datetime.datetime.fromtimestamp(os.path.getmtime(filePath)) 
       fInf['creationdate'] = lmd.strftime("%d/%m/%Y, %H:%M:%S")
    except Exception as dtmEx:
        fInf['creationdate'] = ''

    try:
       fInf['lastmodified'] = fileCreationDate(filePath)
    except Exception as fcdEx:
        fInf['lastmodified'] = ''

    return(fInf)





# Replaces pseudovariables for file entries
# when displaying fs contents in html
def formatFile(fpath, fname, prolog, epilog, level, encUrl=False):

    formatedContents =  prolog.replace('${FILELINK}', makeHtmlLink(fpath, fname, encUrl)).replace('${FILENAME}', fname).replace('${FILEPATH}', fpath).replace('${LEVEL}', str(level)) + epilog
    fMeta = fileInfo(fpath)
    if fMeta:
       formatedContents = formatedContents.replace('${FILESIZE}', fMeta['size']).replace('${FILELASTMODIFIED}', fMeta['lastmodified'])

    return( formatedContents )





# Opens a file using the default application.
def openFile(filePath):

    if sys.platform.lower() == 'win32':
       os.startfile(filePath)
    else:
        opener = "open" if sys.platform.lower() == "darwin" else "xdg-open"
        subprocess.call([opener, filePath])







#####################################################
#
#
#
# Functions traversing directory structure 
#
#
#
#####################################################


#
# TODO: 1) Do we need epilog and fepilog??? 2) Check PSEUDOs - check DIRLINK etc
#       3) Change name to indicate formated output 
def traverseDirectory(root=".//", lvl=1, recursive = True, maxLevel=-1,
                      exclusionPattern="", inclusionPattern="",
                      dirList=None, fileList=None,
                      encodeUrl=False,                      
                      prolog="", epilog="",
                      fprolog="", fepilog="", vrb=False):
    
           
    if maxLevel > 0:
       if lvl > maxLevel: 
          return(-1, 0, 0, 0, "")


    # Gather directories and files in directory identified by
    # path root.
    #
    # In case of error, quit returning special status
    try:      
      path, dirs, files = next( os.walk(root) )    
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )  
      return(-2, 0, 0, 0, "")

    
    nDirs  = 0 # TOTAL number of directories
    nFiles = 0 # TOTAL number of files
    lnDirs = 0 # local number of directories i.e. number of directories in directory NOT including its subdirs
    lnFiles = 0 # local number of files i.e. number of files in directory NOT including files in its subdirs
    formatedContents = "" # Formated directory and files



    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
         
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern): 
           continue
            
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
        dirList.append(directoryPath)

        nDirs +=1
        lnDirs += 1       
        
        # The semantics in order: 
        # total number of directories, total number of files, local number of dirs, local number of files,
        # formatted display of subdirectory 
        subDirData = (0,0,0,0, "")
        if recursive:
            # go into subdirectory and traverse it
            subDirData = traverseDirectory( directoryPath, lvl+1, recursive, maxLevel,
                                              exclusionPattern, inclusionPattern,
                                              dirList, fileList,
                                              encodeUrl,
                                              prolog, epilog, 
                                              fprolog, fepilog, vrb)  

            # Upate total number of directories and files that will
            # be propagated upwards.
            # subDirData[0] will also carry any error encountered
            # during traversal of subdirectories.
            if subDirData[0] >= 0:
               nDirs += subDirData[0]
               nFiles += subDirData[1]

        # Prepare the entry for one single directory encountered
        dId = "d-" + str(lvl) + "-" + str( random.randint(0, 1000000) )
        formatedContents = formatedContents + prolog.replace("${ID}", dId).replace("${DIRLINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeUrl) ).replace('${DIRNAME}', encounteredDirectory).replace('${LEVEL}', str(lvl)) + subDirData[4]
        formatedContents = formatedContents.replace('${LNDIRS}', str(subDirData[2])).replace('${NDIRS}', str(subDirData[0]))
        formatedContents = formatedContents.replace('${LNFILES}', str(subDirData[3])).replace('${NFILES}', str(subDirData[1]) )
        formatedContents = formatedContents + epilog
        
    
  
    # Process all files in current directory
    for encounteredFile in files:

        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           continue
        
        filePath = normalizedPathJoin(root, encounteredFile)          
 
        nFiles +=1
        lnFiles += 1
        
        fileList.append(filePath)

        formatedContents = formatedContents + formatFile(filePath, encounteredFile, fprolog, fepilog, lvl, encodeUrl)


    # Return data to upper directory
    #
    # The tuple returned has the following data
    # nDirs: total directories up to this point, nFiles: total files up to this point
    # lnDirs:  number of directories in this directory only, lnFiles: number of files
    # in this directory only, formatedContents: complete formated content up to this
    # point
    return nDirs, nFiles, lnDirs, lnFiles, formatedContents









# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def jsonTraverseDirectory(root=".//", lvl=1, recursive = True, maxLevel=-1,
                          exclusionPattern="", inclusionPattern="", encodeUrl=False):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          #if vrb: 
             #print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return({})
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return ({})
    

    directoryContents = {}
    

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
        
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern): 
           continue
            
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
    
        #directoryPath = normalizedPathJoin(root, encounteredDirectory)
       
        if recursive:
            directoryContents[encounteredDirectory]  = jsonTraverseDirectory( directoryPath,
                                                                              lvl+1,
                                                                              recursive,
                                                                              maxLevel,
                                                                              exclusionPattern,
                                                                              inclusionPattern,
                                                                              encodeUrl)
                                              
            
            
            
    # Process all files in current directory
    
    fileList = []
    for encounteredFile in files:
        
        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           continue
        
        filePath = normalizedPathJoin(root, encounteredFile)  

        try:
           fMeta = fileInfo(filePath)
           fileList.append( {'path':encounteredFile,
                             'size':fMeta['size'],
                             'lastmodified':fMeta['lastmodified'],
                             'creationdate': fMeta['creationdate']
                             })
        except Exception as szEx:
           # TODO: specialize exceptions. Might get a "File name too long"
           # exception
           ileList.append( {'path':encounteredFile,
                            'size':'-1',
                            'lastmodified':'---',
                            'creationdate': '---'}) 

    directoryContents['__files'] = fileList
    
    return directoryContents







# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def searchDirectories(root=".//", lvl=1, recursive = True, maxLevel=-1, 
                      exclusionPattern="", inclusionPattern="", fileCriteria={},
                      matchingPaths=[], scannedCount=0, matchCount=0, vrb=False):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return((-1, 0))
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return ( (-2, 0) )
    
    #print('Entering searchDirectories with', nF)
    nScanned = scannedCount
    nFound = matchCount
    
    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
        
      
        nScanned += 1 
        if vrb:
            print( lvl*"-", nScanned, ')', normalizedPathJoin(root, encounteredDirectory), "lvl:", lvl )

        directoryPath = normalizedPathJoin(root, encounteredDirectory)
        parentPath = os.path.dirname( directoryPath )
        matchedDirName = searchNameComplies(encounteredDirectory, exclusionPattern, inclusionPattern, r'/\1/', False)
        if matchedDirName == '':
           if vrb:
              print('IGNORING DIRECTRORY', encounteredDirectory)              
        else:           
           nFound += 1
           matchingPaths.append(directoryPath)
           print('\t', nFound, ') ', sep='', end='')
           printPath(parentPath, matchedDirName, '/', 'green')
                  
        if recursive:
            nScanned, nFound = searchDirectories( directoryPath, lvl+1,
                                                  recursive, maxLevel, 
                                                  exclusionPattern, inclusionPattern, fileCriteria,
                                                  matchingPaths, nScanned, nFound, vrb )
                                                  
                             
            if nScanned < 0:
               if nScanned != -1:
                  return( nScanned, nFound )
                
            
            
    # Process all files in current directory
    fileList = []
    for encounteredFile in files:

        nScanned += 1
        fullPath = normalizedPathJoin(root, encounteredFile)
        if vrb:
            print( lvl*"-", nScanned, ')', fullPath, "lvl:", lvl )

        parentPath = os.path.dirname( fullPath )
        matchedFileName = searchNameComplies(encounteredFile, exclusionPattern, inclusionPattern, r'/\1/', False)
        if matchedFileName == '':
           continue
        else:
            # Check file metadata criteria...
            if fileCriteria:            
               fileMeta = fileInfo(fullPath)
               #print('Checking if file [', fullPath, '] meets minimum size criteria ', fileCriteria.get('minfilesize', -1), '...', sep='', end='' )
               if fileCriteria.get('minfilesize', -1) >= 0:
                if int(fileMeta['size']) < fileCriteria.get('minfilesize', -1):
                  #print('No. (', fileMeta['size'], ')' ) 
                  continue

               #print('YES!. (', fileMeta['size'], ')' )
               
               #print('Checking if file [', fullPath, '] meets maximum size criteria ', fileCriteria.get('maxfilesize', -1), '...', sep='', end='' )  

               if  fileCriteria.get('maxfilesize', -1) > 0:
                if int(fileMeta['size']) > fileCriteria.get('maxfilesize', -1):
                  #print('No. (', fileMeta['size'], ')' ) 
                  continue 

               #print('YES!. (', fileMeta['size'], ')' )
               
            nFound += 1
            matchingPaths.append(fullPath)
            print('\t', nFound, ') ', sep='', end='')
            printPath( parentPath, matchedFileName, '/', 'red' ) 
            
    return nScanned, nFound


