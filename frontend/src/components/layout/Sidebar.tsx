"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  FlaskConical,
  BarChart3,
  GitCompare,
  Brain,
  Settings,
  Home,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/experiments", label: "Experiments", icon: FlaskConical },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/strategies", label: "Strategies", icon: Brain },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 flex-shrink-0 bg-card border-r flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b">
        <p className="font-bold text-sm">LLM-MemEval</p>
        <p className="text-xs text-muted-foreground">AI Forgetting Benchmark</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition",
                active
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t">
        <p className="text-xs text-muted-foreground">v0.1.0</p>
      </div>
    </aside>
  );
}
