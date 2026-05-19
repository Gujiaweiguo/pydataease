import { describe, expect, it, vi } from 'vitest'
import CryptoJS from 'crypto-js/crypto-js'

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn() }
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getDekey: 'mockDekey' })
}))

vi.mock('jsencrypt/bin/jsencrypt.min', () => ({
  default: class MockJSEncrypt {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    setKey() {}
    encrypt(word: string) {
      return `encrypted:${word}`
    }
  }
}))

import { symmetricDecrypt } from '../encryption'

const iv = CryptoJS.enc.Utf8.parse('0000000000000000')

const encryptToBase64 = (plaintext: string, rawKey: string) => {
  const key = CryptoJS.enc.Utf8.parse(rawKey)
  const encrypted = CryptoJS.AES.encrypt(plaintext, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  })

  return {
    data: CryptoJS.enc.Base64.stringify(encrypted.ciphertext),
    keyStr: CryptoJS.enc.Base64.stringify(key)
  }
}

describe('encryption', () => {
  it('decrypts ciphertext encrypted with the matching key', () => {
    const { data, keyStr } = encryptToBase64('DataEase', '1234567890123456')

    expect(symmetricDecrypt(data, keyStr)).toBe('DataEase')
  })

  it('decrypts unicode plaintext correctly', () => {
    const { data, keyStr } = encryptToBase64('数据可视化平台', 'abcdefghijklmnop')

    expect(symmetricDecrypt(data, keyStr)).toBe('数据可视化平台')
  })

  it('returns an empty string when the wrong key is used', () => {
    const encrypted = encryptToBase64('secret-message', '1234567890123456')
    const wrongKey = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse('6543210987654321'))

    expect(symmetricDecrypt(encrypted.data, wrongKey)).toBe('')
  })

  it('returns an empty string for invalid ciphertext data', () => {
    const keyStr = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse('1234567890123456'))

    expect(symmetricDecrypt('not-base64', keyStr)).toBe('')
  })

  it('handles empty plaintext payloads', () => {
    const { data, keyStr } = encryptToBase64('', '1234567890123456')

    expect(symmetricDecrypt(data, keyStr)).toBe('')
  })
})
