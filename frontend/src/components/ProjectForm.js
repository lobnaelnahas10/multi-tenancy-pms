import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createProject, getProject, updateProject } from '../api/projectService';
import { toast } from 'react-toastify';
import './ProjectForm.css';

const ProjectForm = ({ isEdit = false }) => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'active'
  });
  
  const [loading, setLoading] = useState(isEdit);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load project data if in edit mode
  useEffect(() => {
    if (!isEdit) return;

    const fetchProject = async () => {
      try {
        const project = await getProject(projectId);
        setFormData({
          name: project.name || '',
          description: project.description || '',
          status: project.status || 'active'
        });
      } catch (err) {
        console.error('Failed to fetch project:', err);
        setError('Failed to load project data');
        toast.error('Failed to load project');
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [isEdit, projectId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      if (isEdit) {
        await updateProject(projectId, formData);
        toast.success('Project updated successfully');
      } else {
        await createProject(formData);
        toast.success('Project created successfully');
      }
      navigate('/projects');
    } catch (err) {
      console.error(isEdit ? 'Update failed:' : 'Creation failed:', err);
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
      toast.error(isEdit ? 'Failed to update project' : 'Failed to create project');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading project data...</p>
      </div>
    );
  }

  return (
    <div className="project-form-container">
      <h2>{isEdit ? 'Edit Project' : 'Create New Project'}</h2>
      
      <form onSubmit={handleSubmit} className="project-form">
        {error && <div className="form-error">{error}</div>}
        
        <div className="form-group">
          <label>Project Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            disabled={submitting}
            placeholder="Enter project name"
          />
        </div>
        
        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            disabled={submitting}
            placeholder="Enter project description (optional)"
            rows="4"
          />
        </div>
        
        {isEdit && (
          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              disabled={submitting}
            >
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        )}
        
        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={() => navigate(-1)}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="submit-button"
            disabled={submitting || !formData.name.trim()}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                {isEdit ? 'Updating...' : 'Creating...'}
              </>
            ) : isEdit ? 'Update Project' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProjectForm;
