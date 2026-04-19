# Remote Printing

Web pública → Supabase → script Python → impresora Mac.

---

## Setup

### 1. Crear tabla en Supabase

1. Abre Supabase → SQL Editor
2. Pega y ejecuta el contenido de `db/schema.sql`

### 2. Variables de entorno

Copia `.env.example` y rellena los valores:

```
Supabase → Settings → API
```

| Variable | Dónde usarla |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Next.js (frontend) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Next.js (frontend) — segura para exponer |
| `SUPABASE_SERVICE_ROLE_KEY` | Script Python ÚNICAMENTE — nunca en frontend |

### 3. Deploy en Vercel

```bash
cd web
npm install
```

En Vercel:
1. Importa el repositorio → selecciona `web/` como **Root Directory**
2. Añade en Environment Variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Deploy

### 4. Activar Row Level Security (Supabase)

En Supabase → Authentication → Policies, activa RLS en la tabla `messages` y añade:

- **INSERT** para `anon`: `true` (permite enviar mensajes desde la web)
- **SELECT / UPDATE** para `service_role`: ya está permitido por defecto

### 5. Script Python

```bash
# Instala dependencias (solo stdlib, sin pip necesario)
export SUPABASE_URL=https://xxxx.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=eyJ...

python3 scripts/print_messages.py
```

### 6. Cron en Mac (cada 3 horas)

```bash
# Abre el crontab
crontab -e
```

Añade esta línea (ajusta las rutas):

```
0 */3 * * * SUPABASE_URL=https://xxxx.supabase.co SUPABASE_SERVICE_ROLE_KEY=eyJ... /usr/bin/python3 /Users/TU_USUARIO/Documents/programming/remoteprinting/scripts/print_messages.py >> /Users/TU_USUARIO/Documents/programming/remoteprinting/scripts/print.log 2>&1
```

Para ver el log:
```bash
tail -f scripts/print.log
```

---

## Estructura

```
/web        → Next.js (Vercel)
/scripts    → Script Python de impresión
/db         → SQL schema
.env.example
README.md
```
