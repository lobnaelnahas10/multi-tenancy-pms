import React, { useState } from 'react';
import { deleteTask } from '../api/taskService';
import EditTaskModal from './EditTaskModal';
import './TaskItem.css';

const statusColors = {
  todo: '#e0e0e0',
  in_progress: '#4a90e2',
  in_review: '#f1c40f',
  done: '#2ecc71'
};

const statusLabels = {
  todo: 'To Do',
  in_progress: 'In Progress',
  in_review: 'In Review',
  done: 'Done'
};

const TaskItem = ({ task, onTaskUpdated, onTaskDeleted }) => {
  const [showEditModal, setShowEditModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setError('');
    setIsDeleting(true);

    try {
      await deleteTask(task.id);
      onTaskDeleted(task.id);
    } catch (err) {
      console.error('Error deleting task:', err);
      setError(err.message || 'Failed to delete task');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await updateTask(task.id, { status: newStatus });
      onTaskUpdated({ ...task, status: newStatus });
    } catch (err) {
      console.error('Error updating task status:', err);
      setError('Failed to update task status');
    }
  };

  return (
    <div className="task-item">
      <div className="task-header">
        <div className="task-title">{task.title}</div>
        <div className="task-actions">
          <button 
            className="edit-button"
            onClick={() => setShowEditModal(true)}
            title="Edit task"
          >
            ✏️
          </button>
          <button 
            className="delete-button"
            onClick={handleDelete}
            disabled={isDeleting}
            title="Delete task"
          >
            {isDeleting ? 'Deleting...' : '🗑️'}
          </button>
        </div>
      </div>
      
      {task.description && (
        <div className="task-description">{task.description}</div>
      )}
      
      <div className="task-footer">
        <div className="task-status" style={{ backgroundColor: statusColors[task.status] }}>
          {statusLabels[task.status] || task.status}
        </div>
        
        {task.assignee && (
          <div className="task-assignee">
            👤 {task.assignee.username || 'Unassigned'}
          </div>
        )}
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {showEditModal && (
        <EditTaskModal
          task={task}
          projectId={task.project_id}
          onClose={() => setShowEditModal(false)}
          onTaskUpdated={(updatedTask) => {
            onTaskUpdated(updatedTask);
            setShowEditModal(false);
          }}
        />
      )}
    </div>
  );
};

export default TaskItem;
