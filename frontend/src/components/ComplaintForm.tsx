import React, { useState } from 'react';
import { complaintsApi } from '../api/complaints';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Label } from './ui/Label';
import { Textarea } from './ui/Textarea';
import { Select } from './ui/Select';
import { MapPin, FileText, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (title.length < 5) throw new Error("Title must be at least 5 characters.");
      if (description.length < 10) throw new Error("Description must be at least 10 characters.");
      
      let lng = 0, lat = 0;
      try {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000 });
        });
        lng = position.coords.longitude;
        lat = position.coords.latitude;
      } catch (geoErr: any) {
        throw new Error("Could not obtain location. Please allow location access to submit a complaint.");
      }

      const payload = {
        title,
        description,
        category,
        location: {
          address,
          geo: {
            type: 'Point' as const,
            coordinates: [lng, lat] as [number, number]
          }
        }
      };

      const result = await complaintsApi.create(payload);
      setSuccessId(result.id);
    } catch (err: any) {
      setError(err.message || 'Failed to submit complaint');
    } finally {
      setSubmitting(false);
    }
  };

  if (successId) {
    return (
      <Card className="max-w-2xl mx-auto mt-10 border-green-200 bg-green-50 shadow-sm animate-in fade-in slide-in-from-bottom-4">
        <CardContent className="flex flex-col items-center justify-center p-10 text-center space-y-4">
          <div className="bg-green-100 p-4 rounded-full">
            <CheckCircle2 className="h-12 w-12 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-green-900 tracking-tight">Issue Recorded Successfully</h2>
          <p className="text-green-700 max-w-md">
            Your civic issue has been securely submitted and routed to the appropriate authority for AI analysis and resolution.
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
          <form onSubmit={handleSubmit} className="space-y-6">
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
              <p className="text-xs text-gray-500 flex items-center gap-1.5 mt-2">
                <MapPin className="h-3.5 w-3.5" />
                Precise GPS coordinates will be captured securely when you submit.
              </p>
            </div>

            <div className="pt-6 border-t border-gray-100 flex justify-end">
              <Button
                type="submit"
                disabled={submitting}
                size="lg"
                className="w-full sm:w-auto"
              >
                {submitting ? (
                  <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Processing Submission</>
                ) : (
                  'Submit Official Report'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
