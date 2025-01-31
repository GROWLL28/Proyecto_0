import flet as ft
import requests
from enum import Enum
import base64
from flet import Container, Row, Column, Image, Text

BASE_URL = "http://0.0.0.0:8080"  # Asegúrate de que esta URL coincida con la de tu backend

class CategoriaEnum(str, Enum):
    HOGAR = "Hogar"
    TRABAJO = "Trabajo"
    URGENTE = "Urgente"
    PERSONAL = "Personal"
    OTROS = "Otros"

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "Gestión de Tareas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Variables para almacenar datos de sesión
    page.client_storage.set("token", "")
    page.client_storage.set("username", "")

    # Componentes de UI
    txt_usuario = ft.TextField(label="Usuario", width=300)
    txt_password = ft.TextField(label="Contraseña", password=True, width=300)
    txt_error = ft.Text(color="red", size=14)
    lista_tareas = ft.ListView(expand=True, spacing=10, padding=20)
    
    # Campo para nueva tarea y selección de categoría
    txt_nueva_tarea = ft.TextField(
        label="Nueva tarea",
        multiline=True,
        min_lines=1,
        max_lines=3,
        expand=True
    )
    
    dd_categoria = ft.Dropdown(
        label="Categoría",
        options=[
            ft.dropdown.Option(key=cat.value, text=cat.value)
            for cat in CategoriaEnum
        ],
        value=CategoriaEnum.OTROS.value,
        width=200
    )

    # Estados para las tareas
    dd_estado = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Sin Empezar"),
            ft.dropdown.Option("Empezada"),
            ft.dropdown.Option("Finalizada")
        ],
        value="Sin Empezar",
        width=150
    )

    # Campos para el registro
    txt_nuevo_usuario = ft.TextField(label="Nuevo Usuario", width=300)
    txt_nueva_password = ft.TextField(label="Nueva Contraseña", password=True, width=300)
    txt_confirmar_password = ft.TextField(label="Confirmar Contraseña", password=True, width=300)
    txt_error_registro = ft.Text(color="red", size=14)
    
    # FilePicker para la imagen de perfil
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    imagen_perfil = ft.Image(src=r"C:\Users\nanox\Downloads\Proyecto_0\app\Front\DEFECTO.jpg", width=100, height=100)
    imagen_bytes = None

    def seleccionar_imagen(e):
        file_picker.pick_files("Selecciona una imagen", allowed_extensions=["jpg", "png", "jpeg"])

    def on_file_selected(e):
        nonlocal imagen_bytes
        if e.files:
            imagen_bytes = base64.b64encode(open(e.files[0].path, "rb").read()).decode("utf-8")
            imagen_perfil.src_base64 = imagen_bytes
            page.update()

    file_picker.on_result = on_file_selected

    def login(e):
        try:
            response = requests.post(
                f"{BASE_URL}/token",
                json={
                    "username": txt_usuario.value,
                    "password": txt_password.value
                }
            )
            if response.status_code == 200:
                data = response.json()
                page.client_storage.set("token", data["access_token"])
                page.client_storage.set("username", txt_usuario.value)
                page.go("/tareas")
            else:
                txt_error.value = "Usuario o contraseña incorrectos"
                page.update()
        except requests.RequestException:
            txt_error.value = "Error de conexión con el servidor"
            page.update()

    def registrar_usuario(e):
        if txt_nueva_password.value != txt_confirmar_password.value:
            txt_error_registro.value = "Las contraseñas no coinciden"
            page.update()
            return

        # Si no se selecciona una imagen, usar una por defecto
        imagen_bytes = None
        if not imagen_bytes:
            with open(r"C:\Users\nanox\Downloads\Proyecto_0\app\Front\DEFECTO.jpg", "rb") as f:
                imagen_bytes = base64.b64encode(f.read()).decode("utf-8")

        try:
            response = requests.post(
                f"{BASE_URL}/usuarios/",
                json={
                    "username": txt_nuevo_usuario.value,
                    "password": txt_nueva_password.value,
                    "imagen_perfil": imagen_bytes
                }
            )
            if response.status_code == 200:
                txt_nuevo_usuario.value = ""
                txt_nueva_password.value = ""
                txt_confirmar_password.value = ""
                txt_error_registro.value = "Usuario registrado exitosamente"
                txt_error_registro.color = "green"
                page.go("/")
            else:
                error_detail = response.json().get("detail", "Error al registrar usuario")
                txt_error_registro.value = error_detail
                txt_error_registro.color = "red"
            page.update()
        except requests.RequestException:
            txt_error_registro.value = "Error de conexión con el servidor"
            page.update()

    def logout():
        page.client_storage.set("token", "")
        page.client_storage.set("username", "")
        page.go("/")

    def mostrar_tareas(e):
        token = page.client_storage.get("token")
        if not token:
            page.go("/")
            return
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/tareas/",
            headers=headers
        )
        
        if response.status_code == 200:
            tareas = response.json()
            if tareas:
                # Obtener la información del usuario desde la primera tarea
                usuario_info = tareas[0].get("propietario", {})
                nombre_usuario = usuario_info.get("username", "")
                imagen_perfil_usuario = usuario_info.get("imagen_perfil", "")

                # Actualizar la imagen de perfil y el nombre en la UI
                imagen_perfil.src_base64 = imagen_perfil_usuario
                page.update()

                lista_tareas.controls = [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                # Mostrar la foto de perfil y el nombre del usuario
                                ft.Row([
                                    ft.Image(
                                        src_base64=imagen_perfil_usuario,
                                        width=30,
                                        height=30,
                                        border_radius=15
                                    ),
                                    ft.Text(nombre_usuario, size=14, weight=ft.FontWeight.W_500),
                                ], spacing=10),
                                ft.Row([
                                    ft.Text(
                                        tarea["texto"],
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        expand=True
                                    ),
                                    ft.IconButton(
                                        ft.icons.DELETE,
                                        icon_color="red",
                                        on_click=lambda _, t=tarea["id"]: eliminar_tarea(t)
                                    )
                                ]),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(
                                            tarea["categoria"],
                                            size=12,
                                            color=ft.colors.WHITE,
                                        ),
                                        bgcolor=ft.colors.BLUE,
                                        border_radius=15,
                                        padding=ft.padding.all(5),
                                    ),
                                    ft.Dropdown(
                                        value=tarea["estado"],
                                        options=[
                                            ft.dropdown.Option("Sin Empezar"),
                                            ft.dropdown.Option("Empezada"),
                                            ft.dropdown.Option("Finalizada")
                                        ],
                                        width=150,
                                        on_change=lambda e, t=tarea["id"]: actualizar_estado_tarea(t, e.control.value)
                                    )
                                ], spacing=10),
                                ft.Text(
                                    f"Creada: {tarea['fecha_creacion'].split('T')[0]}",
                                    size=12,
                                    color=ft.colors.GREY
                                )
                            ]),
                            padding=15
                        )
                    ) for tarea in tareas
                ]
            else:
                lista_tareas.controls = [ft.Text("No hay tareas disponibles")]
        else:
            lista_tareas.controls = [ft.Text("Error al cargar las tareas")]
        page.update()

        def eliminar_tarea(tarea_id: int):
            try:
                token = page.client_storage.get("token")
                if not token:
                    page.go("/")
                    return

                headers = {"Authorization": f"Bearer {token}"}
                response = requests.delete(
                    f"{BASE_URL}/tareas/{tarea_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    mostrar_tareas(None)
                else:
                    print(f"Error al eliminar tarea: {response.status_code}")
                page.update()
            except requests.RequestException as e:
                print("Error de conexión:", e)
                page.update()

        def actualizar_estado_tarea(tarea_id: int, nuevo_estado: str):
            try:
                token = page.client_storage.get("token")
                if not token:
                    page.go("/")
                    return

                headers = {"Authorization": f"Bearer {token}"}
                response = requests.put(
                    f"{BASE_URL}/tareas/{tarea_id}",
                    params={"estado": nuevo_estado},
                    headers=headers
                )
                
                if response.status_code == 200:
                    mostrar_tareas(None)
                else:
                    print(f"Error al actualizar estado: {response.status_code}")
                page.update()
            except requests.RequestException as e:
                print("Error de conexión:", e)
                page.update()

    def crear_tarea(e):
        try:
            token = page.client_storage.get("token")
            if not token:
                page.go("/")
                return

            if not txt_nueva_tarea.value:
                return

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{BASE_URL}/tareas/",
                json={
                    "texto": txt_nueva_tarea.value,
                    "categoria": dd_categoria.value,
                    "estado": dd_estado.value
                },
                headers=headers
            )
            
            if response.status_code == 200:
                txt_nueva_tarea.value = ""
                dd_categoria.value = CategoriaEnum.OTROS.value
                dd_estado.value = "Sin Empezar"
                mostrar_tareas(None)
                page.update()
            else:
                print("Error al crear la tarea:", response.status_code)
        except requests.RequestException as e:
            print("Error de conexión:", e)
            page.update()

    def route_change(route):
        page.views.clear()
        
        if page.route == "/" or page.route == "":
            # Vista de login
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Iniciar Sesión")),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Bienvenido", size=30, weight=ft.FontWeight.BOLD),
                                    txt_usuario,
                                    txt_password,
                                    ft.Row(
                                        [
                                            ft.ElevatedButton("Iniciar Sesión", on_click=login),
                                            ft.TextButton("Registrarse", on_click=lambda _: page.go("/registro")),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    txt_error,
                                ],
                                spacing=20,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            margin=ft.margin.all(20),
                        ),
                    ],
                )
            )
        elif page.route == "/registro":
            # Vista de registro
            page.views.append(
                ft.View(
                    "/registro",
                    [
                        ft.AppBar(
                            title=ft.Text("Registro de Usuario"),
                            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Crear Cuenta", size=30, weight=ft.FontWeight.BOLD),
                                    txt_nuevo_usuario,
                                    txt_nueva_password,
                                    txt_confirmar_password,
                                    ft.ElevatedButton("Seleccionar Imagen", on_click=seleccionar_imagen),
                                    imagen_perfil,
                                    ft.ElevatedButton("Registrar", on_click=registrar_usuario),
                                    txt_error_registro,
                                ],
                                spacing=20,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            margin=ft.margin.all(20),
                        ),
                    ],
                )
            )
        elif page.route == "/tareas":
            # Vista de tareas
            page.views.append(
                ft.View(
                    "/tareas",
                    [
                        ft.AppBar(
                            title=ft.Text("Mis Tareas"),
                            actions=[
                                ft.IconButton(
                                    icon=ft.icons.LOGOUT,
                                    tooltip="Cerrar sesión",
                                    on_click=lambda _: logout()
                                )
                            ]
                        ),
                        ft.Container(
                            content=ft.Column([
                                # Mostrar la imagen de perfil y el nombre de usuario
                                ft.Row(
                                    [
                                        ft.Image(src_base64=imagen_perfil.src_base64, width=50, height=50),
                                        ft.Text(page.client_storage.get("username"), size=20),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=10,
                                ),
                                ft.Row(
                                    [
                                        txt_nueva_tarea,
                                        dd_categoria,
                                        dd_estado,
                                        ft.IconButton(
                                            icon=ft.icons.ADD_CIRCLE,
                                            icon_color="blue",
                                            icon_size=40,
                                            tooltip="Agregar tarea",
                                            on_click=crear_tarea
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                lista_tareas,
                            ]),
                            padding=20,
                        ),
                    ],
                )
            )
            mostrar_tareas(None)
        
        page.update()

    # Configurar el manejador de rutas y empezar en la ruta inicial
    page.on_route_change = route_change
    page.go("/")

ft.app(target=main,port=8500)