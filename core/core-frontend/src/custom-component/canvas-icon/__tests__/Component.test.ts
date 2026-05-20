import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: {
    name: 'Icon',
    template: '<div class="icon-stub"><slot /></div>'
  }
}))
vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    'board-1': 'Board1Icon',
    'board-2': 'Board2Icon'
  }
}))

import Component from '../Component.vue'

describe('canvas-icon Component', () => {
  it('renders successfully with non-board innerType', () => {
    const wrapper = mount(Component, {
      props: {
        propValue: 'some-icon',
        element: { innerType: 'SvgIcon' }
      },
      global: {
        stubs: {
          SvgIcon: { template: '<div class="svg-icon-stub"></div>' }
        }
      }
    })
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('renders with board innerType using iconBoardMap', () => {
    const wrapper = mount(Component, {
      props: {
        propValue: 'board-icon',
        element: { innerType: 'board-1' }
      }
    })
    expect(wrapper.find('.icon-stub').exists()).toBe(true)
  })

  it('passes propValue prop correctly', () => {
    const wrapper = mount(Component, {
      props: {
        propValue: 'test-value',
        element: { innerType: 'SvgIcon' }
      },
      global: {
        stubs: {
          SvgIcon: true
        }
      }
    })
    expect(wrapper.props('propValue')).toBe('test-value')
  })
})
