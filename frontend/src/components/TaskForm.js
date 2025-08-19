import React, { useState } from 'react';
import { createTask } from '../api/taskService';
import { toast } from 'react-toastify';
import './TaskForm.css';

const TaskForm = ({ projectId, onTaskCreated }) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [taskData, setTaskData] = useState({
    title: '',
    description: '',
    status: 'todo'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTaskData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!taskData.title.trim()) {
      toast.error('Task title is required');
      return;
    }

    setIsSubmitting(true);
    try {
      const newTask = await createTask(projectId, taskData);
      onTaskCreated(newTask);
      setTaskData({
        title: '',
        description: '',
        status: 'todo'
      });
      setIsFormOpen(false);
      toast.success('Task created successfully');
    } catch (error) {
      console.error('Failed to create task', error);
      toast.error(error.message || 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isFormOpen) {
    return (
      <button 
        className="add-task-button"
        onClick={() => setIsFormOpen(true)}
      >
        + Add Task
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <div className="form-group">
        <input
          type="text"
          name="title"
          value={taskData.title}
          onChange={handleInputChange}
          placeholder="Task title"
          className="task-input"
          required
          autoFocus
        />
      </div>
      
      <div className="form-group">
        <textarea
          name="description"
          value={taskData.description}
          onChange={handleInputChange}
          placeholder="Task description (optional)"
          className="task-textarea"
          rows="3"
        />
      </div>
      
      <div className="form-group">
        <select
          name="status"
          value={taskData.status}
          onChange={handleInputChange}
          className="status-select"
        >
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="done">Done</option>
        </select>
      </div>
      
      <div className="form-actions">
        <button 
          type="button" 
          className="btn-cancel"
          onClick={() => {
            setIsFormOpen(false);
            setTaskData({
              title: '',
              description: '',
              status: 'todo'
            });
          }}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button 
          type="submit" 
          className="btn-primary"
          disabled={isSubmitting || !taskData.title.trim()}
        >
          {isSubmitting ? 'Creating...' : 'Add Task'}
        </button>
      </div>
    </form>
  );
};

export default TaskForm;
