import { useMemo, useState } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'

const initialItems = [
  {
    id: 1,
    name: 'Midnight Silk Jacket',
    category: 'clothes',
    price: 139.99,
    stock: 14,
    description: 'Tailored statement outerwear for elevated evenings.',
    imageUrl: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 2,
    name: 'Aster Heels',
    category: 'heels',
    price: 89.0,
    stock: 8,
    description: 'All-day silhouette with a luxury heel profile.',
    imageUrl: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 3,
    name: 'Forge Runner',
    category: 'shoes',
    price: 109.5,
    stock: 10,
    description: 'Street-ready comfort with premium build quality.',
    imageUrl: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 4,
    name: 'Nova Chain Set',
    category: 'accessories',
    price: 49.0,
    stock: 20,
    description: 'Sculptural accessory set to finish the look.',
    imageUrl: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=800&q=80',
  },
]

const categoryLabels = {
  clothes: 'Clothes',
  shoes: 'Shoes',
  heels: 'Heels',
  accessories: 'Accessories',
}

function App() {
  const [role, setRole] = useState('user')
  const [user, setUser] = useState(null)
  const [search, setSearch] = useState('')
  const [items, setItems] = useState(initialItems)
  const [cartCount, setCartCount] = useState(0)

  const authenticated = Boolean(user)

  return (
    <Routes>
      <Route
        path="/"
        element={
          <LoginPage
            role={role}
            setRole={setRole}
            onLoginSuccess={(nextUser) => {
              setUser(nextUser)
            }}
            authenticated={authenticated}
          />
        }
      />
      <Route
        path="/dashboard"
        element={
          authenticated ? (
            <DashboardPage
              role={user?.role || role}
              items={items}
              setItems={setItems}
              search={search}
              setSearch={setSearch}
              cartCount={cartCount}
              setCartCount={setCartCount}
              onLogout={() => setUser(null)}
            />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
    </Routes>
  )
}

function LoginPage({ role, setRole, onLoginSuccess, authenticated }) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')

    const payload = { username, password }

    try {
      const response = await fetch(
        role === 'admin'
          ? 'http://127.0.0.1:8000/api/admin/login'
          : 'http://127.0.0.1:8000/api/user/login',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        },
      )

      if (response.ok) {
        const result = await response.json()
        onLoginSuccess({ ...result, role })
        navigate('/dashboard')
        return
      }
    } catch {
      // fallback to local credential validation when backend is offline
    }

    if (role === 'admin' && username === 'admin' && password === 'admin123') {
      onLoginSuccess({ user_id: 1, role: 'admin', message: 'Demo login successful' })
      navigate('/dashboard')
      return
    }

    if (role === 'user' && username === 'user' && password === 'user123') {
      onLoginSuccess({ user_id: 2, role: 'user', message: 'Demo login successful' })
      navigate('/dashboard')
      return
    }

    setError('Invalid credentials. Use the backend account that matches the selected mode.')
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="brand-block">
          <h1>Curato</h1>
          <p>Curated luxury essentials, refined for every mode.</p>
        </div>

        <div className="mode-toggle">
          <button className={role === 'admin' ? 'active' : ''} onClick={() => setRole('admin')}>
            Admin Mode
          </button>
          <button className={role === 'user' ? 'active' : ''} onClick={() => setRole('user')}>
            User Mode
          </button>
        </div>

        <form className="login-form" onSubmit={handleLogin}>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />
          </label>
          {error ? <p className="error-text">{error}</p> : null}
          <button type="submit" className="primary-button">
            Login as {role === 'admin' ? 'Admin' : 'User'}
          </button>
        </form>

        <div className="inline-note">
          Demo admin: <strong>admin / admin123</strong>
          <span className="divider">|</span>
          Demo user: <strong>user / user123</strong>
        </div>
      </div>
    </div>
  )
}

