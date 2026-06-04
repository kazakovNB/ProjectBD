import sys
import requests
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QComboBox, QHBoxLayout
from datetime import datetime


from config import build_url
class Registration(QWidget):
    switch_window = Signal()

    def __init__(self):
        super().__init__()

        url = build_url('/get_roles')
        response = requests.get(url)
        if (response.status_code == 200) or (response.status_code == 201):
            self.json_response = response.json()
        else:
            print('Ошибка при получении списка ролей:', response.status_code, response.json())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loginLabel = QLabel("Логин:", alignment=Qt.AlignCenter)
        loginLabel.setFixedSize(150, 25)
        layout.addWidget(loginLabel, alignment=Qt.AlignCenter)
        self.login_input = QLineEdit()
        self.login_input.setFixedSize(150, 25)
        layout.addWidget(self.login_input, alignment=Qt.AlignCenter)

        fiowidget = QWidget()
        fiolayout = QHBoxLayout()
        fiolayout.setContentsMargins(0, 0, 0, 0)
        fiolayout.setSpacing(5)
        nameLabel = QLabel("Имя:", alignment=Qt.AlignCenter)
        nameLabel.setFixedSize(150, 25)
        fiolayout.addWidget(nameLabel)
        surnameLabel = QLabel("Фамилия:", alignment=Qt.AlignCenter)
        surnameLabel.setFixedSize(150, 25)
        fiolayout.addWidget(surnameLabel)
        patronymicLabel = QLabel("Отчество:", alignment=Qt.AlignCenter)
        patronymicLabel.setFixedSize(150, 25)
        fiolayout.addWidget(patronymicLabel)
        fiowidget.setLayout(fiolayout)
        layout.addWidget(fiowidget, alignment=Qt.AlignCenter)

        inputfiowidget = QWidget()
        inputfiolayout = QHBoxLayout()
        inputfiolayout.setContentsMargins(0, 0, 0, 0)
        inputfiolayout.setSpacing(5)
        self.name_input = QLineEdit()
        self.name_input.setFixedSize(150, 25)
        inputfiolayout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        self.surname_input = QLineEdit()
        self.surname_input.setFixedSize(150, 25)
        inputfiolayout.addWidget(self.surname_input, alignment=Qt.AlignCenter)
        self.patronymic_input = QLineEdit()
        self.patronymic_input.setFixedSize(150, 25)
        inputfiolayout.addWidget(self.patronymic_input, alignment=Qt.AlignCenter)
        inputfiowidget.setLayout(inputfiolayout)
        layout.addWidget(inputfiowidget, alignment=Qt.AlignCenter)

        birthdayLabel = QLabel("Дата рождения:", alignment=Qt.AlignCenter)
        birthdayLabel.setFixedSize(150, 25)
        layout.addWidget(birthdayLabel, alignment=Qt.AlignCenter)
        hlayout1 = QHBoxLayout()
        hlayout1.setContentsMargins(0, 0, 0, 0)
        hlayout1.setSpacing(5)
        hlayout1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # Создаем QComboBox для года
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(i) for i in range(1900, datetime.now().year + 1)])
        self.year_combo.currentIndexChanged.connect(self.update_days_based_on_year)
        self.year_combo.setFixedSize(60, 25)
        hlayout1.addWidget(self.year_combo)
        # Создаем QComboBox для месяца
        self.month_combo = QComboBox()
        self.month_combo.addItems([str(i).zfill(2) for i in range(1, 13)])
        self.month_combo.currentIndexChanged.connect(self.update_days_based_on_month)
        self.month_combo.setFixedSize(55, 25)
        hlayout1.addWidget(self.month_combo)
        # Создаем QComboBox для дня
        self.day_combo = QComboBox()
        self.update_days(year=None, month=None)  # Инициализируем со значениями
        self.day_combo.setFixedSize(55, 25)
        hlayout1.addWidget(self.day_combo)
        cell_widget1 = QWidget()
        cell_widget1.setLayout(hlayout1)
        layout.addWidget(cell_widget1, alignment=Qt.AlignCenter)

        self.organization_input = QLineEdit()
        self.job_title_input = QLineEdit()
        self.university_input = QLineEdit()
        self.department_input = QLineEdit()
        self.student_group_input = QLineEdit()

        roleLabel = QLabel("Роль в приложении:", alignment=Qt.AlignCenter)
        roleLabel.setFixedSize(150, 25)
        layout.addWidget(roleLabel, alignment=Qt.AlignCenter)
        self.role_combo = QComboBox()
        self.role_combo.setFixedSize(150, 25)
        self.role_combo.addItems([str(i) for i in self.json_response['roles']])
        self.role_combo.currentIndexChanged.connect(self.update_fields)
        self.role_combo.setCurrentIndex(self.role_combo.findText('Врач'))
        layout.addWidget(self.role_combo, alignment=Qt.AlignCenter)

        infowidget = QWidget()
        infolayout = QHBoxLayout()
        infolayout.setContentsMargins(0, 0, 0, 0)
        infolayout.setSpacing(5)
        organizationLabel = QLabel("Организация:", alignment=Qt.AlignCenter)
        organizationLabel.setFixedSize(150, 25)
        infolayout.addWidget(organizationLabel)
        job_titleLabel = QLabel("Должность:", alignment=Qt.AlignCenter)
        job_titleLabel.setFixedSize(150, 25)
        infolayout.addWidget(job_titleLabel)
        infowidget.setLayout(infolayout)
        layout.addWidget(infowidget, alignment=Qt.AlignCenter)

        inputinfowidget = QWidget()
        inputinfolayout = QHBoxLayout()
        inputinfolayout.setContentsMargins(0, 0, 0, 0)
        inputinfolayout.setSpacing(5)
        self.organization_input.setFixedSize(150, 25)
        inputinfolayout.addWidget(self.organization_input, alignment=Qt.AlignCenter)
        self.job_title_input.setFixedSize(150, 25)
        inputinfolayout.addWidget(self.job_title_input, alignment=Qt.AlignCenter)
        inputinfowidget.setLayout(inputinfolayout)
        layout.addWidget(inputinfowidget, alignment=Qt.AlignCenter)

        infowidget2 = QWidget()
        infolayout2 = QHBoxLayout()
        infolayout2.setContentsMargins(0, 0, 0, 0)
        infolayout2.setSpacing(5)
        universityLabel = QLabel("Университет:", alignment=Qt.AlignCenter)
        universityLabel.setFixedSize(150, 25)
        infolayout2.addWidget(universityLabel)
        departmentLabel = QLabel("Кафедра:", alignment=Qt.AlignCenter)
        departmentLabel.setFixedSize(150, 25)
        infolayout2.addWidget(departmentLabel)
        student_groupLabel = QLabel("Группа:", alignment=Qt.AlignCenter)
        student_groupLabel.setFixedSize(150, 25)
        infolayout2.addWidget(student_groupLabel)
        infowidget2.setLayout(infolayout2)
        layout.addWidget(infowidget2, alignment=Qt.AlignCenter)

        infowidget2 = QWidget()
        inputinfolayout2 = QHBoxLayout()
        inputinfolayout2.setContentsMargins(0, 0, 0, 0)
        inputinfolayout2.setSpacing(5)
        self.university_input.setFixedSize(150, 25)
        inputinfolayout2.addWidget(self.university_input, alignment=Qt.AlignCenter)
        self.department_input.setFixedSize(150, 25)
        inputinfolayout2.addWidget(self.department_input, alignment=Qt.AlignCenter)
        self.student_group_input.setFixedSize(150, 25)
        inputinfolayout2.addWidget(self.student_group_input, alignment=Qt.AlignCenter)
        infowidget2.setLayout(inputinfolayout2)
        layout.addWidget(infowidget2, alignment=Qt.AlignCenter)

        hlayout2 = QHBoxLayout()
        hlayout2.setContentsMargins(0, 0, 0, 0)
        hlayout2.setSpacing(5)
        hlayout2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.passwordLabel = QLabel("Пароль:")
        self.passwordLabel.setFixedSize(150, 25)
        self.passwordLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout2.addWidget(self.passwordLabel)
        self.confirmpasswordLabel = QLabel("Подтверждение пароля:")
        self.confirmpasswordLabel.setFixedSize(150, 25)
        self.confirmpasswordLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout2.addWidget(self.confirmpasswordLabel)
        cell_widget2 = QWidget()
        cell_widget2.setLayout(hlayout2)
        layout.addWidget(cell_widget2, alignment=Qt.AlignCenter)
        hlayout3 = QHBoxLayout()
        hlayout3.setContentsMargins(0, 0, 0, 0)
        hlayout3.setSpacing(5)
        hlayout3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(150, 25)
        hlayout3.addWidget(self.password_input)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFixedSize(150, 25)
        hlayout3.addWidget(self.confirm_password_input)
        cell_widget3 = QWidget()
        cell_widget3.setLayout(hlayout3)
        layout.addWidget(cell_widget3, alignment=Qt.AlignCenter)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.create_user)
        self.register_button.setFixedSize(250, 25)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        layout.addWidget(QLabel("или"), alignment=Qt.AlignCenter)

        self.authorizationButton = QPushButton('Авторизоваться')
        self.authorizationButton.clicked.connect(self.go_authorization)
        self.authorizationButton.setFixedSize(250, 25)
        layout.addWidget(self.authorizationButton, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def update_fields(self):
        if self.role_combo.currentText() == 'Врач' or self.role_combo.currentText() == 'Разработчик' or self.role_combo.currentText() == 'Администратор':
            self.university_input.setText('')
            self.university_input.setReadOnly(True)
            self.university_input.setStyleSheet("background-color: lightgray;")
            self.department_input.setText('')
            self.department_input.setReadOnly(True)
            self.department_input.setStyleSheet("background-color: lightgray;")
            self.student_group_input.setText('')
            self.student_group_input.setReadOnly(True)
            self.student_group_input.setStyleSheet("background-color: lightgray;")
            self.job_title_input.setReadOnly(False)
            self.job_title_input.setStyleSheet("background-color: light;")
            self.organization_input.setReadOnly(False)
            self.organization_input.setStyleSheet("background-color: light;")

        if self.role_combo.currentText() == 'Студент':
            self.job_title_input.setText('')
            self.job_title_input.setReadOnly(True)
            self.job_title_input.setStyleSheet("background-color: lightgray;")
            self.organization_input.setText('')
            self.organization_input.setReadOnly(True)
            self.organization_input.setStyleSheet("background-color: lightgray;")
            self.university_input.setReadOnly(False)
            self.university_input.setStyleSheet("background-color: light;")
            self.department_input.setReadOnly(False)
            self.department_input.setStyleSheet("background-color: light;")
            self.student_group_input.setReadOnly(False)
            self.student_group_input.setStyleSheet("background-color: light;")

    def update_days(self, year, month):
        # Обновляет дни в зависимости от года и месяца
        self.day_combo.clear()

        # Устанавливаем количество дней
        if month is not None and year is not None:
            days_in_month = self.days_in_month(year, month)
        else:
            days_in_month = 31  # По умолчанию, если еще нет выбора

        # Обновляем выпадающий список с днями
        self.day_combo.addItems([str(i).zfill(2) for i in range(1, days_in_month + 1)])

    def update_days_based_on_month(self):
        # Обновляет дни, когда изменяется месяц
        month = int(self.month_combo.currentText())
        year = int(self.year_combo.currentText())
        self.update_days(year, month)

    def update_days_based_on_year(self):
        # Обновляет дни, когда изменяется год
        month = int(self.month_combo.currentText())
        year = int(self.year_combo.currentText())
        self.update_days(year, month)

    @staticmethod
    def days_in_month(year, month):
        # Возвращает количество дней в заданном месяце и году
        if month == 2:  # Февраль
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29
            else:
                return 28
        elif month in [4, 6, 9, 11]:  # Апрель, Июнь, Сентябрь, Ноябрь
            return 30
        else:
            return 31  # Январь, Март, Июль, Август, Октябрь, Декабрь

    def create_user(self):
        if self.password_input.text() == self.confirm_password_input.text():
            url = build_url('/registering')
            data = {"name": f"{self.name_input.text()}", "surname": f"{self.surname_input.text()}",
                    "patronymic": f"{self.patronymic_input.text()}",
                    "birthday": f"{self.year_combo.currentText()+'-'+self.month_combo.currentText()+'-'+self.day_combo.currentText()}",
                    "role": f"{self.role_combo.currentText()}", "password": f"{self.password_input.text()}",
                    "login": f"{self.login_input.text()}", "job_title": f"{self.job_title_input.text()}",
                    "department": f"{self.department_input.text()}", "university": f"{self.university_input.text()}",
                    "student_group": f"{self.student_group_input.text()}",
                    "organization": f"{self.organization_input.text()}"}
            response = requests.post(url, json=data)
            if (response.status_code == 200) or (response.status_code == 201):
                json_response = response.json()
                print('Пользователь создан:', response.status_code, json_response)
                self.go_authorization()
            else:
                print('Ошибка создания пользователя:', response.status_code, response.json()['message'])
        else:
            print("Пароли должны совпадать")

    def go_authorization(self):
        self.switch_window.emit()


class Authorization(QWidget):
    switch_window = Signal()

    def __init__(self, on_authorized):
        super().__init__()
        self.on_authorized = on_authorized

        layout = QVBoxLayout()
        layout.setSpacing(9)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.registrationButton = QPushButton('Зарегистрироваться')
        self.registrationButton.clicked.connect(self.go_registration)
        self.registrationButton.setFixedSize(250, 25)

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setFixedSize(250, 25)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setFixedSize(250, 25)

        self.authorizationButton = QPushButton('Авторизоваться')
        self.authorizationButton.clicked.connect(self.logining)
        self.authorizationButton.setFixedSize(250, 25)

        layout.addWidget(QLabel("Логин:"), alignment=Qt.AlignCenter)
        layout.addWidget(self.login_input, alignment=Qt.AlignCenter)

        layout.addWidget(QLabel("Пароль:"), alignment=Qt.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.authorizationButton, alignment=Qt.AlignCenter)
        layout.addWidget(QLabel("или"), alignment=Qt.AlignCenter)
        layout.addWidget(self.registrationButton, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def logining(self):
        url = build_url('/logining')
        data = {"login": f"{self.login_input.text()}", "password": f"{self.password_input.text()}"}
        response = requests.post(url, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            self.on_authorized(json_response['access_token'], int(json_response['role_id']))
            self.login_input.setText('')
            self.password_input.setText('')
        else:
            print('Ошибка авторизации пользователя:', response.status_code, response.json()['message'])

    def go_registration(self):
        self.switch_window.emit()  # Возвращаемся на экран со списком операций