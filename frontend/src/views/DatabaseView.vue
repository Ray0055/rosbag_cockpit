<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Database</h1>
      <router-link
        to="/upload"
        class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
      >
        Upload New RosBag
      </router-link>
    </div>

    <div class="mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-grow">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search rosbags..."
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @input="handleSearch"
          />
        </div>
        <div class="flex-shrink-0">
          <select
            v-model="sortBy"
            class="w-full md:w-auto px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="handleSort"
          >
            <option value="name">Sort by Name</option>
            <option value="uploadDate">Sort by Date</option>
            <option value="size">Sort by Size</option>
          </select>
        </div>
      </div>
    </div>

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
      <DataTable
        :columns="columns"
        :data="rosbags"
        :current-page="currentPage"
        :total-pages="totalPages"
        @view="viewRosbag"
        @delete="confirmDelete"
        @page-change="changePage"
      />
    </div>

    <!-- 删除确认对话框 -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md mx-auto">
        <h3 class="text-lg font-semibold mb-4">Confirm Delete</h3>
        <p class="mb-6">
          Are you sure you want to delete the rosbag "{{ rosbagToDelete?.name }}"? This action
          cannot be undone.
        </p>
        <div class="flex justify-end space-x-4">
          <button
            @click="showDeleteConfirm = false"
            class="px-4 py-2 border rounded-lg hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            @click="deleteRosbag"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <div
      v-if="selectedRosbag"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-4xl mx-auto w-full max-h-screen overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold">Rosbag Details</h3>
          <button @click="selectedRosbag = null" class="text-gray-500 hover:text-gray-700">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <Visualization :rosbag-id="selectedRosbag.id" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import Visualization from '../components/Visualization.vue'
import { getRosbags, deleteRosbagById } from '../services/rosbagService'

export default {
  name: 'DatabaseView',
  components: {
    DataTable,
    Visualization,
  },
  setup() {
    const loading = ref(true)
    const error = ref('')
    const rosbags = ref([])
    const allRosbags = ref([])
    const currentPage = ref(1)
    const itemsPerPage = 50
    const totalPages = ref(1)
    const searchTerm = ref('')
    const sortBy = ref('uploadDate')
    const selectedRosbag = ref(null)
    const showDeleteConfirm = ref(false)
    const rosbagToDelete = ref(null)

    const columns = ref([
      { key: 'file_path', label: 'File Path' },
      { key: 'map_category', label: 'Map Category' },
      { key: 'start_time', label: 'Start Time' },
      { key: 'end_time', label: 'End Time' },
      { key: 'duration', label: 'Duration (s)' },
      { key: 'size_mb', label: 'Size (MB)' },
      { key: 'message_count', label: 'Message Count' },
      { key: 'topic_count', label: 'Topics Count' },
      { key: 'created_at', label: 'Created Date' },
    ])
    // 2. 修改 loadRosbags 函数
    const loadRosbags = async () => {
      loading.value = true
      error.value = ''

      try {
        const data = await getRosbags()

        // 首先检查是否有 topic_counts 数据，并创建动态列
        if (data.length > 0 && data[0].topic_counts) {
          // 提取所有可能存在的话题名称
          const topicKeys = Object.keys(data[0].topic_counts)

          // 为每个话题创建一个列定义
          const topicColumns = topicKeys.map((topic) => {
            // 创建更友好的显示名称
            const displayName = topic.substring(1).replace(/\//g, ' ').replace('_', ' ')
            return {
              key: `topic_${topic}`,
              label: `${displayName} Count`,
            }
          })

          // 更新列定义，添加动态列
          columns.value = [
            ...columns.value.filter((col) => !col.key.startsWith('topic_')), // 移除旧的 topic 列
            ...topicColumns,
          ]
        }

        // 处理数据格式，使其适合表格显示
        allRosbags.value = data.map((bag) => {
          // 创建基础数据对象
          const bagData = {
            created_at: bag.created_at,
            duration: bag.duration?.toFixed(2) || 0, // 格式化持续时间
            file_path: bag.file_path,
            end_time: bag.end_time,
            id: bag.id,
            map_category: bag.map_category,
            message_count: bag.message_count,
            size_mb: bag.size_mb?.toFixed(2) || 0, // 格式化大小
            start_time: bag.start_time,
            topic_count: bag.topic_count,
          }

          // 为每个话题添加特定字段，以便表格渲染
          if (bag.topic_counts) {
            Object.entries(bag.topic_counts).forEach(([topic, count]) => {
              bagData[`topic_${topic}`] = count
            })
          }

          return bagData
        })
        updateFilteredRosbags()
      } catch (err) {
        error.value = err.message || 'Failed to load rosbags'
      } finally {
        loading.value = false
      }
    }

    const updateFilteredRosbags = () => {
      // 过滤
      let filtered = [...allRosbags.value]

      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        filtered = filtered.filter((bag) => bag.name.toLowerCase().includes(term))
      }

      // 排序
      filtered.sort((a, b) => {
        if (sortBy.value === 'name') {
          return a.name.localeCompare(b.name)
        } else if (sortBy.value === 'uploadDate') {
          return new Date(b._rawDate) - new Date(a._rawDate)
        } else if (sortBy.value === 'size') {
          return b._rawSize - a._rawSize
        }
        return 0
      })

      // 更新总页数
      totalPages.value = Math.ceil(filtered.length / itemsPerPage)

      // 分页
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      rosbags.value = filtered.slice(start, end)

      // 确保当前页在有效范围内
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = totalPages.value
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const handleSearch = () => {
      currentPage.value = 1
      updateFilteredRosbags()
    }

    const handleSort = () => {
      updateFilteredRosbags()
    }

    const changePage = (page) => {
      currentPage.value = page
      updateFilteredRosbags()
    }

    const viewRosbag = (rosbag) => {
      selectedRosbag.value = rosbag
    }

    const confirmDelete = (rosbag) => {
      rosbagToDelete.value = rosbag
      showDeleteConfirm.value = true
    }

    const deleteRosbag = async () => {
      if (!rosbagToDelete.value) return

      try {
        await deleteRosbagById(rosbagToDelete.value.id)

        // 从列表中移除
        allRosbags.value = allRosbags.value.filter((bag) => bag.id !== rosbagToDelete.value.id)
        updateFilteredRosbags()

        showDeleteConfirm.value = false
        rosbagToDelete.value = null
      } catch (err) {
        error.value = err.message || 'Failed to delete rosbag'
      }
    }

    onMounted(() => {
      loadRosbags()
    })

    return {
      loading,
      error,
      rosbags,
      columns,
      currentPage,
      totalPages,
      searchTerm,
      sortBy,
      selectedRosbag,
      showDeleteConfirm,
      rosbagToDelete,
      handleSearch,
      handleSort,
      changePage,
      viewRosbag,
      confirmDelete,
      deleteRosbag,
    }
  },
}
</script>
