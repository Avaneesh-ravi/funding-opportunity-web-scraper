import React from 'react';
import { OpportunityTable } from '../components/OpportunityTable';
import { Opportunity } from '../types';
import { Award } from 'lucide-react';

interface OpportunitiesProps {
  opportunities: Opportunity[];
  onViewDetails: (opp: Opportunity) => void;
  onRefresh: (opp: Opportunity) => void;
  isLoading?: boolean;
}

export const Opportunities: React.FC<OpportunitiesProps> = ({
  opportunities,
  onViewDetails,
  onRefresh,
  isLoading
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Award className="w-5 h-5 text-sky-600" />
            Funding Opportunities Catalogue
          </h3>
          <p className="text-xs text-slate-500">
            Browse, search, filter by deadline status, and inspect extracted detail documents.
          </p>
        </div>
      </div>

      <OpportunityTable
        opportunities={opportunities}
        onViewDetails={onViewDetails}
        onRefresh={onRefresh}
        isLoading={isLoading}
      />
    </div>
  );
};
