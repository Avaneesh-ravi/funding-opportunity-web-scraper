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
      <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search title, agency, or scheme..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-white border border-slate-300 rounded-lg text-sm py-1.5 px-3 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
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
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" />
            <span>Sort: {sortBy === 'deadline' ? 'Nearest Deadline' : 'Latest Announcement'}</span>
          </button>
        </div>
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-100/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 w-12 text-center">S.No.</th>
              <th className="px-4 py-3 min-w-[140px]">Funding Agency</th>
              <th className="px-4 py-3 min-w-[260px]">Opportunity / Project Title</th>
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
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      <a
                        href={opp.source_url}
                        target="_blank"
                        rel="noreferrer"
                        title="Open Source URL"
                        className="p-1.5 rounded-md text-slate-600 hover:bg-slate-100 transition-colors"
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
                        >
                          <FileText className="w-4 h-4" />
                        </a>
                      )}

                      <button
                        onClick={() => onRefresh(opp)}
                        title="Re-scrape Source"
                        className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 transition-colors"
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
