export interface OpportunityHistory {
  id: number;
  opportunity_id: number;
  field_name: string;
  old_value?: string;
  new_value?: string;
  changed_at: string;
  verification_source?: string;
}

export interface Opportunity {
  id: number;
  website_id: number;
  external_identifier?: string;
  title: string;
  scheme_name?: string;
  funding_agency: string;
  description?: string;
  announcement_date?: string;
  opening_date?: string;
  original_deadline?: string;
  current_deadline?: string;
  deadline_status: 'Open' | 'Closing Soon' | 'Closed' | 'Upcoming' | 'Extended' | 'Unknown' | 'Verification Required';
  funding_amount?: string;
  eligibility?: string;
  research_areas?: string;
  project_duration?: string;
  submission_instructions?: string;
  application_url?: string;
  document_url?: string;
  source_url: string;
  first_seen_at: string;
  last_seen_at: string;
  last_verified_at: string;
  created_at: string;
  updated_at: string;
  history?: OpportunityHistory[];
}

export interface Website {
  id: number;
  name: string;
  base_url: string;
  target_url: string;
  category?: string;
  description?: string;
  scraper_type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScrapeRun {
  id: number;
  website_id: number;
  started_at: string;
  finished_at?: string;
  status: 'RUNNING' | 'SUCCESS' | 'FAILED' | 'PARTIAL';
  records_found: number;
  records_created: number;
  records_updated: number;
  error_message?: string;
}

export interface Activity {
  id: number;
  website_id?: number;
  opportunity_id?: number;
  event_type: 'NEW_OPPORTUNITY' | 'DEADLINE_CHANGED' | 'EXTENSION_VERIFIED' | 'UPCOMING_DEADLINE' | 'SCRAPE_SUCCESS' | 'SCRAPE_FAILED' | 'CONFIG_REQUIRED';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface WebsiteCreatePayload {
  name: string;
  base_url?: string;
  target_url: string;
  category?: string;
  description?: string;
  enabled?: boolean;
}
