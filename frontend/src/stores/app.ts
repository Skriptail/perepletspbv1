// Utilities
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    loading: false,
    error: null as string | null,
    theme: 'dark',
  }),

  actions: {
    setLoading(loading: boolean) {
      this.loading = loading
    },
    setError(error: string | null) {
      this.error = error
    },
    setTheme(theme: 'light' | 'dark') {
      this.theme = theme
    },
  },
})
