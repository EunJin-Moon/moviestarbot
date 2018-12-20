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

app = Flask(__name__)


slack_client_id = "507694811781.507391689443"
slack_client_secret = "507694811781.507391689443"
slack_verification = "ObdFnZMa9BeP4XLVSHZppmic"
# sc = SlackClient(slack_token)


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
        return u'\n'.join(keywords)

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
        return u'\n'.join(keywords)

    elif "평점 95프로" in result:
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
        return u'\n'.join(a)
    else:
        return u"CGV MOVIE STAR 무엇이 궁금하세요?"
        # u'\n'.join())


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

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
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=2000)
