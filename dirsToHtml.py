#
# This program attempts to do the following:
# Traverses a directory structure on the disk and create an html document (index.html)
# linking to the files found inside these folders.
#
# The general idea is to offer an convenient way to browse the directory/files
#
# NOTES:
#  Does not work YET as indended. The main problem is that some
#  links aren't working. Probably has to do with spaces in file names.
#
#
# VERSION HISTORY:
#
#  -20/02/2021: v0.65b
#      * Added -T option to include an introduction text in the html 
#
#  -19/02/2021: v0.6b.
#      * Added options -S (style sheet), -x (excluded file list) and -i (included file list).
#      * Corrected the way directories and files are counted.
#
#  -16/02/2021: v0.4b.
#      * Fixed bug with non working file links. Seems ok-ish now (???)
#      * Added command line options that allow: specifying starting directory, color cycling of directory names, output file, trivial help etc 
#   
#  -12/02/2021: v0.1 first working (more or less) release.
#
#
#  v0.65b rd20022021 
#

import os
import os.path
import sys, getopt
import re
import io
import random
import fnmatch


# This variable holds the html code BEFORE writing it into the file
htmlCode = '<html><head><link rel="stylesheet" href="${CSSFILE}"></head><body><div id="container">\n<div id="cHeader">${TITLE}<br><div id="headerText">${INTROTEXT}</div></div> <div id="content"> <ol id="nestedlist">'

# Colors to choose from if color cycling is enabled (-c)
colorPalette = ['#4287f5', '#801408', '#08259c', '#4560d1', '#0a690a', '#9c5f1e', '#9c1e87', '#1313f2', '#f21313', '#34ba4a', '#19084a', '#27889c', '#317534', '#e8740e', '#000000',
                '#1e5f85', '#2f2561', '#5c0c25', '#324530', '#f07e0c', '#e04e14', '#8f8824', '#478072', '#05998d',  '#1890a8', '#033e6b', '#0a2940', '#281a75', '#453043', '#b50e40' ]


backgroundPalette = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#B5B9FF', '#FF9C##', '#ECD4FF', '#FFFFD1', '#AFF8DB', '#ACE7FF', '#B49FDC',
                    '#A5F8CE', '#FEC9A7']

def folderLink(rootF, henc=False, cl='#000000'):
    nVal = re.sub("\s\s+" , " ", rootF)
    if henc:
       nVal = nVal.replace(' ', '%20')
    
    return '<font color="' + cl + '"><b>'  + rootF + "</b></font>"

def fileLink(filePath, fn="", henc=False):
    nVal = re.sub("\s\s+" , " ", filePath)
    if henc:
       nVal = nVal.replace(' ', '%20')
       nVal = nVal.replace('/', '\\')
       
    return '<a href="' + nVal + '" target="_blank" rel="noopener noreferrer">' + fn + '</a>'  


def excludeFile(fn, xList):

    if (len(xList) == 0 ):
        return(False)
    
    for p in xList:
        #print("---checking", fn, "pattern", p, end="")
        if fnmatch.fnmatch(fn, p):
           #print(fn, "matches", p)
           return(True)
        #else:
        #    print(" NO MATCH!") 

    return(False) 


def includeFile(fn, iList):
    
    if (len(iList) == 0 ):
        return(True)
    
    for p in iList:        
        if fnmatch.fnmatch(fn, p):           
           return(True)
        
    return(False) 

    
#
# Params
#   root: directory to scan
#   vrb: verbose or not. Verbose prints the directory scanned
#   henc: html encoding of special characters
#   colorCycling: should color for directories be cycled randomly (per level)?
#
def scanDir(root, lvl=1, vrb=False, henc=False, colorCycling=False, recDir = True, xList=[], iList=[]):
    global htmlCode, colorPalette, backgroundPalette
    clr = '#000000'
    if colorCycling:
       clr =  random.choice(colorPalette)       
          
    path, dirs, files = next(os.walk(root) )
    nDirs = 0 #len(dirs)
    nFiles = 0 #len(files)
    for d in dirs:
        if vrb:
            print( lvl*"--", os.path.join(root, d), "lvl:", lvl )
        htmlCode = htmlCode + "<li class=\"dre child\">[" +  folderLink(d, henc, clr) + "]\n<ol>\n"
        if (recDir):
            nd, nf = scanDir( os.path.join(root, d), lvl+1, vrb, henc, colorCycling, recDir, xList, iList)
            nDirs += nd
            nFiles += nf
        htmlCode = htmlCode + "</ol></li>\n"
        nDirs +=1

    for f in files:
        if vrb:
           print( lvl*"--", os.path.join(root, f), "lvl:", lvl )

        if not excludeFile(os.path.join(root, f), xList ):   
           htmlCode = htmlCode + "<li class=\"fle\">\n"  + fileLink(os.path.join(root, f), f) + "</li>\n"
           nFiles +=1

    return nDirs, nFiles


