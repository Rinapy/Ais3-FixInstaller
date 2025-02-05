import sys
import time

import psutil
import requests
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QMainWindow, QDialog, QCheckBox)

from fixprocess import (
    login,
    parse_fix,
    download_fixs,
    get_install_version,
    kill_ais_process
)
from arhivework import (
    unpack_fix_zip,
    create_sfx,
    unpack_fix_ais,
    clean_directory
)
from template import login_form
from template import main


from exceptions import LoginError


class Login_dialog(QDialog):
    def __init__(self):
        super().__init__()

        # use the Ui_login_form
        self.ui = login_form.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.authenticate)
        # show the login window
        self.show()

    def authenticate(self):
        login_value = self.ui.login_line_edit.text()
        password_value = self.ui.password_line_edit.text()
        try:
            self.response, self.cookies = login(login_value, password_value)
            self.accept()
        except LoginError:
            QMessageBox.warning(self, 'Ошибка авторизации',
                                'Неверный пользователь или пароль!')
        except (ConnectionError, requests.RequestException):
            QMessageBox.warning(self, 'Ошибка авторизации',
                                'Отсутствует подключение')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        # use the Ui_login_form
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.download_button.clicked.connect(self.download)
        self.ui.progressBar.setValue(0)
        self.ui.create_sfx_button.clicked.connect(self.create_sfx)
        self.ui.install_button.clicked.connect(self.install)
        self.ui.ais_version.setText(get_install_version())

    def initScrollArea(self, response) -> None:
        self.fix_check_box = []
        self.fix_dict = parse_fix(response.text)
        for fix_name in self.fix_dict.keys():
            check_box = QCheckBox(fix_name, self)
            check_box.setObjectName(fix_name)

            self.fix_check_box.append(check_box)
            self.ui.verticalLayout.addWidget(check_box)

    def setInfo(self, response, cookies, login) -> None:
        self.response = response
        self.cookies = cookies
        self.login = login
        self.initScrollArea(response)

    def download(self) -> bool:
        self.ui.progressBar.setValue(0)
        accpet_fix_list = []
        value = 0
        for accpet_fix in self.fix_check_box:
            if accpet_fix.isChecked():
                value += 1
                accpet_fix_list.append(accpet_fix.text())
        if len(accpet_fix_list) == 0:
            QMessageBox.warning(self, 'Ошибка', 'Вы не выбрали ни один фикс!')
            return False
        self.progress_value = int(100/value)
        progress = 0
        download_fixs(accpet_fix_list, self.fix_dict, self.cookies)
        for i in range(value):
            i += 1
            progress += self.progress_value
            time.sleep(1)
            self.ui.progressBar.setValue(int(progress))
        if progress != 100:
            progress = 100 - progress + progress
            self.ui.progressBar.setValue(int(progress))
        return True

    def kill_ais(self) -> None:
        for proc in psutil.process_iter():
            name = proc.name()
            if (name == 'CommonComponents.UserAgent.exe' or
                    name == 'CommonComponents.UnifiedClient.exe'):
                QMessageBox.warning(
                    self,
                    'Fix Installer',
                    'Внимание! АИС будет закрыт, после нажатия ОК.')
                kill_ais_process()
                time.sleep(3)

    def create_sfx(self) -> None:
        if self.download():
            unpack_fix_zip()
            create_sfx()
            clean_directory()

    def install(self) -> None:
        if self.download():
            self.kill_ais()
            unpack_fix_ais()
            clean_directory()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_dialog = Login_dialog()
    if not login_dialog.exec_():
        sys.exit(-1)
    main_window = MainWindow(login_dialog.response)
    main_window.setInfo(login_dialog.response, login_dialog.cookies,
                        login_dialog.ui.login_line_edit.text())
    main_window.show()
    sys.exit(app.exec_())
