import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import DeEmpty from '../common/DeEmpty.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `translated:${key}` })
}))

const EmptyBackgroundStub = defineComponent({
  name: 'EmptyBackground',
  props: {
    description: {
      type: String,
      default: ''
    },
    imgType: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="empty-background-stub" :data-description="description" :data-img-type="imgType">{{ description }}|{{ imgType }}</div>'
})

describe('DeEmpty', () => {
  const mountComponent = () =>
    mount(DeEmpty, {
      global: {
        stubs: {
          ElRow: {
            template: '<div class="el-row-stub"><slot /></div>'
          },
          EmptyBackground: EmptyBackgroundStub
        }
      }
    })

  it('renders the wrapper container', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.custom-position').exists()).toBe(true)
  })

  it('passes the expected description prop to EmptyBackground', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.empty-background-stub').attributes('data-description')).toBe(
      "t('visualization.select_dimension_hint')"
    )
  })

  it('passes the noneWhite image type to EmptyBackground', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.empty-background-stub').attributes('data-img-type')).toBe('noneWhite')
  })
})
