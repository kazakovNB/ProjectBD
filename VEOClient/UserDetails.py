import sys
import requests
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QListWidget, QHBoxLayout
import time
import datetime


from config import build_url
class UserDetails(QWidget):
    switch_window = Signal()  # Создаем сигнал для переключения окна

    def __init__(self, user_id, token, changing_user):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.changing_user = changing_user

        url = build_url('/get_user')
        data = {"user_id": f"{self.user_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            self.json_response = response.json()
        else:
            print('Ошибка при получении данных о пользователе:', response.status_code)

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
        self.update_button = QPushButton("Изменить данные")
        self.update_button.clicked.connect(self.go_changing)
        self.update_button.setFixedSize(150, 50)
        button_layout.addWidget(self.update_button)
        self.delete_button = QPushButton("Удалить пользователя")
        self.delete_button.clicked.connect(self.deleting)
        self.delete_button.setFixedSize(150, 50)
        button_layout.addWidget(self.delete_button)
        if self.json_response['active'] != 'True':
            self.activate_button = QPushButton("Активация пользователя")
            self.activate_button.clicked.connect(self.activating)
            self.activate_button.setFixedSize(150, 50)
            button_layout.addWidget(self.activate_button)
        button_cell_widget.setLayout(button_layout)
        button_cell_widget.setFixedSize(1017, 50)
        layout.addWidget(button_cell_widget, alignment=Qt.AlignCenter)

        self.idLabel = QLabel('ID пользователя: ' + f"{self.json_response['user_id']}")
        self.loginLabel = QLabel('Логин: ' + f"{self.json_response['login']}")
        self.roleLabel = QLabel('Роль: ' + f"{self.json_response['role']}")
        self.activeLabel = QLabel('Статус учётной записи: ' + f"{self.json_response['active']}")
        self.nameLabel = QLabel('Имя: ' + f"{self.json_response['name']}")
        self.surnameLabel = QLabel('Фамилия: ' + f"{self.json_response['surname']}")
        self.patronymicLabel = QLabel('Отчество: ' + f"{self.json_response['patronymic']}")
        self.birthdayLabel = QLabel('Дата рождения: ' + f"{self.json_response['birthday']}")
        self.registrationLabel = QLabel('Дата регистрации: ' + f"{self.json_response['registration']}")
        self.job_titleLabel = QLabel('Должность: ' + f"{self.json_response['job_title']}")
        self.organizationLabel = QLabel('Наименование организации: ' + f"{self.json_response['organization']}")
        self.departmentLabel = QLabel('Отдел/Кафедра: ' + f"{self.json_response['department']}")
        self.universityLabel = QLabel('Название университета: ' + f"{self.json_response['university']}")
        self.student_groupLabel = QLabel('Номер студенческой группы: ' + f"{self.json_response['student_group']}")


        layout.addWidget(self.idLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.loginLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.roleLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.activeLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.nameLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.surnameLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.patronymicLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.birthdayLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.registrationLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.job_titleLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.organizationLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.departmentLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.universityLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.student_groupLabel, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def go_back(self):
        self.switch_window.emit()  # Возвращаемся на экран со списком операций

    def deleting(self):
        url = build_url('/delete_user')
        data = {"user_id": f"{self.json_response['user_id']}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.post(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            print('Пользователь удалён:', response.status_code, json_response)
            self.go_back()
        else:
            print('Ошибка удаления:', response.status_code, response.json())

    def go_changing(self):
        self.changing_user(self.json_response)

    def activating(self):
        url = build_url('/activation')
        user_id = self.json_response['user_id']
        data = {"user_id": f"{user_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.patch(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            print('Пользователь активирован:', response.status_code, json_response)
            self.go_back()
        else:
            print('Ошибка активации пользователя:', response.status_code, response.json())