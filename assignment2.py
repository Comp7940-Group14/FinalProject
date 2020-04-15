from __future__ import unicode_literals

import os
import sys
import re, string
import patientClass as patient
import newsClass as news
import infectionClass as infect
import hospitalMap as map


from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage, \
    TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, \
    FlexSendMessage, BubbleContainer, ImageComponent, URIAction, LocationSendMessage, \
    BoxComponent, SpacerComponent, ButtonComponent, SeparatorComponent, ButtonComponent, TextComponent, IconComponent, \
    ImageCarouselColumn, ImageCarouselTemplate, ConfirmTemplate
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

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue


        # ---------------help--------------------
        if "help" in event.message.text:
            handle_Nav(event)
            continue

        # ----------infectiou diseases-----------
        if "infect" in event.message.text:
            array = infect.get_infect_array()
            handle_Diseases_1(event, array)
            continue

        result = infect.redisGet("diseases_layer")
        if int(result) == 1:
            res = re.findall(r"\d+\.?\d*", event.message.text)
            if len(res) == 0:
                infect.redisSet("diseases_layer", "0")
            else:
                handle_Diseases_2(event)
                continue

        if int(result) == 2:
            res = re.findall(r"\d+\.?\d*", event.message.text)
            if len(res) == 0:
                infect.redisSet("diseases_layer", "0")
            else:
                handle_Diseases_Content(event)
                continue

        # --------patients distribution----------
        if "Introduce patients distribution" in event.message.text:
            handle_Patient_Introduce(event)
            continue

        if "patient" in event.message.text:
            handle_Patient_Distribute(event)
            continue

        # ----------------news---------------
        if "news" in event.message.text and "coronavirus pneumonia" in event.message.text:
            handle_News_Type(event)
            continue

        if "news" in event.message.text and "pic" in event.message.text:
            handle_Pic_News(event)
            continue

        if "news" in event.message.text:
            handle_COVID_News(event)
            continue

        # ---------------hospital---------------
        if "医院" in event.message.text:
            handle_location_message(event)
            continue


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


# --------------------Help-------------------------
def handle_Nav(event):
    message = TemplateSendMessage(
        alt_text = 'Buttons template',
        template = ButtonsTemplate(
            thumbnail_image_url = 'https://wx4.sinaimg.cn/large/682cebefly1gd5yxplyt6j20fa08lqao.jpg',
            title = 'Menu',
            text = 'Hi！I could provide the following functions: ',
            actions = [
                MessageTemplateAction(
                    label='Patients distribute',
                    text='Introduce patients distribution'
                ),
                MessageTemplateAction(
                    label='Coronavirus news',
                    text='What\'s news about coronavirus pneumonia?'
                ),
                MessageTemplateAction(
                    label='Infectious diseases',
                    text='Could you provide information about infection diseases?'
                ),
                MessageTemplateAction(
                    label='Hospital location',
                    text='You could say hospital name like: 珠海中山大学第五医院'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)


# ------------Infectiou Dieases---------------
def handle_Diseases_1(event, array):
    text = infect.get_Diseases_Text1(array)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )

def handle_Diseases_2(event):
    res = re.findall(r"\d+\.?\d*", event.message.text)
    if int(res[0]) >= 7 or int(res[0]) <= 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Please choose the diseases class number in the list!"),
        )
    else:
        text = infect.get_Diseases_Text2(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text),
        )

def handle_Diseases_Content(event):
    first_value = infect.redisGet("first_layer_value")
    address_sub = infect.redisGet("address_sub")
    num = int(first_value) - 1
    temp = address_sub[num]

    res = re.findall(r"\d+\.?\d*", event.message.text)
    if int(res[0]) > len(temp):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Please choose the item number in the list!"),
        )
    else:
        text = infect.get_Diseases_Content(event.message.text, temp)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text)
        )



