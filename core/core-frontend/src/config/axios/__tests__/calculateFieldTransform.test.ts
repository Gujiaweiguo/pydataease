import { describe, expect, it } from 'vitest'
import { encodeCalculatedFieldsDeep, decodeCalculatedFieldsDeep } from '../calculateFieldTransform'

describe('calculateFieldTransform', () => {
  const computedField = {
    extField: 2,
    originName: '[1715072798361]*[1715072798367]',
    name: 'revenue'
  }
  const regularField = { extField: 0, originName: 'sales_amount', name: 'amount' }

  it('encodes computed field originName (extField === 2)', () => {
    const input = { fields: [computedField] }
    const result = encodeCalculatedFieldsDeep(input)
    expect(result.fields[0].originName).not.toBe('[1715072798361]*[1715072798367]')
    expect(result.fields[0].originName).toBeTruthy()
    expect(typeof result.fields[0].originName).toBe('string')
  })

  it('does not encode regular field originName (extField !== 2)', () => {
    const input = { fields: [regularField] }
    const result = encodeCalculatedFieldsDeep(input)
    expect(result.fields[0].originName).toBe('sales_amount')
  })

  it('is idempotent — does not double-encode', () => {
    const input = { fields: [computedField] }
    const once = encodeCalculatedFieldsDeep(input)
    const twice = encodeCalculatedFieldsDeep(once)
    expect(twice.fields[0].originName).toBe(once.fields[0].originName)
  })

  it('decodes encoded computed field originName back to plaintext', () => {
    const encoded = encodeCalculatedFieldsDeep({ fields: [computedField] })
    const decoded = decodeCalculatedFieldsDeep(encoded)
    expect(decoded.fields[0].originName).toBe('[1715072798361]*[1715072798367]')
  })

  it('does not mutate the original input', () => {
    const input = { fields: [{ extField: 2, originName: 'test_expr' }] }
    const originalOrigin = input.fields[0].originName
    encodeCalculatedFieldsDeep(input)
    expect(input.fields[0].originName).toBe(originalOrigin)
  })

  it('handles nested structures — objects containing arrays containing field objects', () => {
    const input = {
      data: {
        allFields: [computedField, regularField],
        nested: {
          deepField: { extField: 2, originName: 'deep_expr' }
        }
      }
    }
    const result = encodeCalculatedFieldsDeep(input)
    expect(result.data.allFields[0].originName).not.toBe('[1715072798361]*[1715072798367]')
    expect(result.data.allFields[1].originName).toBe('sales_amount')
    expect(result.data.nested.deepField.originName).not.toBe('deep_expr')

    const decoded = decodeCalculatedFieldsDeep(result)
    expect(decoded.data.allFields[0].originName).toBe('[1715072798361]*[1715072798367]')
    expect(decoded.data.allFields[1].originName).toBe('sales_amount')
    expect(decoded.data.nested.deepField.originName).toBe('deep_expr')
  })

  it('handles arrays of field objects', () => {
    const input = [computedField, regularField]
    const result = encodeCalculatedFieldsDeep(input)
    expect(result[0].originName).not.toBe('[1715072798361]*[1715072798367]')
    expect(result[1].originName).toBe('sales_amount')
  })

  it('preserves non-originName properties on field objects', () => {
    const input = { fields: [{ extField: 2, originName: 'expr', name: 'my_field', deType: 2 }] }
    const result = encodeCalculatedFieldsDeep(input)
    expect(result.fields[0].name).toBe('my_field')
    expect(result.fields[0].deType).toBe(2)
  })

  it('returns primitives, null, and undefined unchanged', () => {
    expect(encodeCalculatedFieldsDeep(null)).toBeNull()
    expect(encodeCalculatedFieldsDeep(undefined)).toBeUndefined()
    expect(encodeCalculatedFieldsDeep('hello')).toBe('hello')
    expect(encodeCalculatedFieldsDeep(42)).toBe(42)
    expect(encodeCalculatedFieldsDeep(true)).toBe(true)
  })

  it('does not traverse Date, File, Blob, or FormData objects', () => {
    const date = new Date('2024-01-01')
    const input = { date, field: computedField }
    const result = encodeCalculatedFieldsDeep(input)
    expect(result.date).toBe(date)
    expect(result.field.originName).not.toBe('[1715072798361]*[1715072798367]')
  })

  it('handles empty objects and arrays', () => {
    expect(encodeCalculatedFieldsDeep({})).toEqual({})
    expect(encodeCalculatedFieldsDeep([])).toEqual([])
  })

  it('round-trips correctly for complex payloads', () => {
    const input = {
      xAxis: [{ extField: 2, originName: '[id1]+[id2]' }],
      yAxis: [{ extField: 0, originName: 'amount' }],
      allFields: [
        { extField: 2, originName: '[id3]*[id4]' },
        { extField: 1, originName: 'group_field' }
      ]
    }
    const encoded = encodeCalculatedFieldsDeep(input)
    const decoded = decodeCalculatedFieldsDeep(encoded)
    expect(decoded.xAxis[0].originName).toBe('[id1]+[id2]')
    expect(decoded.yAxis[0].originName).toBe('amount')
    expect(decoded.allFields[0].originName).toBe('[id3]*[id4]')
    expect(decoded.allFields[1].originName).toBe('group_field')
  })
})
