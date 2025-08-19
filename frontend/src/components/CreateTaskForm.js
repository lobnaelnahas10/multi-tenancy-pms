import React, { useState } from 'react';
import { createTask } from '../api/taskService';
import './CreateTaskForm.css';

const CreateTaskForm = ({ projectId, onTaskCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('todo');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      console.log('Creating task with data:', { projectId, title, description, status });
      const response = await createTask(projectId, { 
        title, 
        description, 
        status 
      });
      console.log('Task created:', response.data);
      onTaskCreated(response.data);
      setTitle('');
      setDescription('');
    } catch (error) {
      console.error('Failed to create task', error);
      
      // Handle different error response formats
      let errorMessage = 'Failed to create task. Please try again.';
      const errorData = error.response?.data;
      
      if (errorData) {
        // Handle FastAPI validation errors
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => err.msg).join(' ');
        } 
        // Handle string error message
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        }
        // Handle object with message
        else if (errorData.message) {
          errorMessage = errorData.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="create-task-form">
      <h3>Create New Task</h3>
      {error && <div className="error-message">{error}</div>}
      <div className="form-group">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task Title"
          required
          disabled={isLoading}
        />
      </div>
      <div className="form-group">
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Task Description"
          disabled={isLoading}
        />
      </div>
      <div className="form-group">
        <label>Status</label>
        <select 
          value={status} 
          onChange={(e) => setStatus(e.target.value)}
          disabled={isLoading}
          className="status-select"
        >
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="done">Done</option>
        </select>
      </div>
      <button 
        type="submit" 
        disabled={isLoading || !title.trim()}
        className={isLoading ? 'loading' : ''}
      >
        {isLoading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
};

export default CreateTaskForm;
