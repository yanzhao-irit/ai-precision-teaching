"""
Gestion des comptes utilisateurs — script CLI
Usage (depuis le répertoire backend, venv activé) :

  # Créer un enseignant
  python scripts/manage_users.py add-teacher --login prof_wang --password MonMotDePasse

  # Créer un élève manuellement (hors import classe)
  python scripts/manage_users.py add-student --login 20240001 --password 20240001

  # Lister tous les comptes
  python scripts/manage_users.py list

  # Réinitialiser le mot de passe d'un compte
  python scripts/manage_users.py reset-password --login prof_wang --password NouveauMDP

  # Désactiver un compte
  python scripts/manage_users.py deactivate --login prof_wang
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent (backend/) au path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATA_SOURCE", "postgres")

from sqlalchemy import text
from app.core.postgres_client import engine
from app.core.auth import hash_password


async def _exec(sql: str, params: dict = {}):
    async with engine.begin() as conn:
        return await conn.execute(text(sql), params)


async def add_teacher(login: str, password: str):
    await _exec(
        """
        INSERT INTO app_user (login, password_hash, role, must_change_password)
        VALUES (:login, :pw, 'teacher', false)
        ON CONFLICT (login) DO NOTHING
        """,
        {"login": login, "pw": hash_password(password)},
    )
    print(f"✅ Enseignant '{login}' créé.")


async def add_student(login: str, password: str):
    await _exec(
        """
        INSERT INTO app_user (login, password_hash, role, must_change_password)
        VALUES (:login, :pw, 'student', true)
        ON CONFLICT (login) DO NOTHING
        """,
        {"login": login, "pw": hash_password(password)},
    )
    print(f"✅ Élève '{login}' créé (devra changer son mot de passe).")


async def list_users():
    result = await _exec(
        "SELECT user_id, login, role, is_active, must_change_password, last_login_at FROM app_user ORDER BY role, login"
    )
    rows = result.mappings().all()
    if not rows:
        print("Aucun compte trouvé.")
        return
    print(f"\n{'ID':<6} {'Login':<20} {'Rôle':<10} {'Actif':<7} {'MDP init':<10} {'Dernière connexion'}")
    print("─" * 75)
    for r in rows:
        last = str(r["last_login_at"])[:19] if r["last_login_at"] else "jamais"
        mdp = "oui" if r["must_change_password"] else "—"
        actif = "✓" if r["is_active"] else "✗"
        print(f"{r['user_id']:<6} {r['login']:<20} {r['role']:<10} {actif:<7} {mdp:<10} {last}")
    print()


async def reset_password(login: str, password: str):
    res = await _exec(
        "UPDATE app_user SET password_hash = :pw, must_change_password = false WHERE login = :login",
        {"login": login, "pw": hash_password(password)},
    )
    print(f"✅ Mot de passe réinitialisé pour '{login}'.")


async def deactivate(login: str):
    await _exec(
        "UPDATE app_user SET is_active = false WHERE login = :login",
        {"login": login},
    )
    print(f"⛔ Compte '{login}' désactivé.")


def main():
    parser = argparse.ArgumentParser(description="Gestion des comptes AI 精准教学")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-teacher", help="Créer un compte enseignant")
    p.add_argument("--login", required=True)
    p.add_argument("--password", required=True)

    p = sub.add_parser("add-student", help="Créer un compte élève manuellement")
    p.add_argument("--login", required=True)
    p.add_argument("--password", required=True)

    sub.add_parser("list", help="Lister tous les comptes")

    p = sub.add_parser("reset-password", help="Réinitialiser un mot de passe")
    p.add_argument("--login", required=True)
    p.add_argument("--password", required=True)

    p = sub.add_parser("deactivate", help="Désactiver un compte")
    p.add_argument("--login", required=True)

    args = parser.parse_args()

    if args.cmd == "add-teacher":
        asyncio.run(add_teacher(args.login, args.password))
    elif args.cmd == "add-student":
        asyncio.run(add_student(args.login, args.password))
    elif args.cmd == "list":
        asyncio.run(list_users())
    elif args.cmd == "reset-password":
        asyncio.run(reset_password(args.login, args.password))
    elif args.cmd == "deactivate":
        asyncio.run(deactivate(args.login))


if __name__ == "__main__":
    main()
