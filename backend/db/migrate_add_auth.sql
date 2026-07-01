-- Migration : ajout de l'authentification
-- A exécuter UNE SEULE FOIS sur une base déjà existante
-- docker compose exec postgres psql -U postgres -d ai_precision_teaching -f /dev/stdin < backend/db/migrate_add_auth.sql

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
    CREATE TYPE user_role AS ENUM ('teacher', 'student');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS app_user (
    user_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login                TEXT NOT NULL UNIQUE,
    password_hash        TEXT NOT NULL,
    role                 user_role NOT NULL DEFAULT 'student',
    student_id           BIGINT REFERENCES student(student_id),
    must_change_password BOOLEAN NOT NULL DEFAULT false,
    is_active            BOOLEAN NOT NULL DEFAULT true,
    created_at           TIMESTAMPTZ DEFAULT now(),
    last_login_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_app_user_login   ON app_user(login);
CREATE INDEX IF NOT EXISTS idx_app_user_student ON app_user(student_id);