function DashboardPage({ role, items, setItems, search, setSearch, cartCount, setCartCount, onLogout }) {
  const [form, setForm] = useState({
    name: '',
    category: 'clothes',
    price: '',
    stock: '',
    description: '',
    imageUrl: '',
  })

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const q = search.toLowerCase()
      return (
        item.name.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q)
      )
    })
  }, [items, search])

  const handleAddOrUpdate = (event) => {
    event.preventDefault()
    const payload = {
      id: items.length + 1,
      name: form.name,
      category: form.category,
      price: Number(form.price),
      stock: Number(form.stock),
      description: form.description,
      imageUrl: form.imageUrl || 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80',
    }

    setItems((current) => [payload, ...current])
    setForm({ name: '', category: 'clothes', price: '', stock: '', description: '', imageUrl: '' })
  }

  const handleDelete = (itemId) => {
    setItems((current) => current.filter((item) => item.id !== itemId))
  }

  const addToCart = (item) => {
    setCartCount((count) => count + 1)
  }

  return (
    <div className="dashboard-page">
      <header className="top-ribbon">
        <div className="brand-left">Curato</div>
        <div className="top-actions">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search collection"
            className="search-bar"
          />
          <div className="cart-badge">
            <span>🛒</span>
            <em>{cartCount}</em>
          </div>
          <button className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </header>

      <section className="dashboard-grid">
        <aside className="catalog-panel">
          <div className="panel-heading">
            <h2>{role === 'admin' ? 'Admin Inventory' : 'Curato Collection'}</h2>
            <span>{filteredItems.length} items</span>
          </div>

          {role === 'admin' ? (
            <form className="admin-form" onSubmit={handleAddOrUpdate}>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Item name" required />
              <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                <option value="clothes">Clothes</option>
                <option value="shoes">Shoes</option>
                <option value="heels">Heels</option>
                <option value="accessories">Accessories</option>
              </select>
              <input value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} placeholder="Price" type="number" required />
              <input value={form.stock} onChange={(e) => setForm({ ...form, stock: e.target.value })} placeholder="Stock" type="number" required />
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" required />
              <input value={form.imageUrl} onChange={(e) => setForm({ ...form, imageUrl: e.target.value })} placeholder="Image URL" />
              <button type="submit" className="primary-button">Add Item</button>
            </form>
          ) : (
            <div className="catalog-list">
              {filteredItems.map((item) => (
                <article className="catalog-card" key={item.id}>
                  <img src={item.imageUrl} alt={item.name} />
                  <div className="catalog-content">
                    <div className="meta-line">
                      <span>{categoryLabels[item.category]}</span>
                      <strong>${item.price.toFixed(2)}</strong>
                    </div>
                    <h3>{item.name}</h3>
                    <p>{item.description}</p>
                    <button onClick={() => addToCart(item)} className="primary-button">Add to Cart</button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </aside>

        {role === 'admin' ? (
          <section className="admin-content">
            <div className="panel-heading">
              <h2>Current Inventory</h2>
              <span>Manage and update products</span>
            </div>
            <div className="inventory-table">
              {items.map((item) => (
                <div className="inventory-row" key={item.id}>
                  <div>
                    <strong>{item.name}</strong>
                    <small>{categoryLabels[item.category]}</small>
                  </div>
                  <div>
                    <strong>${item.price.toFixed(2)}</strong>
                    <small>Stock: {item.stock}</small>
                  </div>
                  <div className="row-actions">
                    <button className="secondary-button" onClick={() => handleDelete(item.id)}>Remove</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ) : (
          <section className="catalog-results">
            <div className="panel-heading">
              <h2>Featured Collection</h2>
              <span>Premium picks across categories</span>
            </div>
            <div className="catalog-grid">
              {filteredItems.map((item) => (
                <article className="product-card" key={item.id}>
                  <img src={item.imageUrl} alt={item.name} />
                  <div className="product-info">
                    <div className="meta-line">
                      <span>{categoryLabels[item.category]}</span>
                      <strong>${item.price.toFixed(2)}</strong>
                    </div>
                    <h3>{item.name}</h3>
                    <p>{item.description}</p>
                    <button onClick={() => addToCart(item)} className="primary-button">Add to cart</button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
    </div>
  )
}

export default App
