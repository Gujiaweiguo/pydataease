import { Base64 } from 'js-base64'
import { describe, expect, it } from 'vitest'

import {
  originNameHandle,
  originNameHandleBack,
  originNameHandleBackWithArr,
  originNameHandleWithArr
} from '../CalculateFields'

describe('CalculateFields utils', () => {
  it('encodes origin names only for extension fields', () => {
    const fields = [
      { extField: 2, originName: '指标A' },
      { extField: 1, originName: '指标B' }
    ]

    originNameHandle(fields as any)

    expect(fields[0].originName).toBe(Base64.encode('指标A'))
    expect(fields[1].originName).toBe('指标B')
  })

  it('decodes origin names only for extension fields', () => {
    const encoded = Base64.encode('维度A')
    const fields = [
      { extField: 2, originName: encoded },
      { extField: 0, originName: 'plain' }
    ]

    originNameHandleBack(fields as any)

    expect(fields[0].originName).toBe('维度A')
    expect(fields[1].originName).toBe('plain')
  })

  it('handles empty arrays and default arguments safely', () => {
    expect(() => originNameHandle()).not.toThrow()
    expect(() => originNameHandleBack()).not.toThrow()
  })

  it('processes configured array fields on an object', () => {
    const payload = {
      dimensions: [{ extField: 2, originName: '地区' }],
      quotas: [{ extField: 1, originName: '销售额' }]
    }

    originNameHandleWithArr(payload as any, ['dimensions', 'quotas'])

    expect(payload.dimensions[0].originName).toBe(Base64.encode('地区'))
    expect(payload.quotas[0].originName).toBe('销售额')
  })

  it('decodes configured fields and ignores missing arrays', () => {
    const payload = {
      dimensions: [{ extField: 2, originName: Base64.encode('城市') }]
    }

    originNameHandleBackWithArr(payload as any, ['dimensions', 'missing'])

    expect(payload.dimensions[0].originName).toBe('城市')
  })

  it('supports round-tripping through encode and decode helpers', () => {
    const payload = [{ extField: 2, originName: '订单日期' }]

    originNameHandle(payload as any)
    originNameHandleBack(payload as any)

    expect(payload[0].originName).toBe('订单日期')
  })
})
