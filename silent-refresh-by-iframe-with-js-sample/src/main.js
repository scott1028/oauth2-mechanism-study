// Module: SPA only can execute this once.
const initTokenRefresher = (src, timeout = 5000, {
  TOKEN_RENEWED = 'TOKEN_RENEWED',
  RENEW_TIMEOUT = 'RENEW_TIMEOUT',
}) => {
  let config = {
    running: false,
  };
  return () => new Promise((res, rej) => {
    config.onmessage = function(e) {
      switch(e.data.type) {
        case TOKEN_RENEWED:
          this.iframe.remove();
          clearTimeout(this.timeoutId);
          res(e.data);
          break;
        case RENEW_TIMEOUT:
          this.iframe.remove();
          rej(e.data);
          break;
        default:
          console.log(e);
          break;
      }
      window.removeEventListener('message', this.onmessage);
      this.running = false;
    };
    config.perform = function() {
      if (this.running) {
        return console.log(`running: ${this.running}`);
      }
      this.running = true;
      window.addEventListener('message', this.onmessage);
      document.querySelector('#refresh_token_handler')
      const iframe = document.createElement('iframe');
      iframe.id = 'token-handler';
      iframe.src = src;
      document.body.append(iframe);
      this.iframe = iframe;
      this.timeoutId = setTimeout(() => postMessage({ type: 'RENEW-TIMEOUT' }), timeout);
    };
    config.onmessage = config.onmessage.bind(config);
    config.perform = config.perform.bind(config);
    config.perform();
  });
};

export default initTokenRefresher;
