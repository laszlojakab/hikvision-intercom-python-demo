import platform
from hcnetsdk import HCNetSDK, NET_DVR_DEVICEINFO_V30, NET_DVR_DEVICEINFO_V30, NET_DVR_CONTROL_GATEWAY
from ctypes import c_byte, sizeof, byref


HCNetSDK.NET_DVR_Init()
HCNetSDK.NET_DVR_SetValidIP(0, True)

device_info = NET_DVR_DEVICEINFO_V30()

address = "192.168.0.1".encode('utf-8')
user = "admin".encode('utf-8')
password = "pass12345".encode('utf-8')

if platform.uname()[0] == "Windows":
    user_id = HCNetSDK.NET_DVR_Login_V30(
        address, 8000, user, password, device_info)
if platform.uname()[0] == "Linux":
    # suppressing passing device_info on Linux as it is causing crashing
    # (see https://github.com/laszlojakab/hikvision-intercom-python-demo/issues/2)
    user_id = HCNetSDK.NET_DVR_Login_V30(
        address, 8000, user, password)

if (user_id < 0):
    print(
        f"NET_DVR_Login_V30 failed, error code = {HCNetSDK.NET_DVR_GetLastError()}")
    HCNetSDK.NET_DVR_Cleanup()
    exit(1)


gw = NET_DVR_CONTROL_GATEWAY()
gw.dwSize = sizeof(NET_DVR_CONTROL_GATEWAY)
gw.dwGatewayIndex = 1
gw.byCommand = 1 # opening command
gw.byLockType = 0 # this is normal lock not smart lock
gw.wLockID = 0 # door station
gw.byControlSrc = (c_byte * 32)(*[97,98,99,100]) # anything will do but can't be empty
gw.byControlType = 1

print(gw.dwSize)
result = HCNetSDK.NET_DVR_RemoteControl(user_id, 16009, byref(gw), gw.dwSize)

print("unlockreusult", result)
if result == 0:
    print(HCNetSDK.NET_DVR_GetLastError())

HCNetSDK.NET_DVR_Logout_V30(user_id)
HCNetSDK.NET_DVR_Cleanup()
