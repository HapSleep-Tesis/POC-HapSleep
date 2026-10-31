# Variables por plataforma / marca de reloj (investigación para un PoC multi-wearable)

**Estado:** investigación documentada el 2026-09-19. **No hay PoC corrido todavía.** Es el insumo para un
PoC aparte ("multi-wearable") que se hará después de cerrar poc1. Alcance actual: **solo Android**
(Apple queda para otra fase — pide más requisitos de desarrollador que aún no se tienen).

**Cómo se obtuvo:** páginas oficiales de Google, Android y Samsung, más fuentes secundarias donde la oficial
no estaba disponible. Las páginas se leyeron con un resumidor automático, así que **cada dato clave debe
confirmarse directamente en su fuente antes de citarlo en el TI.** Cada celda indica de qué tipo de fuente sale.

## 1. Objetivo

Que ML1 pueda alimentarse con datos de distintos relojes del mercado, no solo Fitbit. Dispositivos
elegidos con el compañero de tesis (Android):

| Marca | Modelo | Precio aprox. (S/) |
|---|---|---|
| Samsung | Galaxy Watch FE | 550 – 700 |
| Fitbit | Charge 6 | 600 – 750 |
| Amazfit | Bip 5 (o Bip 5 Active) | 300 – 380 |
| Xiaomi | Smart Band 9 (básica, no "Active") | 150 – 200 |
| Apple | Apple Watch | fase posterior |

## 2. Variables que lee hoy el modelo (poc1)

11 variables crudas del Fitbit Sense (LifeSnaps), cada una agregada por persona como media y desviación
estándar (= 22 features). `sleep_points_percentage` NO es predictor: de ahí sale la etiqueta.

| Grupo | Variables |
|---|---|
| Sueño | `minutesAsleep`, `minutesAwake`, `sleep_efficiency`, `minutesToFallAsleep` |
| Corazón / sueño | `resting_hr`, `nremhr` (pulso en sueño no-REM), `rmssd` (HRV) |
| Respiración | `spo2`, `full_sleep_breathing_rate` |
| Actividad | `steps`, `sedentary_minutes` |

Top-5 features en poc1 por Gini importance (frágil, ver `poc1/README.md`): `minutesAwake_std` (0.148),
`sleep_duration_inconsistency` = std de `minutesAsleep` (0.112), `sedentary_minutes_mean` (0.100),
`steps_std` (0.060), `resting_hr_mean` (0.054). Las de menor peso son justo las menos disponibles:
SpO2, HRV, `nremhr`, respiración (~0.016–0.041) y `minutesToFallAsleep` (~0.002).

## 3. Qué llega desde cada reloj (Android, vía Health Connect o Google Health API)

Claves: **Of** = confirmado en documentación oficial. **Sec** = fuente secundaria (noticia/guía).
**Der** = derivable de otro dato, sin verificar. **No** = no aparece en lo encontrado. **?** = sin información.

| Variable | Tipo en Health Connect | Fitbit Charge 6 | Galaxy Watch FE | Amazfit Bip 5 | Xiaomi Band 9 |
|---|---|---|---|---|---|
| `minutesAsleep` | `SleepSessionRecord` | Of | Of | Sec | Sec |
| `minutesAwake` | etapa AWAKE de la sesión | Of | ? | ? | ? |
| `sleep_efficiency` | no existe; se calcula | Of (Google Health API) | Der | Der | Der |
| `resting_hr` | `RestingHeartRateRecord` | Of | No (Der desde HR) | Der | Der |
| `steps` | `StepsRecord` | Of | Of | ? | Sec |
| `sedentary_minutes` | **no existe** | Of (solo Google Health API) | No | No | No |
| `spo2` | `OxygenSaturationRecord` | Of | Of | No | No |
| `rmssd` (HRV) | `HeartRateVariabilityRmssdRecord` | Of | No | No | No |
| `full_sleep_breathing_rate` | `RespiratoryRateRecord` | Of | No | No | No |
| `nremhr` | `HeartRateRecord` cruzado con etapas | Der | Der | Der | Der |

