import React from 'react';
import { Settings as SettingsIcon, Clock, Shield, Database, Cpu } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-sky-600" />
          Application Settings & Environment
        </h3>
        <p className="text-xs text-slate-500">
          System configuration, security rules, and database parameters.
        </p>
      </div>

      <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-xs space-y-5 sm:space-y-6">
        
        <div className="flex items-start gap-3 sm:gap-4">
          <div className="p-2.5 sm:p-3 bg-sky-50 text-sky-600 rounded-xl shrink-0">
            <Clock className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-slate-900 text-sm">Timezone & Date Parsing</h4>
            <p className="text-xs text-slate-500">Default application timezone used for deadline calculation</p>
            <div className="mt-2 bg-slate-50 p-2.5 sm:p-3 rounded-lg border border-slate-200 font-mono text-xs text-slate-700 break-all">
              TIMEZONE = "Asia/Kolkata" (IST +05:30)
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3 sm:gap-4 pt-4 border-t border-slate-100">
          <div className="p-2.5 sm:p-3 bg-indigo-50 text-indigo-600 rounded-xl shrink-0">
            <Shield className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-slate-900 text-sm">SSRF & Security Validation</h4>
            <p className="text-xs text-slate-500">User URL registration protection policies</p>
            <div className="mt-2 bg-slate-50 p-2.5 sm:p-3 rounded-lg border border-slate-200 text-xs text-slate-700 space-y-1 break-words">
              <p>• Blocked protocols: file://, ftp://, gopher://</p>
              <p>• Blocked IP ranges: 127.0.0.0/8, 10.0.0.0/8, 192.168.0.0/16, 169.254.0.0/16</p>
              <p>• Download limits: Max PDF size 25MB</p>
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3 sm:gap-4 pt-4 border-t border-slate-100">
          <div className="p-2.5 sm:p-3 bg-emerald-50 text-emerald-600 rounded-xl shrink-0">
            <Database className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-slate-900 text-sm">Database Storage</h4>
            <p className="text-xs text-slate-500">SQLite persistence engine with SQLAlchemy ORM (PostgreSQL in production)</p>
            <div className="mt-2 bg-slate-50 p-2.5 sm:p-3 rounded-lg border border-slate-200 font-mono text-xs text-slate-700 break-all">
              DATABASE_URL = "sqlite:///./data/dashboard.db"
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
