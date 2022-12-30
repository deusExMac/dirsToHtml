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
#
#  -29/12/2022: v0.8b
#      * Complete and major overhaul of source code. functions refactored and added, arguments
#        added, templating redesigned.
#
#
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
#   v0.8b rd29122022 
#  v0.65b rd20022021 
#
#
# Run with params (NEED TO BE UPDATED!): -c -I intro.txt -d .//ManolisMTzagarakis -T "Δημοσιέυσεις Εμμανουήλ Μ. Τζαγκαράκη"
#  

import os
import os.path
import sys, getopt
import argparse
import json

import re
import io
import random
import fnmatch

import utilities


# This variable holds the html code BEFORE writing it into the file
htmlCode = '<html><head> <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"> <title>"${TITLE}"</title><link rel="stylesheet" href="${CSSFILE}"></head><body id="topPage"><div id="container">\n<div id="cHeader">${TITLE}<br><div id="headerText">${INTROTEXT}</div></div> <div id="qnav"><div id="dirnavtitle">${DNAVTITLE}</div><div id="dirnav">${DIRNAV}</div></div> <div id="content"> <ul id="nestedlist">${FILESTRUCTURE}</ul></div></body></html>'
ABOUT = '<div id="about"><br><br>This file was automatically generated by <a href="https://github.com/deusExMac/dirsToHtml">dirsToHtml</a></div>'

# Colors to choose from if color cycling is enabled (-c)
colorPalette = ['#4287f5', '#801408', '#08259c', '#4560d1', '#0a690a', '#9c5f1e', '#9c1e87', '#1313f2', '#f21313', '#34ba4a', '#19084a', '#27889c', '#317534', '#e8740e', '#000000',
                '#1e5f85', '#2f2561', '#5c0c25', '#324530', '#f07e0c', '#e04e14', '#8f8824', '#478072', '#05998d',  '#1890a8', '#033e6b', '#0a2940', '#281a75', '#453043', '#b50e40',
                '#fcad03', '#03a1fc', '#24b332', '#851767', '#156e82', '#8c0a0a', '#b51d39', '#232791', '#6e8c0a', '#cc7a16', '#cc4016', '#051c80', '#9e981e', '#409e1e', '#09979c', '#9c0975']


backgroundPalette = ['#f7f6ab', '#faf9a0', '#f2f0fa', '#f2f8fa', '#faf9cd', '#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#B5B9FF', '#FF9C##', '#ECD4FF', '#FFFFD1', '#AFF8DB', '#ACE7FF', '#B49FDC',
                    '#A5F8CE', '#FEC9A7','#faf2d9', '#e3e8e8', '#eafad9', '#fafac8', '#fae7ca']



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