### Discrepancias entre fuentes y cómo se resolvieron
- Un sitio de terceros decía que Samsung Health sincroniza HRV, respiración y pulso en reposo con Health
  Connect. El [blog oficial de Samsung Developers](https://developer.samsung.com/health/blog/en/accessing-samsung-health-data-through-health-connect)
  NO los lista (sí lista Steps, SpO2, HeartRate, SleepSession, Vo2Max, etc.). Se usó la versión oficial.
- Que un reloj **mida** algo no implica que su app lo **comparta**: Amazfit Bip 5 y Xiaomi Band 9 miden SpO2,
  pero no aparece en lo que sus apps sincronizan con Health Connect.

### Calidad de las fuentes (lo débil)
- **Amazfit:** lista de una [noticia de enero de 2025](https://www.notebookcheck.net/Amazfit-smartwatches-get-new-Health-Connect-data-sync-feature.951489.0.html):
  Zepp escribe en Health Connect solo presión arterial, frecuencia cardíaca, sueño y peso (conexión de una vía,
  solo escritura). Puede estar desactualizada.
- **Xiaomi:** guías de terceros (pasos, sueño, frecuencia cardíaca, ejercicios). La página oficial de Xiaomi
  (`mi.com/uk/support/faq/details/KA-230357/`) devolvió error 403 y no se pudo leer.
- **Fitbit Charge 6:** sensores (SpO2, HRV, respiración nocturna, temperatura, puntaje de sueño) salen de
  fuentes secundarias; la ficha oficial de Google Store no se pudo leer.
- **Amazfit Bip 5:** la [ficha oficial](https://us.amazfit.com/products/amazfit-bip-5) lista frecuencia cardíaca 24 h,
  SpO2, etapas de sueño, calidad de respiración al dormir y puntaje de sueño; NO menciona HRV, frecuencia
  respiratoria ni temperatura de piel.

## 4. Rutas de acceso a los datos

| | Google Health API | Health Connect |
|---|---|---|
| Qué es | API en la nube (OAuth 2.0), sucesora de la Fitbit Web API | Repositorio de datos dentro del teléfono Android que varias apps leen/escriben |
| Dispositivos | Página de `sleep` lista Fitbit (Charge 2–6, Sense, Versa, etc.) y Pixel Watch 1–4. La portada dice "y otras apps y dispositivos de terceros" sin detallar | Depende de que la app de cada marca escriba en él |
| Plataforma | Cualquiera (incluso desde un servidor) | Solo Android; la documentación no menciona iOS |
| Endpoint | `POST https://health.googleapis.com/v4/users/me/dataTypes/sleep/dataPoints` | SDK en la app Android |
| Requisito de publicación | Casi todos los scopes son restringidos, incluido `sleep.readonly`. Sin verificar: límite de 100 usuarios (según resumen de su [página de verificación](https://developers.google.com/health/app-verification); confirmar). Para publicar: verificación + evaluación de seguridad anual (CASA) con un tercero | [Formulario de declaración de apps de salud](https://support.google.com/googleplay/android-developer/answer/14738291?hl=en) en Play Console, incluso en pruebas cerradas; justificación por cada tipo de dato |

**Google Health API, tipo `sleep`** ([documentación](https://developers.google.com/health/data-types/sleep?hl=es-419)):
campos `minutesAsleep`, `minutesToFallAsleep`, `minutesAfterWakeup`, eficiencia = minutos dormido / minutos en cama × 100,
etapas `LIGHT`/`DEEP`/`REM`/`AWAKE`, `shortAwakenings`. **No hay campo de puntaje de sueño.**
`minutesToFallAsleep` vale 0 por defecto en registros autodetectados (explica por qué esa variable es casi
siempre 0 en LifeSnaps). Tipos de actividad: existe `sedentary-period` (período, no minutos totales) y `active-minutes`.

**Health Connect** ([tipos de datos](https://developer.android.com/health-and-fitness/health-connect/data-types)):
52 tipos de registro. Existen sueño con etapas (`AWAKE`, `LIGHT`, `DEEP`, `REM`), frecuencia cardíaca, HRV (RMSSD),
frecuencia cardíaca en reposo, SpO2, frecuencia respiratoria (general, no específica del sueño) y pasos.
**No existen** minutos sedentarios ni puntaje de sueño.

**Los relojes de Fitbit y Amazfit calculan un puntaje de sueño en su propia app, pero ni Health Connect ni la
Google Health API lo exponen como campo** (según lo leído).

## 5. Lectura para el modelo

- **Común a los cuatro (según lo encontrado):** sueño, frecuencia cardíaca y pasos (pasos de Amazfit sin confirmar).
- **Exclusivos de Fitbit:** HRV, respiración y sedentarismo.
- Un modelo con solo variables comunes cubriría 4 de las 5 features top de poc1 (algunas por derivación).
  **Se perdería `sedentary_minutes`**, que no existe en Health Connect. Se podría intentar aproximar con
  `ActivityIntensityRecord` o pasos por hora: es una hipótesis, sin verificar.
- **Riesgo de transferencia:** que el campo exista no implica la misma definición. Cada fabricante calcula sus
  variables con su propio algoritmo. La literatura de la tesis lo respalda: Lee et al. (2023) comparó 11
  dispositivos y su macro F1 varía de 0.26 a 0.69 según el dispositivo.

## 6. PoC multi-wearable

**Actualización:** se corrió un ensayo exploratorio (partes A y B) en [`POC_Multiwearable.ipynb`](POC_Multiwearable.ipynb): el modelo con solo las variables de cada reloj pierde bastante (Spearman 0.70 a 0.36–0.43) y casi todo por los minutos sedentarios; la capa de estandarización funciona como software. No mide diferencias reales entre marcas (solo hay datos de Fitbit). Abajo, la propuesta original:

1. Definir el **conjunto mínimo común** de variables que las marcas objetivo puedan entregar.
2. Con LifeSnaps, entrenar con solo ese conjunto y compararlo contra el modelo completo, con el mismo protocolo
   (Repeated Stratified 5-Fold × 20, F1 + ROC-AUC + PR-AUC vs baseline). Mide cuánto se pierde.
3. Decidir cómo aproximar `sedentary_minutes` (o prescindir de ella).
4. Verificación física: conectar cada reloj a un teléfono con Health Connect y revisar qué tipos de dato
   escribe su app (Health Connect → permisos de apps).

## 7. Pendientes de verificación

- `minutesAwake` (etapa AWAKE): ¿la escriben Samsung, Amazfit y Xiaomi?
- Pasos en Amazfit/Zepp: no aparecen en la lista encontrada.
- Si el límite de 100 usuarios sin verificar de la Google Health API aplica tal cual (leído en un resumen).
- Si alguna métrica del Fitbit Charge 6 requiere Fitbit Premium (no se pudo leer la ficha oficial).
- Lista actual de Zepp y Mi Fitness hacia Health Connect (las fuentes son de 2025 o de terceros).
- Apple (HealthKit): fuera de alcance por ahora.

## 8. Contexto de poc1 que conviene no perder (aún NO reflejado en `poc1/README.md` ni `CLAUDE.md`)

Hallazgos de esta sesión (2026-09-17 a 19), pendientes de decidir cómo documentarlos:
- **`sleep_points_percentage` no es un puntaje de calidad de sueño.** Según la Tabla 2 del data descriptor de
  LifeSnaps (Yfantidou et al., 2022), el *Stress Score* de Fitbit se calcula a partir de frecuencia cardíaca,
  sueño y nivel de actividad (36 usuarios, 1,911 respuestas). Que esa columna sea su componente de sueño (*Sleep
  Patterns*, sobre 30 puntos) está respaldado por los datos (mismas 1,876 filas y 37 personas que el resto de
  columnas del score, y 19 valores distintos en pasos de 1/30), aunque ningún diccionario oficial lo confirma
  literalmente. Detalle en `../POC1/POC1_FINDINGS.md`, sección 5. LifeSnaps no incluye ningún Sleep Score de 1–100.
- **Cobertura:** solo 37 de 71 personas tienen dato (1,876 filas). Las otras 34 reciben la mediana (0.62), que queda
  sobre el umbral de riesgo (0.611): quedan etiquetadas "bajo riesgo" sin medición. Las 18 personas de riesgo alto
  tienen todas dato real. Entre las 37 con dato real la prevalencia es 48.6%, no 25%.
- **Sospechas sin comprobar:** (a) el ROC-AUC de 0.73 podría estar inflado si el modelo detecta "personas con
  muchos datos faltantes"; (b) hay circularidad probable, porque el Stress Score usa frecuencia cardíaca, sueño y
  actividad, y las predictoras incluyen esas tres cosas.
- **Verificación pendiente (no corrida a pedido del usuario):** reevaluar solo con las 37 personas con etiqueta real.
- El otro chat propuso texto para `poc1/README.md` (corrección sobre `sleep_points_percentage` y una limitación
  de superposición conceptual con `minutesAwake_std`); no se aplicó. Sus cifras (36 usuarios, 1,911 respuestas)
  coinciden con la Tabla 2; su afirmación de que Fitbit no expone el Sleep Score por API ni export quedó sin verificar.
- La etiqueta definitiva será el PSQI de la Capa A. LifeSnaps no tiene PSQI y no se encontró otro dataset accesible
  con reloj + PSQI, así que ese dato debe recolectarse con participantes propios.

## 9. Protocolo para cuando lleguen los relojes (verificación física)

Objetivo: reemplazar las suposiciones de la tabla de la sección 3 por lo que realmente entrega cada reloj. **Los nombres de menús
cambian según la versión de Android y de cada app: confirmarlos en el momento.**

1. Emparejar cada reloj con la app de su marca (Fitbit, Samsung Health, Zepp, Mi Fitness) en un teléfono Android con Health Connect,
   y **activar la sincronización con Health Connect** dentro de esa app.
2. Usar cada reloj **al menos 10 noches** (la capa de estandarización rechaza a quien tiene menos), aunque para la primera revisión
   bastan 3.
3. En Health Connect, mirar por app y por categoría qué tipos de dato aparecen y anotar en la tabla de abajo.
4. Comparar, en la app de la marca y en Health Connect, los **minutos despierto** y la **eficiencia** de las mismas noches: es la
   sospecha que dejó el dato de Xiaomi (6.6 min despierto contra 50.6 en Fitbit).
5. Si la app permite pedir o exportar los datos propios (Mi Fitness, Zepp, Samsung Health), guardar la exportación en
   `datasets/<marca>/` con su `FUENTE.md`: sirve para escribir el adaptador real, como se hizo con Xiaomi.
6. Opcional, si se puede: dos relojes a la vez (uno en cada muñeca) durante 7 noches. Es la comparación directa entre marcas.

| Reloj | App de origen | Tipos de dato que llegan a Health Connect | Días con dato | ¿Pulso en reposo? | ¿Minutos despierto? | ¿SpO2? | Notas |
|---|---|---|---|---|---|---|---|
| Galaxy Watch FE | | | | | | | |
| Fitbit Charge 6 | | | | | | | |
| Amazfit Bip 5 | | | | | | | |
| Xiaomi Smart Band 9 | | | | | | | |

**Pruebas de robustez ya hechas con datos sintéticos:** `POC_Multiwearable_Robustez.ipynb`.
