import requests
from bs4 import BeautifulSoup
import redis
import pickle


HOST = "redis-19146.c57.us-east-1-4.ec2.cloud.redislabs.com"
PWD = "U6WRX8xOJb4mi3BShXP1mmAwpryZy6ad"
PORT = "19146"

redis1 = redis.Redis(host = HOST, password = PWD, port = PORT)


def redisSet(key, list):
    redisObject = pickle.dumps(list)
    redis1.set(key, redisObject)


def redisGet(key):
    redisObject = redis1.get(key)
    if redisObject is None:
        return []

    result = pickle.loads(redisObject)
    return result


def get_infect_array():

    array = redisGet("infectlist")
    if len(array) == 0:
        get_Diseases_Data()
        array = redisGet("infectlist")
    return array


def get_Diseases_Data():

    diseases = 'http://www.phsciencedata.cn/Share/ky_sjml.jsp'
    html = requests.get(diseases)  # connect to the server
    bs = BeautifulSoup(html.text, 'html.parser')  # manage tags in HTML document

    recommended_movies = bs.find('div', {'class': 'lanren'})
    movie_list = recommended_movies.find_all('li', {'class': 'li2'})

    array1 = []
    array_sub = []
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

    redisSet("infectlist", array1)
    redisSet("infectlist_sub", array_sub)
    redisSet("address_sub", address_sub)


def get_Diseases_Text1(array):

    # set diseases_layer
    redisSet("diseases_layer", "1")

    n = 1
    text = "In my database, there are the following categories:\n"
    for item in array:
        text += str(n) + '.' + item + '\n'
        n = n + 1
    text += "Please choose one diseases class number!"
    return text


def get_Diseases_Text2(msg):

    # set diseases_layer
    redisSet("diseases_layer", "2")
    redisSet("first_layer_value", msg)

    array = redisGet("infectlist")
    array_sub = redisGet("infectlist_sub")
    num = int(msg) - 1

    text = "在(" + msg + ")" + array[num] + "中，有以下疾病：\n"

    n = 1
    for item in array_sub[num]:
        text += str(n) + '.' + item + '\n'
        n = n + 1

    text += "Please choose the diseases number!"
    return text


def get_Diseases_Content(msg, temp):

    # set diseases_layer
    redisSet("diseases_layer", "0")
    redisSet("infectlist", [])

    prelink = 'http://www.phsciencedata.cn/Share/'
    num = int(msg) - 1
    link = prelink + temp[num]

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

    return '\n'.join(origin)


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