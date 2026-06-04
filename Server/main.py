from flask import Flask, jsonify, request, send_from_directory, send_file, Response
import zipfile
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, String, cast, and_
import psycopg2
from psycopg2.extensions import AsIs
import datetime
import hashlib
from functools import wraps
import os


app = Flask(__name__)

# --- Config (works both in source and PyInstaller .exe) ---
try:
    from dotenv import load_dotenv
    # Load .env from current working dir and from folder near the executable/script
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(base_dir, '.env'), override=False)
    load_dotenv(override=False)
except Exception:
    pass

# Priority: SQLALCHEMY_DATABASE_URI -> DATABASE_URL -> fallback
DEFAULT_DATABASE_URL = 'postgresql+psycopg2://postgres:admin123@127.0.0.1:5432/veomodern'
db_url = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL') or DEFAULT_DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# JWT secret
SECRET_KEY = os.environ.get('SECRET_KEY', 'jwt_secret_for_development_part_veomigration')
db = SQLAlchemy(app)

# Upload folder: prefer env, else ProgramData (so it works from Program Files without admin rights)
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'VEO', 'videos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print('=== VEO Server starting ===')
print('App root:', base_dir)
print('ENV DATABASE_URL:', os.environ.get('DATABASE_URL'))
print('ENV UPLOAD_FOLDER:', os.environ.get('UPLOAD_FOLDER'))
print('SQLALCHEMY_DATABASE_URI:', app.config['SQLALCHEMY_DATABASE_URI'])


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, db.Identity(), primary_key=True, nullable=False, unique=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    registration = db.Column(db.TIMESTAMP, nullable=False)
    job_title = db.Column(db.String(100), nullable=True)
    organization = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    university = db.Column(db.String(200), nullable=True)
    student_group = db.Column(db.String(50), nullable=True)
    role = relationship("Role", back_populates="user", cascade="all, delete")
    operations = relationship("Operation", back_populates="doctor", cascade="all, delete")
    favourites = relationship("Favourite", back_populates="developer", cascade="all, delete")

    def __repr__(self):
        return f"user_id={self.user_id}, " \
               f"name={self.name}, " \
               f"surname={self.surname}, " \
               f"patronymic={self.patronymic}, " \
               f"login={self.login}, " \
               f"active={self.active}, " \
               f"role={self.role[0]}"


class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, db.Identity(), primary_key=True, nullable=False)
    role_name = db.Column(db.String(100), nullable=False)
    user = relationship('User', back_populates='role')

    def __repr__(self):
        return self.role_name


