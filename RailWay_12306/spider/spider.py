import os
import re
import json
import string
import requests
from selenium import webdriver
from urllib.parse import quote
import time
from urllib.parse import urlencode

current_path = os.path.dirname(__file__)

browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])


class RailWayQuery(object):

    def __init__(self, START, END, DATE):
        self.START = START
        self.END = END
        self.DATE = DATE

        self.base_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={}&ts={}&date={}&flag=N,N,Y'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        }

        self.json_compile = re.compile('(\'.*\')')
        self.times_compile = re.compile('(\d{2}:\d{2})(\d{2}:\d{2})')

        with open(os.path.join(current_path, 'station_code.json'), 'r', encoding='utf-8') as f:
            self.station_code_dict = json.load(f)
        self.head_list = []

    def spider(self):
        url = self.base_url.format(self.START + ',' + self.station_code_dict.get(self.START),
                                   self.END + ',' + self.station_code_dict.get(self.END),
                                   self.DATE)
        # 避免中文乱码
        url = quote(url, safe=string.printable)

        print(url)
        try:
            browser.get(url)

        except:
            pass

        else:
            print(browser.current_url)
            head_list = ['车次', '出发站', '到达站', '出发时间', '到达时间', '历时', '商务座/特等座',
                         '一等座', '二等座', '高级软卧', '软卧/一等卧', '动卧', '硬卧/二等卧', '软座',
                         '硬座', '无座', '其他', '备注']

            items_list = []
            content_list = browser.find_elements_by_xpath('//*[@id="queryLeftTable"]/tr[@class]')
            for row in content_list:
                items = []
                # 车次
                train_num = row.find_element_by_xpath('./td[1]/div/div[1]/div/a').get_attribute('innerText')
                # 始发站、终点站
                stations = row.find_element_by_xpath('./td[1]/div/div[2]').get_attribute('innerText')
                print(stations)
                fs, ts, _ = stations.split('\n')
                # 备注
                bz = row.find_element_by_xpath('./td[13]')
                if bz.text == '预订':
                    try:
                        bz.find_element_by_tag_name('a')
                        bz = '可' + bz.get_attribute('innerText')
                    except:
                        bz = '不可' + bz.get_attribute('innerText')
                else:
                    bz = bz.get_attribute('innerText')
                if bz == '列车停运':
                    ft = tt = duration = swz = ydz = edz = gjrw = rw =\
                        dw = yw = rz = yz = wz = qt = '--'
                else:
                    # 出发时间，到达时间
                    times = row.find_element_by_xpath('./td[1]/div/div[3]').get_attribute('innerText')
                    ft, tt = re.findall(self.times_compile, times)[0]
                    # 历时
                    duration = row.find_element_by_xpath('./td[1]/div/div[4]').get_attribute('innerText')
                    duration = duration.replace('\n', '-')
                    # 商务座
                    swz = row.find_element_by_xpath('./td[2]').get_attribute('innerText')
                    # 一等座
                    ydz = row.find_element_by_xpath('./td[3]').get_attribute('innerText')
                    # 二等座
                    edz = row.find_element_by_xpath('./td[4]').get_attribute('innerText')
                    # 高级软卧
                    gjrw = row.find_element_by_xpath('./td[5]').get_attribute('innerText')
                    # 软卧/一等卧
                    rw = row.find_element_by_xpath('./td[6]').get_attribute('innerText')
                    # 动卧
                    dw = row.find_element_by_xpath('./td[7]').get_attribute('innerText')
                    # 硬卧/二等卧
                    yw = row.find_element_by_xpath('./td[8]').get_attribute('innerText')
                    # 软座
                    rz = row.find_element_by_xpath('./td[9]').get_attribute('innerText')
                    # 硬座
                    yz = row.find_element_by_xpath('./td[10]').get_attribute('innerText')
                    # 无座
                    wz = row.find_element_by_xpath('./td[11]').get_attribute('innerText')
                    # 其他
                    qt = row.find_element_by_xpath('./td[12]').get_attribute('innerText')

                items = [train_num, fs, ts, ft, tt, duration, swz, ydz,
                         edz, gjrw, rw, dw, yw, rz, yz, wz, qt, bz]
                print(items)
                items_list.append(items)

            return head_list, items_list

    def get_city_code(self):
        station_code_dict = {}

        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9083'
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            text = response.text
            text = re.search(self.json_compile, text).group(1)
            code_list = text.split('|')
            for _1, city, code, _2, _3 in zip(code_list[0::5], code_list[1::5], code_list[2::5],
                                              code_list[3::5], code_list[4::5]):
                if city not in station_code_dict.keys():
                    station_code_dict[city] = code

        json_str = json.dumps(station_code_dict, indent=4)
        with open('station_code.json', 'w') as json_file:
            json_file.write(json_str)


if __name__ == '__main__':
    rq = RailWayQuery('潮汕', '广州', '2019-01-30')
    rq.spider()




