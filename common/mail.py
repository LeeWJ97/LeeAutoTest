# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  邮件发送模块
# @Version  : 2.1
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from common import config,logger


class Mail:
    """
        用于获取配置并发送邮件
    """
    def __init__(self, result_path=[] ,result_name=[]):
        self.mail_info = {}
        # 发件人
        self.mail_info['from'] = config.config['mail']
        self.mail_info['username'] = config.config['mail']
        # smtp服务器域名
        self.mail_info['hostname'] = f"smtp.{config.config['mail'][config.config['mail'].rfind('@') + 1:config.config['mail'].__len__()]}"

        # 发件人的密码
        self.mail_info['password'] = config.config['pwd']
        # 收件人
        self.mail_info['to'] = str(config.config['mailto']).split(',')
        # 抄送人
        self.mail_info['cc'] = str(config.config['mailcopy']).split(',')
        # 邮件标题
        self.mail_info['mail_subject'] = config.config['mailtitle']
        self.mail_info['mail_encoding'] = config.config['mail_encoding']
        # 添加自定义昵称
        self.mail_info['mailnick'] = config.config['mailnick']
        # 附件内容
        self.mail_info['filepaths'] = result_path
        self.mail_info['filenames'] = result_name


    def send(self, text):
        smtp = SMTP_SSL(self.mail_info['hostname'])
        smtp.set_debuglevel(0)

        ''' SMTP 'ehlo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        '''
        smtp.ehlo(self.mail_info['hostname'])
        smtp.login(self.mail_info['username'], self.mail_info['password'])


        # 普通HTML邮件
        # msg = MIMEText(text, 'html', self.mail_info['mail_encoding'])

        # 支持附件的邮件
        msg = MIMEMultipart()
        msg.attach(MIMEText(text, 'html', self.mail_info['mail_encoding']))
        msg['Subject'] = Header(self.mail_info['mail_subject'], self.mail_info['mail_encoding'])
        # msg['from'] = self.mail_info['from']
        # 添加自定义昵称
        h = Header(self.mail_info['mailnick'], 'utf-8')
        h.append('<' + self.mail_info['from'] + '>', 'ascii')
        msg["from"] = h

        # logger.debug(self.mail_info)
        # logger.debug(text)
        msg['to'] = ','.join(self.mail_info['to'])
        msg['cc'] = ','.join(self.mail_info['cc'])
        receive = self.mail_info['to']
        receive += self.mail_info['cc']

        # 添加附件
        for i in range(len(self.mail_info['filepaths'])):
            att1 = MIMEText(open(self.mail_info['filepaths'][i], 'rb').read(), 'base64', 'utf-8')
            att1['Content-Type'] = 'application/octet-stream'
            att1.add_header('Content-Disposition', 'attachment', filename=('gbk', '', self.mail_info['filenames'][i]))

            msg.attach(att1)

        for i in range(3):
            try:
                smtp.sendmail(self.mail_info['from'], receive, msg.as_string())
                smtp.quit()
                logger.info('邮件发送成功')
                break
            except Exception as e:
                logger.error(f'邮件发送失败第{i}次，重试发送，达到3次后不再重试：')
                logger.exception(e)


if __name__ == '__main__':
    config.get_config('../lib/conf/conf.properties')
    logger.debug(config.config)
    mail = Mail()
    # mail.mail_info['filepaths'] = ['E:\\software\\Python\\myframe\\test\\test.html']
    # mail.mail_info['filenames'] = ['测试报告.html']
    html = '<!DOCTYPE HTML><html><head><title>LeeAutoTest</title><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"></head><body><style>a,aside,b,body,div,footer,h1,h2,h3,h4,h5,h6,header,hgroup,html,img,p,pre,span,table,tbody,td,th,tr,u,var,video{margin:0;padding:0;border:0;font-size:100%;font:inherit;vertical-align:baseline}ol,ul{list-style:none;margin:0;padding:0}.wrap{margin:0 auto;max-width:900px}h1{font-family:Audiowide,cursive;font-size:3em;color:#fff;text-transform:uppercase;text-align:center;font-weight:400;margin-top:10%;margin-bottom:2%}.main{background:#ebebeb;box-shadow:0 0 10px #5f5f5f;-webkit-box-shadow:0 0 10px #5f5f5f;-moz-box-shadow:0 0 10px #5f5f5f;-o-box-shadow:0 0 10px #5f5f5f;text-align:center;padding:20px;-webkit-border-radius:1em;-moz-border-radius:1em;-o-border-radius:1em}.text{margin-top:2%}h2{font-family:"Century Gothic" Arial,Helvetica,sans-serif;font-size:22px;color:#45a09b;text-transform:capitalize;font-weight:700}h3{font-size:1.4em;color:#d5a307;text-transform:capitalize;text-align:left}.clock-ticker{margin:1.33%;width:100%;display:inline-block}.clock-ticker .block{font-family:"Century Gothic" Arial,Helvetica,sans-serif;position:relative;color:#45a09b;float:left;margin-right:1%;margin-top:1%;background:#fff;border-radius:6px;-webkit-border-radius:6px;-moz-border-radius:6px;-o-border-radius:6px;box-shadow:0 0 10px #999;-webkit-box-shadow:0 0 10px #999;-o-box-shadow:0 0 10px #999;box-shadow:0 0 10px #999}.clock-ticker .block .flip-top{font-size:20px;text-align:center}.label{font-family:"Century Gothic" Helvetica,sans-serif;color:#46afa9;font-weight:400;text-transform:capitalize;margin-bottom:8px}.footer{font-family:"Century Gothic"}.footer p{font-size:1em;color:#f09000}.footer a{color:#45a09b}.footer a:hover{text-decoration:underline}</style><div class="wrap"><div class="main"><img src="https://www.baidu.com/img/flexible/logo/pc/result.png" style="height:100px"><h2>LeeAutoTest-自动化测试邮件报告</h2><div class="text" style="border:1px solid #45a09b;width:98%;margin-left:1%"><h2 style="top:7px;position:relative;color:#45a09b">汇总信息</h2><div class="clock-ticker"><div class="block" style="width:48%"><span class="flip-top" id="numdays">{count}</span><span class="flip-btm"></span><footer class="label">总数</footer></div><div class="block" style="width:48%"><span class="flip-top" id="numhours">{passrate}</span><span class="flip-btm"></span><footer class="label">通过率</footer></div><div class="block" style="width:48%"><span class="flip-top" id="nummins">{starttime}</span><span class="flip-btm"></span><footer class="label">开始时间</footer></div><div class="block" style="width:48%"><span class="flip-top" id="numsecs">{endtime}</span><span class="flip-btm"></span><footer class="label">结束时间</footer></div></div></div><br><div style="margin:1%;width:98%;display:inline-block;color:#45a09b;border:1px solid;font-size:18px"><div><p style="font-size:28px;font-weight:700">{reporttitle}</p><table width="100%" border="0" align="center" class="table_c" style="border-collapse:collapse"><tbody><tr><td width="100" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">分组名</td><td width="80" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">用例数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">通过数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">状态</td></tr><tr><td width="100" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">知乎</td><td width="80" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">7</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc">6</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;font-weight:700;color:red">fail</td></tr></tbody></table></div></div><br><br><div class="footer"><p>自动化测试邮件，请勿直接回复</p><p>Copyright &copy; testingedu.com.cn. All rights reserved.<a target="_blank" href="http://wpa.qq.com/msgrd?v=3&amp;uin=332040986&amp;site=qq&amp;menu=yes">LeeAutoTest</a></p></div></div></div></body></html>'
    mail.send(html)
