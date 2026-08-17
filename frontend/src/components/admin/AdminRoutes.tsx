import React, { useEffect, useState } from 'react';
import { GenericAdminModule } from './GenericAdminModule';
import { apiFetch } from '../../api/client';
import { CommandCenter } from './CommandCenter';

export const AdminRoutes: React.FC<{ path: string }> = ({ path }) => {
  const [departments, setDepartments] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);

  useEffect(() => {
    // Fetch departments and wards for select options
    apiFetch('/api/v1/admin/departments').then(res => setDepartments(Array.isArray(res) ? res : []));
    apiFetch('/api/v1/admin/wards').then(res => setWards(Array.isArray(res) ? res : []));
  }, []);

  if (path === '/admin') return <CommandCenter />;

  const deptOptions = departments.map(d => ({ label: d.name, value: d._id || d.id }));
  const wardOptions = wards.map(w => ({ label: w.name, value: w._id || w.id }));

  const modules: Record<string, React.ReactElement> = {
    '/admin/authorities': <GenericAdminModule 
      title="Authorities" description="Manage authority users and municipal staff." endpoint="/api/v1/admin/authorities"
      columns={[{header: 'Name', accessor: 'display_name'}, {header: 'Email', accessor: 'email'}, {header: 'Role', accessor: 'role'}, {header: 'Status', accessor: 'status'}]}
      addAction={{
        label: 'Add Authority',
        fields: [
          { name: 'display_name', label: 'Full Name', type: 'text', required: true },
          { name: 'email', label: 'Official Email', type: 'email', required: true },
          { name: 'role', label: 'Role', type: 'select', required: true, options: [
            { label: 'Authority Officer', value: 'authority' },
            { label: 'Municipal Admin', value: 'admin' },
            { label: 'Super Admin', value: 'super_admin' }
          ] },
          { name: 'department_id', label: 'Department', type: 'select', options: deptOptions },
          // Note: Ward scoping for authority usually supports multiple in backend, using string for simplicity or single select
          { name: 'ward_ids', label: 'Primary Ward', type: 'select', options: wardOptions }
        ],
        onSubmit: async (data) => {
          if (data.ward_ids) data.ward_ids = [data.ward_ids]; // convert to array for backend
          await apiFetch('/api/v1/admin/authorities', { method: 'POST', body: JSON.stringify(data) });
        }
      }}
      editAction={{
        fields: [
          { name: 'role', label: 'Role', type: 'select', required: true, options: [
            { label: 'Authority Officer', value: 'authority' },
            { label: 'Municipal Admin', value: 'admin' },
            { label: 'Super Admin', value: 'super_admin' }
          ] },
          { name: 'status', label: 'Status', type: 'select', required: true, options: [
            { label: 'Active', value: 'active' },
            { label: 'Inactive', value: 'inactive' },
            { label: 'Suspended', value: 'suspended' }
          ] },
          { name: 'department_id', label: 'Department', type: 'select', options: deptOptions },
          { name: 'ward_ids', label: 'Primary Ward', type: 'select', options: wardOptions }
        ],
        onSubmit: async (id, data) => {
          if (data.ward_ids && !Array.isArray(data.ward_ids)) data.ward_ids = [data.ward_ids];
          await apiFetch(`/api/v1/admin/authorities/${id}`, { method: 'PUT', body: JSON.stringify(data) });
        }
      }}
      deleteAction={{
        onSubmit: async (id) => {
          await apiFetch(`/api/v1/admin/authorities/${id}`, { method: 'PUT', body: JSON.stringify({ status: 'inactive' }) });
        }
      }}
    />,
    '/admin/departments': <GenericAdminModule 
      title="Departments" description="Manage municipal departments." endpoint="/api/v1/admin/departments"
      columns={[{header: 'Code', accessor: 'code'}, {header: 'Name', accessor: 'name'}, {header: 'Status', accessor: 'status'}]}
      addAction={{
        label: 'Add Department',
        fields: [
          { name: 'name', label: 'Department Name', type: 'text', required: true },
          { name: 'code', label: 'Department Code', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'text' }
        ],
        onSubmit: async (data) => {
          await apiFetch('/api/v1/admin/departments', { method: 'POST', body: JSON.stringify(data) });
        }
      }}
      editAction={{
        fields: [
          { name: 'name', label: 'Department Name', type: 'text', required: true },
          { name: 'status', label: 'Status', type: 'select', required: true, options: [
            { label: 'Active', value: 'active' },
            { label: 'Inactive', value: 'inactive' }
          ] }
        ],
        onSubmit: async (id, data) => {
          await apiFetch(`/api/v1/admin/departments/${id}`, { method: 'PUT', body: JSON.stringify(data) });
        }
      }}
      deleteAction={{
        onSubmit: async (id) => {
          await apiFetch(`/api/v1/admin/departments/${id}`, { method: 'DELETE' });
        }
      }}
    />,
    '/admin/wards': <GenericAdminModule 
      title="Wards & Zones" description="Manage geographical wards and operational zones." endpoint="/api/v1/admin/wards"
      columns={[{header: 'Code', accessor: 'code'}, {header: 'Name', accessor: 'name'}, {header: 'Status', accessor: 'status'}]}
      addAction={{
        label: 'Add Ward',
        fields: [
          { name: 'name', label: 'Ward Name', type: 'text', required: true },
          { name: 'code', label: 'Ward Code', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'text' }
        ],
        onSubmit: async (data) => {
          await apiFetch('/api/v1/admin/wards', { method: 'POST', body: JSON.stringify(data) });
        }
      }}
      editAction={{
        fields: [
          { name: 'name', label: 'Ward Name', type: 'text', required: true },
          { name: 'status', label: 'Status', type: 'select', required: true, options: [
            { label: 'Active', value: 'active' },
            { label: 'Inactive', value: 'inactive' }
          ] }
        ],
        onSubmit: async (id, data) => {
          await apiFetch(`/api/v1/admin/wards/${id}`, { method: 'PUT', body: JSON.stringify(data) });
        }
      }}
      deleteAction={{
        onSubmit: async (id) => {
          await apiFetch(`/api/v1/admin/wards/${id}`, { method: 'DELETE' });
        }
      }}
    />,
    '/admin/routing': <GenericAdminModule 
      title="Routing Rules" description="Manage automated department routing." endpoint="/api/v1/admin/routing-rules"
      columns={[{header: 'Category', accessor: 'category'}, {header: 'Department', accessor: 'department_id'}, {header: 'Priority', accessor: 'priority'}, {header: 'Active', accessor: 'active'}]}
      addAction={{
        label: 'Add Routing Rule',
        fields: [
          { name: 'category', label: 'Complaint Category', type: 'select', required: true, options: [
            { label: 'Roads & Potholes', value: 'pothole_road_damage' },
            { label: 'Streetlight & Electricity', value: 'streetlight_electricity' },
            { label: 'Water & Leakage', value: 'water_leakage' },
            { label: 'Sewage & Drainage', value: 'sewage_drainage' },
            { label: 'Garbage & Waste', value: 'garbage_waste' },
            { label: 'Public Infrastructure', value: 'public_infrastructure' },
            { label: 'Traffic & Signage', value: 'traffic_signage' },
            { label: 'Other', value: 'other' }
          ] },
          { name: 'department_id', label: 'Route to Department', type: 'select', required: true, options: deptOptions },
          { name: 'jurisdiction', label: 'Specific Ward (Optional)', type: 'select', options: wardOptions },
          { name: 'priority', label: 'Priority (1 is highest)', type: 'number', required: true },
          { name: 'active', label: 'Rule Active', type: 'checkbox' }
        ],
        onSubmit: async (data) => {
          if (data.active === undefined) data.active = true;
          await apiFetch('/api/v1/admin/routing-rules', { method: 'POST', body: JSON.stringify(data) });
        }
      }}
      editAction={{
        fields: [
          { name: 'priority', label: 'Priority (1 is highest)', type: 'number', required: true },
          { name: 'active', label: 'Rule Active', type: 'checkbox' }
        ],
        onSubmit: async (id, data) => {
          await apiFetch(`/api/v1/admin/routing-rules/${id}`, { method: 'PUT', body: JSON.stringify(data) });
        }
      }}
      deleteAction={{
        onSubmit: async (id) => {
          await apiFetch(`/api/v1/admin/routing-rules/${id}`, { method: 'DELETE' });
        }
      }}
    />,
    '/admin/permissions': <GenericAdminModule 
      title="Roles & Permissions" description="Manage system RBAC and role scopes." endpoint="/api/v1/admin/roles"
      columns={[{header: 'Role Key', accessor: 'roles'}]} // API needs formatting, but this handles the array gracefully enough or we let it fall back.
    />,
    '/admin/complaints': <GenericAdminModule 
      title="Complaints Queue" description="Central view of all citizen complaints." endpoint="/api/v1/authority/complaints"
      columns={[{header: 'ID', accessor: '_id'}, {header: 'Category', accessor: 'category'}, {header: 'Status', accessor: 'status'}, {header: 'Priority', accessor: 'priority_score'}]}
    />,
    '/admin/intelligence': <GenericAdminModule 
      title="Civic Intelligence" description="AI-driven intelligence overview." endpoint="/api/v1/predictions/summary"
      columns={[{header: 'Metric', accessor: 'status'}]}
    />,
    '/admin/clusters': <GenericAdminModule 
      title="Problem Clusters" description="AI-identified recurring incident clusters." endpoint="/api/v1/admin/clusters"
      columns={[{header: 'Category', accessor: 'category'}, {header: 'Count', accessor: 'complaint_count'}, {header: 'Severity', accessor: 'severity'}]}
    />,
    '/admin/projects': <GenericAdminModule 
      title="Civic Projects" description="Verified projects open for matching." endpoint="/api/v1/civic-projects"
      columns={[{header: 'Code', accessor: 'project_code'}, {header: 'Title', accessor: 'title'}, {header: 'Status', accessor: 'status'}, {header: 'Verification', accessor: 'verification_status'}]}
    />,
    '/admin/organizations': <GenericAdminModule 
      title="Organizations" description="Participating CSRs, NGOs, and partners." endpoint="/api/v1/organizations"
      columns={[{header: 'Name', accessor: 'name'}, {header: 'Type', accessor: 'org_type'}, {header: 'Status', accessor: 'verification_status'}]}
    />,
    '/admin/matching': <GenericAdminModule 
      title="Resource Matching" description="Active match requests from organizations to projects." endpoint="/api/v1/admin/matching"
      columns={[{header: 'Project ID', accessor: 'project_id'}, {header: 'Org ID', accessor: 'organization_id'}, {header: 'Status', accessor: 'status'}]}
    />,
    '/admin/outcomes': <GenericAdminModule 
      title="Outcome Verification" description="Projects pending outcome verification." endpoint="/api/v1/civic-projects"
      columns={[{header: 'Code', accessor: 'project_code'}, {header: 'Title', accessor: 'title'}, {header: 'Status', accessor: 'status'}, {header: 'Impact', accessor: 'impact_summary'}]}
    />,
    '/admin/analytics': <GenericAdminModule 
      title="Analytics" description="System-wide usage analytics." endpoint="/api/v1/predictions/trends"
      columns={[{header: 'Category', accessor: 'category'}, {header: 'Trend', accessor: 'trend_direction'}]}
    />,
    '/admin/hotspots': <GenericAdminModule 
      title="Hotspots" description="Spatial risk analysis." endpoint="/api/v1/predictions/hotspots"
      columns={[{header: 'Grid ID', accessor: 'grid_id'}, {header: 'Risk Score', accessor: 'risk_score'}]}
    />,
    '/admin/predictions': <GenericAdminModule 
      title="Predictive Intelligence" description="Future risk forecasting." endpoint="/api/v1/predictions/summary"
      columns={[{header: 'Forecast', accessor: 'status'}]}
    />,
    '/admin/notifications': <GenericAdminModule 
      title="System Notifications" description="Global administrative events." endpoint="/api/v1/notifications"
      columns={[{header: 'Type', accessor: 'type'}, {header: 'Title', accessor: 'title'}, {header: 'Status', accessor: 'status'}]}
    />,
    '/admin/audit': <GenericAdminModule 
      title="Audit Logs" description="Immutable record of system actions." endpoint="/api/v1/admin/audit"
      columns={[{header: 'Action', accessor: 'action'}, {header: 'Actor ID', accessor: 'actor_id'}, {header: 'Target Type', accessor: 'resource_type'}, {header: 'Target ID', accessor: 'resource_id'}]}
    />,
    '/admin/settings': <GenericAdminModule 
      title="System Configuration" description="Global operational parameters." endpoint="/api/v1/admin/settings"
      columns={[{header: 'Key', accessor: 'key'}, {header: 'Value', accessor: 'value'}]}
    />,
  };

  const Component = modules[path];
  
  if (!Component) {
    return <div className="p-8 text-slate-500">Route not found.</div>;
  }

  return Component;
};
