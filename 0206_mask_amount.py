# need install Flask,LineBotSDK,requests
# pip3 install requests
# pip3 install flask
# pip3 install line-bot-sdk

import requests
import json
import os,time
import datetime

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

def getHealth(data_msg) :
    answer=""
    url ='http://data.nhi.gov.tw/Datasets/Download.ashx?rid=A21030000I-D50001-001&l=https://data.nhi.gov.tw/resource/mask/maskdata.csv'
    if os.path.exists("./maskdata.csv")==False :
        r = requests.get(url)
        r.encoding='utf-8'
        with open('maskdata.csv', 'w', encoding='utf-8', newline='') as f:
            f.write(r.text)
        with open('maskdata.csv', 'r', encoding='utf-8', newline='') as f:
            datas = f.readlines()
    mtimestamp = os.path.getmtime("./maskdata.csv")
    starttime=datetime.datetime.fromtimestamp(mtimestamp)
    endtime = datetime.datetime.now()
    if((endtime-starttime).seconds > 180):#如果檔案3分鐘以上未更新,重新抓
        r = requests.get(url)
        r.encoding='utf-8'
        with open('maskdata.csv', 'w', encoding='utf-8', newline='') as f:
            f.write(r.text)
        with open('maskdata.csv', 'r', encoding='utf-8', newline='') as f:
            datas = f.readlines()
        print("更新檔案") 
    msgs=data_msg.split(",")#分割使用者傳送過來的訊息
    district=conty=""
    if(len(msgs)>=1):
        conty=msgs[0].replace("台", "臺")
    if(len(msgs)==2):
        district=msgs[1].replace("台", "臺")
    count=0
    if conty != "" :
        #conty = conty.replace("台", "臺")
        with open('maskdata.csv', 'r', encoding='utf-8') as f:
            datas = f.readlines()
        for data in datas:
            if data.replace("台", "臺").find(conty)!=-1:
                if(len(msgs)!=2 or data.replace("台", "臺").find(district)!=-1):
                    pharmacy = data.split(',')
                    answer+=pharmacy[1]+"\n"
                    answer+="成人口罩量:"+pharmacy[4]+"\n兒童口罩量:"+pharmacy[5]+"\n"
                    answer+=pharmacy[2]+"\n"+pharmacy[3]+"\n更新時間:"+pharmacy[6]+""
                    count+=1
            if count>20:
                break
    if answer=="":
        answer="找不到任何資料!!!\n請輸入[縣市]或是[縣市,鄉鎮區]\n如:\n高雄市\n高雄市,新興區"
    #print("-"*20)
    #print(answer)
    return answer

app = Flask(__name__)


line_bot_api = LineBotApi('Channel access token')
handler = WebhookHandler('Channel secret')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=getHealth(text))
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
