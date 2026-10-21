import React from 'react';
import { 
  Bell, 
  Sparkles, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  HelpCircle, 
  CheckCheck,
  Calendar
} from 'lucide-react';
import { Activity } from '../types';

interface ActivityPanelProps {
  activities: Activity[];
  onMarkRead: (id: number) => void;
  onMarkAllRead: () => void;
}

export const ActivityPanel: React.FC<ActivityPanelProps> = ({
  activities,
  onMarkRead,
  onMarkAllRead
}) => {
  const getEventBadge = (type: string) => {
    switch (type) {
      case 'NEW_OPPORTUNITY':
        return {
          icon: Sparkles,
          label: 'New Opportunity',
          color: 'text-sky-700 bg-sky-50 border-sky-200'
        };
      case 'DEADLINE_CHANGED':
        return {
          icon: Clock,
          label: 'Deadline Changed',
          color: 'text-amber-700 bg-amber-50 border-amber-200'
        };
      case 'EXTENSION_VERIFIED':
        return {
          icon: Calendar,
          label: 'Extension Verified',
          color: 'text-indigo-700 bg-indigo-50 border-indigo-200'
        };
      case 'SCRAPE_SUCCESS':
        return {
          icon: CheckCircle2,
          label: 'Scrape Success',
          color: 'text-emerald-700 bg-emerald-50 border-emerald-200'
        };
      case 'SCRAPE_FAILED':
        return {
          icon: XCircle,
          label: 'Scrape Failed',
          color: 'text-rose-700 bg-rose-50 border-rose-200'
        };
      case 'CONFIG_REQUIRED':
        return {
          icon: AlertTriangle,
          label: 'Scraper Needed',
          color: 'text-orange-700 bg-orange-50 border-orange-200'
        };
      default:
        return {
          icon: HelpCircle,
          label: 'System Activity',
          color: 'text-slate-700 bg-slate-50 border-slate-200'
        };
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const unreadCount = activities.filter((a) => !a.is_read).length;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-sky-100 text-sky-700 rounded-lg">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm">In-Website Activity & Event Log</h3>
            <p className="text-[11px] text-slate-500">Live system updates, opportunity changes, and status alerts</p>
          </div>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={onMarkAllRead}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200 transition-colors"
          >
            <CheckCheck className="w-3.5 h-3.5" />
            <span>Mark All as Read ({unreadCount})</span>
          </button>
        )}
      </div>

      {/* Activity List */}
      <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No in-website activity notifications logged yet.
          </div>
        ) : (
          activities.map((act) => {
            const badge = getEventBadge(act.event_type);
            const Icon = badge.icon;
            return (
              <div
                key={act.id}
                className={`p-3.5 flex items-start gap-3 transition-colors ${
                  act.is_read ? 'bg-white' : 'bg-sky-50/40 font-medium'
                }`}
              >
                <div className={`p-2 rounded-lg border shrink-0 ${badge.color}`}>
                  <Icon className="w-4 h-4" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`inline-block px-2 py-0.5 text-[10px] font-bold rounded-md uppercase border ${badge.color}`}>
                      {badge.label}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {formatDate(act.created_at)}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-slate-900 mt-1 line-clamp-1">{act.title}</h4>
                  <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">{act.message}</p>
                </div>

                {!act.is_read && (
                  <button
                    onClick={() => onMarkRead(act.id)}
                    title="Mark as read"
                    className="shrink-0 text-xs text-sky-600 hover:text-sky-800 font-semibold px-2 py-1 rounded-md hover:bg-sky-100"
                  >
                    Mark read
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
