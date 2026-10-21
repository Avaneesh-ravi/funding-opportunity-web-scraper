import React from 'react';
import { History, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { ScrapeRun, Website } from '../types';

interface ScrapingHistoryProps {
  scrapeRuns: ScrapeRun[];
  websites: Website[];
}

export const ScrapingHistory: React.FC<ScrapingHistoryProps> = ({ scrapeRuns, websites }) => {
  const getWebsiteName = (websiteId: number) => {
    const site = websites.find((w) => w.id === websiteId);
    return site ? site.name : `Website #${websiteId}`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-sky-600" />
            Scraping Execution Logs
          </h3>
          <p className="text-xs text-slate-500">
            Historical audit log of all manual and scheduled scraping runs.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-100/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Run ID</th>
                <th className="px-4 py-3">Target Website</th>
                <th className="px-4 py-3">Started At</th>
                <th className="px-4 py-3">Finished At</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-center">Found / Created / Updated</th>
                <th className="px-4 py-3">Error / Status Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {scrapeRuns.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No scraping history logs available.
                  </td>
                </tr>
              ) : (
                scrapeRuns.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-4 py-3.5 font-mono text-xs font-bold text-slate-400">#{run.id}</td>
                    <td className="px-4 py-3.5 font-semibold text-slate-900">
                      {getWebsiteName(run.website_id)}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 whitespace-nowrap">
                      {formatDate(run.started_at)}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 whitespace-nowrap">
                      {formatDate(run.finished_at)}
                    </td>
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      {run.status === 'SUCCESS' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                          <span>SUCCESS</span>
                        </span>
                      )}
                      {run.status === 'FAILED' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                          <XCircle className="w-3.5 h-3.5 text-rose-600" />
                          <span>FAILED</span>
                        </span>
                      )}
                      {run.status === 'RUNNING' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 animate-pulse">
                          <Clock className="w-3.5 h-3.5 text-sky-600" />
                          <span>RUNNING</span>
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-center font-mono text-xs font-semibold text-slate-800">
                      {run.records_found} / <span className="text-emerald-600">+{run.records_created}</span> / <span className="text-sky-600">~{run.records_updated}</span>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 max-w-xs truncate" title={run.error_message || 'Completed successfully'}>
                      {run.error_message ? (
                        <span className="text-rose-600 flex items-center gap-1">
                          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                          <span className="truncate">{run.error_message}</span>
                        </span>
                      ) : (
                        <span className="text-emerald-700 font-medium">Scraping completed successfully.</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
