import { t } from '@/hooks/web/useI18n'
import request from '@/config/axios'
import { normalizeShortcutRow } from '@/utils/visualizationResource'
export interface ShortcutRequest {
  keyword?: string
  type?: string
  asc?: boolean
}
interface TableColumn {
  field: string
  label: string
  type?: string
}
interface BusiRecord {
  columnList: TableColumn[]
  url: string
  busiList: string[]
  dataCache?: any[]
}
class ShortcutOption {
  busiFlag: string
  busiRecordMap: {
    recent: BusiRecord
    store: BusiRecord
    // share: BusiRecord
  }

  constructor() {
    this.busiFlag = 'recent'
    this.busiRecordMap = {
      recent: {
        url: '/dataVisualization/findRecent',
        busiList: ['panel', 'screen', 'dataset', 'datasource'],
        dataCache: [],
        columnList: [
          { field: 'type', label: t('datasource.type') },
          { field: 'creator', label: t('visualization.create_by') },
          { field: 'lastEditor', label: t('work_branch.last_edited_by') },
          { field: 'lastEditTime', label: t('work_branch.last_edit_time'), type: 'time' }
        ]
      },
      store: {
        url: '/store/query',
        busiList: ['panel', 'screen'],
        dataCache: [],
        columnList: [
          { field: 'type', label: t('datasource.type') },
          { field: 'creator', label: t('visualization.create_by') },
          { field: 'lastEditor', label: t('work_branch.last_edited_by') },
          { field: 'lastEditTime', label: t('work_branch.last_edit_time'), type: 'time' }
        ]
      }
    }
  }
  getColumnList() {
    return this.busiRecordMap[this.busiFlag].columnList
  }
  loadData(param: ShortcutRequest): Promise<IResponse> {
    const url = this.busiRecordMap[this.busiFlag].url
    if (this.emptyParam(param) && this.getCacheData()?.length) {
      return new Promise(res => {
        const result = {
          code: 200,
          data: this.getCacheData(),
          msg: null
        }
        return res(result)
      })
    }
    return request
      .post({ url, data: param })
      .then(res => {
        const responseData = res?.data ?? []
        const data = (Array.isArray(responseData) ? responseData : responseData?.list ?? []).map(
          item => normalizeShortcutRow(item)
        )
        if (this.emptyParam(param)) {
          this.busiRecordMap[this.busiFlag].dataCache = data
        }
        return {
          code: res?.code ?? 200,
          data,
          msg: res?.msg ?? null
        }
      })
      .catch(() => ({
        code: 200,
        data: [],
        msg: null
      }))
  }
  getCacheData() {
    return this.busiRecordMap[this.busiFlag].dataCache
  }
  emptyParam(param: ShortcutRequest) {
    return param.asc == null && !param.keyword && !param.type
  }
  setBusiFlag(busiFlag) {
    this.busiFlag = busiFlag
  }
  getBusiList() {
    const all = 'all_types'
    return [all, ...this.busiRecordMap[this.busiFlag].busiList]
  }
}

export const shortcutOption = new ShortcutOption()
