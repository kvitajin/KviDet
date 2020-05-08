#!/usr/bin/env bash

# ukončit skript při první nezachycené chybě
set -e

# normalizace počáteční složky
cd "$(dirname $0)"

echo "Testuji verze nástrojů"
echo "--------------------------"

# test instalace pythonu
command -v python3 >/dev/null 2>&1 || {
  echo >&2 "Python interpeter nenalezen!"
  exit 1
}

# test instalace pip
python3 -m pip -V >/dev/null 2>&1 || {
  echo >&2 "Balíčkový manažer pip nebyl nalezen!"
  exit 1
}

# test verze pythonu
if [[ ! "$(python3 -V)" =~ Python\ 3\.8 ]]; then
  echo "Zdá se, že používáte $(python3 -V)"
  echo "Tento projekt byl ale testován jen na Python 3.8.*."
  read -p "Přejete si přesto pokračovat? [y/N] " -r

  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi

  echo "--------------------------"
fi

# příprava virtuálního prostředí
if [[ -z "$VIRTUAL_ENV" ]]; then
  # vytvoření virtuálního prostředí pro instalaci knihoven
  echo "Vytvářím virtuální prostředí ve složce .venv/"
  echo "--------------------------"
  python3 -m venv --copies .venv

  # aktivace virtuálního prostředí
  echo "Aktivuji virtuální prostředí..."
  echo "--------------------------"
  source .venv/bin/activate
fi

# test, zda jsme skutečně ve virtuálním prostředí
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "Nepovedlo se nastavit virtuální prostředí python venv"
  exit 1
fi

# stažení vah k YOLOv3
if [ ! -f weights/yolov3.weights ]; then
  echo "Nebyly nalezeny váhy pro YOLOv3"
  echo "Stahuji váhy"
  echo "--------------------------"
  wget https://pjreddie.com/media/files/yolov3.weights -O weights/yolov3.weights && echo "Váhy úspěšně staženy!"
fi

# načtení submodulů
echo "Načítám submoduly"
echo "--------------------------"
git submodule update --init --recursive

# patchnutí chybného importu v závislosti yolo
echo "Patchuji yolo/models.py"
sed -i 's/from utils/from .utils/' detector/yolo/models.py

# patchnutí žádosti o interaktivní tkinter v závislosti sort
echo "Patchuji sort/sort.py"
sed -i "s|matplotlib.use('TkAgg')|matplotlib.use('agg')|" tracker/sort/sort.py

# instalace knihoven
echo "Instaluji knihovny"
echo "--------------------------"
python3 -m pip install -r requirements.txt
