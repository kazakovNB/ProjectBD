import sys
import requests
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QListWidget, \
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHBoxLayout, QHeaderView, QComboBox
import time
import datetime


from utils import safe_parse_list
from config import build_url
class FavoriteList(QWidget):
    switch_window = Signal()

    def __init__(self, on_operation_selected, token):
        super().__init__()
        self.on_operation_selected = on_operation_selected
        self.token = token

        self.search_string = ''
        self.operation_number = 0
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        button_cell_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operationListButton = QPushButton('К списку операций')
        self.operationListButton.clicked.connect(self.go_operation_list_widget)
        self.operationListButton.setFixedSize(150, 50)
        button_layout.addWidget(self.operationListButton)
        button_cell_widget.setLayout(button_layout)
        button_cell_widget.setFixedSize(1017, 50)
        layout.addWidget(button_cell_widget, alignment=Qt.AlignCenter)

        table_cell_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)
        table_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        cell_widget = QWidget()
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(10)
        hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.string_input = QLineEdit(self)
        self.string_input.setPlaceholderText("Введите текст для поиска операции")
        self.string_input.setFixedSize(300, 25)
        hlayout.addWidget(self.string_input)
        self.searchButton = QPushButton('Поиск')
        self.searchButton.clicked.connect(self.search)
        self.searchButton.setFixedSize(75, 25)
        hlayout.addWidget(self.searchButton)
        cell_widget.setLayout(hlayout)
        cell_widget.setFixedSize(1017, 25)
        table_layout.addWidget(cell_widget)

        self.table_widget = QTableWidget(0, 8)
        self.table_widget.setHorizontalHeaderLabels(["ID записи", "ID создателя записи", "ID пациента", "Тип операции",
                                                     "Орган", "Дата и время операции", "Клиника", "Добавление в избранное"])
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
        self.table_widget.setColumnWidth(2, 100)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnWidth(4, 100)
        self.table_widget.setColumnWidth(5, 150)
        self.table_widget.setColumnWidth(6, 100)
        self.table_widget.setColumnWidth(7, 150)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_widget.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTriggers.NoEditTriggers)
        self.table_widget.itemClicked.connect(self.highlight_row)
        self.table_widget.setFixedSize(1017, 628)
        url = build_url('/get_favourites')
        self.page_number = 1
        data = {"page_number": f"{self.page_number}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            self.add_favorite(json_response)
            self.max_number_of_pages = int(json_response['max_number_of_pages'])
        else:
            print('Ошибка при получении списка операций:', response.status_code, response.json())

        self.table_widget.cellDoubleClicked.connect(self.on_cell_item_clicked)

        table_layout.addWidget(self.table_widget)

        cell_widget2 = QWidget()
        hlayout2 = QHBoxLayout()
        hlayout2.setContentsMargins(0, 0, 0, 0)
        hlayout2.setSpacing(10)
        hlayout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.backwardButton = QPushButton('Предыдущая страница')
        self.backwardButton.clicked.connect(self.go_backward)
        self.backwardButton.setFixedSize(150, 25)
        hlayout2.addWidget(self.backwardButton)

        self.now_page = QComboBox()
        self.now_page.setFixedSize(75, 25)
        self.now_page.addItems([str(i) for i in range(1, self.max_number_of_pages + 1)])
        self.now_page.setCurrentIndex(self.now_page.findText(str(self.page_number)))
        self.now_page.currentIndexChanged.connect(self.update_page)
        hlayout2.addWidget(self.now_page)
        self.slash = QLabel()
        self.slash.setFixedSize(25, 25)
        self.slash.setText('/')
        self.slash.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout2.addWidget(self.slash)
        self.max_page = QLabel()
        self.max_page.setFixedSize(50, 25)
        self.max_page.setText(str(self.max_number_of_pages))
        hlayout2.addWidget(self.max_page)

        self.forwardButton = QPushButton('Следующая страница')
        self.forwardButton.clicked.connect(self.go_forward)
        self.forwardButton.setFixedSize(150, 25)
        hlayout2.addWidget(self.forwardButton)
        cell_widget2.setLayout(hlayout2)
        cell_widget2.setFixedSize(1017, 25)
        table_layout.addWidget(cell_widget2)
        table_cell_widget.setLayout(table_layout)

        layout.addWidget(table_cell_widget, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def on_cell_item_clicked(self, row, column=None):
        operation_id = self.table_widget.item(row, 0).text()
        self.on_operation_selected(operation_id)

    def go_operation_list_widget(self):
        self.switch_window.emit()

    def highlight_row(self, item):
        # Сначала сбрасываем цвет всех строк на исходный
        for row in range(self.table_widget.rowCount()):
            for column in range(self.table_widget.columnCount()):
                self.table_widget.item(row, column).setBackground(Qt.white)

        # Затем подсвечиваем выбранную строку
        row = item.row()
        for column in range(self.table_widget.columnCount()):
            self.table_widget.item(row, column).setBackground(Qt.gray)  # Выбери любой цвет

    def add_favorite(self, response):
        operations = safe_parse_list(response['operations'])
        self.table_widget.setRowCount(len(operations))
        vertical_headers = [str(self.operation_number + i + 1) for i in range(len(operations))]
        self.table_widget.setVerticalHeaderLabels(vertical_headers)
        if len(operations) > 0:
            keys = list(operations[0])
        for row in range(len(operations)):
            self.operation_number += 1
            for column in range(len(keys)):
                item = QTableWidgetItem(str(operations[row][keys[column]]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, column, item)

    def search(self):
        url = build_url('/search_favourite')
        self.search_string = self.string_input.text()
        data = {"page_number": "1", "search_string": f"{self.search_string}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            self.now_page.currentIndexChanged.disconnect(self.update_page)
            self.now_page.clear()
            self.max_number_of_pages = int(json_response['max_number_of_pages'])
            self.max_page.setText(str(self.max_number_of_pages))
            self.page_number = 1
            self.now_page.addItems([str(i) for i in range(1, self.max_number_of_pages + 1)])
            self.now_page.setCurrentIndex(self.now_page.findText(str(self.page_number)))
            self.now_page.currentIndexChanged.connect(self.update_page)
            self.operation_number = 0
            for i in range(self.table_widget.rowCount()):
                self.table_widget.removeRow(0)
            self.add_favorite(json_response)
        else:
            print('Ошибка при поиске избранного:', response.status_code, response.json())

    def go_forward(self):
        if self.page_number < self.max_number_of_pages:
            self.now_page.setCurrentIndex(self.now_page.currentIndex() + 1)

    def go_backward(self):
        if self.page_number > 1:
            self.now_page.setCurrentIndex(self.now_page.currentIndex() - 1)

    def update_page(self):
        url = build_url('/search_favourite')
        self.page_number = int(self.now_page.currentText())
        self.operation_number = 20 * (self.page_number - 1)
        data = {"page_number": f"{self.page_number}", "search_string": f"{self.search_string}"}
        header = {'Authorization': f'{self.token}'}
        response = requests.get(url, headers=header, json=data)
        if (response.status_code == 200) or (response.status_code == 201):
            json_response = response.json()
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            self.add_favorite(json_response)
            self.max_number_of_pages = int(json_response['max_number_of_pages'])
            self.max_page.setText(str(self.max_number_of_pages))
        else:
            print('Ошибка при получении списка избранного:', response.status_code, response.json())