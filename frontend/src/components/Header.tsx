import React, { useState } from 'react';
import { Plus, RefreshCw, Clock, Bell, CheckCheck, X, Menu, Atom } from 'lucide-react';
import { Activity } from '../types';

interface HeaderProps {
  title: string;
  onAddUrlClick: () => void;
  onRefreshClick: () => void;
  isRefreshing?: boolean;
  activities?: Activity[];
  onMarkRead?: (id: number) => void;
  onMarkAllRead?: () => void;
  onToggleMobileNav?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  onAddUrlClick,
  onRefreshClick,
  isRefreshing = false,
  activities = [],
  onMarkRead,
  onMarkAllRead,
  onToggleMobileNav
}) => {
  const [isBellOpen, setIsBellOpen] = useState(false);
  const unreadCount = activities.filter((a) => !a.is_read).length;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 px-3.5 sm:px-6 py-3 sm:py-4 shadow-xs">
      <div className="flex items-center justify-between gap-2 sm:gap-4">
        
        {/* Left: Mobile Menu Button + Title */}
        <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
          {/* Hamburger button for mobile screens (< 768px) */}
          <button
            onClick={onToggleMobileNav}
            className="md:hidden p-2 -ml-1 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors shrink-0 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
            aria-label="Toggle navigation menu"
            title="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="min-w-0">
            <h2 className="text-base sm:text-xl font-bold text-slate-800 tracking-tight truncate">
              {title}
            </h2>
            <p className="text-[11px] sm:text-xs text-slate-500 flex items-center gap-1 sm:gap-1.5 mt-0.5 truncate">
              <Clock className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-400 shrink-0" />
              <span className="truncate">
                Verified: <strong className="text-slate-700">09 Oct 2026</strong> (IST)
              </span>
            </p>
          </div>
        </div>

        {/* Right: Actions (Notification, Refresh, Add URL) */}
        <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
          
          {/* Notification Bell Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsBellOpen(!isBellOpen)}
              className="p-2 sm:p-2.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 relative transition-colors focus:outline-hidden focus:ring-2 focus:ring-sky-500"
              title="In-Website Notifications"
              aria-label={`Notifications (${unreadCount} unread)`}
              aria-expanded={isBellOpen}
            >
              <Bell className="w-4 h-4 text-slate-600" />
              {unreadCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-rose-500 text-white font-bold text-[9px] sm:text-[10px] flex items-center justify-center animate-pulse shadow-xs">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Bell Dropdown Popup (Responsive width constrained to viewport) */}
            {isBellOpen && (
              <div className="fixed sm:absolute inset-x-2 top-16 sm:inset-x-auto sm:right-0 sm:top-auto sm:mt-2 w-auto sm:w-96 max-w-[calc(100vw-1rem)] sm:max-w-md bg-white rounded-2xl border border-slate-200 shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
                <div className="p-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-sky-600" />
                    <span className="font-bold text-xs text-slate-900">Notifications ({unreadCount} unread)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {unreadCount > 0 && onMarkAllRead && (
                      <button
                        onClick={onMarkAllRead}
                        className="text-[11px] font-semibold text-sky-600 hover:text-sky-800"
                      >
                        Mark all read
                      </button>
                    )}
                    <button
                      onClick={() => setIsBellOpen(false)}
                      className="p-1 text-slate-400 hover:text-slate-600 rounded-md"
                      aria-label="Close notifications"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="max-h-72 overflow-y-auto divide-y divide-slate-100">
                  {activities.length === 0 ? (
                    <div className="p-6 text-center text-xs text-slate-400">No notifications</div>
                  ) : (
                    activities.slice(0, 10).map((act) => (
                      <div
                        key={act.id}
                        className={`p-3 text-xs flex items-start justify-between gap-2 ${
                          act.is_read ? 'bg-white' : 'bg-sky-50/50 font-medium'
                        }`}
                      >
                        <div className="min-w-0 flex-1">
                          <h4 className="font-bold text-slate-900 line-clamp-1">{act.title}</h4>
                          <p className="text-slate-600 mt-0.5 leading-tight line-clamp-2">{act.message}</p>
                        </div>
                        {!act.is_read && onMarkRead && (
                          <button
                            onClick={() => onMarkRead(act.id)}
                            className="shrink-0 text-[10px] font-bold text-sky-600 hover:underline px-1 py-0.5"
                          >
                            Read
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Global Refresh Button */}
          <button
            onClick={onRefreshClick}
            disabled={isRefreshing}
            className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
            title="Re-scrape and verify BRNS research portal"
            aria-label="Refresh BRNS Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0 ${isRefreshing ? 'animate-spin text-sky-600' : 'text-slate-500'}`} />
            <span className="hidden sm:inline">{isRefreshing ? 'Scraping...' : 'Refresh BRNS'}</span>
            <span className="sm:hidden">{isRefreshing ? '...' : 'Refresh'}</span>
          </button>

          {/* Add URL Primary Action */}
          <button
            onClick={onAddUrlClick}
            className="inline-flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold bg-sky-600 text-white hover:bg-sky-700 transition-colors shadow-sm shadow-sky-600/20"
            title="Register a new website URL source"
          >
            <Plus className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
            <span className="hidden xs:inline">+ Add URL</span>
            <span className="xs:hidden">+ Add</span>
          </button>

        </div>
      </div>
    </header>
  );
};

