#global variables
import datetime

#Operation Mode
OPERATION_MODE_PRODUCTION                   = 0
OPERATION_MODE_DEBUG_UUT                    = 1
OPERATION_MODE_DEBUG_CESIUM                 = 2

#return codes
RETURN_CODE_NO_ERROR                        = 0
RETURN_CODE_NO_CONFIG_FILE                  = 1
RETURN_CODE_INPUT_PARM_ERROR                = 2
RETURN_CODE_UUT_COMMUNICATION_ERROR         = 3
RETURN_CODE_REMOTE_COMMUNICATION_ERROR      = 4

#Time delay
BASE_RESET_DELAY_TIME                       = 20
BASE_POWER_UP_DELAY_TIME                    = 20
BASE_MAX_POLLING_DELAY_TIME                 = 240

ToolBeginingTime        = datetime.datetime.now()
ConfigFileName          = 'config.ini'
LogFileName             = 'log.txt'
EaiPortServerName       = ''
CesiumServerUrl         = ''
SetPtMailOptionFileName = "SetPtMailOptions.bat"
OperationMode           = OPERATION_MODE_PRODUCTION



#for certificate request
serialNumber          = ""
productId             = ""
machineName           = ""
userName              = ""
requestType           = ""
certificateMethod     = ""
publicKey             = ""
commonNameHeader      = ""
commonName            = ""
sudiEnabled           = True
publicKeySize         = 0
urlQualifier          = ""

#for certificate response
rootCertificate                   = ""
raEncryptionCertificate           = ""
privateKey                        = ""
code                              = ""
x509Certificate                   = ""
subCaCertificate                  = ""
clientCertificateSigningRequest   = ""
raSigningCertificate              = ""



