import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models


def get_nat_outtraffic_data(date):
    '''
    docment https://console.cloud.tencent.com/api/explorer?Product=vpc&Version=2017-03-12&Action=DescribeGatewayFlowMonitorDetail&SignVersion=
    :param date: time . eg format '2021-03-12 05:02:00'
    :type date: str
    :return data type: dict.
    '''
    try: 
        cred = credential.Credential("xxxxxxx", "xxxxxxxxx") 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "vpc.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = vpc_client.VpcClient(cred, "ap-guangzhou", clientProfile) 

        req = models.DescribeGatewayFlowMonitorDetailRequest()
        params = {
            "TimePoint": date,
            "NatId": "nat-0gbfdfp2",
            "Limit": 100,
            "OrderField": "OutTraffic",
            "OrderDirection": "DESC"
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeGatewayFlowMonitorDetail(req) 
        data = json.loads(resp.to_json_string())
        return data

    except TencentCloudSDKException as err: 
        print(err)
        return False


