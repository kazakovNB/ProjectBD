# seed_defaults.py
from __future__ import annotations

from datetime import datetime, date
import hashlib

from sqlalchemy import func

# Импортируем модели из main.py
from main import db, Role, Type, Stage, User


DEFAULT_ROLES = {
    1: "Администратор",
    2: "Врач",
    3: "Разработчик",
    4: "Студент",
}

# Твой список этапов (убрал повтор "Мобилизация сигмовидной кишки", чтобы не было дублей по имени)
PROSTATECTOMY_STAGES = [
    "Мобилизация сигмовидной кишки",
    "Мобилизация мочевого пузыря",
    "Подвздошно-запирательная лимфаденэктомия справа",
    "Подвздошно-запирательная лимфаденэктомия слева",
    "Вскрытие тазовой фасции справа",
    "Вскрытие тазовой фасции слева",
    "Мобилизация шейки мочевого пузыря",
    "Мобилизация задней стенки мочевого пузыря (включая выделение семенных пузырьков)",
    "Мобилизация боковой стенки, пересечение правого сосудисто-нервного пучка",
    "Мобилизация боковой стенки, пересечение левого сосудисто-нервного пучка",
    "Прошивание венозного комплекса",
    "Мобилизация и пересечение дистального отдела уретры",
    "Контейнеризация простаты",
]


def _sha512_hex(password: str) -> str:
    return hashlib.sha512(password.encode("utf-8")).hexdigest()


def seed_defaults() -> None:
    """
    Идемпотентный сид:
    - чинит/создаёт роли
    - добавляет тип "Простатэктомия"
    - добавляет этапы к этому типу
    - создаёт admin/admin123 если его нет
    """

    # --- Roles ---
    for rid, rname in DEFAULT_ROLES.items():
        role = db.session.query(Role).filter(Role.role_id == rid).first()
        if role is None:
            # role_id = Identity, но обычно BY DEFAULT, поэтому явная вставка допустима
            db.session.add(Role(role_id=rid, role_name=rname))
        else:
            if role.role_name != rname:
                role.role_name = rname
    db.session.commit()

    # --- Type: Простатэктомия ---
    type_obj = db.session.query(Type).filter(Type.type_name == "Простатэктомия").first()
    if type_obj is None:
        max_type_id = db.session.query(func.max(Type.type_id)).scalar()
        next_type_id = (max_type_id or 0) + 1
        type_obj = Type(type_id=next_type_id, type_name="Простатэктомия")
        db.session.add(type_obj)
        db.session.commit()

    type_id = type_obj.type_id

    # --- Stages for this type ---
    existing = db.session.query(Stage.stage_name).filter(Stage.type_id == type_id).all()
    existing_names = {x[0] for x in existing}

    max_stage_id = db.session.query(func.max(Stage.stage_id)).scalar() or 0
    next_stage_id = max_stage_id + 1

    for stage_name in PROSTATECTOMY_STAGES:
        if stage_name in existing_names:
            continue
        db.session.add(Stage(type_id=type_id, stage_id=next_stage_id, stage_name=stage_name))
        next_stage_id += 1

    db.session.commit()

    # --- Default admin user ---
    admin_login = "admin"
    admin_pass = "admin123"
    admin = db.session.query(User).filter(User.login == admin_login).first()
    if admin is None:
        admin_user = User(
            login=admin_login,
            role_id=1,
            password=_sha512_hex(admin_pass),
            active=True,
            name="Admin",
            surname="Admin",
            patronymic="Admin",
            birthday=date(1970, 1, 1),
            registration=datetime.now(),
            job_title=None,
            organization=None,
            department=None,
            university=None,
            student_group=None,
        )
        db.session.add(admin_user)
        db.session.commit()