def printHelp():
    print("Usage: dirTraverse [-v] [-d directory] [-o output file] [-e]")
    print("-v : How verbose")
    print("-d [directory]: Starting directory to start scanning")
    print("-e : Html encode filenames")
    print("-o [file name]: Name of file to save html form of traversal ")
    print("-S : No recusive scanning of directories")
    print("-h : This screen")
    print("-G : Debug mode TODO: not fully implemented")
    print("-s [css file]: css file")
    print("-x [pattern]: exclude files having [pattern] in name. You may add as many -x arguments as you like. If [patttern] is a valid file name, patterns are loaded from that file.")
    sys.exit(0)






#
# Initialize and parse options - if any
#
verbose = False
rootDir = ".\\ManolisMTzagarakis"
htmlEncode = False
outputfile = "index.html"
debugMode = False
cCycling = False
recursiveD = True
relativeP = True
excludedList = []
includedList = []
cssFile = 'style.css'
introText = ''
titleText = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"vd:eo:hcs:ax:i:SI:T:")
    for o, a in opts:
        if o in ['-v']:
           verbose = True
        if o in ['-d']:
           rootDir = a
        if o in ['-e']:
           htmlEncode = True
        if o in ['-o']:            
            outputfile = a
        if o in ['-h']:
            printHelp()
        if o in ['-G']:
            debugMode= True
        if o in ['-c']:
            cCycling = True
        if o in ['-S']:
            recursiveD = False
        if o in ['-a']:
            relativeP = False
        if o in ['-x']:
           if (os.path.isfile(a)):
               with open(a) as f:
                    excludedList = f.read().splitlines()
           else:
               excludedList.append(a)

        if o in ['-i']:
           if (os.path.isfile(a)):
               with open(a) as f:
                    includedList = f.read().splitlines()
           else:
               includedList.append(a)
        if o in ['-s']:
             cssFile = a
             
        if o in ['-I']:
            if (os.path.isfile(a)):
               with open(a) as f:
                    introText = f.read()
            else:
                 introText = a
                 
        if o in ['-T']:
              titleText = a
                        
except getopt.GetoptError as e:
       print("Usage: dirTraverse [-v] [-d directory] [-o output file] [-e] [-G] [-c] [-s] [-a] [-x pattern]")
       print("Try '", sys.argv[0], "-h' for more help")
       sys.exit(-1)


print("\n>>>Program starting with following options:")
print("\t-Root directory:", rootDir)
print("\t-Recursive directories:", recursiveD)
print("\t-Output file:", outputfile)
print("\t-Html encoding:", htmlEncode)
print("\t-Color cycling:", cCycling)
print("\t-Debug mode:", debugMode )
print("\t-Excluded file list:", excludedList)
print("\t-Included file list:", includedList)
print("\t-Style sheet:", cssFile)
print("\t-Title text:", titleText)
print("\t-Intro text:", introText)

if (not os.path.isdir(rootDir)):
    print("\n\nError:Root directory [", rootDir,"] is not a valid directory. Please make sure that the directory exists and is accessible.\n")
    sys.exit(-2)


htmlCode = htmlCode.replace("${CSSFILE}", cssFile)
htmlCode = htmlCode.replace("${BGCOLOR}", random.choice(backgroundPalette) )
htmlCode = htmlCode.replace("${INTROTEXT}", introText )
htmlCode = htmlCode.replace("${TITLE}", titleText )
if (debugMode):
     print("html code start", htmlCode)
     
#
# Start scanning from current directory.
#
print("\n\n>>>Starting scanning from [", rootDir, "]")
nD, nF = scanDir( rootDir, 1, verbose, htmlEncode, cCycling, recursiveD, excludedList)

# Note how we intitialized htmlCode in order to understand WHY we HAVE to
# add these closing tags.
htmlCode = htmlCode + "</ol></div> </div></body></html>"

print(">>>Total of ", nD, "directories and", nF, "files")

print(">>>Writing html to file [", outputfile, "] in utf-8")
# Write contents to index.html file
with io.open(outputfile, 'w', encoding='utf8') as f:
    f.write(htmlCode)
    


