#!/usr/bin/env bash
# Provision the isolated Lab staging site. Usage: setup.sh <plugin zip> <lab page content file>
# Generates DB and admin secrets into .env / admin-password (mode 600); prints neither.
set -euo pipefail
cd "$(dirname "$0")"
umask 077
PLUGIN_ZIP="$1"; PAGE_HTML="$2"; PORT="${STAGING_PORT:-18190}"
if [ ! -f .env ]; then
  printf 'DB_PASSWORD=%s\nDB_ROOT_PASSWORD=%s\nSTAGING_PORT=%s\n' "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" "$PORT" > .env
  openssl rand -hex 24 > admin-password
fi
mkdir -p artifacts && cp "$PLUGIN_ZIP" artifacts/lab.zip && cp "$PAGE_HTML" artifacts/lab-page.html
chmod 755 artifacts && chmod 644 artifacts/*
docker compose up -d db wordpress
for i in $(seq 1 60); do docker compose exec -T db mysqladmin ping -h 127.0.0.1 --silent >/dev/null 2>&1 && break; sleep 2; done
for i in $(seq 1 30); do curl -fsS -o /dev/null "http://127.0.0.1:$PORT/wp-includes/images/blank.gif" && break; sleep 2; done
wp() { docker compose run --rm -T cli wp "$@"; }
if ! wp core is-installed >/dev/null 2>&1; then
  wp core install --url="http://127.0.0.1:$PORT" --title="SC Lab staging (FIG-02A)" --admin_user=staging-admin \
    --admin_password="$(cat admin-password)" --admin_email=staging@localhost.invalid --skip-email
fi
wp core version
wp option update blog_public 0
wp rewrite structure '/%postname%/' --hard
wp theme install astra --version=4.14.2 --activate
wp plugin install /artifacts/lab.zip --force --activate
if ! wp post list --post_type=page --name=lab --field=ID | grep -q .; then
  wp post create /artifacts/lab-page.html --post_type=page --post_status=publish --post_title=Lab --post_name=lab
fi
wp option update sc_lab_fig02a_plotly_preview_enabled 1
wp plugin list --fields=name,status,version
