import os ,sys #
configfile ='/ql/data/config/config.sh'#
configfile1 ='./config.sh'#
configdict ={}#
def get_configdict ():#
    if os .path .exists (configfile ):#
        with open (configfile ,'r',encoding ='utf8')as O0OOOOOOO0OOO00OO :#
            O00000OOO00O00O0O =O0OOOOOOO0OOO00OO .readlines ()#
            if O00000OOO00O00O0O is None :#
                sys .exit ()#
            for OO0O0O0O0O0OO00O0 in O00000OOO00O00O0O :#
                OO0O0O0O0O0OO00O0 =str (OO0O0O0O0O0OO00O0 ).replace ('\n','').replace ('\'','',-1 ).replace ('\"','',-1 )#
                if OO0O0O0O0O0OO00O0 ==''or OO0O0O0O0O0OO00O0 is None :#
                    continue #
                if OO0O0O0O0O0OO00O0 .strip ()[0 ]=='#
                    continue #
                if 'export'in OO0O0O0O0O0OO00O0 .strip ():#
                    OO0O0O0O0O0OO00O0 =OO0O0O0O0O0OO00O0 .replace ('export','',-1 )#
                OO0O0O0O0O0OO00O0 =OO0O0O0O0O0OO00O0 .split ('=',1 )#
                if len (OO0O0O0O0O0OO00O0 )<2 :#
                    continue #
                OO00O00OOOO0OOO00 =OO0O0O0O0O0OO00O0 [0 ].strip ()#
                OOOOO000O0O0OO000 =OO0O0O0O0O0OO00O0 [1 ].strip ()#
                configdict [OO00O00OOOO0OOO00 ]=OOOOO000O0O0OO000 #
    elif os .path .exists (configfile1 ):#
        with open (configfile1 ,'r',encoding ='utf8')as O0OOOOOOO0OOO00OO :#
            O00000OOO00O00O0O =O0OOOOOOO0OOO00OO .readlines ()#
            if O00000OOO00O00O0O is None :#
                sys .exit ()#
            for OO0O0O0O0O0OO00O0 in O00000OOO00O00O0O :#
                OO0O0O0O0O0OO00O0 =str (OO0O0O0O0O0OO00O0 ).replace ('\n','').replace ('\'','',-1 ).replace ('\"','',-1 )#
                if OO0O0O0O0O0OO00O0 ==''or OO0O0O0O0O0OO00O0 is None :#
                    continue #
                if OO0O0O0O0O0OO00O0 .strip ()[0 ]=='#
                    continue #
                if 'export'in OO0O0O0O0O0OO00O0 .strip ():#
                    OO0O0O0O0O0OO00O0 =OO0O0O0O0O0OO00O0 .replace ('export','',-1 )#
                OO0O0O0O0O0OO00O0 =OO0O0O0O0O0OO00O0 .split ('=',1 )#
                if len (OO0O0O0O0O0OO00O0 )<2 :#
                    continue #
                OO00O00OOOO0OOO00 =OO0O0O0O0O0OO00O0 [0 ].strip ()#
                OOOOO000O0O0OO000 =OO0O0O0O0O0OO00O0 [1 ].strip ()#
                configdict [OO00O00OOOO0OOO00 ]=OOOOO000O0O0OO000 #
    else :#
        print ('未找到配置文件！！，请检查配置文件路径与文件名')#
get_configdict ()#
def getconfig (OO00OO0OOO000O00O ):#
    return configdict [OO00OO0OOO000O00O ]#
def setconfig (O0OO00O0000000O0O ,O0O0OOO00000OO0O0 ):#
    configdict [O0OO00O0000000O0O ]=O0O0OOO00000OO0O0 #
def change_param_value_tofile (OOOOOOO0O0OO0000O ,OO0OOOO00O0OO0OO0 ):#
    if os .path .exists (configfile ):#
        O0OO0OOO000O0OOOO =[]#
        with open (configfile ,'r',encoding ='utf8')as OOOOOO0O000000OOO :#
            OO0OO0OOO0O0OO0O0 =OOOOOO0O000000OOO .readlines ()#
            for O0OOO0OO00000O00O in OO0OO0OOO0O0OO0O0 :#
                if OOOOOOO0O0OO0000O in O0OOO0OO00000O00O .strip ():#
                    O00000000OO0O00O0 =getconfig (OOOOOOO0O0OO0000O )#
                    O0OOO0OO00000O00O =O0OOO0OO00000O00O .replace (O00000000OO0O00O0 ,OO0OOOO00O0OO0OO0 )#
                    O0OO0OOO000O0OOOO .append (O0OOO0OO00000O00O )#
                else :#
                    O0OO0OOO000O0OOOO .append (O0OOO0OO00000O00O )#
        if len (O0OO0OOO000O0OOOO )>0 :#
            with open (configfile ,'r',encoding ='utf8')as O0OOOO0OOOOO0O0OO :#
                O0OOOO0OOOOO0O0OO .writelines (O0OO0OOO000O0OOOO )#
    elif os .path .exists (configfile1 ):#
        O0OO0OOO000O0OOOO =[]#
        with open (configfile1 ,'r',encoding ='utf8')as OOOOOO0O000000OOO :#
            OO0OO0OOO0O0OO0O0 =OOOOOO0O000000OOO .readlines ()#
            for O0OOO0OO00000O00O in OO0OO0OOO0O0OO0O0 :#
                if OOOOOOO0O0OO0000O in O0OOO0OO00000O00O :#
                    O00000000OO0O00O0 =getconfig (OOOOOOO0O0OO0000O )#
                    print ('替换前：',O0OOO0OO00000O00O )#
                    O0OOO0OO00000O00O =O0OOO0OO00000O00O .replace (O00000000OO0O00O0 ,OO0OOOO00O0OO0OO0 )#
                    print ('替换后：',O0OOO0OO00000O00O )#
                    O0OO0OOO000O0OOOO .append (O0OOO0OO00000O00O )#
                else :#
                    O0OO0OOO000O0OOOO .append (O0OOO0OO00000O00O )#
        if len (O0OO0OOO000O0OOOO )>0 :#
            with open (configfile1 ,'w',encoding ='utf8')as O0OOOO0OOOOO0O0OO :#
                O0OOOO0OOOOO0O0OO .writelines (O0OO0OOO000O0OOOO )#
        else :#
            print ('未找到配置文件')#
def getcookies (O0OOO00O0O00OO00O ):#
    OO0O0O000OO0000O0 =[]#
    O000O000OO000OOO0 =''#
    OOOO00O0OO00O0000 =configdict [O0OOO00O0O00OO00O ]#
    OOOO00O0OO00O0000 =str (OOOO00O0OO00O0000 ).strip ().split ('@')#
    return OOOO00O0OO00O0000 #
def dict_to_str (O0O00OOOO0O00OO0O ):#
    O0O00O000OOO00O0O =''#
    if O0O00OOOO0O00OO0O :#
        if isinstance (O0O00OOOO0O00OO0O ,dict ):#
            for OOOO0O0O0000OO0OO ,O00OOO0OOOOO000OO in O0O00OOOO0O00OO0O .items ():#
                O0OO0OO0000OOO000 =f'%s: %s \n'%(OOOO0O0O0000OO0OO ,O00OOO0OOOOO000OO )#
                O0O00O000OOO00O0O +=O0OO0OO0000OOO000 #
        else :#
            return O0O00OOOO0O00OO0O #
    return O0O00O000OOO00O0O 