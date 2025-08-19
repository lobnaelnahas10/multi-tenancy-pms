import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button } from '@mui/material';
import ProjectList from '../components/ProjectList';
import CreateProjectForm from '../components/CreateProjectForm';
import { getProjects } from '../api/projectService';

const DashboardPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await getProjects();
      setProjects(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Failed to fetch projects', error);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleProjectCreated = (newProject) => {
    console.log('Adding new project to state:', newProject);
    if (newProject && newProject.id) {
      setProjects(prevProjects => [newProject, ...prevProjects]);
      setShowCreateForm(false);
    } else {
      console.error('Invalid project data received:', newProject);
      fetchProjects();
    }
  };

  const handleProjectDeleted = (deletedProjectId) => {
    setProjects(prevProjects => prevProjects.filter(project => project.id !== deletedProjectId));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Container maxWidth="lg" sx={{ py: 3, flexShrink: 0, borderBottom: '1px solid #e0e0e0', backgroundColor: 'background.paper' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="h1">
            My Projects
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Hide Form' : 'Create New Project'}
          </Button>
        </Box>
      </Container>
      
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {showCreateForm && (
          <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0', backgroundColor: 'background.paper' }}>
            <Container maxWidth="lg">
              <CreateProjectForm 
                onProjectCreated={handleProjectCreated} 
                onClose={() => setShowCreateForm(false)}
              />
            </Container>
          </Box>
        )}
        
        <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
          <Container maxWidth="lg">
            <ProjectList 
              projects={projects} 
              loading={loading}
              error={error}
              onProjectDeleted={handleProjectDeleted}
            />
          </Container>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
