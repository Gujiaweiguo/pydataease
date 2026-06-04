import { Base64 } from 'js-base64'

const isBase64Encoded = (value: string): boolean => {
  try {
    return Base64.encode(Base64.decode(value)) === value
  } catch {
    return false
  }
}

const isCalculatedField = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' &&
  value !== null &&
  !Array.isArray(value) &&
  (value as Record<string, unknown>).extField === 2 &&
  typeof (value as Record<string, unknown>).originName === 'string'

const NON_TRAVERSABLE_TYPES = [File, Blob, FormData, ArrayBuffer, Date, RegExp, DataView]

const isPlainObject = (value: unknown): value is Record<string, unknown> => {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false
  const proto = Object.getPrototypeOf(value)
  return proto === null || proto === Object.prototype
}

const shouldTraverse = (value: unknown): boolean => {
  if (typeof value !== 'object' || value === null) return false
  for (const Type of NON_TRAVERSABLE_TYPES) {
    if (value instanceof Type) return false
  }
  return true
}

type TransformMode = 'encode' | 'decode'

const transformField = (field: Record<string, unknown>, mode: TransformMode): void => {
  const originName = field.originName as string
  if (mode === 'encode') {
    if (!isBase64Encoded(originName)) {
      field.originName = Base64.encode(originName)
    }
  } else {
    field.originName = Base64.decode(originName)
  }
}

const transformDeep = <T>(value: T, mode: TransformMode, seen: WeakSet<object>): T => {
  if (typeof value !== 'object' || value === null) return value

  if (!shouldTraverse(value)) return value
  if (seen.has(value as object)) return value
  seen.add(value as object)

  if (Array.isArray(value)) {
    const result: unknown[] = value.map(item => {
      if (isCalculatedField(item)) {
        const cloned = { ...item }
        transformField(cloned, mode)
        return cloned
      }
      return transformDeep(item, mode, seen)
    })
    return result as T
  }

  if (isPlainObject(value)) {
    const result: Record<string, unknown> = {}
    for (const key of Object.keys(value)) {
      const child = (value as Record<string, unknown>)[key]
      if (isCalculatedField(child)) {
        const cloned = { ...child }
        transformField(cloned, mode)
        result[key] = cloned
      } else {
        result[key] = transformDeep(child, mode, seen)
      }
    }
    return result as T
  }

  return value
}

export const encodeCalculatedFieldsDeep = <T>(payload: T): T => {
  return transformDeep(payload, 'encode', new WeakSet())
}

export const decodeCalculatedFieldsDeep = <T>(payload: T): T => {
  return transformDeep(payload, 'decode', new WeakSet())
}
