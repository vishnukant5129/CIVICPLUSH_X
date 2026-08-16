import React, { useState, useEffect } from 'react';
import { authorityApi } from '../api/authority';
import type { AuthorityDashboardSummary, AuthorityQueueResponse, AuthorityComplaintDetail } from '../api/authority';
import { PredictiveIntelligence } from './PredictiveIntelligence';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Label } from './ui/Label';
import { Badge } from './ui/Badge';
import { 
  Shield, 
  Search, 
  Inbox, 
  UserCheck, 
  Clock, 
  CheckCircle, 
  Archive, 
  FolderLock, 
  MapPin, 
  Calendar,
  X,
  Send,
  Download,
  AlertCircle
} from 'lucide-react';

export const AuthorityDashboard: React.FC = () => {
  const [summary, setSummary] = useState<AuthorityDashboardSummary | null>(null);
  const [queue, setQueue] = useState<AuthorityQueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Pagination States
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Detail & Action Modal States
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AuthorityComplaintDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [statusNote, setStatusNote] = useState('');
  const [targetStatus, setTargetStatus] = useState('');
  const [assignDept, setAssignDept] = useState('');
  const [assignOfficer, setAssignOfficer] = useState('');
  const [departments, setDepartments] = useState<Array<{ id: string; department_id: string; name: string }>>([]);

  const loadSummary = async () => {
    try {
      const data = await authorityApi.getSummary();
      setSummary(data);
    } catch (err: any) {
      console.error('Summary error:', err);
    }
  };

  const loadQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await authorityApi.getComplaintQueue({
        status: statusFilter,
        category: categoryFilter,
        assignment: assignmentFilter,
        search: searchQuery,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        page_size: 15,
      });
      setQueue(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load complaint queue.');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      const depts = await authorityApi.listDepartments();
      setDepartments(depts);
    } catch (err: any) {
      console.error('Failed to load depts:', err);
    }
  };

  useEffect(() => {
    loadSummary();
    loadDepartments();
  }, []);

  useEffect(() => {
    loadQueue();
  }, [statusFilter, categoryFilter, assignmentFilter, searchQuery, page, sortBy, sortOrder]);

  const openDetail = async (id: string) => {
    setSelectedId(id);
    setLoadingDetail(true);
    try {
      const data = await authorityApi.getComplaintDetail(id);
      setDetail(data);
      setTargetStatus(data.complaint.status);
      setAssignDept(data.assignment?.department_id || '');
      setAssignOfficer(data.assignment?.assigned_authority_id || '');
    } catch (err: any) {
      alert(err.message || 'Failed to load case details.');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedId || !targetStatus) return;
    try {
      await authorityApi.updateStatus(selectedId, targetStatus, statusNote);
      alert('Status updated successfully!');
      setStatusNote('');
      openDetail(selectedId);
      loadSummary();
      loadQueue();
    } catch (err: any) {
      alert(err.message || 'Status update failed.');
    }
  };

  const handleAssign = async () => {
    if (!selectedId || !assignDept || !assignOfficer) {
      alert('Please provide both department ID and authority officer ID.');
      return;
    }
    try {
      await authorityApi.assignComplaint(selectedId, assignDept, assignOfficer);
      alert('Case assigned successfully!');
      openDetail(selectedId);
      loadSummary();
      loadQueue();
    } catch (err: any) {
      alert(err.message || 'Assignment failed.');
    }
  };

  const handleExternalDelivery = async () => {
    if (!selectedId) return;
    try {
      const res = await authorityApi.triggerExternalDelivery(selectedId);
      alert(`Integration Response: Status = ${res.status || 'Processed'}`);
      openDetail(selectedId);
    } catch (err: any) {
      alert(err.message || 'External delivery failed.');
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

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header & Scope Banner */}
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-md relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <Shield className="h-40 w-40" />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-400" />
              Authority Operations Command
            </h1>
            <p className="text-slate-400 text-sm mt-2 max-w-2xl">
              Centralized case management, department routing, authority assignments, and operational intelligence.
            </p>
          </div>
          {summary && (
            <div className="bg-slate-800/80 backdrop-blur-sm border border-slate-700 px-4 py-2 rounded-lg flex items-center gap-2">
              <FolderLock className="h-4 w-4 text-slate-300" />
              <span className="text-sm font-medium text-slate-200">
                {summary.scope_note}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <Card className="bg-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <Inbox className="h-6 w-6 text-slate-400 mb-2" />
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Scope</span>
              <p className="text-2xl font-black text-slate-900 mt-1">{summary.total_complaints}</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-amber-500 bg-gradient-to-br from-amber-50/50 to-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <AlertCircle className="h-6 w-6 text-amber-500 mb-2" />
              <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider">Unassigned</span>
              <p className="text-2xl font-black text-amber-900 mt-1">{summary.unassigned_count}</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-blue-500 bg-gradient-to-br from-blue-50/50 to-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <UserCheck className="h-6 w-6 text-blue-500 mb-2" />
              <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider">Assigned To Me</span>
              <p className="text-2xl font-black text-blue-900 mt-1">{summary.assigned_to_me_count}</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-purple-500 bg-gradient-to-br from-purple-50/50 to-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <Clock className="h-6 w-6 text-purple-500 mb-2" />
              <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">In Progress</span>
              <p className="text-2xl font-black text-purple-900 mt-1">{summary.in_progress_count}</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500 bg-gradient-to-br from-green-50/50 to-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <CheckCircle className="h-6 w-6 text-green-500 mb-2" />
              <span className="text-[11px] font-bold text-green-700 uppercase tracking-wider">Resolved</span>
              <p className="text-2xl font-black text-green-900 mt-1">{summary.resolved_count}</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-slate-500 bg-gradient-to-br from-slate-50/50 to-white">
            <CardContent className="p-4 flex flex-col items-center text-center justify-center h-full">
              <Archive className="h-6 w-6 text-slate-500 mb-2" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Closed</span>
              <p className="text-2xl font-black text-slate-800 mt-1">{summary.closed_count}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Complaint Queue Section */}
      <Card className="shadow-sm border-slate-200">
        <CardHeader className="border-b border-slate-100 bg-slate-50/50 pb-4">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <CardTitle className="text-xl flex items-center gap-2">
              <FolderLock className="h-5 w-5 text-slate-500" />
              Complaint Queue
            </CardTitle>

            {/* Search Box */}
            <div className="w-full md:w-80 relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                type="text"
                placeholder="Search by title, description, ID..."
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                className="pl-9 bg-white"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {/* Filter Controls Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 p-4 bg-slate-50 border-b border-slate-100">
            <div>
              <Label className="text-[10px] uppercase text-slate-500 mb-1.5 block">Status</Label>
              <Select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                className="bg-white h-9 text-sm"
              >
                <option value="">All Statuses</option>
                <option value="submitted">Submitted</option>
                <option value="assigned">Assigned</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
                <option value="rejected">Rejected</option>
              </Select>
            </div>

            <div>
              <Label className="text-[10px] uppercase text-slate-500 mb-1.5 block">Category</Label>
              <Select
                value={categoryFilter}
                onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
                className="bg-white h-9 text-sm"
              >
                <option value="">All Categories</option>
                <option value="pothole_road_damage">Pothole & Road Damage</option>
                <option value="streetlight_electricity">Streetlight & Electricity</option>
                <option value="water_leakage">Water Leakage</option>
                <option value="sewage_drainage">Sewage & Drainage</option>
                <option value="garbage_waste">Garbage & Waste</option>
                <option value="public_infrastructure">Public Infrastructure</option>
              </Select>
            </div>

            <div>
              <Label className="text-[10px] uppercase text-slate-500 mb-1.5 block">Assignment Scope</Label>
              <Select
                value={assignmentFilter}
                onChange={(e) => { setAssignmentFilter(e.target.value); setPage(1); }}
                className="bg-white h-9 text-sm"
              >
                <option value="">All Scope</option>
                <option value="me">Assigned to Me</option>
                <option value="unassigned">Unassigned</option>
              </Select>
            </div>

            <div>
              <Label className="text-[10px] uppercase text-slate-500 mb-1.5 block">Sort By</Label>
              <Select
                value={`${sortBy}:${sortOrder}`}
                onChange={(e) => {
                  const [sb, so] = e.target.value.split(':');
                  setSortBy(sb);
                  setSortOrder(so);
                  setPage(1);
                }}
                className="bg-white h-9 text-sm"
              >
                <option value="created_at:desc">Newest First</option>
                <option value="created_at:asc">Oldest First</option>
                <option value="status:asc">Status</option>
                <option value="category:asc">Category</option>
              </Select>
            </div>
          </div>

          {/* Paginated Table */}
          {loading ? (
            <div className="py-16 flex flex-col items-center justify-center text-slate-500 space-y-3">
              <div className="w-8 h-8 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
              <p className="text-sm font-medium">Loading complaints queue...</p>
            </div>
          ) : error ? (
            <div className="p-6">
              <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded text-sm flex items-center gap-3">
                <AlertCircle className="h-5 w-5" />
                {error}
              </div>
            </div>
          ) : queue && queue.items.length === 0 ? (
            <div className="py-16 flex flex-col items-center justify-center text-slate-500">
              <Inbox className="h-12 w-12 text-slate-200 mb-3" />
              <p className="font-medium">No complaints found matching current filters.</p>
            </div>
          ) : (
            queue && (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm border-collapse">
                    <thead>
                      <tr className="bg-white text-xs font-bold text-slate-500 uppercase border-b border-slate-200">
                        <th className="p-4 font-semibold tracking-wider">ID / Date</th>
                        <th className="p-4 font-semibold tracking-wider">Title & Category</th>
                        <th className="p-4 font-semibold tracking-wider">Status</th>
                        <th className="p-4 font-semibold tracking-wider">Department / Officer</th>
                        <th className="p-4 font-semibold tracking-wider text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                      {queue.items.map((item) => (
                        <tr key={item._id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="p-4">
                            <p className="font-mono text-xs font-semibold text-slate-700">{item._id.slice(0, 8)}...</p>
                            <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(item.created_at).toLocaleDateString()}
                            </p>
                          </td>
                          <td className="p-4">
                            <p className="font-semibold text-slate-900 line-clamp-1">{item.title}</p>
                            <p className="text-xs text-slate-500 capitalize mt-1 flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-slate-300"></span>
                              {item.category.replace(/_/g, ' ')}
                            </p>
                          </td>
                          <td className="p-4">
                            <Badge variant={getStatusBadgeVariant(item.status)} className="capitalize">
                              {item.status.replace(/_/g, ' ')}
                            </Badge>
                          </td>
                          <td className="p-4 text-xs">
                            {item.department_id ? (
                              <div className="space-y-1">
                                <p className="font-medium text-slate-900 flex items-center gap-1.5">
                                  <Shield className="h-3.5 w-3.5 text-slate-400" />
                                  {item.department_id}
                                </p>
                                <p className="text-slate-500 flex items-center gap-1.5">
                                  <UserCheck className="h-3.5 w-3.5 text-slate-400" />
                                  {item.assigned_authority_id || 'Unassigned officer'}
                                </p>
                              </div>
                            ) : (
                              <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">
                                Unassigned
                              </Badge>
                            )}
                          </td>
                          <td className="p-4 text-right">
                            <Button
                              onClick={() => openDetail(item._id)}
                              size="sm"
                              className="bg-slate-900 hover:bg-slate-800 text-xs"
                            >
                              Inspect & Act
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                <div className="flex justify-between items-center p-4 border-t border-slate-100 bg-slate-50 text-xs text-slate-600">
                  <p className="font-medium">
                    Showing Page {queue.page} of {queue.total_pages} <span className="text-slate-400">({queue.total} total)</span>
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={queue.page <= 1}
                      onClick={() => setPage((p) => p - 1)}
                      className="h-8 text-xs"
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={queue.page >= queue.total_pages}
                      onClick={() => setPage((p) => p + 1)}
                      className="h-8 text-xs"
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            )
          )}
        </CardContent>
      </Card>

      {/* Predictive Intelligence Section */}
      <div className="pt-4">
        <PredictiveIntelligence />
      </div>

      {/* Case Detail Drawer Overlay */}
      {selectedId && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex justify-end overflow-hidden animate-in fade-in duration-200">
          <div className="bg-slate-50 w-full max-w-2xl h-full shadow-2xl flex flex-col animate-in slide-in-from-right-8 duration-300">
            {/* Drawer Header */}
            <div className="flex justify-between items-center border-b border-slate-200 bg-white px-6 py-4 shadow-sm z-10">
              <div>
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Shield className="h-5 w-5 text-civic-600" />
                  Operational Detail
                </h3>
                <p className="text-xs font-mono text-slate-500 mt-1">ID: {selectedId}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => { setSelectedId(null); setDetail(null); }}
                className="text-slate-400 hover:text-slate-900 hover:bg-slate-100 rounded-full"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            {/* Drawer Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loadingDetail || !detail ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
                  <div className="w-8 h-8 border-4 border-slate-200 border-t-civic-600 rounded-full animate-spin"></div>
                  <p className="font-medium text-sm">Retrieving full case dossier...</p>
                </div>
              ) : (
                <div className="space-y-6 pb-20">
                  {/* Main Overview */}
                  <Card>
                    <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-xl leading-tight">{detail.complaint.title}</CardTitle>
                        <Badge variant={getStatusBadgeVariant(detail.complaint.status)} className="capitalize ml-4 shrink-0">
                          {detail.complaint.status.replace(/_/g, ' ')}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <p className="text-sm text-slate-700 whitespace-pre-wrap">{detail.complaint.description}</p>
                      
                      <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-100 text-xs grid grid-cols-2 gap-y-4 gap-x-6 text-slate-600">
                        <div>
                          <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Category</p>
                          <p className="font-medium text-slate-900 capitalize">{detail.complaint.category.replace(/_/g, ' ')}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Submitted By User</p>
                          <p className="font-mono">{detail.complaint.user_id}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Date Logged</p>
                          <p className="font-medium text-slate-900">{new Date(detail.complaint.created_at).toLocaleString()}</p>
                        </div>
                        <div className="col-span-2 pt-2 border-t border-slate-200">
                          <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Location</p>
                          <p className="font-medium text-slate-900 flex items-center gap-1.5">
                            <MapPin className="h-3.5 w-3.5 text-civic-500" />
                            {(detail as any).complaint?.location?.address || 'Location unavailable'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-1 gap-6">
                    {/* Status Update Form */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Update Complaint Status</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 pt-0">
                        <div className="flex gap-3">
                          <Select
                            value={targetStatus}
                            onChange={(e) => setTargetStatus(e.target.value)}
                            className="flex-1 text-sm"
                          >
                            <option value="submitted">Submitted</option>
                            <option value="assigned">Assigned</option>
                            <option value="in_progress">In Progress</option>
                            <option value="resolved">Resolved</option>
                            <option value="closed">Closed</option>
                            <option value="rejected">Rejected</option>
                          </Select>
                          <Button onClick={handleUpdateStatus} className="shrink-0 bg-civic-600 hover:bg-civic-700">
                            Apply Update
                          </Button>
                        </div>
                        <Input
                          type="text"
                          placeholder="Required audit note / resolution explanation..."
                          value={statusNote}
                          onChange={(e) => setStatusNote(e.target.value)}
                          className="w-full text-sm"
                        />
                      </CardContent>
                    </Card>

                    {/* Assignment Form */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Assign Case to Authority</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3 pt-0">
                        <div className="flex gap-3">
                          <Select
                            value={assignDept}
                            onChange={(e) => setAssignDept(e.target.value)}
                            className="flex-1 text-sm"
                          >
                            <option value="">Select Department...</option>
                            {departments.map((d) => (
                              <option key={d.id} value={d.department_id || d.id}>
                                {d.name} ({d.department_id || d.id})
                              </option>
                            ))}
                          </Select>
                          <Input
                            type="text"
                            placeholder="Officer ID"
                            value={assignOfficer}
                            onChange={(e) => setAssignOfficer(e.target.value)}
                            className="w-1/3 text-sm"
                          />
                        </div>
                        <Button onClick={handleAssign} variant="outline" className="w-full border-slate-300 text-slate-700 hover:bg-slate-50">
                          Commit Assignment
                        </Button>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Evidence Attachments */}
                  <Card>
                    <CardHeader className="pb-3 border-b border-slate-100">
                      <CardTitle className="text-sm flex items-center justify-between">
                        Evidence Attachments
                        <Badge variant="secondary" className="rounded-full">{detail.evidence.length}</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4">
                      {detail.evidence.length === 0 ? (
                        <p className="text-sm text-slate-400 italic text-center py-4 bg-slate-50 rounded border border-dashed border-slate-200">
                          No evidence attached to this case.
                        </p>
                      ) : (
                        <ul className="space-y-2">
                          {detail.evidence.map((ev: any) => (
                            <li key={ev._id} className="flex justify-between items-center p-3 bg-white rounded-lg border border-slate-200 shadow-sm hover:border-slate-300 transition-colors">
                              <div className="flex items-center gap-3 overflow-hidden">
                                <div className="p-2 bg-slate-100 text-slate-500 rounded">
                                  <FolderLock className="h-4 w-4" />
                                </div>
                                <div className="min-w-0">
                                  <p className="text-sm font-medium text-slate-900 truncate">{ev.original_filename}</p>
                                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-0.5">{ev.mime_type}</p>
                                </div>
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                className="shrink-0 ml-4 border-slate-200 text-slate-700 hover:bg-slate-50 h-8"
                                onClick={() => window.open(`/api/v1/authority/evidence/${ev._id}/download`, '_blank')}
                              >
                                <Download className="h-3.5 w-3.5 mr-1.5" />
                                Download
                              </Button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </CardContent>
                  </Card>

                  {/* Government Integration & Delivery */}
                  <Card className="border-amber-200">
                    <CardHeader className="pb-3 border-b border-amber-100 bg-amber-50/30">
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-sm text-amber-900">Municipal Integration</CardTitle>
                        <Button
                          size="sm"
                          onClick={handleExternalDelivery}
                          className="bg-amber-600 hover:bg-amber-700 text-white h-8 text-xs"
                        >
                          <Send className="h-3 w-3 mr-1.5" />
                          Trigger Delivery
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      {detail.external_delivery ? (
                        <div className="grid grid-cols-2 gap-4 text-sm bg-amber-50/50 p-3 rounded border border-amber-100">
                          <div>
                            <p className="text-[10px] uppercase font-bold text-amber-700/70 mb-1">Provider</p>
                            <p className="font-medium text-amber-900">{detail.external_delivery.provider}</p>
                          </div>
                          <div>
                            <p className="text-[10px] uppercase font-bold text-amber-700/70 mb-1">Status</p>
                            <Badge variant="outline" className="text-amber-800 border-amber-300 bg-amber-100">
                              {detail.external_delivery.status}
                            </Badge>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-slate-500">Not yet delivered to external government API.</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Immutable Audit Trail */}
                  <Card>
                    <CardHeader className="pb-3 border-b border-slate-100">
                      <CardTitle className="text-sm flex items-center justify-between">
                        Audit Trail Log
                        <Badge variant="secondary" className="rounded-full text-[10px]">{detail.audit_trail.length} records</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0 px-0">
                      {detail.audit_trail.length === 0 ? (
                        <p className="text-sm text-slate-400 italic text-center py-6 px-6">
                          No audit records logged yet.
                        </p>
                      ) : (
                        <div className="max-h-64 overflow-y-auto divide-y divide-slate-100">
                          {detail.audit_trail.map((at: any) => (
                            <div key={at._id} className="p-4 hover:bg-slate-50 transition-colors">
                              <div className="flex justify-between items-start mb-1">
                                <p className="font-semibold text-slate-800 text-sm">
                                  {at.action_type.toUpperCase().replace(/_/g, ' ')}
                                </p>
                                <span className="text-[10px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                                  {new Date(at.created_at).toLocaleString()}
                                </span>
                              </div>
                              <p className="text-xs text-slate-500 mb-2">Actor ID: <span className="font-mono text-slate-600">{at.actor_id}</span></p>
                              {at.note && (
                                <div className="mt-2 bg-white p-2.5 rounded border border-slate-200 text-xs text-slate-700 italic">
                                  "{at.note}"
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
