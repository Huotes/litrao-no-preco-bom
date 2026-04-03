import { useCallback, useEffect, useRef, useState } from "react";

import { buscarProdutos } from "@/lib/api";
import type { BuscaParams, PaginacaoResponse } from "@/types/produto";

const DEBOUNCE_MS = 400;

interface UseBuscaReturn {
  data: PaginacaoResponse | null;
  loading: boolean;
  error: string | null;
  buscar: (params: BuscaParams) => void;
}

export function useBusca(): UseBuscaReturn {
  const [data, setData] = useState<PaginacaoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const buscar = useCallback((params: BuscaParams) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await buscarProdutos(params);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    }, DEBOUNCE_MS);
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return { data, loading, error, buscar };
}
