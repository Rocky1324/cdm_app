import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Add token to requests if available
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface Document {
    id: number;
    titre: string;
    type: string;
    image_url?: string;
    quantity: number;
    available?: number;
}

export interface Demande {
    id: number;
    username?: string;
    nom: string;
    prenom: string;
    classe: string;
    age: number;
    date_demande: string;
    duree_jours: number;
    status: string;
    details_documents: string;
    date_retour_prevue?: string;
}

export interface DemandeCreate {
    nom: string;
    prenom: string;
    classe: string;
    age: number;
    date_demande: string;
    duree_jours: number;
    details_documents: string;
}

export const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/token', formData);
    return response.data;
};

export const register = async (username: string, password: string, extraData: { nom: string, prenom: string, classe: string }) => {
    const response = await api.post('/register', { username, password, ...extraData });
    return response.data;
};

export const getProfile = async () => {
    const response = await api.get<any>('/users/me'); // Using any or creating a User interface would be better
    return response.data;
};

export const getMyDemandes = async () => {
    const response = await api.get<Demande[]>('/demandes/me');
    return response.data;
};

export const updateDocument = async (id: number, data: { quantity?: number }) => {
    const response = await api.patch<Document>(`/documents/${id}`, data);
    return response.data;
};

export const returnDemande = async (id: number) => {
    const response = await api.patch(`/demandes/${id}/retourner`);
    return response.data;
};

export interface Review {
    id: number;
    username: string;
    rating: number; // 1-5
    comment?: string;
    date: string;
}

export const addReview = async (document_id: number, rating: number, comment: string) => {
    const response = await api.post('/reviews', { document_id, rating, comment });
    return response.data;
};

export const getReviews = async (document_id: number) => {
    const response = await api.get<Review[]>(`/documents/${document_id}/reviews`);
    return response.data;
};

export default api;
