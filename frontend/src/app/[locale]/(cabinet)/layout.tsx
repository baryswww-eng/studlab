import { CabinetShell } from "@/features/cabinet/cabinet-shell";

export default function CabinetLayout({ children }: LayoutProps<"/[locale]">) {
  return <CabinetShell>{children}</CabinetShell>;
}