class Operation(db.Model):
    __tablename__ = 'operations'
    operation_id = db.Column(db.Integer, db.Identity(), primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    patient_id = db.Column(db.Integer, nullable=False)
    operation_type = db.Column(db.Integer, db.ForeignKey('types.type_id'))
    organ = db.Column(db.String(100), nullable=False)
    file_video_path1 = db.Column(db.String(500), nullable=False, unique=True)
    file_video_path2 = db.Column(db.String(500), nullable=True, unique=True)
    medical_center = db.Column(db.String(500), nullable=True)
    description = db.Column(db.TEXT, nullable=True)
    operation_date = db.Column(db.TIMESTAMP, nullable=False)
    doctor = relationship('User', back_populates='operations')
    favourites = relationship('Favourite', back_populates='operation', cascade="all, delete")
    type = relationship("Type", back_populates="operations")
    stages = relationship("StagesOfOperation", back_populates="operation")

    def __repr__(self):
        return '%r' % self.operation_id


class Type(db.Model):
    __tablename__ = 'types'
    type_id = db.Column(db.Integer, primary_key=True, nullable=False)
    type_name = db.Column(db.String(100), nullable=False)
    operations = relationship("Operation", back_populates="type")
    stages = relationship("Stage", back_populates="type")

    def __repr__(self):
        return self.type_name


class Stage(db.Model):
    __tablename__ = 'stages'
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'))
    stage_id = db.Column(db.Integer, primary_key=True, nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)
    type = relationship('Type', back_populates='stages')
    stage = relationship('StagesOfOperation', back_populates='stages')

    def __repr__(self):
        return '%r' % self.stage_id


class StagesOfOperation(db.Model):
    __tablename__ = 'stagesofoperations'
    id = db.Column(db.Integer, db.Identity(), primary_key=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.operation_id'))
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.stage_id'))
    timing = db.Column(db.Time, nullable=False)
    bloodloss = db.Column(db.Integer, nullable=False)
    operation = relationship('Operation', back_populates='stages')
    stages = relationship('Stage', back_populates='stage')

    def __repr__(self):
        return f"operation_id={self.operation_id}, " \
               f"stage_name={self.stage_name}" \
               f"timing={self.timing}"


class Favourite(db.Model):
    __tablename__ = 'favourites'
    id = db.Column(db.Integer, db.Identity(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.operation_id'))
    saving_date = db.Column(db.DateTime, nullable=False)
    developer = relationship('User', back_populates='favourites')
    operation = relationship('Operation', back_populates='favourites')

    def __repr__(self):
        return '%r' % self.id


# Декоратор токена
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'message': 'Токен не передан'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            login = data['login']  # Извлекаем логин пользователя из токена
            role_id = data['role_id']  # Извлекаем роль пользователя
            life_time = data['exp']  # Извлекаем срок действия токена
            if db.session.query(User).filter(User.login == login).first() is False:
                return jsonify({'message': 'Аккаунт не активен'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Срок действия токена истёк'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Недействительный токен'}), 401
        return f(login, role_id, life_time, *args, **kwargs)
    return decorated


# Регистрация пользователя
@app.route('/registering', methods=['POST'])
def registering():
    data = request.json
    hashed_password = hashlib.sha512(data['password'].encode())
    hashed_password = hashed_password.hexdigest()
    for i in data:
        if data[f'{i}'] == '':
            data[f'{i}'] = None
    if db.session.query(User).filter(User.login == data['login'].lower()).first():
        return jsonify({"message": "Пользователь с таким логином уже существует"}), 409
    new_user = User(login=data['login'].lower(), password=hashed_password, role_id=db.session.query(Role).filter(Role.role_name
                                                                                                                 == data['role']).first().role_id,
                    name=data['name'].capitalize(),
                    surname=data['surname'].capitalize(), patronymic=data['patronymic'].capitalize(),
                    birthday=data['birthday'], registration=str(datetime.datetime.now()).split('.')[0], active=False,
                    job_title=data['job_title'], department=data['department'],
                    university=data['university'], student_group=data['student_group'],
                    organization=data['organization'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Пользователь создан, дождитесь активации акаунта"}), 201


# Активация акаунта
@app.route('/activation', methods=['PATCH'])
@token_required
def activation(login, role_id, life_time):
    if role_id == '1':
        data = request.json
        not_active_user = data['user_id']
        user_activation = db.session.get(User, not_active_user)
        if user_activation:
            if user_activation.active:
                return jsonify({"message": "Акаунт уже активен"}), 201
            db.session.query(User).filter(User.user_id == not_active_user).update({'active': True})
            db.session.commit()
        else:
            return jsonify({"message": "Пользователь не найден"}), 404
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403
    return jsonify({"message": "Акаунт активен"}), 201


# Авторизация пользователя
@app.route('/logining', methods=['POST'])
def logining():
    data = request.json
    user = User.query.filter(User.login == data['login'].lower()).first()
    if user is None:
        return jsonify({"message": "Пользователь не найден"}), 401
    elif user.active is not True:
        return jsonify({"message": "Акаунт не активен"}), 401
    else:
        user_password = user.password
        recieved_password = hashlib.sha512(data['password'].encode()).hexdigest()
        if user and user_password == recieved_password and user.active:
            life_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            token_info = {
                'login': user.login,
                'role_id': str(user.role_id),
                'exp': life_time
            }
            token = jwt.encode(token_info, SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            return jsonify(access_token=token, role_id=str(user.role_id)), 200


# Редактирование пользователя
@app.route('/update_user', methods=['PUT'])
@token_required
def update_user(login, role_id, life_time):
    if role_id == '1':
        received_data = request.json
        for i in received_data:
            if received_data[f'{i}'] == '':
                received_data[f'{i}'] = None

        user_id = str(received_data['user_id'])
        new_name = received_data['name'].lower()
        new_surname = received_data['surname'].lower()
        new_patronymic = received_data['patronymic'].lower()
        new_role = received_data['role']
        new_birthday = received_data['birthday']
        new_login = received_data['login'].lower()
        new_organization = received_data['organization']
        new_job_title = received_data['job_title']
        new_department = received_data['department']
        new_university = received_data['university']
        new_student_group = received_data['student_group']

        old_user = User.query.filter(User.user_id == user_id).first()
        if old_user is None:
            return jsonify({"message": "Пользователь не найден"}), 404
        old_role = db.session.query(Role).filter(Role.role_id == old_user.role_id).first().role_name

        if old_role != new_role:
            db.session.query(User).filter(User.user_id == user_id).update({'role_id': db.session.query(Role).filter(Role.role_name == new_role).first().role_id})
            db.session.commit()

        if old_user.login != new_login:
            db.session.query(User).filter(User.user_id == user_id).update({'login': new_login})
            db.session.commit()

        if old_user.name != new_name or old_user.surname != new_surname or old_user.patronymic != new_patronymic\
                or old_user.birthday != new_birthday:
            db.session.query(User).filter(User.user_id == user_id).update({'name': new_name.capitalize(),
                                                                           'surname': new_surname.capitalize(),
                                                                           'patronymic': new_patronymic.capitalize(),
                                                                           'birthday': new_birthday})
            db.session.commit()

        if old_user.student_group != new_student_group or old_user.department != new_department\
                or old_user.university != new_university:
            db.session.query(User).filter(User.user_id == user_id).update({'student_group': new_student_group,
                                                                           'university': new_university,
                                                                           'department': new_department})
            db.session.commit()

        if old_user.job_title != new_job_title or old_user.organization != new_organization:
            db.session.query(User).filter(User.user_id == user_id).update({'organization': new_organization,
                                                                           'job_title': new_job_title})
            db.session.commit()

        if received_data['password'] and received_data['password'] != '':
            new_password = hashlib.sha512(received_data['password'].encode())
            new_password = new_password.hexdigest()
            if old_user.password != new_password:
                db.session.query(User).filter(User.user_id == user_id).update({'password': new_password})
                db.session.commit()

    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403

    return jsonify({"message": "Пользователь изменён"}), 201


# Удаление пользователя
@app.route('/delete_user', methods=['POST'])
@token_required
def delete_user(login, role_id, life_time):
    if role_id == '1':
        data = request.json
        user_id = str(data['user_id'])
        deliting_user = User.query.filter(User.user_id == user_id).first()
        if deliting_user:
            if deliting_user.active is True:
                db.session.query(User).filter(User.user_id == user_id).update({'active': False})
                db.session.commit()
                db.session.query(Favourite).filter(Favourite.user_id == user_id).delete()
                db.session.commit()
            if db.session.query(Operation).filter(Operation.user_id == user_id).first():
                return jsonify({"message": "Пользователь не может быть полностью удалён"}), 206
            db.session.query(Role).filter(Role.user_id == user_id).delete()
            db.session.commit()
            db.session.query(User).filter(User.user_id == user_id).delete()
            db.session.commit()
        else:
            return jsonify({"message": "Пользователь не найден"}), 404
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403
    return jsonify({"message": "Пользователь удалён"}), 200


# Просмотр конкретного пользователя
@app.route('/get_user', methods=['GET'])
@token_required
def get_user(login, role_id, life_time):
    if role_id == '1':
        data = request.json
        user_id = data['user_id']
        user = User.query.filter(User.user_id == user_id).first()
        if user is None:
            return jsonify({"message": "Пользователь не найден"}), 404
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403
    return jsonify({"user_id": f"{user_id}", "name": f"{user.name}", "surname": f"{user.surname}",
                    "patronymic": f"{user.patronymic}", "login": f"{user.login}", "active": f"{user.active}",
                    "birthday": f"{user.birthday}", "registration": f"{user.registration}",
                    "job_title": f"{user.job_title}", "organization": f"{user.organization}",
                    "department": f"{user.department}", "university": f"{user.university}",
                    "student_group": f"{user.student_group}", "role": f'{user.role}'})


# Получение списка пользователей
@app.route('/get_users', methods=['GET'])
@token_required
def get_users(login, role_id, life_time):
    if role_id == '1':
        data = request.json or {}
        # page_number приходит строкой, сразу приводим к числу
        page_number = int(data.get('page_number', 1))

        number_of_users = db.session.query(User).count()
        max_number_of_pages = 1 if number_of_users <= 20 else ((number_of_users // 20) + 1)

        if page_number > max_number_of_pages:
            return jsonify({"message": "Страница не найдена"}), 404

        users = db.session.query(User).offset((page_number - 1) * 20).limit(20).all()

        ten_users = [
            {
                'user_id': user.user_id,
                'login': user.login,
                'name': user.name,
                'surname': user.surname,
                'patronymic': user.patronymic,
                'role': f'{user.role}',
                "registration": f"{(user.registration.isoformat()).replace('T', ' ')}",
                'active': user.active
            }
            for user in users
        ]
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403

    return jsonify({
        "max_number_of_pages": f"{max_number_of_pages}",
        "users": f"{ten_users}"
    })


# Поиск пользователя
@app.route('/search_user', methods=['GET'])
@token_required
def search_user(login, role_id, life_time):
    if role_id == '1':
        data = request.json
        search_string = data['search_string']
        if search_string == '':
            return get_users()
        page_number = int(data['page_number'])
        users = db.session.query(User).join(Role).filter(or_(cast(User.user_id, String).ilike(f'%{search_string}%'),
                                                             cast(User.registration, String).ilike(f'%{search_string}%'),
                                                             User.name.ilike(f'%{search_string}%'),
                                                             User.surname.ilike(f'%{search_string}%'),
                                                             User.patronymic.ilike(f'%{search_string}%'),
                                                             User.login.ilike(f'%{search_string}%'),
                                                             Role.role_name.ilike(f'%{search_string}%'),
                                                             cast(User.active, String).ilike(f'%{search_string}%'))
                                                         )
        number_of_users = users.count()
        max_number_of_pages = 1 if number_of_users <= 20 else ((number_of_users // 20) + 1)
        if page_number > max_number_of_pages:
            return jsonify({"message": "Страница не найдена"}), 404
        users = users.offset((page_number - 1) * 20).limit(20).all()
        ten_users = [{'user_id': user.user_id, 'login': user.login, 'name': user.name, 'surname': user.surname,
                      'patronymic': user.patronymic, 'role': f"{user.role}",
                      "registration": f"{(user.registration.isoformat()).replace('T', ' ')}", 'active': user.active}
                     for user in users]
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора"}), 403
    return jsonify({"max_number_of_pages": f"{max_number_of_pages}", "users": f"{ten_users}"})


# Получение ролей
@app.route('/get_roles', methods=['GET'])
def get_roles():
    roles = {}
    all_roles = db.session.query(Role).with_entities(Role.role_name).all()
    roles['roles'] = [role[0] for role in all_roles]
    return jsonify(roles)


# Создание операции
@app.route('/create_operation', methods=['POST'])
@token_required
def create_operation(login, role_id, life_time):
    if role_id == '2' or role_id == '1':
        user_id = User.query.filter(User.login == login).first().user_id
        operation_type = request.form.get('operation_type').capitalize()
        if operation_type == 'None':
            return jsonify({"message": "Тип None при создании записи не допустим"}), 403
        patient_id = request.form.get('patient_id')
        organ = request.form.get('organ').capitalize()
        operation_date = request.form.get('operation_date')
        description = request.form.get('description')
        medical_center = request.form.get('medical_center')
        stages = eval(request.form.get('stages'))
        files = request.files.getlist('files')
        files_count = 0
        file_paths = []
        for file in files:
            if file:
                files_count += 1
                filename = f"{str(patient_id)}" + f"{str(operation_type)[0]}" \
                           + f"{str(organ)[0]}" + f"{str(operation_date).replace(':', '')}" + f"{str(files_count)}" + ".mp4"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_paths.append(file_path)
                file.save(file_path)
        if files_count == 0:
            return jsonify({"message": "Файлы не переданы"}), 400
        if files_count == 1:
            new_operation = Operation(user_id=user_id, operation_type=db.session.query(Type).filter(Type.type_name == operation_type).first().type_id, organ=organ,
                                      file_video_path1=file_paths[0], file_video_path2=None,
                                      patient_id=patient_id, operation_date=operation_date,
                                      description=description, medical_center=medical_center)
            db.session.add(new_operation)
            db.session.commit()
        if files_count == 2:
            new_operation = Operation(user_id=user_id, operation_type=db.session.query(Type).filter(Type.type_name == operation_type).first().type_id, organ=organ,
                                      file_video_path1=file_paths[0], file_video_path2=file_paths[1],
                                      patient_id=patient_id, operation_date=operation_date,
                                      description=description, medical_center=medical_center)
            db.session.add(new_operation)
            db.session.commit()
        for stage in stages:
            stage_of_new_operation = StagesOfOperation(operation_id=new_operation.operation_id,
                                                       stage_id=db.session.query(Stage).filter(Stage.stage_name == stage['stage_name']).first().stage_id,
                                                       timing=stage['timing'],
                                                       bloodloss=stage['bloodloss'])
            db.session.add(stage_of_new_operation)
            db.session.commit()
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора или врача"}), 403
    return jsonify({"message": "Запись об операции успешно создана"}), 201


# Обновление операции
@app.route('/update_operation', methods=['PUT'])
@token_required
def update_operation(login, role_id, life_time):
    # права доступа
    if role_id not in ('1', '2'):
        return jsonify({"message": "Пользователь должен иметь права врача или администратора"}), 403

    operation_id = request.form.get('operation_id')
    old_operation = Operation.query.filter(Operation.operation_id == operation_id).first()
    if old_operation is None:
        return jsonify({"message": "Запись об операции не найдена"}), 404

    user_id = old_operation.user_id
    if role_id == '2' and User.query.filter(User.login == login).first().user_id != user_id:
        return jsonify(
            {"message": "Запись об операции может быть обновлена только её создателем или администратором"}), 403

    # ----- читаем новые данные -----
    new_operation_type = request.form.get('operation_type')
    new_patient_id = request.form.get('patient_id')
    new_organ = request.form.get('organ')
    new_operation_date = request.form.get('operation_date')
    new_description = request.form.get('description')
    new_medical_center = request.form.get('medical_center')
    new_stages_raw = request.form.get('stages')

    # приводим строки
    if new_operation_type is not None and new_operation_type != 'None':
        new_operation_type = new_operation_type.capitalize()
    if new_organ is not None and new_organ != 'None':
        new_organ = new_organ.capitalize()

    # ----- обновление типа операции -----
    if new_operation_type and new_operation_type != 'None':
        old_type = db.session.query(Type).filter(Type.type_id == old_operation.operation_type).first()
        old_type_name = old_type.type_name if old_type else None

        if new_operation_type != old_type_name:
            new_type = db.session.query(Type).filter(Type.type_name == new_operation_type).first()
            if new_type is None:
                return jsonify({"message": f"Тип операции '{new_operation_type}' не найден"}), 400

            db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
                {'operation_type': new_type.type_id}
            )
            db.session.commit()

    # ----- обновление прочих полей -----
    if new_medical_center != old_operation.medical_center:
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'medical_center': new_medical_center})
        db.session.commit()

    if new_organ != old_operation.organ:
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'organ': new_organ})
        db.session.commit()

    if new_description != old_operation.description:
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'description': new_description})
        db.session.commit()

    if new_patient_id != str(old_operation.patient_id):
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'patient_id': new_patient_id})
        db.session.commit()

    if new_operation_date != str(old_operation.operation_date):
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'operation_date': new_operation_date})
        db.session.commit()

    # ----- ОБНОВЛЕНИЕ ЭТАПОВ -----
    print("update_operation(): stages from client:", new_stages_raw)

    # если stages не пришли или равны 'None' – просто не трогаем этапы
    if new_stages_raw and new_stages_raw != 'None':
        try:
            stages_list = eval(new_stages_raw)  # формат как при создании операции
        except Exception:
            return jsonify({"message": "Некорректный формат этапов операции"}), 400

        # удаляем старые этапы этой операции
        db.session.query(StagesOfOperation).filter(
            StagesOfOperation.operation_id == operation_id
        ).delete()
        db.session.commit()

        # записываем новые
        for stage in stages_list:
            stage_name = stage.get('stage_name')
            timing = stage.get('timing')
            bloodloss = stage.get('bloodloss')

            if not stage_name:
                return jsonify({"message": "У одного из этапов не задано имя"}), 400

            stage_row = db.session.query(Stage).filter(Stage.stage_name == stage_name).first()
            if stage_row is None:
                return jsonify(
                    {"message": f"Этап '{stage_name}' не найден в таблице stages"}
                ), 400

            new_stage_of_operation = StagesOfOperation(
                operation_id=operation_id,
                stage_id=stage_row.stage_id,
                timing=timing,
                bloodloss=bloodloss
            )
            db.session.add(new_stage_of_operation)

        db.session.commit()

    # ----- файлы -----
    files = request.files.getlist('files')
    files_count = 0
    file_paths = []
    for file in files:
        if file:
            files_count += 1
            filename = f"{str(new_patient_id)}" + f"{str(new_operation_type)[0]}" + f"{str(new_organ)[0]}" + \
                       f"{str(files_count)}" + ".mp4"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_paths.append(file_path)

    if files_count > 0:
        old_pass1 = old_operation.file_video_path1
        os.remove(path=old_pass1)
        db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
            {'file_video_path1': file_paths[0]})
        db.session.commit()
        files[0].save(file_paths[0])

        if old_operation.file_video_path2:
            old_pass2 = old_operation.file_video_path2
            os.remove(path=old_pass2)
            db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
                {'file_video_path2': None})
            db.session.commit()

        if files_count == 2:
            db.session.query(Operation).filter(Operation.operation_id == operation_id).update(
                {'file_video_path2': file_paths[1]})
            db.session.commit()
            files[1].save(file_paths[1])

    return jsonify({"message": "Запись об операции изменена"}), 201


