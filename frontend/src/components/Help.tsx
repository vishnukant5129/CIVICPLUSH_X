import React from 'react';
import { Card, CardContent } from './ui/Card';
import { HelpCircle, FileText, Upload, MapPin, Activity } from 'lucide-react';

export const Help: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 animate-in fade-in">
      <div className="text-center mb-10">
        <div className="h-16 w-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <HelpCircle className="h-8 w-8 text-indigo-600" />
        </div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">How can we help?</h1>
        <p className="text-slate-500 max-w-lg mx-auto">
          Learn how to effectively report civic issues and understand the resolution process.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-3">
              <FileText className="h-5 w-5 text-blue-500" /> How to report a problem
            </h3>
            <p className="text-sm text-slate-600 mb-2">
              Click the "Report Issue" button from your dashboard. Provide a clear title and a detailed description of the problem you observed. The more details you provide, the easier it is for authorities to resolve.
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-3">
              <Upload className="h-5 w-5 text-purple-500" /> What evidence to upload
            </h3>
            <p className="text-sm text-slate-600 mb-2">
              Photographic evidence is crucial. Please upload clear, well-lit photos that show the extent of the problem and its immediate surroundings. Supported formats are JPG, PNG, and WEBP up to 5MB.
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-3">
              <MapPin className="h-5 w-5 text-red-500" /> Why location is required
            </h3>
            <p className="text-sm text-slate-600 mb-2">
              Precise GPS coordinates allow civic authorities to dispatch teams directly to the site without confusion. Please allow location access when prompted to ensure accuracy.
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm rounded-xl">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-3">
              <Activity className="h-5 w-5 text-emerald-500" /> How AI helps
            </h3>
            <p className="text-sm text-slate-600 mb-2">
              CivicPulse uses AI to automatically categorize your report and group it with similar reports in your area. This intelligent routing ensures your problem goes to the right department faster.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-10 bg-slate-50 rounded-xl p-8 border border-slate-100">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Understanding Statuses</h3>
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="w-24 flex-shrink-0 font-medium text-sm text-slate-700 bg-white border border-slate-200 rounded px-2 py-1 text-center h-fit">Submitted</div>
            <p className="text-sm text-slate-600 pt-1">Your report has been successfully recorded in the system.</p>
          </div>
          <div className="flex gap-4">
            <div className="w-24 flex-shrink-0 font-medium text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1 text-center h-fit">Assigned</div>
            <p className="text-sm text-slate-600 pt-1">The relevant municipal department has been notified and an officer assigned.</p>
          </div>
          <div className="flex gap-4">
            <div className="w-24 flex-shrink-0 font-medium text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded px-2 py-1 text-center h-fit">In Progress</div>
            <p className="text-sm text-slate-600 pt-1">Work is actively being carried out to resolve the issue.</p>
          </div>
          <div className="flex gap-4">
            <div className="w-24 flex-shrink-0 font-medium text-sm text-green-700 bg-green-50 border border-green-200 rounded px-2 py-1 text-center h-fit">Resolved</div>
            <p className="text-sm text-slate-600 pt-1">The authority has marked this problem as fixed.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
