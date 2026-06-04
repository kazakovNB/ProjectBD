import sys
import requests
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QListWidget, QComboBox, QHBoxLayout, \
    QTableWidget, QSizePolicy, QAbstractItemView, QFileDialog, QTextEdit
from PySide6.QtCore import QTimer, Qt, QRegularExpression
import time
from datetime import datetime


from config import build_url
class NonScrollableComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class CreateOperation(QWidget):
    switch_window = Signal()  # Создаем сигнал для переключения окна

    def __init__(self, token, save_operation):
        super().__init__()

        self.token = token
        self.save_operation = save_operation
        self.optype = None
        self.stages_in_type = []
        self.file_paths = []
        self.validator = QRegularExpressionValidator(QRegularExpression("[0-9]{5}"))

        url = build_url('/get_types_and_stages')
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header)
        if (response.status_code == 200) or (response.status_code == 201):
            self.json_response = response.json()
        else:
            print('Ошибка при получении списка этапов и типов операций:', response.status_code, response.json())

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
        self.create_button = QPushButton("Сохранить запись")
        self.create_button.clicked.connect(self.create_operation)
        self.create_button.setFixedSize(150, 50)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.create_button)
        button_cell_widget.setLayout(button_layout)
        button_cell_widget.setFixedSize(1017, 50)
        layout.addWidget(button_cell_widget, alignment=Qt.AlignCenter)

        labelwidget = QWidget()
        labellayout = QHBoxLayout()
        labellayout.setContentsMargins(0, 0, 0, 0)
        labellayout.setSpacing(5)
        idLabel = QLabel("ID пациента:", alignment=Qt.AlignCenter)
        idLabel.setFixedSize(150, 25)
        labellayout.addWidget(idLabel, alignment=Qt.AlignCenter)
        centerLabel = QLabel("Клиника:", alignment=Qt.AlignCenter)
        centerLabel.setFixedSize(150, 25)
        labellayout.addWidget(centerLabel, alignment=Qt.AlignCenter)
        organLabel = QLabel("Орган:", alignment=Qt.AlignCenter)
        organLabel.setFixedSize(150, 25)
        labellayout.addWidget(organLabel, alignment=Qt.AlignCenter)
        typeLabel = QLabel("Тип операции:", alignment=Qt.AlignCenter)
        typeLabel.setFixedSize(150, 25)
        labellayout.addWidget(typeLabel, alignment=Qt.AlignCenter)
        labelwidget.setLayout(labellayout)
        layout.addWidget(labelwidget, alignment=Qt.AlignCenter)

        inputwidget = QWidget()
        inputlayout = QHBoxLayout()
        inputlayout.setContentsMargins(0, 0, 0, 0)
        inputlayout.setSpacing(5)
        self.patient_id_input = QLineEdit(self)
        self.patient_id_input.setFixedSize(150, 25)
        inputlayout.addWidget(self.patient_id_input, alignment=Qt.AlignCenter)
        self.medical_center_input = QLineEdit(self)
        self.medical_center_input.setFixedSize(150, 25)
        inputlayout.addWidget(self.medical_center_input, alignment=Qt.AlignCenter)
        self.organ_input = QLineEdit(self)
        self.organ_input.setFixedSize(150, 25)
        inputlayout.addWidget(self.organ_input, alignment=Qt.AlignCenter)
        self.type_combo = NonScrollableComboBox()
        self.type_combo.addItems([str(i) for i in self.json_response if i != 'None'])
        self.type_combo.setFixedSize(150, 25)
        inputlayout.addWidget(self.type_combo, alignment=Qt.AlignCenter)
        inputwidget.setLayout(inputlayout)
        layout.addWidget(inputwidget, alignment=Qt.AlignCenter)

        datetimeLabel = QLabel("Дата и время операции:", alignment=Qt.AlignCenter)
        datetimeLabel.setFixedSize(200, 25)
        layout.addWidget(datetimeLabel, alignment=Qt.AlignCenter)
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(5)
        # hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Создаем QComboBox для года
        self.year_combo = NonScrollableComboBox()
        self.year_combo.addItems([str(i) for i in range(2000, datetime.now().year + 1)])
        self.year_combo.setFixedSize(60, 25)
        dateLabel = QLabel("Дата:", alignment=Qt.AlignRight)
        dateLabel.setFixedSize(50, 25)
        hlayout.addWidget(dateLabel)
        hlayout.addWidget(self.year_combo)
        # Создаем QComboBox для месяца
        self.month_combo = NonScrollableComboBox()
        self.month_combo.addItems([str(i).zfill(2) for i in range(1, 13)])
        self.month_combo.setFixedSize(55, 25)
        hlayout.addWidget(self.month_combo)
        # Создаем QComboBox для дня
        self.day_combo = NonScrollableComboBox()
        self.year_combo.currentIndexChanged.connect(self.update_days)
        self.month_combo.currentIndexChanged.connect(self.update_days)
        self.year_combo.setCurrentIndex(self.year_combo.findText(str(datetime.now().year)))
        self.month_combo.setCurrentIndex(self.month_combo.findText(str(datetime.now().month).zfill(2)))
        self.update_days()
        self.day_combo.setCurrentIndex(self.day_combo.findText(str(datetime.now().day).zfill(2)))
        self.day_combo.setFixedSize(55, 25)
        hlayout.addWidget(self.day_combo)
        timeLabel = QLabel("Время:", alignment=Qt.AlignRight)
        timeLabel.setFixedSize(75, 25)
        hlayout.addWidget(timeLabel)
        self.hour_combo = NonScrollableComboBox()
        self.hour_combo.addItems([str(i).zfill(2) for i in range(0, 24)])
        self.hour_combo.setCurrentIndex(self.hour_combo.findText(str(datetime.now().hour).zfill(2)))
        self.hour_combo.setFixedSize(55, 25)
        self.minute_combo = NonScrollableComboBox()
        self.minute_combo.addItems([str(i).zfill(2) for i in range(0, 60)])
        self.minute_combo.setCurrentIndex(self.minute_combo.findText(str(datetime.now().minute).zfill(2)))
        self.minute_combo.setFixedSize(55, 25)
        self.second_combo = NonScrollableComboBox()
        self.second_combo.addItems([str(i).zfill(2) for i in range(0, 60)])
        self.second_combo.setCurrentIndex(self.second_combo.findText(str(datetime.now().second).zfill(2)))
        self.second_combo.setFixedSize(55, 25)
        hlayout.addWidget(self.hour_combo)
        hlayout.addWidget(QLabel(":"))
        hlayout.addWidget(self.minute_combo)
        hlayout.addWidget(QLabel(":"))
        hlayout.addWidget(self.second_combo)
        cell_widget = QWidget()
        cell_widget.setLayout(hlayout)
        layout.addWidget(cell_widget, alignment=Qt.AlignCenter)

        titleLabel = QLabel("Описание операции:", alignment=Qt.AlignCenter)
        titleLabel.setFixedSize(150, 25)
        layout.addWidget(titleLabel, alignment=Qt.AlignCenter)
        self.description_input = QTextEdit()
        self.description_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.description_input.setFixedSize(984, 149)
        layout.addWidget(self.description_input, alignment=Qt.AlignCenter)

        # Область для отображения этапов
        self.table_widget = QTableWidget(0, 4)
        self.table_widget.setHorizontalHeaderLabels(
            ["Этап", "Вемя начала этапа (ЧЧ:ММ:СС)", "Объем кровопотерь (мл)", ''])
        self.table_widget.setColumnWidth(0, 530)
        self.table_widget.setColumnWidth(1, 180)
        self.table_widget.setColumnWidth(2, 180)
        self.table_widget.setColumnWidth(3, 70)
        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setFixedSize(1005, 148)
        self.type_combo.currentIndexChanged.connect(self.update_stages)
        self.update_stages()
        stagesLabel = QLabel("Этапы операции:", alignment=Qt.AlignCenter)
        stagesLabel.setFixedSize(200, 25)
        layout.addWidget(stagesLabel, alignment=Qt.AlignCenter)

        self.add_button = QPushButton("Добавить этап")
        self.add_button.setFixedSize(150, 25)
        self.add_button.clicked.connect(self.add_stage_row)
        layout.addWidget(self.add_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.table_widget, alignment=Qt.AlignCenter)

        # Область загрузки файлов
        button_cell_widget2 = QWidget()
        button_layout2 = QHBoxLayout()
        button_layout2.setContentsMargins(0, 0, 0, 0)
        button_layout2.setSpacing(5)
        self.load_button = QPushButton("Выбрать видеофайлы")
        self.load_button.setFixedSize(150, 25)
        self.load_button.clicked.connect(self.load_files)
        button_layout2.addWidget(self.load_button)
        self.remove_button = QPushButton("Отменить выбор")
        self.remove_button.setFixedSize(150, 25)
        self.remove_button.clicked.connect(self.remove_files)
        button_layout2.addWidget(self.remove_button)
        button_cell_widget2.setLayout(button_layout2)
        layout.addWidget(button_cell_widget2, alignment=Qt.AlignCenter)

        self.list_widget = QListWidget()
        self.list_widget.setFixedSize(600, 75)
        layout.addWidget(self.list_widget, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def add_stage_row(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        # Добавляем элементы управления в ячейки
        stage_combo = NonScrollableComboBox()
        stage_combo.addItems(self.stages_in_type)
        self.table_widget.setCellWidget(row_position, 0, stage_combo)

        hour_combo = NonScrollableComboBox()
        hour_combo.addItems([str(i).zfill(2) for i in range(0, 24)])
        hour_combo.setFixedSize(55, 25)
        minute_combo = NonScrollableComboBox()
        minute_combo.addItems([str(i).zfill(2) for i in range(0, 60)])
        minute_combo.setFixedSize(55, 25)
        second_combo = NonScrollableComboBox()
        second_combo.addItems([str(i).zfill(2) for i in range(0, 60)])
        second_combo.setFixedSize(55, 25)
        cell_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(hour_combo)
        layout.addWidget(QLabel(":"))
        layout.addWidget(minute_combo)
        layout.addWidget(QLabel(":"))
        layout.addWidget(second_combo)
        layout.setAlignment(Qt.AlignCenter)
        cell_widget.setLayout(layout)
        self.table_widget.setCellWidget(row_position, 1, cell_widget)

        blood_loss = QLineEdit()
        blood_loss.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        blood_loss.setValidator(self.validator)
        self.table_widget.setCellWidget(row_position, 2, blood_loss)

        self.add_remove_button(row_position)

    def remove_stage_row(self, row):
        if self.table_widget.rowCount() > 1:  # Минимум одна строка
            self.table_widget.removeRow(row)
            for i in range(row, self.table_widget.rowCount()):
                # Убираем старую кнопку и добавляем новую для каждой строки
                self.table_widget.removeCellWidget(i, 3)  # Удаляем старую кнопку
                self.add_remove_button(i)  # Добавляем новую кнопку над искомой строкой

    def add_remove_button(self, row):
        remove_button = QPushButton("Удалить")
        remove_button.clicked.connect(lambda checked, r=row: self.remove_stage_row(r))
        self.table_widget.setCellWidget(row, 3, remove_button)

    def update_stages(self):
        self.optype = self.type_combo.currentText()
        self.table_widget.setRowCount(0)

        # Обновляет этапы в зависимости от типа
        self.stages_in_type = []
        # Устанавливаем этапы
        if self.optype != 'None':
            for i in self.json_response[self.optype]:
                self.stages_in_type.append(i)
        self.add_stage_row()

    def go_back(self):
        self.switch_window.emit()  # Возвращаемся на экран со списком операций

    def create_operation(self):
        url = build_url('/create_operation')
        patient_id = str(self.patient_id_input.text())
        operation_type = self.type_combo.currentText()
        organ = str(self.organ_input.text())
        operation_date = self.year_combo.currentText()+"-"+self.month_combo.currentText()+"-"+self.day_combo.currentText() + \
                         " "+self.hour_combo.currentText()+":"+self.minute_combo.currentText()+":"+ \
                         self.second_combo.currentText()
        description = str(self.description_input.toPlainText())
        medical_center = str(self.medical_center_input.text())
        stages = []
        for row in range(self.table_widget.rowCount()):
            combo_boxes = self.table_widget.cellWidget(row, 1).findChildren(QComboBox)
            stages.append({'stage_name': f'{self.table_widget.cellWidget(row, 0).currentText()}',
                           'timing': f'{combo_boxes[0].currentText().zfill(2)+":"+combo_boxes[1].currentText().zfill(2)+":"+combo_boxes[2].currentText().zfill(2)}',
                           'bloodloss': f'{0 if self.table_widget.cellWidget(row, 2).text() == "" else self.table_widget.cellWidget(row, 2).text()}'})
        data = {"patient_id": f"{patient_id}", "operation_type": f"{operation_type}",
                "organ": f"{organ}", "operation_date": f"{operation_date}",
                "stages": f"{stages}", "description": f"{description}", "medical_center": f"{medical_center}"}
        # Передача файлов
        if len(self.file_paths) != 0:
            files = [('files', open(file_path, 'rb')) for file_path in self.file_paths]
            header = {'Authorization': f'{self.token}'}
            response = requests.post(url, headers=header, data=data, files=files)
            if (response.status_code == 200) or (response.status_code == 201):
                json_response = response.json()
                print('Запись об операции создана:', response.status_code, json_response)
                self.save_operation()
            else:
                print('Ошибка создания записи об операции:', response.status_code, response.json())
        else:
            print('Файлы не выбраны')

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

    def load_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите видеофайл", "", "Видео файлы (*.mp4 *.avi *.mov)",
                                                options=options)
        if files:
            # Ограничиваем количество выбранных файлов до 2-х
            if len(files) + self.list_widget.count() > 2:
                remaining_slots = 2 - self.list_widget.count()
                selected_files = files[:remaining_slots]
            else:
                selected_files = files

            for file in selected_files:
                self.file_paths.append(file)
                self.list_widget.addItem(file)

    def remove_files(self):
        self.list_widget.clear()
        self.file_paths = []
