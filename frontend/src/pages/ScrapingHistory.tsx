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

      {/* Desktop Table View */}
      <div className="hidden md:block bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
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

      {/* Mobile Card View */}
      <div className="block md:hidden space-y-3">
        {scrapeRuns.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500 text-sm">
            No scraping history logs available.
          </div>
        ) : (
          scrapeRuns.map((run) => (
            <div
              key={run.id}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-3"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-400">#{run.id}</span>
                    <h4 className="font-bold text-slate-900 text-sm">{getWebsiteName(run.website_id)}</h4>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">Started: {formatDate(run.started_at)}</p>
                </div>

                <div>
                  {run.status === 'SUCCESS' && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap">
                      <CheckCircle className="w-3 h-3 text-emerald-600 shrink-0" />
                      <span>SUCCESS</span>
                    </span>
                  )}
                  {run.status === 'FAILED' && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 whitespace-nowrap">
                      <XCircle className="w-3 h-3 text-rose-600 shrink-0" />
                      <span>FAILED</span>
                    </span>
                  )}
                  {run.status === 'RUNNING' && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200 animate-pulse whitespace-nowrap">
                      <Clock className="w-3 h-3 text-sky-600 shrink-0" />
                      <span>RUNNING</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-center">
                <div>
                  <p className="text-[10px] uppercase font-semibold text-slate-400">Found</p>
                  <p className="font-mono text-xs font-bold text-slate-700">{run.records_found}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-semibold text-slate-400">Created</p>
                  <p className="font-mono text-xs font-bold text-emerald-600">+{run.records_created}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase font-semibold text-slate-400">Updated</p>
                  <p className="font-mono text-xs font-bold text-sky-600">~{run.records_updated}</p>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 text-xs">
                {run.error_message ? (
                  <p className="text-rose-600 flex items-start gap-1.5 break-words">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    <span>{run.error_message}</span>
                  </p>
                ) : (
                  <p className="text-emerald-700 font-medium flex items-center gap-1.5">
                    <CheckCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>Completed successfully ({formatDate(run.finished_at)})</span>
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
