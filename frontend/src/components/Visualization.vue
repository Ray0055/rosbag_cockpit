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
                  <input
                    :id="`topic-${index}`"
                    v-model="selectedTopics"
                    :value="topic.name"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
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

      <div>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Visualization</h3>
          <div>
            <button
              @click="refreshVisualization"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Refresh
            </button>
          </div>
        </div>

        <div class="border rounded-lg p-4 h-96 bg-gray-50">
          <!-- 这里是可视化内容 -->
          <div v-if="selectedTopics.length === 0" class="flex justify-center items-center h-full">
            <p class="text-gray-500">Select topics to visualize</p>
          </div>
          <div v-else-if="visualizationLoading" class="flex justify-center items-center h-full">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          </div>
          <div v-else class="h-full w-full" ref="visualizationContainer">
            <!-- 可视化内容将在这里渲染 -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import {
  getRosbagDetails,
  deleteRosbagById,
  downloadRosbagFile,
  visualizeRosbagTopics,
} from '../services/rosbagService'

export default {
  name: 'Visualization',
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

    const selectedTopics = ref([])
    const visualizationLoading = ref(false)
    const visualizationContainer = ref(null)

    const loadRosbagData = async () => {
      loading.value = true
      error.value = ''

      try {
        const data = await getRosbagDetails(props.rosbagId)
        Object.assign(rosbagData, data)

        // 默认选择前3个话题（如果有的话）
        if (data.topics && data.topics.length > 0) {
          selectedTopics.value = data.topics.slice(0, 3).map((topic) => topic.name)
        }
      } catch (err) {
        error.value = err.message || 'Failed to load rosbag data'
      } finally {
        loading.value = false
      }
    }

    const refreshVisualization = async () => {
      if (selectedTopics.value.length === 0) return

      visualizationLoading.value = true

      try {
        const visualizationData = await visualizeRosbagTopics(props.rosbagId, selectedTopics.value)

        // 这里将处理可视化数据和渲染图表的逻辑
        // 注意：具体实现取决于后端返回的数据格式和你选择的可视化库
        // 如 Chart.js, D3.js 等

        if (visualizationContainer.value) {
          // 这里是渲染可视化的代码
          // 例如使用 Chart.js:
          // new Chart(visualizationContainer.value, {
          //   type: 'line',
          //   data: visualizationData,
          //   options: { ... }
          // })
        }
      } catch (err) {
        error.value = err.message || 'Failed to load visualization'
      } finally {
        visualizationLoading.value = false
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

    watch(selectedTopics, () => {
      refreshVisualization()
    })

    onMounted(() => {
      loadRosbagData()
    })

    return {
      loading,
      error,
      rosbagData,
      selectedTopics,
      visualizationLoading,
      visualizationContainer,
      refreshVisualization,
      downloadRosbag,
      deleteRosbag,
      formatDate,
      formatFileSize,
      formatDuration,
    }
  },
}
</script>
