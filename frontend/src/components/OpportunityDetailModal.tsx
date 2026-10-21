import React from 'react';
import { X, ExternalLink, FileText, RefreshCw, Calendar, Award, Building, BookOpen, Layers, ShieldCheck, History } from 'lucide-react';
import { Opportunity } from '../types';
import { StatusBadge } from './StatusBadge';

interface OpportunityDetailModalProps {
  opportunity: Opportunity | null;
  onClose: () => void;
  onRefresh: (opp: Opportunity) => void;
}

export const OpportunityDetailModal: React.FC<OpportunityDetailModalProps> = ({
  opportunity,
  onClose,
  onRefresh,
}) => {
  if (!opportunity) return null;

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Not specified';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4 md:p-6 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-opp-title"
    >
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-4xl w-[calc(100vw-24px)] sm:w-full max-h-[94vh] sm:max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-150">
        
        {/* Modal Header */}
        <div className="p-4 sm:p-6 border-b border-slate-200 bg-slate-50/80 flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className="text-[11px] sm:text-xs font-bold text-sky-700 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-md uppercase tracking-wider truncate">
                {opportunity.funding_agency}
              </span>
              <StatusBadge status={opportunity.deadline_status} />
            </div>
            <h3 id="modal-opp-title" className="text-base sm:text-xl font-bold text-slate-900 tracking-tight break-words">
              {opportunity.title}
            </h3>
            {opportunity.scheme_name && (
              <p className="text-xs text-slate-500 mt-1 break-words">Scheme / Call: {opportunity.scheme_name}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/50 transition-colors shrink-0"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body - 2 Column Layout on md+ */}
        <div className="p-4 sm:p-6 overflow-y-auto flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 text-sm text-slate-700">
          
          {/* Main Info Column (2 cols wide on desktop) */}
          <div className="md:col-span-2 space-y-6">
            
            {/* Description */}
            <div>
              <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                <BookOpen className="w-4 h-4 text-sky-600" />
                Description & Summary
              </h4>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 whitespace-pre-wrap text-slate-600 leading-relaxed text-xs">
                {opportunity.description || 'Not specified on source page.'}
              </div>
            </div>

            {/* Eligibility & Applicant Requirements */}
            <div>
              <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                <ShieldCheck className="w-4 h-4 text-sky-600" />
                Eligibility Criteria & PI Requirements
              </h4>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 text-slate-700 text-xs">
                {opportunity.eligibility || 'Not specified on source page.'}
              </div>
            </div>

            {/* Research Areas & Funding */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                  <Layers className="w-4 h-4 text-sky-600" />
                  Research Thrust Areas
                </h4>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
                  {opportunity.research_areas || 'Not specified'}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                  <Award className="w-4 h-4 text-sky-600" />
                  Funding & Duration
                </h4>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
                  <p><strong>Funding:</strong> {opportunity.funding_amount || 'Not specified'}</p>
                  <p><strong>Duration:</strong> {opportunity.project_duration || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Submission Instructions */}
            <div>
              <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                <Building className="w-4 h-4 text-sky-600" />
                Submission Procedure & Portal
              </h4>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 text-xs text-slate-700">
                {opportunity.submission_instructions || 'Submit via official BRNS GMS portal.'}
              </div>
            </div>

            {/* Field Changes History Audit Log */}
            {opportunity.history && opportunity.history.length > 0 && (
              <div>
                <h4 className="font-semibold text-slate-900 flex items-center gap-2 mb-2">
                  <History className="w-4 h-4 text-indigo-600" />
                  Audit History Log
                </h4>
                <div className="bg-indigo-50/50 p-3 rounded-xl border border-indigo-100 text-xs space-y-2">
                  {opportunity.history.map((h) => (
                    <div key={h.id} className="flex flex-col gap-0.5 border-b border-indigo-100/60 pb-1.5 last:border-none">
                      <div className="flex justify-between font-semibold text-indigo-900">
                        <span>Changed Field: {h.field_name}</span>
                        <span>{new Date(h.changed_at).toLocaleString('en-IN')}</span>
                      </div>
                      <p className="text-slate-600">
                        Old: <span className="line-through">{h.old_value || 'None'}</span> &rarr; New: <strong className="text-emerald-700">{h.new_value}</strong>
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Metadata Sidebar Column */}
          <div className="space-y-6 border-l border-slate-200 pl-0 md:pl-6">
            
            {/* Key Dates Box */}
            <div className="bg-sky-50/60 p-4 rounded-xl border border-sky-100 space-y-3">
              <h4 className="font-bold text-sky-900 flex items-center gap-2 text-xs uppercase tracking-wider">
                <Calendar className="w-4 h-4 text-sky-600" />
                Official Timeline
              </h4>
              
              <div className="text-xs space-y-2">
                <div>
                  <span className="text-slate-500 block">Announcement Date:</span>
                  <strong className="text-slate-800">{formatDate(opportunity.announcement_date)}</strong>
                </div>

                <div>
                  <span className="text-slate-500 block">Current Submission Deadline:</span>
                  <strong className="text-rose-700 text-sm block">{formatDate(opportunity.current_deadline)}</strong>
                </div>

                {opportunity.original_deadline && opportunity.original_deadline !== opportunity.current_deadline && (
                  <div>
                    <span className="text-slate-500 block">Original Deadline:</span>
                    <span className="text-slate-700 line-through">{formatDate(opportunity.original_deadline)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Links & Actions */}
            <div className="space-y-2.5">
              <h4 className="font-semibold text-slate-900 text-xs uppercase tracking-wider">
                Official Links
              </h4>
              
              <a
                href={opportunity.source_url}
                target="_blank"
                rel="noreferrer"
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs transition-colors shadow-xs"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Open Official Website</span>
              </a>

              {opportunity.document_url ? (
                <a
                  href={opportunity.document_url}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-colors shadow-xs"
                >
                  <FileText className="w-4 h-4" />
                  <span>View Official Detail Document</span>
                </a>
              ) : (
                <div className="text-xs text-slate-400 italic text-center py-2 bg-slate-100 rounded-lg">
                  No detail document link attached
                </div>
              )}

              {opportunity.application_url && (
                <a
                  href={opportunity.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium text-xs transition-colors"
                >
                  <span>Go to Application Portal</span>
                </a>
              )}

              <button
                onClick={() => onRefresh(opportunity)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium text-xs transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                <span>Re-scrape Data Now</span>
              </button>
            </div>

            {/* Audit Timestamps */}
            <div className="text-[11px] text-slate-400 space-y-1 pt-4 border-t border-slate-200">
              <p>First Seen: {formatDate(opportunity.first_seen_at)}</p>
              <p>Last Verified: {formatDate(opportunity.last_verified_at)}</p>
              <p className="font-mono truncate" title={opportunity.source_url}>
                URL: {opportunity.source_url}
              </p>
            </div>

          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900 transition-colors"
          >
            Close Panel
          </button>
        </div>

      </div>
    </div>
  );
};
