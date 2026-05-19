import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import TemplateSkeleton from '../TemplateSkeleton.vue'

const globalStubs = {
  ElCol: { template: '<div><slot /></div>' },
  ElRow: { template: '<div><slot /></div>' }
}

describe('TemplateSkeleton', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(TemplateSkeleton, {
      props: { width: 200 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders skeleton template items', () => {
    const wrapper = shallowMount(TemplateSkeleton, {
      props: { width: 200 },
      global: { stubs: globalStubs }
    })
    const skeletons = wrapper.findAll('.testcase-template_skeleton')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('renders with different widths', () => {
    const wrapper = shallowMount(TemplateSkeleton, {
      props: { width: 300 },
      global: { stubs: globalStubs }
    })
    const imgSkeleton = wrapper.find('.template-img_skeleton')
    expect(imgSkeleton.exists()).toBe(true)
  })
})
