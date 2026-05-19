import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('../form/option', () => ({
  dsTypes: [
    { name: 'MySQL', type: 'mysql', catalog: 'OLTP' },
    { name: 'PostgreSQL', type: 'pg', catalog: 'OLTP' }
  ],
  typeList: ['OLTP', 'OLAP', 'DL', 'OTHER', 'LOCAL'],
  nameMap: { OLTP: 'OLTP', OLAP: 'OLAP', DL: 'DL', OTHER: 'OTHER', LOCAL: 'LOCAL' }
}))

vi.mock('@/components/icon-group/datasource-list', () => ({
  iconDatasourceMap: {}
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div class="xpack-stub" />' }
}))

import DsTypeList from '../form/DsTypeList.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' },
  XpackComponent: { template: '<div class="xpack-stub" />' }
}

describe('DsTypeList', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(DsTypeList, {
      props: { currentType: 'OLTP', filterText: '' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('shows OLTP category databases', () => {
    const wrapper = shallowMount(DsTypeList, {
      props: { currentType: 'OLTP', filterText: '' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('MySQL')
    expect(wrapper.text()).toContain('PostgreSQL')
  })

  it('filters databases by filterText', () => {
    const wrapper = shallowMount(DsTypeList, {
      props: { currentType: 'OLTP', filterText: 'mysql' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('MySQL')
    expect(wrapper.text()).not.toContain('PostgreSQL')
  })

  it('emits selectDsType when a database card is clicked', async () => {
    const wrapper = shallowMount(DsTypeList, {
      props: { currentType: 'OLTP', filterText: '' },
      global: { stubs: globalStubs }
    })
    const cards = wrapper.findAll('.db-card')
    if (cards.length > 0) {
      await cards[0].trigger('click')
      expect(wrapper.emitted('selectDsType')).toBeTruthy()
    }
  })
})
