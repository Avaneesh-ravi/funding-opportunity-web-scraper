import React from 'react';
import { StatCards } from '../components/StatCards';
import { OpportunityTable } from '../components/OpportunityTable';
import { ActivityPanel } from '../components/ActivityPanel';
import { Opportunity, Website, ScrapeRun, Activity } from '../types';
import { ArrowRight, FileSpreadsheet } from 'lucide-react';

interface DashboardProps {
  websites: Website[];
  opportunities: Opportunity[];
  scrapeRuns: ScrapeRun[];
  activities: Activity[];
  onViewDetails: (opp: Opportunity) => void;
  onRefresh: (opp: Opportunity) => void;
  onNavigate: (tab: string) => void;
  onMarkRead: (id: number) => void;
  onMarkAllRead: () => void;
  isLoading?: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  websites,
  opportunities,
  scrapeRuns,
  activities,
  onViewDetails,
  onRefresh,
  onNavigate,
  onMarkRead,
  onMarkAllRead,
  isLoading
}) => {
  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-sky-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-4 sm:p-6 shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <span className="inline-block px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300 text-[10px] sm:text-xs font-semibold uppercase tracking-wider mb-2">
            BRNS Funding Opportunity Tracker
          </span>
          <h2 className="text-lg sm:text-2xl font-bold tracking-tight">Active Research Grant Solicitations</h2>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mt-1 leading-relaxed">
            Real-time scraping engine monitoring official Board of Research in Nuclear Sciences (BRNS) project calls and document announcements.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0 w-full sm:w-auto">
          <button
            onClick={() => onNavigate('export')}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-colors border border-white/20"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Export Data</span>
          </button>

          <button
            onClick={() => onNavigate('opportunities')}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs transition-colors shadow-sm"
          >
            <span>All Solicitations</span>
            <ArrowRight className="w-4 h-4 shrink-0" />
          </button>
        </div>
      </div>

      {/* Summary Stat Cards */}
      <StatCards websites={websites} opportunities={opportunities} scrapeRuns={scrapeRuns} />

      {/* In-Website Activity Panel */}
      <ActivityPanel
        activities={activities}
        onMarkRead={onMarkRead}
        onMarkAllRead={onMarkAllRead}
      />

      {/* Main Solicitations Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">Discovered Opportunities</h3>
          <button
            onClick={() => onNavigate('opportunities')}
            className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1"
          >
            <span>View Full Table</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <OpportunityTable
          opportunities={opportunities}
          onViewDetails={onViewDetails}
          onRefresh={onRefresh}
          isLoading={isLoading}
        />
      </div>

    </div>
  );
};
