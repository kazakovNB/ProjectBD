import os
import sys
import secrets
import json
import socket
import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2
from psycopg2 import sql

from pathlib import Path


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


def detect_local_ip(fallback="192.168.8.6") -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
        finally:
            s.close()
    except Exception:
        pass
    return fallback


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
            sql.SQL("CREATE DATABASE {} OWNER {}; ").format(
                sql.Identifier(dbname),
                sql.Identifier(appuser)
            )
        )

    cur.close()
    conn.close()


def write_client_config(server_url: str) -> None:
    client_cfg = {"base_url": server_url}
    # 1) next to db setup exe/script
    try:
        cfg_path = os.path.join(app_root(), "config.json")
        with open(cfg_path, "w", encoding="utf-8") as cf:
            json.dump(client_cfg, cf, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 2) ProgramData common config
    try:
        common_cfg_dir = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "VEO")
        os.makedirs(common_cfg_dir, exist_ok=True)
        common_cfg_path = os.path.join(common_cfg_dir, "config.json")
        with open(common_cfg_path, "w", encoding="utf-8") as cf:
            json.dump(client_cfg, cf, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 3) attempt to write to ../Client if present
    try:
        client_folder_candidate = os.path.normpath(os.path.join(app_root(), "..", "Client"))
        if os.path.isdir(client_folder_candidate):
            client_cfg_path = os.path.join(client_folder_candidate, "config.json")
            with open(client_cfg_path, "w", encoding="utf-8") as cf:
                json.dump(client_cfg, cf, ensure_ascii=False, indent=2)
    except Exception:
        pass


def main():
    root = tk.Tk()
    root.title("VEO Database Setup")
    root.geometry("560x460")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=16)
    frm.pack(fill="both", expand=True)

    def add_row(r, label, default="", show=None):
        ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=6)
        var = tk.StringVar(value=default)
        ent = ttk.Entry(frm, textvariable=var, width=48, show=show)
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

    # Server URL field with auto-detection and fallback
    detected_ip = detect_local_ip()
    default_server_url = f"http://{detected_ip}:5000"
    server_url = add_row(11, "Server URL for clients", default_server_url)

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

            # write client config so clients can auto-detect server url
            try:
                server_value = server_url.get().strip()
                if server_value:
                    write_client_config(server_value)
            except Exception:
                pass

            messagebox.showinfo(
                "Done",
                "Database is ready.\n\nNext step:\n1) Start 'VEO Server'\n2) Start 'VEO Client'",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn = ttk.Button(frm, text="Create / Update database and write .env", command=on_create)
    btn.grid(row=12, column=0, columnspan=2, pady=18, sticky="ew")

    note = ttk.Label(
        frm,
        text="Tip: if PostgreSQL is installed locally, keep host=127.0.0.1 and port=5432.",
        wraplength=520,
        foreground="#555555"
    )
    note.grid(row=13, column=0, columnspan=2, sticky="w")

    root.mainloop()


if __name__ == "__main__":
    main()
