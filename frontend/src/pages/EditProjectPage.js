import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, updateProject } from '../api/projectService';
import { toast } from 'react-toastify';
import './EditProjectPage.css';

const EditProjectPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState({
    name: '',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        const data = await getProject(projectId);
        setProject({
          name: data.name,
          description: data.description || '',
          status: data.status || 'active'
        });
      } catch (err) {
        console.error('Failed to fetch project', err);
        setError('Failed to load project');
        toast.error('Failed to load project');
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [projectId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProject(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateProject(projectId, project);
      toast.success('Project updated successfully');
      // Navigate back to project page
      navigate(`/projects/${projectId}`, { replace: true });
    } catch (err) {
      console.error('Failed to update project', err);
      const errorMessage = err.response?.data?.detail || 'Failed to update project';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  if (loading) {
    return <div className="loading">Loading project...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="edit-project-container">
      <h1>Edit Project</h1>
      <form onSubmit={handleSubmit} className="project-form">
        <div className="form-group">
          <label htmlFor="name">Project Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={project.name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={project.description}
            onChange={handleChange}
            rows="4"
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-actions">
          <button type="button" onClick={() => navigate(-1)} className="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" className="btn btn-primary">
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditProjectPage;
