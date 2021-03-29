

部署环境：  需要 docker 运行环境。

执行：  start.sh 脚本即可部署   

腾讯云，云监控回调接口填写： 

x.x.x.x/send/xxxxx  #xx告警组

*如需要接口回调验证执行  echo "回调码" > code  再执行 start.sh

日志查看  docker logs $(docker ps  |grep "alert_callback_api:latest" |cut -c 1-5)
重启 docker restart $(docker ps  |grep "alert_callback_api:latest" |cut -c 1-5)