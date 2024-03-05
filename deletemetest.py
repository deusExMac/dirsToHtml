# Singleton class design

class someClass:
      loaded = False
      def __init__(self, a=1, b=2):
          
            
          print('\t\tExecuting init in base class with', a, b)
          
          self.c1 = a
          self.c2 = b
          self.loaded = True
          

class singleton(someClass):

      instance = None

      def __new__(cls, a=-66, b=-77):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            print('\tCreating instance')

        print('\tReturning instance')
        return cls.instance

      def __init__(self, a=-1, b=-42):
          print('\tCalling init in singleton with', a, b)
          super().__init__(a, b)



s1 = singleton()
#s1.a = 'sonia' 

s2 = singleton(88, 99)
#print(s2.a)
#s2.a = -222

s3 = singleton(110, 121)
print(s1.c1)
print(s1.c2)



#!/usr/bin/python

import sys
import os
import re
import signal

from pathlib import Path
from clrprint import *


from bloom_filter import BloomFilter



'''
from pynput import keyboard

# The key combination to check
COMBINATION = {keyboard.Key.cmd, keyboard.Key.ctrl}

# The currently active modifiers
current = set()


def on_press(key):
    if key in COMBINATION:
        current.add(key)
        if all(k in current for k in COMBINATION):
            print('All modifiers active!')
    if key == keyboard.Key.esc:
        listener.stop()


def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
'''    


showFiles = False
breakINTR = False

'''
def handler(signum):
   if signum == signal.SIGUSR1:
       print('user defined interrupt!')
       breakINTR = True

signal.signal(signal.SIGUSR1, handler)
'''



def compare( dir1, dir2, xP='' ):
    global   breakINTR

    # make absolute
    absDir1 = os.path.abspath(dir1)
    absDir2 = os.path.abspath(dir2)
    print(absDir1, absDir2)
    nonExistent = BloomFilter(max_elements=10000, error_rate=0.1)
    fsStats = {'nD':0, 'nDC':0, 'nDM':0, 'nDF':0, 'nF':0, 'nFC':0, 'nFM':0, 'nFF':0 }
    
    # traverse root directory, and list directories as dirs and files as files
    try:
          
      for root, dirs, files in os.walk(absDir1):
           
           
        if xP!= '' and re.search(xP, root):  
           continue

        if root == absDir1:
           clrprint(f'[SKIPPING] {root}', clr='purple')
           continue

        fsStats['nD'] += 1
        fsStats['nDC'] += 1
        # Parent path of current directory
        parentPath = Path(root).parent.absolute()
        print(root)
        print('\tChecking if parent path [', parentPath, '] in filter...', sep='', end='')
        if str(parentPath) in nonExistent:
           fsStats['nDM'] += 1 
           clrprint('[YES-Skipping]', clr='y')
           continue

        clrprint('[NO]', clr='o')
        
        # Get relative part           
        rp = os.path.relpath(root, absDir1)
        print(f'\t[RELATIVE PATH of {root} with {absDir1}]', rp)
        print('\t', absDir2 + os.sep + rp, end='')
        if not os.path.isdir(absDir2 + os.sep + rp):
           #print(root)
           clrprint(' [Does not exist]', clr='red')
           nonExistent.add( str(root) )
           clrprint('\t[Adding to bloomfilter]', root, clr='purple')
           fsStats['nDM'] += 1
        else:
              fsStats['nDF'] += 1  
              clrprint(' [Exist]', clr='green')
                  
        if showFiles:
           for file in files:
               print('   [f]', os.sep.join(path[1:]), '/', file, sep='')
               
    except KeyboardInterrupt:
           print('\n\nControl-C seen. Terminating.....')
           return(fsStats)
    except Exception as Ex:
           print('Got exception', str(Ex) )

           
    return(fsStats)



from  filecmp import dircmp

def diffDirs(dir1, dir2, shallow=True):
    result = dircmp(dir1, dir2)
    #result.report()
    return(result)
    
      
import os.path

