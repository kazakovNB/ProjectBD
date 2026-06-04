import os
import sys
import traceback
from sqlalchemy.exc import OperationalError

from main import app, db, seed_defaults


def _app_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    print("=== VEO Server starting ===")
    print("App root:", _app_root())
    print("ENV DATABASE_URL:", os.environ.get("DATABASE_URL"))
    print("ENV UPLOAD_FOLDER:", os.environ.get("UPLOAD_FOLDER"))
    print("SQLALCHEMY_DATABASE_URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    try:
        with app.app_context():
            db.create_all()
            seed_defaults()   # <-- ВОТ ЭТО ВАЖНО
    except OperationalError as e:
        print("\n[DB ERROR] Не удалось подключиться к PostgreSQL.")
        print("\nТекущий DATABASE_URL:", app.config.get("SQLALCHEMY_DATABASE_URI"))
        print("\nОшибка:", repr(e))
        return 1
    except Exception as e:
        print("\n[SERVER ERROR] Ошибка при инициализации:")
        print(repr(e))
        traceback.print_exc()
        return 1

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))

    print("\nRoutes:", app.url_map)
    print(f"\nServer will run on http://{host}:{port}")
    app.run(host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
