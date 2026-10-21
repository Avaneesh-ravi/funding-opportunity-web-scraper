import React from 'react';
import { Clock, AlertTriangle, CheckCircle, XCircle, Calendar, HelpCircle, ArrowUpRight } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  switch (status) {
    case 'Open':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 ${className}`}>
          <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
          <span>Open</span>
        </span>
      );
    case 'Closing Soon':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-300 animate-pulse ${className}`}>
          <Clock className="w-3.5 h-3.5 text-amber-600" />
          <span>Closing Soon</span>
        </span>
      );
    case 'Closed':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 ${className}`}>
          <XCircle className="w-3.5 h-3.5 text-rose-600" />
          <span>Closed / Deadline Passed</span>
        </span>
      );
    case 'Upcoming':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 ${className}`}>
          <Calendar className="w-3.5 h-3.5 text-sky-600" />
          <span>Upcoming</span>
        </span>
      );
    case 'Extended':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 ${className}`}>
          <ArrowUpRight className="w-3.5 h-3.5 text-indigo-600" />
          <span>Extended</span>
        </span>
      );
    case 'Verification Required':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200 ${className}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-orange-600" />
          <span>Verification Required</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200 ${className}`}>
          <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          <span>{status || 'Unknown'}</span>
        </span>
      );
  }
};
