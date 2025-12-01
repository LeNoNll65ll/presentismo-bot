from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import json

# ==========================
# 1. CARGA DE DATOS DESDE JSON
# ==========================

# Archivo JSON que recibís con los datos del parte
# Estructura esperada (lista de diccionarios):
# [
#   {
#     "1. Identifíquese:": "CT Víctor Adrián Vera",
#     "2. Indique estado:": "Presente",
#     "3. En caso de ausente: indicar la causa textual para transcribir al Parte Oficial.": ""
#   },
#   ...
# ]
with open("./datos_parte.json", "r", encoding="utf-8") as f:
    datos_json = json.load(f)

# Orden fijo en el que SIEMPRE aparecen en el SIFIE
orden_sifie = [
    "CT Víctor Adrián Vera",
    "CT Santiago Sánchez Albornoz",
    "CT Hernán Ariel Pérez",
    "CT Ezequiel Waldo Olivera",
    "CT Franco Guarnieri",
    "CT Fernando Darío Guaimás Rosado",
    "CT Mauricio Casals",
    "CT Damián Gonzalo Amor"
]

# Mapa nombre -> registro del JSON
mapa = {item["1. Identifíquese:"]: item for item in datos_json}

# Reordenar los datos según el orden del sistema
datos_ordenados = [mapa[nombre] for nombre in orden_sifie]

# DEBUG: mostrar orden final
print("=== Datos ordenados según SIFIE ===")
for i, fila in enumerate(datos_ordenados, start=1):
    nombre = fila["1. Identifíquese:"]
    estado = fila["2. Indique estado:"]
    causa = fila["3. En caso de ausente: indicar la causa textual para transcribir al Parte Oficial."]
    print(f"{i}. {nombre:<40} Estado: {estado}" + (f". Causa: {causa}" if causa.strip() else ""))


# ==========================
# 2. CONFIGURACIÓN SELENIUM
# ==========================

options = webdriver.ChromeOptions()

options.add_argument('--remote-debugging-port=9222')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

manager = ChromeDriverManager()
manager.driver_version = "136.0.7103.93"
service = Service(manager.install())

try:
    driver = webdriver.Chrome(service=service, options=options)
except Exception as e:
    print("Error detectado al iniciar Chrome:", e)
    exit()


# ==========================
# 3. LOGIN EN SIFIE
# ==========================

driver.get("https://sifie.fie.undef.edu.ar/sifie/login")
driver.find_element(By.XPATH, "//*[@id='username']").send_keys("bedel5")   # usuario
driver.find_element(By.XPATH, "//*[@id='password']").send_keys("35440779") # contraseña
driver.find_element(By.XPATH, "/html/body/div/div[2]/form/div[3]/button").click()  # botón ingresar
time.sleep(2)

# ==========================
# 4. INGRESAR A PARTE DE NOVEDADES
# ==========================

#driver.find_element(By.XPATH, "/html/body/div/main/div/div/div/div/div/div/div/div/div/div[1]").click()
driver.find_element(By.XPATH, "//a[@href='https://sifie.fie.undef.edu.ar/parte-novedades']").click()
time.sleep(2)

# ==========================
# 7. CERRAR SESIÓN
# ==========================
driver.find_element(By.CSS_SELECTOR, "a.nav-link.dropdown-toggle").click()
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, "form[action$='/logout'] button[type='submit']").click()
time.sleep(5)

# ==========================
# 5. CAMBIAR ESTADO DE CADA CURSANTE (UNA SOLA PASADA)
# ==========================

filas_html = driver.find_elements(By.XPATH, "//tbody[@class='text-sm']/tr")

# Se asume que la tabla del SIFIE tiene el mismo orden que 'orden_sifie'
for fila_html, fila_df in zip(filas_html, datos_ordenados):

    nombre_json = fila_df["1. Identifíquese:"]
    estado = fila_df["2. Indique estado:"]
    causa = fila_df["3. En caso de ausente: indicar la causa textual para transcribir al Parte Oficial."]

    # (Opcional) leer nombre/estado actuales del HTML para control
    nombre_html = fila_html.find_element(By.XPATH, "./td[2]").text  # según tu captura, col 2 = Cursante
    print(f"Fila SIFIE: {nombre_html} | JSON: {nombre_json} → {estado}")

    # Caso: Presente -> click en botón de estado (columna 4)
    if estado == "Presente":
        boton_estado = fila_html.find_element(By.XPATH, "./td[4]/button")
        boton_estado.click()
        time.sleep(0.5)

    # Caso: Ausente -> editar, cargar causa y guardar
    if estado == "Ausente":
        boton_editar = fila_html.find_element(By.XPATH, "./td[5]/a")  # botón editar (columna 5)
        boton_editar.click()
        time.sleep(1)

        campo_novedad = driver.find_element(By.XPATH, '//*[@id="novedad"]')
        campo_novedad.click()
        time.sleep(0.3)
        campo_novedad.clear()
        campo_novedad.send_keys(causa)
        time.sleep(0.3)

        boton_guardar = driver.find_element(
            By.XPATH,
            '//*[@id="showModalNew"]/div/div/div[2]/div/form/div[2]/input'
        )
        boton_guardar.click()
        time.sleep(1)


# ==========================
# 6. ELEVAR PARTE (OPCIONAL)
# ==========================

# Si querés elevar automáticamente, descomentá:
# driver.find_element(By.XPATH, '//*[@id="elevar"]').click()
# time.sleep(1)
# driver.find_element(By.XPATH, '/html/body/div[2]/div/div[6]/button[1]').click()
# time.sleep(1)

# ==========================
# 7. CERRAR SESIÓN
# ==========================
driver.find_element(By.CSS_SELECTOR, "a.nav-link.dropdown-toggle").click()
time.sleep(0.5)
driver.find_element(By.CSS_SELECTOR, "form[action$='/logout'] button[type='submit']").click()
time.sleep(10)

driver.quit()