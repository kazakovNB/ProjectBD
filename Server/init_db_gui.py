import os
import sys
import secrets
import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2
from psycopg2 import sql

def app_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def write_env(path: str, values: dict) -> None:
    lines = []
    for k, v in values.items():
        if v is None:
            continue
        lines.append(f"{k}={v}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def create_role_and_db(host, port, superuser, superpass, dbname, appuser, apppass):
    conn = psycopg2.connect(
        host=host, port=port, user=superuser, password=superpass, dbname="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Create role if missing
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s;", (appuser,))
    if cur.fetchone() is None:
        cur.execute(
            sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s;").format(sql.Identifier(appuser)),
            (apppass,)
        )

    # Create database if missing
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (dbname,))
    if cur.fetchone() is None:
        cur.execute(
            sql.SQL("CREATE DATABASE {} OWNER {};").format(
                sql.Identifier(dbname),
                sql.Identifier(appuser)
            )
        )

    cur.close()
    conn.close()

def main():
    root = tk.Tk()
    root.title("VEO Database Setup")
    root.geometry("520x420")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill="both", expand=True)

    def add_row(r, label, default="", show=None):
        ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=6)
        var = tk.StringVar(value=default)
        ent = ttk.Entry(frm, textvariable=var, width=38, show=show)
        ent.grid(row=r, column=1, sticky="w", pady=6)
        return var

    host = add_row(0, "PostgreSQL host", "127.0.0.1")
    port = add_row(1, "PostgreSQL port", "5432")
    superuser = add_row(2, "Admin user (Postgres)", "postgres")
    superpass = add_row(3, "Admin password", "", show="*")

    ttk.Separator(frm).grid(row=4, column=0, columnspan=2, sticky="ew", pady=12)

    dbname = add_row(5, "Database name", "veomodern")
    appuser = add_row(6, "App DB user", "veo_app")
    apppass = add_row(7, "App DB password", secrets.token_urlsafe(16), show="*")

    ttk.Separator(frm).grid(row=8, column=0, columnspan=2, sticky="ew", pady=12)

    max_size = add_row(9, "Max upload size (bytes)", "26843545600")  # 25 GB
    upload_folder_default = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "VEO", "videos")
    upload_folder = add_row(10, "Video storage folder", upload_folder_default)

    def on_create():
        try:
            create_role_and_db(
                host.get().strip(),
                int(port.get().strip()),
                superuser.get().strip(),
                superpass.get(),
                dbname.get().strip(),
                appuser.get().strip(),
                apppass.get(),
            )

            env_values = {
                "DATABASE_URL": f"postgresql://{appuser.get().strip()}:{apppass.get()}@{host.get().strip()}:{port.get().strip()}/{dbname.get().strip()}",
                "JWT_SECRET_KEY": secrets.token_hex(32),
                "UPLOAD_FOLDER": upload_folder.get().strip(),
                "MAX_CONTENT_LENGTH": max_size.get().strip(),
            }
            env_path = os.path.join(app_root(), ".env")
            write_env(env_path, env_values)

            os.makedirs(upload_folder.get().strip(), exist_ok=True)

            messagebox.showinfo(
                "Done",
                "Database is ready.\n\nNext step:\n1) Start 'VEO Server'\n2) Start 'VEO Client'",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn = ttk.Button(frm, text="Create / Update database and write .env", command=on_create)
    btn.grid(row=11, column=0, columnspan=2, pady=18, sticky="ew")

    note = ttk.Label(
        frm,
        text="Tip: if PostgreSQL is installed locally, keep host=127.0.0.1 and port=5432.",
        wraplength=480,
        foreground="#555555"
    )
    note.grid(row=12, column=0, columnspan=2, sticky="w")

    root.mainloop()

if __name__ == "__main__":
    main()
