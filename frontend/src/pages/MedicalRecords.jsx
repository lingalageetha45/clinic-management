import React, { useEffect, useState } from 'react'
import {
  getPatients,
  getMedicalRecords,
  uploadMedicalRecord,
  downloadRecord,
} from '../services/api'

export default function MedicalRecords() {
  const [patients, setPatients] = useState([])
  const [selectedPatient, setSelectedPatient] = useState('')
  const [records, setRecords] = useState([])
  const [file, setFile] = useState(null)
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getPatients()
      .then((res) => setPatients(res.data))
      .catch(() => setError('Failed to load patients'))
  }, [])

  useEffect(() => {
    if (!selectedPatient) {
      setRecords([])
      return
    }

    getMedicalRecords(selectedPatient)
      .then((res) => setRecords(res.data))
      .catch(() => setError('Failed to load medical records'))
  }, [selectedPatient])

  const handlePatientChange = (value) => {
    setSelectedPatient(value)
    setError('')
    setSuccess('')
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0] || null
    setFile(selectedFile)
    setError('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()

    if (!selectedPatient) {
      setError('Please select a patient')
      return
    }

    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()

      formData.append('patient_id', selectedPatient)
      formData.append('file', file)

      if (description.trim()) {
        formData.append('description', description.trim())
      }

      await uploadMedicalRecord(formData)

      setSuccess('Medical record uploaded successfully')
      setFile(null)
      setDescription('')

      const fileInput = document.getElementById('medical-file')
      if (fileInput) {
        fileInput.value = ''
      }

      const response = await getMedicalRecords(selectedPatient)
      setRecords(response.data)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Failed to upload medical record'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (id, fileName) => {
    try {
      setError('')

      const response = await downloadRecord(id)

      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)

      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()

      link.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      setError('Failed to download medical record')
    }
  }

  const selectedPatientName =
    patients.find(
      (patient) => String(patient.id) === String(selectedPatient)
    )?.full_name

  return (
    <div className="page-container">

      {/* Page Header */}
      <div className="page-header">
        <div>
          <span className="page-eyebrow">
            CLINICAL DOCUMENTATION
          </span>

          <h1 className="page-title">
            Medical Records
          </h1>

          <p className="page-subtitle">
            Upload, review and securely access patient medical documents.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-msg">
          {error}
        </div>
      )}

      {success && (
        <div className="success-msg">
          {success}
        </div>
      )}

      {/* Upload Section */}
      <div className="card upload-card">

        <div className="card-header">
          <div>
            <span className="section-eyebrow">
              DOCUMENT UPLOAD
            </span>

            <h2 className="card-title">
              Upload Medical Report
            </h2>

            <p className="card-description">
              Attach a medical document to a patient's record.
            </p>
          </div>
        </div>

        <form onSubmit={handleUpload}>

          <div className="form-grid">

            {/* Patient */}
            <div className="form-group">

              <label htmlFor="upload-patient">
                Patient
              </label>

              <select
                id="upload-patient"
                value={selectedPatient}
                onChange={(e) =>
                  handlePatientChange(e.target.value)
                }
                required
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

            {/* File */}
            <div className="form-group">

              <label htmlFor="medical-file">
                Medical Document
              </label>

              <input
                id="medical-file"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                required
              />

              <small className="form-hint">
                Supported formats: PDF, JPG, JPEG and PNG
              </small>

            </div>

            {/* Description */}
            <div
              className="form-group"
              style={{
                gridColumn: '1 / -1',
              }}
            >

              <label htmlFor="record-description">
                Description
              </label>

              <input
                id="record-description"
                type="text"
                value={description}
                onChange={(e) =>
                  setDescription(e.target.value)
                }
                placeholder="e.g. Blood test report, X-ray report, consultation notes..."
              />

            </div>

          </div>

          {/* Selected file */}
          {file && (
            <div className="selected-file">

              <div className="file-icon">
                FILE
              </div>

              <div className="file-info">
                <strong>
                  {file.name}
                </strong>

                <span>
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>

            </div>
          )}

          <div className="upload-actions">

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading
                ? 'Uploading...'
                : 'Upload Medical Record'}
            </button>

          </div>

        </form>

      </div>

      {/* Patient History */}
      <div className="card">

        <div className="card-header">

          <div>
            <span className="section-eyebrow">
              PATIENT HISTORY
            </span>

            <h2 className="card-title">
              Medical Documents
            </h2>

            <p className="card-description">
              View previously uploaded medical records.
            </p>
          </div>

          <div className="patient-selector">

            <label htmlFor="history-patient">
              Patient
            </label>

            <select
              id="history-patient"
              value={selectedPatient}
              onChange={(e) =>
                handlePatientChange(e.target.value)
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

        </div>

        {/* Selected patient */}
        {selectedPatient && (
          <div className="selected-patient">

            <div className="patient-avatar">
              {selectedPatientName?.charAt(0)?.toUpperCase() || 'P'}
            </div>

            <div>
              <span>
                Selected patient
              </span>

              <strong>
                {selectedPatientName || 'Patient'}
              </strong>
            </div>

          </div>
        )}

        <div className="table-wrap">

          <table>

            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Description</th>
                <th>Uploaded</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>

              {!selectedPatient ? (

                <tr>
                  <td
                    colSpan={5}
                    className="empty-state"
                  >
                    <div className="empty-icon">
                      DOC
                    </div>

                    <strong>
                      Select a patient
                    </strong>

                    <span>
                      Choose a patient to view their medical history.
                    </span>
                  </td>
                </tr>

              ) : records.length === 0 ? (

                <tr>
                  <td
                    colSpan={5}
                    className="empty-state"
                  >
                    <div className="empty-icon">
                      DOC
                    </div>

                    <strong>
                      No medical records
                    </strong>

                    <span>
                      No documents have been uploaded for this patient.
                    </span>
                  </td>
                </tr>

              ) : (

                records.map((record) => (

                  <tr key={record.id}>

                    <td>
                      <div className="document-name">

                        <div className="document-icon">
                          FILE
                        </div>

                        <div>
                          <strong>
                            {record.original_name}
                          </strong>

                          <span>
                            Record #{record.id}
                          </span>
                        </div>

                      </div>
                    </td>

                    <td>
                      <span className="document-type">
                        {record.file_type || 'Document'}
                      </span>
                    </td>

                    <td>
                      {record.description || '—'}
                    </td>

                    <td>
                      {record.created_at
                        ? new Date(
                            record.created_at
                          ).toLocaleString()
                        : '—'}
                    </td>

                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() =>
                          handleDownload(
                            record.id,
                            record.original_name
                          )
                        }
                      >
                        Download
                      </button>
                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

        {selectedPatient && records.length > 0 && (
          <div className="table-footer">
            <span>
              {records.length} medical record
              {records.length !== 1 ? 's' : ''} found
            </span>
          </div>
        )}

      </div>

    </div>
  )
}