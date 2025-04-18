import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Here you can add authentication token, etc.
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    // Request error handling
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // If backend returns standard format, you can handle it uniformly here
    return response.data
  },
  (error) => {
    // Error handling
    if (error.response) {
      // Server returned error status code
      const status = error.response.status
      const errorMessage = error.response.data?.detail || 'Server error'

      if (status === 401) {
        // Unauthorized handling
        console.error('Unauthorized access')
        // You can redirect to login page here
      } else if (status === 403) {
        // Forbidden access handling
        console.error('Access forbidden')
      } else if (status === 404) {
        // Resource not found
        console.error('Resource not found')
      } else if (status === 500) {
        // Server error
        console.error('Server error')
      }

      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      // Request was sent but no response received
      console.error('No response from server')
      return Promise.reject(new Error('No response from server, please check your network'))
    } else {
      // Request setup error
      console.error('Request error', error.message)
      return Promise.reject(error)
    }
  }
)

// Interface for uploading files, supports progress callback
export const uploadFile = async (url, formData, onUploadProgress) => {
  try {
    const response = await axios.post(`${api.defaults.baseURL}${url}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
    return response.data
  } catch (error) {
    // Use the same error handling logic as above
    if (error.response) {
      const errorMessage = error.response.data?.detail || 'Upload failed'
      throw new Error(errorMessage)
    } else if (error.request) {
      throw new Error('No response from server, please check your network')
    } else {
      throw error
    }
  }
}

export default api
