import api from './api';

/**
 * Get all tasks for a project
 * @param {string} projectId - The ID of the project
 * @returns {Promise<Array>} - Array of tasks
 */
export const getTasks = async (projectId) => {
  try {
    const response = await api.get(`/projects/${projectId}/tasks/`);
    return response.data || [];
  } catch (error) {
    console.error(`Error fetching tasks for project ${projectId}:`, error);
    throw enhanceError(error, 'fetch tasks');
  }
};

/**
 * Get a single task by ID
 * @param {string} projectId - The ID of the project
 * @param {string} taskId - The ID of the task
 * @returns {Promise<Object>} - Task details
 */
export const getTask = async (projectId, taskId) => {
  try {
    const response = await api.get(`/projects/${projectId}/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching task ${taskId}:`, error);
    throw enhanceError(error, 'fetch task');
  }
};

/**
 * Create a new task in a project
 * @param {string} projectId - The ID of the project
 * @param {Object} taskData - Task data including title, description, status, etc.
 * @returns {Promise<Object>} - The created task
 */
export const createTask = async (projectId, taskData) => {
  try {
    const response = await api.post(`/projects/${projectId}/tasks/`, taskData);
    return response.data;
  } catch (error) {
    console.error(`Error creating task for project ${projectId}:`, error);
    throw enhanceError(error, 'create task');
  }
};

/**
 * Update an existing task
 * @param {string} projectId - The ID of the project
 * @param {string} taskId - The ID of the task to update
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} - The updated task
 */
export const updateTask = async (projectId, taskId, updates) => {
  try {
    const response = await api.patch(`/projects/${projectId}/tasks/${taskId}`, updates);
    return response.data;
  } catch (error) {
    console.error(`Error updating task ${taskId}:`, error);
    throw enhanceError(error, 'update task');
  }
};

/**
 * Delete a task
 * @param {string} projectId - The ID of the project
 * @param {string} taskId - The ID of the task to delete
 * @returns {Promise<Object>} - The response data
 */
export const deleteTask = async (projectId, taskId) => {
  try {
    const response = await api.delete(`/projects/${projectId}/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting task ${taskId}:`, error);
    throw enhanceError(error, 'delete task');
  }
};

/**
 * Assign a task to a user
 * @param {string} projectId - The ID of the project
 * @param {string} taskId - The ID of the task
 * @param {string} userId - The ID of the user to assign
 * @returns {Promise<Object>} - The updated task
 */
export const assignTask = async (projectId, taskId, userId) => {
  try {
    const response = await api.patch(`/projects/${projectId}/tasks/${taskId}/assign`, { userId });
    return response.data;
  } catch (error) {
    console.error(`Error assigning task ${taskId}:`, error);
    throw enhanceError(error, 'assign task');
  }
};

/**
 * Update task status
 * @param {string} projectId - The ID of the project
 * @param {string} taskId - The ID of the task
 * @param {string} status - New status (todo, in_progress, in_review, done)
 * @returns {Promise<Object>} - The updated task
 */
export const updateTaskStatus = async (projectId, taskId, status) => {
  try {
    // Use the general update endpoint with the status field
    const response = await api.patch(`/projects/${projectId}/tasks/${taskId}`, { status });
    return response.data;
  } catch (error) {
    console.error(`Error updating status for task ${taskId}:`, error);
    throw enhanceError(error, 'update task status');
  }
};

/**
 * Helper function to enhance error messages
 * @private
 */
function enhanceError(error, action) {
  if (!error.response) {
    error.message = `Network error: Could not ${action}. Please check your connection.`;
    return error;
  }

  const { status, data } = error.response;
  
  switch (status) {
    case 400:
      error.message = data.detail || 'Invalid request data.';
      break;
    case 401:
      error.message = 'Your session has expired. Please log in again.';
      break;
    case 403:
      error.message = `You don't have permission to ${action}.`;
      break;
    case 404:
      error.message = 'The requested resource was not found.';
      break;
    case 422: // Validation error
      if (Array.isArray(data.detail)) {
        error.message = data.detail.map(err => err.msg).join(' ');
      } else if (typeof data.detail === 'string') {
        error.message = data.detail;
      } else {
        error.message = 'Validation failed. Please check your input.';
      }
      break;
    case 500:
      error.message = 'Server error. Please try again later.';
      break;
    default:
      error.message = data?.message || `Failed to ${action}.`;
  }
  
  return error;
}
