import api from './api';

export default {
  async getProjectOverview(projectId) {
    const response = await api.get(`/analytics/project/${projectId}/overview`);
    return response.data;
  },

  async getProjectTimeline(projectId) {
    const response = await api.get(`/analytics/project/${projectId}/timeline`);
    return response.data;
  },

  async getTeamWorkload(projectId) {
    const response = await api.get(`/analytics/project/${projectId}/workload`);
    return response.data;
  }
}; 