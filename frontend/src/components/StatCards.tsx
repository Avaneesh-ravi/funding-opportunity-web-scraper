import React from 'react';
import { Globe, Award, CheckCircle2, XCircle, Clock, CheckCheck } from 'lucide-react';
import { Opportunity, Website, ScrapeRun } from '../types';

interface StatCardsProps {
  websites: Website[];
  opportunities: Opportunity[];
  scrapeRuns: ScrapeRun[];
}

export const StatCards: React.FC<StatCardsProps> = ({ websites, opportunities, scrapeRuns }) => {
  const totalWebsites = websites.length;
  const totalOpportunities = opportunities.length;
  
  const openCount = opportunities.filter((o) => o.deadline_status === 'Open').length;
  const closedCount = opportunities.filter((o) => o.deadline_status === 'Closed').length;
  const closingSoonCount = opportunities.filter((o) => o.deadline_status === 'Closing Soon').length;

  const lastSuccessfulRun = scrapeRuns.find((r) => r.status === 'SUCCESS');
  const lastScrapeTime = lastSuccessfulRun?.finished_at
    ? new Date(lastSuccessfulRun.finished_at).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : 'No successful runs yet';

  const stats = [
    {
      label: 'Websites Configured',
      value: totalWebsites,
      icon: Globe,
      color: 'text-sky-600',
      bg: 'bg-sky-50',
      border: 'border-sky-200'
    },
    {
      label: 'Opportunities Discovered',
      value: totalOpportunities,
      icon: Award,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      border: 'border-indigo-200'
    },
    {
      label: 'Open Opportunities',
      value: openCount,
      icon: CheckCircle2,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200'
    },
    {
      label: 'Closed / Deadline Passed',
      value: closedCount,
      icon: XCircle,
      color: 'text-rose-600',
      bg: 'bg-rose-50',
      border: 'border-rose-200'
    },
    {
      label: 'Deadlines Approaching',
      value: closingSoonCount,
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-200'
    },
    {
      label: 'Last Successful Scrape',
      value: lastScrapeTime,
      icon: CheckCheck,
      color: 'text-teal-600',
      bg: 'bg-teal-50',
      border: 'border-teal-200',
      isText: true
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border bg-white shadow-xs flex flex-col justify-between transition-all hover:shadow-md ${stat.border}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {stat.label}
              </span>
              <div className={`p-2 rounded-lg ${stat.bg} ${stat.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="mt-3">
              <span
                className={`font-bold text-slate-900 tracking-tight ${
                  stat.isText ? 'text-sm text-slate-700 block line-clamp-2' : 'text-2xl'
                }`}
              >
                {stat.value}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
