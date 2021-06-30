from hcnetsdk import HCNetSDK, NET_DVR_DEVICEINFO_V30, NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_SETUPALARM_PARAM, fMessageCallBack, COMM_ALARM_V30, COMM_ALARM_VIDEO_INTERCOM, NET_DVR_VIDEO_INTERCOM_ALARM, NET_DVR_ALARMINFO_V30, ALARMINFO_V30_ALARMTYPE_MOTION_DETECTION, VIDEO_INTERCOM_ALARM_ALARMTYPE_DOORBELL_RINGING, VIDEO_INTERCOM_ALARM_ALARMTYPE_DISMISS_INCOMING_CALL, VIDEO_INTERCOM_ALARM_ALARMTYPE_TAMPERING_ALARM, VIDEO_INTERCOM_ALARM_ALARMTYPE_DOOR_NOT_CLOSED, COMM_UPLOAD_VIDEO_INTERCOM_EVENT, NET_DVR_VIDEO_INTERCOM_EVENT, VIDEO_INTERCOM_EVENT_EVENTTYPE_UNLOCK_LOG, VIDEO_INTERCOM_EVENT_EVENTTYPE_ILLEGAL_CARD_SWIPING_EVENT, NET_DVR_UNLOCK_RECORD_INFO
from ctypes import POINTER, cast, c_char_p, c_byte
from pprint import pprint


def callback(command: int, alarmer_pointer, alarminfo_pointer, buffer_length, user_pointer):
    if (command == COMM_ALARM_V30):
        alarminfo_alarm_v30: NET_DVR_ALARMINFO_V30 = cast(
            alarminfo_pointer, POINTER(NET_DVR_ALARMINFO_V30)).contents
        if (alarminfo_alarm_v30.dwAlarmType == ALARMINFO_V30_ALARMTYPE_MOTION_DETECTION):
            print(f"Motion detected")
        else:
            print(
                f"COMM_ALARM_V30, unhandled dwAlarmType: {alarminfo_alarm_v30.dwAlarmType}")
    elif(command == COMM_ALARM_VIDEO_INTERCOM):
        alarminfo_alarm_video_intercom: NET_DVR_VIDEO_INTERCOM_ALARM = cast(
            alarminfo_pointer, POINTER(NET_DVR_VIDEO_INTERCOM_ALARM)).contents        
        if (alarminfo_alarm_video_intercom.byAlarmType == VIDEO_INTERCOM_ALARM_ALARMTYPE_DOORBELL_RINGING):
            print("Doorbell ringing")
        elif (alarminfo_alarm_video_intercom.byAlarmType == VIDEO_INTERCOM_ALARM_ALARMTYPE_DISMISS_INCOMING_CALL):
            print("Call dismissed")            
        elif (alarminfo_alarm_video_intercom.byAlarmType == VIDEO_INTERCOM_ALARM_ALARMTYPE_TAMPERING_ALARM):
            print("Tampering alarm")
        elif (alarminfo_alarm_video_intercom.byAlarmType == VIDEO_INTERCOM_ALARM_ALARMTYPE_DOOR_NOT_CLOSED):
            print("Door not closed")
        else:
            print(
                f"COMM_ALARM_VIDEO_INTERCOM, unhandled byAlarmType: {alarminfo_alarm_video_intercom.byAlarmType}")
    elif(command == COMM_UPLOAD_VIDEO_INTERCOM_EVENT):
        alarminfo_upload_video_intercom_event: NET_DVR_VIDEO_INTERCOM_EVENT = cast(
            alarminfo_pointer, POINTER(NET_DVR_VIDEO_INTERCOM_EVENT)).contents
        if (alarminfo_upload_video_intercom_event.byEventType == VIDEO_INTERCOM_EVENT_EVENTTYPE_UNLOCK_LOG):          
            print(f"Unlocked by: {list(alarminfo_upload_video_intercom_event.uEventInfo.struUnlockRecord.byControlSrc)}")
        elif (alarminfo_upload_video_intercom_event.byEventType == VIDEO_INTERCOM_EVENT_EVENTTYPE_ILLEGAL_CARD_SWIPING_EVENT):
            print(f"Illegal card swiping")
        else:
            print(
                f"COMM_ALARM_VIDEO_INTERCOM, unhandled byEventType: {alarminfo_upload_video_intercom_event.byEventType}")
    else:
        print(f"Unhandled command: {command}")


HCNetSDK.NET_DVR_Init()
HCNetSDK.NET_DVR_SetValidIP(0, True)

login_info = NET_DVR_USER_LOGIN_INFO()
login_info.sDeviceAddress = "192.168.1.206".encode('utf-8')
login_info.sUserName = "admin".encode("utf-8")
login_info.sPassword = "Password123".encode("utf-8")
login_info.wPort = 8000

device_info = NET_DVR_DEVICEINFO_V40()

user_id = HCNetSDK.NET_DVR_Login_V40(login_info, device_info)

if (user_id < 0):
    print(
        f"NET_DVR_Login_V40 failed, error code = {HCNetSDK.NET_DVR_GetLastError()}")
    HCNetSDK.NET_DVR_Cleanup()
    exit(1)

alarm_param = NET_DVR_SETUPALARM_PARAM()
alarm_param.dwSize = 20
alarm_param.byLevel = 1
alarm_param.byAlarmInfoType = 1
alarm_param.byFaceAlarmDetection = 1

alarm_handle = HCNetSDK.NET_DVR_SetupAlarmChan_V41(user_id, alarm_param)

if (alarm_handle < 0):
    print(
        f"NET_DVR_SetupAlarmChan_V41 failed, error code = {HCNetSDK.NET_DVR_GetLastError()}")
    HCNetSDK.NET_DVR_Logout_V30(user_id)
    HCNetSDK.NET_DVR_Cleanup()
    exit(2)

message_callback = fMessageCallBack(callback)
HCNetSDK.NET_DVR_SetDVRMessageCallBack_V50(0, message_callback, user_id)

input("Press Enter to exit...\n")

HCNetSDK.NET_DVR_CloseAlarmChan_V30(alarm_handle)
HCNetSDK.NET_DVR_Logout_V30(user_id)
HCNetSDK.NET_DVR_Cleanup()
