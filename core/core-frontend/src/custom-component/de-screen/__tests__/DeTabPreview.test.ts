import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DeTabPreview from '../DeTabPreview.vue'

describe('de-screen/DeTabPreview', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(DeTabPreview)
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('renders empty div', () => {
    const wrapper = shallowMount(DeTabPreview)
    expect(wrapper.html()).toContain('<div')
  })
})
