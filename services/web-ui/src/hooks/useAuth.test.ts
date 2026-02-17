import { act, renderHook } from "@testing-library/react";
import { AUTH_UNAUTHORIZED_EVENT } from "../api/client";
import { useAuth } from "./useAuth";

it("loads auth from localStorage", () => {
  localStorage.setItem("code-dojo-token", "abc");
  localStorage.setItem("code-dojo-username", "demo");

  const { result } = renderHook(() => useAuth());

  expect(result.current.token).toBe("abc");
  expect(result.current.username).toBe("demo");
  expect(result.current.isAuthenticated).toBe(true);
});

it("clears auth when unauthorized event is emitted", () => {
  localStorage.setItem("code-dojo-token", "abc");
  localStorage.setItem("code-dojo-username", "demo");

  const { result } = renderHook(() => useAuth());

  act(() => {
    window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
  });

  expect(result.current.token).toBeNull();
  expect(result.current.username).toBeNull();
  expect(result.current.error).toMatch(/session expired/i);
});
