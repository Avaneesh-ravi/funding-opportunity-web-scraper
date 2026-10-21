import { Website, WebsiteCreatePayload, Opportunity, ScrapeRun, Activity } from '../types';

// In production on Vercel, set VITE_API_BASE_URL=https://your-backend.onrender.com
// In local development, leave unset to use Vite's proxy (/api -> http://127.0.0.1:8000)
const rawApiBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
const API_BASE = rawApiBase
  ? (rawApiBase.endsWith('/api') ? rawApiBase : `${rawApiBase}/api`)
  : '/api';

// Helper to extract clean error message string from FastAPI responses
export function extractErrorMessage(errorData: any, fallback: string): string {
  if (!errorData) return fallback;
  if (typeof errorData === 'string') return errorData;
  if (typeof errorData.detail === 'string') return errorData.detail;
  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map((item: any) => {
        if (typeof item === 'string') return item;
        if (item?.msg) {
          const field = Array.isArray(item.loc)
            ? item.loc.filter((p: any) => p !== 'body').join('.')
            : '';
          return field ? `${field}: ${item.msg}` : item.msg;
        }
        return JSON.stringify(item);
      })
      .join('; ');
  }
  if (typeof errorData.detail === 'object' && errorData.detail !== null) {
    return JSON.stringify(errorData.detail);
  }
  if (typeof errorData.message === 'string') return errorData.message;
  return fallback;
}

export async function fetchWebsites(): Promise<Website[]> {
  const res = await fetch(`${API_BASE}/websites`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(extractErrorMessage(errorData, 'Failed to fetch websites'));
  }
  return res.json();
}

export async function createWebsite(payload: WebsiteCreatePayload): Promise<Website> {
  const res = await fetch(`${API_BASE}/websites`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(extractErrorMessage(errorData, 'Failed to create website'));
  }
  return res.json();
}

export async function deleteWebsite(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/websites/${id}`, { method: 'DELETE' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(extractErrorMessage(errorData, 'Failed to delete website'));
  }
}

export async function triggerScrape(websiteId: number): Promise<ScrapeRun> {
  const res = await fetch(`${API_BASE}/websites/${websiteId}/scrape`, { method: 'POST' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(extractErrorMessage(errorData, 'Failed to trigger scrape'));
  }
  return res.json();
}

export async function fetchOpportunities(params?: {
  q?: string;
  status?: string;
  website_id?: number;
  sort_by?: string;
}): Promise<Opportunity[]> {
  const base = API_BASE.startsWith('http://') || API_BASE.startsWith('https://')
    ? API_BASE
    : `${window.location.origin}${API_BASE}`;
  const url = new URL(`${base}/opportunities`);
  if (params?.q) url.searchParams.append('q', params.q);
  if (params?.status) url.searchParams.append('status', params.status);
  if (params?.website_id) url.searchParams.append('website_id', params.website_id.toString());
  if (params?.sort_by) url.searchParams.append('sort_by', params.sort_by);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch opportunities');
  return res.json();
}

export async function fetchOpportunityDetails(id: number): Promise<Opportunity> {
  const res = await fetch(`${API_BASE}/opportunities/${id}`);
  if (!res.ok) throw new Error('Failed to fetch opportunity details');
  return res.json();
}

export async function refreshOpportunity(id: number): Promise<ScrapeRun> {
  const res = await fetch(`${API_BASE}/opportunities/${id}/refresh`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh opportunity');
  return res.json();
}

export async function fetchScrapeRuns(): Promise<ScrapeRun[]> {
  const res = await fetch(`${API_BASE}/scrape-runs`);
  if (!res.ok) throw new Error('Failed to fetch scraping history');
  return res.json();
}

export async function fetchActivities(unreadOnly = false): Promise<Activity[]> {
  const res = await fetch(`${API_BASE}/activities?unread_only=${unreadOnly}`);
  if (!res.ok) throw new Error('Failed to fetch in-website activities');
  return res.json();
}

export async function markActivityRead(id: number): Promise<Activity> {
  const res = await fetch(`${API_BASE}/activities/${id}/read`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_read: true }),
  });
  if (!res.ok) throw new Error('Failed to mark notification as read');
  return res.json();
}

export async function markAllActivitiesRead(): Promise<void> {
  const res = await fetch(`${API_BASE}/activities/read-all`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to mark all notifications as read');
}

export function getExportUrl(format: 'csv' | 'excel' = 'csv'): string {
  return `${API_BASE}/opportunities/export?format=${format}`;
}
