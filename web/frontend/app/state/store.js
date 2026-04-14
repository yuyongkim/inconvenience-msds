export function createStore(initialState) {
  let state = { ...initialState };
  const listeners = new Set();

  function getState() {
    return state;
  }

  function setState(patch) {
    const prevState = state;
    const nextPatch = typeof patch === "function" ? patch(prevState) : patch;
    state = { ...prevState, ...nextPatch };
    for (const listener of listeners) listener(state, prevState);
    return state;
  }

  function subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  }

  return { getState, setState, subscribe };
}

