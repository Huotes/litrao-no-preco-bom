interface ProductImageProps {
  src: string | null;
  alt: string;
  size?: "sm" | "lg";
}

const SIZE_CLASSES = {
  sm: "h-20 w-20",
  lg: "h-48 w-48",
} as const;

export function ProductImage({ src, alt, size = "sm" }: ProductImageProps) {
  if (!src) return null;

  return (
    <div className={`${SIZE_CLASSES[size]} flex-shrink-0 overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center`}>
      <img
        src={src}
        alt={alt}
        className="max-h-full max-w-full object-contain"
      />
    </div>
  );
}
