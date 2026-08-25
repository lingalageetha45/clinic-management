import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span>🏥</span> ClinicMS
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end>Dashboard</NavLink>
          {(user?.role === 'admin' || user?.role === 'receptionist') && (
            <>
              <NavLink to="/doctors">Doctors</NavLink>
              <NavLink to="/patients">Patients</NavLink>
            </>
          )}
          <NavLink to="/appointments">Appointments</NavLink>
          {(user?.role === 'admin' || user?.role === 'doctor') && (
            <NavLink to="/prescriptions">Prescriptions</NavLink>
          )}
          <NavLink to="/medical-records">Medical Records</NavLink>
        </nav>
        <div className="sidebar-footer">
          <div style={{ marginBottom: '0.5rem' }}>{user?.full_name}</div>
          <button className="btn btn-secondary btn-sm" onClick={handleLogout} style={{ width: '100%' }}>
            Logout
          </button>
        </div>
      </aside>
      <div className="main-content">
        <header className="topbar">
          <div style={{ fontWeight: 600 }}>Appointment Booking & Clinic Management</div>
          <div className="user-chip">
            <span>{user?.email}</span>
            <span className="role">{user?.role}</span>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
