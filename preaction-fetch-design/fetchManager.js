/**
 * fetchManager
 * This is for client-side fetch manager designed by window.addEventListener('message', ...)
 * @param {Object} session - session flag object for fetchManager
 * @param {function} checkSessionValid - check session valid or not and then return true/false
 * @param {function} originalFetch - fetch function you will use in application
 */
const fetchManager = (
  originalFetch,
  checkSessionValid = () => true) => (...args) => {
  if (checkSessionValid()) {
    return originalFetch.apply(this, args);
  }
  return new Promise((res, rej) => {
    const handler = e => {
      if (checkSessionValid()) {
        window.removeEventListener('message', handler);
        res(originalFetch.apply(this, args));
      }
    };
    window.addEventListener('message', handler);
  });
};
