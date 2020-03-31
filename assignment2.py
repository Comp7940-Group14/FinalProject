from __future__ import unicode_literals

import os
import sys
import oprationDB as oDB
import infectionClass as infect
import patientClass as patient
import hospitalMap as mp

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
    BoxComponent, SpacerComponent, ButtonComponent, SeparatorComponent, ButtonComponent, TextComponent, IconComponent
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

        # ------------add---------------
        if "infect" in event.message.text:
            array = infect.get_infect_array()
            handle_Diseases_1(event, array)
            continue

        result = infect.redisGet("diseases_layer")
        if int(result) == 1:
            handle_Diseases_2(event)
            continue

        if int(result) == 2:
            handle_Diseases_Content(event)
            continue


        if "patient" in event.message.text:
            handle_Patient_Distribute(event)
            continue

        if "news" in event.message.text:
            handle_COVID_News(event)
            continue

        if "医院" in event.message.text:
            handle_location_message(event)
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

# Handler function for Location Message  113.99743053873469, 'lat': 22.53581126769833}
def handle_location_message(event):
    log,lat = mp.getlnglat(event.message.text)
    if log == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("Can't find that hospital!")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            LocationSendMessage(
                title='医院', address=event.message.text,
                latitude=lat, longitude=log
            )
        )

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


# ------------Infectiou Dieases---------------
def handle_Diseases_1(event, array):
    text = infect.get_Diseases_Text1(array)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )

def handle_Diseases_2(event):
    if int(event.message.text) >= 7 or int(event.message.text) <= 0:
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

    if int(event.message.text) > len(temp):
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
# -------------------------------------------


# ------------Patient Distribute-------------
def handle_Patient_Distribute(event):
    text = patient.get_Patient_Distribute_Text(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )
# -------------------------------------------


# ----------------COVID News-----------------
def handle_COVID_News(event):
    title, href, img, imgtitle, imghref, showinTilte = oDB.get_news_data(event.message.text)
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
    oDB.insert_news_data(title, href, img, imgtitle, imghref)


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


    # bubble = BubbleContainer(
    #     direction='ltr',
    #     hero=ImageComponent(
    #         url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg',
    #         size='full',
    #         aspect_ratio='20:13',
    #         aspect_mode='cover',
    #         action=URIAction(uri='http://example.com', label='label')
    #     ),
    #     body=BoxComponent(
    #         layout='vertical',
    #         contents=[
    #             # title
    #             TextComponent(text='Brown Cafe', weight='bold', size='xl'),
    #             # review
    #             BoxComponent(
    #                 layout='baseline',
    #                 margin='md',
    #                 contents=[
    #                     IconComponent(size='sm', url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg'),
    #                     IconComponent(size='sm', url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg'),
    #                     IconComponent(size='sm', url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg'),
    #                     IconComponent(size='sm', url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg'),
    #                     IconComponent(size='sm', url='https://img.soufunimg.com/news/2017_08/23/home/1503466431358_000.jpg'),
    #                     TextComponent(text='4.0', size='sm', color='#999999', margin='md',
    #                                   flex=0)
    #                 ]
    #             ),
    #             # info
    #             BoxComponent(
    #                 layout='vertical',
    #                 margin='lg',
    #                 spacing='sm',
    #                 contents=[
    #                     BoxComponent(
    #                         layout='baseline',
    #                         spacing='sm',
    #                         contents=[
    #                             TextComponent(
    #                                 text='Place',
    #                                 color='#aaaaaa',
    #                                 size='sm',
    #                                 flex=1
    #                             ),
    #                             TextComponent(
    #                                 text='Shinjuku, Tokyo',
    #                                 wrap=True,
    #                                 color='#666666',
    #                                 size='sm',
    #                                 flex=5
    #                             )
    #                         ],
    #                     ),
    #                     BoxComponent(
    #                         layout='baseline',
    #                         spacing='sm',
    #                         contents=[
    #                             TextComponent(
    #                                 text='Time',
    #                                 color='#aaaaaa',
    #                                 size='sm',
    #                                 flex=1
    #                             ),
    #                             TextComponent(
    #                                 text="10:00 - 23:00",
    #                                 wrap=True,
    #                                 color='#666666',
    #                                 size='sm',
    #                                 flex=5,
    #                                 action=URIAction(label='WEBSITE', uri="https://example.com")
    #                             ),
    #                         ],
    #                     ),
    #                 ],
    #             )
    #         ],
    #     ),
    #     footer=BoxComponent(
    #         layout='vertical',
    #         spacing='sm',
    #         contents=[
    #             # callAction, separator, websiteAction
    #             SpacerComponent(size='sm'),
    #             # callAction
    #             ButtonComponent(
    #                 style='link',
    #                 height='sm',
    #                 action=URIAction(label='CALL', uri='tel:000000'),
    #             ),
    #             # separator
    #             SeparatorComponent(),
    #             # websiteAction
    #             ButtonComponent(
    #                 style='link',
    #                 height='sm',
    #                 action=URIAction(label='WEBSITE', uri="https://example.com")
    #             )
    #         ]
    #     ),
    # )
    # message = FlexSendMessage(alt_text="hello", contents=bubble)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     message
    # )

# -------------------------------
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)


