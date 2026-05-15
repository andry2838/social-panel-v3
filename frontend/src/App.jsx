import { useState, useEffect } from 'react'
import { Home, Users, Target, Calendar, MessageCircle, Rocket, TrendingUp, Settings, Heart, Plus, FileText, Download } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView />
      case 'accounts':
        return <AccountsView />
      case 'campaigns':
        return <CampaignsView />
      default:
        return <DashboardView />
    }
  }

  return (
    <>
      <div className="background-mesh"></div>
      <div className="dashboard-container">
        
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="logo-container">
            <Rocket size={28} color="#ec4899" />
            <span>BoostPanel</span>
          </div>
          
          <nav className="nav-menu">
            <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
              <Home size={20} /> Vue d'ensemble
            </div>
            <div className={`nav-item ${activeTab === 'accounts' ? 'active' : ''}`} onClick={() => setActiveTab('accounts')}>
              <Users size={20} /> Comptes <span style={{marginLeft:'auto', fontSize:'0.7rem', background:'#ec4899', color:'white', padding:'2px 6px', borderRadius:'10px'}}>Illimité</span>
            </div>
            <div className={`nav-item ${activeTab === 'campaigns' ? 'active' : ''}`} onClick={() => setActiveTab('campaigns')}>
              <Target size={20} /> Campagnes IA
            </div>
            <div className={`nav-item ${activeTab === 'content' ? 'active' : ''}`} onClick={() => setActiveTab('content')}>
              <Calendar size={20} /> Contenu & Calendrier
            </div>
            <div className={`nav-item ${activeTab === 'messages' ? 'active' : ''}`} onClick={() => setActiveTab('messages')}>
              <MessageCircle size={20} /> Auto-DM & Inbox
            </div>
          </nav>
          
          <div style={{marginTop: 'auto', padding: '1rem', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '12px', border: '1px solid rgba(139, 92, 246, 0.3)'}}>
            <p style={{fontSize: '0.8rem', color: '#a78bfa', marginBottom: '10px'}}>Mode Premium Activé 💎</p>
            <div style={{width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px'}}>
              <div style={{width: '100%', height: '100%', background: 'linear-gradient(90deg, #8b5cf6, #ec4899)', borderRadius: '2px', boxShadow: '0 0 10px #ec4899'}}></div>
            </div>
          </div>
        </aside>

        {/* Main Area */}
        <main className="main-content">
          {renderContent()}
        </main>
      </div>
    </>
  )
}

function DashboardView() {
  const [campaigns, setCampaigns] = useState([])

  useEffect(() => {
    fetch('/api/v1/campaigns')
      .then(res => res.json())
      .then(data => {
        if(data.campaigns) setCampaigns(data.campaigns)
      })
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="fade-in">
      <div className="header-wrapper">
        <div>
          <h1 className="page-title">Bienvenue, Boss 🚀</h1>
          <p style={{color: 'var(--text-muted)'}}>Voici les performances globales de tes comptes aujourd'hui.</p>
        </div>
        <button className="btn-primary" onClick={() => window.location.reload()}>
          <TrendingUp size={18} /> Actualiser
        </button>
      </div>

      <div className="metrics-grid">
        <div className="glass-card stagger-1">
          <div className="metric-title"><Users size={16} color="#8b5cf6"/> Nouveaux Followers</div>
          <div className="metric-value">+ 1,240</div>
          <div className="metric-trend"><TrendingUp size={14}/> +12% ce mois-ci</div>
        </div>
        <div className="glass-card stagger-2">
          <div className="metric-title"><Heart size={16} color="#ec4899"/> Engagement Total</div>
          <div className="metric-value">14.2K</div>
          <div className="metric-trend"><TrendingUp size={14}/> +8% ce mois-ci</div>
        </div>
        <div className="glass-card stagger-3">
          <div className="metric-title"><Target size={16} color="#38bdf8"/> Actions Automatisées</div>
          <div className="metric-value">45,892</div>
        </div>
        <div className="glass-card stagger-4">
          <div className="metric-title"><FileText size={16} color="#10b981"/> Campagnes Lancées</div>
          <div className="metric-value">{campaigns.length}</div>
        </div>
      </div>
      
      <h2 style={{fontSize: '1.5rem', marginBottom: '1.5rem', marginTop: '3rem'}}>Dernières Campagnes & Rapports PDF</h2>
      <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
        {campaigns.length === 0 ? (
          <div className="glass-card" style={{textAlign: 'center', padding: '3rem'}}>
            <p style={{color: 'var(--text-muted)'}}>Aucune campagne en cours. Va dans l'onglet "Campagnes IA" pour en lancer une !</p>
          </div>
        ) : (
          campaigns.map(camp => (
            <div key={camp.id} className="glass-card stagger-1" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
              <div>
                <h3 style={{fontSize: '1.2rem', marginBottom: '5px'}}>{camp.name}</h3>
                <p style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>Statut: <span style={{color: camp.status === 'running' ? '#38bdf8' : '#10b981'}}>{camp.status.toUpperCase()}</span> | Type: {camp.type}</p>
              </div>
              <a 
                href={`/api/v1/reports/${camp.id}/download?agency_name=BoostPanel+Agency`} 
                target="_blank"
                rel="noreferrer"
                style={{textDecoration: 'none'}}
              >
                <button className="btn-primary" style={{background: 'linear-gradient(135deg, #10b981, #059669)'}}>
                  <Download size={18} /> Télécharger le PDF Marque Blanche
                </button>
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function AccountsView() {
  const [form, setForm] = useState({
    username: '', password: '', platform: 'instagram',
    proxy: '', two_factor_seed: '', tags: ''
  })
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(() => {
    fetch('/api/v1/accounts')
      .then(res => res.json())
      .then(data => { if(data.accounts) setAccounts(data.accounts) })
      .catch(console.error)
  }, [])

  const handleAdd = async () => {
    setLoading(true)
    setMsg(null)
    try {
      const payload = {
        username: form.username,
        password: form.password,
        platform: form.platform,
        proxy: form.proxy || null,
        two_factor_seed: form.two_factor_seed || null,
        tags: form.tags ? form.tags.split(',').map(t => t.trim()) : []
      }
      const res = await fetch('/api/v1/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (res.ok) {
        setMsg({ type: 'success', text: `✅ Compte @${data.username} ajouté avec succès !` })
        setAccounts(prev => [...prev, data])
        setForm({ username: '', password: '', platform: 'instagram', proxy: '', two_factor_seed: '', tags: '' })
      } else {
        setMsg({ type: 'error', text: `❌ Erreur: ${data.detail}` })
      }
    } catch(e) { setMsg({ type: 'error', text: `❌ Erreur réseau` }) }
    setLoading(false)
  }

  return (
    <div className="fade-in">
      <h1 className="page-title" style={{marginBottom: '2rem'}}>Comptes Connectés ♾️</h1>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '3rem'}}>
        {/* Formulaire d'ajout */}
        <div className="glass-card">
          <h2 style={{fontSize: '1.2rem', marginBottom: '1.5rem'}}>➕ Ajouter un Compte</h2>

          {msg && (
            <div style={{padding: '0.8rem', borderRadius: '8px', marginBottom: '1rem',
              background: msg.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(236, 72, 153, 0.15)',
              border: `1px solid ${msg.type === 'success' ? '#10b981' : '#ec4899'}`,
              color: msg.type === 'success' ? '#10b981' : '#ec4899'}}>
              {msg.text}
            </div>
          )}

          <div className="input-group">
            <label className="input-label">Plateforme</label>
            <select className="modern-input" value={form.platform}
              onChange={e => setForm({...form, platform: e.target.value})}
              style={{background: 'rgba(15,23,42,0.5)', color: 'white', border: '1px solid rgba(139,92,246,0.3)'}}>
              <option value="instagram">📸 Instagram</option>
              <option value="threads">🧵 Threads</option>
              <option value="twitter">🐦 Twitter/X</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Nom d'utilisateur</label>
            <input className="modern-input" type="text" placeholder="@mon_compte_ig"
              value={form.username} onChange={e => setForm({...form, username: e.target.value})} />
          </div>

          <div className="input-group">
            <label className="input-label">Mot de passe</label>
            <input className="modern-input" type="password" placeholder="••••••••"
              value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          </div>

          <div className="input-group">
            <label className="input-label">🔐 Code Secret 2FA (TOTP Seed) <span style={{color:'#ec4899'}}>Optionnel</span></label>
            <input className="modern-input" type="text" 
              placeholder="Ex: JBSWY3DPEHPK3PXP (depuis Google Authenticator)"
              value={form.two_factor_seed} onChange={e => setForm({...form, two_factor_seed: e.target.value})} />
            <small style={{color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '4px', display: 'block'}}>
              Dans Instagram → Paramètres → Authentification à deux facteurs → App d'authentification → Clé manuelle
            </small>
          </div>

          <div className="input-group">
            <label className="input-label">Proxy <span style={{color:'var(--text-muted)'}}>Optionnel</span></label>
            <input className="modern-input" type="text" placeholder="http://user:pass@ip:port"
              value={form.proxy} onChange={e => setForm({...form, proxy: e.target.value})} />
          </div>

          <button className="btn-primary" style={{width: '100%', justifyContent: 'center', marginTop: '0.5rem'}}
            onClick={handleAdd} disabled={loading || !form.username || !form.password}>
            {loading ? 'Connexion en cours...' : '🔌 Connecter le Compte'}
          </button>
        </div>

        {/* Liste des comptes */}
        <div className="glass-card" style={{overflowY: 'auto', maxHeight: '500px'}}>
          <h2 style={{fontSize: '1.2rem', marginBottom: '1.5rem'}}>📋 Comptes Enregistrés ({accounts.length})</h2>
          {accounts.length === 0 ? (
            <p style={{color: 'var(--text-muted)', textAlign: 'center', padding: '2rem'}}>Aucun compte connecté</p>
          ) : (
            accounts.map(acc => (
              <div key={acc.id} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.8rem', marginBottom: '0.8rem', borderRadius: '10px',
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)'}}>
                <div>
                  <div style={{fontWeight: '600'}}>@{acc.username}</div>
                  <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
                    {acc.platform} · {acc.two_factor_seed ? '🔐 2FA Activé' : '⚠️ Sans 2FA'}
                  </div>
                </div>
                <div style={{
                  padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem',
                  background: acc.status === 'active' ? 'rgba(16,185,129,0.2)' : 'rgba(236,72,153,0.2)',
                  color: acc.status === 'active' ? '#10b981' : '#ec4899'
                }}>
                  {acc.status || 'pending'}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function CampaignsView() {
  const [name, setName] = useState('')
  const [targets, setTargets] = useState('')
  const [features, setFeatures] = useState({
    autoLike: true,
    autoFollow: true,
    storyView: false,
    welcomeDm: false
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const toggleFeature = (feat) => {
    setFeatures({...features, [feat]: !features[feat]})
  }

  const handleLaunch = async () => {
    setLoading(true)
    try {
      const payload = {
        account_id: "demo_account", // En vrai, récupéré d'un selecteur
        name: name || "Nouvelle Campagne",
        type: "EXPERT",
        targets: { competitors: targets.split(',').map(t => t.trim()) },
        features: { 
          story_interactions: features.storyView,
          smart_follow: features.autoFollow,
          auto_like: features.autoLike
        },
        ai_settings: { lang_filter: ["fr"] },
        activity_settings: {}
      }
      
      const response = await fetch('/api/v1/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (response.ok) {
        setSuccess(true)
        setTimeout(() => setSuccess(false), 3000)
      }
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  return (
    <div className="fade-in">
      <h1 className="page-title" style={{marginBottom: '2rem'}}>🎯 Campagnes d'Acquisition</h1>
      
      <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem'}}>
        <div className="glass-card">
          <h2 style={{fontSize: '1.2rem', marginBottom: '1.5rem'}}>Configuration de la Campagne</h2>
          
          <div className="input-group">
            <label className="input-label">Nom de la campagne</label>
            <input 
              className="modern-input" 
              type="text" 
              placeholder="Ex: Croissance Estivale 2026"
              value={name}
              onChange={(e) => setName(e.target.value)} 
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Cibles (Comptes concurrents, hashtags)</label>
            <textarea 
              className="modern-input" 
              rows="4" 
              placeholder="@concurrent1, @concurrent2"
              value={targets}
              onChange={(e) => setTargets(e.target.value)}
            ></textarea>
          </div>
          
          <h3 style={{fontSize: '1rem', margin: '2rem 0 1rem 0', color: 'var(--primary)'}}>Fonctionnalités Activées</h3>
          
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
            <div className={`modern-toggle ${features.autoLike ? 'active' : ''}`} onClick={() => toggleFeature('autoLike')}>
              <span>👍 Auto-Like</span>
              <div style={{width: '20px', height: '20px', borderRadius: '50%', background: features.autoLike ? 'var(--primary)' : 'transparent', border: features.autoLike ? 'none' : '2px solid var(--border-card)'}}></div>
            </div>
            <div className={`modern-toggle ${features.autoFollow ? 'active' : ''}`} onClick={() => toggleFeature('autoFollow')}>
              <span>👤 Auto-Follow</span>
              <div style={{width: '20px', height: '20px', borderRadius: '50%', background: features.autoFollow ? 'var(--primary)' : 'transparent', border: features.autoFollow ? 'none' : '2px solid var(--border-card)'}}></div>
            </div>
            <div className={`modern-toggle ${features.storyView ? 'active' : ''}`} onClick={() => toggleFeature('storyView')}>
              <span>👁️ Story View (Polls/Sliders)</span>
              <div style={{width: '20px', height: '20px', borderRadius: '50%', background: features.storyView ? 'var(--primary)' : 'transparent', border: features.storyView ? 'none' : '2px solid var(--border-card)'}}></div>
            </div>
            <div className={`modern-toggle ${features.welcomeDm ? 'active' : ''}`} onClick={() => toggleFeature('welcomeDm')}>
              <span>💌 Welcome DM</span>
              <div style={{width: '20px', height: '20px', borderRadius: '50%', background: features.welcomeDm ? 'var(--primary)' : 'transparent', border: features.welcomeDm ? 'none' : '2px solid var(--border-card)'}}></div>
            </div>
          </div>
        </div>
        
        <div className="glass-card" style={{height: 'fit-content', background: 'linear-gradient(180deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9))'}}>
          <h2 style={{fontSize: '1.2rem', marginBottom: '1.5rem'}}>Résumé</h2>
          <ul style={{listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1rem', color: 'var(--text-muted)'}}>
            <li><strong style={{color: 'white'}}>Type:</strong> Expert (Automatisé)</li>
            <li><strong style={{color: 'white'}}>Vitesse:</strong> Rapide 🚀</li>
            <li><strong style={{color: 'white'}}>Cibles:</strong> {targets.split(',').filter(x => x.trim()).length || 0} comptes</li>
            <li><strong style={{color: 'white'}}>Actions:</strong> {Object.values(features).filter(Boolean).length} modules actifs</li>
          </ul>
          <button 
            className="btn-primary" 
            style={{width: '100%', marginTop: '2rem', justifyContent: 'center'}}
            onClick={handleLaunch}
            disabled={loading}
          >
            {loading ? 'Lancement en cours...' : success ? '✅ Campagne Lancée !' : 'Lancer l\'Automatisme'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
