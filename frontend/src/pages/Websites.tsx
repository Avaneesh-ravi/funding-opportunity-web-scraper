import React from 'react';
import { Globe, Plus, RefreshCw, ExternalLink, Trash2, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Website } from '../types';

interface WebsitesProps {
  websites: Website[];
  onAddUrlClick: () => void;
  onScrapeWebsite: (websiteId: number) => void;
  onDeleteWebsite: (websiteId: number) => void;
}

export const Websites: React.FC<WebsitesProps> = ({
  websites,
  onAddUrlClick,
  onScrapeWebsite,
  onDeleteWebsite
}) => {
  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Globe className="w-5 h-5 text-sky-600" />
            Configured Website Sources
          </h3>
          <p className="text-xs text-slate-500">
            Registered portals and target URLs monitored by the scraping system.
          </p>
        </div>

        <button
          onClick={onAddUrlClick}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add URL</span>
        </button>
      </div>

      {/* Websites Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {websites.map((site) => {
          const isBRNS = site.scraper_type === 'brns';
          return (
            <div
              key={site.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <h4 className="font-bold text-slate-900 text-base tracking-tight">{site.name}</h4>
                    <span className="inline-block text-xs font-semibold text-sky-600 bg-sky-50 px-2.5 py-0.5 rounded-md mt-1">
                      {site.category || 'Research Grants'}
                    </span>
                  </div>

                  {isBRNS ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Supported Scraper</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                      <span>Scraper Not Configured</span>
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-600 mb-3 line-clamp-2">
                  {site.description || 'Target web page for grant solicitations and PDF announcements.'}
                </p>

                <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-600 truncate mb-4">
                  Target: {site.target_url}
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <a
                  href={site.target_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-sky-600 font-medium"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Visit Portal</span>
                </a>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onScrapeWebsite(site.id)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 font-semibold text-xs transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Scrape Now</span>
                  </button>

                  {!isBRNS && (
                    <button
                      onClick={() => onDeleteWebsite(site.id)}
                      title="Remove Website"
                      className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
