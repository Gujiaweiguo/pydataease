import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { userStore } from '../embedded'

describe('embedded store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('has the expected initial state', () => {
    const store = userStore()

    expect(store.$state).toMatchObject({
      type: '',
      token: '',
      busiFlag: '',
      outerParams: '',
      suffixId: '',
      baseUrl: '',
      dvId: '',
      pid: '',
      chartId: '',
      resourceId: '',
      dfId: '',
      opt: '',
      createType: '',
      templateParams: '',
      jumpInfoParam: '',
      outerUrl: '',
      datasourceId: '',
      tableName: '',
      datasetId: '',
      datasetCopyId: '',
      datasetPid: ''
    })
    expect(store.getTokenInfo).toBeInstanceOf(Map)
    expect(store.getIframeData).toEqual({
      embeddedToken: '',
      busiFlag: '',
      outerParams: '',
      suffixId: '',
      type: '',
      dvId: '',
      chartId: '',
      pid: '',
      resourceId: '',
      dfId: ''
    })
  })

  it('updates core embedded fields through dedicated setters', () => {
    const store = userStore()

    store.setType('dashboard')
    store.setToken('token-1')
    store.setBusiFlag('demo')
    store.setOuterParams('{"year":2026}')
    store.setSuffixId('suffix')
    store.setBaseUrl('https://example.com')

    expect(store.getType).toBe('dashboard')
    expect(store.getToken).toBe('token-1')
    expect(store.getBusiFlag).toBe('demo')
    expect(store.getOuterParams).toBe('{"year":2026}')
    expect(store.getSuffixId).toBe('suffix')
    expect(store.getBaseUrl).toBe('https://example.com')
  })

  it('updates dataset and template related metadata', () => {
    const store = userStore()

    store.setCreateType('copy')
    store.setTemplateParams('template-params')
    store.setJumpInfoParam('jump-info')
    store.setOuterUrl('https://outer.example.com')
    store.setDatasourceId('ds-1')
    store.setTableName('orders')
    store.setDatasetId('dataset-1')
    store.setDatasetCopyId('dataset-copy-1')
    store.setdatasetPid('parent-1')

    expect(store.getCreateType).toBe('copy')
    expect(store.getTemplateParams).toBe('template-params')
    expect(store.getJumpInfoParam).toBe('jump-info')
    expect(store.getOuterUrl).toBe('https://outer.example.com')
    expect(store.datasourceId).toBe('ds-1')
    expect(store.tableName).toBe('orders')
    expect(store.datasetId).toBe('dataset-1')
    expect(store.datasetCopyId).toBe('dataset-copy-1')
    expect(store.datasetPid).toBe('parent-1')
  })

  it('hydrates iframe data from a payload and exposes the derived getter', async () => {
    const store = userStore()

    await store.setIframeData({
      type: 'dashboard',
      embeddedToken: 'embed-token',
      busiFlag: 'share',
      outerParams: '{"region":"cn"}',
      suffixId: 'suf',
      dvId: 'dv-1',
      chartId: 'chart-1',
      pid: 'pid-1',
      resourceId: 'resource-1',
      dfId: 'df-1'
    })

    expect(store.getIframeData).toEqual({
      embeddedToken: 'embed-token',
      busiFlag: 'share',
      outerParams: '{"region":"cn"}',
      suffixId: 'suf',
      type: 'dashboard',
      dvId: 'dv-1',
      chartId: 'chart-1',
      pid: 'pid-1',
      resourceId: 'resource-1',
      dfId: 'df-1'
    })
  })

  it('stores tokenInfo as a map', async () => {
    const store = userStore()
    const tokenInfo = new Map<string, object>([['embedded-token', { role: 'viewer' }]])

    await store.setTokenInfo(tokenInfo)

    expect(store.getTokenInfo).toBeInstanceOf(Map)
    expect(Array.from(store.getTokenInfo.entries())).toEqual(Array.from(tokenInfo.entries()))
    expect(store.getTokenInfo.get('embedded-token')).toEqual({ role: 'viewer' })
  })

  it('clears transient resource state while keeping authentication fields intact', () => {
    const store = userStore()
    store.setToken('token-1')
    store.setType('dashboard')
    store.setPid('pid-1')
    store.setOpt('view')
    store.setCreateType('copy')
    store.setTemplateParams('template-params')
    store.setResourceId('resource-1')
    store.setDfId('df-1')
    store.setDvId('dv-1')
    store.setJumpInfoParam('jump-info')
    store.setOuterUrl('https://outer.example.com')
    store.setDatasourceId('ds-1')
    store.setTableName('orders')
    store.setDatasetId('dataset-1')
    store.setDatasetCopyId('dataset-copy-1')
    store.setdatasetPid('parent-1')

    store.clearState()

    expect(store.getToken).toBe('token-1')
    expect(store.getType).toBe('dashboard')
    expect(store.pid).toBe('')
    expect(store.opt).toBe('')
    expect(store.createType).toBe('')
    expect(store.templateParams).toBe('')
    expect(store.resourceId).toBe('')
    expect(store.dfId).toBe('')
    expect(store.dvId).toBe('')
    expect(store.jumpInfoParam).toBe('')
    expect(store.outerUrl).toBe('')
    expect(store.datasourceId).toBe('')
    expect(store.tableName).toBe('')
    expect(store.datasetId).toBe('')
    expect(store.datasetCopyId).toBe('')
    expect(store.datasetPid).toBe('')
  })
})
