import React, { useState } from 'react';
import { FaEdit, FaTrash, FaUserPlus, FaCheck, FaTimes } from 'react-icons/fa';
import { updateTask, deleteTask } from '../api/taskService';
import { toast } from 'react-toastify';
import './TaskList.css';

const statusOptions = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'in_review', label: 'In Review' },
  { value: 'done', label: 'Done' }
];

const TaskList = ({ 
  tasks = [], 
  projectId, 
  onTaskUpdated, 
  onTaskDeleted,
  availableUsers = []
}) => {
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const [isAddingAssignee, setIsAddingAssignee] = useState(null);
  const [selectedAssignee, setSelectedAssignee] = useState('');

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      const updatedTask = await updateTask(projectId, taskId, { status: newStatus });
      onTaskUpdated && onTaskUpdated(updatedTask);
      toast.success('Task status updated');
    } catch (error) {
      console.error('Failed to update task status', error);
      toast.error('Failed to update task status');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await deleteTask(projectId, taskId);
      onTaskDeleted && onTaskDeleted(taskId);
      toast.success('Task deleted successfully');
    } catch (error) {
      console.error('Failed to delete task', error);
      toast.error('Failed to delete task');
    }
  };

  const handleEditTask = (task) => {
    setEditingTaskId(task.id);
    setEditingTask({ ...task });
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      const updatedTask = await updateTask(projectId, editingTaskId, {
        title: editingTask.title,
        description: editingTask.description
      });
      onTaskUpdated && onTaskUpdated(updatedTask);
      setEditingTaskId(null);
      setEditingTask(null);
      toast.success('Task updated successfully');
    } catch (error) {
      console.error('Failed to update task', error);
      toast.error('Failed to update task');
    }
  };

  const handleAddAssignee = async (taskId) => {
    if (!selectedAssignee) return;
    
    try {
      const updatedTask = await updateTask(projectId, taskId, {
        assignee_id: selectedAssignee
      });
      onTaskUpdated && onTaskUpdated(updatedTask);
      setIsAddingAssignee(null);
      setSelectedAssignee('');
      toast.success('Assignee added successfully');
    } catch (error) {
      console.error('Failed to add assignee', error);
      toast.error('Failed to add assignee');
    }
  };

  const handleRemoveAssignee = async (taskId) => {
    try {
      const updatedTask = await updateTask(projectId, taskId, {
        assignee_id: null
      });
      onTaskUpdated && onTaskUpdated(updatedTask);
      toast.success('Assignee removed successfully');
    } catch (error) {
      console.error('Failed to remove assignee', error);
      toast.error('Failed to remove assignee');
    }
  };

  const getStatusClass = (status) => {
    const statusMap = {
      todo: 'status-todo',
      in_progress: 'status-in-progress',
      in_review: 'status-in-review',
      done: 'status-done'
    };
    return statusMap[status] || '';
  };

  return (
    <div className="task-list">
      {tasks.length === 0 ? (
        <div className="no-tasks">No tasks found. Create your first task to get started.</div>
      ) : (
        <ul className="task-items">
          {tasks.map((task) => (
            <li key={task.id} className="task-item">
              {editingTaskId === task.id ? (
                <form onSubmit={handleSaveEdit} className="task-edit-form">
                  <input
                    type="text"
                    value={editingTask.title}
                    onChange={(e) => setEditingTask({...editingTask, title: e.target.value})}
                    className="task-edit-input"
                    required
                  />
                  <textarea
                    value={editingTask.description || ''}
                    onChange={(e) => setEditingTask({...editingTask, description: e.target.value})}
                    className="task-edit-textarea"
                    rows="3"
                  />
                  <div className="task-edit-actions">
                    <button type="submit" className="btn-save">Save</button>
                    <button 
                      type="button" 
                      className="btn-cancel"
                      onClick={() => setEditingTaskId(null)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <div className="task-main">
                    <div className="task-header">
                      <h4 className="task-title">{task.title}</h4>
                      <div className="task-actions">
                        <button 
                          className="icon-button"
                          onClick={() => handleEditTask(task)}
                          title="Edit task"
                        >
                          <FaEdit />
                        </button>
                        <button 
                          className="icon-button danger"
                          onClick={() => handleDeleteTask(task.id)}
                          title="Delete task"
                        >
                          <FaTrash />
                        </button>
                      </div>
                    </div>
                    
                    {task.description && (
                      <p className="task-description">{task.description}</p>
                    )}
                    
                    <div className="task-footer">
                      <div className="task-status">
                        <span className="status-label">Status:</span>
                        <select
                          value={task.status || 'todo'}
                          onChange={(e) => handleStatusChange(task.id, e.target.value)}
                          className={`status-select ${getStatusClass(task.status)}`}
                        >
                          {statusOptions.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      
                      <div className="task-assignee">
                        {task.assignee ? (
                          <div className="assignee">
                            <span className="assignee-name">
                              {task.assignee.name || 'Unassigned'}
                            </span>
                            <button 
                              className="icon-button small"
                              onClick={() => handleRemoveAssignee(task.id)}
                              title="Remove assignee"
                            >
                              <FaTimes />
                            </button>
                          </div>
                        ) : isAddingAssignee === task.id ? (
                          <div className="assignee-form">
                            <select
                              value={selectedAssignee}
                              onChange={(e) => setSelectedAssignee(e.target.value)}
                              className="assignee-select"
                            >
                              <option value="">Select assignee</option>
                              {availableUsers.map((user) => (
                                <option key={user.id} value={user.id}>
                                  {user.name}
                                </option>
                              ))}
                            </select>
                            <button 
                              type="button" 
                              className="icon-button small success"
                              onClick={() => handleAddAssignee(task.id)}
                              disabled={!selectedAssignee}
                              title="Save assignee"
                            >
                              <FaCheck />
                            </button>
                            <button 
                              type="button" 
                              className="icon-button small"
                              onClick={() => {
                                setIsAddingAssignee(null);
                                setSelectedAssignee('');
                              }}
                              title="Cancel"
                            >
                              <FaTimes />
                            </button>
                          </div>
                        ) : (
                          <button 
                            className="icon-button small"
                            onClick={() => setIsAddingAssignee(task.id)}
                            title="Add assignee"
                          >
                            <FaUserPlus />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;
