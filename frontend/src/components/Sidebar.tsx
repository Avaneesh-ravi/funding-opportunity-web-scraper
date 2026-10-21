import React from 'react';
import { 
  LayoutDashboard, 
  Award, 
  Globe, 
  History, 
  FileSpreadsheet, 
  Settings as SettingsIcon,
  Atom
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'opportunities', label: 'Funding Opportunities', icon: Award },
    { id: 'websites', label: 'Websites', icon: Globe },
    { id: 'history', label: 'Scraping History', icon: History },
    { id: 'export', label: 'Reports / Export', icon: FileSpreadsheet },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col min-h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-800/80">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
          <Atom className="w-6 h-6 animate-spin-slow" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-tight text-sm">BRNS Tracker</h1>
          <p className="text-xs text-sky-400 font-medium">Web Scraping Dashboard</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                  : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-400 space-y-2">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            System Live
          </span>
          <span className="text-[11px] text-slate-400 font-mono">v1.0.0</span>
        </div>
        <p className="text-[11px] text-slate-400">Timezone: Asia/Kolkata</p>
      </div>
    </aside>
  );
};
