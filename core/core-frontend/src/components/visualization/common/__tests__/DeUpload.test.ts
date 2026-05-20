import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: vi.fn(v => v) }))
vi.mock('@/api/staticResource', () => ({
  beforeUploadCheck: vi.fn(),
  uploadFileResult: vi.fn()
}))

import DeUpload from '../DeUpload.vue'

describe('DeUpload', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DeUpload, {
      props: { themes: 'dark' },
      global: {
        stubs: {
          'el-upload': true,
          'el-icon': { template: '<div><slot /></div>' },
          'img-view-dialog': true,
          Plus: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains avatar-uploader-container wrapper', () => {
    const wrapper = shallowMount(DeUpload, {
      props: { themes: 'dark' },
      global: {
        stubs: {
          'el-upload': true,
          'el-icon': { template: '<div><slot /></div>' },
          'img-view-dialog': true,
          Plus: true
        }
      }
    })
    expect(wrapper.find('.avatar-uploader-container').exists()).toBe(true)
  })

  it('renders with light theme', () => {
    const wrapper = shallowMount(DeUpload, {
      props: { themes: 'light', imgUrl: '' },
      global: {
        stubs: {
          'el-upload': true,
          'el-icon': { template: '<div><slot /></div>' },
          'img-view-dialog': true,
          Plus: true
        }
      }
    })
    expect(wrapper.find('.img-area_light').exists()).toBe(true)
  })
})
