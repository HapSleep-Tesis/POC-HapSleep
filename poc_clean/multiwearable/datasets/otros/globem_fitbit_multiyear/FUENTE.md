# GLOBEM (Fitbit + smartphone, multi-año)

- **Enlace:** https://physionet.org/content/globem/1.1/
- **Tipo:** Fitbit real, **sin PSQI** y **sin pulso, HRV, SpO2 ni respiración**. Misma marca que LifeSnaps: no suma como marca nueva al modelo multi-wearable.
- **Personas / duración (verificado al abrir los archivos):** 705 persona-años = 4 cohortes de primavera (2018: 155, 2019: 218, 2020: 137, 2021: 195), ~10 semanas cada una. PhysioNet dice 497 participantes únicos, pero **los pid no se repiten entre años**, así que una misma persona puede aparecer con dos códigos y no se puede comprobar. Población: estudiantes universitarios. El año 3 (2020) es la primavera de la pandemia.
- **Carpetas por año (`INS-W_1` a `INS-W_4`):** `FeatureData` (sleep, steps, rapids, screen, call, location, bluetooth, wifi), `SurveyData` (pre, post, dep_weekly, dep_endterm, ema), `ParticipantsInfoData` (platform).
- **Sueño del Fitbit (`FeatureData/sleep.csv`, 918 columnas):** por día y por tramo (allday, morning, night, 7dhist, 14dhist…): minutos dormidos, despiertos, en cama, latencia, eficiencia, hora de acostarse y de despertar. **La latencia vale 0 en el 98.6 % de las noches** (igual que en LifeSnaps). Hay 411 noches con 0 minutos dormidos (registros vacíos).
- **Pasos (`steps.csv`):** pasos y minutos sedentarios/activos. **Sedentarios + activos = 1440 exactamente** (sedentario = 1440 − activo, incluye dormir y el tiempo sin reloj); correlación con los pasos entre personas −0.92.
- **Encuestas (verificado):** UCLA, SocialFit, SSS, ERQ, BRS, CHIPS, **PSS-10**, **STAI-S** (solo año 1), MAAS, **CES-D**, BFI-10 (la mayoría al inicio `pre.csv` y al final `post.csv`); **BDI-II** solo al final (`post.csv`, `dep_endterm.csv`) y en versión semanal (`dep_weekly.csv`); afecto negativo diario (`ema.csv`). La ficha de PhysioNet menciona PHQ-4 semanal. **Ningún cuestionario de calidad de sueño.** CES-D y BDI-II incluyen ítems de sueño y cansancio.
- **Licencia y descarga:** PhysioNet Credentialed Health Data License 1.5.0 (cuenta credencializada + CITI + acuerdo de uso). Peso en disco: ~3 GB.
- **Fecha de descarga:** octubre de 2026 (carpeta `globem-dataset-multi-year-datasets-for-longitudinal-human-behavior-modeling-generalization-1.1`).

## Para qué sirvió (PoC en `poc_clean/POC_GLOBEM/`)

- **No reemplaza el proxy ni al PSQI.** Sigue haciendo falta el PSQI real (Capa A, n≥50).
- Respalda con ~650 persona-años el supuesto de que el resumen por persona es estable (noche a noche ≈ 0, pares/impares 0.84–0.98).
- La **regularidad** (variación de la duración del sueño y del horario de acostarse) se relaciona con depresión, ansiedad y estrés de forma consistente en las 4 cohortes; el **sedentarismo** no se relaciona con nada y es redundante con los pasos.
- Mostró que con ~50 personas un Random Forest no se distingue del azar si la señal es débil (ver el notebook).

## Ojo

- La etiqueta (estrés, ansiedad, depresión) no es calidad de sueño: no usar estos resultados como desempeño de HapSleep.
- Para uso en el paper: citar el dataset y su paper original (la ficha de PhysioNet trae la cita) y respetar los términos del acuerdo de uso: **no redistribuir los datos**.
