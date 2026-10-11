import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, Navigate, Outlet, Route, Routes, useNavigate, useOutletContext, useParams, useSearchParams } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || '/api' // proxied to the backend by vite.config.js
const BRANDS = ['Adidas', 'H&M', "Levi's", 'Mango', 'Nike', 'Only', 'Puma', 'Uniqlo', 'Vero Moda', 'Zara']
const CATS = ['DRESSES_JUMPSUITS', 'SHOES', 'KNITWEAR', 'SHIRTS', 'ACCESSORIES_JEWELLERY', 'BAGS', 'JACKETS', 'TROUSERS']
const STATES = ['Rajasthan', 'Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Tamil Nadu', 'West Bengal', 'Gujarat', 'Uttar Pradesh']
const CITIES = ['Jaipur', 'Mumbai', 'Pune', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad', 'Lucknow']

// hero photos taken from the product data; the first one that loads is used
const HEROES = [
  'https://static.zara.net/photos///2023/I/0/1/p/9929/327/526/2/w/448/9929327526_1_1_1.jpg?ts=1691758471978',
  'https://static.zara.net/photos///2023/I/0/1/p/2712/468/832/2/w/448/2712468832_1_1_1.jpg?ts=1692776596473',
  'https://static.zara.net/photos///2023/I/0/1/p/6427/117/712/2/w/448/6427117712_1_1_1.jpg?ts=1692869351811',
  'https://static.zara.net/photos///2023/I/0/1/p/3641/815/700/2/w/448/3641815700_1_1_1.jpg?ts=1692865109452',
]

const label = (c = '') => c.replaceAll('_', ' & ').toLowerCase().replace(/(^|\s)\S/g, (m) => m.toUpperCase())
const inr = (n) => (n == null ? '-' : '₹' + Math.round(n).toLocaleString('en-IN'))
const toggle = (arr, v) => (arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v])

// Backend is in testing: by default the app runs fully in the browser (demo mode).
// To connect it later, create frontend/.env with:  VITE_USE_BACKEND=true  (and restart npm run dev)
const USE_BACKEND = import.meta.env.VITE_USE_BACKEND === 'true'

const store = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d } catch { return d } }
const put = (k, v) => localStorage.setItem(k, JSON.stringify(v))
const httpErr = (code) => new Error(String(code))
let BASE = null
const localProducts = async () => {
  if (!BASE) BASE = (await import('./data/products.json')).default
  const o = store('curato_local_products', { added: [], removed: [] })
  return [...o.added, ...BASE.filter((p) => !o.removed.includes(p.id))]
}

async function mock(path, opts = {}) {
  const method = opts.method || 'GET'
  const body = opts.body ? JSON.parse(opts.body) : null
  const [pth, qs] = path.split('?')
  const params = new URLSearchParams(qs || '')
  let m
  if (pth === '/products' && method === 'GET') {
    const all = await localProducts(), skip = +params.get('skip') || 0, limit = +params.get('limit') || 20
    return all.slice(skip, skip + limit)
  }
  if (pth === '/products' && method === 'POST') {
    const all = await localProducts(), o = store('curato_local_products', { added: [], removed: [] })
    const p = { id: Math.max(0, ...all.map((x) => x.id)) + 1, ...body }
    o.added.unshift(p); put('curato_local_products', o); return p
  }
  if ((m = pth.match(/^\/products\/(\d+)$/))) {
    const id = +m[1]
    if (method === 'GET') { const p = (await localProducts()).find((x) => x.id === id); if (!p) throw httpErr(404); return p }
    if (method === 'DELETE') {
      const o = store('curato_local_products', { added: [], removed: [] })
      o.added = o.added.filter((x) => x.id !== id); o.removed.push(id); put('curato_local_products', o); return { ok: true }
    }
  }
  const profiles = store('curato_local_profiles', {})
  if ((m = pth.match(/^\/user-profiles\/user\/(\d+)$/))) { if (!profiles[m[1]]) throw httpErr(404); return profiles[m[1]] }
  if (pth === '/user-profiles' && method === 'POST') { const pr = { id: body.user_id, ...body }; profiles[body.user_id] = pr; put('curato_local_profiles', profiles); return pr }
  if ((m = pth.match(/^\/user-profiles\/(\d+)$/)) && method === 'PATCH') {
    const pr = { ...profiles[m[1]], ...body }; profiles[m[1]] = pr; put('curato_local_profiles', profiles); return pr
  }
  if (pth === '/interactions' && method === 'POST') {
    const ev = store('curato_local_events', []); ev.push({ event_id: ev.length + 1, ...body }); put('curato_local_events', ev.slice(-5000)); return ev[ev.length - 1]
  }
  throw httpErr(404)
}

