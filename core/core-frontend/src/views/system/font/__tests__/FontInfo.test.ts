import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import FontInfo from '../FontInfo.vue'

const globalStubs = {
  ElIcon: { template: '<i @click="$emit(\'click\')"><slot /></i>' },
  Icon: { template: '<i><slot /></i>' }
}

describe('FontInfo', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(FontInfo, {
      props: { name: 'Arial', size: '12kb' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays font name and size', () => {
    const wrapper = shallowMount(FontInfo, {
      props: { name: 'Helvetica', size: '24kb' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.font-info').exists()).toBe(true)
    expect(wrapper.find('.name').text()).toBe('Helvetica')
    expect(wrapper.find('.size').text()).toBe('24kb')
  })

  it('displays dash when name and size are empty', () => {
    const wrapper = shallowMount(FontInfo, {
      props: { name: '', size: '' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.name').text()).toBe('-')
    expect(wrapper.find('.size').text()).toBe('-')
  })

  it('emits del event when delete icon is clicked', async () => {
    const wrapper = shallowMount(FontInfo, {
      props: { name: 'Arial', size: '12kb' },
      global: { stubs: globalStubs }
    })
    const deleteIcon = wrapper.find('.delete')
    await deleteIcon.trigger('click')
    expect(wrapper.emitted('del')).toBeTruthy()
  })

  it('uses default empty strings for name and size', () => {
    const wrapper = shallowMount(FontInfo, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.name').text()).toBe('-')
    expect(wrapper.find('.size').text()).toBe('-')
  })
})
