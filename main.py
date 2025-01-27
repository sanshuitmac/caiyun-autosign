import hashlib
import requests
from loguru import logger
from config import config
import json
import schedule
import time
import os
import xml.etree.ElementTree as ET
class CaiYun:
    def __init__(self, token: str, account: str):
        self.auth_token = token
        self.url = 'https://caiyun.feixin.10086.cn'
        self.headers = {
            "Authorization": f"Basic {self.auth_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            "jwtToken": ""
        }
        self.cookies = {
            "jwtToken": ""
        }
        self.account = account

    def fetch_ssoToken(self):
        url = 'https://orches.yun.139.com/orchestration/auth-rebuild/token/v1.0/querySpecToken?client=app'
        headers = {
            'Authorization': f"Basic {self.auth_token}",
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'orches.yun.139.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        }
        data = {
            "account": self.account,
            "toSourceId": "001003"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data)).json()
        if resp['success'] == True:
            new_token = resp['data']['token']
            return new_token
        return [False, resp['message']]

    def fetch_jwtToken(self):
        ssoToken = self.fetch_ssoToken()
        print(ssoToken)
        url = f"https://caiyun.feixin.10086.cn:7071/portal/auth/tyrzLogin.action?ssoToken={ssoToken}"
        resp = requests.get(url, headers=self.headers).json()
        if resp['code'] != 0:
            return [False, resp['msg']]
        self.headers['jwtToken'] = resp['result']['token']
        self.cookies['jwtToken'] = resp['result']['token']
        return True

    def sign(self):
        checkSign_url = f"{self.url}/market/signin/page/infoV2?client=mini"
        c_resp = requests.get(checkSign_url, headers=self.headers, cookies=self.cookies).json()
        if c_resp.get('msg') == 'success':
            issign = c_resp.get('result').get('todaySignIn', False)
            if issign == True:
                logger.success('今日已签到，不再进行签到操作')
                return True
            else:
                logger.info('今日未签到，正在开始签到')
                signurl = f'{self.url}/market/manager/commonMarketconfig/getByMarketRuleName?marketName=sign_in_3'
                resp = requests.get(signurl, headers=self.headers, cookies=self.cookies).json()
                if resp['msg'] == 'success':
                    logger.success("签到成功")
                    return True
                else:
                    logger.error(f"签到失败，原因：{resp['msg']}")
                    return False
        else:
            logger.warning(f"检测签到状态失败，原因 {c_resp['msg']}")
            return False
    def upload(self, file_bytes):
        data = f"""
        <pcUploadFileRequest>
            <ownerMSISDN>{self.account}</ownerMSISDN>
            <fileCount>1</fileCount>
            <totalSize>{len(file_bytes)}</totalSize>
            <uploadContentList length="1">
            <uploadContentInfo>
                <contentName><![CDATA[7]]></contentName>
                <contentSize>{len(file_bytes)}</contentSize>
                <contentDesc></contentDesc>
                <contentTAGList></contentTAGList>
                <comlexFlag>0</comlexFlag>
                <comlexCID></comlexCID>
                <resCID length="0"></resCID>
                <digest>{hashlib.md5(file_bytes).hexdigest().upper()}</digest>
                <extInfo length="1">
                    <entry>
                        <key>modifyTime</key>
                        <vaule>{time.strftime('%Y%m%d%H%M%S')}</vaule>
                    </entry>
                </extInfo>
            </uploadContentInfo>
            </uploadContentList>
            <newCatalogName></newCatalogName>
            <parentCatalogID>{config.get('caiyun.upload_dirid')}</parentCatalogID>
            <operation>0</operation>
            <path></path>
            <manualRename>2</manualRename>
        </pcUploadFileRequest>
        """
        headers = {
            'x-huawei-uploadSrc': '1',
            'x-huawei-channelSrc': '10200153',
            'x-ClientOprType': '11',
            'Connection': 'keep-alive',
            'x-NetType': '6',
            'x-DeviceInfo': '||11|8.2.1.20241205|PC|V0lOLUVQSUxVNjE1TUlI|D1EA1E8B761492DFF34B18F05A5876E0|| Windows 10 (10.0)|1366X738|RW5nbGlzaA==|||',
            'x-MM-Source': '032',
            'x-SvcType': '1',
            'Authorization': f'Basic {self.auth_token}',
            'X-Tingyun-Id': 'p35OnrDoP8k;c=2;r=1955442920;u=43ee994e8c3a6057970124db00b2442c::8B3D3F05462B6E4C',
            'Host': 'ose.caiyun.feixin.10086.cn',
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'text/xml;UTF-8',
            'Accept': '*/*'
        }
        resp = requests.post(
            "https://ose.caiyun.feixin.10086.cn/richlifeApp/devapp/IUploadAndDownload",
            headers=headers,
            cookies=self.cookies,
            data=data,
            #verify=False
        )
        if resp.status_code != 200:
            logger.error(f"上传文件失败，返回结果{resp.content}")  
            return False
        logger.success("上传文件成功")
        return True  
    

    def check_pending_clouds(self):
        r = requests.get('https://caiyun.feixin.10086.cn/market/signin/page/receive', headers=self.headers, cookies=self.cookies).json()
        clouds = r["result"].get("receive", "")
        all_clouds = r["result"].get("total", "")
        logger.info(f'当前待领取云朵:{clouds}')
        logger.info(f'当前云朵数量:{all_clouds}')


    def share_file(self):
        get_filelist_data = {
            "catalogID": config.get('caiyun.upload_dirid'),
            "sortDirection": 1,
            "startNumber": 1,
            "endNumber": 100,
            "filterType": 0,
            "catalogSortType": 0,
            "contentSortType": 0,
            "commonAccountInfo": {
            "account": self.account,
            "accountType": 1
            }
        }
        # 仅支持个人云
        filelist = requests.post(
            url='https://yun.139.com/orchestration/personalCloud/catalog/v1.0/getDisk',
            headers=self.headers,
            cookies=self.cookies,
            data=json.dumps(get_filelist_data)
        ).json()
        #print(filelist)
        contentList = filelist.get('data').get('getDiskResult').get('contentList')
        if contentList == []:
            logger.warning('没有文件可以分享')
            return False
        share_file_data = [item for item in contentList if config.get('share.filename') in item["contentName"]][0]
        share_data = {
    "getOutLinkReq": {
        "subLinkType": 0,
        "encrypt": 1,
        "coIDLst": [share_file_data.get('contentID')],
        "caIDLst": [],
        "pubType": 1,
        "dedicatedName": share_file_data.get('contentName'),
        "periodUnit": 1,
        "viewerLst": [],
        "extInfo": {
            "isWatermark": 0,
            "shareChannel": "3001"
        },
        "period": 1,   
        "commonAccountInfo": {
            "account": self.account,
            "accountType": 1
        }
    }

}
        resp_json = requests.post(
            url='https://yun.139.com/orchestration/personalCloud-rebuild/outlink/v1.0/getOutLink',
            headers=self.headers,
            cookies=self.cookies,
            data=json.dumps(share_data),
            #verify=False,
        ).json()
        #print(resp_json)
        if resp_json.get('success') == True:
            out_link = resp_json.get("data").get("getOutLinkRes").get("getOutLinkResSet")[0].get("linkUrl")
            logger.success(f'分享成功,url: {out_link}')
            return True
        else:
            logger.error(f'分享失败,原因: {resp_json.get("message")}')
            return False



def gen_file(size_mb=15):
    file_size = size_mb * 1024 * 1024
    return os.urandom(file_size)
def job():
    #print(config.get('caiyun.token'),config.get('caiyun.phone'))
    caiyun = CaiYun(token=config.get('caiyun.token'), account=config.get('caiyun.phone'))
    logger.info("获取jwtToken")
    caiyun.fetch_jwtToken()
    logger.info("开始签到")
    caiyun.sign()
    logger.info("开始上传大小为7M的文件")
    caiyun.upload(gen_file(7))
    logger.info("完成分享文件任务")
    caiyun.share_file()
    logger.info("检查待领取云朵")
    caiyun.check_pending_clouds()

    logger.success("任务执行完成")

def main():
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("20:00").do(job)
    logger.success("定时任务已创建，将在8:00和20:00执行一次")
    while True:
        schedule.run_pending()
        time.sleep(1)
    #job()

if __name__ == '__main__':
    logger.info('程序启动')
    main()