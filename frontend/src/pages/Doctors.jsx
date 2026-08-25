import React, { useEffect, useState } from 'react'
import {
  getDoctors,
  createDoctor,
  updateDoctor,
  deleteDoctor,
} from '../services/api'
import { useAuth } from '../context/AuthContext'

const emptyForm = {
  full_name: '',
  specialization: '',
  qualification: '',
  phone_number: '',
  email: '',
  consultation_fee: 0,
  available_timings: '',
}

export default function Doctors() {
  const [doctors, setDoctors] = useState([])
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const load = () => {
    setError('')

    getDoctors({ search: search || undefined })
      .then((res) => setDoctors(res.data))
      .catch(() => setError('Failed to load doctors'))
  }

  useEffect(() => {
    load()
  }, [])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setError('')
    setShowModal(true)
  }

  const openEdit = (doctor) => {
    setEditing(doctor)

    setForm({
      full_name: doctor.full_name,
      specialization: doctor.specialization,
      qualification: doctor.qualification,
      phone_number: doctor.phone_number,
      email: doctor.email,
      consultation_fee: doctor.consultation_fee,
      available_timings: doctor.available_timings || '',
    })

    setError('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (editing) {
        await updateDoctor(editing.id, form)
      } else {
        await createDoctor(form)
      }

      setShowModal(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Deactivate this doctor?')) return

    try {
      await deleteDoctor(id)
      load()
    } catch {
      setError('Delete failed')
    }
  }

  return (
    <div>
      <h1 className="page-title">Doctors</h1>

      {error && !showModal && (
        <div className="error-msg">
          {error}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div className="search-bar">
            <input
              placeholder="Search name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') load()
              }}
            />

            <button
              className="btn btn-secondary"
              onClick={load}
            >
              Search
            </button>
          </div>

          {isAdmin && (
            <button
              className="btn btn-primary"
              onClick={openCreate}
            >
              + Add Doctor
            </button>
          )}
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Specialization</th>
                <th>Qualification</th>
                <th>Phone</th>
                <th>Fee</th>
                <th>Timings</th>

                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>

            <tbody>
              {doctors.length === 0 ? (
                <tr>
                  <td
                    colSpan={isAdmin ? 7 : 6}
                    className="empty-state"
                  >
                    No doctors found
                  </td>
                </tr>
              ) : (
                doctors.map((doctor) => (
                  <tr key={doctor.id}>
                    <td>{doctor.full_name}</td>

                    <td>{doctor.specialization}</td>

                    <td>{doctor.qualification}</td>

                    <td>{doctor.phone_number}</td>

                    <td>
                      ₹{doctor.consultation_fee}
                    </td>

                    <td>
                      {doctor.available_timings || '—'}
                    </td>

                    {isAdmin && (
                      <td>
                        <div className="btn-group">
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => openEdit(doctor)}
                          >
                            Edit
                          </button>

                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleDelete(doctor.id)}
                          >
                            Remove
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowModal(false)}
        >
          <div
            className="modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>
              {editing ? 'Edit Doctor' : 'Add Doctor'}
            </h2>

            {error && (
              <div className="error-msg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-grid">

                <div className="form-group">
                  <label>Full Name</label>

                  <input
                    required
                    value={form.full_name}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        full_name: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Specialization</label>

                  <input
                    required
                    value={form.specialization}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        specialization: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Qualification</label>

                  <input
                    required
                    value={form.qualification}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        qualification: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Phone</label>

                  <input
                    required
                    value={form.phone_number}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        phone_number: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>

                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        email: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Consultation Fee</label>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={form.consultation_fee}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        consultation_fee:
                          parseFloat(e.target.value) || 0,
                      })
                    }
                  />
                </div>

                <div
                  className="form-group"
                  style={{ gridColumn: '1 / -1' }}
                >
                  <label>Available Timings</label>

                  <input
                    placeholder="Mon-Fri 09:00-17:00"
                    value={form.available_timings}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        available_timings: e.target.value,
                      })
                    }
                  />
                </div>

              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}