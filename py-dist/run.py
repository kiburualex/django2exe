# An example of embedding CEF browser in a PyQt4 application.
# Tested with PyQt 4.10.3 (Qt 4.8.5).
import re, os, sys, platform, traceback, time, codecs 
import subprocess,time,socket
import json
import compileall
from distutils import util

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

proc = None
class Info:
    def __init__(self):
        self.initial_width = 800
        self.initial_height = 600
        self.max_width = 0
        self.max_height = 0
        self.min_width = 800
        self.min_height = 600
        self.window_title = "Ideal POS"
        self.icon_name = "icon.png"
        self.fullscreen_allowed = True
        self.project_dir_name="app"
        self.project_dir_path="../app/"
        self.dev_tools_menu_enabled = True
        self.__file__ = '__file__'
        self.libcef_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'libcef.dll')
        self.splashscreen_img = "splashscreen.png"


    def processconfiguration(self):
        config_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config','config.json'))
        try:
            with open(config_file_path) as data_file:    
                data = json.load(data_file)
                self.splashscreen_img = data["splashscreen_img"]
                django_app_data = data["application"]
                self.project_dir_name = django_app_data["project_dir_name"]
                self.project_dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',self.project_dir_name))
                window_data= data["window"]
                self.dev_tools_menu_enabled = bool(util.strtobool(window_data["dev_tools_menu_enabled"].lower()))
                self.initial_width = int(window_data["width"])
                self.initial_height = int(window_data["height"])
                self.min_width = int(window_data["min_width"])
                self.min_height = int(window_data["min_height"])
                self.window_title = window_data["title"]
                icon_name = window_data["icon"]
                self.icon_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config',icon_name))
                self.fullscreen_allowed =  bool(util.strtobool(window_data["fullscreen_allowed"].lower()))
                self.max_width = int(window_data["max_width"])
                self.max_height = int(window_data["max_height"])
                database_data= data["database"]
                self.dbhost = database_data["dbhost"]
                self.dbname = database_data["dbname"]
                self.dbuser = database_data["dbuser"]
                self.dbpassword = database_data["dbpassword"]
        except Exception as e:
            print (e)
            print ("Failed Reading Config")

    def check_if_migration_performed(self):
        if os.path.exists('migrate.py'):
            from migrate import Database
            db = Database()
            db.makeMigrationsAndmigrate()
            os.remove('migrate.py')

info = Info()
if os.path.exists(info.libcef_dll):
    # Import a local module
    if (2,7) <= sys.version_info < (2,8):
        import cefpython_py27 as cefpython
    elif (3,4) <= sys.version_info < (3,4):
        import cefpython_py34 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import an installed package
    from cefpython3 import cefpython

def GetApplicationPath(file=None):
    # import re, os, platform
    # On Windows after downloading file and calling Browser.GoForward(),
    # current working directory is set to %UserProfile%.
    # Calling os.path.dirname(os.path.realpath(__file__))
    # returns for eg. "C:\Users\user\Downloads". A solution
    # is to cache path on first call.
    if not hasattr(GetApplicationPath, "dir"):
        if hasattr(sys, "frozen"):
            dir = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            dir = os.path.dirname(os.path.realpath(__file__))
        else:
            dir = os.getcwd()
        GetApplicationPath.dir = dir
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        path = GetApplicationPath.dir + os.sep + file
        if platform.system() == "Windows":
            path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)

def ExceptHook(excType, excValue, traceObject):
    # import traceback, os, time, codecs
    # This hook does the following: in case of exception write it to
    # the "error.log" file, display it to the console, shutdown CEF
    # and exit application immediately by ignoring "finally" (os._exit()).
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    errorFile = GetApplicationPath("error.log")
    try:
        appEncoding = cefpython.g_applicationSettings["string_encoding"]
    except:
        appEncoding = "utf-8"
    if type(errorMsg) == bytes:
        errorMsg = errorMsg.decode(encoding=appEncoding, errors="replace")
    try:
        with codecs.open(errorFile, mode="a", encoding=appEncoding) as fp:
            fp.write("\n[%s] %s\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S"), errorMsg))
    except:
        print("[run.py] WARNING: failed writing to error file: %s" % (
                errorFile))
    # Convert error message to ascii before printing, otherwise
    # you may get error like this:
    # | UnicodeEncodeError: 'charmap' codec can't encode characters
    errorMsg = errorMsg.encode("ascii", errors="replace")
    errorMsg = errorMsg.decode("ascii", errors="replace")
    print("\n"+errorMsg+"\n")
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    os._exit(1)

