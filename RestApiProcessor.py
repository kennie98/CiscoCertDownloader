import json
from Helper import Helper
import GlobalData

class RestApiProcessor(object):
  
  def __init__(self, helper):
    self.helper = helper
    pass

  # for REST API Processor
  @staticmethod
  def clearBaseInfo():
    GlobalData.serialNumber    = ""
    GlobalData.productId       = ""
    GlobalData.machineName     = ""
    GlobalData.userName        = ""
    GlobalData.requestType     = ""
    GlobalData.certificateMethod  = ""
    GlobalData.commonName      = ""
    GlobalData.sudiEnabled     = True
    GlobalData.publicKeySize   = 0
    GlobalData.urlQualifier    = ""
  @staticmethod



  def dummyBaseInfo():
    GlobalData.serialNumber    = "FLR18090035"
    GlobalData.publicKey       = "-----BEGIN CERTIFICATE REQUEST-----\nMIICRTCCAS0CAQAwADCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANA0\nOLc4rhuGQskvMTErFhvJnurS2Kz9r9rF5jFcru4aGDEs2zrK8CmnkVMHhx7xtsUD\naZWZB72dIvqTK9/13K7u/FmPHXZIclmKomxHmD9ke4fCGmibVcGOEenhFoGLIb+1\ncqh31XACQsPHxXZ/8hRdilS1ys+0S7HXvL/vaI4sVLSpAlTOxTYJW7l91NLFTC4V\nePm9c22ROZGgefdNpOICGIE5XlOTVkbwsKrOpnx78h4k4xSQi6Um9A9NDer6i++U\nlai+baod4zmIe8AGX5i9ACR3bT7yzIcd8+LywXvHh6RLi2oTWXFH6+boADvBrd/G\nAl/PwWj945Y2LgxVijMCAwEAAaAAMA0GCSqGSIb3DQEBCwUAA4IBAQCxbi9JjEQ3\namRuiZ2AipHFvXteSn2hgJcyF0fn8BhoI1DkS3GCWc7P87wJoaHT0UntzJt9goC1\nD1MTp67dksWrnAdAgtNOSfdUxrqHiZxWBSRw+ww/OcAQeoVgUynG8IuJvj9bC84O\nVOYQsVUZk/1v+kQV+sQWp7p99XGVWIAQtL3psoK5c5ebXdB+hK8Gdfwfl5W/mNZX\n3bWbJ0OWyo+cWoPbDq24rCgk6+rC64INXbdDsFGgwG0jEAXj5DxEtbWboHEmAD2w\n0DxSj+vT8PBzgZgSS9VJn3kYcGjvbbnk0naa7us9kwUanCU9yfHDwqkIQeehb+Ya\noJM3U66ZphZ2\n-----END CERTIFICATE REQUEST-----\n"
    GlobalData.commonName      = "CP-6826-SEP00087B1573AF"

  def getCerRequestJson(self):
    if GlobalData.OperationMode == GlobalData.OPERATION_MODE_DEBUG_CESIUM :
      self.dummyBaseInfo()
    
    request = {
      "root":
      {
        "serial_number":        GlobalData.serialNumber,
        "product_id":           GlobalData.productId,
        "machine_name":         GlobalData.machineName,
        "user_name":            GlobalData.userName,
        "request_type":         GlobalData.requestType,
        "certificate_method":   GlobalData.certificateMethod,
        "public_key":           GlobalData.publicKey,
        "common_name":          GlobalData.commonName,
        "sudi_enabled":         GlobalData.sudiEnabled,
        "public_key_size":      GlobalData.publicKeySize,
        "url_qualifier":        GlobalData.urlQualifier
      }
    }
    strJson = json.dumps(request)
    self.helper.logPrint(strJson)
    return strJson

  def respDataProcess(self, inputData):
    message                   = inputData["root"]["message"]
    if message == "SUCCESS":
      GlobalData.rootCertificate           = inputData["root"]["root_certificate"]
      GlobalData.raEncryptionCertificate   = inputData["root"]["ra_encryption_certificate"]
      GlobalData.privateKey                = inputData["root"]["private_key"]
      GlobalData.code                      = inputData["root"]["code"]
      GlobalData.x509Certificate           = inputData["root"]["x509_certificate"]
      GlobalData.subCaCertificate          = inputData["root"]["sub_ca_certificate"]
      GlobalData.clientCertificateSigningRequest    = inputData["root"]["client_certificate_signing_request"]
      GlobalData.raSigningCertificate      = inputData["root"]["ra_signing_certificate"]
      return True
    else:
      self.helper.logPrint(message)
      return False


pass