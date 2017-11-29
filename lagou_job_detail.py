#-*- coding:utf-8 -*-
import requests
from fake_useragent import UserAgent
import time
from pymongo import MongoClient
from pyquery import PyQuery

#利用Mongodb进行数据存储：lagoudbjob.detail2
client = MongoClient()
db = client.lagoudbjob
lagoudbjob = db.detail2

headers = {
    'Cookie':'JSESSIONID=ABAAABAABEEAAJAAE6D4B3C3C1AC54D0AFF8CE9293E2A16; '
             'user_trace_token=20171127185526-79ad1099-d361-11e7-9a81-5254005c3644; '
             'PRE_UTM=; PRE_HOST=www.google.com.hk; '
             'PRE_SITE=https%3A%2F%2Fwww.google.com.hk%2F; '
             'PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; '
             'LGUID=20171127185526-79ad1312-d361-11e7-9a81-5254005c3644; '
             'index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=search_code; '
             'SEARCH_ID=c2451581078b406c92bf75d15846bc32; _gat=1; '
             '_ga=GA1.2.969421781.1511780126; _gid=GA1.2.1067000274.1511780126; '
             'LGSID=20171127185526-79ad11b1-d361-11e7-9a81-5254005c3644; '
             'LGRID=20171127190225-73339b18-d362-11e7-9a81-5254005c3644; '
             'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1511780131; '
             'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1511780544',
    'referer':'https://www.lagou.com/jobs/list_java?city=%E5%85%A8%E5%9B%BD&cl=false&'
              'fromSearch=true&labelWords=&suginput='
}

url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'

def find_job(page,kw):
    """ 获得
    :param page: 要爬取的页数
    :param kw: 要爬取信息的关键字
    :return:
    """
    for i in range(page):
        find_job_json = []
        data = {
            'first': 'true',
            'pn': i,
            'kd': kw
        }
        ua = UserAgent()
        headers['User-Agent']=ua.random
        response = requests.post(url, headers=headers,data=data)
        metal_url = 'https://www.lagou.com/zhaopin/'+data['kd']+'/'+str(data['pn']+1)+'/'
        response1 = requests.get(metal_url,headers = headers)

        print('正在爬取第' + str(i+1) + '页数据...')
        time.sleep(3)

        if response.status_code==200: #获取页面职位信息
            with open('find_job.txt','w',encoding = 'utf-8') as f:
                f.write(response.text)
            with open('find_job.json','w',encoding='utf-8') as f:
                f.write(response.text)
            find_job_json = response.json()['content']['positionResult']['result']
        else:
            print('something wrong1!!!')

        if response1.status_code==200: #获取职位链接
            jobs = PyQuery(response1.text)
            job_lists = jobs('#s_position_list > ul > li').items()
            job_url_lists = []
            for it in job_lists:
                job_url_list = it('div.list_item_top > div.position > div.p_top > a').attr('href')
                job_url_lists.append(job_url_list)
        else:
            print('something wrong2!!!')

        for i in range(len(job_url_lists)): #获取职位链接内详细信息(职位描述+职位需求)
            find_job_json[i]["jobDetails"] = jobinfo_detail(job_url_lists[i]) # 向List的每个元素（元素是一个字典）中插入字段

        #print(find_job_json)
        lagoudbjob.insert(find_job_json) # 插入数据库



def jobinfo_detail(joburl):
    """ 获取职位的详细信息（职责和需求）
    """
    response1 = requests.get(joburl,headers=headers) # 这里headers是必需的，
    jpy = PyQuery(response1.text)
    info_detail = jpy('#job_detail > dd.job_bt > div > p')
    return(info_detail.text())

if __name__=='__main__':
    total_pages = input("请输入要查看的总的页数： ")
    job_type = input("请输入关键字(如C，Java，Ruby，no python 哈哈)：")
    find_job(int(total_pages),job_type)



