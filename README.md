# Presentismo Bot (WhatsApp + Evolution API)

Bot de presentismo para equipos que reportan asistencia por WhatsApp.  
Escucha mensajes entrantes vía **Evolution API** (WebSocket), guarda los eventos en **SQLite** y:
- Envía **recordatorios** (sólo a quienes no respondieron dentro de una franja horaria).
- Genera y envía un **reporte** al grupo y un **detalle al admin**.
- Responde automáticamente a cada usuario cuando envía un mensaje **válido** (confirmación de estado y cambios).

> Probado en Linux y Raspberry Pi. Proyecto en Python 3.11 con `venv` + `apscheduler` + `python-socketio` + `sqlite3`.

---

## ✨ Características

- **Ingesta en tiempo real** desde Evolution API WebSocket (evento `messages.upsert`).
- **SQLite** como base local: `eventos.db` (idempotencia y esquema simple).
- **Confirmaciones automáticas** de estado al usuario (PRESENTE / AUSENTE con causa).
- **Recordatorios inteligentes**: se notifican **sólo** los *AUSENTE SIN CAUSA* dentro de la franja.
- **Reporte diario**:
  - Al **grupo**: resumen sin causas.
  - Al **admin**: detalle con causas.
- **Orquestación flexible**:
  - `listener_db.py` escucha/guarda eventos.
  - `presentismo.py` agenda recordatorios + reporte.
  - `main.py` los corre **en paralelo**.
- **Configuración por `.env`** (horarios, franja, credenciales y mapeo de compañeros).
- **Tests** incluidos: lógica de DB, envío y formateo de reporte.

---

## 🧭 Arquitectura y flujo

```
Evolution API (WS) ──> listener_db.py ──> SQLite: eventos.db
                              │
                              └── notificador.py  (envía confirmaciones al usuario)
                                
presentismo.py (scheduler) ──> get_reporte(...) ──> envía recordatorios + reporte
           ▲
           └── main.py (lanza listener + scheduler en paralelo)
```

**Flujo diario** (típico):
1) Durante la franja `FRANJA_INICIO`–`FRANJA_FIN` se reciben mensajes.  
2) `db_logic.get_reporte(...)` clasifica por nombre:  
   - **PRESENTE** si el último mensaje válido es “presente…”.  
   - **AUSENTE CON CAUSA** si el último mensaje válido empieza con “ausente…” o “causa:…”.  
   - **AUSENTE SIN CAUSA** si no hubo mensajes válidos en la franja.  
3) `presentismo.py` envía recordatorios **sólo** a *AUSENTE SIN CAUSA*.  
4) `presentismo.py` envía al final: **resumen al grupo** y **detalle al admin**.

> Nota: En la implementación de ejemplo se considera **el último** mensaje válido de cada número dentro de la franja. Si alguien cambia de opinión (ej. de PRESENTE a AUSENTE con causa), el estado se actualiza y se confirma por privado.

---

## 📁 Estructura del repo

```
presentismo/
├── db_logic.py          # lógica de reporte (fecha + franja; considera último mensaje válido)
├── evolution_api.py     # wrapper de envío por Evolution API (HTTP)
├── listener_db.py       # cliente WS (socket.io) -> inserta en SQLite + llama al notificador
├── notificador.py       # confirma por privado el estado (si remitente es válido)
├── presentismo.py       # scheduler: recordatorios + reporte (lee horarios/ventanas desde .env)
├── main.py              # entrypoint que corre scheduler + listener en paralelo
├── eventos.db           # base SQLite (se crea al vuelo)
├── requirements.txt
├── test_db.py
├── test_send.py
└── (opcional) test_presentismo.py / test_notificador.py
```

---

## 🔧 Requisitos

- Python **3.11** (o compatible).
- Entorno virtual `venv` (recomendado).
- Acceso a **Evolution API** (URL base, instancia y API key para WS; token y URL para envío HTTP).
- Raspberry Pi (opcional) para ejecución programada.

Instalación de dependencias:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔐 Variables de entorno (`.env`)

Ejemplo completo:

```ini
# Chat donde se publica el resumen y usuario admin
GRUPO_ID=123456
ADMIN_ID=654321

# Mapeo "numero:nombre" separados por coma
COMPANEROS=111:Juan Pérez,222:María Gómez,333:Carlos López

# Schedulers
RECORDATORIOS=07:00,07:15,07:30,08:00,08:15
REPORTE_FINAL=08:30

# Ventana de control del presentismo (para get_reporte)
FRANJA_INICIO=06:00
FRANJA_FIN=08:30

# Evolution API - WebSocket (para listener_db.py)
BASE_URL=http://localhost:8080
INSTANCE=mi_instancia
API_KEY=token_ws
```

> Asegurate de cargar `.env` en el entorno (`python-dotenv` ya está integrado en los módulos).

---

## ▶️ Cómo ejecutar

### Opción A — Todo junto (recomendado)
Ejecuta **scheduler** + **listener** en paralelo:

```bash
source venv/bin/activate
python main.py
```

### Opción B — Sólo el listener (ingesta WS)
```bash
source venv/bin/activate
python listener_db.py
```

### Opción C — Sólo el scheduler
> Útil para depurar recordatorios y reporte.
```bash
source venv/bin/activate
python presentismo.py  # (si definiste un __main__) 
# o, si no hay __main__, usar main.py o un wrapper que llame start_scheduler()
```

