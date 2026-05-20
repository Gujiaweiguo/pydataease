import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(), set: vi.fn() }
  })
}))

vi.mock('@/api/datasource', () => ({
  checkRepeat: vi.fn(() => Promise.resolve(false)),
  listDatasources: vi.fn(() => Promise.resolve({ data: [] })),
  save: vi.fn(() => Promise.resolve({ data: {} })),
  update: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/api/dataset', () => ({}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
  ElMessageBox: { confirm: vi.fn() },
  ElMessageBoxOptions: {}
}))

vi.mock('@/utils/treeSortUtils', () => ({
  default: vi.fn(() => [])
}))

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v)))
}))

vi.mock('@/utils/utils', () => ({
  filterFreeFolder: vi.fn((v: any) => v)
}))

vi.mock('@/assets/svg/dv-folder.svg', () => ({ default: 'folder-icon' }))
vi.mock('@/assets/svg/icon_search-outline_outlined.svg', () => ({ default: 'search-icon' }))
vi.mock('@/assets/img/nothing-tree.png', () => ({ default: 'nothing-tree-img' }))

import CreatDsGroup from '../CreatDsGroup.vue'

const globalStubs = {
  'el-input': { template: '<input />' },
  'el-button': { template: '<button><slot /></button>' },
  'el-dialog': { template: '<div class="el-dialog"><slot /></div>' },
  'el-tree': { template: '<div><slot /></div>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-scrollbar': { template: '<div><slot /></div>' }
}

describe('CreatDsGroup', () => {
  const mountComponent = () =>
    shallowMount(CreatDsGroup, {
      global: {
        stubs: globalStubs,
        mocks: {
          $t: (k: string) => k
        }
      }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has a wrapper element', () => {
    const wrapper = mountComponent()
    expect(wrapper.element).toBeTruthy()
  })
})
