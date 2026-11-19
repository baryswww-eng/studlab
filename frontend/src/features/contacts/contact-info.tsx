import { Mail, Phone, Send } from "lucide-react";
import Image from "next/image";
import { site } from "@/lib/site";
import { cn } from "@/lib/utils";

const linkClass =
  "inline-flex items-center gap-2 rounded text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

/** Phones (tel: links) and optional email. */
export function ContactList({ className }: { className?: string }) {
  return (
    <ul className={cn("flex flex-col gap-2", className)}>
      {site.phones.map((p) => (
        <li key={p.tel}>
          <a href={`tel:${p.tel}`} className={linkClass}>
            <Phone className="size-4 text-accent" aria-hidden="true" />
            {p.display}
          </a>
        </li>
      ))}
      {site.contactEmail && (
        <li>
          <a href={`mailto:${site.contactEmail}`} className={linkClass}>
            <Mail className="size-4 text-accent" aria-hidden="true" />
            {site.contactEmail}
          </a>
        </li>
      )}
    </ul>
  );
}

/** Social links; Telegram shows its handle and QR code. */
export function SocialList({ qrLabel, showQr = true }: { qrLabel: string; showQr?: boolean }) {
  return (
    <ul className="flex flex-col gap-3">
      {site.social.map((s) => (
        <li key={s.href} className="flex flex-col gap-2">
          <a href={s.href} target="_blank" rel="noopener noreferrer" className={linkClass}>
            <Send className="size-4 text-accent" aria-hidden="true" />
            {s.label}
            {s.handle && <span className="font-medium text-foreground">{s.handle}</span>}
          </a>
          {showQr && s.qr && (
            <a
              href={s.href}
              target="_blank"
              rel="noopener noreferrer"
              className="w-fit rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Image
                src={s.qr}
                alt={`${qrLabel}: ${s.label} ${s.handle ?? ""}`.trim()}
                width={112}
                height={118}
                className="rounded-xl"
              />
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}
