import api, { uploadFile } from './api'

// 获取所有Rosbag列表
export const getRosbags = async () => {
  try {
    return await api.get('/rosbags')
  } catch (error) {
    throw error
  }
}

// 获取Rosbag详情
export const getRosbagDetails = async (id) => {
  try {
    return await api.get(`/rosbags/${id}`)
  } catch (error) {
    throw error
  }
}

// 上传Rosbag文件
export const uploadRosbagFile = async (formData, onUploadProgress) => {
  try {
    return await uploadFile('/rosbags/upload', formData, onUploadProgress)
  } catch (error) {
    throw error
  }
}

// 删除Rosbag
export const deleteRosbagById = async (id) => {
  try {
    return await api.delete(`/rosbags/${id}`)
  } catch (error) {
    throw error
  }
}

// 下载Rosbag文件
export const downloadRosbagFile = async (id) => {
  try {
    // 这里使用标准axios而不是我们的api实例，因为我们需要处理二进制响应
    const response = await api.get(`/rosbags/${id}/download`, {
      responseType: 'blob', // 重要：返回二进制数据
    })

    // 获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = 'rosbag.bag'

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1]
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    return true
  } catch (error) {
    throw error
  }
}

// 获取Rosbag可视化数据
export const visualizeRosbagTopics = async (id, topics) => {
  try {
    return await api.post(`/rosbags/${id}/visualize`, { topics })
  } catch (error) {
    throw error
  }
}

export const getDashboardStats = async () => {
  try {
    return await api.get('/stats')
  } catch (error) {
    throw error
  }
}
