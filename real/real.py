# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from selenium import webdriver
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from operator import itemgetter
slack_ts_back = "0"
app = Flask(__name__)

slack_token = "xoxb-507694811781-507328919956-bf8Qx9b6GdhplAagv4rDNLBG"
slack_client_id = "507694811781.507391689443"
slack_client_secret = "bc0a75f43144970cde274ae2b28bf6ab"
slack_verification = "JxUBZ9ntZfyJqMLvHwFQTthh"
sc = SlackClient(slack_token)

driver = webdriver.Chrome(r'C:\Users\student\Desktop\chromedriver_win32\chromedriver.exe')

# pic=''
# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):

    result = re.sub(r'<@\S+> ', '', text)
    if "추천" in result:

        source = urllib.request.urlopen("http://www.cgv.co.kr/movies").read()
        soup = BeautifulSoup(source, "html.parser")

        keywords = []
        count = 1

        keywords.append("CGV MOVIE CHART Top 10\n")

        for keyword in soup.find_all("strong", class_="title"):
            if count > 10: break
            striped = keyword.get_text().strip()
            keywords.append(str(count) + "위 : " + striped)
            count = count + 1
        return (1,u'\n'.join(keywords),None)

    elif "개봉" in result:
        source = urllib.request.urlopen("http://www.cgv.co.kr/movies/pre-movies.aspx").read()
        soup = BeautifulSoup(source, "html.parser")

        keywords = []
        count = 1

        keywords.append("CGV MOVIE 개봉예정\n")
        title = soup.find_all("strong", class_="title")
        title = title[3:]
        for keyword in title:
            if count > 15: break

            striped = keyword.get_text().strip()
            keywords.append(str(count) + " : " + striped)
            count = count + 1
        return (1,u'\n'.join(keywords),None)

    elif "평점" in result:
        source = urllib.request.urlopen("http://m.cgv.co.kr/WebAPP/MovieV4/movieList.aspx?mtype=now&iPage=1").read()
        soup = BeautifulSoup(source, "html.parser")

        keywords = []
        rates = []
        titles = []

        keywords.append("평점 높은 순위\n")
        #       평점 불러와서 저장
        for rate in soup.find_all("span", class_="percent"):
            rates.append(rate.get_text().strip()[:-1])

        rates = [int(x) if x != '' else 0 for x in rates]

        #       제목 불러와서 저장
        for title in soup.find_all("strong", class_="tit"):
            titles.append(title.get_text().strip())
        temp = zip(titles, rates)
        last = tuple(temp)
        s = sorted(last, key=itemgetter(1), reverse=True)
        great = []
        for i in s:
            if i[1] >= 95:
                great.append(i)
        count = 1
        a = []
        for i in great:
            a.append(str(count) + "위." + i[0] + " : " + str(i[1]))
            count = count + 1
        return (1,u'\n'.join(a),None)

    elif "검색" in result :
        return (1,u"영화인에 대해 검색하겠습니다. ex) 배우 OOO 혹은 감독 OOO",None)

    elif "배우" in result :
         keywords=[]
        # 웹사이트 열기
         driver.get("http://www.cgv.co.kr/")
          # 검색창 찾기
         searchText = driver.find_element_by_id("header_keyword")
         result = result[3:]
         searchText.send_keys(result)
            # 검색
         bt = driver.find_element_by_css_selector("button#btn_header_search.btn-go-search")
         bt.click()
            # 더보기클릭
         cc = driver.find_element_by_css_selector("a.link-more")
         cc.click()
            # 긁어오기
         source = driver.page_source
         soup = BeautifulSoup(source, "html.parser")
         for i in soup.find_all("strong", class_="title"):
             keywords.append(i.get_text())

         return (1,u"\n".join(keywords),None)
    elif "감독" in result :
        keywords=[]
        result = result[3:]
        driver.get("http://www.cgv.co.kr/search/cast.aspx?query=" + result)
        #첫번째 클릭
        dp = driver.find_element_by_css_selector("strong.title")
        dp.click()
        #감독내용 긁어오기
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        links = []

        for i in soup.find_all("div", class_="sect-base"):
            links.append(i.find("img")["src"])

        # global pic
        # pic = links[0]

        titles = []
        for i in soup.find_all("div", class_="box-contents"):
            titles.append(i.get_text().strip())

        titles = titles[1:]

        print(titles)

        years = []
        real_titles = []

        for i in titles:
            years.append(i[-4:])

        for i in titles:
            real_titles.append(i[:-4])

        # print(years)
        # print(real_titles)

        temp = zip(years, real_titles)
        dic_title = dict(temp)
        print(dic_title)

        reretitle = []
        count = 1
        for key, value in dic_title.items():
            reretitle.append(str(count) + ". " + key + " : " + value)
            count += 1

        return (2,u"\n".join(reretitle),links[0])
    elif "제목" in result :
        words=[]

        driver.get("http://www.cgv.co.kr/")
        searchText = driver.find_element_by_id("header_keyword")
        result = result[3:]
        searchText.send_keys(result)

        bt = driver.find_element_by_css_selector("button#btn_header_search.btn-go-search")
        bt.click()

        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        rate = 0

        # global keyword
        for i in soup.find_all("span", class_="percent"):
            rate = i.get_text().strip()[:-1]

        rate = [int(rate) if rate != '' else 0]

        words.append("골든에그 : " + str(rate))

        qq = driver.find_element_by_css_selector("strong.title")
        qq.click()

        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        img_canvas = soup.find_all("div", class_="sect-base-movie")
        links = []

        for i in img_canvas:
            links.append(i.find("img")["src"])


        # global pic
        # pic=links[0]
        return (2,u"\n".join(words),links[0])

    else:
        return (1,u"CGV MOVIE STAR 무엇이 궁금하세요?\n" \
                u"1. 영화를 추천해 드립니다.\n" \
                u"2. 개봉예정작을 알려드립니다.\n" \
                u"3. 평점 순위를 알려드려요.\n" \
                u"4. 검색하고 싶으세요.\n",None)
        # u'\n'.join())


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])
    if event_type == "app_mention":

        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        (menu,keywords,img) = _crawl_naver_keywords(text)
        msg = {}
        msg["text"] = "!THUMB_NAIL!"
        msg["image_url"] = img
        msg["color"] = "#F36F81"
        if menu == 2:
            sc.api_call(

                "chat.postMessage",
                channel=channel,
                attachments=json.dumps([msg]),
                text=keywords
            )
        elif menu == 1:
            # (menu, keywords, img) = _crawl_naver_keywords(text)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )
        else :
            pass
        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        global slack_ts_back
        if (float(slack_ts_back) < float(slack_event["event"]["ts"])):
            slack_ts_back = slack_event["event"]["ts"]
            return _event_handler(event_type, slack_event)
        else:
            return make_response("duplicated", 200, )

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.ssssss</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=2468)