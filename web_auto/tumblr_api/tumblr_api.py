# -*- coding: utf-8 -*-

from selenium import webdriver
import re

import logging.config

import os
import ConfigParser
import datetime
import time


baseconfdir = "conf"
loggingconf = "logging.config"
businessconf = "tumblr.ini"
MIN_PAGE_SOURCE_LENGTH = 300
MAX_GET_NUM = 10000
FILE_MAX_NUM = 1000
baseurldir = "url"

VIDEO_STR = "video"
IMAGE_STR = "image"



logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")
cf = ConfigParser.ConfigParser()
cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

driver = webdriver.PhantomJS()

def get_video_url(_site, _set):
    #get_media_url(r'src="(http://.*)" type="video/mp4"', "//video-player", video_set)
    reg = r'src="(.*)" type="video/mp4"'
    video_re = re.compile(reg)

    vls = driver.find_elements_by_xpath("//video-player")
    for vl in vls:
        vl_url_list = re.findall(video_re, vl.text)
        _set |= set(vl_url_list)
    logger.info("site:%s elements:%s current video_set size:%s", _site, len(vls), len(_set))


#d.find_elements_by_xpath("//photoset/photo/photo-url[@max-width='1280']")
def get_image_url(_site, _set):
    imgs = driver.find_elements_by_xpath("//photo-url[@max-width='1280']")
    for img in imgs:
        _set.add(img.text)
    logger.info("site:%s elements:%s current image_set size:%s", _site, len(imgs), len(_set))


def get_download_url(_site, _dt, begin, end, num):
    try:
        cur_begin = begin
        while True:
            cur_url = "http://%s.tumblr.com/api/read?start=%d&num=%d" % (_site, cur_begin, num)
            logger.info("cur_url:%s", cur_url)
            driver.get(cur_url)
            if len(driver.page_source) < MIN_PAGE_SOURCE_LENGTH:
                break

            get_video_url(_site, _dt[VIDEO_STR])
            get_image_url(_site, _dt[IMAGE_STR])
            cur_begin += num
            if cur_begin >= end:
                break
            time.sleep(2)

    except BaseException, e:
        logger.exception(e)


def get_filename(_site):
    return _site + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_0.txt"

def new_file(_site, _dir):
    file_path = os.path.join(_dir, get_filename(_site))

    #确保不覆盖原有的文件
    index = 1
    while os.path.isfile(file_path):
        file_path = file_path[:file_path.rfind('_') + 1] + str(index) + ".txt"
        index += 1

    logger.info("begin to write file:%s", file_path)
    return open(file_path, 'w')

def write_file(_site, _dir, _set):
    if len(_set) < 1:
        return

    fpy = new_file(_site, _dir)
    count = 0
    for element in _set:
        if count != 0 and count % FILE_MAX_NUM == 0 and fpy is not None:
            fpy.close()
            fpy = new_file(_site, _dir)
        fpy.write(element)
        fpy.write("\n")
        count += 1
    fpy.close()


def write_files(_site, _dt):
    url_dir = os.path.join(os.getcwd(), baseurldir)
    if not os.path.isdir(url_dir):
        os.mkdir(url_dir)

    video_dir = os.path.join(url_dir, VIDEO_STR)
    if not os.path.isdir(video_dir):
        os.mkdir(video_dir)

    image_dir = os.path.join(url_dir, IMAGE_STR)
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    logger.info("site:%s total video_set:%s", _site, len(_dt[VIDEO_STR]))
    write_file(_site, video_dir, _dt[VIDEO_STR])
    logger.info("site:%s total image_set:%s", _site, len(_dt[IMAGE_STR]))
    write_file(_site, image_dir, _dt[IMAGE_STR])


try:
    sites = cf.get("main", "sites").strip().split(',')
    begin = cf.getint("main", "begin")
    end = cf.getint("main", "end")
    end = MAX_GET_NUM if (end == 0) else end
    num = cf.getint("main", "num")
    logger.info("sites:%s,begin:%s,end:%s,num:%s", sites, begin, end, num)

    g_dt = {}
    for site in sites:
        dt = {}
        dt[IMAGE_STR] = set()
        dt[VIDEO_STR] = set()
        g_dt[site] = dt
        get_download_url(site, g_dt[site], begin, end, num)
    driver.close()
    driver.quit()


    for k,v in g_dt.iteritems():
        write_files(k, v)

except BaseException,e:
    logger.exception(e)

import os
import re
to_delete_path = r"E:\TDDOWNLOAD\tumblr\video"
def delete_duplicate_file(_path):
    file_paths = filter(os.path.isfile, map(lambda x: os.path.join(_path, x), os.listdir(_path)))
    dir_paths = filter(os.path.isdir, map(lambda x: os.path.join(_path, x), os.listdir(_path)))
    for file_path in file_paths:
        rf = re.findall(r'.*\(\d+\).*', file_path)
        #满足正则表达式并且存在去掉括号的文件名，表明文件确实重复了，需要删除
        if len(rf) > 0:
            fpath = rf[0]
            if os.path.isfile(fpath[:fpath.rfind('(')] + fpath[fpath.rfind(')') + 1:]):
                print "remove file:%s" % fpath
                os.remove(fpath)

    for dir_path in dir_paths:
        delete_duplicate_file(dir_path)
delete_duplicate_file(to_delete_path)


# d = webdriver.PhantomJS()
# d.get("http://qqqpppbbbddd.tumblr.com/api/read?start=0&num=20")
#
# tx = d.find_elements_by_xpath("//video-player")
#
#
# reg = r'src="(http://.*)" type="video/mp4"'
# video_re = re.compile(reg)
# video_list = re.findall(video_re, tx)
