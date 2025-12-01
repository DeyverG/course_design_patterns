# Refactorización

## Índice
1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Problemas del Código Original (Code Smells)](#problemas-del-código-original-code-smells)
3. [Soluciones Aplicadas](#soluciones-aplicadas)
4. [Patrones de Diseño Utilizados](#patrones-de-diseño-utilizados)
5. [Principios SOLID Aplicados](#principios-solid-aplicados)
6. [Decisiones de Diseño](#decisiones-de-diseño)
7. [Diagramas](#diagramas)

---

## Resumen del Proyecto

Este proyecto es una API REST construida con Flask que gestiona productos, categorías y favoritos de una tienda. La refactorización se enfocó en aplicar patrones de diseño y buenas prácticas para mejorar la mantenibilidad, legibilidad y escalabilidad del código.

---

## Problemas del Código Original (Code Smells)

### 1. **Código Duplicado (DRY Violation)**
La validación del token de autenticación se repetía en **cada método** de cada endpoint:

```python
# Este bloque aparecía en TODOS los métodos GET, POST, DELETE
token = request.headers.get('Authorization')
if not token:
    return { 'message': 'Unauthorized acces token not found'}, 401
if not is_valid_token(token):
    return { 'message': 'Unauthorized invalid token'}, 401
```

**Impacto:** Si necesitáramos cambiar la lógica de autenticación, tendríamos que modificar más de 10 lugares diferentes.

### 2. **Magic Strings (Cadenas Mágicas)**
Valores hardcodeados dispersos en múltiples archivos:

```python
# En auth.py
if username == 'student' and password == 'desingp':
    token = 'abcd12345'

# En products.py, categories.py, favorites.py
def is_valid_token(token):
    return token == 'abcd1234'  # ¡Diferente token!

# Rutas de archivo repetidas
self.db = DatabaseConnection('db.json')
```

**Impacto:** Inconsistencias (tokens diferentes), difícil mantenimiento.

### 3. **Violación del Principio de Responsabilidad Única (SRP)**
La clase `DatabaseConnection` original conocía todas las entidades del sistema:

```python
class DatabaseConnection:
    # Métodos específicos de productos
    def get_products(self): ...
    def add_product(self): ...
    
    # Métodos específicos de categorías
    def get_categories(self): ...
    def add_category(self): ...
    def remove_category(self): ...
    
    # Métodos específicos de favoritos
    def get_favorites(self): ...
    def add_favorite(self): ...
```

**Impacto:** Si agregas una nueva entidad (ej: `users`), tendrías que modificar `DatabaseConnection`.

### 4. **Acoplamiento Alto**
Los endpoints tenían la lógica de negocio mezclada con la lógica de acceso a datos:

```python
class ProductsResource(Resource):
    def __init__(self):
        self.db = DatabaseConnection('db.json')
        self.db.connect()
        self.products = self.db.get_products()  # Acceso directo a BD
    
    def get(self):
        # Lógica de autenticación + Lógica de filtrado + Acceso a datos
        # Todo mezclado en un solo método
```

### 5. **Múltiples Instancias de Conexión**
Cada endpoint creaba su propia instancia de `DatabaseConnection`:

```python
# products.py
self.db = DatabaseConnection('db.json')

# categories.py  
self.db = DatabaseConnection('db.json')

# favorites.py
self.db = DatabaseConnection('favorites.json')  # ¡Archivo incorrecto!
```

**Impacto:** Inconsistencia de datos, mayor uso de memoria.

### 6. **Función `is_valid_token` Duplicada**
La misma función definida en 3 archivos diferentes:

```python
# products.py, categories.py, favorites.py
def is_valid_token(token):
    return token == 'abcd1234'
```

### 7. **Imports No Utilizados y Código Muerto**
```python
# categories.py
from flask import Flask, request  # Flask no se usa aquí
import json  # No se usa

print("*****", args)  # Print de debug olvidado
```

### 8. **Generación de IDs Incorrecta**
```python
new_product = {
    'id': len(self.products) + 1,  # Puede generar IDs duplicados si se eliminan elementos
    ...
}
```

---

## Soluciones Aplicadas

### 1. **Configuración Centralizada**
Creé `config/settings.py` para centralizar todas las constantes:

```python
# config/settings.py
DATABASE_FILE = 'db.json'
VALID_TOKEN = 'abcd1234'
AUTH_USERNAME = 'student'
AUTH_PASSWORD = 'desingp'

ERROR_MESSAGES = {
    'token_not_found': 'Unauthorized: access token not found',
    'invalid_token': 'Unauthorized: invalid token',
    ...
}
```

**Beneficio:** Un solo lugar para modificar configuraciones.

### 2. **Decorador para Autenticación**
Creé `utils/auth_decorator.py` que elimina la duplicación:

```python
# Antes (repetido en cada método):
def get(self):
    token = request.headers.get('Authorization')
    if not token:
        return {'message': '...'}, 401
    if not is_valid_token(token):
        return {'message': '...'}, 401
    # lógica real

# Después (limpio y enfocado):
@require_auth
def get(self):
    # Solo la lógica real
```

### 3. **DatabaseConnection con Responsabilidad Única**
Simplifiqué la clase para que solo maneje operaciones genéricas:

```python
# Antes: métodos específicos para cada entidad
def get_products(self): ...
def get_categories(self): ...
def get_favorites(self): ...

# Después: métodos genéricos
def get_collection(self, collection_name): ...
def save_collection(self, collection_name, items): ...
```

**Beneficio:** Si agregas `users`, no necesitas tocar `DatabaseConnection`.

### 4. **Patrón Repository con Herencia**
Creé una capa de repositorios donde la lógica común está en la clase base:

```python
class BaseRepository:
    COLLECTION_NAME = None  # Cada hijo define su colección
    
    def get_all(self):
        return self.db.get_collection(self.COLLECTION_NAME)
    
    def _save_all(self, items):
        self.db.save_collection(self.COLLECTION_NAME, items)

class ProductRepository(BaseRepository):
    COLLECTION_NAME = 'products'
    
    # Solo métodos específicos de productos
    def get_by_category(self, category): ...
```

### 5. **Generación de IDs Robusta**
```python
# base_repository.py
def _generate_id(self):
    items = self.get_all()
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1
```

---

## Patrones de Diseño Utilizados

### 1. **Singleton Pattern** 
📍 Ubicación: `utils/database_connection.py`

**Problema que resuelve:** Múltiples instancias de conexión a BD.

**Cómo funciona:**
```
Primera llamada: DatabaseConnection('db.json')
    → Crea nueva instancia
    → La guarda en _instances['db.json']

Segunda llamada: DatabaseConnection('db.json')
    → Detecta que ya existe en _instances
    → Retorna la instancia existente
```

```python
class DatabaseConnection:
    _instances = {}
    
    def __new__(cls, json_file_path):
        if json_file_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[json_file_path] = instance
        return cls._instances[json_file_path]
```

### 2. **Decorator Pattern**
📍 Ubicación: `utils/auth_decorator.py`

**Problema que resuelve:** Código de autenticación duplicado.

**Cómo funciona:**
```python
@require_auth  # ← El decorador envuelve la función
def get(self):
    return self.repository.get_all()

# Internamente equivale a:
def get(self):
    # 1. Verificar token (insertado por el decorador)
    # 2. Si es válido, ejecutar la función original
    return self.repository.get_all()
```

### 3. **Repository Pattern**
📍 Ubicación: `repositories/`

**Problema que resuelve:** Lógica de acceso a datos mezclada con lógica de negocio.

**Estructura:**
```
BaseRepository (clase base con métodos comunes)
    ├── ProductRepository  (COLLECTION_NAME = 'products')
    ├── CategoryRepository (COLLECTION_NAME = 'categories')
    └── FavoriteRepository (COLLECTION_NAME = 'favorites')
```

**Beneficios:**
- Endpoints más limpios
- Fácil de probar (mock de repositorios)
- Cambiar la fuente de datos sin modificar endpoints
- Agregar nuevas entidades es trivial

### 4. **Template Method Pattern**
📍 Ubicación: `repositories/base_repository.py`

**Problema que resuelve:** Código común en todos los repositorios.

**Cómo funciona:**
```python
class BaseRepository:
    COLLECTION_NAME = None  # "Hook" - cada hijo lo define
    
    def get_all(self):  # Método template
        return self.db.get_collection(self.COLLECTION_NAME)
    
    def get_by_id(self, item_id):  # Método template
        items = self.get_all()
        return next((item for item in items if item.get('id') == item_id), None)

class ProductRepository(BaseRepository):
    COLLECTION_NAME = 'products'  # Solo define el "hook"
    # Hereda get_all() y get_by_id() automáticamente
```

---

## Principios SOLID Aplicados

### S - Single Responsibility Principle (SRP)
**Cada clase tiene una sola razón para cambiar:**

| Clase | Responsabilidad Única |
|-------|----------------------|
| `DatabaseConnection` | Leer/escribir el archivo JSON |
| `BaseRepository` | Operaciones CRUD genéricas |
| `ProductRepository` | Lógica específica de productos |
| `AuthDecorator` | Validar autenticación |
| `ProductsResource` | Manejar requests HTTP de productos |

### O - Open/Closed Principle (OCP)
**Abierto para extensión, cerrado para modificación:**

```python
# Para agregar una nueva entidad (ej: Users), NO modificas código existente:

class UserRepository(BaseRepository):
    COLLECTION_NAME = 'users'
    
    def get_by_email(self, email):
        users = self.get_all()
        return next((u for u in users if u['email'] == email), None)
```

### D - Dependency Inversion Principle (DIP)
**Depender de abstracciones, no de implementaciones:**

```python
class ProductsResource(Resource):
    def __init__(self):
        db = DatabaseConnection(DATABASE_FILE)
        self.repository = ProductRepository(db)  # Inyección de dependencia
```

---

## Estructura del Proyecto

### Antes (Código Original)
```
codigo_original/
├── app.py
├── db.json
├── endpoints/
│   ├── auth.py
│   ├── categories.py
│   ├── favorites.py
│   └── products.py
└── utils/
    └── database_connection.py   # 130+ líneas, conoce todas las entidades
```

### Después (Código Refactorizado)
```
codigo_refactorizado/
├── app.py                      # Punto de entrada limpio
├── db.json
├── config/                     # 🆕 Configuración centralizada
│   ├── __init__.py
│   └── settings.py
├── endpoints/
│   ├── __init__.py
│   ├── auth.py                 # Usa constantes de config
│   ├── categories.py           # Usa @require_auth y repositorio
│   ├── favorites.py            # Usa @require_auth y repositorio
│   └── products.py             # Usa @require_auth y repositorio
├── repositories/               # 🆕 Capa de acceso a datos
│   ├── __init__.py
│   ├── base_repository.py      # Operaciones CRUD genéricas
│   ├── category_repository.py  # Solo lógica de categorías
│   ├── favorite_repository.py  # Solo lógica de favoritos
│   └── product_repository.py   # Solo lógica de productos
└── utils/
    ├── __init__.py
    ├── auth_decorator.py       # 🆕 Decorador de autenticación
    └── database_connection.py  # ~70 líneas, solo operaciones genéricas
```

---

## Decisiones de Diseño

### 1. ¿Por qué Singleton y no Dependency Injection completo?
Para mantener la simplicidad. Un contenedor de DI completo (como `injector` o `dependency-injector`) agregaría complejidad innecesaria para este proyecto pequeño.

### 2. ¿Por qué no usar un ORM?
El proyecto usa archivos JSON. Agregar un ORM como SQLAlchemy cambiaría significativamente la arquitectura y está fuera del alcance de este refactor.

### 3. ¿Por qué `DatabaseConnection` solo tiene métodos genéricos?
**Principio de Responsabilidad Única (SRP):** La conexión no debería saber qué entidades existen. Si agregas `users`, no deberías modificar la clase de conexión.

### 4. ¿Por qué usar herencia en los repositorios?
Para aplicar el **patrón Template Method**: la lógica común (get_all, get_by_id, add, _generate_id) está en la clase base, y cada repositorio hijo solo define su `COLLECTION_NAME` y métodos específicos.

### 5. ¿Por qué unifiqué todo en `db.json`?
El código original tenía inconsistencia: `favorites.py` apuntaba a `favorites.json` que no existía. Unifiqué todo en un solo archivo por simplicidad.

---

## Diagramas

### Arquitectura por Capas

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      ENDPOINTS (Flask)                      │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐   │
│  │  /auth   │ │/products │ │/categories│ │  /favorites  │   │
│  └──────────┘ └──────────┘ └───────────┘ └──────────────┘   │
│                       │            │              │         │
│                 ┌─────┴────────────┴──────────────┘───┐     │
│                 │  @require_auth (Decorator Pattern)  │     │
│                 └─────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 REPOSITORIES (Repository Pattern)           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              BaseRepository                            │ │
│  │   get_all() | get_by_id() | add() | _generate_id()     │ │
│  └────────────────────────────────────────────────────────┘ │
│             ▲                ▲                 ▲            │
│             │                │                 │            │
│       ┌─────┴─────┐   ┌──────┴──────┐   ┌──────┴──────┐     │
│       │ Product   │   │  Category   │   │  Favorite   │     │
│       │ Repository│   │  Repository │   │  Repository │     │
│       └───────────┘   └─────────────┘   └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           DATABASE CONNECTION (Singleton Pattern)           │
│                                                             │
│   get_collection(name)  |  save_collection(name, items)     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         db.json                             │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de una Petición GET /products

```
┌────────┐     ┌───────────────┐     ┌─────────────┐     ┌────────────┐     ┌──────┐
│ Cliente│     │ @require_auth │     │  Endpoint   │     │ Repository │     │  DB  │
└───┬────┘     └───────┬───────┘     └──────┬──────┘     └──────┬─────┘     └──┬───┘
    │                  │                    │                   │              │
    │ GET /products    │                    │                   │              │
    │ ────────────────>│                    │                   │              │
    │                  │                    │                   │              │
    │                  │ ¿Token válido?     │                   │              │
    │                  │ ──────────────────>│                   │              │
    │                  │                    │                   │              │
    │                  │ [Sí, continuar]    │                   │              │
    │                  │ <──────────────────│                   │              │
    │                  │                    │                   │              │
    │                  │      get_all()     │                   │              │
    │                  │ ──────────────────────────────────────>│              │
    │                  │                    │                   │              │
    │                  │                    │   get_collection  │              │
    │                  │                    │   ('products')    │              │
    │                  │                    │ ─────────────────────────────────>
    │                  │                    │                   │              │
    │                  │                    │                   │   [data]     │
    │                  │                    │ <─────────────────────────────────
    │                  │                    │                   │              │
    │                  │    [productos]     │                   │              │
    │ <──────────────────────────────────────                   │              │
    │                  │                    │                   │              │
```

### Patrón Singleton

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DatabaseConnection                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  _instances = {                                                    │ │
│  │      'db.json': <DatabaseConnection object at 0x...>               │ │
│  │  }                                                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
    ┌──────┴─────┐       ┌──────┴─────┐       ┌──────┴─────┐
    │ Product    │       │ Category   │       │ Favorite   │
    │ Repository │       │ Repository │       │ Repository │
    └────────────┘       └────────────┘       └────────────┘
    
    Todos obtienen la MISMA instancia de conexión
```

---

## Conclusiones

### Mejoras Logradas:
1. **Principio SRP:** Cada clase tiene una sola responsabilidad
2. **Principio DRY:** Eliminada duplicación de código
3. **Principio OCP:** Fácil agregar nuevas entidades sin modificar código existente
4. **Código más legible:** Endpoints enfocados solo en HTTP
5. **Mejor testabilidad:** Repositorios pueden ser mockeados
6. **Configuración centralizada:** Un solo lugar para cambiar valores

### Posibles Mejoras Futuras:
- Agregar validación de esquemas con `marshmallow` o `pydantic`
- Implementar manejo de errores centralizado con excepciones personalizadas
- Agregar logging
- Migrar a una base de datos real (SQLite/PostgreSQL)
- Implementar tests unitarios
