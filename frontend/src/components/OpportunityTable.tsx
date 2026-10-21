import React, { useState } from 'react';
import { ExternalLink, FileText, RefreshCw, Eye, Search, Filter, ArrowUpDown } from 'lucide-react';
import { Opportunity } from '../types';
import { StatusBadge } from './StatusBadge';

interface OpportunityTableProps {
  opportunities: Opportunity[];
  onViewDetails: (opp: Opportunity) => void;
  onRefresh: (opp: Opportunity) => void;
  isLoading?: boolean;
}

export const OpportunityTable: React.FC<OpportunityTableProps> = ({
  opportunities,
  onViewDetails,
  onRefresh,
  isLoading = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState<'deadline' | 'announcement'>('deadline');

  // Filter logic
  const filtered = opportunities.filter((opp) => {
    const matchesSearch =
      opp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.funding_agency.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (opp.scheme_name && opp.scheme_name.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus =
      statusFilter === 'ALL' || opp.deadline_status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  // Sort logic
  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === 'deadline') {
      const dateA = a.current_deadline ? new Date(a.current_deadline).getTime() : 0;
      const dateB = b.current_deadline ? new Date(b.current_deadline).getTime() : 0;
      return dateA - dateB;
    } else {
      const dateA = a.announcement_date ? new Date(a.announcement_date).getTime() : 0;
      const dateB = b.announcement_date ? new Date(b.announcement_date).getTime() : 0;
      return dateB - dateA;
    }
  });

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

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Table Toolbar */}
      <div className="p-3.5 sm:p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2.5 sm:gap-3">
        <div className="relative w-full md:w-72 lg:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search title, agency, or scheme..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 sm:py-1.5 bg-white border border-slate-300 rounded-lg text-xs sm:text-sm focus:outline-hidden focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
        </div>

        <div className="flex flex-wrap sm:flex-nowrap items-center gap-2 w-full md:w-auto">
          <div className="flex items-center gap-1.5 flex-1 sm:flex-initial">
            <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full sm:w-auto bg-white border border-slate-300 rounded-lg text-xs sm:text-sm py-2 sm:py-1.5 px-2.5 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
              aria-label="Filter by status"
            >
              <option value="ALL">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Closing Soon">Closing Soon</option>
              <option value="Closed">Closed</option>
              <option value="Upcoming">Upcoming</option>
              <option value="Extended">Extended</option>
              <option value="Verification Required">Verification Required</option>
            </select>
          </div>

          <button
            onClick={() => setSortBy(sortBy === 'deadline' ? 'announcement' : 'deadline')}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-2 sm:py-1.5 bg-white border border-slate-300 rounded-lg text-xs sm:text-sm font-medium text-slate-700 hover:bg-slate-50 flex-1 sm:flex-initial"
            title="Toggle sort column"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="truncate">{sortBy === 'deadline' ? 'Nearest Deadline' : 'Latest Announced'}</span>
          </button>
        </div>
      </div>

      {/* ── Mobile Card Layout (< 768px) ─────────────────────────────────── */}
      <div className="md:hidden divide-y divide-slate-100">
        {sorted.length === 0 ? (
          <div className="py-8 px-4 text-center text-xs text-slate-500">
            {isLoading ? 'Loading opportunities...' : 'No matching opportunities found.'}
          </div>
        ) : (
          sorted.map((opp, index) => (
            <div key={opp.id} className="p-3.5 sm:p-4 space-y-3 hover:bg-slate-50/70 transition-colors">
              {/* Header: Agency & Status Badge */}
              <div className="flex items-start justify-between gap-2">
                <span className="inline-block text-[11px] font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-200 max-w-[65%] truncate">
                  {opp.funding_agency}
                </span>
                <StatusBadge status={opp.deadline_status} />
              </div>

              {/* Title & Scheme Name */}
              <div>
                <h4
                  onClick={() => onViewDetails(opp)}
                  className="font-bold text-slate-900 text-sm leading-snug cursor-pointer hover:text-sky-600 transition-colors line-clamp-2"
                >
                  {opp.title}
                </h4>
                {opp.scheme_name && (
                  <p className="text-xs text-sky-600 font-medium mt-0.5 line-clamp-1">{opp.scheme_name}</p>
                )}
              </div>

              {/* Dates Grid */}
              <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-200/80">
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Announced</span>
                  <span className="text-slate-700 font-medium text-xs">{formatDate(opp.announcement_date)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Last Date</span>
                  <span className="text-slate-900 font-bold text-xs">{formatDate(opp.current_deadline)}</span>
                </div>
              </div>

              {/* Footer: Timestamp and Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-100">
                <span className="text-[10px] text-slate-400 font-mono">
                  Checked: {formatDate(opp.last_verified_at)}
                </span>

                <div className="flex items-center gap-1.5 ml-auto">
                  <button
                    onClick={() => onViewDetails(opp)}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-sky-50 text-sky-700 hover:bg-sky-100 text-xs font-semibold border border-sky-200 transition-colors"
                    title="View Full Details"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Details</span>
                  </button>

                  <a
                    href={opp.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 border border-slate-200 transition-colors"
                    title="Open Source Portal"
                    aria-label="Open Source Portal"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>

                  {opp.document_url && (
                    <a
                      href={opp.document_url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1.5 rounded-lg text-indigo-600 hover:bg-indigo-50 border border-indigo-200 transition-colors"
                      title="View PDF Document"
                      aria-label="View PDF Document"
                    >
                      <FileText className="w-4 h-4" />
                    </a>
                  )}

                  <button
                    onClick={() => onRefresh(opp)}
                    className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 border border-slate-200 transition-colors"
                    title="Re-scrape Opportunity"
                    aria-label="Re-scrape Opportunity"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* ── Tablet & Desktop Table Layout (>= 768px) ──────────────────────── */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-100/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 w-12 text-center">S.No.</th>
              <th className="px-4 py-3 min-w-[130px]">Funding Agency</th>
              <th className="px-4 py-3 min-w-[240px]">Opportunity / Project Title</th>
              <th className="px-4 py-3 whitespace-nowrap">Announcement Date</th>
              <th className="px-4 py-3 whitespace-nowrap">Last Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 whitespace-nowrap">Last Checked</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  {isLoading ? 'Loading opportunities...' : 'No matching opportunities found.'}
                </td>
              </tr>
            ) : (
              sorted.map((opp, index) => (
                <tr key={opp.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-4 py-3.5 text-center font-medium text-slate-400">{index + 1}</td>
                  <td className="px-4 py-3.5 font-medium text-slate-900">{opp.funding_agency}</td>
                  <td className="px-4 py-3.5">
                    <div className="font-semibold text-slate-900 line-clamp-2">{opp.title}</div>
                    {opp.scheme_name && (
                      <div className="text-xs text-sky-600 mt-0.5">{opp.scheme_name}</div>
                    )}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap text-slate-600">
                    {formatDate(opp.announcement_date)}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap font-medium text-slate-900">
                    {formatDate(opp.current_deadline)}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <StatusBadge status={opp.deadline_status} />
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap text-xs text-slate-500">
                    {formatDate(opp.last_verified_at)}
                  </td>
                  <td className="px-4 py-3.5 text-right whitespace-nowrap">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onViewDetails(opp)}
                        title="View Details"
                        className="p-1.5 rounded-md text-sky-600 hover:bg-sky-50 transition-colors"
                        aria-label="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      <a
                        href={opp.source_url}
                        target="_blank"
                        rel="noreferrer"
                        title="Open Source URL"
                        className="p-1.5 rounded-md text-slate-600 hover:bg-slate-100 transition-colors"
                        aria-label="Open Source URL"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>

                      {opp.document_url && (
                        <a
                          href={opp.document_url}
                          target="_blank"
                          rel="noreferrer"
                          title="View Official PDF Document"
                          className="p-1.5 rounded-md text-indigo-600 hover:bg-indigo-50 transition-colors"
                          aria-label="View PDF Document"
                        >
                          <FileText className="w-4 h-4" />
                        </a>
                      )}

                      <button
                        onClick={() => onRefresh(opp)}
                        title="Re-scrape Source"
                        className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 transition-colors"
                        aria-label="Re-scrape Source"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
