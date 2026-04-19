CREATE TABLE messages (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title       text NOT NULL,
  body        text NOT NULL CHECK (char_length(body) <= 200),
  printed     boolean NOT NULL DEFAULT false,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_messages_printed ON messages (printed) WHERE printed = false;

-- Habilitar RLS
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Cualquiera puede insertar (formulario web con anon key)
CREATE POLICY "anon puede insertar"
  ON messages FOR INSERT
  TO anon
  WITH CHECK (true);

-- service_role bypasea RLS automáticamente (el script Python puede leer/actualizar sin política extra)