class MainWindow(QtGui.QMainWindow):
    mainFrame = None

    def __init__(self):
        super(MainWindow, self).__init__(None)
        info = Info()
        info.processconfiguration()
        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.setMinimumSize(info.min_width,info.min_height)
        if info.fullscreen_allowed == False and info.max_height != 0 and info.max_width != 0: 
            self.setMaximumSize(info.max_width,info.max_height)
        self.resize(info.initial_width, info.initial_height)
        self.setWindowTitle(info.window_title)
        self.setWindowIcon(QtGui.QIcon(info.icon_name))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def createMenu(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(QtGui.QAction("Open", self))
        filemenu.addAction(QtGui.QAction("Exit", self))
        aboutmenu = menubar.addMenu("&About")

    def focusInEvent(self, event):
        cefpython.WindowUtils.OnSetFocus(int(self.centralWidget().winId()), 0, 0, 0)

    def closeEvent(self, event):
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
        self.mainFrame.browser.CloseBrowser()

class MainFrame(QtGui.QWidget):
    browser = None

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(int(self.winId()))    
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1',8000))
            sock.close()
            if result == 0:
                break
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=GetApplicationPath("http://127.0.0.1:8000"))
        self.show()



    def moveEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

    def resizeEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

class CefApplication(QtGui.QApplication):
    timer = None

    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.createTimer()

    def createTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(10)

    def onTimer(self):
        # The proper way of doing message loop should be:
        # 1. In createTimer() call self.timer.start(0)
        # 2. In onTimer() call MessageLoopWork() only when
        #    QtGui.QApplication.instance()->hasPendingEvents() returns False.
        # But... there is a bug in Qt, hasPendingEvents() returns always true.
        cefpython.MessageLoopWork()

    def stopTimer(self):
        # Stop the timer after Qt message loop ended, calls to MessageLoopWork()
        # should not happen anymore.
        self.timer.stop()


if __name__ == '__main__':

    appscreen = QApplication(sys.argv)
    info = Info()
    info.processconfiguration()

    # Create and display the splash screen
    splash_pix = QPixmap(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'img', info.splashscreen_img)))

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)

    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
    progressBar.setStyleSheet ("QProgressBar {border: 2px solid beige;border-radius: 5px;margin-left: 14ex;margin-right: 14ex;text-align: center;} QProgressBar::chunk {background-color: #0A2F3D;width: 20px;margin: 0.5px;}")

    splash.show()
    splash.showMessage("<h1><font color='white'>Configuring the server, Please wait ....</font></h1>", Qt.AlignTop | Qt.AlignCenter, Qt.black)
    
    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
            appscreen.processEvents()
            info.check_if_migration_performed()

    proc = subprocess.Popen(['python','..\\' + info.project_dir_name + '\manage.pyc','runserver','127.0.0.1:8000'])
    print("[pyqt.py] PyQt version: %s" % QtCore.PYQT_VERSION_STR)
    print("[pyqt.py] QtCore version: %s" % QtCore.qVersion())

    # Intercept python exceptions. Exit app immediately when exception
    # happens on any of the threads.
    sys.excepthook = ExceptHook

    # Application settings
    settings = {
        # "cache_path": "webcache/", # Disk cache
        "debug": True, # cefpython debug messages in console and in log_file
        "log_severity": cefpython.LOGSEVERITY_INFO, # LOGSEVERITY_VERBOSE
        "log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess"),
        "context_menu":{
            "enabled" : info.dev_tools_menu_enabled
        },
    }

    # Command line switches set programmatically
    switches = {
        # "proxy-server": "socks5://127.0.0.1:8888",
        # "enable-media-stream": "",
        # "--invalid-switch": "" -> Invalid switch name
    }

    cefpython.Initialize(settings, switches)

    app = CefApplication(sys.argv)

    mainWindow = MainWindow()
    splash.close()
    mainWindow.show()
    app.exec_()
    app.stopTimer()

    # Need to destroy QApplication(), otherwise Shutdown() fails.
    # Unset main window also just to be safe.
    del mainWindow
    del app
    cefpython.Shutdown()
    os._exit(1)