# Удаление операции
@app.route('/delete_operation', methods=['POST'])
@token_required
def delete_operation(login, role_id, life_time):
    if role_id == '2' or role_id == '1':
        data = request.json
        operation_id = data['operation_id']
        operation = Operation.query.filter(Operation.operation_id == operation_id).first()
        if operation is None:
            return jsonify({"message": "Запись об операции не найдена"}), 404
        user_id = operation.user_id
        if role_id == '2' and User.query.filter(User.login == login).first().user_id != user_id:
            return jsonify({"message": "Запись об операции может быть удалена только её создателем или администратором"}), 403

        db.session.query(StagesOfOperation).filter(StagesOfOperation.operation_id == operation_id).delete()
        db.session.commit()
        os.remove(operation.file_video_path1)
        if operation.file_video_path2:
            os.remove(operation.file_video_path2)
        db.session.query(Favourite).filter(Favourite.operation_id == operation_id).delete()
        db.session.commit()
        db.session.query(Operation).filter(Operation.operation_id == operation_id).delete()
        db.session.commit()
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора или врача"}), 403
    return jsonify({"message": "Запись об операции успешно удалена"}), 201


# Передача видео
@app.route('/get_video1/<operation_id>', methods=['GET'])
def get_video1(operation_id):
    operation = Operation.query.filter(Operation.operation_id == operation_id).first()
    return send_file(operation.file_video_path1, as_attachment=False, mimetype='video/mp4')


