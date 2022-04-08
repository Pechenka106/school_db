import sqlite3
import sys
import os
import datetime as dt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

iskl = ["qwe", "wer", "ert", "rty", "tyu", "yui", "uio", "iop",
        "asd", "sdf", "dfg", "fgh", "ghj", "hjk", "jkl",
        "zxc", "xcv", "cvb", "vbn", "bnm",
        "йцу", "цук", "уке", "кен", "енг", "нгш", "гшщ", "шщз", "щзх", "зхъ", "хъё",
        "фыв", "ыва", "вап", "апр", "про", "рол", "олд", "лдж", "джэ", "жэё",
        "ячс", "чсм", "сми", "мит", "ить", "тьб", "ьбю"]


def wtl(text='flag'):
    # wtl -> write to logs
    print(f'{dt.datetime.now()} -> {text}', file=logs)


def check(obj):
    students = obj.cur.execute("SELECT * FROM students").fetchall()
    students_table = []
    for row in range(len(obj.db)):
        lst = []
        for col in range(9):
            if obj.table.item(row, col).text() == '':
                lst.append('None')
            else:
                lst.append(obj.table.item(row, col).text())
        students_table.append(lst)
    if [[str(h) for h in list(i)] for i in students] != students_table:
        wtl('check unsuccess')
        return True
    wtl('check success')
    return False


def check_password(password):
    if len(password) < 8:
        return False, 'Длина пароля должна быть как минимум 8 символов'
    if password.lower() == password:
        return False, 'В пароле должны присутствовать символы разных регистров'
    if password.upper() == password:
        return False, 'В пароле должны присутствовать символы разных регистров'
    if not any([i in password for i in list('0123456789')]):
        return False, 'В пароле должна быть как минимум 1 цифра'
    if any([i in password.lower() for i in iskl]):
        return False, 'В пароле не должны присутствовать 3 подряд идущих символа'
    return True, ''


def check_data(data):
    try:
        if data.strip() == '':
            return True, ''
        if data.count('/') < 2 or len(data) < 10 or data[2] != '/' or data[5] != '/':
            return False, 'Неверный формат даты'
        if not (0 < int(data.split('/')[0]) < 32):
            return False, 'Неверно задан день'
        if not (0 < int(data.split('/')[1]) < 13):
            return False, 'Неверно задан месяц'
        if dt.date(*[int(i) for i in data.split('/')[::-1]]) >= dt.date.today():
            return False, 'Введенная дата не может превышать текущую'
        return True, ''
    except Exception as error:
        print(error)
        wtl(f'error: {error}')
        return False, 'Возникла непредвиденная ошибка'


def check_phone(number):
    def rangelist(i):
        for i in range(i[0], i[1]):
            code_phone.append(i)
    number = ''.join(number.split())
    try:
        if number[:2] == '+7':
            pass
        elif number[0] == '8':
            number = list(number)
            number[0] = '+7'
            number = ''.join(number)
        else:
            raise TypeError
        if number[0] == '-' or number[-1] == '-':
            raise TypeError
        number = number.split('-')
        for i in list(number):
            if i == '':
                raise TypeError
        number = str(number)
        if number.find('(') > number.find(')'):
            raise TypeError
        elif (number.count('(') == 0 and number.count(')') > 0):
            raise TypeError
        elif (number.count(')') == 0 and number.count('(') > 0):
            raise TypeError
        elif number.count('(') > 1 or number.count(')') > 1:
            raise TypeError
        spis = []
        for i in range(len(number)):
            if number[i] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+'):
                spis.append(number[i])
        number = ''.join(spis)
        if len(number) != 12:
            raise NameError
        rangelst = [(910, 920), (980, 990), (920, 940), (902, 907), (960, 970)]
        code_phone = []
        for i in rangelst:
            rangelist(i)
        if int(number[2:5]) not in code_phone:
            raise ValueError
        return True, ''
    except TypeError:
        return False, 'неверный формат'
    except NameError:
        return False, 'неверное количество цифр'
    except ValueError:
        return False, 'не определяется оператор сотовой связи'


