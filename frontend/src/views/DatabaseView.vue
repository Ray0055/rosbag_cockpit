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
            placeholder="Search rosbags from file path ..."
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @input="handleSearch"
          />
        </div>
        <div class="flex-shrink-0">
          <select
            v-model="filterBy"
            class="w-full md:w-auto px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="handleFilter"
          >
            <option value="all">All Maps</option>
            <option value="skidpad">Skidpad</option>
            <option value="acceleration">Acceleration</option>
            <option value="autox">Autox</option>
            <option value="trackdrive">Trackdrive</option>
            <option value="undefined">Undefined</option>
          </select>
        </div>
        <div class="flex-shrink-0">
          <select
            v-model="sortBy"
            class="w-full md:w-auto px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="handleSort"
          >
            <option value="map_category">Sort by Map</option>
            <option value="start_time">Sort by Date</option>
            <option value="size_mb">Sort by Size</option>
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

    <!-- Delete confirmation dialog -->
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

    <!-- Details dialog -->
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

        <RosbagDetail :rosbag-id="selectedRosbag.id" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import RosbagDetail from '../components/RosbagDetail.vue'
import { getRosbags, deleteRosbagById } from '../services/rosbagService'

export default {
  name: 'DatabaseView',
  components: {
    DataTable,
    RosbagDetail: RosbagDetail,
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
    const sortBy = ref('map_category')
    const filterBy = ref('all')
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
    // 2. Modify loadRosbags function
    const loadRosbags = async () => {
      loading.value = true
      error.value = ''

      try {
        const data = await getRosbags()

        // First check if there is topic_counts data, and create dynamic columns
        if (data.length > 0 && data[0].topic_counts) {
          // Extract all possible topic names
          const topicKeys = Object.keys(data[0].topic_counts)

          // Create a column definition for each topic
          const topicColumns = topicKeys.map((topic) => {
            // Create a more friendly display name
            const displayName = topic.substring(1).replace(/\//g, ' ').replace('_', ' ')
            return {
              key: `topic_${topic}`,
              label: `${displayName} Count`,
            }
          })

          // Update column definitions, add dynamic columns
          columns.value = [
            ...columns.value.filter((col) => !col.key.startsWith('topic_')), // Remove old topic columns
            ...topicColumns,
          ]
        }

        // Process data format to make it suitable for table display
        allRosbags.value = data.map((bag) => {
          // Create base data object
          const bagData = {
            created_at: bag.created_at,
            duration: bag.duration?.toFixed(2) || 0, // Format duration
            file_path: bag.file_path,
            end_time: bag.end_time,
            id: bag.id,
            map_category: bag.map_category,
            message_count: bag.message_count,
            size_mb: bag.size_mb?.toFixed(2) || 0, // Format size
            start_time: bag.start_time,
            topic_count: bag.topic_count,
          }

          // Add specific fields for each topic for table rendering
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
      // Filter
      let filtered = []
      if (filterBy.value === 'all') {
        filtered = [...allRosbags.value]
      } else {
        // Filter items based on map_category
        filtered = allRosbags.value.filter(
          (item) =>
            item.map_category && item.map_category.toLowerCase() === filterBy.value.toLowerCase()
        )
      }

      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        filtered = filtered.filter((bag) => bag.file_path.toLowerCase().includes(term))
      }

      // Sort
      filtered.sort((a, b) => {
        if (sortBy.value === 'map_category') {
          return a.map_category.localeCompare(b.map_category)
        } else if (sortBy.value === 'start_time') {
          // Convert custom date format to something Date can understand
          const dateA = a.start_time ? convertCustomDateFormat(a.start_time) : null
          const dateB = b.start_time ? convertCustomDateFormat(b.start_time) : null

          // Handle cases where dates might be missing
          if (dateA && dateB) {
            return dateB - dateA // Sort descending (newer first)
          }
          if (!dateA) return 1 // Items with no date go to the end
          if (!dateB) return -1
          return 0
        } else if (sortBy.value === 'size_mb') {
          return b.size_mb - a.size_mb
        }
        return 0
      })

      // Update total pages
      totalPages.value = Math.ceil(filtered.length / itemsPerPage)

      // Pagination
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      rosbags.value = filtered.slice(start, end)

      // Ensure current page is within valid range
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

    const handleFilter = () => {
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

        // Remove from list
        allRosbags.value = allRosbags.value.filter((bag) => bag.id !== rosbagToDelete.value.id)
        updateFilteredRosbags()

        showDeleteConfirm.value = false
        rosbagToDelete.value = null
      } catch (err) {
        error.value = err.message || 'Failed to delete rosbag'
      }
    }

    const convertCustomDateFormat = (dateString) => {
      // supose dateString is "2023-10-01-12-00-00"
      const parts = dateString.split('-')
      const year = parseInt(parts[0], 10)
      const month = parseInt(parts[1], 10) - 1 // Months are 0-based in JavaScript
      const day = parseInt(parts[2], 10)
      const hour = parseInt(parts[3], 10)
      const minute = parseInt(parts[4], 10)
      const second = parseInt(parts[5], 10)
      return new Date(year, month, day, hour, minute, second)
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
      filterBy,
      selectedRosbag,
      showDeleteConfirm,
      rosbagToDelete,
      handleSearch,
      handleSort,
      changePage,
      viewRosbag,
      confirmDelete,
      deleteRosbag,
      handleFilter,
    }
  },
}
</script>
