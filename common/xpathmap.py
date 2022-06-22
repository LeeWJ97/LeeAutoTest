import traceback
from inter.commonKeys import sysKey
from common.GetExcelResult import Reader
from common import logger

class XpathMap():
    XPATH_DICT = dict()
    def __init__(self):
        if not XpathMap.XPATH_DICT:
            XpathMap.readall_xpath()

    @staticmethod
    def readall_xpath():
        try:
            xpath_dict = dict()

            xpathmap_excel = Reader()
            xpathmap_excel.open_excel(f'{sysKey.path}/lib/xpathmap.xlsx')

            for i in xpathmap_excel.get_sheets():
                i = str(i)
                xpathmap_excel.set_sheet(i)
                xpath_dict.update({i:xpathmap_excel.readline()})

            XpathMap.XPATH_DICT = xpath_dict
            logger.info('init xpathmap successfully')
            return xpath_dict
        except Exception as e:
            logger.exception(f'init xpathmap failed: {str(traceback.format_exc())}')
            return []

    @staticmethod
    def read_xpath(s):
        try:
            xp = s.split('_')
            xp_entity = xp[0]
            xp_xpathname = xp[1]

            for i in XpathMap.XPATH_DICT:
                if i.lower() == xp_entity.lower():
                    for j in XpathMap.XPATH_DICT[i]:
                        if j[0].lower() == xp_xpathname.lower():
                            logger.info(f'find xpath {s} -> {j[1]}')
                            return j[1]
            logger.error(f'Cannot find xpath: {s}')
            return None
        except Exception as e:
            logger.exception(f'find xpath {s} failed: {str(traceback.format_exc())}')
            return None



if __name__ == '__main__':
    XpathMap()

    xp = 'Login_emailinput'

    print(xp,XpathMap.read_xpath(xp))