class AuthorisedWindow(QWidget):
    def __init__(self, name_db='school_db.sqlite'):
        super().__init__()
        self.name_db = name_db
        self.initUI()

    def initUI(self):
        uic.loadUi('auth_page.ui', self)
        self.setWindowTitle('Авторизация')
        self.setWindowIcon(QtGui.QIcon('icons/icon_auth.png'))
        self.cur = sqlite3.connect(self.name_db)
        self.cur.cursor()
        self.login.setFocus()
        self.auth_btn.clicked.connect(self.check)
        self.auth_btn.setToolTip('Войти в аккаунт')
        self.show()
        wtl('load success')

    def keyPressEvent(self, event):
        try:
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                wtl('press enter')
                if self.login.text() != '' and self.password.text() == '':
                    self.password.setFocus()
                    wtl('password set focus(enter)')
                elif self.login.text() != '' and self.password.text() != '':
                    self.check()
                    wtl('check user data')
                else:
                    self.login.setFocus()
                    wtl('login set focus(enter)')
            elif event.key() == Qt.Key_Up:
                self.login.setFocus()
                wtl('login set focus(up)')
            elif event.key() == Qt.Key_Down:
                self.password.setFocus()
                wtl('password set focus(down)')
        except Exception as error:
            wtl(f'error: {error}')

    def check(self):
        db = self.cur.execute("SELECT * FROM users").fetchall()
        try:
            if [i[1] for i in db].index(self.login.text()) == [h[2] for h in db].index(self.password.text()):
                wtl('authorise successful')
                self.id = db[[i[1] for i in db].index(self.login.text())][0]
                self.FI = self.cur.execute(f"SELECT Фамилия, Имя FROM students WHERE Id = "
                                           f"{self.id}").fetchall()
                ex.load_interface()
                wtl('start_main_successful')
                self.hide()
            else:
                raise Exception

        except Exception as error:
            print(error)
            QMessageBox.information(self, 'Внимание', 'Неверный логин или пароль')
            wtl(f'error: {error}')


