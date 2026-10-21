import React from 'react';
import { FileSpreadsheet, Download, FileText, CheckCircle2 } from 'lucide-react';
import { getExportUrl } from '../services/api';
import { Opportunity } from '../types';

interface ExportPageProps {
  opportunities: Opportunity[];
}

export const ExportPage: React.FC<ExportPageProps> = ({ opportunities }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
          Reports & Opportunity Export
        </h3>
        <p className="text-xs text-slate-500">
          Export verified BRNS research grant solicitations into standard CSV or Microsoft Excel formats.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* CSV Export Box */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-100 text-emerald-700 rounded-xl">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-lg">CSV Format (.csv)</h4>
              <p className="text-xs text-slate-500">Standard UTF-8 comma separated spreadsheet file</p>
            </div>
          </div>

          <ul className="text-xs text-slate-600 space-y-1.5 pt-2 border-t border-slate-100">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Includes Agency, Title, Dates, Document URLs, & Status</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Compatible with Python, R, Excel, Google Sheets</span>
            </li>
          </ul>

          <a
            href={getExportUrl('csv')}
            download
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm transition-colors shadow-sm shadow-emerald-600/20"
          >
            <Download className="w-4 h-4" />
            <span>Download CSV ({opportunities.length} Records)</span>
          </a>
        </div>

        {/* Excel Export Box */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-sky-100 text-sky-700 rounded-xl">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-lg">Excel Workbook (.xlsx)</h4>
              <p className="text-xs text-slate-500">Formatted OpenPyXL Microsoft Excel spreadsheet</p>
            </div>
          </div>

          <ul className="text-xs text-slate-600 space-y-1.5 pt-2 border-t border-slate-100">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-sky-600" />
              <span>Structured worksheet tab: 'Funding Opportunities'</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-sky-600" />
              <span>Full eligibility and submission URL columns included</span>
            </li>
          </ul>

          <a
            href={getExportUrl('excel')}
            download
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-sm transition-colors shadow-sm shadow-sky-600/20"
          >
            <Download className="w-4 h-4" />
            <span>Download Excel WorkBook (.xlsx)</span>
          </a>
        </div>

      </div>
    </div>
  );
};
