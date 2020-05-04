import os
import re
import shutil
import json
import subprocess
import GlobalData
import datetime

class Helper(object):
  tag_server_url        = 'CESIUM_SERVER_URL'
  tag_req_product_id    = 'REQ_PRODUCT_ID'
  tag_req_request_type  = 'REQ_REQUEST_TYPE'
  tag_req_user_name     = 'REQ_USER_NAME'
  tag_req_certificate_method = 'REQ_CERTIFICATE_METHOD'
  tag_req_common_name   = 'REQ_COMMON_NAME'
  tag_req_sudi_enable   = 'REQ_SUDI_ENABLE'
  tag_req_machine_name  = 'REQ_MACHINE_NAME'
  tag_req_public_key_size = 'REQ_PUBLIC_KEY_SIZE'
  tag_req_url_qualifier = 'REQ_URL_QUALIFIER'

  tag_ramdisktool_loc = 'RAMDISKTOOL_LOC'
  tag_ramdisktool_create_argv = 'RAMDISKTOOL_CREATE_ARGV'
  tag_ramdisktool_remove_argv = 'RAMDISKTOOL_REMOVE_ARGV'
  tag_ramdisktool_drive_letter = 'RAMDISKTOOL_DRV_LETTER'
  tag_openssl_loc = 'OPSSLTOOL_LOC'
  tag_prodtest_loc = 'PRODTEST_LOC'
  tag_cert_path = 'CERTIFICATE_LOC'

  tag_datalog_path = 'DATALOG_LOC'

  tag_csr_country_name = 'CSR_COUNTRY_NAME'
  tag_csr_state_name = 'CSR_STATE_NAME'
  tag_csr_org_name = 'CSR_ORG_NAME'
  tag_csr_org_unit_name = 'CSR_ORG_UNIT_NAME'

  ramdisktool       = 'imdisk.exe'
  ram_drive_create_cmd = ''
  ram_drive_remove_cmd = ''
  ram_drive_letter  = ''

  openssl         = 'openssl.exe'
  openssl_loc     = ''
  prodtest_loc    = ''
  prodtest_dll_loc = ''
  prodtest_bat_loc = ''
  cert_path       = ''

  datalog_path = ''

  csr_content = ''
  csr_country_name = ''
  csr_state_name = ''
  csr_org_name = ''
  csr_org_unit_name = ''

  gen_key_pair_cmd = \
    'openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048'
  get_public_key_cmd = \
    'openssl rsa -pubout -in private_key.pem -out public_key.pem'
  convert_public_key_to_csr_cmd = \
    'openssl req -new -key private_key.pem -out public_key.csr -subj '
  convert_cert_to_der_cmd = \
    'openssl x509 -in cert.cer -outform der -out cert.der'
  get_cert_md5_cmd = \
    'openssl dgst -md5 cert.der > cert-md5.txt'
  convert_pkcs8_key_to_der_cmd = \
    'openssl pkcs8 -v1 PBE-SHA1-3DES -topk8 -in private_key.pem -outform DER -out pkcs8.key -nocrypt'
  convert_pkcs1_key_to_der_cmd = \
    'openssl pkcs8 -topk8 -inform PEM -outform DER -in pkcs1key.pem -out pkcs8.der -nocrypt'
  get_key_md5_cmd = \
    'openssl dgst -md5 pkcs8.key > key-md5.txt'

  # ------------------------------
  # process the configuration file
  # ------------------------------
  def processConfigFile(self, config_file):
    server_url              = re.compile(r'^'+self.tag_server_url+'\s*\=\=\s*')
    req_product_id          = re.compile(r'^'+self.tag_req_product_id+'\s*\=\=\s*')
    req_request_type        = re.compile(r'^'+self.tag_req_request_type+'\s*\=\=\s*')
    req_user_name           = re.compile(r'^'+self.tag_req_user_name+'\s*\=\=\s*')
    req_certificate_method  = re.compile(r'^'+self.tag_req_certificate_method+'\s*\=\=\s*')
    req_common_name         = re.compile(r'^'+self.tag_req_common_name+'\s*\=\=\s*')
    req_sudi_enable         = re.compile(r'^'+self.tag_req_sudi_enable+'\s*\=\=\s*')
    req_machine_name        = re.compile(r'^'+self.tag_req_machine_name+'\s*\=\=\s*')
    req_public_key_size     = re.compile(r'^'+self.tag_req_public_key_size+'\s*\=\=\s*')
    req_url_qualifier       = re.compile(r'^'+self.tag_req_url_qualifier+'\s*\=\=\s*')

    re_ramdisktool_loc         = re.compile(r'^'+self.tag_ramdisktool_loc+'\s*\=\=\s*')
    re_ramdisktool_create_argv = re.compile(r'^'+self.tag_ramdisktool_create_argv+'\s*\=\=\s*')
    re_ramdisktool_remove_argv = re.compile(r'^'+self.tag_ramdisktool_remove_argv+'\s*\=\=\s*')
    re_ramdisktool_drive_letter= re.compile(r'^'+self.tag_ramdisktool_drive_letter+'\s*\=\=\s*')

    re_openssl_loc = re.compile(r'^' + self.tag_openssl_loc + '\s*\=\=\s*')
    re_prodtest_loc = re.compile(r'^' + self.tag_prodtest_loc + '\s*\=\=\s*')
    re_cert_path = re.compile(r'^' + self.tag_cert_path + '\s*\=\=\s*')

    re_datalog_path = re.compile(r'^' + self.tag_datalog_path + '\s*\=\=\s*')

    re_csr_country_name = re.compile(r'^' + self.tag_csr_country_name + '\s*\=\=\s*')
    re_csr_state_name = re.compile(r'^' + self.tag_csr_state_name + '\s*\=\=\s*')
    re_csr_org_name = re.compile(r'^' + self.tag_csr_org_name + '\s*\=\=\s*')
    re_csr_org_unit_name = re.compile(r'^' + self.tag_csr_org_unit_name + '\s*\=\=\s*')

    ramdisktool_loc = ''
    ramdisktool_create_argv = ''
    ramdisktool_remove_argv = ''

    with open(config_file, 'r') as cf:
      for line in cf.readlines():
        if re.search(server_url, line):
          GlobalData.CesiumServerUrl = line.split('==')[-1].strip()
        elif re.search(req_product_id, line):
          GlobalData.productId = line.split('==')[-1].strip()
        elif re.search(req_request_type, line):
          GlobalData.requestType = line.split('==')[-1].strip()
        elif re.search(req_user_name, line):
          GlobalData.userName = line.split('==')[-1].strip()
        elif re.search(req_certificate_method, line):
          GlobalData.certificateMethod = line.split('==')[-1].strip()
        elif re.search(req_common_name, line):
          GlobalData.commonNameHeader = line.split('==')[-1].strip()
        elif re.search(req_sudi_enable, line):
          GlobalData.sudiEnabled = False
          configData = line.split('==')[-1].strip().lower()
          if configData == 'true':
            GlobalData.sudiEnabled = True
        elif re.search(req_machine_name, line):
          GlobalData.machineName = line.split('==')[-1].strip()
        elif re.search(req_public_key_size, line):
          GlobalData.publicKeySize = int(line.split('==')[-1].strip())
        elif re.search(req_url_qualifier, line):
          GlobalData.urlQualifier = line.split('==')[-1].strip()
        elif re.search(re_ramdisktool_loc, line):
          ramdisktool_loc = line.split('==')[-1].strip()
        elif re.search(re_ramdisktool_create_argv, line):
          ramdisktool_create_argv = line.split('==')[-1].strip()
        elif re.search(re_ramdisktool_remove_argv, line):
          ramdisktool_remove_argv = line.split('==')[-1].strip()
        elif re.search(re_ramdisktool_drive_letter, line):
          self.ram_drive_letter = line.split('==')[-1].strip()
        elif re.search(re_openssl_loc, line):
          self.openssl_loc = line.split('==')[-1].strip()
        elif re.search(re_prodtest_loc, line):
          self.prodtest_loc = line.split('==')[-1].strip()
        elif re.search(re_cert_path, line):
          self.cert_path = line.split('==')[-1].strip()
        elif re.search(re_datalog_path, line):
          self.datalog_path = line.split('==')[-1].strip()
        elif re.search(re_csr_country_name, line):
          self.csr_country_name = line.split('==')[-1].strip()
        elif re.search(re_csr_state_name, line):
          self.csr_state_name = line.split('==')[-1].strip()
        elif re.search(re_csr_org_name, line):
          self.csr_org_name = line.split('==')[-1].strip()
        elif re.search(re_csr_org_unit_name, line):
          self.csr_org_unit_name = line.split('==')[-1].strip()
    cf.close()

    self.prodtest_dll_loc = self.prodtest_loc+'\\RtxProdTestDll'
    self.prodtest_bat_loc = self.prodtest_loc+'\\bat'

    if ramdisktool_create_argv != '' and ramdisktool_remove_argv != '':
      self.ram_drive_create_cmd = ramdisktool_loc+'\\'+self.ramdisktool+' '+ramdisktool_create_argv+' -m '+self.ram_drive_letter+': >tmp'
      self.ram_drive_remove_cmd = ramdisktool_loc+'\\'+self.ramdisktool+' '+ramdisktool_remove_argv+' -m '+self.ram_drive_letter+': >tmp'

  # ------------------------------
  # get certificate path
  # ------------------------------
  def getCertPath(self):
    return self.cert_path

  # ------------------------------
  # save to log file
  # ------------------------------
  @staticmethod
  def logPrint(s):
    with open(GlobalData.LogFileName, 'a') as Of:

      t = datetime.datetime.now()
      timestamp = str(t.strftime('%Y/%m/%d %H:%M:%S'))
      # log the current time
      Of.write('[' + timestamp + ']\t')
      Of.write(str(s)+'\n')
    Of.close()
  
  @staticmethod  
  def logSectionBegin(s):
    with open(GlobalData.LogFileName, 'a') as Of:
      t = datetime.datetime.now()
      Of.write('BEGIN\t====' + str(s)+'====\n')
    Of.close()
    return t

  @staticmethod
  def logSectionEnd(s, beginTime):
    with open(GlobalData.LogFileName, 'a') as Of:
      t = datetime.datetime.now()
      sectionTime= t - beginTime
      timestamp = str(sectionTime)
      Of.write('END\t====' + str(s)+ '====\tSection Time(' + timestamp + ')' + '\n')
    Of.close()

  @staticmethod  
  def logProgramBegin():
    with open(GlobalData.LogFileName, 'a') as Of:
      t = datetime.datetime.now()
      Of.write('BEGIN\n')
    Of.close()
    return t

  @staticmethod
  def logProgramEnd(beginTime):
    with open(GlobalData.LogFileName, 'a') as Of:
      t = datetime.datetime.now()
      sectionTime= t - beginTime
      timestamp = str(sectionTime)
      Of.write('END\tTotal Time(' + timestamp + ')' + '\n')
    Of.close()



  # ------------------------------
  # check HTTP Status code
  # ------------------------------
  @staticmethod
  def checkHttpStatusError(status_code):
    ret_val = {
      302: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      303: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      304: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      307: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      308: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      400: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      401: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      403: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      404: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      405: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      409: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      410: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      411: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      412: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      413: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      416: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      429: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      500: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      502: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
      503: GlobalData.RETURN_CODE_UUT_COMMUNICATION_ERROR,
    }
    return ret_val.get(status_code, GlobalData.RETURN_CODE_NO_ERROR)

  # ------------------------------
  # create RAM drive
  # ------------------------------
  def createRamDrive(self):
    if os.path.exists((self.ram_drive_letter+':\\')) is False:
      os.system(self.ram_drive_create_cmd)
    #self.logPrint('RAM drive: '+self.ram_drive_letter+' created')

  # ------------------------------
  # remove RAM drive
  # ------------------------------
  def removeRamDrive(self):
    #return # for debug
    if os.path.exists((self.ram_drive_letter+':\\')) is True:
      os.system(self.ram_drive_remove_cmd)
    #self.logPrint('RAM drive: ' +self.ram_drive_letter + ' removed')

  # ------------------------------
  # enter RAM Drive
  # ------------------------------
  def enterRamDrive(self):
    os.chdir(self.ram_drive_letter+':\\')

  # ------------------------------
  # make directory
  # ------------------------------
  def _mkdir_in_ramdrive(self, dir):
    os.system('mkdir '+self.ram_drive_letter + ':\\'+dir)

  # ------------------------------
  # copy file
  # ------------------------------
  def _copy_file(self, filename, src_dir , tgt_dir='.'):
    shutil.copy(src_dir + '\\' + filename, self.ram_drive_letter + ':\\'+tgt_dir)

  # ------------------------------
  # Backup datalog file
  # ------------------------------
  def backupDatalog(self, inputSerialNumber, inputTime):
    if inputSerialNumber == "":
      return

    backupName = inputSerialNumber + '_' + inputTime + '.txt'
    os.rename('log.txt', backupName)

    if os.path.exists(self.datalog_path) is False:
      os.system('mkdir '+ self.datalog_path)

    shutil.move(backupName, self.datalog_path)

  # ------------------------------
  # copy batch files to ram drive
  # ------------------------------
  def copyBatchFilesToRamDrive(self):
    dirpath = self.ram_drive_letter+':\\RtxProdTestDll'
    if os.path.exists(dirpath) is False:
      self._mkdir_in_ramdrive('RtxProdTestDll')
    self._copy_file('RtxProdTest.dll', self.prodtest_dll_loc, 'RtxProdTestDll')
    self._copy_file('PtMail.exe', self.prodtest_bat_loc)
    self._copy_file('SetPtMailOptions.bat', self.prodtest_bat_loc)
    self._copy_file('getSerialNumber.bat', self.prodtest_bat_loc)
    self._copy_file('GetMac.bat', self.prodtest_bat_loc)
    self._copy_file('LoadCert.bat', self.prodtest_bat_loc)
    self._copy_file('CalcManuCertKeyMd5.bat', self.prodtest_bat_loc)
    self._copy_file('GetManuCertMd5.bat', self.prodtest_bat_loc)
    self._copy_file('GetManuKeyMd5.bat', self.prodtest_bat_loc)
    self._copy_file('GetId.bat', self.prodtest_bat_loc)
    self._copy_file('ClearPersistentCertifiates.bat', self.prodtest_bat_loc)
    self._copy_file('GetFreq.bat', self.prodtest_bat_loc)
    self._copy_file('Reset.bat', self.prodtest_bat_loc)
    self._copy_file('SetManuCertAndKey.bat', self.prodtest_bat_loc)
    self._copy_file('Bin2Ascii.exe', self.prodtest_bat_loc)
    self._copy_file('LoadCertOnly.bat', self.prodtest_bat_loc)
    # for Public Key
    self._copy_file('ManufactoryCalcCertKeys.bat', self.prodtest_bat_loc)
    self._copy_file('ManufactoryGetPublicKey.bat', self.prodtest_bat_loc)
    self._copy_file('ManufactoryPollKeysReady.bat', self.prodtest_bat_loc)
    self._copy_file('GetLinkDate.bat', self.prodtest_bat_loc)

  # ------------------------------
  # copy openSSL files to ram drive
  # ------------------------------
  def copyOpenSslFilesToRamDrive(self):
    self._copy_file('openssl.exe', self.openssl_loc)
    self._copy_file('openssl.cnf', '.\\3Party\\openssl')

  # ------------------------------
  # openSSL related functions
  # ------------------------------
  @staticmethod
  def openSslInit():
    os.system('set OPENSSL_CONF=openssl.cnf')

  @staticmethod
  def run_without_screen_output(cmd):
    subprocess.call(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

  def packCsrContent(self):
    csr_content = '/C='+self.csr_country_name+'/ST='+self.csr_state_name+\
                  '/O='+self.csr_org_name+'/OU='+self.csr_org_unit_name+'/CN='+GlobalData.commonName
    return csr_content

  def genKeyPair(self):
    self.openSslInit()
    self.run_without_screen_output(self.gen_key_pair_cmd)

  def getPublicKey(self):
    self.openSslInit()
    self.run_without_screen_output(self.get_public_key_cmd)

  def convertPublicKeyToCsr(self):
    self.openSslInit()
    #self.run_without_screen_output(self.convert_public_key_to_csr_cmd+'\"'+self.packCsrContent()+'\"')
    os.system(self.convert_public_key_to_csr_cmd+'\"'+self.packCsrContent()+'\"')

  def convertCertToDer(self):
    self.openSslInit()
    self.run_without_screen_output(self.convert_cert_to_der_cmd)

  def getCertMd5(self):
    self.openSslInit()
    self.run_without_screen_output(self.get_cert_md5_cmd)

  def convertPkcs1KeyToDer(self):
    self.openSslInit()
    self.run_without_screen_output(self.convert_pkcs1_key_to_der_cmd)

  def convertPkcs8KeyToDer(self):
    self.openSslInit()
    self.run_without_screen_output(self.convert_pkcs8_key_to_der_cmd)

  def getKeyMd5(self):
    self.openSslInit()
    self.run_without_screen_output(self.get_key_md5_cmd)

  def saveX509Cert(self, x509_cert):
    with open('cert.cer', 'w') as f:
      f.write(x509_cert)
    f.close()

  def savePkcs1Key(selfself, pkcs1_key):
    with open('pkcs1key.pem', 'w') as f:
      f.write(pkcs1_key)
    f.close()

  def copyCertFile(self):
    self._copy_file('cert.txt', self.prodtest_loc)

pass

if __name__ == '__main__':
  helper = Helper()
  helper.processConfigFile('config.ini')
  helper.removeRamDrive()
  helper.createRamDrive()
  helper.copyBatchFilesToRamDrive()
  helper.copyOpenSslFilesToRamDrive()

  #test code
  helper._copy_file('cert.txt', '.')

  helper.enterRamDrive()
  helper.genKeyPair()
  helper.getPublicKey()

  GlobalData.commonName = "CP6826-SEP00087B1573AF"
  helper.convertPublicKeyToCsr()

  # test code
  with open('cert.txt', 'r') as If:
    s =''.join(line.strip() for line in If)
    s = re.sub(r'\'', r'"', s)
    with open('cert.cer', 'w') as f:
      f.write(json.loads(s)['root']['x509_certificate'])
    f.close()

  helper.convertCertToDer()
  helper.getCertMd5()
  helper.convertPkcs8KeyToDer()
  helper.getKeyMd5()

  #helper.removeRamDrive()