---

## 🤖 Confirmaciones automáticas (notificador)

- `notificador.py` exporta `notificar_respuesta(numero: str, mensaje: str)`.
- Es invocado al final de `save_event(...)` en `listener_db.py`.
- Lógica:
  - Ignora remitentes que **no** estén en `COMPANEROS`.
  - Responde ✅ si comienza con `presente`.
  - Responde ❌ si comienza con `ausente` o `causa:` (incluye la causa textual).
  - Cualquier otro texto no responde.

Ejemplo de confirmación:
- `presente` → `✅ Hola Juan Pérez, tu presentismo fue registrado como PRESENTE.`
- `ausente: turno médico` → `❌ Hola Juan Pérez, tu presentismo fue registrado como AUSENTE (ausente: turno médico).`

---

## 🧠 Lógica de `db_logic.get_reporte(...)`

Firma:
```python
get_reporte(companeros: dict[str, str], fecha: date | None, inicio: time | None, fin: time | None) -> dict[str, str]
```
- Filtra **por día** y **por franja**.
- Revisa **sólo mensajes válidos**: `presente%`, `ausente%`, `causa:%`.
- Considera el **último** mensaje válido por número en ese rango.
- Devuelve un dict `{Nombre: "PRESENTE" | "AUSENTE CON CAUSA (...)" | "AUSENTE SIN CAUSA"}`.

> `presentismo.enviar_recordatorio()` envía sólo a quienes están como **"AUSENTE SIN CAUSA"** en ese cálculo.

---

## 🗄️ Esquema de SQLite

```sql
CREATE TABLE IF NOT EXISTS eventos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fechahora TEXT,
  numero_salida TEXT,
  numero_llegada TEXT,
  tipo_evento TEXT,
  mensaje TEXT,
  id_mensaje TEXT,
  id_mensaje_respondido TEXT
);

CREATE INDEX IF NOT EXISTS idx_eventos_num_ts ON eventos (numero_salida, fechahora);
```

> `fechahora` se almacena en formato `YYYY-MM-DD HH:MM:SS` (zona `America/Argentina/Buenos_Aires`).

---

## 📜 Logs

- Ejecución manual: salida a consola.
- Ejecución con scripts/cron: se recomienda redirigir a `bot.log`.
- Cambiar nivel con `logging.basicConfig(level=logging.INFO)` (ej. `DEBUG`).

Tail en vivo:
```bash
tail -f /home/servidor3/chatbot/presentismo/bot.log
```

---

## ⏱️ Ejecución en Raspberry Pi con `cron`

### Scripts de ayuda

**`start.sh`**
```bash
#!/bin/bash
cd ~/chatbot/presentismo
./venv/bin/python main.py >> bot.log 2>&1 &
echo $! > bot.pid
```

**`stop.sh`**
```bash
#!/bin/bash
cd ~/chatbot/presentismo
if [ -f bot.pid ]; then
  kill $(cat bot.pid) && rm bot.pid
fi
```

Dar permisos:
```bash
chmod +x start.sh stop.sh
```

### Entradas de `crontab` (usuario `servidor3`)
```cron
# Inicia el bot a las 06:00
0 6 * * * /home/servidor3/chatbot/presentismo/start.sh
# Detiene el bot a las 08:30
30 8 * * * /home/servidor3/chatbot/presentismo/stop.sh
```

> Verificar con `crontab -l`.  
> Si querés logs en `/var/log`, ajustá la ruta de `bot.log`.

---

## 🧩 Solución de problemas

- **No cierra el proceso con cron**  
  Usar `bot.pid` + `stop.sh` (método más confiable). Verificar permisos y rutas.

- **`TypeError: 'module' object is not callable`**  
  Asegurate de importar `time` desde `datetime` si vas a construir horas:
  ```python
  from datetime import time
  h, m = 7, 30
  t = time(h, m)
  ```
  Si necesitás el módulo `time` para `sleep`, importalo con alias:
  ```python
  import time as time_module
  time_module.sleep(1)
  ```

- **No conecta a Evolution API (WS)**  
  Revisar `BASE_URL`, `INSTANCE`, `API_KEY` y reachability de red. Chequear que el URL de WS sea `ws://` o `wss://` acorde.

- **Zona horaria**  
  El listener usa `America/Argentina/Buenos_Aires` para `fechahora`. Ajustar si fuese necesario.

- **Permisos en Raspberry**  
  Asegurarse de que el usuario tenga permisos de escritura sobre la carpeta del proyecto (para `bot.log` y `bot.pid`).

---

## 🔒 Seguridad y privacidad

- El archivo `.env` contiene tokens/keys; **no** versionarlo en git.
- Los números de teléfono y mensajes son datos personales: proteger `eventos.db` y los logs.
- Rotar tokens periódicamente. Usar HTTPS/WSS cuando sea posible.

---

## 🗺️ Roadmap (ideas futuras)

- Comandos administrativos por WhatsApp (ej. `status`, `help`).
- Cambiar franja/horarios por mensaje admin.
- Reintentos y colas de envío.
- Exportación de reporte (CSV/PDF).
- Dockerfile + Compose.

---

## 👤 Autor

- Hernán Ariel Pérez (perico) – _implementación y despliegue_
asdfasdfsadfsfa