// api.ts - conversa do app com o servidor
const BASE_URL = "https://SEU-SERVIDOR-RENDER.onrender.com";

export type LogEntry = {
  id?: string;
  message: string;
  level: string;
  created_at?: string;
};

export type Stats = {
  total_vendas: number;
  lucro_total: number;
  anuncios_ativos: number;
};

export async function api<T>(path: string, options: any = {}): Promise<T> {
  const res = await fetch(BASE_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (!res.ok) throw new Error("Erro no servidor: " + res.status);
  return res.json();
}