# ------------Patient Distribute-------------
def handle_Patient_Introduce(event):

    textlist = ['See coronavirus pneumonia patients distribution (Update to 3.27)', \
                'Check the distribution of patients in China in some day (must choose a date, provided 1.22-3.27)', \
                'View patients distribution in a country (must choose a date, provided 1.22-3.27)', \
                'Look patients distributionis in a province or region']

    questionlist = ['I want to know coronavirus pneumonia patients distribution.', \
                'How\'s patients distributionis in China in 3.23?', \
                'How\'s patients condition about US in 2.24?', \
                'How\'s patients distributionis in Hubei?']

    cont = []
    for i in range(4):
        row = BoxComponent(
            layout='baseline',
            spacing='sm',
            contents=[
                TextComponent(text = textlist[i], color='#666666', size='sm', margin='md', wrap=True,
                    action=MessageTemplateAction(text=questionlist[i])
                )
            ],
        )
        cont.append(row)
        cont.append(SeparatorComponent())
    del (cont[-1])

    title = 'You could ask following four type questions:'
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text=title, weight='bold', wrap=True, size='md'),
                BoxComponent(layout='vertical', margin='lg', spacing='sm', contents=cont)
            ]
        )
    )

    message = FlexSendMessage(alt_text="hello", contents=bubble)
    line_bot_api.reply_message(
        event.reply_token,
        message
    )

def handle_Patient_Distribute(event):

    df = patient.get_Patient_Distribute_Text(event.message.text)
    if df == "1":
        text = "We don't have data in that day!"
    elif df == "2":
        text = "We don't have data!"
    else:
        text = df

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )


# ----------------COVID News-----------------
def handle_News_Type(event):
    message = TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text='Do you want to see news list or Pictures?',
            actions=[
                MessageTemplateAction(
                    label='List',
                    text='I\'d like to see news list.',
                ),
                MessageTemplateAction(
                    label='Picture',
                    text='I\'d like to see pictures of news.'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def handle_Pic_News(event):
    title, href, img, imgtitle, imghref, showinTilte = news.get_news_data(event.message.text)
    if len(img) == 0 :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("There no news pic in that day in our database.")
        )
        return

    message = get_pic_message(title, href, img, imghref, showinTilte)
    line_bot_api.reply_message(
        event.reply_token,
        message
    )

def get_pic_message(title, href, img, imghref, showinTilte):
    ImgList = []
    for i in range(len(img)):
        item = ImageCarouselColumn(
            image_url = img[i],
            action = URIAction(
                uri = imghref[i],
                label = 'Image News' + str(i+1),
            ))
        ImgList.append(item)

    message = TemplateSendMessage(
        alt_text = 'ImageCarousel template',
        template = ImageCarouselTemplate(
            columns = ImgList
        )
    )
    return message


def handle_COVID_News(event):

    title, href, img, imgtitle, imghref, showinTilte = news.get_news_data(event.message.text)
    if len(title) == 0 :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("There no news in that day in our database.")
        )
        return

    message = get_news_message(title, href, img, imghref, showinTilte)
    line_bot_api.reply_message(
        event.reply_token,
        message
    )
    news.insert_news_data(title, href, img, imgtitle, imghref)


def get_news_message(title, href, img, imghref, showinTilte):
    cont = []
    for i in range(len(title)):
        row = BoxComponent(
            layout='baseline',
            spacing='sm',
            contents=[
                TextComponent(
                    text=title[i],
                    color='#666666',
                    size='sm',
                    margin='md',
                    wrap=True,
                    action=URIAction(label='WEBSITE', uri=href[i])
                )
            ],
        )
        cont.append(row)
        cont.append(SeparatorComponent())
    del (cont[-1])

    title = 'Top News' + showinTilte
    bubble = BubbleContainer(
        direction='ltr',
        hero=ImageComponent(
            url=img[0],
            size='full',
            aspect_ratio='20:13',
            aspect_mode='cover',
            action=URIAction(uri=imghref[0], label='label')
        ),
        body=BoxComponent(
            layout='vertical',
            contents=[
                # title
                TextComponent(text=title, weight='bold', size='xl'),
                # info
                BoxComponent(
                    layout='vertical',
                    margin='lg',
                    spacing='sm',
                    contents=cont,
                )
            ],
        )
    )

    message = FlexSendMessage(alt_text="hello", contents=bubble)
    return message



# ----------------Hospital location-----------------
# Handler function for Location Message  113.99743053873469, 'lat': 22.53581126769833}
def handle_location_message(event):

    exclude = set(string.punctuation)
    address = ''.join(ch for ch in event.message.text if ch not in exclude)
    address = re.sub('[a-zA-Z]', '', address)
    address = address.replace(' ', '')

    log, lat = map.getlnglat(address)
    if log == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Can't find that hospital!")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            LocationSendMessage(
                title='Hospital', address=address, latitude=lat, longitude=log
            )
        )


# -------------------------------
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)


