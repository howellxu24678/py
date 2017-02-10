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
baseurldir = "url"



logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")
cf = ConfigParser.ConfigParser()
cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

d = webdriver.PhantomJS()
video_set = set()
image_set = set()


# def get_media_url(reg, xpath, container):
#     video_re = re.compile(reg)
#
#     vls = d.find_elements_by_xpath(xpath)
#     logger.info("find %s elements", len(vls))
#     #video_list = re.findall(video_re, tx)
#     for vl in vls:
#         vl_url_list = re.findall(video_re, vl.text)
#         container |= set(vl_url_list)
#     logger.info("container size:%s", len(container))


def get_video_url():
    #get_media_url(r'src="(http://.*)" type="video/mp4"', "//video-player", video_set)
    reg = r'src="(http://.*)" type="video/mp4"'
    video_re = re.compile(reg)

    vls = d.find_elements_by_xpath("//video-player")
    logger.info("find %s videos", len(vls))
    for vl in vls:
        vl_url_list = re.findall(video_re, vl.text)
        global video_set
        video_set |= set(vl_url_list)
    logger.info("video_set size:%s", len(video_set))

#d.find_elements_by_xpath("//photoset/photo/photo-url[@max-width='1280']")
def get_image_url():
    imgs = d.find_elements_by_xpath("//photoset/photo/photo-url[@max-width='1280']")
    logger.info("find %s images", len(imgs))
    for img in imgs:
        global image_set
        image_set.add(img.text)
    logger.info("image_set size:%s", len(image_set))


def get_download_url(site, begin, end, num):
    try:
        cur_begin = begin
        while True:
            cur_url = "http://%s.tumblr.com/api/read?start=%d&num=%d" % (site, cur_begin, num)
            logger.info("cur_url:%s", cur_url)
            d.get(cur_url)
            if len(d.page_source) < MIN_PAGE_SOURCE_LENGTH or cur_begin >= end:
                break
            get_video_url()
            get_image_url()
            cur_begin += num
            time.sleep(2)

    except BaseException, e:
        logger.exception(e)

def write_file(namepre, container):
    url_dir = os.path.join(os.getcwd(), baseurldir)
    if not os.path.isdir(url_dir):
        os.mkdir(url_dir)
    filename = namepre + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    file_path = os.path.join(url_dir, filename)

    logger.info("begin to write file:%s", file_path)
    fpy = open(file_path, 'w')
    for element in container:
        fpy.write(element)
        fpy.write("\n")
    fpy.close()




try:
    sites = cf.get("main", "sites").strip().split(',')
    begin = cf.getint("main", "begin")
    end = cf.getint("main", "end")
    end = MAX_GET_NUM if (end == 0) else end
    num = cf.getint("main", "num")
    logger.info("sites:%s,begin:%s,end:%s,num:%s", sites, begin, end, num)

    for site in sites:
        get_download_url(site, begin, end, num)
    d.close()
    d.quit()

    logger.info("total video_set:%s", len(video_set))
    write_file("video", video_set)
    logger.info("total image_set:%s", len(image_set))
    write_file("image", image_set)

except BaseException,e:
    logger.exception(e)

#todo:生成url文件时按照域名分目录，每1000个记录生成一个文件






# d = webdriver.PhantomJS()
# d.get("http://qqqpppbbbddd.tumblr.com/api/read?start=0&num=20")
#
# tx = d.find_elements_by_xpath("//video-player")
#
#
# reg = r'src="(http://.*)" type="video/mp4"'
# video_re = re.compile(reg)
# video_list = re.findall(video_re, tx)
