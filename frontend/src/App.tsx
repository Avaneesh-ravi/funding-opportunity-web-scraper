import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OpportunityDetailModal } from './components/OpportunityDetailModal';
import { AddUrlModal } from './components/AddUrlModal';

import { Dashboard } from './pages/Dashboard';
import { Opportunities } from './pages/Opportunities';
import { Websites } from './pages/Websites';
import { ScrapingHistory } from './pages/ScrapingHistory';
import { ExportPage } from './pages/ExportPage';
import { SettingsPage } from './pages/Settings';

import { 
  fetchWebsites, 
  fetchOpportunities, 
  fetchScrapeRuns, 
  fetchActivities,
  markActivityRead,
  markAllActivitiesRead,
  createWebsite, 
  deleteWebsite, 
  triggerScrape, 
  refreshOpportunity 
} from './services/api';
import { Website, Opportunity, ScrapeRun, Activity, WebsiteCreatePayload } from './types';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [isMobileNavOpen, setIsMobileNavOpen] = useState<boolean>(false);
  
  const [websites, setWebsites] = useState<Website[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [scrapeRuns, setScrapeRuns] = useState<ScrapeRun[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [isAddUrlOpen, setIsAddUrlOpen] = useState<boolean>(false);

  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [sitesData, oppsData, runsData, actsData] = await Promise.all([
        fetchWebsites(),
        fetchOpportunities(),
        fetchScrapeRuns(),
        fetchActivities()
      ]);
      setWebsites(sitesData);
      setOpportunities(oppsData);
      setScrapeRuns(runsData);
      setActivities(actsData);
    } catch (err: any) {
      console.error('Failed to load application data:', err);
      showToast('Failed to load data from backend server.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleGlobalRefreshBRNS = async () => {
    const brnsSite = websites.find((w) => w.scraper_type === 'brns') || websites[0];
    if (!brnsSite) return;

    setIsRefreshing(true);
    try {
      const run = await triggerScrape(brnsSite.id);
      if (run.status === 'SUCCESS') {
        showToast('BRNS funding opportunity successfully scraped and verified!', 'success');
      } else {
        showToast(run.error_message || 'BRNS scraping run failed.', 'error');
      }
      await loadAllData();
    } catch (err: any) {
      showToast('Failed to execute scraping run.', 'error');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleAddWebsite = async (payload: WebsiteCreatePayload) => {
    try {
      const newSite = await createWebsite(payload);
      showToast(`Website "${newSite.name}" registered successfully.`, 'success');
      await loadAllData();
    } catch (err: any) {
      const msg = err?.message || 'Failed to register website.';
      showToast(msg, 'error');
      throw err;
    }
  };

  const handleDeleteWebsite = async (siteId: number) => {
    if (!window.confirm('Are you sure you want to remove this website?')) return;
    try {
      await deleteWebsite(siteId);
      showToast('Website removed successfully.', 'success');
      await loadAllData();
    } catch (err) {
      showToast('Failed to remove website.', 'error');
    }
  };

  const handleScrapeSpecificWebsite = async (siteId: number) => {
    setIsRefreshing(true);
    try {
      const run = await triggerScrape(siteId);
      if (run.status === 'SUCCESS') {
        showToast('Website scraped successfully!', 'success');
      } else {
        showToast(run.error_message || 'Scraping run failed.', 'error');
      }
      await loadAllData();
    } catch (err) {
      showToast('Failed to execute scrape.', 'error');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRefreshSingleOpportunity = async (opp: Opportunity) => {
    setIsRefreshing(true);
    try {
      const run = await refreshOpportunity(opp.id);
      if (run.status === 'SUCCESS') {
        showToast(`Refreshed data for ${opp.title}`, 'success');
      } else {
        showToast(run.error_message || 'Refresh failed', 'error');
      }
      await loadAllData();
    } catch (err) {
      showToast('Failed to refresh opportunity data', 'error');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleMarkActivityRead = async (id: number) => {
    try {
      await markActivityRead(id);
      setActivities((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
    } catch (err) {
      console.error('Failed to mark read', err);
    }
  };

  const handleMarkAllActivitiesRead = async () => {
    try {
      await markAllActivitiesRead();
      setActivities((prev) => prev.map((a) => ({ ...a, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all read', err);
    }
  };

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard': return 'Dashboard Overview';
      case 'opportunities': return 'Funding Solicitations';
      case 'websites': return 'Website Portals';
      case 'history': return 'Scraping History Audit';
      case 'export': return 'Export Reports';
      case 'settings': return 'System Settings';
      default: return 'Web Scraping Dashboard';
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 relative">
      
      {/* Sidebar Navigation (Desktop permanent / Mobile drawer) */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 w-full">
        
        <Header
          title={getPageTitle()}
          onAddUrlClick={() => setIsAddUrlOpen(true)}
          onRefreshClick={handleGlobalRefreshBRNS}
          isRefreshing={isRefreshing}
          activities={activities}
          onMarkRead={handleMarkActivityRead}
          onMarkAllRead={handleMarkAllActivitiesRead}
          onToggleMobileNav={() => setIsMobileNavOpen((prev) => !prev)}
        />

        {/* Toast Notification Alert */}
        {toast && (
          <div className="px-3 sm:px-6 pt-3 sm:pt-4">
            <div className={`p-3 rounded-xl border flex items-center justify-between text-xs font-semibold shadow-xs ${
              toast.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-rose-50 text-rose-800 border-rose-200'
            }`}>
              <div className="flex items-center gap-2 min-w-0">
                {toast.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />}
                <span className="break-words">{toast.message}</span>
              </div>
              <button onClick={() => setToast(null)} className="text-slate-400 hover:text-slate-600 ml-2 shrink-0" aria-label="Dismiss message">✕</button>
            </div>
          </div>
        )}

        <main className="p-3 sm:p-5 md:p-6 flex-1 min-w-0">
          {currentTab === 'dashboard' && (
            <Dashboard
              websites={websites}
              opportunities={opportunities}
              scrapeRuns={scrapeRuns}
              activities={activities}
              onViewDetails={(opp) => setSelectedOpportunity(opp)}
              onRefresh={handleRefreshSingleOpportunity}
              onNavigate={(tab) => setCurrentTab(tab)}
              onMarkRead={handleMarkActivityRead}
              onMarkAllRead={handleMarkAllActivitiesRead}
              isLoading={isLoading}
            />
          )}

          {currentTab === 'opportunities' && (
            <Opportunities
              opportunities={opportunities}
              onViewDetails={(opp) => setSelectedOpportunity(opp)}
              onRefresh={handleRefreshSingleOpportunity}
              isLoading={isLoading}
            />
          )}

          {currentTab === 'websites' && (
            <Websites
              websites={websites}
              scrapeRuns={scrapeRuns}
              onAddUrlClick={() => setIsAddUrlOpen(true)}
              onScrapeWebsite={handleScrapeSpecificWebsite}
              onDeleteWebsite={handleDeleteWebsite}
            />
          )}

          {currentTab === 'history' && (
            <ScrapingHistory scrapeRuns={scrapeRuns} websites={websites} />
          )}

          {currentTab === 'export' && (
            <ExportPage opportunities={opportunities} />
          )}

          {currentTab === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Detail Modal Drawer */}
      <OpportunityDetailModal
        opportunity={selectedOpportunity}
        onClose={() => setSelectedOpportunity(null)}
        onRefresh={handleRefreshSingleOpportunity}
      />

      {/* Add URL Form Modal */}
      <AddUrlModal
        isOpen={isAddUrlOpen}
        onClose={() => setIsAddUrlOpen(false)}
        onSubmit={handleAddWebsite}
      />

    </div>
  );
}

export default App;
