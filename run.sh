#!/usr/bin/env bash
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"
echo "🧹  Limpiando __pycache__ ..."
find . -depth -type d -name "__pycache__" -exec rm -rf {} +

if [[ ! -d "venv" ]]; then
  echo "🐍  Creando entorno virtual..."
  python -m venv venv
fi

source venv/bin/activate
echo "📦  Instalando dependencias (requests, python‑dotenv)..."
pip install requests python-dotenv

TODAY=$(date +%F)
python -m scripts.fetch_and_exports departures BCN 2025-05-04 --limit 8

echo "🌐  Sirviendo en http://localhost:8000 (CTRL‑C para salir)"
python -m http.server 8000