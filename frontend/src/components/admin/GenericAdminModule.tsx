import React, { useEffect, useState } from 'react';
import { apiFetch } from '../../api/client';
import { Search, Filter, RefreshCw, Plus, Edit2, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { EntityModal, type FormField } from './EntityModal';

interface Column {
  header: string;
  accessor: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface GenericAdminModuleProps {
  title: string;
  description: string;
  endpoint: string;
  columns: Column[];
  addAction?: {
    label: string;
    fields: FormField[];
    onSubmit: (data: any) => Promise<void>;
  };
  editAction?: {
    fields: FormField[];
    onSubmit: (id: string, data: any) => Promise<void>;
  };
  deleteAction?: {
    onSubmit: (id: string) => Promise<void>;
  };
}

export const GenericAdminModule: React.FC<GenericAdminModuleProps> = ({
  title,
  description,
  endpoint,
  columns,
  addAction,
  editAction,
  deleteAction
}) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState<any>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Handle pagination or response structures (e.g. AuthorityQueueResponse has .items)
      const res = await apiFetch(endpoint);
      if (Array.isArray(res)) {
        setData(res);
      } else if (res && Array.isArray((res as any).items)) {
        setData((res as any).items);
      } else {
        setData(res ? [res] : []); // Fallback
      }
    } catch (err) {
      console.error(err);
      setError('Unable to load data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [endpoint]);

  const filteredData = data.filter(item => {
    if (!search) return true;
    return JSON.stringify(item).toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          <p className="text-slate-500 mt-1">{description}</p>
        </div>
        {addAction && (
          <Button onClick={() => { setSelectedEntity(null); setModalOpen(true); }} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> {addAction.label}
          </Button>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex gap-4 items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search records..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <Button variant="outline" size="sm" className="flex items-center gap-2 text-slate-600">
              <Filter className="h-4 w-4" /> Filters
            </Button>
          </div>
          <Button variant="ghost" size="sm" onClick={fetchData} className="text-slate-500">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        <div className="overflow-x-auto min-h-[300px]">
          {loading ? (
            <div className="p-12 text-center text-slate-500">Loading records...</div>
          ) : error ? (
            <div className="p-12 text-center text-red-500">
              <p>{error}</p>
              <Button variant="outline" size="sm" onClick={fetchData} className="mt-4">Retry</Button>
            </div>
          ) : filteredData.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              No records found.
            </div>
          ) : (
            <table className="w-full text-sm text-left text-slate-600">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                <tr>
                  {columns.map((col, i) => (
                    <th key={i} className="px-6 py-3 font-semibold tracking-wider">
                      {col.header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredData.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    {columns.map((col, j) => (
                      <td key={j} className="px-6 py-4 whitespace-nowrap">
                        {col.render 
                          ? col.render(row[col.accessor], row)
                          : (row[col.accessor] === null || row[col.accessor] === undefined ? '-' : String(row[col.accessor]))}
                      </td>
                    ))}
                    {(editAction || deleteAction) && (
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex justify-end gap-2">
                          {editAction && (
                            <button onClick={() => { setSelectedEntity(row); setModalOpen(true); }} className="p-1 text-slate-400 hover:text-indigo-600 transition-colors">
                              <Edit2 className="h-4 w-4" />
                            </button>
                          )}
                          {deleteAction && (
                            <button onClick={async () => {
                              if (window.confirm('Are you sure you want to deactivate/delete this record?')) {
                                try {
                                  const idField = row._id || row.id;
                                  await deleteAction.onSubmit(idField);
                                  await fetchData();
                                } catch (e) {
                                  alert('Error deleting record.');
                                }
                              }
                            }} className="p-1 text-slate-400 hover:text-red-600 transition-colors">
                              <Trash2 className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 flex justify-between">
          <span>Showing {filteredData.length} records</span>
          <span className="cursor-not-allowed">Pagination disabled in quick-view</span>
        </div>
      </div>

      {(addAction || editAction) && (
        <EntityModal
          isOpen={modalOpen}
          onClose={() => { setModalOpen(false); setSelectedEntity(null); }}
          title={title}
          fields={selectedEntity ? (editAction?.fields || []) : (addAction?.fields || [])}
          initialData={selectedEntity}
          onSubmit={async (data) => {
            if (selectedEntity && editAction) {
              const idField = selectedEntity._id || selectedEntity.id;
              await editAction.onSubmit(idField, data);
            } else if (addAction) {
              await addAction.onSubmit(data);
            }
            await fetchData();
          }}
        />
      )}
    </div>
  );
};
