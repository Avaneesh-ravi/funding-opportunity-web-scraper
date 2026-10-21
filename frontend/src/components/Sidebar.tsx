import React, { useEffect } from 'react';
import { 
  LayoutDashboard, 
  Award, 
  Globe, 
  History, 
  FileSpreadsheet, 
  Settings as SettingsIcon,
  Atom,
  X
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  isOpen = false,
  onClose
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'opportunities', label: 'Funding Opportunities', icon: Award },
    { id: 'websites', label: 'Websites', icon: Globe },
    { id: 'history', label: 'Scraping History', icon: History },
    { id: 'export', label: 'Reports / Export', icon: FileSpreadsheet },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  // Lock body scroll and listen for Escape key when mobile drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape' && onClose) {
          onClose();
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => {
        document.body.style.overflow = '';
        window.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      document.body.style.overflow = '';
    }
  }, [isOpen, onClose]);

  const handleSelectTab = (tabId: string) => {
    setCurrentTab(tabId);
    if (onClose) {
      onClose();
    }
  };

  return (
    <>
      {/* ── Mobile Backdrop (under 768px) ─────────────────────────────────── */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-xs md:hidden transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* ── Mobile Drawer (under 768px) ───────────────────────────────────── */}
      <aside
        id="mobile-navigation"
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-slate-900 text-slate-300 flex flex-col min-h-screen border-r border-slate-800 shadow-2xl transition-transform duration-300 ease-in-out md:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        aria-label="Mobile Navigation"
        aria-hidden={!isOpen}
      >
        {/* Mobile Brand Header with Close button */}
        <div className="p-4 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 shrink-0">
              <Atom className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <h1 className="font-bold text-white tracking-tight text-sm">BRNS Tracker</h1>
              <p className="text-xs text-sky-400 font-medium">Web Scraping Dashboard</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mobile Navigation Links */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-lg text-sm font-medium transition-all duration-150 text-left ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                    : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Mobile Footer System Status */}
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

      {/* ── Tablet & Desktop Permanent Sidebar (768px and above) ──────────── */}
      <aside
        className="hidden md:flex flex-col md:w-20 lg:w-64 bg-slate-900 text-slate-300 min-h-screen border-r border-slate-800 shrink-0 transition-all duration-200"
        aria-label="Desktop Navigation"
      >
        {/* Brand Header */}
        <div className="p-4 lg:p-5 flex items-center md:justify-center lg:justify-start gap-3 border-b border-slate-800/80">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 shrink-0">
            <Atom className="w-6 h-6 animate-spin-slow" />
          </div>
          <div className="hidden lg:block overflow-hidden">
            <h1 className="font-bold text-white tracking-tight text-sm truncate">BRNS Tracker</h1>
            <p className="text-xs text-sky-400 font-medium truncate">Web Scraping Dashboard</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-2 lg:p-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                title={item.label}
                className={`w-full flex md:flex-col lg:flex-row items-center md:justify-center lg:justify-start gap-1.5 lg:gap-3 px-2 lg:px-3.5 py-2.5 rounded-lg text-xs lg:text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                    : 'hover:bg-slate-800/80 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-5 h-5 lg:w-4 lg:h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span className="md:text-[10px] lg:text-sm truncate text-center lg:text-left">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer System Status */}
        <div className="p-3 lg:p-4 border-t border-slate-800 text-xs text-slate-400 space-y-1 lg:space-y-2">
          <div className="flex md:flex-col lg:flex-row md:items-center lg:justify-between gap-1">
            <span className="flex items-center gap-1.5 text-[11px] lg:text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
              <span className="hidden lg:inline">System Live</span>
            </span>
            <span className="text-[10px] lg:text-[11px] text-slate-400 font-mono">v1.0.0</span>
          </div>
          <p className="hidden lg:block text-[11px] text-slate-400">Timezone: Asia/Kolkata</p>
        </div>
      </aside>
    </>
  );
};

