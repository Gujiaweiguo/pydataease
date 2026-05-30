import { defineStore } from 'pinia'
import { store } from '@/store/index'
import { featureStatus } from '@/api/feature-flag'

/** Canonical feature flag keys — must match SETTINGS_DEFAULTS in backend */
export const FEATURE_KEYS = {
  adminConfig: 'feature.adminConfig.enabled',
  appearance: 'feature.appearance.enabled',
  watermark: 'feature.watermark.enabled',
  sysVariable: 'feature.sysVariableContract.enabled',
  embedding: 'feature.embedding.enabled',
  platformIntegration: 'feature.platformIntegration.enabled',
  identification: 'feature.identification.enabled',
  dataFiling: 'feature.dataFiling.enabled'
} as const

export type FeatureKey = (typeof FEATURE_KEYS)[keyof typeof FEATURE_KEYS]

interface FeatureFlagState {
  flags: Record<string, boolean>
  loaded: boolean
}

export const useFeatureFlagStore = defineStore('featureFlag', {
  state: (): FeatureFlagState => ({
    flags: {},
    loaded: false
  }),

  getters: {
    isAdminConfigEnabled(): boolean {
      return this.flags[FEATURE_KEYS.adminConfig] ?? false
    },
    isAppearanceEnabled(): boolean {
      return this.flags[FEATURE_KEYS.appearance] ?? false
    },
    isWatermarkEnabled(): boolean {
      return this.flags[FEATURE_KEYS.watermark] ?? false
    },
    isSysVariableEnabled(): boolean {
      return this.flags[FEATURE_KEYS.sysVariable] ?? false
    },
    isEmbeddingEnabled(): boolean {
      return this.flags[FEATURE_KEYS.embedding] ?? false
    },
    isPlatformIntegrationEnabled(): boolean {
      return this.flags[FEATURE_KEYS.platformIntegration] ?? false
    },
    isIdentificationEnabled(): boolean {
      return this.flags[FEATURE_KEYS.identification] ?? false
    },
    isDataFilingEnabled(): boolean {
      return this.flags[FEATURE_KEYS.dataFiling] ?? false
    },
    isFeatureEnabled:
      state =>
      (key: FeatureKey): boolean => {
        return state.flags[key] ?? false
      }
  },

  actions: {
    async loadFlags() {
      if (this.loaded) return
      try {
        const res = await featureStatus()
        const data: Record<string, boolean> = res.data || {}
        this.flags = data
      } catch {
        // fail-closed: leave all flags false
        this.flags = {}
      } finally {
        this.loaded = true
      }
    },

    setFlag(key: FeatureKey, enabled: boolean) {
      this.flags[key] = enabled
    }
  }
})

export const useFeatureFlagStoreWithOut = () => {
  return useFeatureFlagStore(store)
}
