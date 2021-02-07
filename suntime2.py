from gui import AppBundle
import sys

if __name__ == '__main__':
    app = AppBundle()
    app.window.show()
    sys.exit(app.application.exec_())
