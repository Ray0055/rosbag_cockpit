<template>
  <div class="bg-white shadow-md rounded-lg p-6">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <div
      v-else-if="error"
      class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
    >
      <p>{{ error }}</p>
    </div>

    <div v-else>
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">{{ rosbagData.name }}</h2>
        <div class="flex space-x-2">
          <button
            @click="downloadRosbag"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            Download
          </button>
          <button
            @click="deleteRosbag"
            class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Delete
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 class="text-lg font-semibold mb-2">Details</h3>
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="mb-2">
              <span class="font-medium">Upload Date:</span>
              {{ formatDate(rosbagData.uploadDate) }}
            </p>
            <p class="mb-2">
              <span class="font-medium">Size:</span>
              {{ formatFileSize(rosbagData.size) }}
            </p>
            <p class="mb-2">
              <span class="font-medium">Duration:</span>
              {{ formatDuration(rosbagData.duration) }}
            </p>
            <p>
              <span class="font-medium">Description:</span>
              {{ rosbagData.description || 'No description provided' }}
            </p>
          </div>
        </div>

        <div>
          <h3 class="text-lg font-semibold mb-2">Topics</h3>
          <div class="max-h-60 overflow-y-auto bg-gray-50 p-4 rounded-lg">
            <ul class="divide-y divide-gray-200">
              <li v-for="(topic, index) in rosbagData.topics" :key="index" class="py-2">
                <div class="flex items-center">
                  <label :for="`topic-${index}`" class="ml-2 text-sm text-gray-700">
                    {{ topic.name }}
                    <span class="text-xs text-gray-500">({{ topic.messageType }})</span>
                  </label>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { getRosbagDetails, deleteRosbagById, downloadRosbagFile } from '../services/rosbagService'

export default {
  name: 'RosbagDetails',
  props: {
    rosbagId: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const loading = ref(true)
    const error = ref('')
    const rosbagData = reactive({
      id: '',
      name: '',
      description: '',
      uploadDate: '',
      size: 0,
      duration: 0,
      topics: [],
    })

    const loadRosbagData = async () => {
      loading.value = true
      error.value = ''

      try {
        const data = await getRosbagDetails(props.rosbagId)
        Object.assign(rosbagData, data)
      } catch (err) {
        error.value = err.message || 'Failed to load rosbag data'
      } finally {
        loading.value = false
      }
    }

    const downloadRosbag = async () => {
      try {
        await downloadRosbagFile(props.rosbagId)
      } catch (err) {
        error.value = err.message || 'Failed to download rosbag'
      }
    }

    const deleteRosbag = async () => {
      if (!confirm('Are you sure you want to delete this rosbag?')) return

      try {
        await deleteRosbagById(props.rosbagId)
        // 删除成功后，可以跳转到列表页面
        // router.push('/database')
      } catch (err) {
        error.value = err.message || 'Failed to delete rosbag'
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString()
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDuration = (seconds) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    onMounted(() => {
      loadRosbagData()
    })

    return {
      loading,
      error,
      rosbagData,
      downloadRosbag,
      deleteRosbag,
      formatDate,
      formatFileSize,
      formatDuration,
    }
  },
}
</script>