def is_same(dir1, dir2):
    """
    Compare two directory trees content.
    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2)
    print(f'Comparison of {dir1} and {dir2}:')
    print('\tleft_only:', compared.left_only)
    print('\tright_only:', compared.right_only)
    print('\tcommon:', compared.common_dirs)
    
    if (compared.left_only or compared.right_only or compared.diff_files 
        or compared.funny_files):
        return False
      
    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
      
    return True










import keyboard
import time
from os.path import join
from filecmp import dircmp


def defaultDH(l=1, side='right', path='') -> None:
    """
      Default Directory Handler displaying only formatted side and path of Directories
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """
    print('\t'*l, f'[{l}][D] [{side}] {path}', sep='')



def defaultFH(l=1, side='right', path=''):
    """
      Default File Handler displaying only formatted side and path of Files
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """  
    print('\t'*l, f'[{l}][F] [{side}] {path}', sep='')






def customDirectoryHandler(l=1, side='right', path='') -> None:
    print('\t'*l, f'[{l}][{side}] {path}', sep='')






def matches(mF, fname) -> bool:
    """
      Returns if the file name matches pattern specified in mF
      
      :param mF: regular expression a file name must match. Empty string for no filter.
      :param fname: file name to check regular expression agains. NOTE: No full path expected
      :return: Boolean indicating if file name matches pattern
    """
    
    #print(f'matchfilter:{mF} filename:{fname}') 
    if mF == '' or mF is None:
       return(True)

    if re.search(mF, fname) is not None:
       return(True)
      
    return(False)  




def on_alt(event):
    if keyboard.is_pressed('ctrl'):
        print('\n\n\nCtrl + Alt pressed')
        input('Press any key to continue...>')



#
#
# Returns only the differences between two directories in terms of files and directories
# Seems to work. More testing needed though.
# 
#
def fsDiff(L_dir, R_dir, lvl=1, dirOnly=False, matchFilter='', dirHandler=defaultDH, fileHandler=defaultFH):

  """
       Traverses recursively directories and calculates the differences (in terms of directories and files) between
       two directories.
      
      :param L_dir: One directory path- left side
      :param fname: Second directory path - right side
      :param lvl: Current level of traversal
      :param dirOnly: If True calculates differences for directories only. Otherwise, also files are taken
      into consideration.
      :param matchFilter: regular expression directory and file names must match. Empty string indicates no filter.
      :param dirHandler: Function to call for each directory encountered
      :param fileHandler:Function to call for each file encountered 
      :return: tuple indicatins status, total objects matching, list of objects only in left side, list of objects only in right side
  """

  localTotal = 0
  prefix = '\t'*lvl
  
  print('\t'*lvl, f'{40*"+"}\n', '\t'*lvl, f'[L:{lvl}] Comparing\n', prefix, f'[{L_dir}]\n', prefix, 'to\n', prefix, f'[{R_dir}]\n', sep='')
  # TODO: is this correct/
  L_only, R_only = [], []
  try:  
    dcmp = dircmp(L_dir, R_dir)
    if dirOnly:
       L_only = [join(L_dir, f) for f in dcmp.left_only if  os.path.isdir( join(L_dir, f)  ) and matches(matchFilter, f)  ]
       R_only = [join(R_dir, f) for f in dcmp.right_only if os.path.isdir( join(R_dir, f)  ) and matches(matchFilter, f)]  
    else:       
       L_only = [join(L_dir, f) for f in dcmp.left_only if matches(matchFilter, f) ]
       R_only = [join(R_dir, f) for f in dcmp.right_only if matches(matchFilter, f)]


    # TODO: This is not correct. Recheck and redesign it   
    if dirHandler:  
       for d in L_only:
           if os.path.isdir(d):   
              dirHandler(lvl, 'left', d)
           else:
              fileHandler(lvl, 'left', d)
              
       for d in R_only:
           if os.path.isdir(d):   
              dirHandler(lvl, 'right', d)
           else:
              fileHandler(lvl, 'right', d)  
            


    # TODO: Check this...
    if (not L_only) and (not R_only):
       print('\t'*lvl + '[Same content].')   

    print('\t'*lvl + f'l_only={len(L_only)} r_only={len(R_only)} common={len(dcmp.common_dirs)}')
    localTotal = len(L_only) + len(R_only) + len(dcmp.common_dirs)
    
    # Handle directories having common names. I.e. traverse these and
    # find their differences
    for sub_dir in dcmp.common_dirs:
        dirHandler(lvl, 'common', join(L_dir, sub_dir))  
        s, lt, new_L, new_R = fsDiff(join(L_dir, sub_dir), join(R_dir, sub_dir), (lvl+1), dirOnly, matchFilter, dirHandler, fileHandler)
        L_only.extend(new_L)
        R_only.extend(new_R)
        print('\t'*lvl,  f'>> From level below {lt}', sep='')
        localTotal = localTotal + lt

    print('\t'*lvl + f'returning {localTotal}\n', '\t'*lvl, f'{40*"-"}', sep='')

    # TODO: This has issues...
    if keyboard.is_pressed("p"):
       input("Paused. Press any key to continue.")

       
    return 0, localTotal, L_only, R_only

  except KeyboardInterrupt as kI:
         #
         # Do a full/cascading unrolling. raising exceptions until
         # top level is reached; from which it is returned
         #
         print(f'\n\n[L:{lvl}] Interupted in {L_dir} {R_dir}. Terminating: Total:{localTotal}')
         if lvl > 1:
            raise kI
         else:
            return( -1, localTotal, L_only, R_only )  
         
          
          





#r = is_same("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects")
#print(r)

'''
try:      
   keyboard.on_press_key('alt', on_alt)
except Exception as kEx:
   print('Error hooking keypress handler:', str(kEx))
   time.sleep(3)
'''   
   
sts, t, a, b = fsDiff(L_dir="/Users/manolistzagarakis/users", R_dir="/Users/manolistzagarakis/users-NEW", lvl=1, dirOnly=False, matchFilter='')

#fsD = compare("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", '\.svn')
#clrprint(fsD, clr='green')

#dff = diffDirs("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", False)
#dff.report()
sys.exit(-2)









maxIter = 3
n = 0
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("/Users/manolistzagarakis/users/"):
    path = root.split(os.sep)
    #print(path[1:])
    #print('[D]', os.path.abspath(os.sep.join(path[1:])) )
    
    #root = root.replace('exampleDir/', '')
    print('[', root, ']')
    print('\t[RELATIVE] ::', os.path.relpath(root, "/Users/manolistzagarakis") ) 
    print('\t[ABSOLUTE] ::', os.path.abspath(root))
    print('\t[D]', dirs)
    print('\t[F]', files)
    #break
    #print((len(path) - 1) * '---', os.path.basename(root))
    if showFiles:
      for file in files:
        #print(len(path) * '---', file)
         print('   [f]', os.sep.join(path[1:]), '/', file, sep='')

    print(n*'*')
    n += 1
    if n >= 3:
       break   

