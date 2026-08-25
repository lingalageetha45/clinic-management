import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api

// Auth
export const login = (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export const register = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

// Doctors
export const getDoctors = (params) => api.get('/doctors', { params })
export const getDoctor = (id) => api.get(`/doctors/${id}`)
export const createDoctor = (data) => api.post('/doctors', data)
export const updateDoctor = (id, data) => api.put(`/doctors/${id}`, data)
export const deleteDoctor = (id) => api.delete(`/doctors/${id}`)

// Patients
export const getPatients = (params) => api.get('/patients', { params })
export const getPatient = (id) => api.get(`/patients/${id}`)
export const createPatient = (data) => api.post('/patients', data)
export const updatePatient = (id, data) => api.put(`/patients/${id}`, data)
export const deletePatient = (id) => api.delete(`/patients/${id}`)

// Appointments
export const getAppointments = (params) => api.get('/appointments', { params })
export const getAppointment = (id) => api.get(`/appointments/${id}`)
export const createAppointment = (data) => api.post('/appointments', data)
export const updateAppointment = (id, data) => api.put(`/appointments/${id}`, data)
export const cancelAppointment = (id) => api.delete(`/appointments/${id}`)
export const exportAppointmentsCsv = () =>
  api.get('/appointments/export/csv', { responseType: 'blob' })

// Prescriptions
export const getPrescriptions = (params) => api.get('/prescriptions', { params })
export const getPrescription = (id) => api.get(`/prescriptions/${id}`)
export const createPrescription = (data) => api.post('/prescriptions', data)
export const updatePrescription = (id, data) => api.put(`/prescriptions/${id}`, data)

// Medical Records
export const getMedicalRecords = (patientId) => api.get(`/medical-records/${patientId}`)
export const uploadMedicalRecord = (formData) =>
  api.post('/medical-records/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const downloadRecord = (id) =>
  api.get(`/medical-records/download/${id}`, { responseType: 'blob' })

// Reports
export const getDashboard = () => api.get('/reports/dashboard')
export const getAppointmentsReport = () => api.get('/reports/appointments')
export const getDoctorsReport = () => api.get('/reports/doctors')