def main():

  # 
  # Parse command line arguments - if ant
  #
  try:
      
   cmdArgParser = argparse.ArgumentParser(description='Command line arguments', add_help=False)

   # Directory traversal related
   cmdArgParser.add_argument('-d', '--directory', default="exampleDir")
   cmdArgParser.add_argument('-NR', '--nonrecursive', action='store_true')
   cmdArgParser.add_argument('-X', '--excluded', default="")
   cmdArgParser.add_argument('-C', '--included', default="")
   cmdArgParser.add_argument('-L', '--maxlevel', type=int, default=-1)
  
   # html related output

   # Template to use.
   cmdArgParser.add_argument('-P', '--htmltemplate', default="html/template1.html")
   cmdArgParser.add_argument('-o', '--outputhtmlfile', default="index.html")
   cmdArgParser.add_argument('-s', '--cssfile', default="html/style.css")
   cmdArgParser.add_argument('-I', '--introduction', default="")
   cmdArgParser.add_argument('-T', '--title', default="")
   cmdArgParser.add_argument('-e', '--urlencode', action='store_true')

   cmdArgParser.add_argument('-G', '--debug', action='store_true')

   
   # We only parse known arguments (see previous add_argument calls) i.e. arguments
   # that the app requires for starting.
  
   knownArgs, unknownArgs = cmdArgParser.parse_known_args()
   args = vars( knownArgs )
   
  except Exception as argumentException:
    print('Argument error:', str(argumentException))
    sys.exit(-4)


    
  

  print("\n>>>Program starting with following options:")
  print("\t-Root directory:", args['directory'])
  print("\t-Max level:", args['maxlevel'])
  print("\t-Recursive directories:", not args['nonrecursive'])
  print("\t-Output file:", args['outputhtmlfile'])
  print("\t-Html encoding:", "???")
  print("\t-Color cycling:", "???")
  print("\t-Debug mode:", "???" )
  print("\t-Excluded file list:", args['excluded'])
  print("\t-Included file list:", args['included'])
  print("\t-Template file:", args['htmltemplate'])
  print("\t-Style sheet:", args['cssfile'])
  print("\t-Title text:", args['introduction'])
  print("\t-Intro text:", args['title'])


  # Check if introdution is a file. If so, read its contents
  # and use this as the introduction to the html export.
  if (os.path.isfile(args['introduction'])):
    try:
      with open(args['introduction']) as f:
         args['introduction'] = f.read() # replace it
    except Exception as introLoadEx:
         print('ERROR: Error reading file [', args['introduction'], ']')
         sys.exit(-1)


  if (not os.path.isdir(args['directory'])):
      print("\n\nError:Root directory [", args['directory'],"] is not a valid directory. Please make sure that the directory exists and is accessible.\n")
      sys.exit(-2)


  # Read template file. Exit in case of error
  htmlTemplate = ""
  try:
    with open( args['htmltemplate'], 'r', encoding='utf8') as content_file:
      htmlTemplate = content_file.read()
  except Exception as rdEx:
      print('Error reading template html file [', args['htmltemplate'],']:', str(rdEx))
      sys.exit(-3)

  #    
  # Replace all pseudovariables in the template file
  #
  htmlTemplate = htmlTemplate.replace("${CSSFILE}", args['cssfile'])
  htmlTemplate = htmlTemplate.replace("${BGCOLOR}", random.choice(backgroundPalette) )
  htmlTemplate = htmlTemplate.replace("${INTROTEXT}", args['introduction'] )
  htmlTemplate = htmlTemplate.replace("${TITLE}", args['title'] )


  ###################################################
  #
  # traverseDirectory (html output)
  #
  ###################################################
  
  dL = []
  fL = []
  d, f, traversalResult = utilities.traverseDirectory(args['directory'], 1,  not args['nonrecursive'],
                                                      args['maxlevel'], args['excluded'], args['included'],
                                                      dL, fL, args['urlencode'],            
                                                      "<li id=\"${ID}\"><details><summary>[${DIRNAME}]</summary><ul>\n",
                                                      "</ul></details></li>",
                                                      "<li class=\"fle\">${LINK}</li>\n",
                                                      "", False)


  htmlTemplate = htmlTemplate.replace("${INITIALDIRECTORY}", args['directory'] )
  htmlTemplate = htmlTemplate.replace("${FILESTRUCTURE}", traversalResult )

  print("\n#Directories:", d, "#Files:", f)
  with io.open(args['outputhtmlfile'], 'w', encoding='utf8') as f:
      f.write(htmlTemplate)


  sys.exit(-5)



  ###################################################
  #
  # searchDirectories
  #
  ###################################################
  utilities.searchDirectories(args['directory'], 1, args['maxlevel'], False, True, True, True, "", args['included'])
  sys.exit(-3)



  ###################################################
  #
  # jsonTraverseDirectory
  #
  ###################################################

  dCnts = utilities.jsonTraverseDirectory(args['directory'], 1, args['maxlevel'], False, True, True, True, "(?i).ds_store", "")
  print( json.dumps(dCnts) )
  sys.exit(-1)



  ###################################################
  #
  # traverseDirectoryToList
  #
  ###################################################
  
  dL = []
  fL = []

  dL, fL = utilities.traverseDirectoryToList(args['directory'], 1, args['maxlevel'], False, True, True, True, "(?i).ds_store", "")

  # Sort based on file size
  fL = sorted(fL, reverse=True, key=lambda d: d['size'])

  sys.exit(-1) 




# main guard
if __name__ == '__main__':
   main() 






