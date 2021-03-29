# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
import requests,json,datetime
import random
import os
import logging
import myjsonpath
from natapi import get_nat_outtraffic_data
import time

#cloud tencent alert document：https://cloud.tencent.com/document/product/248/9066


app = Flask(__name__)

alert_groups = {
                "test_group":"https://oapi.dingtalk.com/robot/send?access_token=xxxxx",
                "ops_group":"https://oapi.dingtalk.com/robot/send?access_token=xxx",
                "pro_group":"https://oapi.dingtalk.com/robot/send?access_token=xxx",
                "test_pod_group":"https://oapi.dingtalk.com/robot/send?access_token=xxxx",
                }

#一分钟的流量转换bps
def bps_convert(value):    
    value = int(value)
    units = ["Bbps", "KBbps", "MBbps", "GBbps", "TBbps", "PBbps"]
    size = 1024.0
    for i in range(len(units)):
     if (value / size) < 1:
         return "%.2f%s" % (value / 60, units[i])
     value = value / size

     
def hum_convert(value):
    value = int(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
     if (value / size) < 1:
         return "%.2f%s" % (value, units[i])
     value = value / size


def page404():
    return '''<title>404 Not Found</title>
              <h1>Not Found</h1>
              <p>The requested URL was not found on the server. </p>''',404

def metric_type_data(data):
    msg = ""
    if int(data.get('alarmStatus')) == 1:
        msg = ["云监控告警已经触发"] + \
              ["\n告警类型:"] + myjsonpath.jsonpath(data,'$..policyTypeCName') + \
              ["\n告警策略名称: "] + myjsonpath.jsonpath(data,'$..policyName') + \
              ["\n告警内容: "] + myjsonpath.jsonpath(data,'$..metricShowName') + myjsonpath.jsonpath(data,'$..calcType') + myjsonpath.jsonpath(data,'$..calcValue') + \
              ["\n告警对象: "] + myjsonpath.jsonpath(data,'$..objName') + \
              ["\n当前数据: "] + myjsonpath.jsonpath(data,'$..currentValue') + myjsonpath.jsonpath(data,'$..unit')+ \
              ["\n触发时间: "] + myjsonpath.jsonpath(data,'$..firstOccurTime')
    elif int(data.get('alarmStatus')) == 0:
        msg = ["云监控告警已经恢复"] + \
              ["\n告警类型: "] + myjsonpath.jsonpath(data,'$..policyTypeCName') + \
              ["\n告警策略名称: "] + myjsonpath.jsonpath(data,'$..policyName') + \
              ["\n告警内容: "] + myjsonpath.jsonpath(data,'$..metricShowName') + myjsonpath.jsonpath(data,'$..calcType') + myjsonpath.jsonpath(data,'$..calcValue') + \
              ["\n告警对象: "] + myjsonpath.jsonpath(data,'$..objName') + \
              ["\n当前数据: "] + myjsonpath.jsonpath(data,'$..currentValue') + myjsonpath.jsonpath(data,'$..unit')+ \
              ["\n触发时间: "] + myjsonpath.jsonpath(data,'$..firstOccurTime') + \
              ["\n恢复时间: "] + myjsonpath.jsonpath(data,'$..recoverTime')  + \
              ["\n持续时间: "] + myjsonpath.jsonpath(data,'$..durationTime')
    return msg


def event_type_data(data):
    msg = ""
    if int(data.get('alarmStatus')) == 1:
        msg = ["云监控告警已经触发"] + \
              ["\n告警类型: "] + myjsonpath.jsonpath(data,'$..policyTypeCName') +  \
              ["\n告警策略名称: "] + myjsonpath.jsonpath(data,'$..policyName') + \
              ["\n事件类型名称: "] + myjsonpath.jsonpath(data,'$..productShowName') + \
              ["\n事件名称: "] + myjsonpath.jsonpath(data,'$..eventShowName')+ \
              ["\n事件对象: "] + myjsonpath.jsonpath(data,'$..unInstanceId') + \
              ["\n事件告警对象详情: "] + myjsonpath.jsonpath(data,'$..objDetail') + \
              ["\n触发时间: "] + myjsonpath.jsonpath(data,'$..firstOccurTime')
    elif int(data.get('alarmStatus')) == 0:
        msg = ["云监控告警已经恢复"] + \
              ["\n告警类型: "] + myjsonpath.jsonpath(data,'$..policyTypeCName') +  \
              ["\n告警策略名称: "] + myjsonpath.jsonpath(data,'$..policyName') + \
              ["\n事件类型名称: "] + myjsonpath.jsonpath(data,'$..productShowName') + \
              ["\n事件名称: "] + myjsonpath.jsonpath(data,'$..eventShowName')+ \
              ["\n事件对象: "] + myjsonpath.jsonpath(data,'$..unInstanceId') + \
              ["\n事件告警对象详情: "] + myjsonpath.jsonpath(data,'$..objDetail') + \
              ["\n触发时间: "] + myjsonpath.jsonpath(data,'$..firstOccurTime') + \
              ["\n恢复时间: "] + myjsonpath.jsonpath(data,'$..recoverTime') + \
              ["\n持续时间: "] + myjsonpath.jsonpath(data,'$..durationTime')
    return msg


def natdata_parse():
    msg = ""
    now_time = time.time()
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time - 60 ))
    one_min = time.strftime("%Y-%m-%d %H:%M", time.localtime(now_time - 60 ))
    natdata = get_nat_outtraffic_data(date)
    if natdata:
        private_ip = myjsonpath.jsonpath(natdata,"$..PrivateIpAddress")
        out_traffic = myjsonpath.jsonpath(natdata,"$..OutTraffic")
        out_traffic_unit = list(map(hum_convert,out_traffic))
        count = sum(map(int,out_traffic))
        count_unit = hum_convert(sum(map(int,out_traffic)))
        mbps = bps_convert(count)
        msg = "NAT网关出口流量TOP 10 IP:" + str(dict(zip(private_ip[:10],out_traffic_unit[:10]))) + "\n" + one_min + '一分钟总计流量: ' + count_unit + "\n平均每秒: " + mbps
        send_dingding(msg, "pro_group")
        app.logger.info(msg)
    else:
        send_dingding("无 nat 流量数据信息 - from alert-call-back. ", "pro_group")
        


    

