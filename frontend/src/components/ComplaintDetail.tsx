import React, { useEffect, useState } from 'react';
import { complaintsApi } from '../api/complaints';
import { intelligenceApi } from '../api/intelligence';
import type { ComplaintResponse, StatusHistoryResponse, EvidenceResponse, AIAnalysisResponse } from '../api/complaints';
import type { IntelligenceResponse } from '../api/intelligence';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  FileText, MapPin, Calendar, Clock, Upload, Paperclip, 
  Bot, AlertTriangle, Link as LinkIcon, Network, CheckCircle2, XCircle, Loader2
} from 'lucide-react';

export const ComplaintDetail: React.FC<{ complaintId: string }> = ({ complaintId }) => {
  const [complaint, setComplaint] = useState<ComplaintResponse | null>(null);
  const [history, setHistory] = useState<StatusHistoryResponse[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [aiAnalyses, setAiAnalyses] = useState<AIAnalysisResponse[]>([]);
  const [intelligence, setIntelligence] = useState<IntelligenceResponse | null>(null);
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [complaintId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [complaintData, historyData, evidenceData, aiData] = await Promise.all([
        complaintsApi.getById(complaintId),
        complaintsApi.getHistory(complaintId),
        complaintsApi.listEvidence(complaintId),
        complaintsApi.getAIAnalysis(complaintId)
      ]);
      setComplaint(complaintData);
      setHistory(historyData);
      setEvidenceList(evidenceData);
      setAiAnalyses(aiData);
      
      // Load intelligence safely (might 404 if not yet processed)
      try {
        const intel = await intelligenceApi.getForComplaint(complaintId);
        setIntelligence(intel);
      } catch (e) {
        console.log("No intelligence found yet.");
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load complaint details');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setUploading(true);
    setUploadError(null);
    try {
      await complaintsApi.uploadEvidence(complaintId, file);
      // Reload data to get new evidence and new AI analysis status
      await loadData();
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload evidence');
    } finally {
      setUploading(false);
      if (e.target) e.target.value = ''; // clear input
    }
  };



  const getStatusBadgeVariant = (status: string) => {
    switch(status.toLowerCase()) {
      case 'submitted': return 'secondary';
      case 'assigned': return 'info';
      case 'in_progress': return 'warning';
      case 'resolved': return 'success';
      case 'closed': return 'default';
      case 'rejected': return 'destructive';
      default: return 'outline';
    }
  };

  const getStatusExplanation = (status: string) => {
    switch(status.toLowerCase()) {
      case 'submitted': return "Your report has been successfully recorded in the system.";
      case 'assigned': return "Your report has been assigned to the responsible department.";
      case 'in_progress': return "Your complaint is currently being worked on by the responsible civic authority.";
      case 'resolved': return "The authority has marked this problem as fixed.";
      case 'closed': return "This report has been officially closed.";
      case 'rejected': return "This report was rejected. See the reason for details.";
      default: return "";
    }
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-slate-500 space-y-4">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-civic-600 rounded-full animate-spin"></div>
        <p className="text-sm font-medium">Retrieving issue dossier...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg text-sm font-medium flex items-center gap-3">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      </div>
    );
  }

  if (!complaint) return <div className="p-4 text-center text-slate-500 font-medium">Complaint not found</div>;

  return (
    <div className="max-w-5xl mx-auto py-6 space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <Badge variant={getStatusBadgeVariant(complaint.status)} className="capitalize px-3 py-1 text-sm">
              {complaint.status.replace(/_/g, ' ')}
            </Badge>
            <span className="text-sm font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">ID: {complaint.id.slice(0, 8)}</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight line-clamp-2">{complaint.title}</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Info Column */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Details Card */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-slate-500" />
                Issue Description
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <p className="text-slate-700 whitespace-pre-wrap leading-relaxed text-[15px]">
                {complaint.description}
              </p>
              
              <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-6 text-sm">
                <div>
                  <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Category</p>
                  <p className="font-medium text-slate-900 capitalize flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-civic-500"></span>
                    {complaint.category.replace(/_/g, ' ')}
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Submitted At</p>
                  <p className="font-medium text-slate-900 flex items-center gap-1.5">
                    <Calendar className="h-4 w-4 text-slate-400" />
                    {new Date(complaint.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="sm:col-span-2 pt-2 border-t border-slate-200">
                  <p className="font-semibold text-slate-400 uppercase tracking-wider mb-1 text-[10px]">Location</p>
                  <p className="font-medium text-slate-900 flex items-start gap-1.5">
                    <MapPin className="h-4 w-4 text-civic-500 mt-0.5 shrink-0" />
                    <span>
                      {complaint.location.address || 'Address not provided'}
                      <span className="block text-xs font-mono text-slate-400 mt-1 font-normal">
                        Lat: {complaint.location.geo.coordinates[1].toFixed(4)}, Lng: {complaint.location.geo.coordinates[0].toFixed(4)}
                      </span>
                    </span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Intelligence Card */}
          <Card className="border-indigo-100 overflow-hidden">
            <CardHeader className="bg-indigo-50/50 border-b border-indigo-100 pb-4">
              <div className="flex justify-between items-center">
                <CardTitle className="text-indigo-900 flex items-center gap-2">
                  <Network className="h-5 w-5 text-indigo-500" />
                  Civic Problem Network
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-4 p-0">
              {intelligence ? (
                <div className="divide-y divide-indigo-100">
                  {intelligence.cluster && (
                    <div className="p-5 bg-indigo-50/30">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                          <Network className="h-5 w-5" />
                        </div>
                        <div>
                          <h3 className="font-bold text-indigo-900">Incident Cluster Detected</h3>
                          <p className="text-sm text-indigo-700 mt-1">This issue is part of a larger, systemic incident containing <strong className="font-bold">{intelligence.cluster.member_complaint_ids.length}</strong> related reports.</p>
                          <p className="text-[10px] font-mono text-indigo-400 mt-2 bg-indigo-50 inline-block px-2 py-0.5 rounded border border-indigo-100">Cluster ID: {intelligence.cluster.cluster_id}</p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="p-5">
                    <h4 className="font-semibold text-slate-800 mb-3 text-sm flex items-center gap-2">
                      <LinkIcon className="h-4 w-4 text-slate-400" />
                      Semantic Relationships
                    </h4>
                    {intelligence.relations.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {intelligence.relations.map(rel => (
                          <div key={rel.id} className="p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 transition-colors shadow-sm">
                            <div className="flex justify-between items-center mb-3">
                              <Badge variant={rel.relation_type === 'duplicate' ? 'destructive' : 'warning'} className="uppercase text-[10px] tracking-wider">
                                {rel.relation_type.replace('_', ' ')}
                              </Badge>
                              <span className="text-slate-400 text-[10px] font-medium">{new Date(rel.created_at).toLocaleDateString()}</span>
                            </div>
                            <p className="text-sm text-slate-700 mb-3 line-clamp-2">{rel.explanation}</p>
                            
                            <div className="grid grid-cols-3 gap-2 mb-4 p-2 bg-slate-50 rounded-lg border border-slate-100">
                              <div className="text-center">
                                <p className="text-[9px] uppercase font-bold text-slate-400">Match</p>
                                <p className="text-xs font-semibold text-slate-700">{(rel.semantic_similarity * 100).toFixed(0)}%</p>
                              </div>
                              <div className="text-center border-l border-r border-slate-200">
                                <p className="text-[9px] uppercase font-bold text-slate-400">Dist</p>
                                <p className="text-xs font-semibold text-slate-700">{rel.geographic_distance_meters !== null ? `${rel.geographic_distance_meters.toFixed(0)}m` : 'N/A'}</p>
                              </div>
                              <div className="text-center">
                                <p className="text-[9px] uppercase font-bold text-slate-400">Time</p>
                                <p className="text-xs font-semibold text-slate-700">{rel.temporal_distance_days.toFixed(1)}d</p>
                              </div>
                            </div>
                            
                            <Button variant="outline" size="sm" className="w-full text-xs h-8 border-indigo-200 text-indigo-700 hover:bg-indigo-50" onClick={() => window.location.href = `/complaints/${rel.complaint_a_id === complaintId ? rel.complaint_b_id : rel.complaint_a_id}`}>
                              View Related Report
                            </Button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-500 text-sm italic">No duplicates or related complaints detected in your area.</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-500">
                  <Bot className="h-10 w-10 mx-auto text-slate-300 mb-3" />
                  <p className="text-sm font-medium">Analyzing problem network...</p>
                </div>
              )}
            </CardContent>
          </Card>

        </div>

        {/* Sidebar Column */}
        <div className="space-y-6">
          
          {/* Status History */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100">
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="h-4 w-4 text-slate-500" />
                Status Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 px-4">
              <div className="space-y-4">
                {history.map((h, i) => (
                  <div key={h.id} className="relative pl-6 pb-4 last:pb-0">
                    {/* Timeline Line */}
                    {i !== history.length - 1 && (
                      <div className="absolute left-2 top-6 bottom-0 w-px bg-slate-200"></div>
                    )}
                    {/* Timeline Dot */}
                    <div className={`absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-white shadow-sm ${
                      i === 0 ? 'bg-civic-500' : 'bg-slate-300'
                    }`}></div>
                    
                    <div className="flex flex-col">
                      <span className="font-bold text-slate-800 text-sm">{h.new_status.toUpperCase().replace('_', ' ')}</span>
                      <span className="text-[10px] text-slate-400 font-medium">{new Date(h.created_at).toLocaleString()}</span>
                      <p className="text-xs text-slate-500 mt-1">{getStatusExplanation(h.new_status)}</p>
                      {h.reason && (
                        <p className="text-xs text-slate-600 mt-1.5 p-2 bg-slate-50 rounded border border-slate-100 italic">
                          "{h.reason}"
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Evidence Upload */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100">
              <CardTitle className="text-sm flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Paperclip className="h-4 w-4 text-slate-500" />
                  Evidence
                </span>
                <Badge variant="secondary" className="rounded-full text-[10px]">{evidenceList.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {/* Upload Input */}
              <div className="relative border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:bg-slate-50 transition-colors">
                <input 
                  type="file" 
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  accept="image/jpeg, image/png, image/webp, application/pdf"
                />
                <div className="flex flex-col items-center justify-center pointer-events-none">
                  {uploading ? (
                    <><Loader2 className="h-6 w-6 text-civic-500 animate-spin mb-2" />
                    <span className="text-sm font-medium text-slate-600">Uploading...</span></>
                  ) : (
                    <><Upload className="h-6 w-6 text-slate-400 mb-2" />
                    <span className="text-sm font-medium text-slate-700">Click to upload evidence</span>
                    <span className="text-[10px] text-slate-400 mt-1">JPEG, PNG, WEBP, PDF (Max 5MB)</span></>
                  )}
                </div>
              </div>
              {uploadError && <div className="text-xs text-red-600 font-medium text-center">{uploadError}</div>}

              {/* Evidence List */}
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {evidenceList.map(ev => (
                  <div key={ev.id} className="p-3 bg-white rounded-lg border border-slate-200 text-sm shadow-sm flex items-start gap-3">
                    {ev.mime_type && ev.mime_type.startsWith('image/') ? (
                      <div className="h-16 w-16 flex-shrink-0 rounded-md overflow-hidden bg-slate-100 border border-slate-200 cursor-pointer" onClick={() => window.open(complaintsApi.getEvidenceDownloadUrl(complaintId, ev.id), '_blank')}>
                        <img 
                          src={complaintsApi.getEvidenceDownloadUrl(complaintId, ev.id)} 
                          alt={ev.original_filename} 
                          className="h-full w-full object-cover hover:opacity-90 transition-opacity"
                          crossOrigin="use-credentials"
                        />
                      </div>
                    ) : (
                      <div className="p-2 bg-slate-100 text-slate-500 rounded flex-shrink-0">
                        <FileText className="h-4 w-4" />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-slate-800 text-xs truncate">{ev.original_filename}</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">{(ev.size_bytes / 1024 / 1024).toFixed(2)} MB • {new Date(ev.created_at).toLocaleDateString()}</p>
                      <a 
                        href={complaintsApi.getEvidenceDownloadUrl(complaintId, ev.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[10px] text-civic-600 hover:text-civic-700 mt-1 inline-block font-medium"
                      >
                        View Full Size
                      </a>
                    </div>
                  </div>
                ))}
                {evidenceList.length === 0 && !uploading && (
                  <p className="text-slate-400 text-xs text-center py-2">No evidence uploaded yet.</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* AI Analysis List */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100">
              <CardTitle className="text-sm flex items-center gap-2">
                <Bot className="h-4 w-4 text-slate-500" />
                AI Evidence Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              {aiAnalyses.length === 0 ? (
                <p className="text-slate-500 text-xs text-center py-4 bg-slate-50 rounded border border-slate-100">Upload evidence to automatically trigger AI Analysis.</p>
              ) : (
                aiAnalyses.map(ai => (
                  <div key={ai.id} className={`p-4 rounded-xl border ${
                    ai.status === 'completed' ? 'border-green-200 bg-green-50/50' : 
                    ai.status === 'failed' ? 'border-red-200 bg-red-50' : 
                    'border-amber-200 bg-amber-50/50'
                  }`}>
                    <div className="flex justify-between items-center mb-3">
                      <Badge variant={ai.status === 'completed' ? 'success' : ai.status === 'failed' ? 'destructive' : 'warning'} className="text-[10px] uppercase">
                        {ai.status}
                      </Badge>
                      <span className="text-[9px] text-slate-500 font-medium">{new Date(ai.created_at).toLocaleString()}</span>
                    </div>
                    
                    {ai.status === 'completed' && ai.result && (
                      <div className="space-y-2">
                        <div>
                          <p className="text-[10px] uppercase font-bold text-slate-400">Category Detected</p>
                          <p className="text-sm font-semibold text-slate-800 capitalize">{ai.result.category.replace(/_/g, ' ')}</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase font-bold text-slate-400">Summary</p>
                          <p className="text-xs text-slate-700 leading-relaxed">{ai.result.summary}</p>
                        </div>
                        
                        <div className="flex items-center gap-2 pt-2 border-t border-green-100 mt-2">
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          <span className="text-xs font-semibold text-green-700">{(ai.confidence! * 100).toFixed(0)}% Confidence</span>
                        </div>
                      </div>
                    )}
                    
                    {ai.status === 'processing' && (
                      <div className="flex items-center gap-2 text-sm text-amber-700">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        AI is analyzing the evidence...
                      </div>
                    )}
                    
                    {ai.status === 'failed' && (
                      <div className="flex items-center gap-2 text-sm text-red-700">
                        <XCircle className="h-4 w-4" />
                        Analysis failed to process.
                      </div>
                    )}
                  </div>
                ))
              )}
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};