class StudentPage(QWidget):
    def __init__(self, row):
        super().__init__()
        self.row = row + 1
        self.initUI()

    def initUI(self):
        try:
            uic.loadUi('student_page.ui', self)
            self.cur = sqlite3.connect(ex.name_db)
            self.cur.cursor()
            self.info = ex.db[self.row - 1]
            for index, obj in enumerate(self.info):
                if obj is None:
                    self.info[index] = ''
            self.Id.setText(f'Id = {self.info[0]}')
            self.F.setText(self.info[1])
            self.I.setText(self.info[2])
            self.O.setText(self.info[3])
            self.clas.setText(self.info[4])
            self.phone.setText(self.info[5])
            self.address.setText(self.info[6])
            self.data.setText(self.info[7])
            self.other.setText(self.info[8])
            user_data = ex.user_data[self.row - 1]
            self.login, self.password, self.status = str(user_data[1]), user_data[2], user_data[3]
            self.setWindowTitle(f'Карточка пользователя {" ".join([self.info[1], self.info[2], self.info[3]]).strip()}'
                                f' ({self.status})')
            self.setWindowIcon(QtGui.QIcon('icons/student_site_icon.png'))
            self.icon_way = ex.icons[self.row - 1][-1]
            self.load.clicked.connect(self.load_picture)
            self.corr_icon_way = self.icon_way[:]
            self.load_icon(self.icon_way)
        except Exception as error:
            print(f'{error} test')
            wtl(f'error: {error}')

    def load_icon(self, icon_way):
        pixmap = QPixmap(icon_way)
        self.icon.setPixmap(pixmap.scaled(256, 340))
        self.corr_icon_way = icon_way

    def closeEvent(self, event):
        try:
            if self.check_data() or self.check_phone():
                event.ignore()
                raise Exception
            info = ex.db[self.row - 1][:]
            for i in range(1, 4):
                info[i] = info[i].capitalize()
            corr_info = []
            corr_info.append(self.Id.text().split(' ')[-1].strip())
            corr_info.append(self.F.text().capitalize())
            corr_info.append(self.I.text().capitalize())
            corr_info.append(self.O.text().capitalize())
            corr_info.append(self.clas.text().strip())
            corr_info.append(self.phone.text().strip())
            corr_info.append(self.address.text().strip())
            corr_info.append(self.data.text().strip())
            corr_info.append(self.other.toPlainText())
            corr_info.append(self.corr_icon_way)
            info.append(self.icon_way)
            if info != corr_info:
                reply = QMessageBox.question(self, 'Внимание',
                                             'В карточке есть несохранённые изменения. Хотите сохранить изменения?',
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    for i, obj in enumerate(ex.db):
                        if obj[0] == info[0]:
                            ex.db[self.row - 1] = [corr_info[0], corr_info[1], corr_info[2], corr_info[3], corr_info[4],
                                                   corr_info[5], corr_info[6], corr_info[7], corr_info[8]]
                            ex.icons[i] = (self.row, self.corr_icon_way)
                            ex.load_table()
                    self.hide()
                else:
                    event.ignore()
            else:
                event.accept()
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def load_picture(self):
        try:
            icon_way = QFileDialog.getOpenFileName(self, 'Открыть', '',
                                                   'Картинка (*jpg);;Картинка (*png);;Все файлы (*)')[0]
            self.load_icon(icon_way)
        except Exception as error:
            wtl(f'error: {error}')
            QMessageBox.information(self, 'Внимание', 'Некоректный файл', QMessageBox.Ok)

    def check_data(self):
        try:
            chck = check_data(self.data.text())
            if not chck[0]:
                wtl(chck[1])
                QMessageBox.information(self, 'Внимание', chck[1], QMessageBox.Ok)
            return chck[1]
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def check_phone(self):
        try:
            chck = check_phone(self.phone.text())
            if not chck[0]:
                wtl(chck[1])
                QMessageBox.information(self, 'Внимание', chck[1], QMessageBox.Ok)
            return chck[1]
        except Exception as error:
            print(error)
            wtl(f'error: {error}')


class AddWindow(QWidget):
    def __init__(self, status):
        super().__init__()
        self.status = status
        self.initUI()

    def initUI(self):
        uic.loadUi('add.ui', self)
        self.setWindowIcon(QtGui.QIcon('icons/add_icon.png'))
        self.setWindowTitle(f'Добавить карточку {self.status}')
        self.icon_way = ''
        self.load.clicked.connect(self.load_picture)
        self.save.clicked.connect(self.save_data)
        if self.status == 'Ученик':
            self.login.hide()
            self.password.hide()
            self.lbl.hide()
            self.lbl2.hide()

    def save_data(self):
        try:
            if self.check_login():
                raise Exception
            elif self.check_password():
                raise Exception
            elif self.check_data():
                raise Exception
            elif self.check_phone():
                raise Exception
            if self.F.text() == '' and self.I.text() == '' and self.O.text() == '':
                QMessageBox.information(self, 'Внимание', 'В карточке обязательно дожно быть ФИО', QMessageBox.Ok)
                raise Exception
            ex.db.append([len(ex.db) + 1, self.F.text().capitalize(), self.I.text().capitalize(),
                          self.O.text().capitalize(), self.clas.text(), self.phone.text(), self.address.text(),
                          self.data.text(), self.other.toPlainText()])
            if self.status != 'Ученик':
                ex.user_data.append([len(ex.user_data) + 1, self.login.text(), self.password.text(), self.status])
            else:
                ex.user_data.append([len(ex.user_data) + 1, None, None, self.status])
            ex.icons.append([len(ex.icons) + 1, self.icon_way])
            ex.load_table()
            QMessageBox.information(self, 'Сообщение', 'Карточка была успешно добавленна', QMessageBox.Ok)
            self.close()
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def load_picture(self):
        try:
            self.icon_way = QFileDialog.getOpenFileName(self, 'Открыть', '',
                                                        'Картинка (*jpg);;Картинка (*png);;Все файлы (*)')[0]
            self.icon.setPixmap(QPixmap(self.icon_way).scaled(256, 340))
        except Exception as error:
            wtl(f'error: {error}')
            QMessageBox.information(self, 'Внимание', 'Некоректный файл', QMessageBox.Ok)

    def check_data(self):
        try:
            if self.data.text() == '':
                return False
            chck = check_data(self.data.text())
            if not chck[0]:
                wtl(chck[1])
                QMessageBox.information(self, 'Внимание', chck[1], QMessageBox.Ok)
            return chck[1]
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def check_phone(self):
        try:
            if self.phone.text() == '':
                return False
            chck = check_phone(self.phone.text())
            if not chck[0]:
                wtl(chck[1])
                QMessageBox.information(self, 'Внимание', chck[1], QMessageBox.Ok)
            return chck[1]
        except Exception as error:
            print(error)
            QMessageBox.information(self, 'Внимание', 'Неверный номер телефона', QMessageBox.Ok)
            wtl(f'error: {error}')
            return True

    def check_password(self):
        try:
            if self.status == 'Ученик' and self.password.text() == '':
                return False
            chck = check_password(self.password.text())
            if not chck[0]:
                wtl(chck[1])
                QMessageBox.information(self, 'Внимание', chck[1], QMessageBox.Ok)
            return chck[1]
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def check_login(self):
        try:
            if self.status == 'Ученик' and self.login.text() == '':
                return False
            if self.login.text() in [i[1] for i in ex.user_data]:
                wtl('login is used')
                QMessageBox.information(self, 'Внимание', 'Данный логин уже занят другим пользователем', QMessageBox.Ok)
                return True
            return False
        except Exception as error:
            print(error)
            wtl(f'error: {error}')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name_db = ''
        self.initUI()

    def initUI(self):
        uic.loadUi('main_page.ui', self)
        self.setWindowTitle('Список карточек')
        self.setWindowIcon(QtGui.QIcon('icons/icon_main.png'))
        self.show()

        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(8, QtWidgets.QHeaderView.Stretch)

        self.cur = sqlite3.connect(self.name_db)
        self.cur.cursor()

        self.exit.clicked.connect(self.user_exit)
        self.new_db.triggered.connect(self.new_database)
        self.new_db.setIcon(QtGui.QIcon('icons/icon_add.png'))
        self.new_db.setShortcut('Ctrl+N')
        self.open_db.triggered.connect(self.load_database)
        self.open_db.setIcon(QtGui.QIcon('icons/icon_load.png'))
        self.open_db.setShortcut('Ctrl+O')
        self.save_db.triggered.connect(self.save_database)
        self.save_db.setIcon(QtGui.QIcon('icons/icon_save.png'))
        self.save_db.setShortcut('Ctrl+S')
        self.save_as_db.triggered.connect(self.save_as_database)
        self.save_as_db.setIcon(QtGui.QIcon('icons/icon_save_as.png'))
        self.close_db.triggered.connect(self.close_database)
        self.close_db.setIcon(QtGui.QIcon('icons/icon_close.png'))
        self.close_db.setShortcut('Ctrl+F4')
        self.add_student_btn.triggered.connect(self.add_student)
        self.add_teatcher_btn.triggered.connect(self.add_teatcher)
        self.add_admin_btn.triggered.connect(self.add_admin)
        self.delete_2.triggered.connect(self.remove_page)
        self.menu_3.setIcon(QtGui.QIcon('icons/add_icon.png'))
        self.open.clicked.connect(self.open_page)
        self.search_line.textChanged[str].connect(self.search_data)
        self.combo.setToolTip('Поиск по параметрам')
        self.open.setToolTip('Открыть карточку ученика')
        self.exit.setToolTip('Выйти из учетной записи')
        self.open_student_page.triggered.connect(self.open_page)

        self.add_page = None
        self.db = []
        self.user_data = []
        self.icons = []
        self.search_line.setFocus()
        self.combo.addItems(['Id', 'Фамилия', 'Имя', 'Отчество', 'Класс', 'Дата рождения'])
        self.combo.activated[str].connect(self.activated)
        self.user_status = ('Администратор',)
        self.load_table()

    def load_interface(self):
        self.selected_parameter = 'Id'
        self.selected_row = None
        self.icons = self.cur.execute("SELECT * FROM icons").fetchall()
        self.user_data = self.cur.execute("SELECT * FROM users").fetchall()
        self.db = self.cur.execute("SELECT * FROM students").fetchall()
        self.list_student_pages = []
        if self.sender() == AuthorisedWindow:
            self.nickname.setText(' '.join(self.auth.FI))
            self.user_index = self.auth.id
        else:
            self.nickname.setText('Admin')
            self.user_index = 1
        self.user_status = self.cur.execute(f"SELECT status FROM users WHERE Id = {self.user_index}").fetchone()
        self.load_table()
        self.show()

    def get_items(self):
        db = []
        for i in range(len(self.db)):
            temp = []
            for h in range(9):
                if self.table.item(i, h).text() == '':
                    temp.append(None)
                else:
                    temp.append(self.table.item(i, h).text())
            db.append(temp)
        self.db = db[:]

    def open_page(self):
        try:
            self.selected_row = self.table.currentItem().row()
            if not (self.selected_row is None):
                self.get_items()
                self.list_student_pages.append(StudentPage(self.selected_row))
                self.list_student_pages[-1].show()
                wtl(f'create page with Id = {self.selected_row}')
            else:
                raise Exception
        except Exception as error:
            print(error)
            if str(error) == "'NoneType' object has no attribute 'row'" and self.db == []:
                wtl("user don't select database")
                QMessageBox.information(self, 'Внимание', 'Загрузите или создайте новую базу данных', QMessageBox.Ok)
            elif str(error) == "'NoneType' object has no attribute 'row'":
                wtl("user don't select row")
                QMessageBox.information(self, 'Внимание', 'Выберете колонку с карточкой ученика которую хотите открыть',
                                        QMessageBox.Ok)
            else:
                wtl(f'error: {error}')
                QMessageBox.information(self, 'Внимание', f'{error}', QMessageBox.Ok)

    def remove_students_page(self, obj):
        self.list_student_pages.remove(self.list_student_pages.index(obj))

    def closeEvent(self, event):
        try:
            reply2 = self.close_database()
            reply = QMessageBox.question(self, 'Закрыть окно?', 'Вы действительно хотите закрыть окно?',
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if reply2:
                    event.ignore()
                else:
                    wtl('window close')
                    if os.path.isfile('temp_db.sqlite'):
                        self.cur.close()
                        os.remove('temp_db.sqlite')
                        wtl('remove temp file')
                    self.hide()
            else:
                wtl('window not close')
                event.ignore()
        except Exception as error:
            wtl(f'error: {error}')

    def load_table(self):
        try:
            self.table.setRowCount(len(self.db))
            for row, tupl in enumerate(self.db):
                for col, item in enumerate(list(tupl)):
                    if item is None:
                        cell = QTableWidgetItem('')
                    else:
                        cell = QTableWidgetItem(str(item))
                    cell.setFlags(Qt.ItemIsEnabled)
                    self.table.setItem(row, col, cell)
            wtl('load table')
        except Exception as error:
            print(error)
            QMessageBox.critical(self, 'Ошибка', 'Неверный формат базы данных', QMessageBox.Ok)

    def keyPressEvent(self, event):
        selected = QtWidgets.QApplication.focusWidget()
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and selected == self.search_line:
            wtl('key pressed Enter in main')
            self.search_data()
            wtl('search data')
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter) and selected == self.table:
            self.open_page()

    def search_data(self):
        try:
            if self.selected_parameter == 'Id':
                if self.search_line.text() == '':
                    self.db = self.cur.execute("SELECT * FROM students").fetchall()
                else:
                    self.db = self.cur.execute(f"SELECT * FROM students WHERE CAST (Id as text)"
                                               f"LIKE '%{self.search_line.text()}%'").fetchall()
                wtl(f"search to Id = '{self.search_line.text()}'")
            else:
                self.db = self.cur.execute(f"SELECT * FROM students WHERE {self.selected_parameter} LIKE"
                                           f"'%{self.search_line.text().lower().capitalize().strip()}%'").fetchall()
            self.load_table()
            wtl(f"search to {self.selected_parameter} = '{self.search_line.text()}'")
        except Exception as error:
            wtl(f'error: {error}')

    def user_exit(self):
        if self.name_db == '':
            wtl('window close')
            self.close()
        else:
            reply = QMessageBox.question(self, 'Выйти из аккаунта?', 'Вы действительно хотите выйти из аккаунта?',
                                        QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.hide()
                self.auth = AuthorisedWindow(self.name_db)
            wtl('user exit')

    def activated(self, text):
        if text == 'Дата рождения':
            self.selected_parameter = 'Дата_рождения'
        else:
            self.selected_parameter = text
        self.search_line.setFocus()
        self.search_data()
        wtl('change parameter')

    def add_student(self):
        try:
            user_status = self.user_status[0]
            if user_status != 'Ученик':
                self.add_page = AddWindow('Ученик')
                self.add_page.show()
                wtl(f'add site with status - {user_status}')
            else:
                wtl('user tried add student_page')
                QMessageBox.information(self, 'Внимание', 'У Вас недостаточно прав для создания карточки Ученика',
                                        QMessageBox.Ok)
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def add_teatcher(self):
        try:
            user_status = self.user_status[0]
            if user_status == 'Администратор':
                self.add_page = AddWindow('Учитель')
                self.add_page.show()
                wtl(f'add site with status - {user_status}')
            else:
                wtl('user tried add teatcher_page')
                QMessageBox.information(self, 'Внимание', 'У Вас недостаточно прав для создания карточки Учителя',
                                        QMessageBox.Ok)
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def add_admin(self):
        try:
            user_status = self.user_status[0]
            if user_status == 'Администратор':
                self.add_page = AddWindow('Администратор')
                self.add_page.show()
                wtl(f'add site with status - {user_status}')
            else:
                wtl('user tried add admin_page')
                QMessageBox.information(self, 'Внимание', 'У Вас недостаточно прав для создания карточки Администратора',
                                        QMessageBox.Ok)
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def remove_page(self):
        try:
            user_status = self.user_status[0]
            if user_status == 'Администратор':
                try:
                    selected = self.table.currentItem().row()
                    print(selected)
                    reply = QMessageBox.question(self, 'Внимание', f'Вы действительно хотите удалить карточку с Id ='
                                                                   f'{selected + 1}', QMessageBox.Yes,
                                                 QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.db.remove(self.db[selected])
                        self.user_data.remove(self.user_data[selected])
                        self.icons.remove(self.icons[selected])
                        self.load_table()
                except Exception as error:
                    print(error)
                    wtl(f'error: {error}')
                    QMessageBox.information(self, 'Внимание', 'Нажмите на нужную карточку для удаления', QMessageBox.Ok)
            else:
                wtl('user not admin')
                QMessageBox.information(self, 'Внимание', 'У Вас недостаточно прав для удаления карточки', QMessageBox.Ok)
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def new_database(self):
        try:
            self.cur.close()
            self.name_db = 'temp_db.sqlite'
            if os.path.isfile(self.name_db):
                os.remove(self.name_db)
            self.cur = sqlite3.connect(self.name_db)
            self.cur.cursor()
            self.cur.execute("CREATE TABLE students (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,\
            Фамилия TEXT, Имя TEXT, Отчество TEXT, Класс TEXT, phone TEXT, Адрес TEXT, Дата_рождения TEXT,\
                             other TEXT);")
            self.cur.execute("CREATE TABLE users (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,\
            login TEXT, password TEXT, status TEXT);")
            self.cur.execute("CREATE TABLE icons (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, icon TEXT);")
            self.cur.execute(f"INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (1, 'Admin', None, None, None, None, None, None, None))
            self.cur.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", (1, 'admin', 'admin', 'Администратор'))
            self.cur.execute(f"INSERT INTO icons VALUES (?, ?)", (1, ''))
            self.cur.commit()
            self.icons = self.cur.execute("SELECT * FROM icons").fetchall()
            self.user_data = self.cur.execute("SELECT * FROM users").fetchall()
            self.db = self.cur.execute("SELECT * FROM students").fetchall()
            self.load_table()
            self.load_interface()
        except Exception as error:
            wtl(f'error: {error}')
            QMessageBox.critical(self, 'Ошибка', f'Возникла непредвиденная ошибка {error}', QMessageBox.Ok)

    def load_database(self):
        try:
            self.close_database()
            self.name_db = QFileDialog.getOpenFileName(self, 'Выберите файл', '',
                                                       'База данных (*.sqlite);;База данных (*.db);;Все файлы (*)')[0]
            if self.name_db != '':
                self.cur = sqlite3.connect(self.name_db)
                self.cur.cursor()
                wtl('load database success')
                self.hide()
                self.auth = AuthorisedWindow(self.name_db)
        except Exception as error:
            wtl(f'error: {error}')
            QMessageBox.critical(self, 'Ошибка', 'Неверный формат базы данных', QMessageBox.Ok)

    def save_database(self):
        try:
            self.get_items()
            self.cur.execute("DELETE FROM students")
            self.cur.execute("DELETE FROM users")
            self.cur.execute("DELETE FROM icons")
            for row in self.db:
                self.cur.execute(f"INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
            for row in self.user_data:
                self.cur.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", row)
            for row in self.icons:
                self.cur.execute(f"INSERT INTO icons VALUES (?, ?)", row)
                self.cur.commit()
        except Exception as error:
            wtl(f'error: {error}')

    def save_as_database(self):
        try:
            name = QFileDialog.getSaveFileName(self, 'Сохранить как', 'school database', '')[0]
            if name != '':
                file_name = name.split('/')[-1]
                if name.count('.') == 0:
                    name += '.sqlite'
                if name.split('/')[-1] != 'temp_db.sqlite':
                    if os.path.isfile(name):
                        os.remove(name)
                        wtl(f'remove file {name}')
                    if self.name_db in (name, file_name):
                        wtl(f'file {name} open in program')
                        QMessageBox.critical(self, 'Ошибка', f'Файл {file_name} открыт в программе', QMessageBox.Ok)
                    else:
                        self.get_items()
                        new_file = sqlite3.connect(name)
                        new_file.cursor()
                        new_file.execute("CREATE TABLE students (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,\
                        Фамилия TEXT, Имя TEXT, Отчество TEXT, Класс TEXT, phone TEXT, Адрес TEXT,\
                        Дата_рождения TEXT, other TEXT);")
                        new_file.execute("CREATE TABLE users (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE\
                        NOT NULL REFERENCES students (id), login TEXT, password TEXT, status TEXT);")
                        new_file.execute("CREATE TABLE icons (Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,\
                        icon TEXT);")
                        for r in self.db:
                            new_file.execute(f"INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                             (r[0], r[1], r[2],
                                              r[3], r[4], r[5], r[6], r[7], r[8]))
                        for r in self.user_data:
                            new_file.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", (r[0], r[1], r[2], r[3]))
                        for r in self.icons:
                            new_file.execute(f"INSERT INTO icons VALUES (?, ?)", (r[0], r[1]))
                        new_file.commit()
                        new_file.close()
                        wtl(f'save database as {name} success')
                elif file_name == 'temp_db.sqlite':
                    wtl('used reserved name of file')
                    QMessageBox.information(self, 'Внимание', 'Имя temp_db.sqlite зарезервированно программой')
        except Exception as error:
            print(error)
            wtl(f'error: {error}')

    def close_database(self):
        try:
            if check(self):
                reply = QMessageBox.question(self, 'Закрыть', 'В файле есть несохранённые изменения. Хотите сохранить?',
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    wtl('rewrite file')
                    if self.name_db == 'temp_db.sqlite':
                        self.save_as_database()
                        self.db = []
                        self.load_table()
                    else:
                        self.save_database()
                        self.db = []
                        self.load_table()
                else:
                    self.db = []
                    self.load_table()
                    wtl('close file')
            else:
                self.db = []
                self.load_table()
                wtl('close file(files the same)')
            self.cur.close()
        except Exception as error:
            print(f'error: {error}')
            wtl(f'error: {error}')


if __name__ == '__main__':
    try:
        old_logs = open('logs.txt', encoding='utf-8', mode='r').readlines()
        logs = open('logs.txt', encoding='utf-8', mode='w')
        if old_logs != []:
            wtl(' '.join(old_logs))
        print(f'{dt.datetime.now()} -> start program', file=logs)
        app = QApplication(sys.argv)
        ex = MainWindow()
        sys.exit(app.exec())
    except Exception as error:
        print(error)
        wtl(f'error: {error}')
