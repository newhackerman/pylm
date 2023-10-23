import random #
import hashlib #
from base import *#
import time ,sys #
import requests as req #
import multiprocessing as mp #
from costtime import time_counts #
import sendNotify #
'''
 作者：newhackerman
 日期：2023-10-19
 功能 	海信爱家 积分换实物
 抓包：搜https://careapi.oclean.com/mall/v1/CheckIn/GetCheckInfo - header:Cookie
 变量格式：export hsajck='Cookie'
 定时：1天2次
 cron: 59 59 9,20 * * *
 无邀请码
 用于青龙，其它平台未测试
 [task_local]

 [rewrite_local]

 [MITM]

 '''#
session =req .session ()#
def starttask (O0O00OO00O00OOOOO ,O0O000OOO0000000O ):#
    OO0OO0O000O00OOOO =tasks (O0O00OO00O00OOOOO ,O0O000OOO0000000O )#
    OO0OO0O000O00OOOO .runtasklist ()#
class tasks ():#
    def __init__ (OOO0OO000OO0OOO00 ,OOOOOOOOOO0O000OO ,OO00OOO0O00O0O000 ):#
        OOO0OO000OO0OOO00 .times =0 #
        OO0O0O0000O0O00O0 ='账号 %s:'%(OO00OOO0O00O0O000 )#
        OOO0OO000OO0OOO00 .resultdict ={}#
        OOO0OO000OO0OOO00 .resultdict ['说明']='积分换实物'#
        OOO0OO000OO0OOO00 .resultdict [OO0O0O0000O0O00O0 ]=''#
        OOO0OO000OO0OOO00 .Cookie =OOOOOOOOOO0O000OO #
        OOO0OO000OO0OOO00 .headers ={'Cookie':OOO0OO000OO0OOO00 .Cookie ,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/8447','referer':'https://cps.hisense.com/static/game_sign.shtml?code=74f51fd29cea445e9b95eb0dd14fba40','accept-encoding':'gzip, deflate, br','accept-language':'zh-CN,zh;q=0.9'}#
    @time_counts #
    def runtasklist (OOO0O00O0OO000O00 ):#
        OOO0000OOO000O0OO =OOO0O00O0OO000O00 .hsajck_check_sign ()#
        time .sleep (0.2 )#
        OOO0O00O0OO000O00 .hsajck_sign ()#
        OOO0O00O0OO000O00 .hsajck_get_dds ()#
        time .sleep (30 )#
        OOO0O00O0OO000O00 .hsajck_gamesubmit ()#
        time .sleep (30 )#
        OOO0O00O0OO000O00 .hsajck_gamesubmit ()#
        print (OOO0O00O0OO000O00 .resultdict )#
        sendNotify .send ('海信爱家:',OOO0O00O0OO000O00 .resultdict )#
    def hsajck_check_sign (O00O0OO0O00O00OOO ):#
        OO0O000OO000OO00O =f"https://cps.hisense.com/customerAth/activity-manage/activityUser/noLoginCheck"#
        O00O00000O0O000OO ={"activityUrl":"https://cps.hisense.com/static/game_sign.shtml?code=74f51fd29cea445e9b95eb0dd14fba40"}#
        try :#
            OO0OO000OOO000OOO =session .post (url =OO0O000OO000OO00O ,headers =O00O0OO0O00O00OOO .headers ,json =O00O00000O0O000OO ,timeout =5 )#
            if OO0OO000OOO000OOO .status_code ==200 :#
                O00O0000O0000O0O0 =OO0OO000OOO000OOO .json ()#
                if O00O0000O0000O0O0 .get ('data'):#
                    O00O0OO0O00O00OOO .resultdict ['是否已签']=O00O0000O0000O0O0 ['data']['noLoginCheck']#
                else :#
                    return #
            else :#
                print (OO0OO000OOO000OOO .content .decode ('utf8'))#
                O00O0OO0O00O00OOO .hsajck_sign ()#
        except BaseException as OOOOO0O0O00OOO000 :#
            print (OOOOO0O0O00OOO000 )#
    def hsajck_sign (OO0OOOO000O0O00OO ):#
        O00000O00OOOO0000 =f"https://cps.hisense.com/customerAth/activity-manage/activityUser/participate"#
        OO00000OOO0OOOOO0 ={"code":"74f51fd29cea445e9b95eb0dd14fba40"}#
        try :#
            O0000OO000OO00OO0 =session .post (url =O00000O00OOOO0000 ,headers =OO0OOOO000O0O00OO .headers ,json =OO00000OOO0OOOOO0 ,timeout =5 )#
            if O0000OO000OO00OO0 .status_code ==200 :#
                OOO0OO0O0O0000OO0 =O0000OO000OO00OO0 .json ()#
                if OOO0OO0O0O0000OO0 .get ('resultCode')=='00000':#
                    OO0OOOO000O0O00OO .resultdict ['签到']=OOO0OO0O0O0000OO0 ['data']['resultMsg']#
                else :#
                    OO0OOOO000O0O00OO .resultdict ['签到']=OOO0OO0O0O0000OO0 ['data']['resultMsg']#
                    print ('签到:',O0000OO000OO00OO0 .content .decode ('utf8'))#
                O000O000OOOOO000O ='https://cps.hisense.com/customerAth/activity-manage/activityUser/getActivityInfo?code=74f51fd29cea445e9b95eb0dd14fba40'#
                try :#
                    O0000OO000OO00OO0 =session .get (url =O000O000OOOOO000O ,headers =OO0OOOO000O0O00OO .headers ,timeout =5 )#
                except :#
                    pass #
            else :#
                print (O0000OO000OO00OO0 .content .decode ('utf8'))#
        except BaseException as O000O0OO00O0OO00O :#
            print (O000O0OO00O0OO00O )#
    def hsajck_get_dds (O00OOO0O0O0OO0000 ):#
        OOO0O0OOOO0O0000O =f"https://cps.hisense.com/customerAth/activity-manage/activityUser/getActivityInfo?code=a55ca53d96bd43be81c0df7ced7ef2b0"#
        try :#
            O0OOOO0O0000O000O =session .get (url =OOO0O0OOOO0O0000O ,headers =O00OOO0O0O0OO0000 .headers ,timeout =5 )#
            if O0OOOO0O0000O000O .status_code ==200 :#
                OOOOO0OOOOO00O0OO =O0OOOO0O0000O000O .json ()#
                if OOOOO0OOOOO00O0OO .get ('resultCode')=='00000':#
                    O00OOO0O0O0OO0000 .resultdict ['开始游戏']=OOOOO0OOOOO00O0OO .get ('resultMsg')#
                else :#
                    O00OOO0O0O0OO0000 .resultdict ['开始游戏']=OOOOO0OOOOO00O0OO .get ('resultMsg')#
            else :#
                O00OOO0O0O0OO0000 .resultdict ['开始游戏']=O0OOOO0O0000O000O .content .decode ('utf8')#
                print (O0OOOO0O0000O000O .content .decode ('utf8'))#
        except BaseException as OO0OO00OOOOO000O0 :#
            print (OO0OO00OOOOO000O0 )#
    def hsajck_gamesubmit (OO0O0O000OO00OO00 ):#
        O0OOO0O0OO0OO0O0O =random .randint (6 ,20 )*10 #
        OOO00O00OOOOO0OOO =('a55ca53d96bd43be81c0df7ced7ef2b0'+str (O0OOO0O0OO0OO0O0O )).encode ('utf8')#
        OO0O00O00000OO0OO =hashlib .md5 ()#
        OO0O00O00000OO0OO .update (OOO00O00OOOOO0OOO )#
        O00OOOOO00O000OOO =OO0O00O00000OO0OO .hexdigest ()#
        O00OOO00OO0000O00 =f"https://cps.hisense.com/customerAth/activity-manage/activityUser/participate"#
        OOOOO0OOO000O0O00 ={"code":"a55ca53d96bd43be81c0df7ced7ef2b0","gameScore":O0OOO0O0OO0OO0O0O ,"gameSignature":O00OOOOO00O000OOO }#
        try :#
            OO0O0000OOO0000O0 =session .post (url =O00OOO00OO0000O00 ,headers =OO0O0O000OO00OO00 .headers ,json =OOOOO0OOO000O0O00 ,timeout =5 )#
            if OO0O0000OOO0000O0 .status_code ==200 :#
                O00OO0OO0OOOO000O =OO0O0000OOO0000O0 .json ()#
                if O00OO0OO0OOOO000O .get ('resultCode')=='00000':#
                    OO0O0O000OO00OO00 .resultdict ['获得积分']=O00OO0OO0OOOO000O ['data']['obtainScore']#
                else :#
                    OO0O0O000OO00OO00 .resultdict ['获得积分']=OO0O0000OOO0000O0 .content .decode ('utf8')#
            else :#
                print (OO0O0000OOO0000O0 .content .decode ('utf8'))#
        except BaseException as O00OO00OOO0O00OO0 :#
            print (O00OO00OOO0O00OO0 )#
if __name__ =='__main__':#
    cookies =getcookies ('hsajck')#
    if len (cookies )>5 :#
        print ('请勿一次性跑太多账号，造成服端与本机压力！')#
    i =0 #
    if cookies is not None :#
        for cookie1 in cookies :#
            i +=1 #
            process =mp .Process (target =starttask ,args =(cookie1 ,i ,))#
            process .start ()#
            if i %5 ==0 :#
                time .sleep (120 )#
        sys .exit ()#
    else :#
        print ('未配置cookies')#
        sys .exit (0 )#
