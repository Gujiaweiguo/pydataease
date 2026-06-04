import { i18n } from '@/plugins/vue-i18n'

type I18nGlobalTranslation = {
  (key: string): string
  (key: string, locale: string): string
  (key: string, locale: string, list: unknown[]): string
  (key: string, locale: string, named: Record<string, unknown>): string
  (key: string, list: unknown[]): string
  (key: string, named: Record<string, unknown>): string
}

type I18nTranslationRestParameters = [string, any]

const translate = (namespace: string | undefined, key: string, ...arg: unknown[]) => {
  if (!key) return ''
  if (!key.includes('.') && !namespace) return key
  if (!i18n) {
    return getKey(namespace, key)
  }

  const { t } = i18n.global
  return (t as I18nGlobalTranslation)(
    getKey(namespace, key),
    ...(arg as I18nTranslationRestParameters)
  )
}

const getKey = (namespace: string | undefined, key: string) => {
  if (!namespace) {
    return key
  }
  if (key.startsWith(namespace)) {
    return key
  }
  return `${namespace}.${key}`
}

export const useI18n = (
  namespace?: string
): {
  t: I18nGlobalTranslation
} => {
  const tFn: I18nGlobalTranslation = (key: string, ...arg: any[]) => {
    return translate(namespace, key, ...arg)
  }

  if (!i18n) {
    return {
      t: tFn
    }
  }

  const { ...methods } = i18n.global
  return {
    ...methods,
    t: tFn
  }
}

export const t = (key: string) => translate(undefined, key)
