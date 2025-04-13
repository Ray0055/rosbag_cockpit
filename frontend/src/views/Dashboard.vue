<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="bg-white shadow-md rounded-lg p-6">
      <h2 class="text-xl font-bold mb-4">Statistics</h2>

      <div v-if="loading" class="flex justify-center items-center h-32">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <div v-else class="grid grid-cols-2 gap-4">
        <div class="bg-blue-50 p-4 rounded-lg">
          <p class="text-sm text-blue-500 font-medium">Total Rosbags</p>
          <p class="text-2xl font-bold">{{ stats.totalRosbags }}</p>
        </div>

        <div class="bg-green-50 p-4 rounded-lg">
          <p class="text-sm text-green-500 font-medium">Total Size</p>
          <p class="text-2xl font-bold">
            {{ formatFileSize(stats.totalSize) }}
          </p>
        </div>

        <div class="bg-purple-50 p-4 rounded-lg">
          <p class="text-sm text-purple-500 font-medium">Total Topics</p>
          <p class="text-2xl font-bold">{{ stats.totalTopics }}</p>
        </div>

        <div class="bg-yellow-50 p-4 rounded-lg">
          <p class="text-sm text-yellow-600 font-medium">Latest Upload</p>
          <p class="text-lg font-bold">
            {{ stats.latestUpload ? formatDate(stats.latestUpload) : 'None' }}
          </p>
        </div>
      </div>
    </div>

    <div class="bg-white shadow-md rounded-lg p-6">
      <h2 class="text-xl font-bold mb-4">Recent Activity</h2>

      <div v-if="loading" class="flex justify-center items-center h-32">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <div v-else-if="activities.length === 0" class="text-gray-500 text-center py-8">
        <p>No recent activity</p>
      </div>

      <div v-else>
        <ul class="divide-y divide-gray-200">
          <li v-for="(activity, index) in activities" :key="index" class="py-3">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <span
                  :class="getActivityIcon(activity.type).bgColor"
                  class="flex items-center justify-center h-8 w-8 rounded-full"
                >
                  <svg
                    class="h-5 w-5"
                    :class="getActivityIcon(activity.type).textColor"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      :d="getActivityIcon(activity.type).icon"
                    />
                  </svg>
                </span>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">
                  {{ activity.description }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatDate(activity.timestamp) }}
                </p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="bg-white shadow-md rounded-lg p-6 md:col-span-2 lg:col-span-1">
      <h2 class="text-xl font-bold mb-4">Popular Topics</h2>

      <div v-if="loading" class="flex justify-center items-center h-32">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <div v-else-if="popularTopics.length === 0" class="text-gray-500 text-center py-8">
        <p>No topic data available</p>
      </div>

      <div v-else>
        <ul class="space-y-3">
          <li
            v-for="(topic, index) in popularTopics"
            :key="index"
            class="bg-gray-50 rounded-lg p-3"
          >
            <div class="flex justify-between items-center">
              <div>
                <p class="font-medium text-gray-900">{{ topic.name }}</p>
                <p class="text-xs text-gray-500">{{ topic.messageType }}</p>
              </div>
              <div class="flex items-center">
                <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                  {{ topic.count }} bags
                </span>
              </div>
            </div>
            <div class="mt-2 w-full bg-gray-200 rounded-full h-2.5">
              <div
                class="bg-blue-600 h-2.5 rounded-full"
                :style="{
                  width: `${(topic.count / popularTopics[0].count) * 100}%`,
                }"
              ></div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '../services/rosbagService'

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(true)
    const error = ref('')
    const stats = ref({
      totalRosbags: 0,
      totalSize: 0,
      totalTopics: 0,
      latestUpload: null,
    })
    const activities = ref([])
    const popularTopics = ref([])

    const loadDashboardData = async () => {
      loading.value = true
      error.value = ''

      try {
        // 并行请求数据
        const [statsData, activitiesData, topicsData] = await Promise.all([getDashboardStats()])

        stats.value = statsData
        activities.value = activitiesData
        popularTopics.value = topicsData
      } catch (err) {
        error.value = err.message || 'Failed to load dashboard data'
      } finally {
        loading.value = false
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

    const getActivityIcon = (type) => {
      const icons = {
        upload: {
          icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
          bgColor: 'bg-green-100',
          textColor: 'text-green-600',
        },
        delete: {
          icon: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
          bgColor: 'bg-red-100',
          textColor: 'text-red-600',
        },
        view: {
          icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-600',
        },
        download: {
          icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
          bgColor: 'bg-purple-100',
          textColor: 'text-purple-600',
        },
        default: {
          icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-600',
        },
      }

      return icons[type] || icons.default
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      error,
      stats,
      activities,
      popularTopics,
      formatDate,
      formatFileSize,
      getActivityIcon,
    }
  },
}
</script>