async function api(path, opts = {}) {
  if (!USE_BACKEND) return mock(path, opts)
  const r = await fetch(API + path, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!r.ok) { const e = new Error(r.status); e.detail = (await r.json().catch(() => ({}))).detail; throw e }
  const t = await r.text()
  return t ? JSON.parse(t) : null
}

// demo accounts: kept until the real backend login exists
const DEMO = { admin: { p: 'admin123', id: 1, role: 'admin' }, user: { p: 'user123', id: 20000, role: 'user' } }

const sha = async (t) =>
  Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)))).map((b) => b.toString(16).padStart(2, '0')).join('')
const accounts = () => { try { return JSON.parse(localStorage.getItem('curato_accounts')) || {} } catch { return {} } }

// subcategories with no photo of their own borrow a cover from a related one
const COVER_FROM = {
  Tops: ['Shirts', 'Knitwear', 'Basics'], Skirts: ['Dresses'], 'Shorts & Skorts': ['Trousers', 'Jeans'],
  'Co-ord Sets': ['Blazers', 'Trousers'], Jeans: ['Trousers'], Trousers: ['Jeans'], Beauty: ['Perfume'], Basics: ['Shirts'],
}
const spread = (arr, n) => (arr.length <= n ? arr : Array.from({ length: n }, (_, i) => arr[Math.floor((i * arr.length) / n)]))
// each subcategory gets a list of candidate photos; the first one that loads is shown
const makeCovers = (all) => {
  const own = new Map()
  all.forEach((p) => {
    if (!p.subcategory || !p.image_url) return
    if (!own.has(p.subcategory)) own.set(p.subcategory, [])
    own.get(p.subcategory).push(p.image_url)
  })
  const anyImg = spread([...own.values()].flat(), 12)
  const covers = new Map()
  all.forEach((p) => {
    const sub = p.subcategory
    if (!sub || covers.has(sub)) return
    const related = (COVER_FROM[sub] || []).flatMap((x) => spread(own.get(x) || [], 6))
    covers.set(sub, [...new Set([...spread(own.get(sub) || [], 12), ...related, ...anyImg])])
  })
  return covers
}

let CACHE = null
const loadAll = async () => {
  if (CACHE) return CACHE
  const pages = await Promise.all(Array.from({ length: 24 }, (_, i) => api(`/products?skip=${i * 100}&limit=100`)))
  CACHE = pages.flat()
  return CACHE
}

const load = () => {
  try { return JSON.parse(localStorage.getItem('curato')) } catch { return null }
}

