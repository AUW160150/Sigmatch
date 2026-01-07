import { NavLink, useLocation } from 'react-router-dom';
import { 
  Edit3, 
  MessageSquare, 
  ClipboardList, 
  BarChart3,
  Activity,
  Cog
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useApi } from '@/contexts/ApiContext';
import { SettingsModal } from '@/components/SettingsModal';

const navItems = [
  { path: '/', label: 'Configure', icon: Cog },
  { path: '/prompts', label: 'Adjust Prompts', icon: Edit3 },
  { path: '/evaluation', label: 'Evaluation Criteria', icon: MessageSquare },
  { path: '/review', label: 'Review Results', icon: ClipboardList },
  { path: '/results', label: 'Results Summary', icon: BarChart3 },
];

export function AppSidebar() {
  const location = useLocation();
  const { apiBase } = useApi();

  // Extract host from URL for display
  const displayUrl = (() => {
    try {
      const url = new URL(apiBase);
      return `${url.host}`;
    } catch {
      return apiBase;
    }
  })();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-sidebar text-sidebar-foreground">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary">
            <Activity className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Sigmatch</h1>
            <p className="text-xs text-sidebar-foreground/60">Trial Matching</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-primary'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-4 space-y-2">
          <SettingsModal />
          <p className="text-xs text-sidebar-foreground/50 truncate" title={apiBase}>
            Connected to {displayUrl}
          </p>
        </div>
      </div>
    </aside>
  );
}
