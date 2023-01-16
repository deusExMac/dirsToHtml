import os
import os.path

import argparse
import configparser


class applicationConfiguration:

      # Singleton
      #__shared_state = {}
      
      def __init__(self, argSpec=None, cfgFile=None, cmdArgs=None, configFileArgument='config', defaultConfigFile='default.conf'):

          # Singleton
          #self.__dict__ = self.__shared_state
            
          self.configFile = cfgFile
          self.passedArguments = cmdArgs
          self.argumentSpecification = argSpec
          
          
          self.passedArguments = self.parseArguments()

          self.config = self.defaultConfiguration()
          if self.passedArguments is not None:
             if os.path.exists(self.passedArguments.get(configFileArgument, defaultConfigFile)):
                self.config = configparser.RawConfigParser(allow_no_value=True)
                self.config.read(self.passedArguments.get(configFileArgument, defaultConfigFile))
             else:
                 print('File does not exist:', self.passedArguments.get(configFileArgument, defaultConfigFile))
          
          self.overwriteConfiguration()



      def  defaultConfiguration(self, sectionList=None):          
           sL = sectionList
           if sL is None:
              sL = list( self.getSpecificationSections() )
              

           if not sL:
              return(None)
            
           c = configparser.RawConfigParser(allow_no_value=True) 
           for s in sL:
               c.add_section(s)
           
           return(c)


      def getSpecificationSections(self, paramSpec=None):

          if paramSpec is None:
             paramSpec = self.argumentSpecification

          if self.argumentSpecification is None:
             return(())
            
          scts = set()
          for p in paramSpec:
              scts.add( p['param']['section'].lower() )

          return(scts)    



      def getParameterByName( self, paramName ):
          for p in self.argumentSpecification:
              if p['param']['paramname'].lower() == paramName.lower():
                 return(p)

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

          if self.argumentSpecification is None:
              return(None)
            
          for k,v in self.passedArguments.items():
              
                              
              argSpec = self.getParameterByName(k)
              if argSpec is None:
                 print('No such specification found:', k)
                 raise Exception("No argument specification for", k)

              if isinstance(v, str) and v.strip() == '':
                 continue
                 
              if argSpec['param']['section'].lower() not in self.config.sections():
                 self.config.add_section(argSpec['param']['section'])

              if argSpec['param']['datatype'].lower() == 'boolean':
                 if self.passedArguments[k]:  
                    self.config.set(argSpec['param']['section'], k, 'True') 
              else:    
                 self.config.set(argSpec['param']['section'], k, v)
              




      def parseArguments(self):

          if self.argumentSpecification is None:
             return(None)
            
          seenSwitches = []
          seenParamNames = []
          cmdArgs = argparse.ArgumentParser(description='Command line arguments', add_help=False)
          #d1 = {'param': {'section' : 'sectionname', 'datatype': 'bool', 'switch': '-k', 'paramname':'someuniquename', 'default':''}}
          for p in self.argumentSpecification:
               # Check if switch and/or paramname has been seen again i.e.
               # is duplicate. Duplicate switches/parameter names are fatal and
               # argument parsing stops.
               if p['param']['switch'] in seenSwitches:
                  raise Exception("Dublicate switch", p['param']['switch'], "detected.") 

               if p['param']['paramname'].lower() in seenSwitches:
                  raise Exception("Dublicate parameter name", p['param']['switch'], "detected.") 

               if p['param']['datatype'].lower() == 'boolean':
                  cmdArgs.add_argument(p['param']['switch'], '--' + p['param']['paramname'], action='store_true') 
               else:    
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

