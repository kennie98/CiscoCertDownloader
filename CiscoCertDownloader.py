import json
import requests
import sys
import datetime
import GlobalData
from Helper import Helper
from UutCommunicator import UutCommunicator
from RestApiProcessor import RestApiProcessor
import time
import urllib3

# ------------------------------
# main program body
# ------------------------------
class CiscoCertDownloader(object):
    
  def __init__(self):
    self.helper = Helper()
    self.uutCommunicator = UutCommunicator(self.helper)
    self.restApiProcessor = RestApiProcessor(self.helper)
    pass
# ------------------------------------------------------------------------------------------------------------------------    
  def baseReset(self):
    listReult = [""]
    self.uutCommunicator.baseReset()
    for i in range(GlobalData.BASE_RESET_DELAY_TIME):
      time.sleep(1)
      self.helper.logPrint (("Reset try: ", i+1))
      if self.uutCommunicator.getBaseId(listReult):
        # add delay time after reset for UUT stabilizing 
        time.sleep(3)
        return True
    return False
# ------------------------------------------------------------------------------------------------------------------------
  def uutConnectionCheck(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION or\
      GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      listReult = [""]
      self.helper.logPrint('UUT Ready')
      for i in range(GlobalData.BASE_POWER_UP_DELAY_TIME):
        time.sleep(1)
        self.helper.logPrint (("Reset try: ", i+1))
        if self.uutCommunicator.getBaseId(listReult):
          return True
      return False
    return True
# ------------------------------------------------------------------------------------------------------------------------
  def uutClearCerificates(self):
    result = self.uutConnectionCheck()
    if result is False:
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR

    result = self.uutCommunicator.clearPersistentCerificates()
    if result is False:   #error encountered when running ClearPersistentCertification.bat
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR

    result = self.baseReset()
    if result is False:
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR
    return result

# ------------------------------------------------------------------------------------------------------------------------
  def uutCalCertKeyPolling(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION or\
      GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      self.helper.logPrint('UUT Certificate Polling')
      for i in range(GlobalData.BASE_MAX_POLLING_DELAY_TIME):
        time.sleep(1)
        self.helper.logPrint (("Polling: ", i+1))
        if self.uutCommunicator.certKeyPolling():
          return True
      return False
    return True

# ------------------------------------------------------------------------------------------------------------------------
  def uutPublicKeyGeneration(self):
    sectionTime = self.helper.logSectionBegin('Public Key Generation')
    strPublicKey = [""]
    if self.uutCommunicator.getLinkDate() == False:
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR

    if self.uutCommunicator.calcCertKey() == False:
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR
    
    if self.uutCalCertKeyPolling() == False:
      return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR
    self.helper.logSectionEnd('Public Key Generation', sectionTime)
    sectionTime = self.helper.logSectionBegin('Get Public Key')

    for i in range(1,32):
      # result 
      # 0 = true
      # 1 = false
      # 2 = bad arguments
      subResult = self.uutCommunicator.getPublicKey(i, strPublicKey)
      if subResult == 1:
        return GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR
      elif subResult == 2:
        break
    GlobalData.publicKey = strPublicKey[0].replace(chr(0), '')
    self.helper.logPrint(GlobalData.publicKey)
    self.helper.logSectionEnd('Get Public Key', sectionTime)
    return GlobalData.RETURN_CODE_NO_ERROR

# ------------------------------------------------------------------------------------------------------------------------
  def endProcess(self, returnCode):
    
    self.helper.logPrint('Return: ' + str(returnCode))
    self.helper.logProgramEnd(GlobalData.ToolBeginingTime)
    #log copy to config location 
    self.helper.backupDatalog(GlobalData.serialNumber, str(GlobalData.ToolBeginingTime.strftime('%Y%m%d%H%M%S')))
    
    # remember to remove the RAMDRIVE afterwards.
    self.helper.removeRamDrive()
  
    # print return code
    print(returnCode)
    return returnCode

# ------------------------------------------------------------------------------------------------------------------------
  def run(self):

    ret_val = GlobalData.RETURN_CODE_NO_ERROR

    # log the current time
    GlobalData.ToolBeginingTime = datetime.datetime.now()
    
    # read in configuration file
    self.helper.processConfigFile(GlobalData.ConfigFileName)
        
    # check syntax
    if len(sys.argv) == 2:
      GlobalData.EaiPortServerName = sys.argv[1]
      GlobalData.OperationMode = GlobalData.OPERATION_MODE_PRODUCTION
    elif len(sys.argv) == 3:
      if sys.argv[2].lower() == 'uut':
        GlobalData.EaiPortServerName = sys.argv[1]
        GlobalData.OperationMode = GlobalData.OPERATION_MODE_DEBUG_UUT
      elif sys.argv[2].lower() == 'cesium':
        GlobalData.EaiPortServerName = sys.argv[1]
        GlobalData.OperationMode = GlobalData.OPERATION_MODE_DEBUG_CESIUM
      else:
        return self.endProcess(GlobalData.RETURN_CODE_INPUT_PARM_ERROR)
    else:
      self.helper.logPrint('Syntax: CiscoCertDownloader.exe [EAI_PORT_SERVER_NAME]')
      return self.endProcess(GlobalData.RETURN_CODE_INPUT_PARM_ERROR)

    # create RAMDRIVE environment
    self.helper.removeRamDrive()
    self.helper.createRamDrive()
    self.helper.copyBatchFilesToRamDrive()
    self.helper.copyOpenSslFilesToRamDrive()
    self.helper.enterRamDrive()

    # Process Begin
    processTime = self.helper.logProgramBegin()
    # UUT Init
    sectionTime = self.helper.logSectionBegin('UUT Init')
    self.uutCommunicator.setEaiServerPortName(GlobalData.EaiPortServerName)
    # get the parameters needed to create the request
    # TBD: need to handle the exception case
    result = self.uutClearCerificates()
    if result is False:
      return self.endProcess(GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR)
    self.helper.logSectionEnd("UUT Init", sectionTime)

    # UUT Infomation Collection
    sectionTime = self.helper.logSectionBegin('UUT Information Collection')
    listReult = [""]
    if self.uutCommunicator.getSerialNumber(listReult) == False:
      return self.endProcess(GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR)
    else:
      GlobalData.serialNumber = listReult[0].upper()
    listReult = [""]
    if self.uutCommunicator.getMacAddress(listReult) == False:
      return self.endProcess(GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR)
    else:
      GlobalData.commonName     = GlobalData.commonNameHeader + "-SEP" + listReult[0].upper()
    self.helper.logSectionEnd('UUT Information Collection', sectionTime)

    # Get Public Key
    sectionResult  = self.uutPublicKeyGeneration()
    if sectionResult  != GlobalData.RETURN_CODE_NO_ERROR:
      return self.endProcess(sectionResult)

    # Certificate Request
    sectionTime = self.helper.logSectionBegin('Certificate Request')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION \
      or GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      # send the request to the Cesium server
      self.helper.logPrint("send the request to the Cesium server")
      response = requests.post(GlobalData.CesiumServerUrl,
                               data=self.restApiProcessor.getCerRequestJson(),
                               allow_redirects=True,
                               verify=False,
                               headers={'Content-type': 'application/json'},
                               cert=self.helper.cert_path)

      ret_val = self.helper.checkHttpStatusError(response.status_code)
      if ret_val == GlobalData.RETURN_CODE_NO_ERROR:
        self.helper.logPrint(
          "Cersium server communication succeeded, HTTP Status and Error Code: " + str(response.status_code))
        self.helper.saveX509Cert(response.json()['root']['x509_certificate'])
      else:
        self.helper.logPrint(
          "Cersium server communication failed, HTTP Status and Error Code: " + str(response.status_code))
        return self.endProcess(GlobalData.RETURN_CODE_REMOTE_COMMUNICATION_ERROR)
    
    self.helper.logSectionEnd('Certificate Request', sectionTime)   

    # Certificate Upload To Base
    sectionTime = self.helper.logSectionBegin('Certificate Upload To Base')
    self.helper.convertCertToDer()
    result = self.uutConnectionCheck()
    if result is False:
      return self.endProcess(GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR)

    result = self.uutCommunicator.LoadCertificate("cert.der") 
    if result is False:
      return self.endProcess(GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR)

    self.helper.logSectionEnd('Certificate Upload To Base', sectionTime) 

    return self.endProcess(GlobalData.RETURN_CODE_NO_ERROR)


pass

# ==============================
# Main Entry Point
# ==============================
if __name__ == '__main__':
  ciscoCertDownloader = CiscoCertDownloader()
  ciscoCertDownloader.run()
