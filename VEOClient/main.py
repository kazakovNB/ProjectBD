import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QSizePolicy
import OperationList
import VideoPlayer
import AR
import UserList
import UserDetails
import ChangingUser
import ChangingOperation
import CreateOperation
import FavoriteList
import FavoritePlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VEOClient")
        self.setGeometry(500, 40, 500, 660)
        self.setFixedSize(500, 660)

        self.token = None
        self.role = None

        # Создаем основной контейнер
        self.stacked_widget = QStackedWidget()

        # Добавляем страницы
        self.authorization_widget = AR.Authorization(self.on_authorized)
        self.authorization_widget.switch_window.connect(self.switch_to_registration_widget)
        self.stacked_widget.addWidget(self.authorization_widget)

        self.setCentralWidget(self.stacked_widget)

    def on_authorized(self, token, role):
        self.token = token
        self.role = role
        self.operation_list_widget = OperationList.OperationList(self.show_operation_details, self.token, role,
                                                                 self.create_operation)
        self.operation_list_widget.to_users.connect(self.switch_from_operations_to_users)
        self.operation_list_widget.to_favorites.connect(self.switch_from_operations_to_favorites)
        self.operation_list_widget.exit.connect(self.exit_from_system)
        self.setGeometry(250, 40, 1035, 770)
        self.setFixedSize(1035, 770)
        self.stacked_widget.addWidget(self.operation_list_widget)
        self.stacked_widget.setCurrentWidget(self.operation_list_widget)

    def show_operation_details(self, operation_id):
        self.operation_details_widget = VideoPlayer.VideoPlayer(operation_id, self.token, self.role, self.change_operation, self.after_delete_operation)
        self.operation_details_widget.switch_window.connect(self.switch_to_operation_list_widget)
        self.stacked_widget.addWidget(self.operation_details_widget)
        self.stacked_widget.setCurrentWidget(self.operation_details_widget)

    def show_favorite_details(self, operation_id):
        self.favorite_details_widget = FavoritePlayer.FavoritePlayer(operation_id, self.token, self.role,  self.after_delete_favorite)
        self.favorite_details_widget.switch_window.connect(self.switch_to_favorite_list_widget)
        self.stacked_widget.addWidget(self.favorite_details_widget)
        self.stacked_widget.setCurrentWidget(self.favorite_details_widget)

    def after_delete_favorite(self):
        self.stacked_widget.removeWidget(self.favorite_list_widget)
        self.favorite_list_widget.deleteLater()
        self.favorite_list_widget = FavoriteList.FavoriteList(self.show_favorite_details, self.token)
        self.favorite_list_widget.switch_window.connect(self.switch_from_favorites_to_operations)
        self.stacked_widget.addWidget(self.favorite_list_widget)
        self.stacked_widget.setCurrentWidget(self.favorite_list_widget)
        self.stacked_widget.removeWidget(self.favorite_details_widget)
        self.favorite_details_widget.deleteLater()

    def switch_to_favorite_list_widget(self):
        self.stacked_widget.setCurrentWidget(self.favorite_list_widget)
        self.stacked_widget.removeWidget(self.favorite_details_widget)
        self.favorite_details_widget.deleteLater()

    def after_delete_operation(self):
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()
        self.on_authorized(self.token, self.role)
        self.stacked_widget.removeWidget(self.operation_details_widget)
        self.operation_details_widget.deleteLater()

    def create_operation(self):
        self.create_operation_widget = CreateOperation.CreateOperation(self.token, self.save_operation)
        self.create_operation_widget.switch_window.connect(self.switch_to_operation_list_from_creating)
        self.stacked_widget.addWidget(self.create_operation_widget)
        self.stacked_widget.setCurrentWidget(self.create_operation_widget)
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()

    def change_operation(self, data):
        self.changing_operation_widget = ChangingOperation.ChangingOperation(data, self.token, self.save_operation_changes)
        self.changing_operation_widget.switch_window.connect(self.switch_to_operation_details_widget)
        self.stacked_widget.addWidget(self.changing_operation_widget)
        self.stacked_widget.setCurrentWidget(self.changing_operation_widget)

    def save_operation_changes(self, operation_id):
        self.stacked_widget.removeWidget(self.operation_details_widget)
        self.operation_details_widget.deleteLater()
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()
        self.operation_list_widget = OperationList.OperationList(self.show_operation_details, self.token, self.role,
                                                                 self.create_operation)
        self.operation_list_widget.to_users.connect(self.switch_from_operations_to_users)
        self.operation_list_widget.to_favorites.connect(self.switch_from_operations_to_favorites)
        self.operation_list_widget.exit.connect(self.exit_from_system)
        self.stacked_widget.addWidget(self.operation_list_widget)
        self.show_operation_details(operation_id)
        self.stacked_widget.removeWidget(self.changing_operation_widget)
        self.changing_operation_widget.deleteLater()

    def switch_to_operation_list_from_creating(self):
        self.on_authorized(self.token, self.role)
        self.stacked_widget.setCurrentWidget(self.operation_list_widget)
        self.stacked_widget.removeWidget(self.create_operation_widget)
        self.create_operation_widget.deleteLater()

    def save_operation(self):
        self.on_authorized(self.token, self.role)
        self.stacked_widget.removeWidget(self.create_operation_widget)
        self.create_operation_widget.deleteLater()

    def switch_to_operation_details_widget(self):
        self.stacked_widget.setCurrentWidget(self.operation_details_widget)
        self.stacked_widget.removeWidget(self.changing_operation_widget)
        self.changing_operation_widget.deleteLater()

    def switch_from_operations_to_favorites(self):
        self.favorite_list_widget = FavoriteList.FavoriteList(self.show_favorite_details, self.token)
        self.favorite_list_widget.switch_window.connect(self.switch_from_favorites_to_operations)
        self.stacked_widget.addWidget(self.favorite_list_widget)
        self.stacked_widget.setCurrentWidget(self.favorite_list_widget)
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()

    def switch_from_favorites_to_operations(self):
        self.on_authorized(self.token, self.role)
        self.stacked_widget.setCurrentWidget(self.operation_list_widget)
        self.stacked_widget.removeWidget(self.favorite_list_widget)
        self.favorite_list_widget.deleteLater()

    def switch_from_operations_to_users(self):
        self.user_list_widget = UserList.UserList(self.show_user_details, self.token)
        self.user_list_widget.switch_window.connect(self.switch_from_users_to_operations)
        self.stacked_widget.addWidget(self.user_list_widget)
        self.stacked_widget.setCurrentWidget(self.user_list_widget)
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()

    def show_user_details(self, user_id):
        self.user_details_widget = UserDetails.UserDetails(user_id, self.token, self.change_user)
        self.user_details_widget.switch_window.connect(self.switch_to_user_list_widget)
        self.stacked_widget.addWidget(self.user_details_widget)
        self.stacked_widget.setCurrentWidget(self.user_details_widget)

    def switch_from_users_to_operations(self):
        self.on_authorized(self.token, self.role)
        self.stacked_widget.setCurrentWidget(self.operation_list_widget)
        self.stacked_widget.removeWidget(self.user_list_widget)
        self.user_list_widget.deleteLater()

    def switch_to_operation_list_widget(self):
        self.stacked_widget.setCurrentWidget(self.operation_list_widget)
        self.stacked_widget.removeWidget(self.operation_details_widget)
        self.operation_details_widget.deleteLater()

    def switch_to_user_list_widget(self):
        self.stacked_widget.removeWidget(self.user_list_widget)
        self.user_list_widget.deleteLater()
        self.user_list_widget = UserList.UserList(self.show_user_details, self.token)
        self.user_list_widget.switch_window.connect(self.switch_from_users_to_operations)
        self.stacked_widget.addWidget(self.user_list_widget)
        self.stacked_widget.setCurrentWidget(self.user_list_widget)
        self.stacked_widget.removeWidget(self.user_details_widget)
        self.user_details_widget.deleteLater()

    def change_user(self, data):
        self.changing_user_widget = ChangingUser.ChangingUser(data, self.token, self.save_user_changes)
        self.changing_user_widget.switch_window.connect(self.switch_to_user_details_widget)
        self.stacked_widget.addWidget(self.changing_user_widget)
        self.stacked_widget.setCurrentWidget(self.changing_user_widget)

    def save_user_changes(self, user_id):
        self.stacked_widget.removeWidget(self.user_details_widget)
        self.user_details_widget.deleteLater()
        self.stacked_widget.removeWidget(self.user_list_widget)
        self.user_list_widget.deleteLater()
        self.user_list_widget = UserList.UserList(self.show_user_details, self.token)
        self.user_list_widget.switch_window.connect(self.switch_from_users_to_operations)
        self.stacked_widget.addWidget(self.user_list_widget)
        self.show_user_details(user_id)
        self.stacked_widget.removeWidget(self.changing_user_widget)
        self.changing_user_widget.deleteLater()

    def switch_to_user_details_widget(self):
        self.stacked_widget.setCurrentWidget(self.user_details_widget)
        self.stacked_widget.removeWidget(self.changing_user_widget)
        self.changing_user_widget.deleteLater()

    def switch_to_registration_widget(self):
        self.registration_widget = AR.Registration()
        self.registration_widget.switch_window.connect(self.switch_to_authorization_widget)
        self.stacked_widget.addWidget(self.registration_widget)
        self.stacked_widget.setCurrentWidget(self.registration_widget)

    def switch_to_authorization_widget(self):
        self.stacked_widget.setCurrentWidget(self.authorization_widget)
        self.stacked_widget.removeWidget(self.registration_widget)
        self.registration_widget.deleteLater()

    def exit_from_system(self):
        self.stacked_widget.setCurrentWidget(self.authorization_widget)
        self.stacked_widget.removeWidget(self.operation_list_widget)
        self.operation_list_widget.deleteLater()
        self.setGeometry(500, 40, 500, 660)
        self.setFixedSize(500, 660)
        self.token = None
        self.role = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
