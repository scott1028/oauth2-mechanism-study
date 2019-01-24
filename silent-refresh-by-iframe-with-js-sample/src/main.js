// Module: SPA only can execute this once.
// Usage: Hook this after your fetch function
class SilentRefresher {
  constructor(
    src,
    timeout = 5000,
    {
      tokenRenewed = 'TOKEN_RENEWED',
      renewTimeout = 'RENEW_TIMEOUT',
      id = `silent-refresher-${new Date().getTime()}`,
    } = {}) {
    this.id = id;
    this.src = src;
    this.timeout = timeout;
    this.tokenRenewed = tokenRenewed;
    this.renewTimeout = renewTimeout;
    this.running = false;
    this.perform = this.perform.bind(this);
    this.pendingProcedures = [];
  }
  perform(callback = undefined) {
    return new Promise((res, rej) => {
      if (this.running) {
        if (typeof callback === 'function') {
          this.pendingProcedures.push(callback);
        }
        return console.debug(`running: ${this.running}`);
      }
      if (typeof callback === 'function') {
        this.pendingProcedures.push(callback);
      }
      this.running = true;
      this.onmessage = function(e) {
        const runAction = (run) => {
          const pendingLen = this.pendingProcedures.length;
          for (let i = 0; i < pendingLen; i += 1) {
            run ? this.pendingProcedures.shift()() : this.pendingProcedures.shift();
          }
        };
        const postAction = (run) => {
          window.removeEventListener('message', this.onmessage);
          runAction(run);
          this.running = false;
        };
        switch(e.data.type) {
          case this.tokenRenewed:
            this.iframe.remove();
            clearTimeout(this.timeoutId);
            res(e.data);
            postAction(true);
            break;
          case this.renewTimeout:
            this.iframe.remove();
            rej(e.data);
            postAction(false);
            break;
          default:
            console.debug(e);
            break;
        }
      };
      this.onmessage = this.onmessage.bind(this);
      window.addEventListener('message', this.onmessage);
      const iframe = document.createElement('iframe');
      iframe.id = this.id;
      iframe.src = this.src;
      document.body.append(iframe);
      this.iframe = iframe;
      this.timeoutId = setTimeout(() => postMessage({ type: this.renewTimeout }), this.timeout);
    });
  }
}

export default SilentRefresher;
