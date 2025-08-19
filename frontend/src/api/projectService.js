import api from './api';

/**
 * Get all projects for the current user
 * @returns {Promise<Array>} - Array of projects
 */
export const getProjects = async () => {
  try {
    const response = await api.get('/projects/');
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching projects:', error);
    throw enhanceError(error, 'fetch projects');
  }
};

/**
 * Get a single project by ID with basic details
 * @param {string} projectId - The ID of the project
 * @returns {Promise<Object>} - Project details
 */
export const getProject = async (projectId) => {
  try {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching project ${projectId}:`, error);
    throw enhanceError(error, 'fetch project');
  }
};

/**
 * Get a project with its associated tasks
 * @param {string} projectId - The ID of the project
 * @returns {Promise<Object>} - Project with tasks
 */
export const getProjectWithTasks = async (projectId) => {
  try {
    const response = await api.get(`/projects/${projectId}?include_tasks=true`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching project ${projectId} with tasks:`, error);
    throw enhanceError(error, 'fetch project with tasks');
  }
};

/**
 * Get users associated with a project
 * @param {string} projectId - The ID of the project
 * @returns {Promise<Array>} - Array of users
 */
export const getProjectUsers = async (projectId) => {
  try {
    const response = await api.get(`/projects/${projectId}/users`);
    return response.data || [];
  } catch (error) {
    console.error(`Error fetching users for project ${projectId}:`, error);
    throw enhanceError(error, 'fetch project users');
  }
};

/**
 * Create a new project
 * @param {Object} projectData - Project data including name, description, etc.
 * @returns {Promise<Object>} - The created project
 */
export const createProject = async (projectData) => {
  try {
    const response = await api.post('/projects/', {
      name: projectData.name,
      description: projectData.description || '',
      status: projectData.status || 'active'
    });
    
    if (!response.data.id) {
      throw new Error('Invalid project data received from server');
    }
    
    return {
      id: response.data.id,
      name: response.data.name,
      description: response.data.description || '',
      status: response.data.status || 'active',
      created_at: response.data.created_at || new Date().toISOString()
    };
  } catch (error) {
    console.error('Error creating project:', error);
    throw enhanceError(error, 'create project');
  }
};

/**
 * Update an existing project
 * @param {string} projectId - The ID of the project to update
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} - The updated project
 */
export const updateProject = async (projectId, updates) => {
  try {
    const response = await api.patch(`/projects/${projectId}`, updates);
    return response.data;
  } catch (error) {
    console.error(`Error updating project ${projectId}:`, error);
    throw enhanceError(error, 'update project');
  }
};

/**
 * Delete a project
 * @param {string} projectId - The ID of the project to delete
 * @returns {Promise<boolean>} - True if successful
 */
export const deleteProject = async (projectId) => {
  try {
    await api.delete(`/projects/${projectId}`);
    return true;
  } catch (error) {
    console.error(`Error deleting project ${projectId}:`, error);
    throw enhanceError(error, 'delete project');
  }
};

/**
 * Add a user to a project
 * @param {string} projectId - The ID of the project
 * @param {string} userId - The ID of the user to add
 * @param {string} role - The role of the user in the project (e.g., 'member', 'admin')
 * @returns {Promise<Object>} - The updated project user
 */
export const addUserToProject = async (projectId, userId, role = 'member') => {
  try {
    const response = await api.post(`/projects/${projectId}/users`, { userId, role });
    return response.data;
  } catch (error) {
    console.error(`Error adding user to project ${projectId}:`, error);
    throw enhanceError(error, 'add user to project');
  }
};

/**
 * Remove a user from a project
 * @param {string} projectId - The ID of the project
 * @param {string} userId - The ID of the user to remove
 * @returns {Promise<boolean>} - True if successful
 */
export const removeUserFromProject = async (projectId, userId) => {
  try {
    await api.delete(`/projects/${projectId}/users/${userId}`);
    return true;
  } catch (error) {
    console.error(`Error removing user from project ${projectId}:`, error);
    throw enhanceError(error, 'remove user from project');
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
