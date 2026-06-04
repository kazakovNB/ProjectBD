import sys
import requests
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QListWidget, QHBoxLayout, QComboBox
import time
from datetime import datetime


from config import build_url
class ChangingUser(QWidget):
    switch_window = Signal()  # Создаем сигнал для переключения окна

    def __init__(self, data, token, save_user_changes):
        super().__init__()
        self.data = data
        self.token = token
        self.save_user_changes = save_user_changes

        url = build_url('/get_roles')
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header)
        if (response.status_code == 200) or (response.status_code == 201):
            self.json_response = response.json()
        else:
            print('Ошибка при получении списка ролей:', response.status_code, response.json())

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        button_cell_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setFixedSize(150, 50)
        button_layout.addWidget(self.back_button)
        self.update_button = QPushButton("Сохранить изменения")
        self.update_button.clicked.connect(self.changing_user)
        self.update_button.setFixedSize(150, 50)
        button_layout.addWidget(self.update_button)
        button_cell_widget.setLayout(button_layout)
        button_cell_widget.setFixedSize(1017, 50)
        layout.addWidget(button_cell_widget, alignment=Qt.AlignCenter)

        self.idLabel = QLabel('ID пользователя: ' + f"{self.data['user_id']}")

        loginLabel = QLabel("Логин:", alignment=Qt.AlignCenter)
        loginLabel.setFixedSize(150, 25)
        layout.addWidget(loginLabel, alignment=Qt.AlignCenter)
        self.login_input = QLineEdit()
        self.login_input.setFixedSize(150, 25)
        self.login_input.setText(f"{self.data['login']}")
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
        self.name_input.setText(f"{self.data['name']}")
        inputfiolayout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        self.surname_input = QLineEdit()
        self.surname_input.setFixedSize(150, 25)
        self.surname_input.setText(f"{self.data['surname']}")
        inputfiolayout.addWidget(self.surname_input, alignment=Qt.AlignCenter)
        self.patronymic_input = QLineEdit()
        self.patronymic_input.setFixedSize(150, 25)
        self.patronymic_input.setText(f"{self.data['patronymic']}")
        inputfiolayout.addWidget(self.patronymic_input, alignment=Qt.AlignCenter)
        inputfiowidget.setLayout(inputfiolayout)
        layout.addWidget(inputfiowidget, alignment=Qt.AlignCenter)

        birthdayLabel = QLabel("Дата рождения:", alignment=Qt.AlignCenter)
        birthdayLabel.setFixedSize(150, 25)
        layout.addWidget(birthdayLabel, alignment=Qt.AlignCenter)
        hlayout1 = QHBoxLayout()
        hlayout1.setContentsMargins(0, 0, 0, 0)
        hlayout1.setSpacing(5)
        hlayout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date = self.data['birthday']
        # Создаем QComboBox для года
        self.year_combo = QComboBox()
        self.year_combo.setMinimumSize(5, 25)
        self.year_combo.addItems([str(i) for i in range(1900, datetime.now().year + 1)])
        self.year_combo.setCurrentIndex(self.year_combo.findText(self.date.split('-')[0]))
        self.year_combo.setFixedSize(60, 25)
        hlayout1.addWidget(self.year_combo)
        # Создаем QComboBox для месяца
        self.month_combo = QComboBox()
        self.month_combo.setMinimumSize(5, 25)
        self.month_combo.addItems([str(i).zfill(2) for i in range(1, 13)])
        self.month_combo.setCurrentIndex(self.month_combo.findText(self.date.split('-')[1]))
        self.month_combo.setFixedSize(40, 25)
        hlayout1.addWidget(self.month_combo)
        # Создаем QComboBox для дня
        self.day_combo = QComboBox()
        self.day_combo.setFixedSize(40, 25)
        self.year_combo.currentIndexChanged.connect(self.update_days)
        self.month_combo.currentIndexChanged.connect(self.update_days)
        self.update_days()
        self.day_combo.setCurrentIndex(self.day_combo.findText(self.date.split('-')[2]))
        hlayout1.addWidget(self.day_combo)
        cell_widget1 = QWidget()
        cell_widget1.setLayout(hlayout1)
        layout.addWidget(cell_widget1, alignment=Qt.AlignCenter)

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

        roleLabel = QLabel("Роль в приложении:", alignment=Qt.AlignCenter)
        roleLabel.setFixedSize(150, 25)
        layout.addWidget(roleLabel, alignment=Qt.AlignCenter)

        self.organization_input = QLineEdit()
        self.organization_input.setText(f"{self.data['organization']}")
        self.job_title_input = QLineEdit()
        self.job_title_input.setText(f"{self.data['job_title']}")
        self.university_input = QLineEdit()
        self.university_input.setText(f"{self.data['university']}")
        self.department_input = QLineEdit()
        self.department_input.setText(f"{self.data['department']}")
        self.student_group_input = QLineEdit()
        self.student_group_input.setText(f"{self.data['student_group']}")

        self.role_combo = QComboBox()
        self.role_combo.setFixedSize(150, 25)
        self.role_combo.addItems([str(i) for i in self.json_response['roles']])
        self.role_combo.currentIndexChanged.connect(self.update_fields)
        self.role_combo.setCurrentIndex(self.role_combo.findText(self.data['role']))
        layout.addWidget(self.role_combo, alignment=Qt.AlignCenter)

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

    def go_back(self):
        self.switch_window.emit()  # Возвращаемся на экран со списком операций

    def changing_user(self):
        if self.password_input.text() == self.confirm_password_input.text():
            url = build_url('/update_user')
            user_id = self.data['user_id']
            login = str(self.login_input.text())
            if str(self.password_input.text()) is not None and str(self.password_input.text()) != '' and \
                    str(self.password_input.text()) != 'None':
                password = str(self.password_input.text())
            else:
                password = ''
            name = str(self.name_input.text())
            surname = str(self.surname_input.text())
            patronymic = str(self.patronymic_input.text())
            birthday = self.year_combo.currentText()+"-"+self.month_combo.currentText()+"-"+self.day_combo.currentText()
            role = str(self.role_combo.currentText())
            job_title = str(self.job_title_input.text())
            organization = str(self.organization_input.text())
            department = str(self.department_input.text())
            university = str(self.university_input.text())
            student_group = str(self.student_group_input.text())
            data = {"user_id": f"{user_id}", "name": f"{name}", "surname": f"{surname}", "patronymic": f"{patronymic}",
                    "birthday": f"{birthday}", "role": f"{role}", "password": f"{password}", "login": f"{login}",
                    "job_title": f"{job_title}", "department": f"{department}", "university": f"{university}",
                    "student_group": f"{student_group}", "organization": f"{organization}"}
            header = {'Authorization': f'{self.token}'}
            response = requests.put(url, headers=header, json=data)
            if (response.status_code == 200) or (response.status_code == 201):
                json_response = response.json()
                print('Пользователь изменён:', response.status_code, json_response)
                self.save_user_changes(user_id)
            else:
                print('Ошибка изменения пользователя:', response.status_code, response.json())
        else:
            print("Пароли должны совпадать")

    def update_days(self):
        # Обновляет дни в зависимости от года и месяца
        month = int(self.month_combo.currentText())
        year = int(self.year_combo.currentText())
        self.day_combo.clear()
        # Устанавливаем количество дней
        days_in_month = self.days_in_month(year, month)
        # Обновляем выпадающий список с днями
        self.day_combo.addItems([str(i).zfill(2) for i in range(1, days_in_month + 1)])

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