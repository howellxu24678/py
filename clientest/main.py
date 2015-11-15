# -*- coding: utf-8 -*-
import logging 
import logging.config
from auto.mainengine import MainEngine
import os
import ConfigParser
import sys
from PyQt4.QtCore import QCoreApplication

baseconfdir="conf"
loggingconf= "logging.config"
businessconf= "business.ini"

def main():
    """主程序入口"""
    app = QCoreApplication(sys.argv)

    logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
    logger = logging.getLogger("run")

    print os.getcwd()

    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

    ee = MainEngine(cf)
    ee.logon()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


