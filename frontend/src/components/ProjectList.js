import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { deleteProject } from '../api/projectService';
import { toast } from 'react-toastify';
import './ProjectList.css';

const ProjectList = ({ projects = [], loading = false, error = '', onProjectDeleted }) => {
  const navigate = useNavigate();

  const handleDelete = async (projectId, projectName) => {
    if (!window.confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteProject(projectId);
      if (onProjectDeleted) {
        onProjectDeleted(projectId);
      }
      toast.success('Project deleted successfully');
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error(error.message || 'Failed to delete project');
    }
  };

  const handleEdit = (projectId, e) => {
    e.stopPropagation();
    navigate(`/projects/${projectId}/edit`);
  };
  
  const handleCreateProject = () => {
    navigate('/projects/new');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading projects...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="project-list-container">
      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects found. Create your first project to get started.</p>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map(project => (
            <div key={project.id} className="project-card">
              <div className="project-card-header">
                <h3 className="project-title">
                  <Link to={`/projects/${project.id}`}>
                    {project.name}
                  </Link>
                </h3>
                <div className="project-actions">
                  <button 
                    className="icon-button edit-button"
                    onClick={(e) => handleEdit(project.id, e)}
                    title="Edit project"
                  >
                    ✏️
                  </button>
                  <button 
                    className="icon-button delete-button"
                    onClick={() => handleDelete(project.id, project.name)}
                    title="Delete project"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              {project.description && (
                <p className="project-description">
                  {project.description.length > 100 
                    ? `${project.description.substring(0, 100)}...` 
                    : project.description}
                </p>
              )}
              
              <div className="project-footer">
                <span className="project-meta">
                  📅 Created: {new Date(project.created_at).toLocaleDateString()}
                </span>
                <Link 
                  to={`/projects/${project.id}`}
                  className="view-details-link"
                >
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectList;
