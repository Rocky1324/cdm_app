import React, { useEffect, useState } from 'react';
import api, { Document, Demande, DemandeCreate, login, getMyDemandes, register, getProfile, updateDocument, returnDemande, addReview, getReviews, Review } from './api';

// Simple JWT decode helper
const parseJwt = (token: string) => {
    try {
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        return null;
    }
};

function App() {
    // Auth State
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [userRole, setUserRole] = useState<string | null>(null);
    const [showLogin, setShowLogin] = useState(false);
    const [isRegistering, setIsRegistering] = useState(false);
    const [loginCreds, setLoginCreds] = useState({ username: '', password: '', nom: '', prenom: '', classe: '' });
    const [userProfile, setUserProfile] = useState<{ nom: string, prenom: string, classe: string } | null>(null);

    // App State
    const [documents, setDocuments] = useState<Document[]>([]);
    const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
    const [formData, setFormData] = useState({ nom: '', prenom: '', classe: '', age: '', duree_jours: '' });
    const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);
    const [demandes, setDemandes] = useState<Demande[]>([]);

    // Student Dashboard State
    const [showMyDemandes, setShowMyDemandes] = useState(false);
    const [myDemandes, setMyDemandes] = useState<Demande[]>([]);

    // Admin Edit State
    const [editingDoc, setEditingDoc] = useState<Document | null>(null);
    const [editQuantity, setEditQuantity] = useState<number>(0);

    // Reviews State
    const [detailedDoc, setDetailedDoc] = useState<Document | null>(null);
    const [reviews, setReviews] = useState<Review[]>([]);
    const [newReview, setNewReview] = useState({ rating: 5, comment: '' });

    // Search State
    const [searchTerm, setSearchTerm] = useState('');
    const [typeFilter, setTypeFilter] = useState('');

    useEffect(() => {
        fetchDocuments();
        if (token) {
            const decoded = parseJwt(token);
            if (decoded) {
                setUserRole(decoded.role);
            }
        }
    }, [token]);

    // Fetch user profile to auto-fill
    useEffect(() => {
        if (token && userRole === 'STUDENT') {
            getProfile().then(profile => {
                setUserProfile(profile);
                setFormData(prev => ({
                    ...prev,
                    nom: profile.nom || '',
                    prenom: profile.prenom || '',
                    classe: profile.classe || '',
                }));
            }).catch(err => console.error("Failed to fetch profile", err));
        }
    }, [token, userRole]);

    useEffect(() => {
        if (token && userRole === 'STUDENT' && showMyDemandes) {
            fetchMyDemandes();
        }
    }, [token, userRole, showMyDemandes]);

    // Debounced Search (Simple effect implementation)
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchDocuments();
        }, 300);
        return () => clearTimeout(timer);
    }, [searchTerm, typeFilter]);

    const fetchDocuments = async () => {
        try {
            const params: any = {};
            if (searchTerm) params.search = searchTerm;
            if (typeFilter) params.type = typeFilter;
            const response = await api.get<Document[]>('/documents', { params });
            setDocuments(response.data);
        } catch (error) {
            console.error('Error fetching documents:', error);
        }
    };

    const fetchDemandes = async () => {
        try {
            const response = await api.get<Demande[]>('/demandes');
            setDemandes(response.data);
        } catch (error) {
            console.error('Error fetching demandes:', error);
            alert("Erreur: Accès non autorisé (Admin seulement)");
        }
    };

    const fetchMyDemandes = async () => {
        try {
            const data = await getMyDemandes();
            setMyDemandes(data);
        } catch (error) {
            console.error("Error fetching my demandes", error);
        }
    };

    const handleLoginOrRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (isRegistering) {
                await register(loginCreds.username, loginCreds.password, {
                    nom: loginCreds.nom,
                    prenom: loginCreds.prenom,
                    classe: loginCreds.classe
                });
                alert("Inscription réussie ! Vous pouvez maintenant vous connecter.");
                setIsRegistering(false);
            } else {
                const data = await login(loginCreds.username, loginCreds.password);
                localStorage.setItem('token', data.access_token);
                setToken(data.access_token);
                setShowLogin(false);
                if (loginCreds.username === 'admin') setUserRole('ADMIN');
                else setUserRole('STUDENT');
            }
        } catch (error: any) {
            alert(isRegistering ? "Erreur lors de l'inscription (Nom d'utilisateur déjà pris ?)" : "Échec de la connexion");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUserRole(null);
        setDemandes([]);
        setMyDemandes([]);
        setShowMyDemandes(false);
        setEditingDoc(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedDocs.length === 0) {
            setMessage({ text: "Veuillez sélectionner au moins un document.", type: 'error' });
            return;
        }

        const selectedTitles = documents.filter(d => selectedDocs.includes(d.id)).map(d => d.titre).join(', ');
        const payload: DemandeCreate = {
            nom: formData.nom, prenom: formData.prenom, classe: formData.classe,
            age: parseInt(formData.age), date_demande: new Date().toISOString().split('T')[0],
            duree_jours: parseInt(formData.duree_jours), details_documents: selectedTitles
        };

        try {
            const response = await api.post('/demandes', payload);
            setMessage({ text: response.data.message, type: 'success' });
            setFormData({ nom: '', prenom: '', classe: '', age: '', duree_jours: '' });
            setSelectedDocs([]);
            // Refresh availability
            fetchDocuments();
            if (showMyDemandes) fetchMyDemandes();
        } catch (error: any) {
            const errorMsg = error.response?.data?.detail || "Erreur lors de l'envoi de la demande.";
            setMessage({ text: errorMsg, type: 'error' });
        }
    };

    const handleApprouver = async (id: number) => {
        try {
            await api.patch(`/demandes/${id}/approuver`);
            fetchDemandes();
        } catch (error) {
            alert("Erreur lors de l'approbation.");
        }
    };

    const toggleDocument = (id: number) => {
        const doc = documents.find(d => d.id === id);
        if (!doc) return;

        // Prevent selecting if unavailable and not currently selected
        if (!selectedDocs.includes(id) && (doc.available === 0)) {
            return;
        }

        setSelectedDocs(prev => prev.includes(id) ? prev.filter(d => d !== id) : [...prev, id]);
    };

    const handleRelance = (d: Demande) => {
        alert(`📧 Simulation: Email de rappel envoyé à ${d.prenom} ${d.nom} (Classe: ${d.classe}) pour le retour prévu le ${d.date_retour_prevue}.`);
    };

    const isOverdue = (dateStr: string | null | undefined) => {
        if (!dateStr) return false;
        const today = new Date().toISOString().split('T')[0];
        return dateStr < today;
    };

    const handleViewDetails = async (doc: Document) => {
        setDetailedDoc(doc);
        const fetchedReviews = await getReviews(doc.id);
        setReviews(fetchedReviews);
    };

    const submitReview = async () => {
        if (!detailedDoc) return;
        try {
            await addReview(detailedDoc.id, newReview.rating, newReview.comment);
            const updatedReviews = await getReviews(detailedDoc.id);
            setReviews(updatedReviews);
            setNewReview({ rating: 5, comment: '' });
        } catch (error) {
            alert("Erreur lors de l'envoi de l'avis.");
        }
    };


    const handleReturn = async (id: number) => {
        if (confirm("Confirmer le retour des documents ?")) {
            try {
                await returnDemande(id);
                fetchDemandes(); // Refresh list
                fetchDocuments(); // Refresh stock
            } catch (error) {
                alert("Erreur lors du retour.");
            }
        }
    };

    const handleEditStock = (doc: Document) => {
        setEditingDoc(doc);
        setEditQuantity(doc.quantity);
    };

    const saveStock = async () => {
        if (!editingDoc) return;
        try {
            await updateDocument(editingDoc.id, { quantity: editQuantity });
            setEditingDoc(null);
            fetchDocuments(); // Refresh list
            alert("Stock mis à jour !");
        } catch (error) {
            console.error("Failed to update stock", error);
            alert("Erreur lors de la mise à jour.");
        }
    };

    if (showLogin) {
        return (
            <div className="min-h-screen bg-slate-900/50 backdrop-blur-md flex items-center justify-center p-4" style={{ zIndex: 50 }}>
                <div className="bg-white/10 backdrop-blur-xl border border-white/20 p-8 rounded-3xl shadow-2xl w-full max-w-sm">
                    <h2 className="text-3xl font-bold mb-6 text-center text-white">{isRegistering ? 'Inscription' : 'Connexion'}</h2>
                    <form onSubmit={handleLoginOrRegister} className="space-y-4">
                        <input placeholder="Username" value={loginCreds.username} onChange={e => setLoginCreds({ ...loginCreds, username: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                        <input type="password" placeholder="Password" value={loginCreds.password} onChange={e => setLoginCreds({ ...loginCreds, password: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />

                        {isRegistering && (
                            <>
                                <div className="grid grid-cols-2 gap-4">
                                    <input placeholder="Prénom" value={loginCreds.prenom} onChange={e => setLoginCreds({ ...loginCreds, prenom: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                    <input placeholder="Nom" value={loginCreds.nom} onChange={e => setLoginCreds({ ...loginCreds, nom: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                </div>
                                <input placeholder="Classe (ex: Terminale S2)" value={loginCreds.classe} onChange={e => setLoginCreds({ ...loginCreds, classe: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                            </>
                        )}

                        <button type="submit" className="w-full bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-indigo-500/30 transition-all transform hover:scale-[1.02]">
                            {isRegistering ? "S'inscrire" : "Se connecter"}
                        </button>

                        <div className="flex justify-between items-center text-sm mt-4">
                            <button type="button" onClick={() => setIsRegistering(!isRegistering)} className="text-indigo-300 hover:text-white transition underline">
                                {isRegistering ? "J'ai déjà un compte" : "Créer un compte"}
                            </button>
                            <button type="button" onClick={() => setShowLogin(false)} className="text-slate-400 hover:text-white transition">Fermer</button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen py-8 px-4 font-sans text-slate-100">
            <div className="max-w-7xl mx-auto relative">
                <header className="mb-10 flex flex-col md:flex-row justify-between items-center bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-3xl shadow-xl">
                    <div className="mb-4 md:mb-0 text-center md:text-left">
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-300 via-indigo-300 to-purple-300">CDM Réservations</h1>
                        <p className="text-slate-400 mt-1">Espace de réservation multimédia</p>
                    </div>
                    <div>
                        {token ? (
                            <div className="flex items-center gap-4">
                                <span className="font-semibold text-slate-300">Bonjour, {userRole}</span>
                                {userRole === 'STUDENT' && (
                                    <button onClick={() => setShowMyDemandes(true)} className="bg-indigo-500/20 text-indigo-300 px-4 py-2 rounded-xl border border-indigo-500/30 hover:bg-indigo-500/30 transition">Mes Réservations</button>
                                )}
                                <button onClick={handleLogout} className="bg-red-500/10 text-red-300 px-4 py-2 rounded-xl border border-red-500/20 hover:bg-red-500/20 transition">Déconnexion</button>
                            </div>
                        ) : (
                            <button onClick={() => setShowLogin(true)} className="bg-white/10 text-white px-6 py-3 rounded-xl hover:bg-white/20 border border-white/10 transition font-medium backdrop-blur-lg">Espace Admin</button>
                        )}
                    </div>
                </header>

                <main className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Form Side */}
                    <div className="lg:col-span-4 space-y-8">
                        <section className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-3xl shadow-xl">
                            <h2 className="text-xl font-bold mb-6 flex items-center text-white">
                                <span className="bg-indigo-500 text-white w-8 h-8 flex items-center justify-center rounded-lg mr-3 text-sm shadow-lg shadow-indigo-500/30">1</span>
                                Vos Informations
                            </h2>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <input required placeholder="Nom" name="nom" value={formData.nom} onChange={(e: any) => setFormData({ ...formData, nom: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                <input required placeholder="Prénom" name="prenom" value={formData.prenom} onChange={(e: any) => setFormData({ ...formData, prenom: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                <div className="grid grid-cols-2 gap-4">
                                    <input required placeholder="Classe" name="classe" value={formData.classe} onChange={(e: any) => setFormData({ ...formData, classe: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                    <input required type="number" placeholder="Âge" name="age" value={formData.age} onChange={(e: any) => setFormData({ ...formData, age: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition" />
                                </div>
                                <select required name="duree_jours" value={formData.duree_jours} onChange={(e: any) => setFormData({ ...formData, duree_jours: e.target.value })} className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-400 outline-none transition appearance-none">
                                    <option value="" className="text-black">Durée d'emprunt...</option>
                                    <option value="7" className="text-black">7 jours</option>
                                    <option value="14" className="text-black">14 jours</option>
                                </select>
                                <button type="submit" className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-indigo-500/30 transition-all transform hover:scale-[1.02]">
                                    Envoyer la demande
                                </button>
                            </form>
                            {message && <div className={`mt-4 p-4 rounded-xl text-sm font-medium border ${message.type === 'success' ? 'bg-green-500/20 text-green-200 border-green-500/30' : 'bg-red-500/20 text-red-200 border-red-500/30'}`}>{message.text}</div>}
                        </section>

                        {userRole === 'ADMIN' && (
                            <section className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-3xl shadow-xl">
                                <h2 className="text-xl font-bold mb-4 text-white">Zone Admin</h2>
                                <button onClick={fetchDemandes} className="w-full bg-white/5 border border-white/10 text-white font-medium py-3 rounded-xl hover:bg-white/10 transition mb-4">Rafraîchir les demandes</button>

                                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                                    {demandes.filter(d => d.status !== 'RETOURNÉE').map(d => (
                                        <div key={d.id} className="p-4 rounded-xl bg-black/20 border border-white/5 text-sm hover:bg-black/30 transition">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="font-bold text-white text-lg">{d.prenom} {d.nom}</span>
                                                <div className="flex gap-2">
                                                    {isOverdue(d.date_retour_prevue) && d.status !== 'RETOURNÉE' && (
                                                        <span className="px-2 py-1 rounded-lg text-xs font-bold bg-red-500 text-white animate-pulse">RETARD</span>
                                                    )}
                                                    <span className={`px-3 py-1 rounded-lg text-xs font-bold ${d.status === 'APPROUVÉE' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'}`}>{d.status}</span>
                                                </div>
                                            </div>
                                            <p className="text-slate-400 mb-2 italic">Class: {d.classe} | Age: {d.age}</p>
                                            <p className="text-slate-300 mb-3 bg-white/5 p-2 rounded-lg">{d.details_documents}</p>
                                            <div className="flex justify-between items-center text-xs text-slate-500">
                                                <span className={`${isOverdue(d.date_retour_prevue) && d.status !== 'RETOURNÉE' ? 'text-red-400 font-bold' : 'font-mono'}`}>Retour: {d.date_retour_prevue || 'N/A'}</span>
                                                <div className="flex gap-2">
                                                    {isOverdue(d.date_retour_prevue) && d.status === 'APPROUVÉE' && (
                                                        <button onClick={() => handleRelance(d)} className="bg-orange-500 text-white px-3 py-1 rounded-lg hover:bg-orange-600 transition shadow-lg shadow-orange-500/30">Relancer</button>
                                                    )}
                                                    {d.status !== 'APPROUVÉE' && <button onClick={() => handleApprouver(d.id)} className="bg-indigo-500 text-white px-3 py-1 rounded-lg hover:bg-indigo-600 transition shadow-lg shadow-indigo-500/30">Approuver</button>}
                                                    {d.status === 'APPROUVÉE' && <button onClick={() => handleReturn(d.id)} className="bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 transition shadow-lg shadow-green-600/30">Rendue</button>}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {demandes.length === 0 && <p className="text-center text-slate-500 py-4">Aucune demande.</p>}
                                </div>
                            </section>
                        )}
                    </div>

                    {/* Document Grid */}
                    <div className="lg:col-span-8">
                        <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-3xl shadow-xl min-h-full">
                            <div className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
                                <h2 className="text-2xl font-bold text-white flex items-center">
                                    <span className="bg-purple-500 text-white w-8 h-8 flex items-center justify-center rounded-lg mr-3 text-sm shadow-lg shadow-purple-500/30">2</span>
                                    Catalogue
                                </h2>
                                <div className="flex gap-2 w-full sm:w-auto">
                                    <input placeholder="Rechercher..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="px-5 py-2.5 rounded-xl bg-black/20 border border-white/5 text-white placeholder-slate-400 focus:ring-2 focus:ring-purple-400 outline-none text-sm w-full" />
                                    <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="px-5 py-2.5 rounded-xl bg-black/20 border border-white/5 text-white focus:ring-2 focus:ring-purple-400 outline-none text-sm appearance-none cursor-pointer">
                                        <option value="" className="text-black">Tout</option>
                                        <option value="LIVRE" className="text-black">Livres</option>
                                        <option value="DVD" className="text-black">DVD</option>
                                        <option value="CD" className="text-black">CD</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
                                {documents.map(doc => {
                                    // available defaults to quantity if null (for old seed data compatibility) but really simple logic:
                                    const available = doc.available !== undefined ? doc.available : 1;
                                    const isOutOfStock = available <= 0;

                                    return (
                                        <div
                                            key={doc.id}
                                            onClick={() => userRole === 'ADMIN' ? handleEditStock(doc) : handleViewDetails(doc)}
                                            className={`relative group cursor-pointer rounded-2xl overflow-hidden transition-all duration-300 ${isOutOfStock ? 'opacity-60 grayscale cursor-not-allowed' : ''} ${selectedDocs.includes(doc.id) ? 'ring-4 ring-indigo-500 transform scale-95 shadow-2xl shadow-indigo-500/50' : 'hover:transform hover:scale-105 hover:shadow-xl hover:shadow-black/40'}`}
                                        >
                                            <div className="aspect-[2/3] bg-slate-800 relative">
                                                {doc.image_url ? (
                                                    <img src={doc.image_url} alt={doc.titre} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                                                ) : (
                                                    <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 p-4 text-center">
                                                        <span className="text-4xl mb-2">📚</span>
                                                        <span className="text-xs">Pas d'image</span>
                                                    </div>
                                                )}

                                                {/* Selection Overlay (Only for non-Admins) */}
                                                {!isOutOfStock && userRole !== 'ADMIN' && (
                                                    <div className={`absolute inset-0 bg-indigo-900/60 backdrop-blur-[2px] flex items-center justify-center transition-opacity duration-300 ${selectedDocs.includes(doc.id) ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                                                        <div className={`rounded-full p-3 transform transition-transform duration-300 ${selectedDocs.includes(doc.id) ? 'bg-white text-indigo-600 scale-110' : 'bg-white/20 text-white scale-100'}`}>
                                                            {selectedDocs.includes(doc.id) ? (
                                                                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                                                            ) : (
                                                                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Admin Edit Overlay Hint */}
                                                {userRole === 'ADMIN' && (
                                                    <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-bold border border-white/30 backdrop-blur-md">Modifier Stock</span>
                                                    </div>
                                                )}

                                                {/* Out of Stock Overlay */}
                                                {isOutOfStock && (
                                                    <div className="absolute inset-0 bg-black/60 backdrop-blur-[1px] flex items-center justify-center">
                                                        <span className="bg-red-500/80 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border border-white/20 transform -rotate-12">Rupture</span>
                                                    </div>
                                                )}

                                                {/* Type Badge */}
                                                <div className="absolute top-2 right-2 px-2 py-1 rounded-md bg-black/60 backdrop-blur-md text-[10px] font-bold text-white uppercase tracking-wider border border-white/10">
                                                    {doc.type}
                                                </div>

                                                {/* Stock Count */}
                                                <div className="absolute bottom-2 left-2 px-2 py-1 rounded-md bg-black/60 backdrop-blur-md text-[10px] font-bold text-slate-200 border border-white/10">
                                                    {available} dispo / {doc.quantity} total
                                                </div>
                                            </div>
                                            <div className="p-4 bg-white/5 backdrop-blur-md border-t border-white/5 h-full flex flex-col justify-between">
                                                <h3 className="font-bold text-slate-100 text-sm leading-tight line-clamp-2 mb-2" title={doc.titre}>{doc.titre}</h3>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </main>

                {/* Edit Stock Modal */}
                {editingDoc && (
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4" onClick={() => setEditingDoc(null)}>
                        <div className="bg-[#1e1b4b] border border-white/10 p-6 rounded-3xl w-full max-w-sm shadow-2xl" onClick={e => e.stopPropagation()}>
                            <h3 className="text-xl font-bold text-white mb-4">Modifier le Stock</h3>
                            <p className="text-slate-400 text-sm mb-4">{editingDoc.titre}</p>

                            <div className="mb-6">
                                <label className="block text-slate-300 text-xs uppercase font-bold mb-2">Quantité Totale</label>
                                <input
                                    type="number"
                                    min="0"
                                    value={editQuantity}
                                    onChange={e => setEditQuantity(parseInt(e.target.value) || 0)}
                                    className="w-full px-5 py-3 rounded-xl bg-black/20 border border-white/10 text-white outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>

                            <div className="flex gap-3">
                                <button onClick={() => setEditingDoc(null)} className="flex-1 bg-white/5 hover:bg-white/10 text-white py-3 rounded-xl transition font-medium">Annuler</button>
                                <button onClick={saveStock} className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-xl shadow-lg shadow-indigo-500/30 transition font-bold">Sauvegarder</button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Document Details Modal with Reviews */}
                {detailedDoc && (
                    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-[70] p-4" onClick={() => setDetailedDoc(null)}>
                        <div className="bg-[#1e1b4b] border border-white/10 rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[90vh]" onClick={e => e.stopPropagation()}>
                            {/* Left: Image & Actions */}
                            <div className="md:w-1/3 bg-black/20 p-6 flex flex-col items-center">
                                <img src={detailedDoc.image_url} alt={detailedDoc.titre} className="w-48 rounded-lg shadow-2xl mb-6 object-cover" />
                                <h3 className="text-2xl font-bold text-white text-center mb-2">{detailedDoc.titre}</h3>
                                <p className="text-indigo-300 font-medium mb-6">{detailedDoc.type}</p>

                                <button
                                    onClick={() => { toggleDocument(detailedDoc.id); setDetailedDoc(null); }}
                                    className={`w-full py-3 rounded-xl font-bold transition shadow-lg ${selectedDocs.includes(detailedDoc.id) ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30' : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-indigo-500/30'}`}
                                >
                                    {selectedDocs.includes(detailedDoc.id) ? 'Retirer de la demande' : 'Ajouter à la demande'}
                                </button>
                            </div>

                            {/* Right: Reviews using API */}
                            <div className="md:w-2/3 p-8 flex flex-col overflow-hidden">
                                <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                                    <h4 className="text-xl font-bold text-white mb-6 flex items-center">
                                        <span className="mr-2">⭐</span> Avis ({reviews.length})
                                    </h4>

                                    <div className="space-y-4 mb-8">
                                        {reviews.length === 0 ? (
                                            <p className="text-slate-500 italic">Soyez le premier à donner votre avis !</p>
                                        ) : (
                                            reviews.map((r, idx) => (
                                                <div key={idx} className="bg-white/5 p-4 rounded-xl border border-white/5">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <span className="font-bold text-white text-sm">{r.username}</span>
                                                        <div className="flex text-yellow-500 text-xs">
                                                            {[...Array(5)].map((_, i) => (
                                                                <span key={i}>{i < r.rating ? '★' : '☆'}</span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                    {r.comment && <p className="text-slate-300 text-sm">{r.comment}</p>}
                                                    <div className="text-right mt-1 text-[10px] text-slate-500">{r.date}</div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>

                                {/* Add Review Form */}
                                <div className="pt-6 border-t border-white/10 mt-auto">
                                    <h5 className="text-white font-bold mb-3 text-sm">Ajouter un avis</h5>
                                    <div className="flex gap-2 mb-3">
                                        {[1, 2, 3, 4, 5].map(star => (
                                            <button
                                                key={star}
                                                onClick={() => setNewReview({ ...newReview, rating: star })}
                                                className={`text-2xl transition ${star <= newReview.rating ? 'text-yellow-400 scale-110' : 'text-slate-600 hover:text-slate-400'}`}
                                            >
                                                ★
                                            </button>
                                        ))}
                                    </div>
                                    <div className="flex gap-2">
                                        <input
                                            placeholder="Votre commentaire..."
                                            value={newReview.comment}
                                            onChange={e => setNewReview({ ...newReview, comment: e.target.value })}
                                            className="flex-1 px-4 py-2 rounded-xl bg-black/20 border border-white/5 text-white text-sm outline-none focus:ring-1 focus:ring-indigo-500"
                                        />
                                        <button onClick={submitReview} className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-xl transition font-bold text-sm">Publier</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}


                {/* Student Dashboard Modal */}
                {showMyDemandes && (
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowMyDemandes(false)}>
                        <div className="bg-[#1e1b4b] border border-white/10 rounded-3xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
                            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                                <h2 className="text-2xl font-bold text-white">Mes Réservations</h2>
                                <button onClick={() => setShowMyDemandes(false)} className="text-slate-400 hover:text-white transition">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                                </button>
                            </div>
                            <div className="p-6 overflow-y-auto custom-scrollbar space-y-4">
                                {myDemandes.length === 0 ? (
                                    <div className="text-center py-10 text-slate-500">
                                        <p>Vous n'avez aucune réservation en cours.</p>
                                    </div>
                                ) : (
                                    myDemandes.map(d => (
                                        <div key={d.id} className="bg-white/5 p-4 rounded-xl border border-white/5 hover:bg-white/10 transition">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex items-center gap-2">
                                                    <span className={`w-2 h-2 rounded-full ${d.status === 'APPROUVÉE' ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
                                                    <span className="font-bold text-slate-200">Demande du {d.date_demande}</span>
                                                </div>
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${d.status === 'APPROUVÉE' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'}`}>{d.status}</span>
                                            </div>
                                            <p className="text-slate-300 text-sm mb-2 pl-4">{d.details_documents}</p>
                                            <div className="flex justify-between items-center text-xs text-slate-500 pl-4">
                                                <span>Durée: {d.duree_jours} jours</span>
                                                {d.date_retour_prevue && <span>Retour le: {d.date_retour_prevue}</span>}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                            <div className="p-4 border-t border-white/10 bg-white/5 text-right">
                                <button onClick={() => setShowMyDemandes(false)} className="px-6 py-2 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition">Fermer</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
