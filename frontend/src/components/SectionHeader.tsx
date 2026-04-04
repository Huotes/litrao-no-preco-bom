import Link from "next/link";

interface SectionHeaderProps {
  title: string;
  emoji?: string;
  href?: string;
  linkText?: string;
}

export function SectionHeader({ title, emoji, href, linkText = "Ver tudo" }: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <h2 className="section-title">
        {emoji && <span className="mr-1.5">{emoji}</span>}
        {title}
      </h2>
      {href && (
        <Link href={href} className="text-xs font-medium text-brand-teal hover:underline">
          {linkText} →
        </Link>
      )}
    </div>
  );
}
