import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api/client';

interface Organization {
  id: string;
  name: string;
  org_type: string;
  description: string;
  focus_areas: string[];
  verification_status: string;
}

export const Organizations: React.FC = () => {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrgs = async () => {
      try {
        const data = await apiFetch<Organization[]>('/api/v1/organizations');
        setOrgs(data);
      } catch (error) {
        console.error('Failed to fetch orgs', error);
      } finally {
        setLoading(false);
      }
    };
    fetchOrgs();
  }, []);

  if (loading) return <div className="p-4">Loading Participating Organizations...</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Participating Organizations</h1>
      <p className="mb-8 text-gray-600">Verified partners helping to execute civic projects.</p>
      
      {orgs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500 border border-gray-200">
          No verified organizations yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {orgs.map((org) => (
            <div key={org.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">{org.name}</h3>
                <span className="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded flex items-center">
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                  Verified
                </span>
              </div>
              <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold mb-2">{org.org_type.replace(/_/g, ' ')}</p>
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">{org.description || 'No description provided.'}</p>
              
              {org.focus_areas.length > 0 && (
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Focus Areas</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {org.focus_areas.map(area => (
                      <span key={area} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">{area}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
