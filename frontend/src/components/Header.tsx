import React, { useState } from 'react';
import { Plus, RefreshCw, Clock, Bell, CheckCheck, X } from 'lucide-react';
import { Activity } from '../types';

interface HeaderProps {
  title: string;
  onAddUrlClick: () => void;
  onRefreshClick: () => void;
  isRefreshing?: boolean;
  activities?: Activity[];
  onMarkRead?: (id: number) => void;
  onMarkAllRead?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  onAddUrlClick,
  onRefreshClick,
  isRefreshing = false,
  activities = [],
  onMarkRead,
  onMarkAllRead
}) => {
  const [isBellOpen, setIsBellOpen] = useState(false);
  const unreadCount = activities.filter((a) => !a.is_read).length;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-20 px-6 py-4 flex items-center justify-between shadow-xs">
      <div>
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h2>
        <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Verified Timestamp: <strong className="text-slate-700">09 Oct 2026</strong> (Asia/Kolkata)</span>
        </p>
      </div>

      <div className="flex items-center gap-3 relative">
        
        {/* Notification Bell Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsBellOpen(!isBellOpen)}
            className="p-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 relative transition-colors"
            title="In-Website Notifications"
          >
            <Bell className="w-4 h-4 text-slate-600" />
            {unreadCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-rose-500 text-white font-bold text-[10px] flex items-center justify-center animate-pulse shadow-xs">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Bell Dropdown Popup */}
          {isBellOpen && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl border border-slate-200 shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
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
                  <button onClick={() => setIsBellOpen(false)} className="text-slate-400 hover:text-slate-600">
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
                      <div>
                        <h4 className="font-bold text-slate-900">{act.title}</h4>
                        <p className="text-slate-600 mt-0.5 leading-tight">{act.message}</p>
                      </div>
                      {!act.is_read && onMarkRead && (
                        <button
                          onClick={() => onMarkRead(act.id)}
                          className="shrink-0 text-[10px] font-bold text-sky-600 hover:underline"
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
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-sky-600' : 'text-slate-500'}`} />
          <span>{isRefreshing ? 'Scraping...' : 'Refresh BRNS Data'}</span>
        </button>

        {/* Add URL Primary Action */}
        <button
          onClick={onAddUrlClick}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-sky-600 text-white hover:bg-sky-700 transition-colors shadow-sm shadow-sky-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add URL</span>
        </button>
      </div>
    </header>
  );
};
