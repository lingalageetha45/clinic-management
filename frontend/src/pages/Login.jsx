import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('admin@clinic.com')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Login failed. Please check your credentials.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-shell">

        <section className="login-brand-panel">
          <div className="brand-icon">+</div>

          <div>
            <span className="brand-label">CLINIC MANAGEMENT</span>
            <h1>Care that is<br />organized.</h1>
          </div>

          <p>
            Manage appointments, doctors, patients and medical records
            from one secure platform.
          </p>

          <div className="login-features">
            <div>
              <span>✓</span>
              Appointment management
            </div>
            <div>
              <span>✓</span>
              Patient records
            </div>
            <div>
              <span>✓</span>
              Prescription management
            </div>
          </div>
        </section>

        <section className="login-form-panel">
          <div className="login-form-content">
            <div className="mobile-brand">
              <div className="brand-icon small">+</div>
              <span>ClinicMS</span>
            </div>

            <div className="login-heading">
              <span className="eyebrow">WELCOME BACK</span>
              <h2>Sign in to your account</h2>
              <p>
                Enter your credentials to access the clinic management
                dashboard.
              </p>
            </div>

            {error && (
              <div className="error-msg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email">Email address</label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <div className="password-label">
                  <label htmlFor="password">Password</label>
                </div>

                <input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <button
                type="submit"
                className="login-submit"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign in'}
                {!loading && <span>→</span>}
              </button>
            </form>

            <div className="login-divider">
              <span>DEMO ACCESS</span>
            </div>

            <div className="demo-access">
              <strong>Administrator account</strong>
              <span>admin@clinic.com</span>
              <span>••••••••</span>
            </div>

            <div className="login-footer">
              <span>Appointment Booking &amp; Clinic Management</span>
              <span>API v1.0.0</span>
            </div>
          </div>
        </section>

      </div>
    </div>
  )
}