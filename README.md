# DDAEmpresariales5 — Administrador con Django

Laboratorio 05 de Desarrollo de Aplicaciones Empresariales (4-C24-A).
App `movies` con los modelos `Movie`, `Genre`, `Person` y `Rating`, el panel de administración personalizado, el grupo `editores` y una vista pública de recomendaciones.

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo     # 10 películas, 4 géneros, valoraciones, grupo y usuarios
python manage.py runserver
```

- Panel: http://127.0.0.1:8000/admin/
- Vista pública: http://127.0.0.1:8000/
- Usuarios de demostración: `admin` (superusuario) y `editor1` (grupo `editores`). Las contraseñas de demostración se pueden cambiar con las variables `DEMO_ADMIN_PASSWORD` y `DEMO_EDITOR_PASSWORD` antes de ejecutar `setup_demo`. No usar estas cuentas fuera del laboratorio.
- `SECRET_KEY` y `DEBUG` se leen de las variables `DJANGO_SECRET_KEY` y `DJANGO_DEBUG`.

## Pruebas

```bash
python manage.py test
```

## Configuración del panel

| Modelo | list_display | list_filter | search_fields | Extras |
|---|---|---|---|---|
| Movie | título, año, director, géneros, creación | género, año | título, director | `RatingInline`, `filter_horizontal` |
| Genre | nombre, creación | — | nombre | — |
| Person | nombre, nacimiento | — | nombre | — |
| Rating | película, evaluador, puntaje, creación | puntaje, género | película, evaluador | — |

Los campos `created_at` y `updated_at` son de solo lectura en todos los modelos.

## Observaciones: roles y por qué

- **Superusuario (`admin`)**: ve y gestiona los cuatro modelos, usuarios y grupos. Reservado para quien administra el sistema.
- **Grupo `editores`**: puede ver, añadir y cambiar películas, pero **no eliminarlas** ni tocar géneros, personas, valoraciones, usuarios o grupos. Una película borrada arrastra sus valoraciones (`CASCADE`), así que eliminar es la operación irreversible y se deja solo al superusuario. Las valoraciones se editan dentro del formulario de la película mediante el inline, pero un editor sin permiso sobre `Rating` solo las ve; no las modifica.
- **Qué desaparece para el editor**: en el panel solo aparece «Películas»; los demás modelos y la sección de autenticación no se muestran, y el botón de eliminar tampoco (un intento directo por URL devuelve 403, comprobado en las pruebas).
- **Panel vs. vista propia**: el panel resuelve el CRUD sin escribir vistas, pero no puede expresar «las mejor valoradas de un género», que requiere agregaciones (`Avg`, `Count`) y una vista pública propia (`/recomendaciones/<id>/`).
