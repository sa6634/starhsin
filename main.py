import random

# 引入套件 flask
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
# 引入 linebot 異常處理
from linebot.exceptions import (
    InvalidSignatureError
)
# 引入 linebot 訊息元件
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage
)

user_command_dict = {}
good_luck_list = ['2330 台積電', '2317 鴻海', '2308 台達電', '2454 聯發科']
stock_price_dict = {
    '2330': 210,
    '2317': 90,
    '2308': 150,
    '2454': 300
}

app = Flask(__name__)

# LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 類似聊天機器人的密碼，記得不要放到 repl.it 或是和他人分享
line_bot_api = LineBotApi('ZPTmhjBhhlDu2OWt9DN1tfPI8r+Fpfy7YgKr+SlsEdO4DZHJ3iiJl4F5TgG1RmoLdvrsc6XLcm0MBJdwSX1fST6GAoTjp2lOLJ2zF9Oyj+gTwydyj+Way5E2Li8/VxQhY1Nl2oSrX4cPSrVLsL97vAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('616821b23a51b2be1d26b76a7acd3075')


# 此為 Webhook callback endpoint
@app.route("/callback", methods=['POST'])
def callback():
    # 取得網路請求的標頭 X-Line-Signature 內容，確認請求是從 LINE Server 送來的
    signature = request.headers['X-Line-Signature']

    # 將請求內容取出
    body = request.get_data(as_text=True)

    # handle webhook body（轉送給負責處理的 handler，ex. handle_message）
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# decorator 負責判斷 event 為 MessageEvent 實例，event.message 為 TextMessage 實例。所以此為處理 TextMessage 的 handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = TextSendMessage(text='請輸入正確指令')
    user_id = event.source.user_id

    # 根據使用者 ID 暫存指令
    user_command = user_command_dict.get(user_id)

    # 判斷使用者輸入為 @查詢股價 且 之前輸入的指令非 @查詢股價
    if user_message == '@查詢股價' and user_command != '@查詢股價':
        reply_message = TextSendMessage(text='請問你要查詢的股票是？')
        # 儲存使用者輸入了 @查詢股價 指令
        user_command_dict[user_id] = '@查詢股價'
    elif user_message == '@報明牌':
        # 隨機從 good_luck_list 中取出一個股票代號
        random_stock = random.choice(good_luck_list)
        reply_message = TextSendMessage(text=f'報明牌：{random_stock}')
        # 將暫存指令清空
        user_command_dict[user_id] = None
    # 若上一個指令為 @查詢股價
    elif user_command == '@查詢股價':
        # 若使用者上一指令為 @查詢股價 則取出使用者輸入代號的股票價格資訊
        stock_price = stock_price_dict[user_message]
        if stock_price:
            reply_message = TextSendMessage(text=f'成交價：{stock_price}')
            # 清除指令暫存
            user_command_dict[user_id] = None

    # 回傳訊息給使用者
    line_bot_api.reply_message(
        event.reply_token,
        reply_message)


# __name__ 為內建變數，若程式不是被當作模組引入則為 __main__
if __name__ == "__main__":
    # 運行 Flask server，預設設定監聽 127.0.0.1 port 5000（網路 IP 位置搭配 Port 可以辨識出要把網路請求送到那邊 xxx.xxx.xxx.xxx:port，app.run 參數可以自己設定監聽 ip/port）
    app.run()