# -*- coding: utf-8 -*-
import logging 
import logging.config

import os
import ConfigParser
import sys
reload(sys)
sys.setdefaultencoding('utf8')

baseconfdir="conf"
loggingconf= "logging.config"
businessconf= "business.ini"

def main():
    try:
        from auto.mainengine import MainEngine
        from PyQt4.QtCore import QCoreApplication
        """主程序入口"""
        app = QCoreApplication(sys.argv)

        logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
        logger = logging.getLogger("run")

        cf = ConfigParser.ConfigParser()
        cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

        me = MainEngine(cf)

        sys.exit(app.exec_())
    except BaseException,e:
        logger.exception(e)


if __name__ == '__main__':
    main()