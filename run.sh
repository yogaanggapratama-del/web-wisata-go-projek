#!/usr/bin/env bash
# Menjalankan GoWisata di Mac/Linux
cd "$(dirname "$0")"

USE_VENV=1

if [ ! -d "venv" ]; then
  echo ">> Membuat virtual environment..."
  if ! python3 -m venv venv 2>/tmp/gowisata_venv_err.log; then
    echo ">> Tidak bisa membuat virtual environment, akan install dependency langsung ke Python sistem."
    USE_VENV=0
  fi
fi

if [ "$USE_VENV" = "1" ] && [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  echo ">> Menginstal dependencies (virtual environment)..."
  pip install --quiet -r requirements.txt
else
  echo ">> Menginstal dependencies (Python sistem)..."
  pip3 install --quiet -r requirements.txt --break-system-packages 2>/dev/null \
    || pip3 install --quiet -r requirements.txt --user \
    || pip3 install --quiet -r requirements.txt
fi

echo ""
echo "======================================================"
echo "  GoWisata siap berjalan di: http://127.0.0.1:5000"
echo "  Tekan CTRL+C untuk menghentikan server."
echo "======================================================"
echo ""

python3 app.py
