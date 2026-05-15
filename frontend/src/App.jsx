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
  const [posts, setPosts] = useState([
    { id:1, account:'@mon_compte', caption:'✨ Post motivation du lundi !', scheduled:'2026-05-16 09:00', status:'scheduled' },
    { id:2, account:'@mon_compte', caption:'🚀 Découvrez notre nouvelle offre...', scheduled:'2026-05-17 18:00', status:'scheduled' },
    { id:3, account:'@shop_ig',    caption:'🛍️ Promo flash -30% ce weekend !', scheduled:'2026-05-15 12:00', status:'published' },
  ])
  const [form, setForm] = useState({ account:'', caption:'', date:'', time:'' })
  const f = (k,v) => setForm(p=>({...p,[k]:v}))

  const addPost = () => {
    if (!form.caption || !form.date) return
    const newPost = { id: Date.now(), account: form.account||'@mon_compte', caption: form.caption, scheduled: `${form.date} ${form.time||'12:00'}`, status:'scheduled' }
    setPosts(p=>[...p, newPost])
    setForm({ account:'', caption:'', date:'', time:'' })
  }

  return (
    <div>
      <div className="page-header fade-up">
        <div>
          <div className="page-title">📅 Contenu & Calendrier</div>
          <div className="page-sub">Programmez et gérez vos publications sur tous vos comptes</div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:24}}>
        {/* Formulaire de programmation */}
        <div className="card fade-up-2">
          <div className="section-title">📝 Programmer un Post</div>
          <div className="form-group">
            <label className="form-label">Compte</label>
            <input className="input" placeholder="@mon_compte" value={form.account} onChange={e=>f('account',e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Caption / Légende</label>
            <textarea className="input" placeholder="Rédigez votre caption ici...\n\n#hashtag1 #hashtag2" value={form.caption} onChange={e=>f('caption',e.target.value)} />
          </div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}} className="form-group">
            <div>
              <label className="form-label">Date de publication</label>
              <input className="input" type="date" value={form.date} onChange={e=>f('date',e.target.value)} />
            </div>
            <div>
              <label className="form-label">Heure</label>
              <input className="input" type="time" value={form.time} onChange={e=>f('time',e.target.value)} />
            </div>
          </div>
          <div style={{padding:'12px', borderRadius:'10px', background:'rgba(56,189,248,0.08)', border:'1px solid rgba(56,189,248,0.2)', marginBottom:'18px', fontSize:'13px', color:'#7dd3fc'}}>
            💡 Le Celery Beat publiera automatiquement à l'heure programmée via l'API Instagram.
          </div>
          <button className="btn btn-primary" style={{width:'100%', justifyContent:'center'}} onClick={addPost}>
            📅 Ajouter au Calendrier
          </button>
        </div>

        {/* Calendrier / Liste */}
        <div className="card fade-up-3" style={{overflow:'auto', maxHeight:520}}>
          <div className="section-title">🗓️ Posts Programmés ({posts.filter(p=>p.status==='scheduled').length})</div>
          {posts.map(post => (
            <div key={post.id} style={{padding:'14px 16px', borderRadius:'12px', marginBottom:'10px',
              background: post.status==='published' ? 'rgba(16,185,129,0.06)' : 'rgba(255,255,255,0.02)',
              border: `1px solid ${post.status==='published'?'rgba(16,185,129,0.2)':'var(--c-border)'}`}}>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'6px'}}>
                <span style={{fontSize:'13px', fontWeight:600, color:'var(--c-purple2)'}}>{post.account}</span>
                <span className={`status-pill ${post.status==='published'?'status-active':'status-pending'}`}>
                  {post.status==='published' ? '✅ Publié' : `⏰ ${post.scheduled}`}
                </span>
              </div>
              <div style={{fontSize:'13px', color:'var(--c-muted2)', lineHeight:1.5}}>{post.caption}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ════════════════════════════ MESSAGES PAGE ════════════════════════════ */
function MessagesPage() {
  const [welcomeMsg, setWelcomeMsg] = useState('Bonjour {username} ! 👋 Merci de me suivre. Découvrez mes offres exclusives ici 👇')
  const [rules, setRules] = useState([
    { id:1, trigger:'Nouveau follower', action:'Envoyer Welcome DM', active:true },
    { id:2, trigger:'Mot-clé: "prix"', action:'Envoyer tarifs automatiquement', active:false },
    { id:3, trigger:'Story Reply', action:'Répondre via IA (Groq)', active:true },
  ])
  const [saved, setSaved] = useState(false)

  const toggleRule = id => setRules(r => r.map(x => x.id===id ? {...x, active:!x.active} : x))

  const save = () => { setSaved(true); setTimeout(()=>setSaved(false), 2000) }

  return (
    <div>
      <div className="page-header fade-up">
        <div>
          <div className="page-title">💬 Auto-DM & Inbox</div>
          <div className="page-sub">Automatisez vos messages et répondez intelligemment à vos abonnés</div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:24}}>
        {/* Message de bienvenue */}
        <div className="card fade-up-2">
          <div className="section-title">👋 Message de Bienvenue (Welcome DM)</div>
          <div style={{padding:'12px', borderRadius:'10px', background:'rgba(124,58,237,0.08)', border:'1px solid rgba(124,58,237,0.2)', marginBottom:'16px', fontSize:'13px', color:'#a78bfa'}}>
            💡 Variables disponibles : <strong>{'{'+'username'+'}'}</strong>, <strong>{'{'+'followers_count'+'}'}</strong>
          </div>
          <div className="form-group">
            <label className="form-label">Message envoyé aux nouveaux abonnés</label>
            <textarea className="input" rows={5} value={welcomeMsg} onChange={e=>setWelcomeMsg(e.target.value)} />
          </div>
          <div style={{padding:'12px', borderRadius:'10px', background:'rgba(16,185,129,0.06)', border:'1px solid rgba(16,185,129,0.15)', marginBottom:'16px', fontSize:'13px', color:'#6ee7b7'}}>
            <strong>Aperçu :</strong> {welcomeMsg.replace('{username}', '@nouveau_follower')}
          </div>
          <button className="btn btn-primary" style={{width:'100%', justifyContent:'center'}} onClick={save}>
            {saved ? '✅ Sauvegardé !' : '💾 Sauvegarder le Message'}
          </button>
        </div>

        {/* Règles d'automatisation */}
        <div className="card fade-up-3">
          <div className="section-title">⚙️ Règles d'Automatisation</div>
          {rules.map(rule => (
            <div key={rule.id} style={{display:'flex', justifyContent:'space-between', alignItems:'center',
              padding:'16px', borderRadius:'12px', marginBottom:'10px',
              background: rule.active ? 'rgba(124,58,237,0.08)' : 'rgba(255,255,255,0.02)',
              border: `1px solid ${rule.active ? 'rgba(124,58,237,0.25)' : 'var(--c-border)'}`}}>
              <div>
                <div style={{fontSize:'14px', fontWeight:600}}>🔔 {rule.trigger}</div>
                <div style={{fontSize:'12px', color:'var(--c-muted2)', marginTop:'3px'}}>→ {rule.action}</div>
              </div>
              <div className={`toggle-card ${rule.active?'on':''}`} style={{padding:'6px 12px', margin:0}}
                onClick={()=>toggleRule(rule.id)}>
                <div className={`toggle-dot ${rule.active?'on':''}`} />
              </div>
            </div>
          ))}

          <div style={{marginTop:'20px', padding:'16px', borderRadius:'12px',
            background:'rgba(56,189,248,0.06)', border:'1px solid rgba(56,189,248,0.15)'}}>
            <div style={{fontSize:'13px', color:'#7dd3fc', marginBottom:'8px'}}>🤖 Génération de réponses par IA</div>
            <div style={{fontSize:'12px', color:'var(--c-muted2)'}}>Connectez votre clé API Groq dans les variables Railway (GROQ_API_KEY) pour activer les réponses intelligentes.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
