class MockWorker {
  url: string
  constructor(url: string) {
    this.url = url
  }
  postMessage() {
    /* noop */
  }
  terminate() {
    /* noop */
  }
  addEventListener() {
    /* noop */
  }
  removeEventListener() {
    /* noop */
  }
}
;(globalThis as any).Worker = MockWorker
