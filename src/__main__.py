from PyQt5.QtCore import QThreadPool

from src.gui import app
import sys

if __name__ == '__main__':
    pool = QThreadPool.globalInstance()
    pool.setMaxThreadCount(pool.maxThreadCount());

    app.start(sys.argv)
