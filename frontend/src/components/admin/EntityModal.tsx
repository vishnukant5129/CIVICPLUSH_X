import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'select' | 'checkbox' | 'number';
  options?: { label: string; value: string }[];
  required?: boolean;
}

interface EntityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  title: string;
  fields: FormField[];
  initialData?: any;
}

export const EntityModal: React.FC<EntityModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  title,
  fields,
  initialData
}) => {
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData(initialData);
      } else {
        // Initialize with default values
        const defaults: any = {};
        fields.forEach(f => {
          if (f.type === 'checkbox') defaults[f.name] = false;
          else if (f.type === 'select' && f.options && f.options.length > 0) defaults[f.name] = f.options[0].value;
          else defaults[f.name] = '';
        });
        setFormData(defaults);
      }
      setError(null);
    }
  }, [isOpen, initialData, fields]);

  if (!isOpen) return null;

  const handleChange = (name: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <h2 className="text-xl font-semibold text-slate-800">{initialData ? 'Edit' : 'Add'} {title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-red-50 text-red-600 text-sm flex items-start gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {fields.map(field => (
            <div key={field.name} className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">
                {field.label} {field.required && <span className="text-red-500">*</span>}
              </label>
              
              {field.type === 'text' || field.type === 'email' || field.type === 'number' ? (
                <input
                  type={field.type}
                  required={field.required}
                  value={formData[field.name] || ''}
                  onChange={e => handleChange(field.name, field.type === 'number' ? parseFloat(e.target.value) : e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                />
              ) : field.type === 'select' ? (
                <select
                  required={field.required}
                  value={formData[field.name] || ''}
                  onChange={e => handleChange(field.name, e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors bg-white"
                >
                  <option value="" disabled>Select {field.label}</option>
                  {field.options?.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : field.type === 'checkbox' ? (
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={!!formData[field.name]}
                    onChange={e => handleChange(field.name, e.target.checked)}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-slate-600">Enabled</span>
                </label>
              ) : null}
            </div>
          ))}

          <div className="pt-6 flex justify-end gap-3 border-t border-slate-100 mt-6">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex items-center gap-2">
              {loading ? (
                <span className="animate-spin inline-block h-4 w-4 border-2 border-white/20 border-t-white rounded-full" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              {loading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
