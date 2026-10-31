# Datasets de otros relojes (descarga manual)

Aquí se guardan los datasets **que no son Fitbit**, para probar si el modelo generaliza a otras marcas.
Los archivos de datos NO se suben a git (ver `.gitignore`); lo que sí se versiona es la ficha `FUENTE.md` de cada
carpeta, para que se pueda repetir la descarga en otra PC.

## Dónde dejar cada dataset

| Carpeta | Qué va aquí |
|---|---|
| `xiaomi/` | Mi Band / Smart Band |
| `amazfit/` | Amazfit (Zepp) |
| `samsung/` | Galaxy Watch |
| `garmin/` | Garmin |
| `apple_watch/` | Apple Watch (fase posterior, pero útil para validar contra polisomnografía) |
| `huawei/` | Huawei |
| `multi_dispositivo/` | Estudios donde la misma persona usa 2 o más dispositivos a la vez, o reloj contra polisomnografía/actigrafía, sin importar la marca |
| `otros/` | Cualquier otro que no encaje |

**Un dataset = una subcarpeta con su nombre**, por ejemplo `garmin/nombre_del_dataset/`, con los archivos originales
sin modificar y la `FUENTE.md` llenada. Si un dataset trae varias marcas, ponlo en `multi_dispositivo/`.

## Antes de usar algo
Verifica en la página del dataset la licencia, el número de personas y las variables. Las listas que devuelve un buscador
o un chat de IA pueden traer datos incorrectos: no tomes nada como cierto hasta abrir la página.

## Datasets encontrados (páginas verificadas)

| Carpeta | Dataset | Enlace |
|---|---|---|
| `xiaomi/group_health_sleep_screen/` | Group Health (Sleep and Screen Time), Mi Band, Zenodo | https://zenodo.org/records/15171250 |
| `garmin/anonymized_wearable_greece/` | Anonymized Wearable Sensor Health and Activity, Garmin Vivosmart 5, Zenodo | https://zenodo.org/records/17967723 |
| `apple_watch/walch_sleep_accel/` | Walch: Apple Watch contra polisomnografía, PhysioNet | https://physionet.org/content/sleep-accel/1.0.0/ |
| `apple_watch/bidsleep_song/` | BIDSleep: Apple Watch contra EEG, 47 personas, 28 GB, PhysioNet | https://physionet.org/content/bidsleep-dataset/1.0.0/ |
| `otros/mmash_polar_actigraph/` | MMASH: Polar H7 + ActiGraph con PSQI, 22 hombres, PhysioNet | https://physionet.org/content/mmash/1.0.0/ |
| `otros/globem_fitbit_multiyear/` | GLOBEM: Fitbit + celular, 497 estudiantes, 4 años, sin PSQI, PhysioNet (credencializado) | https://physionet.org/content/globem/1.1/ |

Cada subcarpeta tiene su `FUENTE.md` con lo verificado y lo que falta revisar.
