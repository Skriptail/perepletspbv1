/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        colors: {
          primary: '#2026A2',
          secondary: '#FC2237',
          accent: '#FFF100',
          background: '#0F0F0F',
          surface: '#1A1A1A',
          'surface-variant': '#2D2D2D',
          'on-surface-variant': '#E0E0E0',
        },
        variables: {
          'border-color': 'rgba(255, 255, 255, 0.12)',
          'border-opacity': 1,
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.6,
          'disabled-opacity': 0.38,
          'idle-opacity': 0.04,
          'hover-opacity': 0.04,
          'focus-opacity': 0.12,
          'selected-opacity': 0.08,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.12,
          'dragged-opacity': 0.08,
          'theme-kbd': '#000000',
          'theme-on-kbd': '#FFFFFF',
          'code-color': '#FC2237',
        },
      }
    }
  },
  defaults: {
    global: {
      ripple: false,
      font: {
        family: 'GeistSans, sans-serif',
      },
    },
    VApp: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VBtn: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VTextField: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VCard: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VToolbar: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VList: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VChip: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VDialog: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VTabs: {
      fontFamily: 'GeistSans, sans-serif',
    },
    VBottomNavigation: {
      fontFamily: 'GeistSans, sans-serif',
    },
  },
})