export default function App() {
  const [s, setS] = useState(load)
  const save = (v) => {
    setS(v)
    if (v) localStorage.setItem('curato', JSON.stringify(v))
    else localStorage.removeItem('curato')
  }
  const admin = s?.user.role === 'admin'
  return (
    <Routes>
      <Route path="/login" element={<Login onAuth={save} />} />
      <Route path="/admin" element={admin ? <Admin s={s} onLogout={() => save(null)} /> : <Navigate to="/login" replace />} />
      <Route path="/onboarding" element={s && !admin ? <Onboarding s={s} save={save} /> : <Navigate to="/login" replace />} />
      <Route element={!s ? <Navigate to="/login" replace /> : admin ? <Navigate to="/admin" replace /> : !s.profile ? <Navigate to="/onboarding" replace /> : <Shell s={s} onLogout={() => save(null)} />}>
        <Route path="/" element={<Home />} />
        <Route path="/browse" element={<Listing />} />
        <Route path="/product/:id" element={<Detail />} />
        <Route path="/cart" element={<CartPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function Eye({ open }) {
  return (
    <svg className={'eye' + (open ? ' open' : '')} viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" />
      <circle className="pupil" cx="12" cy="12" r="3" />
      <path className="slash" d="M4 4l16 16" />
    </svg>
  )
}

function Login({ onAuth }) {
  const nav = useNavigate()
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const signup = mode === 'signup'

  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setError('')
    try {
      const name = username.trim().toLowerCase()
      const demo = !signup && DEMO[name]?.p === password ? DEMO[name] : null
      let user
      if (demo) user = { user_id: demo.id, username: name, role: demo.role }
      else {
        const db = accounts()
        const hash = await sha(password)
        if (signup) {
          if (db[name] || DEMO[name]) throw new Error('Username already taken')
          db[name] = { hash, user_id: 10001 + Object.keys(db).length }
          localStorage.setItem('curato_accounts', JSON.stringify(db))
        } else if (db[name]?.hash !== hash) throw new Error('Invalid username or password')
        user = { user_id: db[name].user_id, username: name, role: 'user' }
      }
      if (user.role === 'admin') { onAuth({ user, profile: null }); nav('/admin'); return }
      let profile = null
      if (!signup) { try { profile = await api(`/user-profiles/user/${user.user_id}`) } catch { /* new user */ } }
      onAuth({ user, profile })
      nav(profile ? '/' : '/onboarding')
    } catch (err) {
      setError(err.message)
    }
    setBusy(false)
  }

  const [hi, setHi] = useState(0)
  const [big, setBig] = useState(true)
  const [noPhoto, setNoPhoto] = useState(false)
  const photoFail = () => {
    if (big) setBig(false)
    else if (hi < HEROES.length - 1) { setHi(hi + 1); setBig(true) }
    else setNoPhoto(true)
  }
  const swap = () => { setMode(signup ? 'login' : 'signup'); setError('') }

  return (
    <div className="ed">
      <div className="ed-frame">
        <h1 className="ed-title" aria-label="Curato">CURATO</h1>
        {!noPhoto && <img className="ed-photo" key={hi + '-' + big} src={big ? HEROES[hi].replace('/w/448/', '/w/1024/') : HEROES[hi]} alt="" referrerPolicy="no-referrer" onError={photoFail} />}
        <p className="ed-tag">MADE FOR YOU.<br />BY YOU.</p>
        <form className="ed-form" onSubmit={submit}>
          <h2>{signup ? 'CREATE YOUR PERSONALIZED WARDROBE' : 'WELCOME BACK'}</h2>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" autoComplete="off" required minLength={3} />
          <div className="pw">
            <input type={show ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" autoComplete="off" required minLength={6} />
            <button type="button" className="eye-btn" onClick={() => setShow(!show)} aria-label="Toggle password"><Eye open={show} /></button>
          </div>
          {error && <p className="err">{error}</p>}
          <button className="ed-btn" type="submit" disabled={busy}>{busy ? 'PLEASE WAIT' : signup ? 'SIGN UP' : 'LOG IN'}</button>
          <p className="ed-alt">{signup ? 'Already have an account?' : 'New here?'} <button type="button" onClick={swap}>{signup ? 'Log in' : 'Create account'}</button></p>
          <p className="ed-demo">Demo: user / user123 · admin / admin123{!USE_BACKEND && ' · saved in this browser only'}</p>
        </form>
      </div>
    </div>
  )
}

function Chips({ options, value, onChange, fmt = (x) => x }) {
  return (
    <div className="chips">
      {options.map((o) => (
        <button type="button" key={o} className={'chip' + (value.includes(o) ? ' on' : '')} onClick={() => onChange(toggle(value, o))}>{fmt(o)}</button>
      ))}
    </div>
  )
}

function Onboarding({ s, save }) {
  const nav = useNavigate()
  const [step, setStep] = useState(0)
  const [f, setF] = useState({ age: '', gender: '', country: 'India', state: '', city: '', min: 500, max: 10000, rating: 3.5, cats: [], brands: [] })
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const set = (k, v) => setF((x) => ({ ...x, [k]: v }))
  const ok0 = f.age >= 18 && f.age <= 100 && f.gender && f.country.trim() && f.state.trim() && f.city.trim()
  const ok1 = f.cats.length > 0 && +f.min <= +f.max

  const submit = async () => {
    setBusy(true); setErr('')
    const uid = s.user.user_id
    const body = {
      age: +f.age, gender: f.gender, city: f.city.trim(), state: f.state.trim(), country: f.country.trim(),
      preferred_min_price: +f.min, preferred_max_price: +f.max, preferred_categories: f.cats.join('|'),
      preferred_rating: +f.rating, preferred_brands: f.brands.join('|') || null,
    }
    try {
      let existing = null
      try { existing = await api(`/user-profiles/user/${uid}`) } catch { /* new user */ }
      const profile = existing
        ? await api(`/user-profiles/${existing.id}`, { method: 'PATCH', body: JSON.stringify(body) })
        : await api('/user-profiles', { method: 'POST', body: JSON.stringify({ user_id: uid, ...body }) })
      save({ ...s, profile })
      nav('/')
    } catch (e) {
      const why = e.detail ? (typeof e.detail === 'string' ? e.detail : JSON.stringify(e.detail).slice(0, 200)) : ''
      setErr(`Could not save your profile (${e.message}${why ? ': ' + why : ''}). Check that the backend is running and the dev server was restarted.`)
    }
    setBusy(false)
  }

  return (
    <div className="auth center">
      <div className="blob b1" /><div className="blob b2" />
      <div className="glow wide">
        <div className="in">
          <div className="bar"><i style={{ width: step ? '100%' : '50%' }} /></div>
          <h2>{step ? 'Your taste' : 'Tell us about you'}</h2>
          <p className="muted">{step ? 'We use this to tune what you see first.' : 'Your demographics help us find shoppers like you.'}</p>
          {step === 0 ? (
            <div className="fields fade" key="a">
              <div className="two">
                <label>Age<input type="number" min="18" max="100" value={f.age} onChange={(e) => set('age', e.target.value)} placeholder="18-100" /></label>
                <label>Gender
                  <div className="chips">
                    {['Women', 'Men', 'Other'].map((g) => (
                      <button type="button" key={g} className={'chip' + (f.gender === g ? ' on' : '')} onClick={() => set('gender', g)}>{g}</button>
                    ))}
                  </div>
                </label>
              </div>
              <label>Country<input value={f.country} onChange={(e) => set('country', e.target.value)} /></label>
              <div className="two">
                <label>State<input list="states" value={f.state} onChange={(e) => set('state', e.target.value)} placeholder="State" /></label>
                <label>City<input list="cities" value={f.city} onChange={(e) => set('city', e.target.value)} placeholder="City" /></label>
              </div>
              <datalist id="states">{STATES.map((x) => <option key={x} value={x} />)}</datalist>
              <datalist id="cities">{CITIES.map((x) => <option key={x} value={x} />)}</datalist>
            </div>
          ) : (
            <div className="fields fade" key="b">
              <label>Favourite categories<Chips options={CATS} value={f.cats} onChange={(v) => set('cats', v)} fmt={label} /></label>
              <label>Favourite brands<Chips options={BRANDS} value={f.brands} onChange={(v) => set('brands', v)} /></label>
              <div className="two">
                <label>Min budget (₹)<input type="number" min="0" value={f.min} onChange={(e) => set('min', e.target.value)} /></label>
                <label>Max budget (₹)<input type="number" min="0" value={f.max} onChange={(e) => set('max', e.target.value)} /></label>
              </div>
              <label>Minimum rating: {f.rating}<input type="range" min="1" max="5" step="0.5" value={f.rating} onChange={(e) => set('rating', e.target.value)} /></label>
            </div>
          )}
          {err && <p className="err">{err}</p>}
          <div className="row">
            {step > 0 && <button className="btn ghost" onClick={() => { setErr(''); setStep(0) }}>Back</button>}
            {step === 0
              ? <button className="btn" disabled={!ok0} onClick={() => { setErr(''); setStep(1) }}>Continue</button>
              : <button className="btn" disabled={!ok1 || busy} onClick={submit}>{busy ? 'Saving...' : 'Start exploring'}</button>}
          </div>
        </div>
      </div>
    </div>
  )
}

function Shell({ s, onLogout }) {
  const nav = useNavigate()
  const uid = s.user.user_id
  const key = 'curato_cart_' + uid
  const [cart, setCart] = useState(() => { try { return JSON.parse(localStorage.getItem(key)) || [] } catch { return [] } })
  const [col, setCol] = useState(false)
  const [q, setQ] = useState('')
  const [toast, setToast] = useState('')
  const [all, setAll] = useState(null)
  useEffect(() => { loadAll().then(setAll).catch(() => setAll('error')) }, [])
  const covers = useMemo(() => (Array.isArray(all) ? makeCovers(all) : new Map()), [all])
  const sid = useRef('web-' + Math.random().toString(36).slice(2, 10))
  useEffect(() => localStorage.setItem(key, JSON.stringify(cart)), [cart])

  const say = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }
  const log = (p, type, source = 'homepage', quantity = 1) =>
    api('/interactions', { method: 'POST', body: JSON.stringify({
      user_id: uid, product_id: p.id, event_type: type, session_id: sid.current, time_spent_seconds: 0,
      scroll_depth: 0, source, quantity, timestamp: new Date().toISOString().slice(0, 19) }) }).catch(() => {})
  const add = (p, qty = 1) => {
    setCart((c) => c.some((x) => x.id === p.id) ? c.map((x) => x.id === p.id ? { ...x, qty: x.qty + qty } : x)
      : [...c, { id: p.id, product_name: p.product_name, brand: p.brand, price: p.price, original_price: p.original_price, image_url: p.image_url, subcategory: p.subcategory, qty }])
    say('Added to cart'); log(p, 'add_to_cart', 'product_page', qty)
  }
  const setQty = (id, qty) => setCart((c) => qty < 1 ? c.filter((x) => x.id !== id) : c.map((x) => x.id === id ? { ...x, qty } : x))
  const count = cart.reduce((a, x) => a + x.qty, 0)
  const search = (e) => { e.preventDefault(); if (q.trim()) nav('/browse?q=' + encodeURIComponent(q.trim())) }

  return (
    <div className="app">
      <aside className={'side' + (col ? ' col' : '')}>
        <div className="logo"><span>C</span><b>Curato</b></div>
        <button className="collapse" onClick={() => setCol(!col)}>{col ? '›' : '‹'}</button>
        <nav>
          <Link to="/"><i>◈</i><span>Shop</span></Link>
          <Link to="/cart"><i>🛍</i><span>Cart ({count})</span></Link>
        </nav>
        <div className="me">
          <div className="av">{s.user.username[0].toUpperCase()}</div>
          <div><b>{s.user.username}</b><small>{s.profile.city}, {s.profile.state}</small></div>
          <button onClick={onLogout} title="Log out">⏻</button>
        </div>
      </aside>
      <main className="main">
        <header className="top">
          <form className="tools grow" onSubmit={search}>
            <input className="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search products, brands..." />
            <button className="btn">Search</button>
          </form>
          <Link to="/cart" className="cartb" key={count}>Cart <em>{count}</em></Link>
        </header>
        <Outlet context={{ s, cart, add, setQty, log, say, setCart, all, covers }} />
      </main>
      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}

function Img({ p, cover = [] }) {
  const srcs = [p.image_url, ...cover].filter(Boolean)
  const [i, setI] = useState(0)
  if (i >= srcs.length) return <span className="mono">{(p.brand || p.subcategory || 'C')[0]}</span>
  const borrowed = !(i === 0 && p.image_url) && !!p.product_name
  return (
    <>
      <img key={srcs[i]} className={borrowed ? 'borrowed' : ''} src={srcs[i]} alt={borrowed ? '' : p.product_name || p.subcategory} loading="lazy" referrerPolicy="no-referrer" onError={() => setI(i + 1)} />
      {borrowed && <span className="soon">Photo coming soon</span>}
    </>
  )
}

function Home() {
  const { s, all, covers } = useOutletContext()
  const subs = useMemo(() => {
    if (!Array.isArray(all)) return null
    const m = new Map()
    all.forEach((p) => {
      if (!p.subcategory) return
      const e = m.get(p.subcategory) || { subcategory: p.subcategory, category: p.category, count: 0, image_url: null }
      e.count++; e.image_url ||= p.image_url
      m.set(p.subcategory, e)
    })
    return [...m.values()].sort((a, b) => b.count - a.count)
  }, [all])
  const err = all === 'error' ? 'Cannot reach the backend. Start it and refresh.' : ''
  const pref = (s.profile.preferred_categories || '').split('|')
  const list = subs && [...subs].sort((a, b) => pref.includes(b.category) - pref.includes(a.category))
  return (
    <div className="page">
      <h1 className="title">Shop by category</h1>
      <p className="muted">Hi {s.user.username}, pick a category to start. Your favourites come first.</p>
      {err && <p className="err">{err}</p>}
      <section className="tiles">
        {(list || Array.from({ length: 8 })).map((x, i) => x ? (
          <Link to={'/browse?sub=' + encodeURIComponent(x.subcategory)} className="tile" key={x.subcategory} style={{ '--i': i }}>
            <div className="ph"><Img p={{ subcategory: x.subcategory }} cover={covers.get(x.subcategory)} />{pref.includes(x.category) && <b className="badge">For you</b>}</div>
            <div className="cb"><h3>{x.subcategory}</h3><small>{x.count} products</small></div>
          </Link>
        ) : <div className="tile sk" key={i} />)}
      </section>
    </div>
  )
}

function Listing() {
  const { add, all, covers } = useOutletContext()
  const nav = useNavigate()
  const [sp] = useSearchParams()
  const sub = sp.get('sub') || '', q = sp.get('q') || ''
  const [n, setN] = useState(40)
  useEffect(() => setN(40), [sub, q])
  const found = useMemo(() => {
    if (!Array.isArray(all)) return null
    const t = q.toLowerCase()
    return all.filter((p) => (!sub || p.subcategory === sub) && (!t || `${p.product_name} ${p.brand} ${p.category} ${p.subcategory}`.toLowerCase().includes(t)))
  }, [all, sub, q])
  const items = found ? found.slice(0, n) : []
  const loading = found === null && all !== 'error'
  return (
    <div className="page">
      <Link to="/" className="back">← All categories</Link>
      <h1 className="title">{q ? `Results for "${q}"` : sub}{q && sub ? ` in ${sub}` : ''}</h1>
      {all === 'error' && <p className="err">Cannot reach the backend. Start it and refresh.</p>}
      <section className="grid flush">
        {items.map((p, i) => (
          <article className="card" key={p.id} style={{ '--i': Math.min(i, 12) }} onClick={() => nav('/product/' + p.id)}>
            <div className="ph"><Img p={p} cover={covers.get(p.subcategory)} />{p.discount > 0 && <b className="badge">-{Math.round(p.discount)}%</b>}</div>
            <div className="cb">
              <small>{p.brand}</small><h3>{p.product_name}</h3>
              <div className="pr"><strong>{inr(p.price)}</strong>{p.original_price > p.price && <s>{inr(p.original_price)}</s>}{p.rating > 0 && <em>★ {p.rating.toFixed(1)}</em>}</div>
              <button className="btn" onClick={(e) => { e.stopPropagation(); add(p) }}>Add to cart</button>
            </div>
          </article>
        ))}
        {loading && Array.from({ length: 8 }).map((_, i) => <div className="card sk" key={i} />)}
      </section>
      {found && found.length === 0 && <p className="muted empty">No products found.</p>}
      {found && n < found.length && <button className="btn ghost loadmore" onClick={() => setN(n + 40)}>Load more</button>}
    </div>
  )
}

function Detail() {
  const { id } = useParams()
  const { add, log, all, covers } = useOutletContext()
  const [p, setP] = useState(null)
  const [qty, setQty] = useState(1)
  const [err, setErr] = useState('')
  useEffect(() => {
    const hit = Array.isArray(all) && all.find((x) => String(x.id) === id)
    if (hit) { setP(hit); log(hit, 'view', 'product_page'); return }
    api('/products/' + id).then((d) => { setP(d); log(d, 'view', 'product_page') }).catch(() => setErr('Product not found.'))
  }, [id])
  if (err) return <div className="page"><p className="err">{err}</p><Link to="/" className="back">← Back to shop</Link></div>
  if (!p) return <div className="page"><div className="card sk wide" /></div>
  const rows = [['Category', p.category], ['Type', p.subcategory], ['Color', p.color], ['Material', p.material], ['Style', p.style], ['Occasion', p.occasion], ['Fit', p.fit], ['Season', p.season], ['Availability', p.availability]].filter((r) => r[1])
  return (
    <div className="page">
      <Link to={'/browse?sub=' + encodeURIComponent(p.subcategory || '')} className="back">← Back to {p.subcategory || 'shop'}</Link>
      <section className="detail">
        <div className="ph big"><Img key={p.id} p={p} cover={covers.get(p.subcategory)} />{p.discount > 0 && <b className="badge">-{Math.round(p.discount)}%</b>}</div>
        <div className="info">
          <small>{p.brand}</small>
          <h1>{p.product_name}</h1>
          <div className="pr big"><strong>{inr(p.price)}</strong>{p.original_price > p.price && <s>{inr(p.original_price)}</s>}{p.rating > 0 && <em>★ {p.rating.toFixed(1)}</em>}</div>
          <p className="desc">{p.description || 'No description available.'}</p>
          <table className="specs"><tbody>{rows.map(([k, v]) => <tr key={k}><th>{k}</th><td>{v}</td></tr>)}</tbody></table>
          <div className="row left">
            <div className="qty"><button onClick={() => setQty(Math.max(1, qty - 1))}>−</button><span>{qty}</span><button onClick={() => setQty(qty + 1)}>+</button></div>
            <button className="btn" onClick={() => add(p, qty)}>Add to cart</button>
          </div>
        </div>
      </section>
    </div>
  )
}

function CartPage() {
  const { cart, setQty, setCart, log, covers } = useOutletContext()
  const [done, setDone] = useState(false)
  const total = cart.reduce((a, x) => a + (x.price || 0) * x.qty, 0)
  const order = () => { cart.forEach((x) => log(x, 'purchase', 'product_page', x.qty)); setCart([]); setDone(true) }
  if (done) return <div className="page center-msg"><h1 className="title">Order placed ✓</h1><p className="muted">Thank you for shopping with Curato.</p><Link className="btn" to="/">Continue shopping</Link></div>
  return (
    <div className="page">
      <h1 className="title">Your cart</h1>
      {cart.length === 0 ? <div className="center-msg"><p className="muted">Your cart is empty.</p><Link className="btn" to="/">Start shopping</Link></div> : (
        <div className="cartwrap">
          <div className="items">
            {cart.map((x) => (
              <div className="citem" key={x.id}>
                <Link to={'/product/' + x.id} className="ph sm"><Img p={x} cover={covers.get(x.subcategory)} /></Link>
                <div className="grow"><small>{x.brand}</small><h3>{x.product_name}</h3><strong>{inr(x.price)}</strong></div>
                <div className="qty"><button onClick={() => setQty(x.id, x.qty - 1)}>−</button><span>{x.qty}</span><button onClick={() => setQty(x.id, x.qty + 1)}>+</button></div>
                <b className="line">{inr((x.price || 0) * x.qty)}</b>
                <button className="x" onClick={() => setQty(x.id, 0)} title="Remove">✕</button>
              </div>
            ))}
          </div>
          <aside className="summary">
            <h3>Order summary</h3>
            <div className="sumrow"><span>Items</span><b>{cart.reduce((a, x) => a + x.qty, 0)}</b></div>
            <div className="sumrow total"><span>Total</span><b>{inr(total)}</b></div>
            <button className="btn" onClick={order}>Place order</button>
          </aside>
        </div>
      )}
    </div>
  )
}

function Admin({ s, onLogout }) {
  const blank = { product_name: '', category: CATS[0], subcategory: '', brand: BRANDS[0], price: '', original_price: '', image_url: '', description: '' }
  const [items, setItems] = useState(null)
  const [q, setQ] = useState('')
  const [n, setN] = useState(50)
  const [adding, setAdding] = useState(false)
  const [nf, setNf] = useState(blank)
  const [toast, setToast] = useState('')
  useEffect(() => { loadAll().then((d) => setItems([...d])).catch(() => setItems('error')) }, [])
  const say = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }
  const sync = (list) => { CACHE = list; setItems(list) }
  const list = Array.isArray(items) ? items.filter((p) => !q || `${p.product_name} ${p.brand} ${p.subcategory}`.toLowerCase().includes(q.toLowerCase())) : []
  const subs = Array.isArray(items) ? [...new Set(items.map((p) => p.subcategory).filter(Boolean))] : []

  const remove = async (p) => {
    if (!window.confirm(`Remove "${p.product_name}"?`)) return
    try {
      await api(`/products/${p.id}`, { method: 'DELETE' })
      sync(items.filter((x) => x.id !== p.id)); say('Product removed')
    } catch { say('Could not remove product') }
  }
  const create = async (e) => {
    e.preventDefault()
    const price = +nf.price, orig = nf.original_price ? +nf.original_price : null
    const body = {
      product_name: nf.product_name.trim(), category: nf.category, subcategory: nf.subcategory.trim() || null, brand: nf.brand,
      gender: 'Women', price, original_price: orig, discount: orig && orig > price ? Math.round((1 - price / orig) * 100) : null,
      image_url: nf.image_url.trim() || null, description: nf.description.trim() || null,
    }
    try {
      const p = await api('/products', { method: 'POST', body: JSON.stringify(body) })
      sync([p, ...items]); setAdding(false); setNf(blank); say('Product added')
    } catch { say('Could not add product. Check the fields and the backend.') }
  }

  return (
    <div className="app">
      <aside className="side">
        <div className="logo"><span>C</span><b>Curato</b></div>
        <nav>
          <a className="on"><i>▤</i><span>Inventory</span></a>
          <a onClick={() => setAdding(true)} style={{ cursor: 'pointer' }}><i>＋</i><span>Add product</span></a>
        </nav>
        <div className="me">
          <div className="av">A</div>
          <div><b>{s.user.username}</b><small>Administrator</small></div>
          <button onClick={onLogout} title="Log out">⏻</button>
        </div>
      </aside>
      <main className="main">
        <header className="top">
          <div className="tools grow">
            <input className="search" value={q} onChange={(e) => { setQ(e.target.value); setN(50) }} placeholder="Search inventory..." />
          </div>
          <button className="btn" onClick={() => setAdding(true)}>+ Add product</button>
        </header>
        <div className="page">
          <h1 className="title">Inventory</h1>
          <p className="muted">{Array.isArray(items) ? `${list.length} of ${items.length} products` : items === 'error' ? 'Cannot reach the backend. Start it and refresh.' : 'Loading...'}</p>
          <div className="items" style={{ marginTop: 20 }}>
            {list.slice(0, n).map((p) => (
              <div className="citem" key={p.id}>
                <div className="ph sm"><Img p={p} /></div>
                <div className="grow"><small>{p.brand} · {p.subcategory || p.category}</small><h3>{p.product_name}</h3></div>
                <strong className="line">{inr(p.price)}</strong>
                <button className="btn ghost" onClick={() => remove(p)}>Remove</button>
              </div>
            ))}
          </div>
          {n < list.length && <button className="btn ghost loadmore" onClick={() => setN(n + 50)}>Load more</button>}
        </div>
      </main>
      {adding && (
        <div className="modal" onClick={() => setAdding(false)}>
          <form className="sheet form" onClick={(e) => e.stopPropagation()} onSubmit={create}>
            <h2>Add product</h2>
            <input required placeholder="Product name" value={nf.product_name} onChange={(e) => setNf({ ...nf, product_name: e.target.value })} />
            <div className="two">
              <select value={nf.category} onChange={(e) => setNf({ ...nf, category: e.target.value })}>{CATS.map((c) => <option key={c} value={c}>{label(c)}</option>)}</select>
              <select value={nf.brand} onChange={(e) => setNf({ ...nf, brand: e.target.value })}>{BRANDS.map((b) => <option key={b}>{b}</option>)}</select>
            </div>
            <input list="subs" placeholder="Subcategory (e.g. Dresses)" value={nf.subcategory} onChange={(e) => setNf({ ...nf, subcategory: e.target.value })} />
            <datalist id="subs">{subs.map((x) => <option key={x} value={x} />)}</datalist>
            <div className="two">
              <input required type="number" min="0" placeholder="Price (₹)" value={nf.price} onChange={(e) => setNf({ ...nf, price: e.target.value })} />
              <input type="number" min="0" placeholder="Original price (₹)" value={nf.original_price} onChange={(e) => setNf({ ...nf, original_price: e.target.value })} />
            </div>
            <input placeholder="Image URL" value={nf.image_url} onChange={(e) => setNf({ ...nf, image_url: e.target.value })} />
            <textarea placeholder="Description" value={nf.description} onChange={(e) => setNf({ ...nf, description: e.target.value })} />
            <div className="row"><button type="button" className="btn ghost" onClick={() => setAdding(false)}>Cancel</button><button className="btn">Save product</button></div>
          </form>
        </div>
      )}
      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}
