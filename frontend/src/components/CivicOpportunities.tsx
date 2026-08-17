import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api/client';


interface CivicProject {
  id: string;
  project_code: string;
  title: string;
  description: string;
  category: string;
  status: string;
  verification_status: string;
  required_resources: string[];
}

export const CivicOpportunities: React.FC = () => {
  const [projects, setProjects] = useState<CivicProject[]>([]);
  const [loading, setLoading] = useState(true);
  // useAuth();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await apiFetch<CivicProject[]>('/api/v1/civic-projects');
        setProjects(data);
      } catch (error) {
        console.error('Failed to fetch projects', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  if (loading) return <div className="p-4">Loading Civic Opportunities...</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Civic Opportunities</h1>
      <p className="mb-8 text-gray-600">Discover verified civic projects and matching resource opportunities.</p>
      
      {projects.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500 border border-gray-200">
          No verified civic projects yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                  {project.category.replace(/_/g, ' ')}
                </span>
                <span className="text-sm font-mono text-gray-500">{project.project_code}</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">{project.title}</h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">{project.description}</p>
              
              <div className="space-y-3 mb-6">
                <div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Status</span>
                  <p className="text-sm">{project.status.replace(/_/g, ' ')}</p>
                </div>
                {project.required_resources.length > 0 && (
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Requirements</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {project.required_resources.map(res => (
                        <span key={res} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">{res}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <button 
                onClick={() => alert('Viewing detailed opportunity and match request flow will be implemented here.')}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                View Opportunity
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
