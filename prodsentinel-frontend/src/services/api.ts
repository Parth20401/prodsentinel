import axios from 'axios';
import type { Incident, AnalysisResult, PaginatedResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

export const getIncidents = async (page = 1, limit = 50): Promise<PaginatedResponse<Incident>> => {
    const offset = (page - 1) * limit;
    const response = await api.get('/query/incidents', {
        params: { limit, offset }
    });
    return response.data;
};

export const getIncidentAnalysis = async (id: string): Promise<AnalysisResult> => {
    const response = await api.get(`/query/incidents/${id}/analysis`);
    return response.data;
};
