import React, { useEffect, useState } from 'react'
import { getDashboard } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')
  const { user } = useAuth()

  useEffect(() => {
    if (user?.role === 'admin' || user?.role === 'receptionist') {
      getDashboard()
        .then((res) => setStats(res.data))
        .catch(() => setError('Could not load dashboard statistics'))
    }
  }, [user])

  if (user?.role === 'doctor') {
    return (
      <div>
        <div className="dashboard-heading">
          <div>
            <span className="dashboard-eyebrow">CLINIC DASHBOARD</span>
            <h1 className="page-title">
              Welcome, Dr. {user.full_name}
            </h1>
            <p className="dashboard-subtitle">
              Manage your appointments and prescriptions from one place.
            </p>
          </div>
        </div>

        <div className="doctor-welcome-card">
          <div className="doctor-welcome-icon">+</div>

          <div>
            <h2>Your workspace is ready</h2>
            <p>
              View your assigned appointments, update appointment status,
              and create prescriptions for your patients.
            </p>

            <div className="doctor-actions">
              <span>Appointments</span>
              <span>Prescriptions</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="dashboard-heading">
        <div>
          <span className="dashboard-eyebrow">OVERVIEW</span>
          <h1 className="page-title">Dashboard</h1>
          <p className="dashboard-subtitle">
            Welcome back. Here's what's happening at your clinic today.
          </p>
        </div>

        <div className="dashboard-date">
          <span>Today</span>
          <strong>
            {new Date().toLocaleDateString('en-IN', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })}
          </strong>
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {stats ? (
        <>
          <div className="stats-grid">
            <div className="stat-card primary">
              <div className="stat-card-top">
                <div className="label">Total Patients</div>
                <div className="stat-icon">P</div>
              </div>
              <div className="value">{stats.total_patients}</div>
              <div className="stat-description">
                Registered patients
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-top">
                <div className="label">Total Doctors</div>
                <div className="stat-icon">D</div>
              </div>
              <div className="value">{stats.total_doctors}</div>
              <div className="stat-description">
                Active doctors
              </div>
            </div>

            <div className="stat-card warning">
              <div className="stat-card-top">
                <div className="label">Today's Appointments</div>
                <div className="stat-icon">A</div>
              </div>
              <div className="value">{stats.todays_appointments}</div>
              <div className="stat-description">
                Scheduled for today
              </div>
            </div>

            <div className="stat-card primary">
              <div className="stat-card-top">
                <div className="label">Upcoming</div>
                <div className="stat-icon">U</div>
              </div>
              <div className="value">{stats.upcoming_appointments}</div>
              <div className="stat-description">
                Future appointments
              </div>
            </div>

            <div className="stat-card success">
              <div className="stat-card-top">
                <div className="label">Completed</div>
                <div className="stat-icon">✓</div>
              </div>
              <div className="value">{stats.completed_appointments}</div>
              <div className="stat-description">
                Completed appointments
              </div>
            </div>

            <div className="stat-card danger">
              <div className="stat-card-top">
                <div className="label">Cancelled</div>
                <div className="stat-icon">×</div>
              </div>
              <div className="value">{stats.cancelled_appointments}</div>
              <div className="stat-description">
                Cancelled appointments
              </div>
            </div>
          </div>

          <div className="dashboard-bottom-grid">
            <div className="card dashboard-insights">
              <div className="card-header">
                <div>
                  <span className="section-eyebrow">PERFORMANCE</span>
                  <h2 className="card-title">Clinic Insights</h2>
                </div>
              </div>

              <div className="insight-row">
                <div className="insight-label">
                  <span className="insight-icon">D</span>
                  <span>Most Visited Doctor</span>
                </div>

                <strong>
                  {stats.most_visited_doctor || 'N/A'}
                </strong>
              </div>

              <div className="insight-row">
                <div className="insight-label">
                  <span className="insight-icon">A</span>
                  <span>Average Daily Appointments</span>
                </div>

                <strong>
                  {stats.average_daily_appointments}
                </strong>
              </div>
            </div>

            <div className="card dashboard-summary">
              <div className="card-header">
                <div>
                  <span className="section-eyebrow">QUICK SUMMARY</span>
                  <h2 className="card-title">Appointment Status</h2>
                </div>
              </div>

              <div className="summary-item">
                <span>
                  <i className="summary-dot scheduled"></i>
                  Upcoming
                </span>
                <strong>{stats.upcoming_appointments}</strong>
              </div>

              <div className="summary-item">
                <span>
                  <i className="summary-dot completed"></i>
                  Completed
                </span>
                <strong>{stats.completed_appointments}</strong>
              </div>

              <div className="summary-item">
                <span>
                  <i className="summary-dot cancelled"></i>
                  Cancelled
                </span>
                <strong>{stats.cancelled_appointments}</strong>
              </div>
            </div>
          </div>
        </>
      ) : (
        !error && (
          <div className="dashboard-loading">
            <div className="loading-spinner"></div>
            <span>Loading dashboard...</span>
          </div>
        )
      )}
    </div>
  )
}