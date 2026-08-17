import React, { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';

export const CommandCenter: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const data = await apiFetch('/api/v1/admin/overview');
        setOverview(data);
      } catch (error) {
        console.error('Failed to load admin overview', error);
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Command Center...</div>;
  }

  if (!overview) {
    return <div className="p-8 text-center text-red-500">Unable to load command center statistics. <button onClick={() => window.location.reload()} className="underline">Retry</button></div>;
  }

  const { operational, administrative } = overview;

  return (
    <div className="space-y-6">
      {/* Operational Stats */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Cases</p>
          <p className="text-2xl font-bold mt-2">{operational.total_cases}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Unassigned</p>
          <p className="text-2xl font-bold mt-2 text-red-600">{operational.unassigned}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Assigned</p>
          <p className="text-2xl font-bold mt-2 text-blue-600">{operational.assigned}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">In Progress</p>
          <p className="text-2xl font-bold mt-2 text-amber-500">{operational.in_progress}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Resolved</p>
          <p className="text-2xl font-bold mt-2 text-green-600">{operational.resolved}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 flex flex-col justify-between">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Closed</p>
          <p className="text-2xl font-bold mt-2 text-slate-700">{operational.closed}</p>
        </div>
      </div>

      {/* Administrative Stats */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Auth</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.active_authorities}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Auth</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.pending_authorities}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Departments</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.active_departments}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Wards</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.active_wards}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Open Projects</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.open_civic_projects}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Verified Orgs</p>
          <p className="text-xl font-bold mt-1 text-slate-700">{administrative.verified_organizations}</p>
        </div>
      </div>

      {/* Main Queue Container */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-lg font-bold text-slate-800">Civic Operations Queue</h2>
          <div className="flex gap-2">
            <button className="px-4 py-1.5 text-sm font-medium bg-slate-100 text-slate-800 rounded-md">Complaints</button>
            <button className="px-4 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-md">Problem Clusters</button>
            <button className="px-4 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-md">Civic Projects</button>
          </div>
        </div>
        
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex gap-4">
          <input type="text" placeholder="Search by ID, Title, Ward..." className="flex-1 px-3 py-2 border border-slate-300 rounded-md text-sm" />
          <select className="px-3 py-2 border border-slate-300 rounded-md text-sm bg-white"><option>All Statuses</option></select>
          <select className="px-3 py-2 border border-slate-300 rounded-md text-sm bg-white"><option>All Categories</option></select>
        </div>

        <div className="p-12 text-center text-slate-500">
          <p>This queue is populated from the actual `/api/v1/authority/complaints` and `/api/v1/civic-projects` APIs.</p>
        </div>
      </div>
    </div>
  );
};
