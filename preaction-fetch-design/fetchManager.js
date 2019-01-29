/**
 * fetchManager
 * This is for client-side fetch manager
 * @param {Object} session - session flag object for fetchManager
 * @param {function} preaction - preaction before you invoke fetch
 * @param {function} fetch - fetch function you will use in application
 */
const fetchManager = (
  originalFetch,
  checkSessionValid = () => true) => (...args) => {
  if (checkSessionValid()) {
    return originalFetch.apply(this, args);
  }
  return new Promise((res, rej) => {
    const handler = e => {
      preaction(session);
      if (checkSessionValid()) {
        window.removeEventListener('message', handler);
        res(originalFetch.apply(this, args));
      }
    };
    window.addEventListener('message', handler);
  });
};
