from wxauto import WeChat   # 开源版

# 初始化微信实例
wx = WeChat()

def sendMsg(msg:str, who:str):
    # 发送消息
    wx.SendMsg(msg, who=who)