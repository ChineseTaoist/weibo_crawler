import requests
from urllib.parse import quote, unquote
import re
import csv
import time
import datetime


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-CN,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Host': 's.weibo.com',
    'Referer': 'https://s.weibo.com/weibo/%25E8%2588%2592%25E6%25B7%2587%2520%25E7%25BB%2588%25E4%25BA%258E%25E6%25B2%25A1%25E4%25BA%25BA%25E7%25AE%25A1%25E6%2588%2591%25E6%25B2%25A1%25E4%25BA%25BA%25E8%25A6%2581%25E6%2588%2591%25E7%25AE%25A1%25E5%2595%25A6?q=%E9%95%BF%E6%B2%99&scope=ori&suball=1&timescope=custom:2021-05-04-1:2021-05-04-2&Refer=g&page=14',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'login_sid_t=f66170626b954913fdf89544d3047649; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=4883951398872.874.1577448321741; SINAGLOBAL=4883951398872.874.1577448321741; WBtopGlobal_register_version=307744aa77dd5677; ULV=1608648546194:1:1:1:4883951398872.874.1577448321741:; ALF=1651045450; SCF=Aq6rRph9kSSe6c3PS_2pjLdysp8Yxp32xIPwhGOrLYMxXDQoeRLOQoAGN8sdq8YpGRbDvhkZYoo3oYSA2Mp0InQ.; wvr=6; SSOLoginState=1620390084; SUB=_2A25NkUCUDeRhGeNL6FYX-CzKyzqIHXVvemDcrDV8PUJbkNAKLUnekW1NSPQs6Jb3bmIwthaqF6fdDyzjwAjsA-65; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFdCAvHWRqKqrceilSExXm.5NHD95QfSKeXSonESo5cWs4Dqc_zi--fi-z7iK.pi--fiKnRi-zNi--fi-i8i-88i--fiKy2iKLWi--fi-2XiKLWi--Ri-8si-iFi--Xi-z4i-2ci--fiK.fiKyW; UOR=,,www.baidu.com; webim_unReadCount=%7B%22time%22%3A1620547590068%2C%22dm_pub_total%22%3A13%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A33%2C%22msgbox%22%3A0%7D; WBStorage=202105101250|undefined'
}


def get_pages(query, scope='ori', suball='1', refer='g', time_scope='custom:2021-05-04-1:2021-05-04-2', page=1):
    url = 'https://s.weibo.com/weibo/%25E8%2588%2592%25E6%25B7%2587%2520%25E7%25BB%2588%25E4%25BA%258E%25E6%25B2%25A1%25E4%25BA%25BA%25E7%25AE%25A1%25E6%2588%2591%25E6%25B2%25A1%25E4%25BA%25BA%25E8%25A6%2581%25E6%2588%2591%25E7%25AE%25A1%25E5%2595%25A6?' \
            'q=' + quote(query) \
            + '&scope=' + scope \
            + '&suball=' + suball \
            + '&timescope=' + time_scope \
            + '&Refer=' + refer
    url += ('&page=' + str(page)) if page > 1 else ''
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError as e:
        print('Error', e.args)
        print("第" + str(page) + '页获取失败')
        return ''


def get_page_num(page):
    page = page.replace('\n', '')
    pattern_page_num = '<div class="m-page">.*?<!--/翻页-->'
    pattern_page = '<li.*?</li>'
    page_nums_content = re.findall(pattern=pattern_page_num, string=page)
    if len(page_nums_content) > 0:
        page_nums_content = page_nums_content[0]
        page_num = len(re.findall(pattern_page, page_nums_content))
        return page_num
    else:
        return 0


def parse_page(page):
    page = page.replace('\n', '')
    # 提取所有微博
    pattern = '<div class="card-wrap" action-type="feed_list_item".*?<!--card解析-->'
    weibos = re.findall(pattern=pattern, string=page)
    nodes = []
    pattern_user = 'nick-name=".*?"'
    pattern_location = '<a href="http://t.cn/.*?"  target="_blank"><i class="wbicon">2.*?</a>'
    # pattern_location_rest = '<a.*?i>'
    pattern_content = '<p.*?</p>'
    pattern_rest = '<.*?>'
    for weibo in weibos:
        username = re.findall(pattern_user, weibo)
        if len(username) != 0:
            username = username[0]
        else:
            username = ''
        location = re.findall(pattern_location, weibo)
        if len(location) != 0:
            location = location[0]
            # noises = re.findall(pattern_location_rest, location)
            # for noise in noises:
            #     location = location.replace(noise, '')
            noises = re.findall(pattern_rest, location)
            for noise in noises:
                location = location.replace(noise, '')
        else:
            location = ''
        content = re.findall(pattern_content, weibo)
        if len(content) != 0:
            content = content[0]
            noises = re.findall(pattern_rest, content)
            for noise in noises:
                content = content.replace(noise, '')
            content = content.replace(' ', '')
            content = content.replace(location, '')
        else:
            continue
        # 地址头有个杂字符
        if not location.__eq__(''):
            location = location.lstrip('2')
        nodes.append([username, content, location])
    return nodes


if __name__ == '__main__':
    # 获取城市信息
    cities = ['长沙', '武汉', '上海']
    start_date = '2020-05-01'
    end_date = '2020-06-01'
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    for city in cities:
        current_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        print(city + ':' + str(current_date))
        # 日期遍历
        while current_date < end:
            # 当天与下一天
            datetime_str = str(current_date.strftime('%Y-%m-%d'))
            current_next_date = current_date + datetime.timedelta(days=1)
            with open('./cities/{}/{}_{}.csv'.format(city, city, datetime_str), 'w') as reviews_csv:
                # 某天时间遍历
                for current_time in range(24):
                    # 当前时间与一小时后的时间
                    current_datetime = datetime_str + '-' + str(current_time)
                    current_datetime_next = (datetime_str + '-' + str(current_time + 1)) if current_time + 1 < 24 else (str(current_next_date.strftime('%Y-%m-%d')) + '-' + '0')
                    # 组合成时间参数
                    datetime_parm = current_datetime + ':' + current_datetime_next
                    print(city + '---' + datetime_parm)
                    # 获取页码数目
                    page = get_pages(query=city, time_scope='custom:'+datetime_parm, page=2)
                    page_num = get_page_num(page)
                    print('微博总页数为:' + str(page_num))
                    writer = csv.writer(reviews_csv)
                    count = 0
                    # if count <= 32:
                    #     count += 1
                    #     continue
                    for i in range(1, page_num + 1):
                        page = get_pages(city, page=i)
                        if page.__eq__(''):
                            continue
                        res = parse_page(page)
                        for review in res:
                            writer.writerow([city, datetime_parm] + review)
                        print('第' + str(i) + '页获取成功')
                        time.sleep(5)
            current_date = current_date + datetime.timedelta(days=1)