@app.route('/get_video2/<operation_id>', methods=['GET'])
def get_video2(operation_id):
    operation = Operation.query.filter(Operation.operation_id == operation_id).first()
    return send_file(operation.file_video_path2, as_attachment=False, mimetype='video/mp4')


# Просмотр конкретной операции
@app.route('/get_operation', methods=['GET'])
@token_required
def get_operation(login, role_id, life_time):
    data = request.json
    operation_id = data['operation_id']
    operation = Operation.query.filter(Operation.operation_id == operation_id).first()
    if operation is None:
        return jsonify({"message": "Операция не найдена"}), 404

    # Этапы
    stages = db.session.query(StagesOfOperation).filter(StagesOfOperation.operation_id == operation_id).all()
    if stages:
        stages_of_operation = [
            {
                'stage_name': db.session.query(Stage).filter(Stage.stage_id == stage.stage_id).first().stage_name,
                'timing': stage.timing.isoformat(),
                'bloodloss': stage.bloodloss
            }
            for stage in stages
        ]
    else:
        stages_of_operation = 'None'

    # Сколько файлов
    if operation.file_video_path2 is None:
        files_count = 1
    else:
        files_count = 2

    return jsonify({
        "operation_id": f"{operation_id}",
        "user_id": f"{operation.user_id}",
        "patient_id": f"{operation.patient_id}",
        "operation_type": f"{operation.type}",
        "organ": f"{operation.organ}",
        "operation_date": f"{(operation.operation_date.isoformat()).replace('T', ' ')}",
        "medical_center": f"{operation.medical_center}",
        "description": f"{operation.description}",
        "stages": f"{stages_of_operation}",
        "files_count": f"{files_count}",

        # 🔴 НОВОЕ – пути к видеофайлам
        "file_video_path1": operation.file_video_path1,
        "file_video_path2": operation.file_video_path2
    }), 200


