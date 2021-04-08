#!/usr/bin/env python3

'''
Description: Try to export each activitiy in specified android apk using root privilege
        than take a screenshot and save to the current path apk name directory.
Usage: ./auto_enum_activity.py <xxx.apk>
Require: aapt adb
Author: JRZ
'''

import os
import sys
from apkutils import APK
import json
import subprocess
import re
import time

global Path_aapt
aapt_path="/usr/bin/aapt"
adb_path="/usr/bin/adb"

def getManifest(apkPath):
    try:
        # Require aapt
        act = subprocess.check_output( aapt_path + ' dump xmltree ' + apkPath + ' AndroidManifest.xml' , shell=True )
        return act
    except Exception as e:
        print(e)
        return

def getActivities(manifest):
    activities = []
    for line in manifest.splitlines():
        line = line.decode('utf-8')
        if "A: android:name" in line or "0x01010003" in line:
            (t1,line2,t2,t3,t4) = re.split('"',line)
            if re.search('Activity$',line2) and line2 not in activities:
                activities.append(line2)
    return activities

def exportActivity(packageName,activityName):
    try:
        # Require adb
        subprocess.call([adb_path,"shell","am","start","-n","%s/%s" % (packageName,activityName)])
    except Exception as e:
        print(e)
        return

def exitApp(packageName):
    try:
        subprocess.call([adb_path,"shell","am","force-stop",packageName])
    except Exception as e:
        print(e)
        return

def makeDir():
    try:
        print("[*] Creating local output directory.")
        if not os.path.exists("./screenshot_output"):
            os.system("mkdir ./screenshot_output")
        subprocess.call([adb_path,"shell","mkdir","-p","/sdcard/snapshot"])
    except Exception as e:
        print(e)
        return

def snapshotAndFetch(activityName):
    try:
        pic_name = activityName + ".png"
        subprocess.call([adb_path,"shell","screencap","-p","/sdcard/snapshot/%s" % pic_name])
        #time.sleep(3)
        subprocess.call([adb_path,"pull","/sdcard/snapshot/%s" % pic_name,"./screenshot_output"])
    except Exception as e:
        print(e)
        return

def cleanUp():
    try:
        subprocess.call([adb_path,"shell","rm","-r","/sdcard/snapshot"])
    except Exception as e:
        print(e)
        return

def banner(package_name,length,delay):
    print("-"*80)
    print("[+] APP package name: %s" % package_name)
    print("[+] Total: %d activities.\n\
[+] Its about %.2f minutes to finish, please be patient." % (length,(length*delay/60)))
    print("[+] Author: JRZ")
    print("-"*80)
    

def main():
    package_name = []
    activities = []
    
    apkPath = sys.argv[1]
    if os.path.exists(apkPath):
        apk = APK(apkPath)
    else:
        print("[-] APK path:\t%s\tdose not exsits"  % apkPath)
        return

    # Get package_name
    if apk.get_manifest():
        package_name = apk.get_manifest()['@package']


    # Get AndroidManifest.xml
    manifest = getManifest(apkPath)

    if manifest == None:
        print("[-] Error getting Manifest")
        return

    # Get all activity
    activities = getActivities(manifest)
    activities = set(activities)

    if activities == None:
        print("[-] None activity found")

    delay = 10
    banner(package_name,len(activities),delay)


    # Require android root
    subprocess.call([adb_path,"root"])
    makeDir()
    count = 0
    for activity_name in activities:
        count += 1
        print("[*] Trying the num %d activity -- Total: %d" % (count,len(activities)))
        print("[*] Trying export activity ---> %s" % activity_name)
        exportActivity(package_name,activity_name)
        time.sleep(delay)
        snapshotAndFetch(activity_name)
        exitApp(package_name)
    cleanUp()
    print("[*] Enumerate done! All the result have been save to the screenshot_output directory, check it!")

if __name__ == '__main__':
    main()
