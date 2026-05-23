export interface PreviewCalcParam {
  id?: string
  value?: number | string | null
}

export interface PreviewCalcField {
  id?: string | number | null
  dataeaseName?: string | null
  fieldShortName?: string | null
  name?: string | null
  originName?: string | null
  deType?: number | null
  type?: string | null
  extField?: number | null
  params?: PreviewCalcParam[] | null
  checked?: boolean | null
  columnIndex?: number | null
}

export type PreviewRow = Record<string, unknown>

const SINGLE_REFERENCE_RE = /^\[([^\]]+)\]$/

const fieldKey = (field: PreviewCalcField): string => {
  return String(field.dataeaseName || field.name || field.originName || field.id || '')
}

const fieldLookupKeys = (field: PreviewCalcField): string[] => {
  return [field.dataeaseName, field.name, field.originName, field.fieldShortName].filter(
    (value): value is string => typeof value === 'string' && value.length > 0
  )
}

const readRowValue = (row: PreviewRow, field: PreviewCalcField): unknown => {
  for (const key of fieldLookupKeys(field)) {
    if (key in row) {
      return row[key]
    }
  }
  return undefined
}

const toNumericLiteral = (value: unknown): string => {
  if (value === null || value === undefined || value === '') {
    return '0'
  }
  if (typeof value === 'number') {
    return Number.isFinite(value) ? String(value) : '0'
  }
  const numeric = Number(value)
  return Number.isFinite(numeric) ? String(numeric) : '0'
}

const sanitizeExpression = (expression: string): string => expression.replace(/\s+/g, '')

const evaluateNumericExpression = (expression: string): number | null => {
  if (!/^[0-9+\-*/().]+$/.test(expression)) {
    return null
  }
  try {
    const value = Function(`"use strict"; return (${expression})`)()
    return typeof value === 'number' && Number.isFinite(value) ? value : null
  } catch {
    return null
  }
}

const compareColumnOrder = (left: PreviewCalcField, right: PreviewCalcField): number => {
  const leftIndex = left.columnIndex ?? Number.MAX_SAFE_INTEGER
  const rightIndex = right.columnIndex ?? Number.MAX_SAFE_INTEGER
  if (leftIndex !== rightIndex) {
    return leftIndex - rightIndex
  }
  return fieldKey(left).localeCompare(fieldKey(right))
}

const isNumericField = (field: PreviewCalcField): boolean => {
  return field.deType === 1 || field.deType === 2 || field.deType === 3
}

const baseFieldsInOrder = (fields: PreviewCalcField[]): PreviewCalcField[] => {
  return fields.filter(field => field.extField === 0).sort(compareColumnOrder)
}

const resolveDirectField = (
  referenceId: string,
  fieldsById: Map<string, PreviewCalcField>
): PreviewCalcField | undefined => {
  return fieldsById.get(referenceId.trim())
}

const evaluateCalculatedField = (
  field: PreviewCalcField,
  row: PreviewRow,
  fieldsById: Map<string, PreviewCalcField>,
  orderedBaseFields: PreviewCalcField[],
  cache: Map<string, unknown>
): unknown => {
  const cacheKey = String(field.id || fieldKey(field))
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey)
  }

  const expression = sanitizeExpression(String(field.originName || ''))
  if (!expression) {
    cache.set(cacheKey, null)
    return null
  }

  const references = Array.from(expression.matchAll(/\[(.+?)\]/g)).map(match => match[1].trim())
  const unresolvedReferenceOrder = Array.from(new Set(references)).filter(referenceId => {
    return !resolveDirectField(referenceId, fieldsById)
  })
  const fallbackBaseFields = (() => {
    if (typeof field.columnIndex !== 'number') {
      return orderedBaseFields
    }
    const precedingNumericFields = orderedBaseFields.filter(candidate => {
      return (
        typeof candidate.columnIndex === 'number' &&
        candidate.columnIndex < field.columnIndex &&
        isNumericField(candidate)
      )
    })
    if (precedingNumericFields.length >= unresolvedReferenceOrder.length) {
      return precedingNumericFields.slice(-unresolvedReferenceOrder.length)
    }
    return orderedBaseFields
  })()

  const resolveReferenceValue = (referenceId: string): unknown => {
    const normalizedReferenceId = referenceId.trim()
    const param = field.params?.find(item => String(item.id || '').trim() === normalizedReferenceId)
    if (param) {
      return param.value ?? null
    }

    const directField = resolveDirectField(normalizedReferenceId, fieldsById)
    if (directField) {
      return directField.extField === 2
        ? evaluateCalculatedField(directField, row, fieldsById, orderedBaseFields, cache)
        : readRowValue(row, directField)
    }

    const fallbackIndex = unresolvedReferenceOrder.indexOf(normalizedReferenceId)
    if (fallbackIndex >= 0) {
      const fallbackField = fallbackBaseFields[fallbackIndex]
      if (fallbackField) {
        return readRowValue(row, fallbackField)
      }
    }

    return null
  }

  const singleRef = expression.match(SINGLE_REFERENCE_RE)
  if (singleRef) {
    const value = resolveReferenceValue(singleRef[1])
    cache.set(cacheKey, value)
    return value
  }

  const substituted = expression.replace(/\[(.+?)\]/g, (_, referenceId: string) => {
    return toNumericLiteral(resolveReferenceValue(referenceId))
  })
  const value = evaluateNumericExpression(substituted)
  cache.set(cacheKey, value)
  return value
}

export const applyCalculatedPreviewFields = (
  previewFields: PreviewCalcField[],
  previewRows: PreviewRow[],
  allFields: PreviewCalcField[]
): { fields: PreviewCalcField[]; rows: PreviewRow[] } => {
  const visibleFields = allFields.filter(field => field.checked !== false && field.extField !== 3)
  const calculatedFields = visibleFields.filter(field => field.extField === 2)
  const orderedBaseFields = baseFieldsInOrder(visibleFields)

  const mergedFields = [...previewFields]
  const existingKeys = new Set(previewFields.map(field => fieldKey(field)).filter(Boolean))
  for (const field of calculatedFields) {
    const key = fieldKey(field)
    if (!key || existingKeys.has(key)) {
      continue
    }
    existingKeys.add(key)
    mergedFields.push({
      id: field.id,
      dataeaseName: field.dataeaseName || field.name || key,
      fieldShortName: field.fieldShortName || field.name || key,
      name: field.name || key,
      originName: field.originName || key,
      deType: field.deType ?? 0,
      type: field.type || '',
      extField: field.extField,
      params: field.params || []
    })
  }

  const fieldsById = new Map<string, PreviewCalcField>()
  for (const field of visibleFields) {
    if (field.id !== null && field.id !== undefined) {
      fieldsById.set(String(field.id), field)
    }
  }

  const rows = previewRows.map(row => {
    const nextRow = { ...row }
    const cache = new Map<string, unknown>()
    for (const field of calculatedFields) {
      const key = fieldKey(field)
      if (!key) {
        continue
      }
      nextRow[key] = evaluateCalculatedField(field, nextRow, fieldsById, orderedBaseFields, cache)
    }
    return nextRow
  })

  return { fields: mergedFields, rows }
}
