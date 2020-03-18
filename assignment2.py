from __future__ import unicode_literals

import os
import sys
import redis
import requests
from bs4 import BeautifulSoup
import csv


from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # ------------zwt---------------
    global array1
    if len(array1) == 0:
        get_Diseases_Data()
    # ------------zwt---------------


    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    global diseases_layer
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        # ------------ouou---------------
        if "infect" in event.message.text:
            handle_Diseases_1(event)
            continue

        if diseases_layer == 1:
            handle_Diseases_2(event)
            continue

        if diseases_layer == 2:
            handle_Diseases_Content(event)
            continue
        # ------------------------------

        # ------------YuWangAs----------
        if "patient" in event.message.text:
            handle_Patient_Distribute(event)
        # ------------------------------

        # ------------sunshine----------
        if "news" in event.message.text:
            news(event)
            continue
        # ------------------------------

        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for Text Message
def handle_TextMessage(event):
    print(event.message.text)
    msg = 'You said: "' + event.message.text + '" '
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(msg)
    )

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice image!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice video!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice file!")
    )



# ------------ouou---------------
diseases_layer = 0
first_value = 0

array1 = []
array_sub = []
address_sub = []


def get_Diseases_Data():
    diseases = 'http://www.phsciencedata.cn/Share/ky_sjml.jsp'
    html = requests.get(diseases)  # connect to the server
    bs = BeautifulSoup(html.text, 'html.parser')  # manage tags in HTML document

    recommended_movies = bs.find('div', {'class': 'lanren'})
    movie_list = recommended_movies.find_all('li', {'class': 'li2'})
    global array1
    array1 = []
    global array_sub
    array_sub = []
    global address_sub
    address_sub = []
    for item in movie_list:
        title = item.find('a').get_text()
        array1.append(title)

        sublist = item.find_all('li', {'class': 'li3'})
        tempTitle = []
        tempAdd = []

        for item in sublist:
            subtitle = item.find('a').get_text()
            tempTitle.append(subtitle)

            address = item.find('a').get('href')
            tempAdd.append(address)

        array_sub.append(tempTitle)
        address_sub.append(tempAdd)
    n = len(array1)-1
    del(array1[n])

def handle_Diseases_1(event):
    print(event.message.text)
    global diseases_layer
    diseases_layer = 1
    n=1
    text = "In my database, there are the following categories:\n"
    global array1
    for item in array1:
        text += str(n) + '.' + item + '\n'
        n=n+1
    text += "Please choose one diseases class number!"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text),
    )

def handle_Diseases_2(event):
    if int(event.message.text) >= 7 or int(event.message.text) <= 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Please choose the diseases class number in the list!"),
        )
    else:
        n = 1
        global array1
        i =  int(event.message.text)
        array1[i]
        text = "在(" + event.message.text + ")." + array1[i] + "中，有以下疾病：\n"
        num = int(event.message.text)-1
        global array_sub
        for item in array_sub[num]:
            text += str(n) + '.' + item + '\n'
            n = n + 1
        print(text)
        text += "Please choose the diseases number!"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text),
        )
        global diseases_layer
        diseases_layer = 2
        global first_value
        first_value = int(event.message.text)

def handle_Diseases_Content(event):
    global first_value
    global address_sub
    n1 = first_value-1
    temp = address_sub[n1]
    if int(event.message.text) > len(temp):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Please choose the item number in the list"),
        )
    else:
        prelink = 'http://www.phsciencedata.cn/Share/'
        n2 = int(event.message.text)-1
        link = prelink + temp[n2]

        html = requests.get(link)  # connect to the server
        bs = BeautifulSoup(html.text, 'html.parser')  # manage tags in HTML document

        recommended_movies = bs.find('div', {'id': 'tabs-note'})
        text_list = recommended_movies.find_all('span')

        arr = []
        for strContent in text_list:
            text = strContent.get_text().strip()
            arr.append(text)

        origin = []
        for i in range(len(arr)):
            if arr[i] not in origin:
                origin.append(arr[i])
        print('\n'.join(origin))

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('\n'.join(origin)),
        )
        global diseases_layer
        diseases_layer = 0
# ---------------------------------

# ------------YuWangAs-------------
def handle_Patient_Distribute(event):
    # df = pd.read_csv("patients.csv", index=None)
    # text = str(df[:3])
    str = event.message.text
    arr = str.split(' ')
    n = len(arr)-1

    text = ''
    temp = ''
    day = 0
    with open("patients.csv" , newline='', encoding='UTF-8') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            if row[0] == "Date":
                text += row[0] + '      ' + row[1] + ' ' + row[2] + "\n"
            else:
                text += row[0] + ' ' + row[1] + ' '+ row[2] + "\n"

            if arr[n] == row[1]:
                if day == 1:
                    text = temp + "\n" + row[0] + ' ' + row[1] + ' ' + row[2]
                    break
                temp = row[0] + ' ' + row[1] + ' ' + row[2]
                day = 1

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )
# ---------------------------------

# ------------sunshine------------
def news(event):
    link ='https://www.globaltimes.cn//special-coverage/Coronavirus-Outbreak.html'
    html = requests.get(link)  # connect to the server
    bs = BeautifulSoup(html.text, 'html.parser')  # manage tags in HTML document

    recommended_movies = bs.find('div', {'class': 'op-news'})
    movie_list = recommended_movies.find_all('div', {'class': 'news'})

    content = 'The Coronavirus news list from Global Times:\n\n'
    for item in movie_list:
        title = item.find('a').get_text()
        content += title + "\n\n"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(content),
    )
# -------------------------------


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)


