import os
import os.path
import re
import random

import urllib.parse


# Joins and creates a path string to file
# with fixed slashes/backslashes
def normalizedPathJoin(base, pth):
    if os.path.isabs(pth): 
       return( pth.replace("\\", "/") )
    
    return( os.path.join(base, pth).replace("\\", "/") )


# Checks if obect name on complies to exclusion and inclusion pattern.
# nameComplies returns True, if name does NOT match exclusion regex pattern (xP)
# AND matches inclusion regex pattern (iP).
# An empty imclusion regex pattern means no inclusion pattern i.e. all
# object names are good.
#
# TODO: Has not been tested.
def nameComplies( on, xP='', iP='', dbg=False ):
    if xP!= "" and re.search(xP, on) is not None:
       if dbg:
              print( lvl*"-", "EXCLUDING:[", on, "] lvl:", lvl )               
       return(False) 

    if re.search(iP, on) is None:
       if dbg:
          print( lvl*"-", "NOT MATCHING INCLUSION:[", on, "] lvl:", lvl )
       return(False)

    return(True)




def makeHtmlLink(itemPath, displayAnchor, htmlEncode):
    
    if htmlEncode:
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8') ) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 
    




def traverseDirectory(root=".//", lvl=1, maxLevel=-1, vrb=False, encodeHtml=False,
                     colorCycling=False, recursive = True,
                     exclusionPattern="", inclusionPattern="",
                     dirList=None, fileList=None, prolog="", epilog="",
                     fprolog="", fepilog=""):
    
           
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return(-1, 0, "")
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return(-2,0, "")
    
    nDirs  = 0 
    nFiles = 0 
    formatedContents = ""

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
         
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern):
           if vrb:
              print('IGNORING', encounteredDirectory) 
           continue
            
        directoryPath = normalizedPathJoin(root, encounteredDirectory) 

        nDirs +=1
        dirList.append(directoryPath)
        
        # Generate a unique id; used for html elements
        dId = "d-" + str(lvl) + "-" + str( random.randint(0, 1000000) )
        formatedContents = formatedContents + prolog.replace("${ID}", dId).replace("${LINK}", makeHtmlLink(directoryPath, encounteredDirectory, encodeHtml) ).replace('${DIRNAME}', encounteredDirectory)
             
        if recursive:
            nd, nf, fmtC = traverseDirectory( directoryPath, lvl+1,
                                              maxLevel, vrb, encodeHtml, colorCycling,
                                              recursive, exclusionPattern, inclusionPattern,
                                              dirList, fileList, prolog, epilog, fprolog, fepilog)
            
            formatedContents = formatedContents + fmtC
            if nd >= 0 and nf >= 0:
               nDirs += nd
               nFiles += nf

        formatedContents = formatedContents + epilog
        # TODO: if error indicates that max level was reached,
        #       just break - no reason to continue



        
        
    # Process all files in current directory
    for encounteredFile in files:

        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           if vrb:
              print('IGNORING', encounteredDirectory) 
           continue
        
        filePath = normalizedPathJoin(root, encounteredFile)          
 
        nFiles +=1
        fileList.append(filePath)
        
        formatedContents = formatedContents + fprolog.replace('${LINK}', makeHtmlLink(filePath, encounteredFile, encodeHtml)).replace('${FILENAME}', encounteredFile) + fepilog
        
        
    return nDirs, nFiles, formatedContents

















# Traverses directory and returns paths to encountered directories and files
# in separate lists. Files are returned as dict, containing two keys: path and size.
# 
def traverseDirectoryToList(root=".//", lvl=1, maxLevel=-1, vrb=False, encodeUrl=False,
                            colorCycling=False, recursive = True, exclusionPattern="",
                            inclusionPattern="", rootObj={}):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return([], [])
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return ([], [])
    

    directoryList = []
    fileList = []

    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
        
        if vrb:
            print( lvl*"-", normalizedPathJoin(root, encounteredDirectory), "lvl:", lvl )

        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern):
           if vrb:
              print('IGNORING', encounteredDirectory) 
           continue
        
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)

        dirEntry = {'path':directoryPath, 'nFiles':-1} 
        #directoryList.append(directoryPath)
        directoryList.append(dirEntry)
        
        # Generate a unique id; used for html elements
          
        if recursive:
            dL, fL = traverseDirectoryToList( directoryPath, lvl+1,
                                              maxLevel, vrb, encodeUrl, colorCycling,
                                              recursive, exclusionPattern,
                                              inclusionPattern, dirEntry)
            
            directoryList.extend(dL)
            fileList.extend(fL)
            
             

    # Process all files in current directory
    nF = 0
    for encounteredFile in files:
        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           print('IGNORING', encounteredFile) 
           continue
        nF += 1
        fullPath = normalizedPathJoin(root, encounteredFile)
        
        if vrb:
           print( lvl*"-", fullPath, "lvl:", lvl )

        try:
           fileList.append( {'path':fullPath, 'size':os.path.getsize(fullPath)})
        except Exception as szEx:
           # TODO: specialize exceptions. Might get a "File name too long"
           # exception
           fileList.append( {'path':fullPath, 'size':-3}) 

    rootObj['nFiles'] = nF    
    return directoryList, fileList





# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def jsonTraverseDirectory(root=".//", lvl=1, maxLevel=-1, vrb=False, encodeUrl=False,
                            colorCycling=False, recursive = True, exclusionPattern="",
                            inclusionPattern=""):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
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
        
        if vrb:
            print( lvl*"-", normalizedPathJoin(root, encounteredDirectory), "lvl:", lvl )

        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern):
           if vrb:
              print('IGNORING', encounteredDirectory) 
           continue
        
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)

        
          
        if recursive:
            directoryContents[encounteredDirectory]  = jsonTraverseDirectory( directoryPath, lvl+1,
                                              maxLevel, vrb, encodeUrl, colorCycling,
                                              recursive, exclusionPattern,
                                              inclusionPattern)
            
            
            
    # Process all files in current directory
    
    fileList = []
    for encounteredFile in files:
        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           print('IGNORING', encounteredFile) 
           continue
        
        #fullPath = normalizedPathJoin(root, encounteredFile)
        
        if vrb:
           print( lvl*"-", fullPath, "lvl:", lvl )

        try:
           fileList.append( {'path':encounteredFile, 'size':os.path.getsize(fullPath)})
        except Exception as szEx:
           # TODO: specialize exceptions. Might get a "File name too long"
           # exception
           fileList.append( {'path':encounteredFile, 'size':-3}) 

    directoryContents['__files'] = fileList
    
    return directoryContents











# Traverses directory and returns directory structure as a json object.
# directory/file names are relative
# 
def searchDirectories(root=".//", lvl=1, maxLevel=-1, vrb=False, encodeUrl=False,
                            colorCycling=False, recursive = True, exclusionPattern="",
                            inclusionPattern=""):
    
    if maxLevel > 0:
       if lvl > maxLevel:
          if vrb: 
             print('Current Level greater than maxLevel', maxLevel, "Not traversing INTO", root) 
          return(None)
        
    try:      
      path, dirs, files = next( os.walk(root) )
    except:
      return (None)
    


    # Process all directories in current directory.
    # If recursive is True, traverse into each directory
    # Does a depth first search (DFS) approach
    for encounteredDirectory in dirs:
        
        if vrb:
            print( lvl*"-", normalizedPathJoin(root, encounteredDirectory), "lvl:", lvl )

        directoryPath = normalizedPathJoin(root, encounteredDirectory) 
        if not nameComplies(encounteredDirectory, exclusionPattern, inclusionPattern):
           if vrb:
              print('IGNORING DIRECTRORY', encounteredDirectory)              
        else:           
           print('FOUND DIRECTORY MATCH:[', directoryPath, '] ', sep='' ) 
                  
        if recursive:
            searchDirectories( directoryPath, lvl+1,
                             maxLevel, vrb, encodeUrl, colorCycling,
                             recursive, exclusionPattern, inclusionPattern)
            
            
            
    # Process all files in current directory
    
    fileList = []
    for encounteredFile in files:
        if not nameComplies(encounteredFile, exclusionPattern, inclusionPattern):
           if vrb: 
              print('IGNORING FILE', encounteredFile) 
           continue
        
        fullPath = normalizedPathJoin(root, encounteredFile)
        
        if vrb:
           print( lvl*"-", fullPath, "lvl:", lvl )

          
        try:
           #fileList.append( {'path':encounteredFile, 'size':os.path.getsize(fullPath)})
           print('FOUND FILE:[', fullPath, '] Size:', os.path.getsize(fullPath), sep='' )
        except Exception as szEx:
           # TODO: specialize exceptions. Might get a "File name too long"
           # exception
           print('FOUND MATCH:[', fullPath, '] Size: error getting size', sep='' )
   
    
    return None


