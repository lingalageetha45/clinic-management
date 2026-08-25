import React, { useEffect, useState } from 'react'
import {
  getPrescriptions,
  createPrescription,
  getPatients,
  getDoctors,
} from '../services/api'
import { useAuth } from '../context/AuthContext'

const emptyForm = {
  patient_id: '',
  doctor_id: '',
  diagnosis: '',
  medicines: '',
  dosage: '',
  instructions: '',
  follow_up_date: '',
}

export default function Prescriptions() {
  const [list, setList] = useState([])
  const [patients, setPatients] = useState([])
  const [doctors, setDoctors] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')

  const { user } = useAuth()

  const canCreate =
    user?.role === 'admin' ||
    user?.role === 'doctor'

  const load = () => {
    getPrescriptions()
      .then((res) => setList(res.data))
      .catch(() => setError('Failed to load prescriptions'))
  }

  useEffect(() => {
    load()

    getPatients()
      .then((res) => setPatients(res.data))
      .catch(() => {})

    getDoctors()
      .then((res) => setDoctors(res.data))
      .catch(() => {})
  }, [])

  const openCreate = () => {
    setForm(emptyForm)
    setError('')
    setShowModal(true)
  }

  const closeModal = () => {
    if (loading) return

    setShowModal(false)
    setForm(emptyForm)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    setLoading(true)
    setError('')

    try {
      const payload = {
        ...form,
        patient_id: parseInt(form.patient_id),
        doctor_id: parseInt(form.doctor_id),
        follow_up_date: form.follow_up_date || null,
      }

      await createPrescription(payload)

      closeModal()
      load()
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Failed to create prescription'
      )
    } finally {
      setLoading(false)
    }
  }

  const filteredList = list.filter((p) => {
    const searchText = search.toLowerCase()

    const patientName =
      p.patient?.full_name?.toLowerCase() || ''

    const doctorName =
      p.doctor?.full_name?.toLowerCase() || ''

    const diagnosis =
      p.diagnosis?.toLowerCase() || ''

    return (
      patientName.includes(searchText) ||
      doctorName.includes(searchText) ||
      diagnosis.includes(searchText) ||
      String(p.patient_id).includes(searchText)
    )
  })

  return (
    <div className="page-container">

      {/* Page Header */}
      <div className="page-header">
        <div>
          <span className="page-eyebrow">
            CLINICAL MANAGEMENT
          </span>

          <h1 className="page-title">
            Prescriptions
          </h1>

          <p className="page-subtitle">
            Create and manage patient prescriptions.
          </p>
        </div>

        {canCreate && (
          <button
            className="btn btn-primary"
            onClick={openCreate}
          >
            + Create Prescription
          </button>
        )}
      </div>

      {error && !showModal && (
        <div className="error-msg">
          {error}
        </div>
      )}

      {/* Main Card */}
      <div className="card">

        <div className="card-header">

          <div>
            <h2 className="card-title">
              Prescription Records
            </h2>

            <p className="card-description">
              View prescriptions issued to clinic patients.
            </p>
          </div>

          <div className="search-bar">
            <input
              type="text"
              placeholder="Search patient, doctor..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

        </div>

        <div className="table-wrap">

          <table>

            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Diagnosis</th>
                <th>Medicines</th>
                <th>Dosage</th>
                <th>Follow-up</th>
                <th>Created</th>
              </tr>
            </thead>

            <tbody>

              {filteredList.length === 0 ? (
                <tr>
                  <td
                    colSpan={8}
                    className="empty-state"
                  >
                    <div className="empty-icon">
                      Rx
                    </div>

                    <strong>
                      No prescriptions found
                    </strong>

                    <span>
                      Prescription records will appear here.
                    </span>
                  </td>
                </tr>
              ) : (

                filteredList.map((p) => (

                  <tr key={p.id}>

                    <td>
                      <span className="record-id">
                        #{p.id}
                      </span>
                    </td>

                    <td>
                      <strong>
                        {p.patient?.full_name ||
                          p.patient_id}
                      </strong>
                    </td>

                    <td>
                      {p.doctor?.full_name ||
                        p.doctor_id}
                    </td>

                    <td>
                      {p.diagnosis || '—'}
                    </td>

                    <td>
                      <span className="medicine-text">
                        {p.medicines || '—'}
                      </span>
                    </td>

                    <td>
                      {p.dosage || '—'}
                    </td>

                    <td>
                      {p.follow_up_date || '—'}
                    </td>

                    <td>
                      {p.created_at
                        ? new Date(
                            p.created_at
                          ).toLocaleDateString()
                        : '—'}
                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

        <div className="table-footer">
          <span>
            Showing {filteredList.length} prescription
            {filteredList.length !== 1 ? 's' : ''}
          </span>
        </div>

      </div>

      {/* Create Prescription Modal */}
      {showModal && (

        <div
          className="modal-overlay"
          onClick={closeModal}
        >

          <div
            className="modal prescription-modal"
            onClick={(e) => e.stopPropagation()}
          >

            <div className="modal-header">

              <div>
                <span className="modal-eyebrow">
                  NEW RECORD
                </span>

                <h2>
                  Create Prescription
                </h2>

                <p>
                  Add prescription details for a patient.
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeModal}
                disabled={loading}
              >
                ×
              </button>

            </div>

            {error && (
              <div className="error-msg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>

              <div className="form-section">

                <div className="form-section-title">
                  Patient & Doctor
                </div>

                <div className="form-grid">

                  <div className="form-group">

                    <label>
                      Patient
                    </label>

                    <select
                      required
                      value={form.patient_id}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          patient_id: e.target.value,
                        })
                      }
                    >
                      <option value="">
                        Select patient
                      </option>

                      {patients.map((p) => (
                        <option
                          key={p.id}
                          value={p.id}
                        >
                          {p.full_name}
                        </option>
                      ))}

                    </select>

                  </div>

                  <div className="form-group">

                    <label>
                      Doctor
                    </label>

                    <select
                      required
                      value={form.doctor_id}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          doctor_id: e.target.value,
                        })
                      }
                    >
                      <option value="">
                        Select doctor
                      </option>

                      {doctors.map((d) => (
                        <option
                          key={d.id}
                          value={d.id}
                        >
                          {d.full_name}
                        </option>
                      ))}

                    </select>

                  </div>

                </div>

              </div>

              <div className="form-section">

                <div className="form-section-title">
                  Clinical Information
                </div>

                <div className="form-grid">

                  <div
                    className="form-group"
                    style={{
                      gridColumn: '1 / -1',
                    }}
                  >

                    <label>
                      Diagnosis
                    </label>

                    <textarea
                      required
                      placeholder="Enter diagnosis..."
                      value={form.diagnosis}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          diagnosis: e.target.value,
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

                    <label>
                      Medicines
                    </label>

                    <textarea
                      required
                      placeholder="Enter prescribed medicines..."
                      value={form.medicines}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          medicines: e.target.value,
                        })
                      }
                    />

                  </div>

                  <div className="form-group">

                    <label>
                      Dosage
                    </label>

                    <input
                      type="text"
                      placeholder="1-0-1 after food"
                      value={form.dosage}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          dosage: e.target.value,
                        })
                      }
                    />

                  </div>

                  <div className="form-group">

                    <label>
                      Follow-up Date
                    </label>

                    <input
                      type="date"
                      value={form.follow_up_date}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          follow_up_date: e.target.value,
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

                    <label>
                      Instructions
                    </label>

                    <textarea
                      placeholder="Additional instructions for the patient..."
                      value={form.instructions}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          instructions: e.target.value,
                        })
                      }
                    />

                  </div>

                </div>

              </div>

              <div className="modal-actions">

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeModal}
                  disabled={loading}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading
                    ? 'Creating...'
                    : 'Create Prescription'}
                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>
  )
}