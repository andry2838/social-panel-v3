import { useState } from 'react'
import { Home, Users, Target, Calendar, MessageCircle, Rocket, TrendingUp, Settings, Heart, Plus } from 'lucide-react'
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
  return (
    <div className="fade-in">
      <div className="header-wrapper">
        <div>
          <h1 className="page-title">Bienvenue, Boss 🚀</h1>
          <p style={{color: 'var(--text-muted)'}}>Voici les performances globales de tes comptes aujourd'hui.</p>
        </div>
        <button className="btn-primary">
          <Plus size={18} /> Nouvelle Campagne
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
          <div className="metric-title"><Rocket size={16} color="#10b981"/> Comptes Connectés</div>
          <div className="metric-value">12 <span style={{fontSize:'1rem', color:'var(--text-muted)'}}>(Illimité)</span></div>
        </div>
      </div>
      
      <div className="glass-card" style={{height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <p style={{color: 'var(--text-muted)'}}>Graphique de croissance interactive (Recharts ou Chart.js sera injecté ici)</p>
      </div>
    </div>
  )
}

function AccountsView() {
  return (
    <div className="fade-in">
      <h1 className="page-title" style={{marginBottom: '2rem'}}>Comptes Connectés ♾️</h1>
      <div className="glass-card">
        <p style={{color: 'var(--text-muted)'}}>Interface de gestion des proxies et des sessions Instagram en cours de construction avec les vraies données de l'API.</p>
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
