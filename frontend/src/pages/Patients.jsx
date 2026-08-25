import React, { useEffect, useState } from 'react'
import {
  getPatients,
  createPatient,
  updatePatient,
  deletePatient,
} from '../services/api'
import { useAuth } from '../context/AuthContext'

const emptyForm = {
  full_name: '',
  age: 30,
  gender: 'Male',
  phone_number: '',
  address: '',
  blood_group: '',
  emergency_contact: '',
  email: '',
}

export default function Patients() {
  const [patients, setPatients] = useState([])
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { user } = useAuth()

  const canManage =
    user?.role === 'admin' ||
    user?.role === 'receptionist'

  const isAdmin = user?.role === 'admin'

  const load = () => {
    setError('')

    getPatients({
      search: search || undefined,
    })
      .then((res) => setPatients(res.data))
      .catch(() => setError('Failed to load patients'))
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

  const openEdit = (patient) => {
    setEditing(patient)

    setForm({
      full_name: patient.full_name,
      age: patient.age,
      gender: patient.gender,
      phone_number: patient.phone_number,
      address: patient.address || '',
      blood_group: patient.blood_group || '',
      emergency_contact: patient.emergency_contact || '',
      email: patient.email || '',
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
        await updatePatient(editing.id, form)
      } else {
        await createPatient(form)
      }

      setShowModal(false)
      load()
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Save failed'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this patient?')) {
      return
    }

    try {
      await deletePatient(id)
      load()
    } catch {
      setError('Delete failed')
    }
  }

  return (
    <div>
      <h1 className="page-title">Patients</h1>

      {error && !showModal && (
        <div className="error-msg">
          {error}
        </div>
      )}

      <div className="card">
        <div className="card-header">

          <div className="search-bar">
            <input
              placeholder="Search name or phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  load()
                }
              }}
            />

            <button
              className="btn btn-secondary"
              onClick={load}
            >
              Search
            </button>
          </div>

          {canManage && (
            <button
              className="btn btn-primary"
              onClick={openCreate}
            >
              + Register Patient
            </button>
          )}

        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Phone</th>
                <th>Blood Group</th>
                <th>Email</th>

                {canManage && (
                  <th>Actions</th>
                )}
              </tr>
            </thead>

            <tbody>
              {patients.length === 0 ? (
                <tr>
                  <td
                    colSpan={canManage ? 7 : 6}
                    className="empty-state"
                  >
                    No patients found
                  </td>
                </tr>
              ) : (
                patients.map((patient) => (
                  <tr key={patient.id}>

                    <td>
                      {patient.full_name}
                    </td>

                    <td>
                      {patient.age}
                    </td>

                    <td>
                      {patient.gender}
                    </td>

                    <td>
                      {patient.phone_number}
                    </td>

                    <td>
                      {patient.blood_group || '—'}
                    </td>

                    <td>
                      {patient.email || '—'}
                    </td>

                    {canManage && (
                      <td>
                        <div className="btn-group">

                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() =>
                              openEdit(patient)
                            }
                          >
                            Edit
                          </button>

                          {isAdmin && (
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() =>
                                handleDelete(patient.id)
                              }
                            >
                              Delete
                            </button>
                          )}

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
              {editing
                ? 'Update Patient'
                : 'Register Patient'}
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
                  <label>Age</label>

                  <input
                    type="number"
                    min="0"
                    max="150"
                    required
                    value={form.age}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        age:
                          parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>Gender</label>

                  <select
                    value={form.gender}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        gender: e.target.value,
                      })
                    }
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
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
                  <label>Blood Group</label>

                  <input
                    value={form.blood_group}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        blood_group: e.target.value,
                      })
                    }
                    placeholder="A+, B-, O+..."
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>

                  <input
                    type="email"
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
                  <label>Emergency Contact</label>

                  <input
                    value={form.emergency_contact}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        emergency_contact:
                          e.target.value,
                      })
                    }
                  />
                </div>

                <div
                  className="form-group"
                  style={{
                    gridColumn: '1 / -1',
                  }}
                >
                  <label>Address</label>

                  <textarea
                    value={form.address}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        address: e.target.value,
                      })
                    }
                  />
                </div>

              </div>

              <div className="modal-actions">

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() =>
                    setShowModal(false)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading
                    ? 'Saving...'
                    : 'Save'}
                </button>

              </div>

            </form>
          </div>
        </div>
      )}
    </div>
  )
}