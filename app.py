# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
import requests,json,datetime
import os
import logging

#cloud tencent alert document：https://cloud.tencent.com/document/product/248/9066


app = Flask(__name__)


def page404():
    return '''<title>404 Not Found</title>
                  <h1>Not Found</h1>
                  <p>The requested URL was not found on the server. </p>''',404
 
def send_dingding(alert_msg, alert_group):

    if alert_group == "test_group":     #测试组dingding
        webhook="https://oapi.dingtalk.com/robot/send?access_token=xxxxxx"
    elif alert_group == "ops_group":    #运维组dingding
        webhook="https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxx"
    elif alert_group == "all_alerts":   
        webhook="https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxx"
    else:
        webhook="https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxx" #测试组dingding


    alert_msg = alert_msg
    headers = {'Content-Type': 'application/json'}
    data={
        "msgtype": "text",
        "text": {
            "content": alert_msg
        }
    }
    r = requests.post(url=webhook,data=json.dumps(data),headers=headers)

    if r.json().get("errcode") == 0:
        app.logger.info( "发送告警成功！")
        return True
    else:
        app.logger.error("dingding 发送失败 ")
        app.logger.error(r.text)
        return False

def re_code():
    code = ""
    if os.path.exists(os.path.join(os.getcwd(),"code")):
        f = open('code',"r")
        code = f.readline()
        f.close()
        return code

@app.route('/send/<alert_group>',methods=['POST'])
def alert_data(alert_group="test_group"):
    data = request.get_data()
    if data:
        try:
            data = json.loads(data)
        except Exception as err:
            app.logger.error(err)
            app.logger.error("alert data is: " + data.decode('utf-8'))
            return page404()
        app.logger.info("alert data is :" + str(data)) 
        alarm_info = data.get("alarmPolicyInfo")
        alarm_conditions_info = alarm_info.get('conditions')

        if "msg" in data:
            return re_code(),200   #返回腾讯云的给的code
        elif "sessionId" in data:
            re_data = {
                            "sessionId": data.get("sessionId"),
                            "retCode": 0
                       }

        try:
            if data.get('alarmStatus') == 1 :
                alert_msg = "云监控告警已经触发。\n告警内容：" + alarm_info.get('policyTypeCName') \
                        + "|" + alarm_conditions_info.get('metricShowName') \
                        + alarm_conditions_info.get('calcType',"") + alarm_conditions_info.get('calcValue',"") \
                        + "\n告警对象: " + data.get('alarmObjInfo').get('dimensions').get('objName',"")  \
                        + "\n当前数据：" + alarm_conditions_info.get('currentValue',"") + alarm_conditions_info.get('unit',"") \
                        + "\n触发时间: " + data.get('firstOccurTime')

            elif data.get('alarmStatus') == 0 :
                alert_msg = "云监控告警已经恢复。\n" + "告警内容：" + alarm_info.get('policyTypeCName') \
                        + "|" + alarm_conditions_info.get('metricShowName') \
                        + alarm_conditions_info.get('calcType',"") + alarm_conditions_info.get('calcValue',"") \
                        + "\n告警对象: " + data.get('alarmObjInfo').get('dimensions').get('objName',"")  \
                        + "\n当前数据：" + alarm_conditions_info.get('currentValue',"") + alarm_conditions_info.get('unit',"") \
                        + "\n触发时间: " + data.get('firstOccurTime') \
                        + "\n恢复时间: " + data.get('recoverTime') \
                        + "\n持续时间: " + data.get('durationTime')
            else :
                alert_msg = "ERROR: alarmStatus is other! "

            if send_dingding(alert_msg, alert_group): #发送消息
                return json.dumps(re_data),200
            else:
                return "send msg error.",200
        except Exception as err:
            app.logger.error("parse alert data !")
            app.logger.error(err)
            return "err!"
    else:
        return page404()

if __name__ == '__main__':
    handler = logging.FileHandler('flask.log', encoding='UTF-8')   # 设置日志字符集和存储路径名字
    logging_format = logging.Formatter(                            # 设置日志格式
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    app.url_map.converters['re'] = RegexConverter
    app.run(host='0.0.0.0',debug=True)
