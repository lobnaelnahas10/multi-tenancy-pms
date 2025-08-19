import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, getProjectWithTasks, getProjectUsers } from '../api/projectService';
import { getTasks, createTask, updateTask, deleteTask } from '../api/taskService';
import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';
import { toast } from 'react-toastify';
import './ProjectPage.css';

const ProjectPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // First get the basic project data
      const projectData = await getProject(projectId);
      setProject(projectData);
      
      // Then fetch tasks and users in parallel
      const [tasksData, usersData] = await Promise.all([
        getTasks(projectId).catch(err => {
          console.error('Error fetching tasks:', err);
          return [];
        }),
        getProjectUsers(projectId).catch(err => {
          console.error('Error fetching project users:', err);
          return [];
        })
      ]);
      
      setTasks(tasksData);
      setAvailableUsers(usersData);
      
    } catch (error) {
      console.error('Failed to fetch project data', error);
      const errorMessage = error.response?.data?.detail || 'Failed to load project data';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const handleTaskCreated = (newTask) => {
    setTasks(prevTasks => [...prevTasks, newTask]);
    toast.success('Task created successfully');
  };

  const handleTaskUpdated = (updatedTask) => {
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === updatedTask.id ? updatedTask : task
      )
    );
  };

  const handleTaskDeleted = (deletedTaskId) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== deletedTaskId));
    toast.success('Task deleted successfully');
  };

  const handleEditProject = () => {
    navigate(`/projects/${projectId}/edit`);
  };

  if (loading) {
    return <div className="loading">Loading project data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!project) {
    return <div className="not-found">Project not found</div>;
  }

  return (
    <div className="project-page">
      <div className="project-header">
        <div>
          <h1>{project.name}</h1>
          {project.description && (
            <p className="project-description">{project.description}</p>
          )}
          <div className="project-meta">
            <span className={`status-badge ${project.status || 'active'}`}>
              {project.status ? project.status.replace('_', ' ') : 'Active'}
            </span>
            <span className="created-date">
              Created on: {new Date(project.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        <button 
          onClick={handleEditProject}
          className="edit-project-btn"
        >
          Edit Project
        </button>
      </div>

      <div className="tasks-section">
        <div className="tasks-header">
          <h2>Tasks</h2>
          <div className="task-count">{tasks.length} tasks</div>
        </div>
        
        <TaskForm 
          projectId={projectId} 
          onTaskCreated={handleTaskCreated} 
        />
        
        <TaskList 
          tasks={tasks}
          projectId={projectId}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
          availableUsers={availableUsers}
        />
      </div>
    </div>
  );
};

export default ProjectPage;
