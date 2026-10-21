import React from 'react';
import { Globe, Plus, RefreshCw, ExternalLink, Trash2, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Globe className="w-5 h-5 text-sky-600 shrink-0" />
            <span>Configured Website Sources</span>
          </h3>
          <p className="text-xs text-slate-500">
            Registered portals monitored by dedicated site scrapers and the universal adaptive scraping engine.
          </p>
        </div>

        <button
          onClick={onAddUrlClick}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs transition-colors shadow-sm self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add URL</span>
        </button>
      </div>

      {/* Websites Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {websites.map((site) => {
          // Check if website has a dedicated specialized scraper (BRNS or DST)
          const scraperType = (site.scraper_type || '').toLowerCase().trim();
          const isDedicatedType = scraperType === 'brns' || scraperType === 'dst';
          
          // Domain / canonical URL verification
          let isDedicatedDomain = false;
          try {
            const rawUrl = site.target_url.startsWith('http://') || site.target_url.startsWith('https://')
              ? site.target_url
              : `https://${site.target_url}`;
            const hostname = new URL(rawUrl).hostname.toLowerCase();
            isDedicatedDomain =
              hostname === 'brns.res.in' ||
              hostname.endsWith('.brns.res.in') ||
              hostname === 'dst.gov.in' ||
              hostname.endsWith('.dst.gov.in') ||
              hostname === 'onlinedst.gov.in' ||
              hostname.endsWith('.onlinedst.gov.in');
          } catch {
            const targetLower = (site.target_url || '').toLowerCase();
            isDedicatedDomain =
              targetLower.includes('brns.res.in') ||
              targetLower.includes('dst.gov.in') ||
              targetLower.includes('onlinedst.gov.in');
          }

          // System seeded IDs: 1 = BRNS, 2 = DST
          const isSystemPortal = site.id === 1 || site.id === 2;
          const isDedicated = isDedicatedType || isDedicatedDomain || isSystemPortal;
          const canDelete = !isSystemPortal;

          return (
            <div
              key={site.id}
              className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
                  <div>
                    <h4 className="font-bold text-slate-900 text-base tracking-tight">{site.name}</h4>
                    <span className="inline-block text-xs font-semibold text-sky-600 bg-sky-50 px-2.5 py-0.5 rounded-md mt-1">
                      {site.category || 'Research Grants'}
                    </span>
                  </div>

                  <div className="self-start">
                    {isDedicated ? (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap" title="High-precision domain-specific scraper active">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>Dedicated Scraper</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-50 text-sky-700 border border-sky-200 whitespace-nowrap" title="Universal adaptive scraping engine active">
                        <Sparkles className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                        <span>Universal Engine (Active)</span>
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-600 mb-3 line-clamp-2">
                  {site.description || 'Target web page for grant solicitations and PDF announcements.'}
                </p>

                <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-600 break-all mb-4">
                  Target: {site.target_url}
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                <a
                  href={site.target_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-sky-600 font-medium"
                >
                  <ExternalLink className="w-3.5 h-3.5 shrink-0" />
                  <span>Visit Portal</span>
                </a>

                <div className="flex items-center gap-2 ml-auto sm:ml-0">
                  <button
                    onClick={() => onScrapeWebsite(site.id)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 font-semibold text-xs transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5 shrink-0" />
                    <span>Scrape Now</span>
                  </button>

                  {canDelete && (
                    <button
                      onClick={() => onDeleteWebsite(site.id)}
                      title="Remove Website"
                      className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 transition-colors"
                    >
                      <Trash2 className="w-4 h-4 shrink-0" />
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
