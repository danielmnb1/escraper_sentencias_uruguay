import tkinter as tk
from tkinter import messagebox
import threading
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import csv

def ejecutar_script():
    ejecutar_button.config(state=tk.DISABLED)
    # Obtener los valores de los inputs
    fecha_ini = fecha_ini_entry.get()
    fecha_end = fecha_end_entry.get()

    def ejecutar_en_hilo():
        # Configura las opciones de Chrome
        chrome_options = Options()
        #chrome_options.headless = False

        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--headless')

        # Crea un servicio de Chrome
        service = Service("C:\\tinder\\chromedriver.exe")

        # Inicia el navegador Chrome con las opciones y el servicio configurados
        driver = undetected_chromedriver.Chrome(service=service, options=chrome_options)

        print("ingresando a la pagina")
        driver.get("https://bjn.poderjudicial.gub.uy/BJNPUBLICA/busquedaSelectiva.seam?cid=16774")
        time.sleep(10)
        fecha_ante = driver.find_element(By.ID,'formBusqueda:j_id20:j_id23:fechaDesdeCalInputDate')
        fecha_ante.send_keys(fecha_ini)
        time.sleep(1)
        print("ingresando datos")
        fecha_despues = driver.find_element(By.ID,'formBusqueda:j_id20:j_id147:fechaHastaCalInputDate')
        fecha_despues.send_keys(fecha_end)
        time.sleep(1)

        elemento_input = driver.find_element(By.ID,'formBusqueda:j_id20:j_id223:cantPagcomboboxValue')

        # También puedes cambiar el valor del elemento si es necesario
        nuevo_valor = '200'  
        driver.execute_script("arguments[0].setAttribute('value', arguments[1])", elemento_input, nuevo_valor)
        time.sleep(1)


        select_element = driver.find_element(By.NAME, "formBusqueda:j_id20:j_id240:j_id248")

        # Crear un objeto Select a partir del elemento encontrado
        select = Select(select_element)

        # Seleccionar la opción por valor
        select.select_by_value("FECHA_ASCENDENTE")
        time.sleep(1)

        fecha_despues = driver.find_element(By.ID,'formBusqueda:j_id20:Search')
        fecha_despues.click()
        print("Buscando.....")
        time.sleep(10)

        elemento_span = driver.find_elements(By.CLASS_NAME, 'negrita')
        # Obtener el texto del elemento
        texto_span = elemento_span[1].text

        # Extraer el valor "375" del texto
        valor = int(texto_span.split()[-1] ) # Esto toma la última palabra del texto

        print("Numeros de paginas de sentencia para Escrapeando", valor)

        valor = 3

        for i in range(valor):
            tabla = driver.find_element(By.ID,'formResultados:dataTable')

            # Obtener todas las filas de la tabla
            filas = tabla.find_elements(By.TAG_NAME,'tr')

            datos_tabla = []

            # Iterar sobre las filas para obtener los datos de cada celda
            for fila in filas:
                # Obtener las celdas de cada fila
                celdas = fila.find_elements(By.TAG_NAME, 'td')
                datos_fila = []
                for celda in celdas:
                    # Obtener el texto de cada celda
                    datos_fila.append(celda.text)
                # Agregar los datos de la fila a la lista de datos de la tabla
                datos_tabla.append(datos_fila)

            # Escribir los datos en un archivo CSV
            encabezado = ['Fecha', 'Tipo', 'Numero', 'Sede Sentencia', 'Procedimiento']

            # Nombre del archivo CSV
            nombre_archivo_csv = 'datos_sentencia.csv'

            # Abrir el archivo CSV en modo de adición ('a' para 'append')
            with open(nombre_archivo_csv, 'a', newline='', encoding='utf-8') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)

                # Comprobar si el archivo está vacío
                archivo_vacio = archivo_csv.tell() == 0

                # Escribir el encabezado si el archivo está vacío
                if archivo_vacio:
                    escritor_csv.writerow(encabezado)

                # Escribir los datos en el archivo sin sobrescribir
                for fila in datos_tabla:
                    escritor_csv.writerow(fila)
            print(f"guardado la pagina de sentencia Nro:{i}")
            siguiente = driver.find_element(By.ID, 'formResultados:sigLink')
            siguiente.click()
            print("Buscando la siguiente")
            time.sleep(10)

        # Limpieza de filas en blanco al finalizar el loop
        # Leer el archivo CSV y eliminar las filas en blanco
        print("haciendo ultimos ajustes")
        with open(nombre_archivo_csv, 'r', newline='', encoding='utf-8') as archivo_lectura:
            lineas = archivo_lectura.readlines()
            lineas = [linea.strip() for linea in lineas if linea.strip()]

        # Escribir nuevamente al archivo CSV eliminando las filas en blanco
        with open(nombre_archivo_csv, 'w', newline='', encoding='utf-8') as archivo_csv:
            for linea in lineas:
                archivo_csv.write(linea + '\n')
        driver.quit()
        print("finalizado el proceso")
        root.after(0, lambda: [
            messagebox.showinfo("Script finalizado", "El script ha finalizado con éxito."),
            ejecutar_button.config(state=tk.NORMAL)
        ])
    threading.Thread(target=ejecutar_en_hilo).start()
# Configuración de la ventana principal
root = tk.Tk()
root.title("Ejecutar Script")

# Establecer dimensiones de la ventana
ancho_ventana = 500
alto_ventana = 300
x_ventana = (root.winfo_screenwidth() // 2) - (ancho_ventana // 2)
y_ventana = (root.winfo_screenheight() // 2) - (alto_ventana // 2)
root.geometry(f"{ancho_ventana}x{alto_ventana}+{x_ventana}+{y_ventana}")

# Creación de los elementos de la interfaz
tk.Label(root, text="Fecha Inicial (DD/MM/YYYY):").grid(row=0, column=0)
fecha_ini_entry = tk.Entry(root)
fecha_ini_entry.grid(row=0, column=1)

tk.Label(root, text="Fecha Final (DD/MM/YYYY):").grid(row=1, column=0)
fecha_end_entry = tk.Entry(root)
fecha_end_entry.grid(row=1, column=1)

ejecutar_button = tk.Button(root, text="Ejecutar Script", command=ejecutar_script)
ejecutar_button.grid(row=2, columnspan=2)

root.mainloop()
