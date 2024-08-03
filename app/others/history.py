import time
import shutil
import os

lastCsvPath = './history/lastcsv.txt'
history_dir = './history'

def getStrTime():
    return time.strftime("%Y%m%d%H%M%S", time.localtime()), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def log(str):
    nowtime, nowtime_log = getStrTime()
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    srcfile = './web_view/show_data.js'
    dstfile = '%s/%s_show_data.js' % (history_dir, nowtime)
    shutil.copyfile(srcfile, dstfile)

    with open('%s/log.txt' % history_dir, 'a+', encoding='utf-8') as f:
        f.write('[%s] %s\n' % (nowtime_log, str))

def get_logs():
    with open('%s/log.txt' % history_dir, 'r', encoding='utf-8') as f:
        return f.readlines()


if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    log('addnode')