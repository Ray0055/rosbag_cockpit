<template>
  <div class="overflow-x-auto bg-white shadow-md rounded-lg">
    <table class="min-w-full table-auto">
      <!--table header-->
      <thead class="bg-gray-200">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
          >
            {{ column.label }}
          </th>
          <th
            class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
          >
            Actions
          </th>
        </tr>
      </thead>
      <!--table body-->
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="(item, index) in data" :key="index" class="hover:bg-gray-50">
          <td
            v-for="column in columns"
            :key="`${index}-${column.key}`"
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
          >
            <template v-if="column.key.startsWith('topic_')">
              <span
                v-if="item[column.key]"
                class="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
              >
                {{ item[column.key] }}
              </span>
              <span v-else>-</span>
            </template>
            <template v-else>
              {{ item[column.key] }}
            </template>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
            <button @click="$emit('view', item)" class="text-blue-600 hover:text-blue-900 mr-3">
              View
            </button>
            <button @click="$emit('delete', item)" class="text-red-600 hover:text-red-900">
              Delete
            </button>
          </td>
        </tr>
        <tr v-if="data.length === 0">
          <td :colspan="columns.length + 1" class="px-6 py-4 text-center text-sm text-gray-500">
            No data available
          </td>
        </tr>
      </tbody>
    </table>
    <div class="px-6 py-3 bg-gray-50 border-t flex justify-between">
      <span class="text-sm text-gray-700"> Showing {{ data.length }} items </span>
      <div class="flex space-x-2">
        <button
          @click="$emit('page-change', currentPage - 1)"
          :disabled="currentPage <= 1"
          class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          :class="currentPage <= 1 ? 'text-gray-400' : 'text-blue-600 hover:bg-blue-50'"
        >
          Previous
        </button>
        <button
          @click="$emit('page-change', currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="px-3 py-1 border rounded text-sm disabled:opacity-50"
          :class="currentPage >= totalPages ? 'text-gray-400' : 'text-blue-600 hover:bg-blue-50'"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    columns: {
      type: Array,
      required: true,
    },
    data: {
      type: Array,
      required: true,
    },
    currentPage: {
      type: Number,
      default: 1,
    },
    totalPages: {
      type: Number,
      default: 1,
    },
  },
  emits: ['view', 'delete', 'page-change'],
}
</script>
