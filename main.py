# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal,QThread,QTimer,QEvent,QTime
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QAction, QMenu, QSystemTrayIcon, QFileDialog,QLabel,QSplitter
from PyQt5.QtGui import QIcon,QCursor
import sys,threading, time, os, traceback, platform

from Ui_main import Ui_MainWindow
from Ui_setting import Ui_DlgSetting
from lib.Spider import AnySpider
from lib.Icon import MyIcon

class Spider(AnySpider, QThread):
    signal = pyqtSignal(object)
    def __init__(self, parent=None):
        super(Spider, self).__init__(False)
        super(QThread, self).__init__()

    def log(self, str, extra=None):
        self.signal.emit({"str":str, "extra":extra})

class DlgSetting(QDialog, Ui_DlgSetting):
    parent = None

    def __init__(self, parent=None):
        super(DlgSetting, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent

        self.chk_min_tray.setChecked(parent.settings['chkMinToTray'])

        self.chk_start.setChecked(parent.settings['chkStart'])
        self.time_start.setEnabled(self.chk_start.isChecked())
        self.time_start.setTime(QTime.fromString(parent.settings['timeStart'], 'hh:mm:ss'))
        
        self.chk_end.setChecked(parent.settings['chkEnd'])
        self.time_end.setEnabled(self.chk_end.isChecked())
        self.time_end.setTime(QTime.fromString(parent.settings['timeEnd'], 'hh:mm:ss'))
        
    
    @pyqtSlot() 
    def on_btn_ok_clicked(self):
        settings = {
            "chkMinToTray":self.chk_min_tray.isChecked(),
            "chkStart":self.chk_start.isChecked(),
            "chkEnd":self.chk_end.isChecked(),
            "timeStart":self.time_start.text(),
            "timeEnd":self.time_end.text(),
        }

        #check
        startTime = time.strptime(time.strftime('%Y-%m-%d') + ' ' + settings['timeStart'], '%Y-%m-%d %H:%M:%S')
        endTime = time.strptime(time.strftime('%Y-%m-%d') + ' ' + settings['timeEnd'], '%Y-%m-%d %H:%M:%S')
        if settings['chkStart'] and settings['chkEnd'] and startTime >= endTime:
            QMessageBox.critical(self, '提示', "结束时间必须大于开始时间！", QMessageBox.Ok, QMessageBox.Ok) 
            return
        
        self.parent.settings = settings

        self.parent.timeStartDate = None
        self.parent.timeEndDate = None

        self.close()

    @pyqtSlot() 
    def on_btn_cancel_clicked(self):
        self.close()
    
    @pyqtSlot() 
    def on_chk_start_clicked(self):
        self.time_start.setEnabled(self.chk_start.isChecked())
    
    @pyqtSlot() 
    def on_chk_end_clicked(self):
        self.time_end.setEnabled(self.chk_end.isChecked())



class MainWindow(QMainWindow, Ui_MainWindow):
    spider = None
    threads = None
    startTime = 0
    emailCount = 0
    thread_load_email = None
    thread_check_network = None
    tray = None
    dlgSetting = None
    settings = {
        "chkMinToTray":True,
        "chkStart":False,
        "chkEnd":False,
        "timeStart":None,
        "timeEnd":None,
    }
    timeStartDate = None
    timeEndDate = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        
        self.spider = Spider()
        self.spider.signal.connect(self.log)
        self.spider.init()
        self.threads = []
        
    def changeEvent(self, e):
        if e.type() == QEvent.WindowStateChange:
            if self.isMinimized() and isWindows():
                #print("窗口最小化")
                #print(self.settings)
                if self.settings["chkMinToTray"]:
                    self.hide()
            elif self.isMaximized():
                #print("窗口最大化")
                pass
            elif self.isFullScreen():
                #print("全屏显示")
                pass
            elif self.isActiveWindow():
                #print("活动窗口")
                pass
        elif e.type()==QEvent.ActivationChange:
            #self.repaint()
            pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "是否要退出程序吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes: 
            self.exitSystem()
            sys.exit()
        else: 
            event.ignore()

    def addContextMenu(self):
        self.addEmailContextMenu()
        self.addLogContextMenu()

    def addEmailContextMenu(self):
        self.txt_email.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_email.customContextMenuRequested.connect(self.showEmailPopupMenu)
        self.emailContextMenu = QMenu(self)

        self.clearEmailAction = self.emailContextMenu.addAction('清空数据')
        self.clearEmailAction.triggered.connect(lambda: self.doMenuEvent('clear'))

        self.backupEmailAction = self.emailContextMenu.addAction('数据备份')
        self.backupEmailAction.triggered.connect(lambda: self.doMenuEvent('backup'))

        self.exportEmailAction = self.emailContextMenu.addAction('导出数据')
        self.exportEmailAction.triggered.connect(lambda: self.doMenuEvent('export'))

        self.refreshEmailAction = self.emailContextMenu.addAction('刷新数据')
        self.refreshEmailAction.triggered.connect(lambda: self.doMenuEvent('reload'))

    def addLogContextMenu(self):
        self.txt_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_log.customContextMenuRequested.connect(self.showLogPopupMenu)
        self.logContextMenu = QMenu(self)

        self.clearLogAction = self.logContextMenu.addAction('清空数据')
        self.clearLogAction.triggered.connect(lambda: self.doMenuEvent('clearLog'))

        self.exportLogAction = self.logContextMenu.addAction('导出数据')
        self.exportLogAction.triggered.connect(lambda: self.doMenuEvent('exportLog'))

    def showEmailPopupMenu(self, pos):
        self.emailContextMenu.exec_(QCursor.pos()) 
    
    def showLogPopupMenu(self, pos):
        self.logContextMenu.exec_(QCursor.pos()) 

    def doMenuEvent(self, action):
        if action == 'reload':
            self.loadEmail()
        elif action == 'clear':
            reply = QMessageBox.question(self, '提示', "您确定要清空所有已保存的Email文件吗，建议您先备份数据？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
            if reply == QMessageBox.Yes: 
                self.spider.emptyEmail()
                self.loadEmail()
        elif action == 'clearLog':
            self.txt_log.clear()
        elif action == 'backup':
            self.spider.backupEmail()
        elif action == 'export':
            f =  QFileDialog.getSaveFileName(self,"保存文件", None ,"Text files (*.txt);;All files(*.*)") 
            self.spider.exportEmail(f[0], self.txt_email.toPlainText())
        elif action == 'exportLog':
            f =  QFileDialog.getSaveFileName(self,"保存文件", None ,"Text files (*.txt);;All files(*.*)") 
            self.spider.exportLog(f[0], self.txt_log.toPlainText())
                

    def addSystemTray(self):
        self.tray = QSystemTrayIcon() 

        #self.icon = QIcon(self.spider.logoIconPath)
        self.icon = MyIcon.getLogoIcon()
        self.tray.setIcon(self.icon) 
            

        self.tray.activated.connect(self.clickTray) 
        self.tray.messageClicked.connect(self.clickTray)
        self.tray_menu = QMenu(QApplication.desktop()) 
        self.RestoreAction = QAction('显示', self, triggered=self.restoreAction) 
        self.SettingAction = QAction('设置', self, triggered=self.settingAction) 
        self.QuitAction = QAction('退出', self, triggered=self.exitAction) 
        self.tray_menu.addAction(self.RestoreAction) 
        self.tray_menu.addAction(self.SettingAction) 
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu) 
        self.tray.show()
     
    def settingAction(self):
        self.dlgSetting = DlgSetting(self)
        self.dlgSetting.show()


    def exitAction(self):
        reply = QMessageBox.question(self, '提示', "是否要退出程序吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes: 
            self.exitSystem()
            sys.exit()

    def clickTray(self, reason):
        if reason != QSystemTrayIcon.DoubleClick:
            return
            
        self.restoreAction()

    def restoreAction(self):
        if self.isMaximized():
            self.showMaximized()
        elif self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()
        
        self.activateWindow()
        
        #scrollbar
        self.txt_email.verticalScrollBar().setValue(self.txt_email.verticalScrollBar().maximum())
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    @pyqtSlot()
    def windowIconChanged(self, icon):
        print('changed.')

    @pyqtSlot()
    def on_btn_search_link_clicked(self):
        if len(self.threads) <= 0:
            self.startTime = time.time()

            self.btn_start.setDisabled(True)
            self.btn_resume.setDisabled(True)
            self.btn_stop.setDisabled(False)

            t = threading.Thread(target=self.spider.fetchSearchPageTask,args=())
            self.threads.append(t)
            self.threads[0].setDaemon(True)
            self.threads[0].start()
        else:
            self.log({'str':'已经在有其他进程在运行了，请稍后运行!','extra':None})

    @pyqtSlot()
    def on_btn_saveKeyword_clicked(self):
        if len(self.threads)>0:
            self.log({'str':'已经在有其他进程在运行了，请稍后运行!','extra':None})
            return

        if self.txt_keyword.toPlainText().strip() == '':
            QMessageBox.critical(self, '提示', "请输入关键词！", QMessageBox.Ok, QMessageBox.Ok) 
            return

        #check
        if self.spider.workInterupted():
            reply = QMessageBox.question(self, '提示', "任务尚未完成，您确定要重新设置吗？建议您继续运行完成后重新设置!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
            allow = reply == QMessageBox.Yes
        else:
            allow = True
        if not allow:
            return

        self.spider.saveConfig({
            "isSearchList": 1 if self.chk_searchList.isChecked() else 0, 
            "searchPageSize": self.txt_pageSize.text(), 
            "workQueueSize": self.txt_workSize.text(),
            "searchListDelay": self.txt_searchDelay.text(),
            "searchPageDelay": self.txt_pageDelay.text(),
            "resultMatchPatternType":self.combo_pattern.currentIndex(),
            "maxThreadNum":self.txt_threadNum.text(),
            "searchSource":self.combo_source.currentIndex()
        })
        if self.spider.saveKeyword(self.txt_keyword.toPlainText()) and self.spider.saveKeywordFlag(self.txt_keyword_flag.toPlainText()):
            self.spider.saveResultMatchPattern(self.txt_pattern.toPlainText())
            self.loadSettingData()

            #start
            self.btn_start.setDisabled(True)
            self.btn_resume.setDisabled(True)
            self.btn_stop.setDisabled(False)
            self.btn_saveKeyword.setDisabled(True)

            self.startTime = time.time()
            self.progressBar.setValue(0)

            #thread
            self.threads.clear()
            t = threading.Thread(target=self.spider.createSearchUrlTask,args=())
            self.threads.append(t)
            self.threads[0].setDaemon(True)
            self.threads[0].start()
                
        
        

    @pyqtSlot()
    def on_btn_start_clicked(self):
        if not self.spider.isNetworkConnected():
            QMessageBox.critical(self, '提示', "网络故障，请稍后重试！", QMessageBox.Ok, QMessageBox.Ok) 
            return

        if len(self.threads) <= 0:
            if self.spider.getWorkConfig() == None:
                QMessageBox.critical(self, '提示', "请先保存设置项！", QMessageBox.Ok, QMessageBox.Ok) 
                return

            #check
            if self.spider.workInterupted():
                reply = QMessageBox.question(self, '提示', "任务尚未完成，您确定要重新运行吗？建议您继续运行！", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
                allow = reply == QMessageBox.Yes
            else:
                allow = True
            if not allow:
                return

            self.startTime = time.time()
            self.progressBar.setValue(0)
            
            self.btn_start.setDisabled(True)
            self.btn_resume.setDisabled(True)
            self.btn_stop.setDisabled(False) 
            self.btn_saveKeyword.setDisabled(True) 

            self.threads.clear()
            t = threading.Thread(target=self.spider.fetchSearchListTask,args=(True,False))
            self.threads.append(t)
            self.threads[0].setDaemon(True)
            self.threads[0].start()

        else:
            self.log({'str':'已经在有其他进程在运行了，请稍后运行!','extra':None})

    @pyqtSlot()
    def on_btn_resume_clicked(self):
        if not self.spider.isNetworkConnected():
            QMessageBox.critical(self, '提示', "网络故障，请稍后重试！", QMessageBox.Ok, QMessageBox.Ok) 
            return
            
        if self.spider.getWorkConfig() == None:
            QMessageBox.critical(self, '提示', "请先保存设置项！", QMessageBox.Ok, QMessageBox.Ok) 
            return

        self.resumeAllTask()
        

    def resumeAllTask(self, status=-1):
        if not self.spider.isNetworkConnected():
            self.log({'str':'网络故障，请稍后重试!','extra':None})
            return

        if len(self.threads) <= 0:
            if status != -2:
                self.startTime = time.time()

            self.progressBar.setValue(0)
            
            self.btn_start.setDisabled(True)
            self.btn_resume.setDisabled(True)
            self.btn_stop.setDisabled(False)   
            self.btn_saveKeyword.setDisabled(True) 

            self.threads.clear()
            t = threading.Thread(target=self.spider.fetchSearchListTask,args=(True,True))
            self.threads.append(t)
            self.threads[0].setDaemon(True)
            self.threads[0].start()
        else:
            self.log({'str':'已经在有其他进程在运行了，请稍后运行!','extra':None})
        
    @pyqtSlot()
    def on_btn_stop_clicked(self):
        self.stopAllTask()

    def stopAllTask(self, status=-1):
        self.log({'str':'开始停止所有任务...','extra':None})
        
        self.spider.stopCreateSearchUrlTask()
        self.spider.stopSearchListTask(status)
        self.spider.stopSearchPageTask(status)
        self.threads.clear()

        self.btn_start.setDisabled(False)
        self.btn_resume.setDisabled(False)
        self.btn_stop.setDisabled(True)
        self.btn_saveKeyword.setDisabled(False)

        if status != -2:
            self.startTime = 0

    def loadSettingData(self):
        keyword = self.spider.getKeyword()
        keywordFlag = self.spider.getKeywordFlag()

        self.txt_keyword.setPlainText(keyword)
        self.txt_keyword_flag.setPlainText(keywordFlag)
        self.txt_pattern.setPlainText(self.spider.getResultMatchPattern())
        self.title_keyword.setText('搜索关键词(%s)' % (format(len(keyword.split('\n')),'0,') if keyword!='' else 0))
        self.title_keywordFlag.setText('附加关键词(%s)' % (format(len(keywordFlag.split('\n')),'0,') if keywordFlag!='' else 0))

        #load config
        self.config = self.spider.getConfig()
        self.chk_searchList.setChecked(1 if self.config['isSearchList']=='1' else 0)
        self.txt_pageSize.setText(self.config['searchPageSize'])
        self.txt_workSize.setText(self.config['workQueueSize'])
        self.txt_searchDelay.setText(self.config['searchListDelay'])
        self.txt_pageDelay.setText(self.config['searchPageDelay'])
        self.txt_pageDelay.setText(self.config['searchPageDelay'])
        self.txt_threadNum.setText(self.config['maxThreadNum'])
        self.combo_pattern.setCurrentIndex(int(self.config['resultMatchPatternType']))

        if len(self.config['searchSourceList']) > 1:
            self.combo_source.clear()
            for i in self.config['searchSourceList']:
                self.combo_source.addItem(i)
            self.combo_source.setCurrentIndex(int(self.config['searchSource']))
        else:
            self.combo_source.setHidden(True)


        self.progressBar.setValue(self.spider.getWorkProgress())
        
        if self.config['debug'] == '1' and self.config['isSearchList'] == '1':
            self.btn_search_link.setHidden(False)
        else:
            self.btn_search_link.setHidden(True)

        if self.spider.getKeyword() == '':
            self.btn_start.setDisabled(True)
            self.btn_resume.setDisabled(True)

    def loadEmail(self):
        if not self.thread_load_email or not self.thread_load_email.isAlive():
            self.thread_load_email = threading.Thread(target=self.spider.loadEmails,args=())
            self.thread_load_email.setDaemon(True)
            self.thread_load_email.start()
            self.log({'str':'正在从文件中载入Email...','extra':None})
        else:
            self.log({'str':'Email线程正在运行，请等待!','extra':None})
    
    def setTimer(self):
        if self.startTime>0:
            self.lbl_timer.setText(self.convertTime(time.time() - self.startTime))

        #other setting
        if self.settings['chkStart']:
            startTime = time.strptime(time.strftime('%Y-%m-%d') + ' ' + self.settings['timeStart'], '%Y-%m-%d %H:%M:%S')
            if time.localtime() >= startTime and self.timeStartDate != time.strftime('%Y-%m-%d'):
                self.timeStartDate = time.strftime('%Y-%m-%d')
                self.resumeAllTask(-1)

        if self.settings['chkEnd']:
            endTime = time.strptime(time.strftime('%Y-%m-%d') + ' ' + self.settings['timeEnd'], '%Y-%m-%d %H:%M:%S')
            if time.localtime() >= endTime and self.timeEndDate != time.strftime('%Y-%m-%d'):
                self.timeEndDate = time.strftime('%Y-%m-%d')
                self.stopAllTask(-1)

    def convertTime(self, raw_time):
        hour = int(raw_time // 3600)
        minute = int((raw_time % 3600) // 60)
        second = int(raw_time % 60)

        return '{:0>2d}:{:0>2d}:{:0>2d}'.format(hour, minute, second)

    def clearSystem(self):
        log = self.txt_log.toPlainText()
        c = log.count('\n') + 1
        maxLine = self.spider.autoSaveLogSize
        
        if c > maxLine:
            if self.spider.saveLog(log):
                self.txt_log.clear()
        del log

        self.spider.saveSystemData()
        self.loadEmail()


    def exitSystem(self):
        if self.tray:
            self.tray.hide()
        self.spider.exitSystem()

    def exitAll(self):
        if self.tray:
            self.tray.hide()
        sys.exit()


    def log(self, o):
        self.txt_log.appendPlainText('['+time.strftime("%H:%M:%S", time.localtime()) + ']' + o['str']) 

        if o['extra']:
            if o['extra'][0] == 'exit':
                QMessageBox.critical(self, '提示', o['str'], QMessageBox.Ok, QMessageBox.Ok) 
                sys.exit()

            if o['extra'][0] == 'data-loaded':
                self.emailCount = len(o['extra'][1])
                self.txt_email.setPlainText("".join(o['extra'][1]))
                self.lbl_email.setText("已载入 %s 个Email" % format(self.emailCount,'0,'))

                #self.txt_email.verticalScrollBar().setValue(self.txt_email.verticalScrollBar().maximum())
            elif o['extra'][0] == 'data-update':
                self.emailCount += len(o['extra'][1])
                self.txt_email.appendPlainText("\n".join(o['extra'][1]))
                self.lbl_email.setText("已获取 %s 个Email" % format(self.emailCount,'0,'))

                #self.txt_email.verticalScrollBar().setValue(self.txt_email.verticalScrollBar().maximum())
            elif o['extra'][0] == 'createurl-end':
                self.btn_start.setDisabled(False)
                self.btn_resume.setDisabled(False)
                self.btn_stop.setDisabled(False)
                self.btn_saveKeyword.setDisabled(False)

                self.threads.clear()

                self.startTime = 0
            elif o['extra'][0] == 'link-end':
                self.btn_start.setDisabled(False)
                self.btn_resume.setDisabled(False)
                self.btn_stop.setDisabled(False)   
                self.btn_saveKeyword.setDisabled(False) 

                self.threads.clear()
                
                if not self.chk_searchList.isChecked() and not self.spider.taskInterrupted():
                    self.startTime = 0

            elif o['extra'][0] == 'work-end':
                self.btn_start.setDisabled(False)
                self.btn_resume.setDisabled(False)
                self.btn_stop.setDisabled(False) 
                self.btn_saveKeyword.setDisabled(False) 

                self.threads.clear()

                if not self.spider.taskInterrupted():
                    self.startTime = 0

            elif o['extra'][0] == 'check-end' and o['extra'][1]['allowUpgrade']:
                reply = QMessageBox.question(self, '提示', "发现新版本，您确认要更新吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
                if reply == QMessageBox.Yes: 
                    mainScript = os.path.basename(sys.argv[0])[0:os.path.basename(sys.argv[0]).rfind('.')]
                    self.spider.runScriptFile(self.spider.updaterFilePath, ' -s' + mainScript)
                    self.exitAll()
            elif o['extra'][0] == 'network-stop':
                self.stopAllTask(-2)
            elif o['extra'][0] == 'network-resume':
                self.resumeAllTask(-2)

            #progress
            if o['extra'][0] in ['link-end','work-end','link-progress','work-progress','createurl-progress']:
                o['extra'][1]>self.progressBar.value() and self.progressBar.setValue(o['extra'][1])

        #scrollbar
        #self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())
    
    def loadData(self):
        self.btn_stop.setDisabled(True)
        self.txt_log.setReadOnly(True)

        self.txt_log.clear()
        self.txt_email.clear()
        self.txt_keyword.clear()
        self.txt_keyword_flag.clear()
        self.txt_pattern.clear()

        self.loadEmail()

        self.timer = QTimer()
        self.timer.timeout.connect(self.setTimer)
        self.timer.start(1000)

        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.clearSystem)
        self.log_timer.start(self.spider.clearSystemInterval)

        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.checkNetworkStatus)
        self.network_timer.start(self.spider.networkConnectionCheckInterval)

        #self.startTime = time.time()

        self.loadSettingData()

        #check upgrade
        t1 = threading.Thread(target=self.spider.checkUpgrade,args=())
        t1.setDaemon(True)
        t1.start()
        
        if self.config['debug'] == '1':
            self.usage_timer = QTimer()
            self.usage_timer.timeout.connect(self.loadUsage)
            self.usage_timer.start(self.spider.systemMonitorInterval)
            self.loadUsage()
        
        #spitter
        splitter  =  QSplitter(self)
        splitter.addWidget(self.groupBox)
        splitter.addWidget(self.groupBox_2)
        splitter.addWidget(self.groupBox_3)
        splitter.setContentsMargins(9,9,9,9)
        splitter.setOrientation(Qt.Vertical)
        self.setCentralWidget(splitter)

    def loadUsage(self):
        self.statusBar().showMessage(self.spider.getUsageInfo())

    def checkNetworkStatus(self):
        if not self.thread_check_network or not self.thread_check_network.isAlive():
            self.thread_check_network = threading.Thread(target=self.spider.checkNetworkStatus,args=())
            self.thread_check_network.setDaemon(True)
            self.thread_check_network.start()
            #self.log({'str':'正在启动检查网络连接...','extra':None})
        else:
            #self.log({'str':'检查网络连接线程正在运行，请等待!','extra':None})
            pass
        


#common func
def isNewSystem():
    return float('%d.%d' % (sys.version_info[0],sys.version_info[1])) >= 3.7

def isWindows():
    return platform.system() == 'Windows'

#handle error
def saveError(v):
    #save
    s = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']\n' + v + '\n'
    p = os.path.dirname(os.path.realpath(sys.argv[0])) + '/error.log'
    with open(p, "a+", encoding="utf-8") as f:
        f.write(s)
def errorHandler(type, value, trace):  
    v = 'Main Error: \n%s' % (''.join(traceback.format_exception(type, value, trace)))
    print(v)
    saveError(v)
    sys.__excepthook__(type, value, trace) 
sys.excepthook = errorHandler

#main
if __name__ == '__main__':
    #scale
    if isNewSystem():QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    if isNewSystem():app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setQuitOnLastWindowClosed(False)

    #icon
    '''
    import ctypes
    from PyQt5.QtGui import QImageReader
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("spider")
    print(QImageReader.supportedImageFormats())
    if os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0])) + '/logo.png'):
        app.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(sys.argv[0])) + '/logo.png'))
    '''

    #style
    """
    import qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    """
    '''
    #style_blue style_black style_Classic style_Dark style_DarkOrange style_gray style_navy
    import PyQt5_stylesheets
    app.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_blue"))
    '''
    if os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0])) + '/qss/default.qss'):
        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + '/qss/default.qss', 'r') as f:
            app.setStyleSheet(f.read())

    

    dlg = MainWindow()

    #single instance
    if  isWindows() and isNewSystem():
        import win32con,win32file,pywintypes
        
        LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
        LOCK_SH = 0
        LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
        __overlapped = pywintypes.OVERLAPPED()

        pid_dir = dlg.spider.tmpPath
        self_name = os.path.basename(sys.argv[0])[0:os.path.basename(sys.argv[0]).rfind('.')]
        if os.path.exists(pid_dir):
            try:
                fd = open(pid_dir + '/'+self_name+'.pid', 'w')
                hfile = win32file._get_osfhandle(fd.fileno())
                win32file.LockFileEx(hfile, LOCK_EX | LOCK_NB, 0, 0xffff0000,__overlapped)
                #print('获取文件锁成功！')
            except:
                #print('获取文件锁失败！')
                QMessageBox.critical(dlg, '提示', "程序已经在运行了，请点击右下角托盘程序图标恢复！", QMessageBox.Ok, QMessageBox.Ok) 
                #sys.exit(app.exec_())
                sys.exit()
    elif not isWindows():
        import fcntl
        pid_dir = dlg.spider.tmpPath
        self_name = os.path.basename(sys.argv[0])[0:os.path.basename(sys.argv[0]).rfind('.')]
        if os.path.exists(pid_dir):
            try:
                fd = open(pid_dir + '/'+self_name+'.pid', 'w')
                fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                #print('获取文件锁成功！')
            except:
                #traceback.print_exc()
                #print('获取文件锁失败！')
                QMessageBox.critical(dlg, '提示', "程序已经在运行了，请点击右下角托盘程序图标恢复！", QMessageBox.Ok, QMessageBox.Ok) 
                #sys.exit(app.exec_())
                sys.exit()
    
    
    #resize
    desktop = QApplication.desktop()
    screenRect = desktop.availableGeometry()
    dlgRect = dlg.geometry()
    if screenRect.width() < dlgRect.width() or screenRect.height()<dlgRect.height():
        dlg.resize(screenRect.width(), screenRect.height())
        dlg.showMaximized()
        dlg.show()
    else:
        #dlg.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        dlg.show()
    del desktop
    del screenRect
    del dlgRect

    #show window
    try:
        #dlg.setWindowIcon(QIcon(dlg.spider.logoIconPath))
        dlg.setWindowIcon(MyIcon.getLogoIcon())
        dlg.setWindowTitle('Spider (%s)' % os.path.realpath(sys.argv[0]))
        dlg.loadData()
        if isWindows():
            dlg.addSystemTray()
        dlg.addContextMenu()
    except:
        traceback.print_exc()
        saveError('Startup Error:\n' + traceback.format_exc())
    finally:
        sys.exit(app.exec_())
