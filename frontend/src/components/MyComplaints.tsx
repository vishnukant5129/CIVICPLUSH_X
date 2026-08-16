import React, { useEffect, useState } from 'react';
import { complaintsApi } from '../api/complaints';
import type { ComplaintResponse } from '../api/complaints';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { FileText, Plus, Calendar, Inbox, ArrowRight } from 'lucide-react';

export const MyComplaints: React.FC = () => {
  const [complaints, setComplaints] = useState<ComplaintResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadComplaints();
  }, []);

  const loadComplaints = async () => {
    try {
      setLoading(true);
      const data = await complaintsApi.listMy();
      setComplaints(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load complaints');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch(status) {
      case 'submitted': return 'secondary';
      case 'assigned': return 'info';
      case 'in_progress': return 'warning';
      case 'resolved': return 'success';
      case 'closed': return 'default';
      case 'rejected': return 'destructive';
      default: return 'outline';
    }
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-slate-500 space-y-4">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-civic-600 rounded-full animate-spin"></div>
        <p className="text-sm font-medium">Loading your submitted issues...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded text-sm font-medium">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <FileText className="h-8 w-8 text-civic-600" />
            My Complaints
          </h1>
          <p className="text-slate-500 mt-1">Track the status of your reported civic issues.</p>
        </div>
        <Button onClick={() => window.location.href = '/complaints/new'} className="bg-civic-600 hover:bg-civic-700">
          <Plus className="h-4 w-4 mr-2" />
          File New Complaint
        </Button>
      </div>

      {complaints.length === 0 ? (
        <Card className="border-dashed border-2 shadow-none bg-slate-50/50">
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <Inbox className="h-12 w-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-700">No Complaints Found</h3>
            <p className="text-slate-500 mt-2 max-w-sm mb-6">
              You haven't submitted any civic issues yet. Help improve your community by reporting problems when you see them.
            </p>
            <Button onClick={() => window.location.href = '/complaints/new'} variant="outline">
              Report Your First Issue
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {complaints.map(c => (
            <Card key={c.id} className="hover:shadow-md transition-all hover:border-slate-300 cursor-pointer group" onClick={() => window.location.href = `/complaints/${c.id}`}>
              <CardContent className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <Badge variant={getStatusBadgeVariant(c.status)} className="capitalize">
                    {c.status.replace(/_/g, ' ')}
                  </Badge>
                  <span className="text-[10px] text-slate-400 font-medium flex items-center gap-1 bg-slate-50 px-2 py-1 rounded">
                    <Calendar className="h-3 w-3" />
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <h3 className="font-bold text-lg text-slate-900 mb-1 group-hover:text-civic-700 transition-colors line-clamp-1">
                  {c.title}
                </h3>
                
                <p className="text-xs text-slate-500 capitalize mb-3 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                  {c.category.replace(/_/g, ' ')}
                </p>
                
                <p className="text-sm text-slate-600 line-clamp-2 mb-4 leading-relaxed">
                  {c.description}
                </p>
                
                <div className="pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
                  <p className="text-slate-500 font-mono text-[10px]">ID: {c.id.slice(0, 8)}...</p>
                  <span className="text-civic-600 font-medium flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    View Details
                    <ArrowRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
