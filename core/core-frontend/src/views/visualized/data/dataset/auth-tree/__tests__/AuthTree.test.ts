import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import AuthTree from '../AuthTree.vue'

describe('AuthTree', () => {
  it('renders component', () => {
    const wrapper = shallowMount(AuthTree, {
      props: { relationList: [], logic: 'or', x: 0 },
      global: {
        stubs: {
          'filter-filed': true,
          'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>' },
          'el-dropdown-menu': { template: '<div><slot /></div>' },
          'el-dropdown-item': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          'logic-relation': true,
          Icon: { template: '<div><slot /></div>' },
          icon_down_outlined: true,
          icon_deleteTrash_outlined: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains logic wrapper', () => {
    const wrapper = shallowMount(AuthTree, {
      props: { relationList: [], logic: 'or', x: 0 },
      global: {
        stubs: {
          'filter-filed': true,
          'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>' },
          'el-dropdown-menu': { template: '<div><slot /></div>' },
          'el-dropdown-item': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          'logic-relation': true,
          Icon: { template: '<div><slot /></div>' },
          icon_down_outlined: true,
          icon_deleteTrash_outlined: true
        }
      }
    })
    expect(wrapper.find('.logic').exists()).toBe(true)
  })

  it('shows OR logic label when logic is or', () => {
    const wrapper = shallowMount(AuthTree, {
      props: { relationList: [], logic: 'or', x: 0 },
      global: {
        stubs: {
          'filter-filed': true,
          'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>' },
          'el-dropdown-menu': { template: '<div><slot /></div>' },
          'el-dropdown-item': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          'logic-relation': true,
          Icon: { template: '<div><slot /></div>' },
          icon_down_outlined: true,
          icon_deleteTrash_outlined: true
        }
      }
    })
    expect(wrapper.text()).toContain('OR')
  })

  it('shows AND logic label when logic is and', () => {
    const wrapper = shallowMount(AuthTree, {
      props: { relationList: [], logic: 'and', x: 0 },
      global: {
        stubs: {
          'filter-filed': true,
          'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>' },
          'el-dropdown-menu': { template: '<div><slot /></div>' },
          'el-dropdown-item': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          'logic-relation': true,
          Icon: { template: '<div><slot /></div>' },
          icon_down_outlined: true,
          icon_deleteTrash_outlined: true
        }
      }
    })
    expect(wrapper.text()).toContain('AND')
  })
})
