import sys
import os
import requests
from PySide6.QtCore import QTimer, Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QSlider,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QHBoxLayout, QTextEdit
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import time
import datetime


# ПУТЬ К ПАПКЕ Server НА ТВОЕМ КОМПЕ
SERVER_HTTP = os.environ.get('VEO_SERVER_URL', 'http://127.0.0.1:5000')


class CustomVideoWidget(QVideoWidget):
    def __init__(self, toggle_pause, parent=None):
        super(CustomVideoWidget, self).__init__(parent)
        self.toggle_pause = toggle_pause

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_pause()


class VideoPlayer(QWidget):
    switch_window = Signal()  # Создаем сигнал для переключения окна

    def __init__(self, operation_id, token, role, changing_operation, after_delete):
        super().__init__()
        self.operation_id = operation_id
        self.changing_operation = changing_operation
        self.token = token
        self.role = role
        self.after_delete = after_delete

        self.timings = []

        # ---- Получаем данные операции с сервера ----
        url = config.api_url('/get_operation')
        data = {"operation_id": f"{self.operation_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            self.json_response = response.json()
            print("JSON операции в плеере:", self.json_response)
        else:
            print('Ошибка при получении данных об операции:', response.status_code)
            self.go_back()
            return

        raw_stages = self.json_response.get('stages')

        # Если этапов нет (на сервере 'None' или пусто) – работаем с пустым списком
        if not raw_stages or raw_stages == 'None':
            self.timings = []
        else:
            try:
                self.timings = eval(raw_stages)
            except Exception as e:
                print('Не удалось разобрать этапы операции:', e, 'stages =', raw_stages)
                self.timings = []

        self.files_count = int(self.json_response['files_count'])

        # ---- Готовим пути к видеофайлам ----
        self.video1_path = None
        self.video2_path = None

        video1_rel = self.json_response.get("file_video_path1")
        video2_rel = self.json_response.get("file_video_path2")

        # Для воспроизведения используем HTTP-стрим с сервера (это работает на других ПК без общего диска)
        self.video1_path = f"{SERVER_HTTP}/get_video1/{operation_id}" if video1_rel else None
        self.video2_path = f"{SERVER_HTTP}/get_video2/{operation_id}" if video2_rel else None

        print("video1_url:", self.video1_path)
        print("video2_url:", self.video2_path)
        if self.video1_path and not os.path.exists(self.video1_path):
            print("ВНИМАНИЕ: файл видео 1 не найден на диске:", self.video1_path)
        if self.video2_path and not os.path.exists(self.video2_path):
            print("ВНИМАНИЕ: файл видео 2 не найден на диске:", self.video2_path)

        # ---- Дальше твой существующий UI-код ----

        self.layout = QVBoxLayout()
        self.layout.setSpacing(9)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)

        button_cell_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setFixedSize(150, 50)
        button_layout.addWidget(self.back_button)
        self.favorite_button = QPushButton("Добавить в избранное")
        self.favorite_button.clicked.connect(self.add_to_favorite)
        self.favorite_button.setFixedSize(150, 50)
        button_layout.addWidget(self.favorite_button)
        if self.role == 1 or self.role == 2:
            self.update_button = QPushButton("Изменить данные")
            self.update_button.clicked.connect(self.go_changing)
            self.update_button.setFixedSize(150, 50)
            button_layout.addWidget(self.update_button)
            self.delete_button = QPushButton("Удалить запись")
            self.delete_button.clicked.connect(self.deleting)
            self.delete_button.setFixedSize(150, 50)
            button_layout.addWidget(self.delete_button)
        if self.role == 1 or self.role == 2 or self.role == 3:
            self.upload_button = QPushButton("Скачать данные")
            self.upload_button.clicked.connect(self.upload)
            self.upload_button.setFixedSize(150, 50)
            button_layout.addWidget(self.upload_button)
        button_cell_widget.setLayout(button_layout)
        button_cell_widget.setFixedSize(1017, 50)
        self.layout.addWidget(button_cell_widget, alignment=Qt.AlignCenter)

        info_cell_widget1 = QWidget()
        info_layout1 = QHBoxLayout()
        info_layout1.setContentsMargins(0, 0, 0, 0)
        info_layout1.setSpacing(30)
        info_layout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.idLabel = QLabel('ID операции: ' + f"{self.json_response['operation_id']}")
        info_layout1.addWidget(self.idLabel)
        self.patientLabel = QLabel('ID пациента: ' + f"{self.json_response['patient_id']}")
        info_layout1.addWidget(self.patientLabel)
        self.userLabel = QLabel('ID создателя записи: ' + f"{self.json_response['user_id']}")
        info_layout1.addWidget(self.userLabel)
        info_cell_widget1.setLayout(info_layout1)
        info_cell_widget1.setFixedSize(1035, 25)
        self.layout.addWidget(info_cell_widget1)

        info_cell_widget2 = QWidget()
        info_layout2 = QHBoxLayout()
        info_layout2.setContentsMargins(0, 0, 0, 0)
        info_layout2.setSpacing(30)
        info_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.typeLabel = QLabel('Тип операции: ' + f"{self.json_response['operation_type']}")
        info_layout2.addWidget(self.typeLabel)
        self.organLabel = QLabel('Орган: ' + f"{self.json_response['organ']}")
        info_layout2.addWidget(self.organLabel)
        self.dateLabel = QLabel('Дата и время операции: ' + f"{self.json_response['operation_date']}")
        info_layout2.addWidget(self.dateLabel)
        self.centerLabel = QLabel('Клиника: ' + f"{self.json_response['medical_center']}")
        info_layout2.addWidget(self.centerLabel)
        info_cell_widget2.setLayout(info_layout2)
        info_cell_widget2.setFixedSize(1035, 25)
        self.layout.addWidget(info_cell_widget2)

        # Видео-область
        cell_widget = QWidget()
        videolayout = QHBoxLayout()
        self.video_widget1 = CustomVideoWidget(self.toggle_pause, self)
        self.video_widget1.setFixedSize(500, 300)
        videolayout.setSpacing(5)
        videolayout.addWidget(self.video_widget1)
        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.video_widget1)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.audio_output = QAudioOutput(self)

        if self.files_count > 1:
            self.video_widget2 = CustomVideoWidget(self.toggle_pause, self)
            self.video_widget2.setFixedSize(500, 300)
            videolayout.addWidget(self.video_widget2)
            self.player2 = QMediaPlayer(self)
            self.player2.setVideoOutput(self.video_widget2)
            self.audio_output2 = QAudioOutput(self)

        cell_widget.setLayout(videolayout)
        self.layout.addWidget(cell_widget, alignment=Qt.AlignCenter)

        # ---- Устанавливаем источники видео (локально или по HTTP) ----
        if self.video1_path:
            if self.video1_path.startswith('http'):
                self.player.setSource(QUrl(self.video1_path))
            elif os.path.exists(self.video1_path):
                self.player.setSource(QUrl.fromLocalFile(self.video1_path))
            else:
                print("Видео 1 не может быть установлено, файла нет:", self.video1_path)
            self.player.setAudioOutput(self.audio_output)
        else:
            print("Видео 1 отсутствует (путь пустой).")

        if self.files_count > 1 and self.video2_path:
            if self.video2_path.startswith('http'):
                self.player2.setSource(QUrl(self.video2_path))
            elif os.path.exists(self.video2_path):
                self.player2.setSource(QUrl.fromLocalFile(self.video2_path))
            else:
                print("Видео 2 не может быть установлено, файла нет:", self.video2_path)
            self.player2.setAudioOutput(self.audio_output2)
        elif self.files_count > 1:
            print("Видео 2 отсутствует (путь пустой).")

        # Для старта по клику используется toggle_pause(); автозапуск не делаем.


       # ---- Слайдер и время ----
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.player.positionChanged.connect(self.update_slider_position)
        self.player.durationChanged.connect(self.update_slider_range)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        self.slider.setFixedSize(1005, 25)
        self.layout.addWidget(self.slider, alignment=Qt.AlignCenter)

        time_cell_widget = QWidget()
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(917)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeLabel = QLabel('00:00:00')
        self.timeLabel.setFixedSize(54, 25)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(50)
        time_layout.addWidget(self.timeLabel)
        self.endtimeLabel = QLabel('00:00:00')
        self.endtimeLabel.setFixedSize(54, 25)
        time_layout.addWidget(self.endtimeLabel)
        time_cell_widget.setLayout(time_layout)
        time_cell_widget.setFixedSize(1005, 25)
        self.layout.addWidget(time_cell_widget, alignment=Qt.AlignCenter)

        self.stageLabel = QLabel("Этапы операции")
        self.stageLabel.setFixedSize(102, 25)
        self.layout.addWidget(self.stageLabel, alignment=Qt.AlignCenter)

        self.table_widget = QTableWidget(0, 3)
        self.table_widget.setHorizontalHeaderLabels(["Название этапа", "Тайминг", "Кровопотеря, мл"])
        self.table_widget.setStyleSheet("""
            QTableWidget {
                border: 1px solid lightgray;
            }
            QHeaderView::section{
                border: 1px solid gray;
                background-color: white;
            }
        """)
        self.table_widget.setColumnWidth(1, 121)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_widget.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTriggers.NoEditTriggers)
        self.table_widget.itemClicked.connect(self.highlight_row)
        self.table_widget.setFixedSize(1005, 148)
        self.table_widget.cellDoubleClicked.connect(self.go_to_timing)
        self.layout.addWidget(self.table_widget, alignment=Qt.AlignCenter)

        self.table_widget.setRowCount(len(self.timings))
        if self.timings:
            keys = list(self.timings[0])
            for row in range(len(self.timings)):
                for column in range(len(keys)):
                    item = QTableWidgetItem(str(self.timings[row][keys[column]]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_widget.setItem(row, column, item)

        self.description_button = QPushButton("Показать описание")
        self.description_button.clicked.connect(self.show_description)
        self.description_button.setFixedSize(150, 50)
        self.layout.addWidget(self.description_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.overlay.setGeometry(15, 513, 1005, 193)
        overlaylayout = QVBoxLayout(self.overlay)
        overlaylayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        overlaylayout.setSpacing(9)

        self.titleLabel = QLabel("Описание операции")
        self.titleLabel.setFixedSize(123, 25)
        overlaylayout.addWidget(self.titleLabel, alignment=Qt.AlignCenter)

        self.description = QTextEdit()
        self.description.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.description.setReadOnly(True)
        self.description.setFixedSize(984, 149)
        self.description.setText(f"{self.json_response['description']}")
        overlaylayout.addWidget(self.description, alignment=Qt.AlignCenter)
        self.overlay.setVisible(False)

    def go_back(self):
        self.switch_window.emit()  # Возвращаемся на экран со списком операций

    def go_to_timing(self, row):
        item = self.table_widget.item(row, 1).text()
        x = time.strptime(item, '%H:%M:%S')
        timing = int(datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds())
        self.player.setPosition(timing * 1000)  # Перемотка в миллисекундах
        if self.files_count > 1:
            self.player2.setPosition(timing * 1000)

    def highlight_row(self, item):
        for row in range(self.table_widget.rowCount()):
            for column in range(self.table_widget.columnCount()):
                self.table_widget.item(row, column).setBackground(Qt.white)
        row = item.row()
        for column in range(self.table_widget.columnCount()):
            self.table_widget.item(row, column).setBackground(Qt.gray)

    def update_slider_range(self, duration):
        self.slider.setRange(0, duration)

    def update_slider_position(self, position):
        self.slider.setValue(position)

    def on_slider_pressed(self):
        if self.files_count > 1:
            self.player2.pause()
        self.player.pause()

    def on_slider_released(self):
        value = self.slider.value()
        if self.files_count > 1:
            self.player2.play()
            self.player2.setPosition(value)
        self.player.play()
        self.player.setPosition(value)

    def update_time_label(self):
        position = self.slider.value()
        hours = (position // 1000) // 3600
        minutes = (position // 1000) // 60
        seconds = (position // 1000) % 60
        self.timeLabel.setText(f'{hours:02}:{minutes:02}:{seconds:02}')

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            end_time = self.player.duration() // 1000
            hours = end_time // 3600
            minutes = end_time // 60
            seconds = end_time % 60
            self.endtimeLabel.setText(f'{hours:02}:{minutes:02}:{seconds:02}')

    def toggle_pause(self):
        # НИКАКИХ HTTP-ЗАПРОСОВ – только play/pause
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            if self.files_count > 1:
                self.player2.pause()
            self.player.pause()
        else:
            if self.files_count > 1:
                self.player2.play()
            self.player.play()

    def deleting(self):
        url = config.api_url('/delete_operation')
        data = {"operation_id": f"{self.operation_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.post(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            print('Запись об операции удалена:', response.status_code, json_response)
            self.after_delete()
        else:
            print('Ошибка удаления записи об операции:', response.status_code, response.json())

    def go_changing(self):
        self.changing_operation(self.json_response)

    def add_to_favorite(self):
        url = config.api_url('/save_to_favourites')
        operation_id = self.operation_id
        data = {"operation_id": f"{operation_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.post(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            print(json_response)
        else:
            print('Ошибка при добавлении записи в избранное:', response.status_code, response.json())

    def show_description(self):
        self.overlay.setVisible(True)
        self.description_button.setText('Скрыть описание')
        self.description_button.clicked.disconnect()
        self.description_button.clicked.connect(self.close_description)

    def close_description(self):
        self.description_button.setText('Показать описание')
        self.description_button.clicked.disconnect()
        self.description_button.clicked.connect(self.show_description)
        self.overlay.setVisible(False)

    def upload(self):
        url = config.api_url('/upload')
        operation_id = self.json_response['operation_id']
        data = {"operation_id": f"{operation_id}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            with open('videos.zip', 'wb') as file:
                file.write(response.content)
            with open(f'{response.headers["X-Message"].encode("latin-1").decode("utf-8")}.txt', 'w') as file:
                file.write(f'ID операции: {self.json_response["operation_id"]}\n')
                file.write(f'ID создателя записи: {self.json_response["user_id"]}\n')
                file.write(f'ID пациента: {self.json_response["patient_id"]}\n')
                file.write(f'Тип операции: {self.json_response["operation_type"]}\n')
                file.write(f'Оперируемый орган: {self.json_response["organ"]}\n')
                file.write(f'Киника: {self.json_response["medical_center"]}\n')
                file.write(f'Описание: {self.json_response["description"]}\n')
                for stage in self.timings:
                    file.write(f'{stage}\n')
        else:
            print('Ошибка при скачивании данных:', response.status_code, response.json())