def send_dingding(alert_msg, alert_group):
    
    webhook = alert_groups.get(alert_group)

    if alert_group == "nat":
        webhook = alert_groups.get("pro_group")
        natdata_parse()
    elif not webhook:
        webhook = alert_groups.get("test_group")        


    headers = {'Content-Type': 'application/json'}
    data={ "msgtype": "text", "text": { "content": alert_msg } }
    
    r = requests.post(url=webhook,data=json.dumps(data),headers=headers)

    if r.json().get("errcode") == 0:
        app.logger.info( "发送告警成功！")
    else:
        app.logger.error("dingding 发送失败 ")
        app.logger.error(r.text)

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
    alert_title = []

    if data:
        app.logger.info("POST data is :" + data.decode('utf-8'))

        try:
            data = json.loads(data)
        except Exception as err:
            app.logger.error("data loadd json faile!!")
            app.logger.error(err)
            return page404()


        if "msg" in data:
            return re_code(),200   #返回腾讯云的给的code
        elif "sessionId" in data:
            re_data = {
                            "sessionId": data.get("sessionId"),
                            "retCode": 0
                       }
            
        if data.get('alarmType') == "event":
            alert_msg = event_type_data(data)
        elif data.get('alarmType') == "metric":
            alert_msg = metric_type_data(data)
        else:
            app.logger.error("other alert type data. try metric_type_data parse")
            alert_msg = metric_type_data(data)
            
        alert_msg = "".join(alert_msg)
        
        send_dingding(alert_msg, alert_group) #发送dingding消息
        return json.dumps(re_data),200

    else:
        return page404()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    handler = logging.FileHandler('flask.log', encoding='UTF-8')   # 设置日志字符集和存储路径名字
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(                            # 设置日志格式
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0',port="15000",debug=False)
