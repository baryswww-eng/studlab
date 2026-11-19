/**
 * Public site contacts. Defaults are the platform's own contacts; each value can
 * be overridden per deployment with NEXT_PUBLIC_* env vars.
 */
export interface SocialLink {
  label: string;
  href: string;
  handle?: string;
  qr?: string; // path to a QR image in /public
}

export interface Phone {
  display: string; // "+7 747 997 18 92"
  tel: string; // "+77479971892" for tel: links
}

function parsePhones(raw: string | undefined): Phone[] | null {
  // Format: "+7 747 997 18 92,+7 747 185 14 88"
  if (!raw) return null;
  return raw
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean)
    .map((display) => ({ display, tel: display.replace(/[^\d+]/g, "") }));
}

function parseSocial(raw: string | undefined): SocialLink[] | null {
  // Format: "Telegram|https://t.me/x,Instagram|https://instagram.com/x"
  if (!raw) return null;
  return raw
    .split(",")
    .map((pair) => pair.split("|").map((s) => s.trim()))
    .filter(([label, href]) => label && href?.startsWith("https://"))
    .map(([label, href]) => ({ label, href }));
}

const DEFAULT_PHONES: Phone[] = [
  { display: "+7 747 997 18 92", tel: "+77479971892" },
  { display: "+7 747 185 14 88", tel: "+77471851488" },
];

const DEFAULT_SOCIAL: SocialLink[] = [
  {
    label: "Telegram",
    href: "https://t.me/BARYS444",
    handle: "@BARYS444",
    qr: "/telegram-qr.png",
  },
];

export const site = {
  contactEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL || null,
  phones: parsePhones(process.env.NEXT_PUBLIC_CONTACT_PHONES) ?? DEFAULT_PHONES,
  social: parseSocial(process.env.NEXT_PUBLIC_SOCIAL_LINKS) ?? DEFAULT_SOCIAL,
};

export const mainNav = [
  { href: "/", key: "home" },
  { href: "/courses", key: "courses" },
  { href: "/ai-tutor", key: "ai" },
  { href: "/about", key: "about" },
] as const;
