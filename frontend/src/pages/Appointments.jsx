import React, { useEffect, useState } from 'react'
import {
  getAppointments,
  createAppointment,
  updateAppointment,
  cancelAppointment,
  getPatients,
  getDoctors,
  exportAppointmentsCsv,
} from '../services/api'
import { useAuth } from '../context/AuthContext'

const emptyForm = {
  patient_id: '',
  doctor_id: '',
  appointment_date: '',
  time_slot: '09:00-09:30',
  reason_for_visit: '',
  status: '',
}

const TIME_SLOTS = [
  '09:00-09:30',
  '09:30-10:00',
  '10:00-10:30',
  '10:30-11:00',
  '11:00-11:30',
  '11:30-12:00',
  '14:00-14:30',
  '14:30-15:00',
  '15:00-15:30',
  '15:30-16:00',
  '16:00-16:30',
  '16:30-17:00',
]

const STATUS_OPTIONS = [
  'scheduled',
  'confirmed',
  'completed',
  'cancelled',
  'no_show',
]

export default function Appointments() {
  const [appointments, setAppointments] = useState([])
  const [patients, setPatients] = useState([])
  const [doctors, setDoctors] = useState([])

  const [filters, setFilters] = useState({
    status: '',
    search: '',
  })

  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { user } = useAuth()

  const canBook =
    user?.role === 'admin' ||
    user?.role === 'receptionist'

  const canUpdateStatus =
    user?.role === 'admin' ||
    user?.role === 'doctor' ||
    user?.role === 'receptionist'

  const load = () => {
    const params = {}

    if (filters.status) {
      params.status = filters.status
    }

    if (filters.search) {
      params.search = filters.search
    }

    getAppointments(params)
      .then((res) => setAppointments(res.data))
      .catch(() => setError('Failed to load appointments'))
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
    setEditing(null)

    setForm({
      ...emptyForm,
      appointment_date: new Date()
        .toISOString()
        .slice(0, 10),
    })

    setShowModal(true)
    setError('')
  }

  const openEdit = (appointment) => {
    setEditing(appointment)

    setForm({
      patient_id: appointment.patient_id,
      doctor_id: appointment.doctor_id,
      appointment_date: appointment.appointment_date,
      time_slot: appointment.time_slot,
      reason_for_visit: appointment.reason_for_visit || '',
      status: appointment.status,
    })

    setShowModal(true)
    setError('')
  }

  const closeModal = () => {
    if (loading) return

    setShowModal(false)
    setEditing(null)
    setForm(emptyForm)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    setLoading(true)
    setError('')

    try {
      if (editing) {
        if (user?.role === 'doctor') {
          await updateAppointment(editing.id, {
            status: form.status,
            notes: form.reason_for_visit,
          })
        } else {
          await updateAppointment(editing.id, {
            ...form,
            patient_id: parseInt(form.patient_id),
            doctor_id: parseInt(form.doctor_id),
          })
        }
      } else {
        await createAppointment({
          patient_id: parseInt(form.patient_id),
          doctor_id: parseInt(form.doctor_id),
          appointment_date: form.appointment_date,
          time_slot: form.time_slot,
          reason_for_visit:
            form.reason_for_visit || null,
        })
      }

      setShowModal(false)
      setEditing(null)
      setForm(emptyForm)

      load()
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Operation failed'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id) => {
    if (!window.confirm('Cancel this appointment?')) {
      return
    }

    try {
      await cancelAppointment(id)
      load()
    } catch {
      setError('Cancel failed')
    }
  }

  const handleExport = async () => {
    try {
      const res = await exportAppointmentsCsv()

      const url = window.URL.createObjectURL(
        new Blob([res.data])
      )

      const link = document.createElement('a')

      link.href = url
      link.download = 'appointments.csv'
      link.click()

      window.URL.revokeObjectURL(url)
    } catch {
      setError('Export failed')
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters({
      ...filters,
      [field]: value,
    })
  }

  return (
    <div className="appointments-page">

      <div className="page-header">
        <div>
          <span className="eyebrow">CLINIC OPERATIONS</span>
          <h1 className="page-title">
            Appointments
          </h1>
          <p className="page-subtitle">
            Schedule, manage and monitor patient appointments.
          </p>
        </div>

        {canBook && (
          <button
            className="btn btn-primary"
            onClick={openCreate}
          >
            + Book Appointment
          </button>
        )}
      </div>

      {error && !showModal && (
        <div className="error-msg">
          {error}
        </div>
      )}

      <div className="card">

        <div className="appointment-toolbar">

          <div className="search-bar">

            <input
              placeholder="Search appointment, patient or doctor..."
              value={filters.search}
              onChange={(e) =>
                handleFilterChange(
                  'search',
                  e.target.value
                )
              }
              onKeyDown={(e) =>
                e.key === 'Enter' && load()
              }
            />

            <select
              value={filters.status}
              onChange={(e) =>
                handleFilterChange(
                  'status',
                  e.target.value
                )
              }
            >
              <option value="">
                All Status
              </option>

              {STATUS_OPTIONS.map((status) => (
                <option
                  key={status}
                  value={status}
                >
                  {status.replace('_', ' ')}
                </option>
              ))}
            </select>

            <button
              className="btn btn-secondary"
              onClick={load}
            >
              Filter
            </button>

          </div>

          {(user?.role === 'admin' ||
            user?.role === 'receptionist') && (
            <button
              className="btn btn-secondary"
              onClick={handleExport}
            >
              Export CSV
            </button>
          )}

        </div>

        <div className="table-wrap">

          <table>

            <thead>
              <tr>
                <th>Appointment</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>

              {appointments.length === 0 ? (
                <tr>
                  <td
                    colSpan={8}
                    className="empty-state"
                  >
                    <div className="empty-icon">
                      📅
                    </div>

                    <strong>
                      No appointments found
                    </strong>

                    <span>
                      Appointments matching your
                      filters will appear here.
                    </span>
                  </td>
                </tr>
              ) : (
                appointments.map((appointment) => (
                  <tr key={appointment.id}>

                    <td>
                      <strong>
                        {appointment.appointment_number}
                      </strong>
                    </td>

                    <td>
                      <div className="table-primary">
                        {appointment.patient?.full_name ||
                          appointment.patient_id}
                      </div>
                    </td>

                    <td>
                      <div className="table-primary">
                        {appointment.doctor?.full_name ||
                          appointment.doctor_id}
                      </div>
                    </td>

                    <td>
                      {appointment.appointment_date}
                    </td>

                    <td>
                      {appointment.time_slot}
                    </td>

                    <td>
                      <span
                        className={`badge badge-${appointment.status}`}
                      >
                        {appointment.status.replace(
                          '_',
                          ' '
                        )}
                      </span>
                    </td>

                    <td>
                      {appointment.reason_for_visit ||
                        '—'}
                    </td>

                    <td>
                      <div className="btn-group">

                        {canUpdateStatus &&
                          appointment.status !==
                            'cancelled' && (
                            <button
                              className="btn btn-secondary btn-sm"
                              onClick={() =>
                                openEdit(appointment)
                              }
                            >
                              Update
                            </button>
                          )}

                        {canBook &&
                          appointment.status !==
                            'cancelled' && (
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() =>
                                handleCancel(
                                  appointment.id
                                )
                              }
                            >
                              Cancel
                            </button>
                          )}

                      </div>
                    </td>

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
          onClick={closeModal}
        >
          <div
            className="modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div className="modal-header">
              <div>
                <span className="eyebrow">
                  {editing
                    ? 'APPOINTMENT UPDATE'
                    : 'NEW APPOINTMENT'}
                </span>

                <h2>
                  {editing
                    ? 'Update Appointment'
                    : 'Book Appointment'}
                </h2>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeModal}
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

              <div className="form-grid">

                {!editing && (
                  <>
                    <div className="form-group">
                      <label>Patient</label>

                      <select
                        required
                        value={form.patient_id}
                        onChange={(e) =>
                          setForm({
                            ...form,
                            patient_id:
                              e.target.value,
                          })
                        }
                      >
                        <option value="">
                          Select patient
                        </option>

                        {patients.map((patient) => (
                          <option
                            key={patient.id}
                            value={patient.id}
                          >
                            {patient.full_name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Doctor</label>

                      <select
                        required
                        value={form.doctor_id}
                        onChange={(e) =>
                          setForm({
                            ...form,
                            doctor_id:
                              e.target.value,
                          })
                        }
                      >
                        <option value="">
                          Select doctor
                        </option>

                        {doctors.map((doctor) => (
                          <option
                            key={doctor.id}
                            value={doctor.id}
                          >
                            {doctor.full_name} (
                            {doctor.specialization})
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                {(user?.role !== 'doctor' ||
                  !editing) && (
                  <>
                    <div className="form-group">
                      <label>Appointment Date</label>

                      <input
                        type="date"
                        required
                        value={
                          form.appointment_date
                        }
                        onChange={(e) =>
                          setForm({
                            ...form,
                            appointment_date:
                              e.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Time Slot</label>

                      <select
                        required
                        value={form.time_slot}
                        onChange={(e) =>
                          setForm({
                            ...form,
                            time_slot:
                              e.target.value,
                          })
                        }
                      >
                        {TIME_SLOTS.map((slot) => (
                          <option
                            key={slot}
                            value={slot}
                          >
                            {slot}
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                {editing && (
                  <div className="form-group">
                    <label>Status</label>

                    <select
                      value={form.status || ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          status:
                            e.target.value,
                        })
                      }
                    >
                      {STATUS_OPTIONS.map(
                        (status) => (
                          <option
                            key={status}
                            value={status}
                          >
                            {status.replace(
                              '_',
                              ' '
                            )}
                          </option>
                        )
                      )}
                    </select>
                  </div>
                )}

                <div
                  className="form-group"
                  style={{
                    gridColumn: '1 / -1',
                  }}
                >
                  <label>
                    Reason / Notes
                  </label>

                  <textarea
                    placeholder="Enter reason for visit or additional notes..."
                    value={
                      form.reason_for_visit
                    }
                    onChange={(e) =>
                      setForm({
                        ...form,
                        reason_for_visit:
                          e.target.value,
                      })
                    }
                  />
                </div>

              </div>

              <div className="modal-actions">

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeModal}
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
                    : editing
                      ? 'Update Appointment'
                      : 'Book Appointment'}
                </button>

              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  )
}