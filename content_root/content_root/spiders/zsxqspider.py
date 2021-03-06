import datetime
import json
import os
import urllib.parse
import time

import scrapy

from .. import items

group_api = 'https://api.zsxq.com/v2/groups'
files_api = 'https://api.zsxq.com/v2/files/'
group_files_page = "https://api.zsxq.com/v2/groups/551151485124/files?count=20"


class MySpider(scrapy.Spider):
    name = 'zsxq'
    allowed_domains = ['api.zsxq.com']
    start_urls = [group_api]

    def parse(self, response):
        data = json.loads(response.body)
        if not data['succeeded']:
            self.logger.warning("cant login, error code %d", data['code'])
            return

        groups = data['resp_data']['groups']
        self.logger.info("Get Groups Num %d", len(groups))
        for group in groups:
            self.logger.info("Get Groups Name %s", group['name'])
            if not group['name'] == self.settings['ZSXQ_GROUP_NAME']:
                continue

            groupID = group['group_id']
            self.logger.info("Get Group %d info", groupID)

            url = self.__buildFileInfoUrl(groupID)
            yield scrapy.Request(url, self.__parseFile)

    def __buildEndTime(self, ctime):
        beginTime = datetime.datetime.strptime(ctime, "%Y-%m-%dT%H:%M:%S.%f+0800")
        deltaTime = datetime.timedelta(microseconds=1000)
        endTime = beginTime - deltaTime
        return endTime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0800"

    def __buildFileInfoUrl(self, groupID, etime=None):
        count = self.settings['ZSXQ_DL_NUMBER_ONCE']
        url = f"{group_api}/{groupID}/files?count={count}"
        if etime:
            url = url + '&end_time=' + urllib.parse.quote(etime)
        return url

    def __getGroupIDFromFileInfoUrl(self, url):
        path = urllib.parse.urlparse(url).path
        return path.split('/')[3]

    def __buildSubDirName(self, ctime):
        fileDate = datetime.datetime.strptime(ctime, "%Y-%m-%dT%H:%M:%S.%f+0800")
        return f"{fileDate.year}年{fileDate.month}月"

    def __needDownload(self, fileName, ctime):
        subDir = self.__buildSubDirName(ctime)
        path = "/".join([self.settings['FILES_STORE'], subDir, fileName])
        if os.path.exists(path):
            return False

        if 'ZSXQ_DL_CTIME_BEGIN' in self.settings:
            fileDate = datetime.datetime.strptime(ctime, "%Y-%m-%dT%H:%M:%S.%f+0800")
            beginDate = datetime.datetime.strptime(self.settings['ZSXQ_DL_CTIME_BEGIN'], "%Y-%m-%d")
            if fileDate < beginDate:
                return False

        return True

    def __parseFile(self, response):
        data = json.loads(response.body)
        if not data['succeeded']:
            self.logger.warning("failed on getting file list, error code %d", data['code'])
            return

        fInfos = data['resp_data']['files']
        for fInfo in fInfos:
            fileName = fInfo['file']['name']
            ctime = fInfo['file']['create_time']
            if not self.__needDownload(fileName, ctime):
                continue

            self.logger.info("ready download file %s, %s", fileName, ctime)
            fileID = fInfo['file']['file_id']
            url = f"{files_api}{fileID}/download_url"
            subDir = self.__buildSubDirName(ctime)
            yield scrapy.Request(url, self.__parseFileUrl, meta={'subdir': subDir})

        self.logger.info("cur file number %d", len(fInfos))
        maxNum = self.settings['ZSXQ_DL_NUMBER_ONCE']
        if len(fInfos) >= maxNum:
            self.logger.info("get more files")
            time.sleep(3)
            lastInfo = fInfos[maxNum - 1]
            etime = self.__buildEndTime(lastInfo['file']['create_time'])
            groupID = self.__getGroupIDFromFileInfoUrl(response.url)
            url = self.__buildFileInfoUrl(groupID, etime)
            yield scrapy.Request(url, self.__parseFile)

    def __parseFileUrl(self, response):
        data = json.loads(response.body)
        dlUrl = data['resp_data']['download_url']

        item = items.DLFileItem()
        item['sub_dir'] = response.meta['subdir']
        item['file_urls'] = [dlUrl]
        yield item
