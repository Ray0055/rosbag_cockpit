import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api', // FastAPI 后端API地址
  timeout: 30000, // 超时时间30秒
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 这里可以添加认证token等
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    // 请求错误处理
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果后端返回标准格式，可以在这里统一处理
    return response.data
  },
  (error) => {
    // 错误处理
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      const errorMessage = error.response.data?.detail || 'Server error'

      if (status === 401) {
        // 未授权处理
        console.error('Unauthorized access')
        // 可以在这里跳转到登录页面
      } else if (status === 403) {
        // 禁止访问处理
        console.error('Access forbidden')
      } else if (status === 404) {
        // 资源不存在
        console.error('Resource not found')
      } else if (status === 500) {
        // 服务器错误
        console.error('Server error')
      }

      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('No response from server')
      return Promise.reject(new Error('No response from server, please check your network'))
    } else {
      // 请求设置错误
      console.error('Request error', error.message)
      return Promise.reject(error)
    }
  }
)

// 用于上传文件的接口，支持进度回调
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
    // 使用与上面相同的错误处理逻辑
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
