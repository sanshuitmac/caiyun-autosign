import hashlib
import requests
from loguru import logger
from config import config
import json
import schedule
import time
import os
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
        file_size = len(file_bytes)
        sha256 = hashlib.sha256()
        sha256.update(file_bytes)
        file_hash = sha256.hexdigest()
        data = {"parentFileId":"/","name":file_hash,"type":"file","size":int(file_size),"formUpload":True,"contentHash":file_hash,"contentHashAlgorithm":"SHA256"}
        headers = {
   'Host': 'personal-kd-njs.yun.139.com',
   'Connection': 'keep-alive',
   'x-yun-op-type': '1',
   'x-yun-net-type': '1',
   'x-yun-module-type': '100',
   'x-yun-app-channel': '10214200',
   'x-yun-client-info': '1||8|5.6.1|microsoft|microsoft|6b9643c4-85d7-4c49-8731-ad0cdc||windows 10 x64|||||',
   'Authorization': f'Basic {self.auth_token}',
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11275',
   'x-yun-api-version': 'v1',
   'Accept': '*/*',
   'Sec-Fetch-Site': 'cross-site',
   'Sec-Fetch-Mode': 'cors',
   'Sec-Fetch-Dest': 'empty',
   'Referer': 'https://servicewechat.com/wx4e4ed37286c816c2/113/page-frame.html',
   'Accept-Language': 'zh-CN,zh;q=0.9',
   'Content-Type': 'application/json'
}
        resp = requests.post(
            "https://personal-kd-njs.yun.139.com/hcy/file/create",
            headers=headers,
            cookies=self.cookies,
            data=json.dumps(data)
        ).json()
        if resp['code'] != 0000:
            logger.error(f"上传文件失败，原因{resp['message']}")  
            return False
        return True      
def gen_file(size_mb=15):
    file_size = size_mb * 1024 * 1024
    return os.urandom(file_size)
def job():
    caiyun = CaiYun(token=config.caiyun_token, account=config.phone)
    logger.info("获取jwtToken")
    caiyun.fetch_jwtToken()
    logger.info("开始签到")
    caiyun.sign()
    logger.info("开始上传大小为7M的文件")
    caiyun.upload(gen_file(7))

def main():
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("20:00").do(job)
    logger.success("定时任务已创建，将在8:00和20:00执行一次")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    logger.info('程序启动')
    main()