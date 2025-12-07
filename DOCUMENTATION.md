# Documentación del Módulo de Notificaciones

## ¿Qué hicimos?

Creamos un sistema de "Eventos". Básicamente, cuando pasa algo importante en la app (como crear un producto), se lanza un evento y los que estén interesados (suscriptores) reaccionan.

## Patrones de Diseño Aplicados

### 1. Observer Pattern

Es el corazón del módulo.

- **Quién es quién:**
  - El `EventManager` es el sujeto que vigila.
  - Los `Subscribers` (como `LogSubscriber`) son los observadores.
- **Para qué:** Para que cuando ocurra un evento, automáticamente se avise a todos los interesados sin que el código original sepa quiénes son.

### 2. Singleton Pattern
- **Dónde:** En la clase `EventManager`.
- **Para qué:** Necesitamos que haya UN SOLO gestor de eventos en toda la aplicación. Si tuviéramos varios, unos suscriptores se registrarían en uno y los eventos saldrían por otro. Con Singleton nos aseguramos que todos hablen con el mismo intermediario.

### 3. Strategy Pattern
- **Dónde:** En `notifications/strategies`.
- **Para qué:** Para definir diferentes formas de enviar notificaciones (por consola, por archivo, y en el futuro por email) y poder cambiarlas fácilmente sin tocar el código de los suscriptores.

## Estructura del Módulo

Todo está en la carpeta `notifications/`:

- **`event_manager.py`**: El cerebro. Aquí te suscribes y aquí se emiten los eventos.
- **`events/`**: Aquí definimos "qué pasó".
  - `ProductCreatedEvent`: Alguien creó un producto.
  - `FavoriteAddedEvent`: Alguien dio like a un producto.
- **`subscribers/`**: Aquí definimos "qué hacer".
  - `LogSubscriber`: Guarda un registro en `audit.log`.
  - `RecommendationSubscriber`: Simula guardar datos para un algoritmo de recomendaciones (guarda en `recommendations.json`).

## ¿Cómo funciona el flujo?

1.  **Configuración (`app.py`)**: Al arrancar la app, le decimos al `EventManager`: "Oye, cuando pase un `ProductCreatedEvent`, avísale al `LogSubscriber`".
2.  **Acción (`endpoints/products.py`)**: Un usuario crea un producto.
3.  **Emisión**: El endpoint crea el producto en la BD y luego dice: `event_manager.emit(ProductCreatedEvent(producto))`.
4.  **Reacción**: El `EventManager` busca quién estaba escuchando y ejecuta sus métodos `handle()`.

## ¿Por qué esto es mejor?

Antes, si queríamos agregar un log, teníamos que ir al archivo de productos y meter código. Si queríamos mandar un correo, otra vez a modificar el archivo de productos.

Ahora, el archivo de productos **solo crea productos**. Si mañana queremos mandar un WhatsApp cada vez que se crea un producto, solo creamos un `WhatsAppSubscriber` y lo conectamos en `app.py`. ¡No tocamos ni una línea del código de productos!

