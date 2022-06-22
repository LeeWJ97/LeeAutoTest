# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  邮件发送模块
# @Version  : 2.1
import smtplib
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
        if 'works.com' in config.config['mail']:
            self.mail_info['hostname'] = 'smtp.office365.com'
        else:
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
        # office365不支持SSL，只支持TLS
        if 'works.com' in config.config['mail']:
            smtp = smtplib.SMTP(self.mail_info['hostname'],587)
            smtp.starttls()
        else:
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
        if self.mail_info['cc'] != ['None']:
            msg['cc'] = ','.join(self.mail_info['cc'])

        receive = self.mail_info['to']
        if self.mail_info['cc'] != ['None']:
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
    #config.get_config('../lib/conf/conf.properties')
    config.get_config('../lib/conf/conf.yml')
    logger.debug(config.config)
    mail = Mail()
    html = '这是一封测试邮件'
    mail.send(html)
