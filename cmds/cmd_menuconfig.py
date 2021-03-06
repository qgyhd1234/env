import os
import argparse
from vars import Import, Export
'''menuconfig for system configuration'''
import platform

# make rtconfig.h from .config

def mk_rtconfig(filename):
    try:
        config = file(filename)
    except:
        print 'open .config failed'
        return

    rtconfig = file('rtconfig.h', 'w')
    rtconfig.write('#ifndef RT_CONFIG_H__\n')
    rtconfig.write('#define RT_CONFIG_H__\n\n')

    empty_line = 1

    for line in config:
        line = line.lstrip(' ').replace('\n', '').replace('\r', '')

        if len(line) == 0: continue

        if line[0] == '#':
            if len(line) == 1:
                if empty_line:
                    continue

                rtconfig.write('\n')
                empty_line = 1
                continue

            comment_line = line[1:]
            if line.startswith('# CONFIG_'): line = ' ' + line[9:]
            else: 
                line = line[1:]
                rtconfig.write('/*%s */\n' % line)

            empty_line = 0
        else:
            empty_line = 0
            setting = line.split('=')
            if len(setting) >= 2:
                if setting[0].startswith('CONFIG_'):
                    setting[0] = setting[0][7:]

                # remove CONFIG_PKG_XX_PATH or CONFIG_PKG_XX_VER
                if type(setting[0]) == type('a') and (setting[0].endswith('_PATH') or setting[0].endswith('_VER')):
                    continue

                if setting[1] == 'y':
                    rtconfig.write('#define %s\n' % setting[0])
                else:
                    rtconfig.write('#define %s %s\n' % (setting[0], setting[1]))

    if os.path.isfile('rtconfig_project.h'):
        rtconfig.write('#include "rtconfig_project.h"\n')

    rtconfig.write('\n')
    rtconfig.write('#endif\n')
    rtconfig.close()


def find_macro_in_condfig(filename,macro_name):
    try:
        config = file(filename)
    except:
        print 'open .config failed'
        return

    empty_line = 1

    for line in config:
        line = line.lstrip(' ').replace('\n', '').replace('\r', '')

        if len(line) == 0: continue

        if line[0] == '#':   
            if len(line) == 1:
                if empty_line:
                    continue

                empty_line = 1
                continue

            comment_line = line[1:]
            if line.startswith('# CONFIG_'): line = ' ' + line[9:]
            else: line = line[1:]

            #print line

            empty_line = 0
        else: 
            empty_line = 0
            setting = line.split('=')
            if len(setting) >= 2:
                if setting[0].startswith('CONFIG_'):
                    setting[0] = setting[0][7:]

                    if setting[0] == macro_name and setting[1] == 'y':
                        return True
        
    return False

def cmd(args):
    env_root = Import('env_root')
    currentdir = os.getcwd() 
    dirname = os.path.split(os.path.split(currentdir)[0])[0]
    get_rtt_name = os.path.basename(dirname)
    os_version = platform.platform(True)[10:13]
    #print os.path.split(currentdir)[1]
    kconfig_win7_path = os.path.join(env_root, 'tools', 'bin', 'kconfig-mconf_win7.exe')

    if not os.getenv("RTT_ROOT"):
        if get_rtt_name != 'rt-thread':  
            print ("menuconfig command should be used in a bsp root path with a Kconfig file, you should check if there is a Kconfig file in your bsp root first.")
            print ('And then you can check Kconfig file and modify the default option below to your rtthread root path.\n')

            print ('config $RTT_DIR')
            print ('string' )
            print ('option env="RTT_ROOT"')
            print ('default "../.."\n')
            print ('example:  default "F:/git_repositories/rt-thread"  \n')

            print ("using command 'set RTT_ROOT=your_rtthread_root_path' to set RTT_ROOT is ok too.\n")
            print ("you can ignore debug messages below.")
            #if not args.menuconfig_easy:                
            #    return

    fn = '.config'

    if os.path.isfile(fn):
        mtime = os.path.getmtime(fn)
    else:
        mtime = -1

    if args.menuconfig_fn:
        print 'use', args.menuconfig_fn
        import shutil
        shutil.copy(args.menuconfig_fn, fn)
    elif args.menuconfig_silent:
        if float(os_version) >=  6.2 :
            os.system('kconfig-mconf Kconfig -n')
        else:
            if os.path.isfile(kconfig_win7_path):
                os.system('kconfig-mconf_win7 Kconfig -n')
            else:
                os.system('kconfig-mconf Kconfig -n')

    elif args.menuconfig_setting:
        env_kconfig_path = os.path.join(env_root, 'tools\scripts\cmds')
        beforepath = os.getcwd()
        os.chdir(env_kconfig_path)

        if float(os_version) >=  6.2 :
            os.system('kconfig-mconf Kconfig')
        else:
            if os.path.isfile(kconfig_win7_path):
                os.system('kconfig-mconf_win7 Kconfig')
            else:
                os.system('kconfig-mconf Kconfig')

        os.chdir(beforepath)  
        return
    else:
        if float(os_version) >=  6.2 :
            os.system('kconfig-mconf Kconfig')
        else:
            if os.path.isfile(kconfig_win7_path):
                os.system('kconfig-mconf_win7 Kconfig')
            else:
                os.system('kconfig-mconf Kconfig')

    if os.path.isfile(fn):
        mtime2 = os.path.getmtime(fn)
    else:
        mtime2 = -1

    if mtime != mtime2:
        mk_rtconfig(fn)

    if platform.system() == "Windows":
        env_kconfig_path = os.path.join(env_root, 'tools\scripts\cmds')
        fn = os.path.join(env_kconfig_path,'.config')

        if not os.path.isfile(fn):
            return

        print("\nTry the command <menuconfig -s/--setting> ")
        print("\nEnable the auto update option,env will auto update the packages you select.")

        if find_macro_in_condfig(fn,'SYS_AUTO_UPDATE_PKGS'):
            os.system('pkgs --update')
            print "Auto update packages done"

        print("Select the project type your bsp support and then env will create a new mdk/iar project.")

        if find_macro_in_condfig(fn,'SYS_CREATE_MDK_IAR_PROJECT'):
            if find_macro_in_condfig(fn,'SYS_CREATE_MDK4'):
                os.system('scons --target=mdk4 -s')
                print "Create mdk4 project done"
            elif find_macro_in_condfig(fn,'SYS_CREATE_MDK5'):
                os.system('scons --target=mdk5 -s')
                print "Create mdk5 project done"
            elif find_macro_in_condfig(fn,'SYS_CREATE_IAR'):
                os.system('scons --target=iar -s')
                print "Create iar project done"


def add_parser(sub):
    parser = sub.add_parser('menuconfig', help=__doc__, description=__doc__)

    parser.add_argument('--config', 
        help = 'Using the user specified configuration file.',
        dest = 'menuconfig_fn')

    parser.add_argument('--silent', 
        help = 'Silent mode,don\'t display menuconfig window.',
        action='store_true',
        default=False,
        dest = 'menuconfig_silent')

    parser.add_argument('-s','--setting', 
        help = 'Env config,auto update packages and create mdk/iar project',
        action='store_true',
        default=False,
        dest = 'menuconfig_setting')

    parser.add_argument('--easy', 
        help = 'easy mode,place kconfig file everywhere,just modify the option env="RTT_ROOT" default "../.."',
        action='store_true',
        default=False,
        dest = 'menuconfig_easy')

    parser.set_defaults(func=cmd)
