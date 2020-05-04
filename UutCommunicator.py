import os
import sys
import re
import GlobalData
from Helper import Helper

class UutCommunicator(object):
  
  def __init__(self, helper):
    self.helper = helper
    pass
  #======================================================================================
  #   raw data Process from Base RTX8665
  #======================================================================================

  # get raw data content by length
  def getContentRawDataByLength(self, inputData):
    # get data length
    iLength = 0;
    search_pattern  = re.compile(r'\[(\d+)\]:')
    reResult = re.search(search_pattern, inputData)
    if reResult:
      iLength = int(reResult.group(1))
    if iLength <= 0:
      return False
    # get data content
    outputData = ""
    reResult  = re.findall(r'0x(\w+)', inputData)
    for dataIndex, rawData in enumerate(reResult):
      outputData += rawData
      if dataIndex == iLength - 1:
        break
    return outputData

  # get raw data content
  def getHexContentRawData(self, inputData):
    outputData = ""
    search_pattern  = re.compile(r'0x(\d+)')
    reResult = re.search(search_pattern, inputData)
    if reResult:
      outputData = reResult.group(1)
    return outputData

  #======================================================================================
  #   Implement "Set" information commands to Base RTX8665
  #======================================================================================
  # set EAI Port Server Name
  def setEaiServerPortName(self, serverPortName):
    match_pattern = re.compile("SET PTMAILOPTIONS")
    search_pattern = re.compile("( --name=)(\w*)")
    newContent = ""
    with open(GlobalData.SetPtMailOptionFileName, 'r') as If:
      for line in If:
        if re.search(match_pattern, line):
          if re.search(search_pattern, line):
            newContent += search_pattern.sub(" --name=" + serverPortName, line)
          else:
            newContent += line.strip() + " --name=" + serverPortName + "\n"
        else:
          newContent += line
    If.close()
    Of = open(GlobalData.SetPtMailOptionFileName,'w')
    Of.write(newContent)
    self.helper.logPrint ("set EAI Port Server: " + serverPortName)
    Of.close()

  # clear all of certificates
  def clearPersistentCerificates(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION \
      or GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      self.helper.logPrint ("clear all of certificates")
      fh = os.popen("ClearPersistentCertifiates.bat")
      strData = fh.read()
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Clear Persistent Cerificates: " + strData)
        fh.close()
        return False
      self.helper.logPrint ("Data from Base: " + strData)
      fh.close()
    return True

  # reset base
  def baseReset(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION \
      or GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      fh = os.popen("Reset.bat")
      fh.close()
      self.helper.logPrint ("Reset Base")
    return True


  # Load Certificate and private key
  def LoadCertificatePrivateKey(self, certFile, PrivateKeyFile):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION \
      or GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      self.helper.logPrint ("Load Certificate Private Key: " + certFile + " " + PrivateKeyFile)
      strCmd = "LoadCert.bat " + certFile + " " + PrivateKeyFile
      fh = os.popen(strCmd)
      strData = fh.read()
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Load Certificate Private Key: \n" + strData)
        fh.close()
        return False
      self.helper.logPrint ("Data: " + strData)
      fh.close()
    return True

  # Load Certificate
  def LoadCertificate(self, certFile):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_PRODUCTION \
      or GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_UUT :
      self.helper.logPrint ("Load Certificate: " + certFile)
      strCmd = "LoadCertOnly.bat " + certFile
      fh = os.popen(strCmd)
      strData = fh.read()
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Load Certificate: \n" + strData)
        fh.close()
        return False
      self.helper.logPrint ("Data: " + strData)
      fh.close()
    return True
  #======================================================================================
  #   Implement "Get" information commands from Base RTX8665
  #======================================================================================
  # get Base ID
  def getBaseId(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "FFFFFFFF"
    else:
      self.helper.logPrint ("Get BaseId")
      fh = os.popen("GetId.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get BaseId: " + strData)
        fh.close()
        return False
      strContent  = self.getContentRawDataByLength(strData)
      self.helper.logPrint ("Output for GetId.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # get Serial Number
  def getSerialNumber(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "TESTING1234"
    else:
      self.helper.logPrint ("Get Serial Number")
      fh = os.popen("getSerialNumber.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get SerialNumber: " + strData)
        fh.close()
        return False
      strContent  = bytes.fromhex(self.getContentRawDataByLength(strData)).decode('utf-8')
      self.helper.logPrint("Output for GetSerialNumber.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # get Frequency
  def getFreq(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "0"
    else:
      self.helper.logPrint ("Get Frequency")
      fh = os.popen("GetFreq.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get Frequency: " + strData)
        fh.close()
        return False
      strContent  = self.getHexContentRawData(strData)
      self.helper.logPrint ("Output for GetFreq.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # get Base MacAddress
  def getMacAddress(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "FFFFFFFFFFFF"
    else:
      self.helper.logPrint ("Get Base MacAddress")
      fh = os.popen("GetMac.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get Mac Address: " + strData)
        fh.close()
        return False
      strContent  = self.getContentRawDataByLength(strData)
      self.helper.logPrint ("Output for GetMac.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # get Certifiate MD5 checksum
  def getCertMd5(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "0123456789ABCDEF0123456789ABCDEF"
    else:
      self.helper.logPrint ("Get Certifiate MD5 checksum")
      fh = os.popen("GetManuCertMd5.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get Cert Md5: " + strData)
        fh.close()
        return False
      strContent  = self.getContentRawDataByLength(strData)
      self.helper.logPrint ("Output for GetManuCertMd5.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # get Private Key MD5 checksum
  def getPrivateKeyMd5(self, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "0123456789ABCDEF0123456789ABCDEF"
    else:
      self.helper.logPrint ("Get Private Key MD5 checksum")
      fh = os.popen("GetManuKeyMd5.bat")
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get Private Key Md5: " + strData)
        fh.close()
        return False
      strContent  = self.getContentRawDataByLength(strData)
      self.helper.logPrint ("Output for GetManuKeyMd5.bat:" + strContent)
      fh.close()
    output[0] = strContent
    return True

  # for Public Key

  #  get Link Date
  def getLinkDate(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      return True
    self.helper.logPrint ("Get Link Date")
    fh = os.popen("GetLinkDate.bat")
    strData = fh.read()
    self.helper.logPrint ("Data from Base: " + strData)
    if strData.find("ERROR") >=0 :
      self.helper.logPrint ("**Calculate Certificate Key: " + strData)
      fh.close()
      return False
    self.helper.logPrint ("Get Link Date SUCCESS: " +strData)
    fh.close()
    return True


  #  Calculate CertKey
  def calcCertKey(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      return True
    self.helper.logPrint ("Calculate Certificate Key")
    fh = os.popen("ManufactoryCalcCertKeys.bat")
    strData = fh.read()
    self.helper.logPrint ("Data from Base: " + strData)
    if strData.find("ERROR") >=0 :
      self.helper.logPrint ("**Calculate Certificate Key: " + strData)
      fh.close()
      return False
    elif strData.find("BUSY") >=0 :
      self.helper.logPrint ("**Calculate Certificate Key: " + strData)
      fh.close()
      return False
    self.helper.logPrint ("Calculate Certificate Key SUCCESS")
    fh.close()
    return True


  #  Certificate Key polling
  def certKeyPolling(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      return True
    #self.helper.logPrint ("Certificate Key polling")
    fh = os.popen("ManufactoryPollKeysReady.bat")
    strData = fh.read()
    #self.helper.logPrint ("Data from Base: " + strData)
    if strData.find("RSS_SUCCESS") >=0 :
      self.helper.logPrint ("Certificate Key polling SUCCESS")
      fh.close()
      return True
    elif strData.find("ERROR") >=0 :
      self.helper.logPrint ("**Certificate Key polling: " + strData)
      fh.close()
      return False
    self.helper.logPrint ("**Certificate Key polling: " + strData)
    fh.close()
    return False

  #  Get Public Key
  # result 
  # 0 = true
  # 1 = false
  # 2 = bad arguments

  def getPublicKey(self, lineNumber, output):
    strContent  = ""
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM:
      strContent = "Testing: " + str(lineNumber)
    else:
      self.helper.logPrint ("Get Public Key")
      fh = os.popen("ManufactoryGetPublicKey.bat " + str(hex(lineNumber)))
      strData = fh.read()
      self.helper.logPrint ("Data from Base: " + strData)
      if strData.find("ERROR") >=0 :
        self.helper.logPrint ("**Get Public Key: " + strData)
        fh.close()
        return 1
      if strData.find("BAD_ARGUMENTS") >=0 and lineNumber != 0:
        self.helper.logPrint ("**Get Public Key: Done")
        fh.close()
        return 2
      strContent  = bytes.fromhex(self.getContentRawDataByLength(strData)).decode('utf-8')
      self.helper.logPrint ("Output for ManufactoryGetPublicKey.bat:" + strContent)
      fh.close()
    output[0] += strContent
    return 0
    
pass
