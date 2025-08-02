import sqlite3
import flet as ft

# Database setup
conn = sqlite3.connect("biblioteca.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        anio INTEGER
    )
    """
)
conn.commit()

# CRUD operations
def obtener_libros():
    cursor.execute("SELECT id, titulo, autor, anio FROM libros")
    return cursor.fetchall()

def agregar_libro(titulo, autor, anio):
    cursor.execute(
        "INSERT INTO libros (titulo, autor, anio) VALUES (?, ?, ?)",
        (titulo, autor, anio)
    )
    conn.commit()

def editar_libro(libro_id, titulo, autor, anio):
    cursor.execute(
        "UPDATE libros SET titulo = ?, autor = ?, anio = ? WHERE id = ?",
        (titulo, autor, anio, libro_id)
    )
    conn.commit()

def eliminar_libro(libro_id):
    cursor.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
    conn.commit()

# Flet UI
def main(page: ft.Page):
    page.title = "Gestión de Librería"
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Controles de entrada
    input_titulo = ft.TextField(label="Título", width=300)
    input_autor = ft.TextField(label="Autor", width=300)
    input_anio = ft.TextField(label="Año", width=100)
    btn_agregar = ft.ElevatedButton(text="Agregar Libro")

    # Listado de libros
    lista_libros = ft.ListView(expand=True, spacing=10, padding=10)

    def cargar_libros():
        lista_libros.controls.clear()
        for libro in obtener_libros():
            libro_id, titulo, autor, anio = libro
            # Crear fila con datos y botones de acción
            btn_edit = ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, lid=libro_id: abrir_dialogo_editar(lid)
            )
            btn_delete = ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip="Eliminar",
                on_click=lambda e, lid=libro_id: (eliminar_libro(lid), cargar_libros())
            )
            lista_libros.controls.append(
                ft.Row([
                    ft.Text(f"{titulo} | {autor} | {anio}"),
                    btn_edit,
                    btn_delete
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        page.update()

    def on_agregar_click(e):
        titulo = input_titulo.value.strip()
        autor = input_autor.value.strip()
        anio = int(input_anio.value.strip()) if input_anio.value.isdigit() else None
        if titulo and autor and anio:
            agregar_libro(titulo, autor, anio)
            input_titulo.value = ""
            input_autor.value = ""
            input_anio.value = ""
            cargar_libros()

    btn_agregar.on_click = on_agregar_click

    # Diálogo de edición
    dlg = ft.AlertDialog(title=ft.Text("Editar Libro"))
    edit_titulo = ft.TextField(label="Título", width=300)
    edit_autor = ft.TextField(label="Autor", width=300)
    edit_anio = ft.TextField(label="Año", width=100)
    btn_guardar = ft.ElevatedButton(text="Guardar")

    def abrir_dialogo_editar(lid):
        # Cargar datos actuales
        cursor.execute("SELECT titulo, autor, anio FROM libros WHERE id = ?", (lid,))
        fila = cursor.fetchone()
        if fila:
            t, a, y = fila
            edit_titulo.value = t
            edit_autor.value = a
            edit_anio.value = str(y)
            dlg.content = ft.Column([
                edit_titulo,
                edit_autor,
                edit_anio,
                btn_guardar
            ])
            def on_guardar(e):
                editar_libro(lid, edit_titulo.value.strip(), edit_autor.value.strip(), int(edit_anio.value.strip()))
                page.dialog.open = False
                cargar_libros()
                page.update()
            btn_guardar.on_click = on_guardar
            dlg.open = True
            page.update()

    page.add(
        ft.Row([input_titulo, input_autor, input_anio, btn_agregar], spacing=20),
        ft.Text("Lista de Libros", style="headlineMedium"),
        lista_libros,
        dlg
    )

    cargar_libros()

if __name__ == "__main__":
    ft.app(target=main)
