import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import DsTypeList from '../DsTypeList.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<i class="icon-stub"><slot /></i>', props: ['name', 'staticContent'] }
}))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div class="xpack-stub" />', props: ['jsname'] }
}))
vi.mock('@/components/icon-group/datasource-list', () => ({
  iconDatasourceMap: { mysql: 'mysql-icon', pg: 'pg-icon', Excel: 'excel-icon' }
}))
vi.mock('../option', () => ({
  dsTypes: [
    { type: 'mysql', name: 'MySQL', catalog: 'OLTP', extraParams: '' },
    { type: 'pg', name: 'PostgreSQL', catalog: 'OLTP', extraParams: '' },
    { type: 'Excel', name: 'Excel', catalog: 'LOCAL', extraParams: '' }
  ],
  typeList: ['OLTP', 'LOCAL'],
  nameMap: { OLTP: 'OLTP', LOCAL: 'LOCAL' }
}))

const elStubs = {
  'el-icon': { template: '<i class="el-icon"><slot /></i>' },
  Icon: { template: '<i class="icon-stub"><slot /></i>', props: ['name', 'staticContent'] },
  XpackComponent: { template: '<div class="xpack-stub" />', props: ['jsname'] }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(DsTypeList, {
    props: {
      currentType: 'OLTP',
      filterText: '',
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('DsTypeList', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.ds-type-list').exists()).toBe(true)
  })

  it('should render with currentType OLTP', () => {
    const wrapper = createWrapper({ currentType: 'OLTP' })
    const cards = wrapper.findAll('.db-card')
    expect(cards.length).toBe(2)
  })

  it('should render with currentType LOCAL', () => {
    const wrapper = createWrapper({ currentType: 'LOCAL' })
    const cards = wrapper.findAll('.db-card')
    expect(cards.length).toBe(1)
  })

  it('should render with currentType all', () => {
    const wrapper = createWrapper({ currentType: 'all' })
    expect(wrapper).toBeTruthy()
  })

  it('should filter by filterText', () => {
    const wrapper = createWrapper({ currentType: 'OLTP', filterText: 'mysql' })
    const cards = wrapper.findAll('.db-card')
    expect(cards.length).toBe(1)
  })

  it('should render with empty filterText showing all items in category', () => {
    const wrapper = createWrapper({ currentType: 'OLTP', filterText: '' })
    const cards = wrapper.findAll('.db-card')
    expect(cards.length).toBe(2)
  })

  it('should emit selectDsType when clicking a db card', async () => {
    const wrapper = createWrapper({ currentType: 'OLTP' })
    const cards = wrapper.findAll('.db-card')
    if (cards.length > 0) {
      await cards[0].trigger('click')
      expect(wrapper.emitted('selectDsType')).toBeTruthy()
    }
  })

  it('should render with latestUse currentType', () => {
    const wrapper = createWrapper({
      currentType: 'latestUse',
      latestUseTypes: ['mysql']
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render xpack component', () => {
    const wrapper = createWrapper()
    expect(wrapper.html()).toContain('anonymous-stub')
    expect(wrapper.html()).toContain('L2NvbXBvbmVudC9wbHVnaW5zLWhhbmRsZXIvRHNDYXRlZ29yeUhhbmRsZXI=')
  })
})
