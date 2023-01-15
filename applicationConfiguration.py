import os
import os.path

import argparse
import configparser


class applicationConfiguration:

      def __init__(self, cfgParamSpec=None, cfgFile=None, cmdArgs=None, cfgFileArgParamName='config'):
          self.configFile = cfgFile
          self.cmdArguments = cmdArgs
          self.sectionParameters = cfgParamSpec
          
          
          self.cmdArguments = self.parseArguments()
          #print( self.cmdArguments )
          
          #print('Reading file', self.cmdArguments.get(cfgFileArgParamName, 'xxx') )
          self.config = self.defaultConfiguration()
          if os.path.exists(self.cmdArguments.get(cfgFileArgParamName, 'xxx')):
             self.config = configparser.RawConfigParser(allow_no_value=True)
             self.config.read(self.cmdArguments.get(cfgFileArgParamName, 'xxx'))
          else:
              print('File does not exist:', self.cmdArguments.get(cfgFileArgParamName, 'xxx'))
          




      def  defaultConfiguration(self, sectionList=None):          
           sL = sectionList
           if sL is None:
              sL = list( self.getSections() )

           c = configparser.RawConfigParser(allow_no_value=True) 
           for s in sL:
               c.add_section(s)

           return(c)


      def getSections(self, paramSpec=None):

          if paramSpec is None:
             paramSpec = self.sectionParameters
             
          scts = set()
          for p in paramSpec:
              scts.add( p['param']['section'].lower() )

          return(scts)    



      def getParameterByName( self, paramName ):
          for p in self.sectionParameters:
              if p['param']['paramname'].lower() == paramName.lower():
                 return(p['param']['section'])

          return(None)      



      def printConfiguration(self, cfg=None):
          if cfg is None:
             cfg = self.config

          if cfg is None:
              print('No configuration object.') 
              return
                    
          for s in cfg.sections():
              print("Section [", s, "]", sep="")
              for key, value in cfg[s].items():
                  print( "\t-", key, "=", value)




      def overwriteConfiguration(self):

          argSections = list( self.getSections() )
          for k,v in self.cmdArguments.items():
              print('Checking', k, v)
              if v.strip() == '':
                 continue
                
              sectionName = self.getParameterByName(k)
              #print('Checking section', sectionName) 
              if sectionName.lower() not in self.config.sections():
                 #print('Adding section', sectionName) 
                 self.config.add_section(sectionName)
                 
              self.config.set(sectionName, k, v)
              




      def parseArguments(self):

          seenSwitches = []
          seenParamNames = []
          cmdArgs = argparse.ArgumentParser(description='Command line arguments', add_help=False)
          #d1 = {'param': {'section' : 'sectionname', 'datatype': 'bool', 'switch': '-k', 'paramname':'someuniquename', 'default':''}}
          for p in self.sectionParameters:
               # Check if switch and/or paramname has been seen again i.e.
               # is duplicate. Duplicate switches/parameter names are fatal and
               # argument parsing stops.
               if p['param']['switch'] in seenSwitches:
                  raise Exception("Dublicate switch", p['param']['switch'], "detected.") 

               if p['param']['paramname'].lower() in seenSwitches:
                  raise Exception("Dublicate parameter name", p['param']['switch'], "detected.") 
                
               cmdArgs.add_argument(p['param']['switch'], '--' + p['param']['paramname'], default=p['param']['default'])
               seenSwitches.append( p['param']['switch'] )
               seenParamNames.append(p['param']['paramname'].lower() )
               
          try:
              knownArgs, unknownArgs = cmdArgs.parse_known_args()
              args = vars( knownArgs )
              return(args)
          except Exception as argEx:
              print('Argument error:', str(argEx))
              return( None )

