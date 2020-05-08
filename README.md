# KviDet - Bakalářská práce (Kvita Detection)

## Instalace

### Požadavky pro instalaci
* bash
* git
* python 3.8+
* python-pip
* python-venv

```bash
# stažení repozitáře
git clone --recurse-submodules https://github.com/kvitajin/KviDet.git
cd kvitajin-bak

# instalace závislostí
bash setup.sh
```

## Práce s programem

Je potřeba upravit si soubor config/config.py dle vašeho videa. Zejména je potřeba upravit proměnnou BOUNDING_VECTORS.

Pro odhad souřadnic těchto vektorů vám pomůže html/js aplikace ve složce config_helper_app

```bash
source .venv/bin/activate
python3 -m kvidet cesta/k/videosouboru
```