# Получение списка операций
@app.route('/get_operations', methods=['GET'])
@token_required
def get_operations(login, role_id, life_time):
    data = request.json
    page_number = int(data['page_number'])
    number_of_operations = db.session.query(Operation).count()
    max_number_of_pages = 1 if number_of_operations <= 20 else ((number_of_operations//20)+1)
    if page_number > max_number_of_pages:
        return jsonify({"message": "Страница не найдена"}), 404
    operations = db.session.query(Operation).offset((page_number - 1) * 20).limit(20).all()
    ten_operations = [{'operation_id': operation.operation_id, 'user_id': operation.user_id,
                       'patient_id': operation.patient_id, 'operation_type': f"{operation.type}",
                       'organ': operation.organ,
                       'operation_date': (operation.operation_date.isoformat()).replace("T", " "),
                       'medical_center': operation.medical_center}
                      for operation in operations]
    return jsonify({"max_number_of_pages": f"{max_number_of_pages}", "operations": f"{ten_operations}"})


# Поиск операции
@app.route('/search_operation', methods=['GET'])
@token_required
def search_operation(login, role_id, life_time):
    data = request.json
    search_string = data['search_string']
    if search_string == '':
        return get_operations()
    page_number = int(data['page_number'])
    operations = db.session.query(Operation).join(Type).filter(or_(cast(Operation.operation_id, String).ilike(f'%{search_string}%'),
                                                    cast(Operation.operation_date, String).ilike(f'%{search_string}%'),
                                                    cast(Operation.user_id, String).ilike(f'%{search_string}%'),
                                                    cast(Operation.patient_id, String).ilike(f'%{search_string}%'),
                                                    Type.type_name.ilike(f'%{search_string}%'),
                                                    Operation.organ.ilike(f'%{search_string}%'),
                                                    Operation.medical_center.ilike(f'%{search_string}%'))
                                                    )
    number_of_operations = operations.count()
    max_number_of_pages = 1 if number_of_operations <= 20 else ((number_of_operations//20)+1)
    if page_number > max_number_of_pages:
        return jsonify({"message": "Страница не найдена"}), 404
    operations = operations.offset((page_number - 1) * 20).limit(20).all()
    ten_operations = [{'operation_id': operation.operation_id, 'user_id': operation.user_id,
                       'patient_id': operation.patient_id, 'operation_type': f"{operation.type}",
                       'organ': operation.organ,
                       'operation_date': (operation.operation_date.isoformat()).replace("T", " "),
                       'medical_center': operation.medical_center}
                      for operation in operations]
    return jsonify({"max_number_of_pages": f"{max_number_of_pages}", "operations": f"{ten_operations}"})


# Скачивание данных
@app.route('/upload', methods=['GET'])
@token_required
def upload(login, role_id, life_time):
    if role_id == '2' or role_id == '1' or role_id == '3':
        data = request.json
        operation_id = data['operation_id']
        operation = Operation.query.filter(Operation.operation_id == operation_id).first()
        if operation is None:
            return jsonify({"message": "Запись об операции не найдена"}), 404
        zip_filename = 'videos.zip'
        if os.path.isfile(zip_filename):
            os.remove(zip_filename)
        if operation.file_video_path2:
            file_path1 = operation.file_video_path1
            file_name1 = file_path1.split('\\')[-1]
            file_path2 = operation.file_video_path2
            file_name2 = file_path2.split('\\')[-1]
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                zipf.write(file_path1, os.path.basename(file_name1))
                zipf.write(file_path2, os.path.basename(file_name2))
        else:
            file_path1 = operation.file_video_path1
            file_name1 = file_path1.split('\\')[-1]
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                zipf.write(file_path1, os.path.basename(file_name1))
        response = send_file(zip_filename, as_attachment=True)
        response.headers['X-Message'] = file_name1.split(".")[0][:-1].encode('utf-8').decode('latin-1')
        return response, 200
    else:
        return jsonify({"message": "Пользователь должен иметь права администратора, врача или разработчика"}), 403


# Сохранение в избранное
@app.route('/save_to_favourites', methods=['POST'])
@token_required
def save_to_favourites(login, role_id, life_time):
    data = request.json
    operation_id = data['operation_id']
    operation = Operation.query.filter(Operation.operation_id == operation_id).first()
    if operation is None:
        return jsonify({"message": "Запись об операции не найдена"}), 404
    user_id = db.session.query(User).filter(User.login == login).first().user_id
    if db.session.query(Favourite).filter(and_(Favourite.user_id == user_id, Favourite.operation_id == operation_id)).first():
        return jsonify({"message": "Запись уже в избранном"}), 201

    new_favourite = Favourite(user_id=user_id, operation_id=operation_id, saving_date=str(datetime.datetime.now()).split('.')[0])
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify({"message": "Запись добавлена в избранное"}), 201


# Просмотр избранного
@app.route('/get_favourites', methods=['GET'])
@token_required
def get_favourites(login, role_id, life_time):
    data = request.json
    user_id = db.session.query(User).filter(User.login == login).first().user_id
    page_number = int(data['page_number'])
    number_of_operations = db.session.query(Operation).join(Favourite).filter(Favourite.user_id == user_id).count()
    max_number_of_pages = 1 if number_of_operations <= 20 else ((number_of_operations//20)+1)
    if page_number > max_number_of_pages:
        return jsonify({"message": "Страница не найдена"}), 404
    favourite_operations = db.session.query(Operation).join(Favourite).filter(Favourite.user_id == user_id).offset((page_number - 1) * 20).limit(20).all()
    ten_favourite_operations = [{'operation_id': favourite_operation.operation_id,
                                 'user_id': favourite_operation.user_id,
                                 'patient_id': favourite_operation.patient_id,
                                 'operation_type': f"{favourite_operation.type}",
                                 'organ': favourite_operation.organ,
                                 'operation_date': (favourite_operation.operation_date.isoformat()).replace("T", " "),
                                 'medical_center': favourite_operation.medical_center,
                                 'favourite_datetime': (db.session.query(Favourite).filter(and_(Favourite.user_id ==
                                                                                                user_id,
                                                                                                Favourite.operation_id
                                                                                                == favourite_operation.operation_id)).first().saving_date)}
                                for favourite_operation in favourite_operations]
    return jsonify({"max_number_of_pages": f"{max_number_of_pages}", "operations": f"{ten_favourite_operations}"})


# Поиск избранного
@app.route('/search_favourite', methods=['GET'])
@token_required
def search_favourite(login, role_id, life_time):
    data = request.json
    search_string = data['search_string']
    if search_string == '':
        return get_favourites()
    page_number = int(data['page_number'])
    user_id = db.session.query(User).filter(User.login == login).first().user_id
    operations = db.session.query(Operation).join(Favourite).filter(Favourite.user_id == user_id).join(Type).filter(
        or_(cast(Operation.operation_id, String).ilike(f'%{search_string}%'),
            cast(Operation.operation_date, String).ilike(f'%{search_string}%'),
            cast(Operation.user_id, String).ilike(f'%{search_string}%'),
            cast(Operation.patient_id, String).ilike(f'%{search_string}%'),
            Type.type_name.ilike(f'%{search_string}%'),
            Operation.organ.ilike(f'%{search_string}%'),
            Operation.medical_center.ilike(f'%{search_string}%'),
            cast(Favourite.saving_date, String).ilike(f'%{search_string}%'))
        )

    number_of_operations = operations.count()
    max_number_of_pages = 1 if number_of_operations <= 20 else ((number_of_operations // 20) + 1)
    if page_number > max_number_of_pages:
        return jsonify({"message": "Страница не найдена"}), 404
    operations = operations.offset((page_number - 1) * 20).limit(20).all()
    ten_operations = [{'operation_id': favourite_operation.operation_id,
                       'user_id': favourite_operation.user_id,
                       'patient_id': favourite_operation.patient_id,
                       'operation_type': f"{favourite_operation.type}",
                       'organ': favourite_operation.organ,
                       'operation_date': (favourite_operation.operation_date.isoformat()).replace("T", " "),
                       'medical_center': favourite_operation.medical_center,
                       'favourite_datetime': (db.session.query(Favourite).filter(and_(Favourite.user_id ==
                                                                                                user_id,
                                                                                                Favourite.operation_id
                                                                                                == favourite_operation.operation_id)).first().saving_date)}
                      for favourite_operation in operations]
    return jsonify({"max_number_of_pages": f"{max_number_of_pages}", "operations": f"{ten_operations}"})


# Удаление из избранного
@app.route('/delete_favourite', methods=['POST'])
@token_required
def delete_favourite(login, role_id, life_time):
    data = request.json
    operation_id = data['operation_id']
    user_id = db.session.query(User).filter(User.login == login).first().user_id
    if db.session.query(Favourite).filter(and_(Favourite.user_id == user_id, Favourite.operation_id == operation_id)).first() is None:
        return jsonify({"message": "Запись в избранном не найдена"}), 404
    if Operation.query.filter(Operation.operation_id == operation_id).first() is None:
        return jsonify({"message": "Запись об операции не найдена"}), 404
    db.session.query(Favourite).filter(and_(Favourite.user_id == user_id, Favourite.operation_id == operation_id)).delete()
    db.session.commit()
    return jsonify({"message": "Запись об операции успешно удалена из избранного"}), 200


# Получение типов и этапов
@app.route('/get_types_and_stages', methods=['GET'])
@token_required
def get_types_and_stages(login, role_id, life_time):
    types_and_stages = {}

    optypes = db.session.query(Type).with_entities(Type.type_name, Type.type_id).all()

    for optype in optypes:
        opstages = db.session.query(Stage).filter(Stage.type_id == optype[1]).with_entities(Stage.stage_name).all()
        types_and_stages[optype[0]] = [opstage[0] for opstage in opstages]
    return jsonify(types_and_stages)


# # Создание типов и этапов
# @app.route('/create_types_and_stages', methods=['PUT'])
# @token_required
# def create_types_and_stages(login, role_id, life_time):
#     if role_id == '1':
#         type_name = request.form.get('type_name').capitalize()
#         stages = eval(request.form.get('type_name'))
#         new_type = Type(type_name=type_name)
#         db.session.add(new_type)
#         db.session.commit()
#         type_id = db.session.query(Type).filter(Type.type_name == type_name).first().type_id
#         for i in range(len(stages)):
#             new_stage = Stage(type_id=type_id, type_name=stages[i])
#             db.session.add(new_stage)
#             db.session.commit()
#     else:
#         return jsonify({"message": "Пользователь должен иметь права администратора"}), 403
#     return jsonify({"message": "Новый тип операции создан"}), 201


if __name__ == '__main__':
    with app.app_context():
        try:
    db.create_all()
except Exception as e:
    print('DB connection failed. Check Postgres is running and DATABASE_URL/SQLALCHEMY_DATABASE_URI is correct.')
    print('Error:', e)
    raise
    app.run(host='0.0.0.0', port=5000)
