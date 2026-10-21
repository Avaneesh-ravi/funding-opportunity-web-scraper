import React, { useState } from 'react';
import { X, Plus, AlertCircle, CheckCircle } from 'lucide-react';
import { WebsiteCreatePayload } from '../types';

interface AddUrlModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: WebsiteCreatePayload) => Promise<void>;
}

export const AddUrlModal: React.FC<AddUrlModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [targetUrl, setTargetUrl] = useState('');
  const [category, setCategory] = useState('Research Grants');
  const [description, setDescription] = useState('');
  const [enabled, setEnabled] = useState(true);

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Close on Escape key press
  React.useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic URL validation
    if (!targetUrl.trim()) {
      setError('Target URL is required.');
      return;
    }

    try {
      const parsed = new URL(targetUrl.trim());
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        setError('Only HTTP and HTTPS URLs are allowed.');
        return;
      }
    } catch {
      setError('Please enter a valid HTTP/HTTPS web URL.');
      return;
    }

    setIsSubmitting(true);
    try {
      const parsedUrl = new URL(targetUrl.trim());
      const derivedBaseUrl = `${parsedUrl.protocol}//${parsedUrl.host}`;

      await onSubmit({
        name: name.trim() || targetUrl.trim(),
        base_url: derivedBaseUrl,
        target_url: targetUrl.trim(),
        category,
        description: description.trim() || undefined,
        enabled
      });

      // Reset form
      setName('');
      setTargetUrl('');
      setDescription('');
      onClose();
    } catch (err: any) {
      const msg = typeof err === 'string'
        ? err
        : (err?.message && err.message !== '[object Object]')
          ? err.message
          : (typeof err?.detail === 'string' ? err.detail : 'Failed to register website URL');
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-add-url-title"
    >
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-[calc(100vw-24px)] sm:w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-150">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-sky-100 text-sky-700 rounded-lg shrink-0">
              <Plus className="w-5 h-5" />
            </div>
            <div>
              <h3 id="modal-add-url-title" className="font-bold text-slate-900 tracking-tight text-sm sm:text-base">
                Add New Source URL
              </h3>
              <p className="text-xs text-slate-500">Configure additional funding opportunity portal</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/50 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form - Scrollable */}
        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 text-sm overflow-y-auto flex-1">
          
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 mt-0.5" />
              <span className="break-words">{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Website Name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Science & Engineering Research Board (SERB)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:outline-hidden text-xs sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Target URL *
            </label>
            <input
              type="url"
              required
              placeholder="https://example.gov.in/funding-calls.php"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:outline-hidden text-xs sm:text-sm"
            />
            <p className="text-[11px] text-slate-400 mt-1 leading-normal">
              For new domain URLs, system will display "Scraper not configured" until a site-specific scraper is implemented.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:outline-hidden text-xs sm:text-sm"
              >
                <option value="Research Grants">Research Grants</option>
                <option value="Fellowships">Fellowships</option>
                <option value="Symposium & Conferences">Symposium & Conferences</option>
                <option value="Nuclear Sciences">Nuclear Sciences</option>
                <option value="General Funding">General Funding</option>
              </select>
            </div>

            <div className="flex items-center sm:pt-5">
              <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                  className="rounded-md border-slate-300 text-sky-600 focus:ring-sky-500 w-4 h-4"
                />
                <span>Enable Scraping</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Description / Notes
            </label>
            <textarea
              rows={2}
              placeholder="Optional notes about this funding portal..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:outline-hidden text-xs sm:text-sm"
            />
          </div>

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-200 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-end gap-2 sm:gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors font-medium text-xs sm:text-sm text-center"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-semibold text-xs sm:text-sm transition-colors shadow-sm disabled:opacity-50 text-center"
            >
              {isSubmitting ? 'Saving URL...' : 'Register Website'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
