"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { formatarPreco } from "@/lib/format";

interface PriceSliderProps {
  min?: number;
  max?: number;
  value: [number, number];
  onChange: (range: [number, number]) => void;
}

export function PriceSlider({ min = 0, max = 200, value, onChange }: PriceSliderProps) {
  const [local, setLocal] = useState(value);
  const trackRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef<"min" | "max" | null>(null);

  useEffect(() => { setLocal(value); }, [value]);

  const pctMin = ((local[0] - min) / (max - min)) * 100;
  const pctMax = ((local[1] - min) / (max - min)) * 100;

  const handlePointer = useCallback(
    (e: React.PointerEvent) => {
      if (!draggingRef.current || !trackRef.current) return;
      const rect = trackRef.current.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const val = Math.round(min + pct * (max - min));

      setLocal((prev) => {
        const next: [number, number] =
          draggingRef.current === "min"
            ? [Math.min(val, prev[1] - 1), prev[1]]
            : [prev[0], Math.max(val, prev[0] + 1)];
        return next;
      });
    },
    [min, max]
  );

  const stopDrag = useCallback(() => {
    if (draggingRef.current) {
      draggingRef.current = null;
      onChange(local);
    }
  }, [local, onChange]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs font-medium text-gray-500">
        <span>{formatarPreco(local[0])}</span>
        <span>{formatarPreco(local[1])}</span>
      </div>

      <div
        ref={trackRef}
        className="relative h-6 flex items-center cursor-pointer touch-none"
        onPointerMove={handlePointer}
        onPointerUp={stopDrag}
        onPointerLeave={stopDrag}
      >
        {/* Track background */}
        <div className="absolute inset-x-0 h-1.5 bg-gray-200 rounded-full" />
        {/* Active range */}
        <div
          className="absolute h-1.5 bg-brand-teal rounded-full"
          style={{ left: `${pctMin}%`, right: `${100 - pctMax}%` }}
        />

        {/* Min thumb */}
        <div
          className="absolute w-5 h-5 bg-white border-2 border-brand-teal rounded-full shadow-md cursor-grab active:cursor-grabbing active:scale-110 transition-transform -translate-x-1/2"
          style={{ left: `${pctMin}%` }}
          onPointerDown={(e) => {
            draggingRef.current = "min";
            (e.target as HTMLElement).setPointerCapture(e.pointerId);
          }}
        />

        {/* Max thumb */}
        <div
          className="absolute w-5 h-5 bg-white border-2 border-brand-teal rounded-full shadow-md cursor-grab active:cursor-grabbing active:scale-110 transition-transform -translate-x-1/2"
          style={{ left: `${pctMax}%` }}
          onPointerDown={(e) => {
            draggingRef.current = "max";
            (e.target as HTMLElement).setPointerCapture(e.pointerId);
          }}
        />
      </div>

      {/* Quick presets */}
      <div className="flex gap-1.5 flex-wrap">
        {[
          { label: "Até R$10", range: [0, 10] as [number, number] },
          { label: "R$10–50", range: [10, 50] as [number, number] },
          { label: "R$50–100", range: [50, 100] as [number, number] },
          { label: "R$100+", range: [100, max] as [number, number] },
        ].map((preset) => (
          <button
            key={preset.label}
            onClick={() => { setLocal(preset.range); onChange(preset.range); }}
            className={`chip text-[11px] ${
              local[0] === preset.range[0] && local[1] === preset.range[1]
                ? "chip-active"
                : "chip-inactive"
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>
    </div>
  );
}
