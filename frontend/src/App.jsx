import { useState, useEffect } from 'react'
import './App.css'

const NAV = [
  { id: 'dashboard', icon: '⚡', label: "Vue d'ensemble" },
  { id: 'accounts',  icon: '👥', label: 'Comptes', badge: '∞' },
  { id: 'campaigns', icon: '🎯', label: 'Campagnes IA' },
  { id: 'content',   icon: '📅', label: 'Contenu & Calendrier' },
  { id: 'messages',  icon: '💬', label: 'Auto-DM & Inbox' },
]

export default function App() {
  const [tab, setTab] = useState('dashboard')

  const pages = {
    dashboard: <DashboardPage />,
    accounts:  <AccountsPage />,
    campaigns: <CampaignsPage />,
    content:   <ContentPage />,
    messages:  <MessagesPage />,
  }

  return (
    <>
      {/* Animated background orbs */}
      <div className="orbs">
        <div className="orb orb1" />
        <div className="orb orb2" />
        <div className="orb orb3" />
      </div>

      <div className="shell">
        {/* ── SIDEBAR ── */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">🚀</div>
            <span className="sidebar-logo-text">BoostPanel</span>
          </div>

          {NAV.map(n => (
            <div key={n.id} className={`nav-item ${tab === n.id ? 'active' : ''}`} onClick={() => setTab(n.id)}>
              <span>{n.icon}</span>
              <span>{n.label}</span>
              {n.badge && <span className="nav-badge">{n.badge}</span>}
            </div>
          ))}

          <div className="sidebar-footer">
            <p>💎 Plan Premium Actif</p>
            <div className="progress-bar"><div className="progress-fill" style={{width:'100%'}} /></div>
          </div>
        </aside>

        {/* ── MAIN ── */}
        <main className="main">
          {pages[tab]}
        </main>
      </div>
    </>
  )
}

/* ════════════════════════════ DASHBOARD ════════════════════════════ */
function DashboardPage() {
  const [campaigns, setCampaigns] = useState([])

  useEffect(() => {
    fetch('/api/v1/campaigns').then(r => r.json()).then(d => {
      if (d.campaigns) setCampaigns(d.campaigns)
    }).catch(() => {})
  }, [])

  const metrics = [
    { icon: '👥', val: '+1,240', label: 'Nouveaux Followers', trend: '+12% ce mois' },
    { icon: '❤️', val: '14.2K',  label: 'Engagement Total',   trend: '+8% ce mois' },
    { icon: '⚡', val: '45,892', label: 'Actions Automatisées' },
    { icon: '📋', val: campaigns.length, label: 'Campagnes Lancées' },
  ]

  return (
    <div>
      <div className="page-header fade-up">
        <div>
          <div className="page-title">Bonjour, Boss 👋</div>
          <div className="page-sub">Voici les performances globales de tes comptes</div>
        </div>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>⟳ Rafraîchir</button>
      </div>

      <div className="metrics-row">
        {metrics.map((m, i) => (
          <div key={i} className={`metric-card fade-up-${i+1}`}>
            <div className="metric-icon">{m.icon}</div>
            <div className="metric-val">{m.val}</div>
            <div className="metric-label">{m.label}</div>
            {m.trend && <div className="metric-trend">↑ {m.trend}</div>}
          </div>
        ))}
      </div>

      <div className="section-title fade-up-2">Campagnes Récentes & Rapports PDF</div>
      <div>
        {campaigns.length === 0 ? (
          <div className="card fade-up-3" style={{textAlign:'center', padding:'48px', color:'var(--c-muted2)'}}>
            <div style={{fontSize:40, marginBottom:12}}>🎯</div>
            Aucune campagne. Va dans "Campagnes IA" pour en lancer une !
          </div>
        ) : campaigns.map(c => (
          <div key={c.id} className="campaign-row fade-up-2">
            <div>
              <div className="campaign-name">{c.name}</div>
              <div className="campaign-meta">Type: {c.type} · Statut: <span style={{color: c.status==='running'?'#38bdf8':'#10b981'}}>{c.status?.toUpperCase()}</span></div>
            </div>
            <a href={`/api/v1/reports/${c.id}/download?agency_name=BoostPanel+Agency`} target="_blank" rel="noreferrer" style={{textDecoration:'none'}}>
              <button className="btn btn-green">⬇ Rapport PDF</button>
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ════════════════════════════ ACCOUNTS ════════════════════════════ */
function AccountsPage() {
  const [form, setForm] = useState({ username:'', password:'', platform:'instagram', proxy:'', two_factor_seed:'', tags:'' })
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  const f = (k, v) => setForm(p => ({...p, [k]: v}))

  useEffect(() => {
    fetch('/api/v1/accounts').then(r => r.json()).then(d => { if(d.accounts) setAccounts(d.accounts) }).catch(()=>{})
  }, [])

  const submit = async () => {
    setLoading(true); setMsg(null)
    try {
      const res = await fetch('/api/v1/accounts', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ username:form.username, password:form.password, platform:form.platform,
          proxy:form.proxy||null, two_factor_seed:form.two_factor_seed||null,
          tags: form.tags ? form.tags.split(',').map(t=>t.trim()) : [] }) })
      const d = await res.json()
      if (res.ok) {
        setMsg({ok:true, txt:`✅ @${d.username} connecté !`})
        setAccounts(p=>[...p, d])
        setForm({ username:'', password:'', platform:'instagram', proxy:'', two_factor_seed:'', tags:'' })
      } else setMsg({ok:false, txt:`❌ ${d.detail}`})
    } catch { setMsg({ok:false, txt:'❌ Erreur réseau'}) }
    setLoading(false)
  }

  const statusClass = s => s==='active'?'status-active':s==='banned'?'status-banned':'status-pending'

  return (
    <div>
      <div className="page-header fade-up">
        <div>
          <div className="page-title">Comptes Connectés ♾️</div>
          <div className="page-sub">Gérez vos comptes Instagram, Threads et Twitter/X sans limite</div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:24}}>
        {/* Formulaire */}
        <div className="card fade-up-2">
          <div className="section-title">➕ Ajouter un Compte</div>
          {msg && <div className={`alert ${msg.ok?'alert-success':'alert-error'}`}>{msg.txt}</div>}

          <div className="form-group">
            <label className="form-label">Plateforme</label>
            <select className="select" value={form.platform} onChange={e=>f('platform',e.target.value)}>
              <option value="instagram">📸 Instagram</option>
              <option value="threads">🧵 Threads</option>
              <option value="twitter">🐦 Twitter/X</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Nom d'utilisateur</label>
            <input className="input" placeholder="@mon_compte" value={form.username} onChange={e=>f('username',e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Mot de passe</label>
            <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={e=>f('password',e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">🔐 Clé 2FA TOTP <span>Optionnel</span></label>
            <input className="input" placeholder="JBSWY3DPEHPK3PXP" value={form.two_factor_seed} onChange={e=>f('two_factor_seed',e.target.value)} />
            <div className="input-hint">Instagram → Sécurité → 2FA → App d'authentification → Clé manuelle</div>
          </div>
          <div className="form-group">
            <label className="form-label">Proxy <span style={{color:'var(--c-muted)'}}>Optionnel</span></label>
            <input className="input" placeholder="http://user:pass@ip:port" value={form.proxy} onChange={e=>f('proxy',e.target.value)} />
          </div>
          <button className="btn btn-primary" style={{width:'100%', justifyContent:'center'}}
            onClick={submit} disabled={loading||!form.username||!form.password}>
            {loading ? '⏳ Connexion...' : '🔌 Connecter le Compte'}
          </button>
        </div>

        {/* Liste */}
        <div className="card fade-up-3" style={{overflow:'auto', maxHeight:560}}>
          <div className="section-title">📋 Comptes Enregistrés ({accounts.length})</div>
          {accounts.length === 0
            ? <div style={{textAlign:'center', padding:'40px', color:'var(--c-muted2)'}}>Aucun compte connecté</div>
            : accounts.map(a => (
                <div key={a.id} className="account-row">
                  <div>
                    <div className="account-name">@{a.username}</div>
                    <div className="account-meta">{a.platform} · {a.two_factor_seed ? '🔐 2FA Activé' : '⚠️ Sans 2FA'}</div>
                  </div>
                  <div className={`status-pill ${statusClass(a.status)}`}>{a.status||'pending'}</div>
                </div>
              ))
          }
        </div>
      </div>
    </div>
  )
}

/* ════════════════════════════ CAMPAIGNS ════════════════════════════ */
function CampaignsPage() {
  const [form, setForm] = useState({ name:'', targets:'', langFilter:'fr' })
  const [features, setFeatures] = useState({ autoLike:true, autoFollow:true, storyInteractions:false, aiComments:false, likTopComments:false, welcomeDm:false })
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  const toggleFeat = k => setFeatures(p => ({...p, [k]: !p[k]}))
  const f = (k, v) => setForm(p => ({...p, [k]: v}))

  const FEATS = [
    { k:'autoLike',         label:'👍 Auto-Like Feed' },
    { k:'autoFollow',       label:'👤 Auto-Follow' },
    { k:'storyInteractions',label:'👁️ Story (Vue + Sondages)' },
    { k:'aiComments',       label:'🤖 Commentaires IA (Groq)' },
    { k:'likTopComments',   label:'💬 Liker Meilleurs Commentaires' },
    { k:'welcomeDm',        label:'💌 Welcome DM Auto' },
  ]

  const submit = async () => {
    setLoading(true); setMsg(null)
    try {
      const res = await fetch('/api/v1/campaigns', { method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          account_id: 'demo_account',
          name: form.name || 'Nouvelle Campagne',
          type: 'EXPERT',
          targets: { competitors: form.targets.split(',').map(t=>t.trim()).filter(Boolean) },
          features: { auto_like: features.autoLike, smart_follow: features.autoFollow,
            story_interactions: features.storyInteractions, ai_comments: features.aiComments,
            like_top_comments: features.likTopComments },
          ai_settings: { lang_filter: [form.langFilter] },
          activity_settings: {}
        })
      })
      const d = await res.json()
      if (res.ok) setMsg({ok:true, txt:`✅ Campagne "${form.name}" lancée !`})
      else setMsg({ok:false, txt:`❌ ${d.detail}`})
    } catch { setMsg({ok:false, txt:'❌ Erreur réseau'}) }
    setLoading(false)
  }

  const activeCount = Object.values(features).filter(Boolean).length

  return (
    <div>
      <div className="page-header fade-up">
        <div>
          <div className="page-title">🎯 Campagnes d'Acquisition IA</div>
          <div className="page-sub">Configurez et lancez vos automatisations intelligentes</div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'2fr 1fr', gap:24}}>
        <div className="card fade-up-2">
          <div className="section-title">Configuration</div>
          {msg && <div className={`alert ${msg.ok?'alert-success':'alert-error'}`}>{msg.txt}</div>}

          <div className="form-group">
            <label className="form-label">Nom de la campagne</label>
            <input className="input" placeholder="Ex: Croissance Marché FR 2026" value={form.name} onChange={e=>f('name',e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Cibles (comptes concurrents ou hashtags)</label>
            <textarea className="input" placeholder="@competitor1, @competitor2, #niche" value={form.targets} onChange={e=>f('targets',e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Filtre de langue</label>
            <select className="select" value={form.langFilter} onChange={e=>f('langFilter',e.target.value)}>
              <option value="fr">🇫🇷 Français</option>
              <option value="mg">🇲🇬 Malgache</option>
              <option value="en">🇬🇧 Anglais</option>
              <option value="">🌍 Toutes langues</option>
            </select>
          </div>

          <div className="form-label" style={{marginBottom:12}}>Modules actifs</div>
          <div className="toggle-grid">
            {FEATS.map(({k, label}) => (
              <div key={k} className={`toggle-card ${features[k]?'on':''}`} onClick={()=>toggleFeat(k)}>
                <span>{label}</span>
                <div className={`toggle-dot ${features[k]?'on':''}`} />
              </div>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="card fade-up-3" style={{height:'fit-content', position:'sticky', top:0}}>
          <div className="section-title">📊 Résumé</div>
          <div style={{display:'flex', flexDirection:'column', gap:14, color:'var(--c-muted2)', fontSize:14}}>
            <div><strong style={{color:'var(--c-text)'}}>Type:</strong> Expert (Automatisé)</div>
            <div><strong style={{color:'var(--c-text)'}}>Cibles:</strong> {form.targets.split(',').filter(x=>x.trim()).length} comptes</div>
            <div><strong style={{color:'var(--c-text)'}}>Modules:</strong> {activeCount} / {FEATS.length} actifs</div>
            <div><strong style={{color:'var(--c-text)'}}>Langue:</strong> {form.langFilter||'Toutes'}</div>
            <div><strong style={{color:'var(--c-text)'}}>Protection:</strong> <span style={{color:'#10b981'}}>🛡️ HumanDelay ON</span></div>
          </div>

          <div style={{height:1, background:'var(--c-border)', margin:'20px 0'}} />

          <button className="btn btn-primary" style={{width:'100%', justifyContent:'center'}} onClick={submit} disabled={loading}>
            {loading ? '⏳ Lancement...' : '🚀 Lancer la Campagne'}
          </button>
        </div>
      </div>
    </div>
  )
}

/* ════════════════════════════ CONTENT PAGE ════════════════════════════ */
function ContentPage() {
  return (
    <div>
      <div className="page-header fade-up">
        <div className="page-title">📅 Contenu & Calendrier</div>
      </div>
      <div className="card fade-up-2" style={{textAlign:'center', padding:'60px', color:'var(--c-muted2)'}}>
        <div style={{fontSize:48, marginBottom:16}}>🚧</div>
        <div style={{fontSize:18, fontWeight:700, color:'var(--c-text)', marginBottom:8}}>Module en Développement</div>
        Programmation de posts, prévisualisation du Grid et génération de captions IA arrivent bientôt.
      </div>
    </div>
  )
}

/* ════════════════════════════ MESSAGES PAGE ════════════════════════════ */
function MessagesPage() {
  return (
    <div>
      <div className="page-header fade-up">
        <div className="page-title">💬 Auto-DM & Inbox</div>
      </div>
      <div className="card fade-up-2" style={{textAlign:'center', padding:'60px', color:'var(--c-muted2)'}}>
        <div style={{fontSize:48, marginBottom:16}}>🚧</div>
        <div style={{fontSize:18, fontWeight:700, color:'var(--c-text)', marginBottom:8}}>Module en Développement</div>
        Système de Welcome DM, réponses automatiques et gestion centralisée de l'inbox arrive bientôt.
      </div>
    </div>
  )
}
