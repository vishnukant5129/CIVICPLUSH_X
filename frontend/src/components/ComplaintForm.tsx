import React, { useState, useEffect } from 'react';
import { complaintsApi } from '../api/complaints';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Label } from './ui/Label';
import { Textarea } from './ui/Textarea';
import { Select } from './ui/Select';
import { MapPin, FileText, CheckCircle2, AlertTriangle, Loader2, Upload, X, ChevronLeft } from 'lucide-react';

const CATEGORIES = [
  { value: 'pothole_road_damage', label: 'Pothole & Road Damage' },
  { value: 'streetlight_electricity', label: 'Streetlight & Electricity' },
  { value: 'water_leakage', label: 'Water Leakage' },
  { value: 'sewage_drainage', label: 'Sewage & Drainage' },
  { value: 'garbage_waste', label: 'Garbage & Waste' },
  { value: 'public_infrastructure', label: 'Public Infrastructure' },
  { value: 'traffic_signage', label: 'Traffic Signage' },
  { value: 'other', label: 'Other' },
];

export const ComplaintForm: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0].value);
  const [address, setAddress] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successId, setSuccessId] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  
  const [step, setStep] = useState<'form' | 'review'>('form');
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [capturingLocation, setCapturingLocation] = useState(false);

  const captureLocation = async () => {
    setCapturingLocation(true);
    setLocationError(null);
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000 });
      });
      setLocation({ lat: position.coords.latitude, lng: position.coords.longitude });
    } catch (err: any) {
      setLocationError("Unable to access your location. Please enable location permission and try again.");
    } finally {
      setCapturingLocation(false);
    }
  };

  useEffect(() => {
    captureLocation();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const selectedFiles = Array.from(e.target.files);
    
    const validFiles = selectedFiles.filter(f => {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
        alert(`${f.name} has an unsupported file type. Use JPG, PNG, or WEBP.`);
        return false;
      }
      if (f.size > 5 * 1024 * 1024) {
        alert(`${f.name} exceeds the 5MB size limit.`);
        return false;
      }
      return true;
    });

    setFiles(prev => [...prev, ...validFiles]);
    if (e.target) e.target.value = '';
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (title.length < 5) throw new Error("Title must be at least 5 characters.");
      if (description.length < 10) throw new Error("Description must be at least 10 characters.");
      if (!location) throw new Error("Location must be captured before submission.");

      const payload = {
        title,
        description,
        category,
        location: {
          address,
          geo: {
            type: 'Point' as const,
            coordinates: [location.lng, location.lat] as [number, number]
          }
        }
      };

      const result = await complaintsApi.create(payload);
      const newComplaintId = result.id;
      
      // Upload evidence
      if (files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          try {
            setUploadProgress(`Uploading ${i + 1} of ${files.length} images...`);
            await complaintsApi.uploadEvidence(newComplaintId, files[i]);
          } catch (uploadErr) {
            console.error('Failed to upload an image', uploadErr);
          }
        }
      }
      setSuccessId(newComplaintId);
    } catch (err: any) {
      setError(err.message || 'Failed to submit complaint');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReviewRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!location) {
      setError("Please enable location services and capture your location.");
      return;
    }
    setStep('review');
  };

  if (successId) {
    return (
      <Card className="max-w-2xl mx-auto mt-10 border-green-200 bg-green-50 shadow-sm animate-in fade-in slide-in-from-bottom-4">
        <CardContent className="flex flex-col items-center justify-center p-10 text-center space-y-4">
          <div className="bg-green-100 p-4 rounded-full">
            <CheckCircle2 className="h-12 w-12 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-green-900 tracking-tight">REPORT SUBMITTED</h2>
          <div className="bg-white px-6 py-4 rounded-lg shadow-sm border border-green-200 text-center w-full max-w-sm mt-4">
            <p className="text-sm text-green-700 font-medium mb-1">Complaint ID:</p>
            <p className="text-2xl font-mono font-bold text-green-900">{successId}</p>
          </div>
          <p className="text-green-700 max-w-md mt-4">
            Your report has been submitted successfully and routed to the appropriate authority.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 mt-6 w-full sm:w-auto">
            <Button onClick={() => window.location.href = `/complaints/${successId}`} className="bg-green-600 hover:bg-green-700">
              Track Status
            </Button>
            <Button onClick={() => window.location.href = '/dashboard'} variant="outline" className="border-green-300 text-green-700 hover:bg-green-100 hover:text-green-800">
              Return to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <FileText className="h-8 w-8 text-civic-600" />
          Report a Civic Problem
        </h1>
        <p className="text-gray-500 mt-2">Help improve your community by submitting detailed reports of civic infrastructure issues.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-start gap-3 shadow-sm animate-in fade-in">
          <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Submission Error</h4>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      <Card className="shadow-sm">
        <CardHeader className="bg-gray-50/50 border-b border-gray-100">
          <CardTitle>Issue Details</CardTitle>
          <CardDescription>Provide clear information so authorities can respond effectively.</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          {step === 'form' ? (
          <form onSubmit={handleReviewRequest} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Issue Title <span className="text-red-500">*</span></Label>
              <Input
                id="title"
                required
                minLength={5}
                maxLength={300}
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g., Deep pothole on Main St causing traffic hazard"
                className="text-base"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category <span className="text-red-500">*</span></Label>
              <Select
                id="category"
                required
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="text-base"
              >
                {CATEGORIES.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Detailed Description <span className="text-red-500">*</span></Label>
              <Textarea
                id="description"
                required
                minLength={10}
                maxLength={5000}
                rows={5}
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Please describe the problem in detail. Include any specific landmarks, the severity of the issue, and how long it has been present..."
                className="resize-y text-base leading-relaxed"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Approximate Address or Landmark <span className="text-red-500">*</span></Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  id="address"
                  required
                  className="pl-10 text-base"
                  value={address}
                  onChange={e => setAddress(e.target.value)}
                  placeholder="e.g., Near City Hall, 100 Main St"
                />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-gray-100">
              <Label>LOCATION <span className="text-red-500">*</span></Label>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                {capturingLocation ? (
                  <div className="flex items-center gap-3 text-slate-500">
                    <Loader2 className="h-5 w-5 animate-spin text-civic-600" />
                    <span className="text-sm">Capturing location securely...</span>
                  </div>
                ) : locationError ? (
                  <div className="flex flex-col gap-3 text-red-600 text-sm">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      <span>{locationError}</span>
                    </div>
                    <Button type="button" variant="outline" size="sm" onClick={captureLocation} className="w-fit">
                      Retry Location
                    </Button>
                  </div>
                ) : location ? (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-3 text-emerald-700">
                      <CheckCircle2 className="h-5 w-5" />
                      <div>
                        <span className="text-sm font-semibold block">Location captured</span>
                        <span className="text-xs font-mono">Lat: {location.lat.toFixed(6)} | Lng: {location.lng.toFixed(6)}</span>
                      </div>
                    </div>
                    <Button type="button" variant="outline" size="sm" onClick={captureLocation}>
                      Refresh Location
                    </Button>
                  </div>
                ) : null}
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-gray-100">
              <Label>ADD EVIDENCE <span className="text-gray-500 font-normal">(Optional)</span></Label>
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:bg-gray-50 transition-colors relative cursor-pointer">
                <input 
                  type="file" 
                  multiple 
                  accept="image/jpeg, image/png, image/webp" 
                  capture="environment"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                  onChange={handleFileChange}
                  disabled={submitting}
                />
                <div className="flex flex-col items-center justify-center pointer-events-none">
                  <Upload className="h-8 w-8 text-gray-400 mb-3" />
                  <p className="font-semibold text-gray-700">📷 Add Photos</p>
                  <p className="text-sm text-gray-500 mt-1">Upload photos showing the civic problem.</p>
                  <p className="text-xs text-gray-400 mt-1">JPG, PNG, WEBP (Max 5MB)</p>
                </div>
              </div>

              {files.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4">
                  {files.map((file, index) => (
                    <div key={index} className="relative group rounded-lg overflow-hidden border border-gray-200 bg-gray-50 aspect-video flex items-center justify-center">
                      <img 
                        src={URL.createObjectURL(file)} 
                        alt={`Evidence ${index + 1}`} 
                        className="w-full h-full object-cover"
                        onLoad={(e) => URL.revokeObjectURL((e.target as HTMLImageElement).src)}
                      />
                      <button 
                        type="button" 
                        onClick={() => removeFile(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-90 hover:opacity-100 hover:bg-red-600 shadow-sm"
                        disabled={submitting}
                      >
                        <X className="h-4 w-4" />
                      </button>
                      <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] px-2 py-1 truncate">
                        {file.name}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-6 border-t border-gray-100 flex justify-end">
              <Button
                type="submit"
                size="lg"
                className="w-full sm:w-auto bg-civic-600 hover:bg-civic-700"
              >
                Review Report
              </Button>
            </div>
          </form>
          ) : (
            <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
              <div className="bg-slate-50 p-6 rounded-xl border border-slate-100 space-y-6">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Problem</h4>
                  <p className="text-lg font-bold text-slate-900">{title}</p>
                </div>
                
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Category</h4>
                  <p className="text-sm font-medium text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-md w-fit">
                    {CATEGORIES.find(c => c.value === category)?.label}
                  </p>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Description</h4>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap bg-white p-3 border border-slate-200 rounded-md">
                    {description}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Evidence</h4>
                    <p className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <FileText className="h-4 w-4 text-slate-400" />
                      {files.length > 0 ? `${files.length} photos attached` : 'No photos attached'}
                    </p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Location</h4>
                    <p className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-slate-400" />
                      {address}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex flex-col items-center pt-4">
                <p className="text-sm font-medium text-slate-600 mb-4">Is everything correct?</p>
                <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setStep('form')} 
                    disabled={submitting}
                    className="w-full sm:w-auto"
                  >
                    <ChevronLeft className="h-4 w-4 mr-2" /> Back to Edit
                  </Button>
                  <Button 
                    type="button" 
                    onClick={handleSubmit} 
                    disabled={submitting}
                    className="w-full sm:w-auto bg-civic-600 hover:bg-civic-700"
                  >
                    {submitting ? (
                      <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> {uploadProgress || 'Submitting...'}</>
                    ) : (
                      'Submit Report'
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
