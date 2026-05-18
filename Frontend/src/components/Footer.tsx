import Link from "next/link";
import { Activity } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container mx-auto px-4 flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
        <div className="flex items-center gap-2 text-sm text-muted-foreground text-center md:text-left">
          <Activity className="h-4 w-4" />
          <p>
            &copy; {new Date().getFullYear()} HelloHealth. For educational purposes only.
          </p>
        </div>
        <div className="flex gap-4 text-sm font-medium text-muted-foreground">
          <Link href="#" className="hover:underline underline-offset-4">Terms</Link>
          <Link href="#" className="hover:underline underline-offset-4">Privacy</Link>
          <Link href="#" className="hover:underline underline-offset-4">Contact</Link>
        </div>
      </div>
    </footer>
  );
}
