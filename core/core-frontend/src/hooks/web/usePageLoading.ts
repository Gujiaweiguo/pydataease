import { useAppStoreWithOut } from '@/store/modules/app'

export const usePageLoading = () => {
  const appStore = useAppStoreWithOut()
  const loadStart = () => {
    appStore.setPageLoading(true)
  }

  const loadDone = () => {
    appStore.setPageLoading(false)
  }

  return {
    loadStart,
    loadDone
  }
}
